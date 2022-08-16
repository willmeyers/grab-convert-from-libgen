from bs4 import BeautifulSoup
from .exceptions import MetadataError
from .search_config import get_request_headers, get_mirror_sources
from .metadata_helpers import fiction_field_value, scitech_field_value
from typing import Union, Optional
import re
from requests import exceptions
from requests_html import HTMLSession


class Metadata:
    def __init__(self, timeout: Optional[Union[int, tuple]] = None):
        # No method here is rate-limited, use it with caution!
        # You will get blocked for abusing this.
        # 2000ms between each call is probably safe.
        # Timeout = None equals to infinite timeout in requests library.

        if isinstance(timeout, int):
            if timeout <= 0:
                timeout = None
        elif isinstance(timeout, tuple):
            if timeout[0] <= 0 or timeout[1] <= 0:
                timeout = None

        self.timeout = timeout

        # Common paterns for URLs used here.
        self._liblol_base = "http://library.lol"
        self._librocks_base = "https://libgen.rocks/ads.php?md5="
        self._3lib_base = "https://3lib.net/md5/"
        self._libgen_fiction_base = "https://libgen.is/fiction/"
        self._libgen_scitech_base = "https://libgen.is/book/index.php?md5="

    def get_cover(self, md5: str) -> str:
        session = HTMLSession()
        # Both 3lib and LibraryRocks doesn't use CORS in their cover images.

        _3lib = self._3lib_base + md5
        librocks = self._librocks_base + md5

        # This function will try for both 3lib and libraryrocks.
        try:
            page = session.get(_3lib, headers=get_request_headers(), timeout=self.timeout)
            # If 3lib is up.
            _3libup = True

        except (exceptions.Timeout, exceptions.ConnectionError, exceptions.HTTPError):
            # If 3lib is down.
            _3libup = False
            try:
                page = session.get(librocks, headers=get_request_headers(), timeout=self.timeout)

            except (exceptions.Timeout, exceptions.ConnectionError, exceptions.HTTPError) as err:
                raise MetadataError("Both 3lib and LibraryRocks failed to connect. The last error was: ", err)

        soup = BeautifulSoup(page.html.raw_html, "html.parser")

        if _3libup:
            # if 3lib is up
            cover = soup.find("img", {"class": "cover"})
            try:
                # 3lib returns a very small cover on the search page, this changes the url to render the bigger one.
                if cover.has_attr("data-src"):
                    cover_url = re.sub("covers100", "covers299", cover["data-src"])
                else:
                    raise TypeError

            except TypeError:
                raise MetadataError("Could not find cover for this specific md5.")

            except KeyError:
                # Sometimes there's no covers299 version of the cover.
                try:
                    if cover.has_attr("data-src"):
                        cover_url = re.sub("covers100", "covers200", cover["data-src"])
                    else:
                        raise TypeError

                except TypeError:
                    raise MetadataError("Could not find cover for this specific md5.")

                except KeyError:
                    raise MetadataError("Could not find cover for this specific md5.")

            if cover_url == "/img/cover-not-exists.png":
                # This image doesn't actually render,
                # So sending this link is equivalent.

                cover_url = "https://libgen.rocks/img/blank.png"
        else:
            # if 3lib is down
            try:
                cover = soup.select("img:last-of-type")[1]

                if cover is not None:
                    cover_url = "https://libgen.rocks" + cover["src"]
                else:
                    raise TypeError

            except KeyError:
                raise MetadataError("Could not find cover for this specific md5.")
            except TypeError:
                raise MetadataError("Could not find cover for this specific md5.")

        return cover_url

    def _get_fiction_metadata(self, md5: str):
        session = HTMLSession()
        url = self._libgen_fiction_base + md5
        try:
            page = session.get(url, headers=get_request_headers(), timeout=self.timeout)
            page.raise_for_status()
        except (exceptions.Timeout, exceptions.ConnectionError, exceptions.HTTPError) as err:
            raise MetadataError("Error while connecting to Libgen: ", err)

        soup = BeautifulSoup(page.html.raw_html, "lxml")
        try:
            # The description element is an td with colspan = 2, with no class.
            description = soup.find("td", colspan="2", class_=None).text.strip()

            if description == "":
                description = None
        except AttributeError:
            description = None

        return {
            "title": fiction_field_value("Title:", soup),
            "authors": fiction_field_value("Author(s):", soup),
            "series": fiction_field_value("Series:", soup),
            "edition": fiction_field_value("Edition:", soup),
            "language": fiction_field_value("Language:", soup),
            "year": fiction_field_value("Year:", soup),
            "publisher": fiction_field_value("Publisher:", soup),
            "isbn": fiction_field_value("ISBN:", soup),
            "md5": md5,
            "topic": "fiction",
            "extension": fiction_field_value("Format:", soup),
            "size": fiction_field_value("File size:", soup),
            "description": description
        }

    def _get_scitech_metadata(self, md5: str):
        session = HTMLSession()
        url = self._libgen_scitech_base + md5
        try:
            page = session.get(url, headers=get_request_headers(), timeout=self.timeout)
            page.raise_for_status()
        except (exceptions.Timeout, exceptions.ConnectionError, exceptions.HTTPError) as err:
            raise MetadataError("Error while connecting to Libgen: ", err)

        soup = BeautifulSoup(page.html.raw_html, "lxml")
        # A special case, no field name attached.
        try:
            # The description element is an td with colspan = 4
            description = soup.find("td", colspan="4").text.strip()

            if description == "":
                description = None
        except AttributeError:
            description = None

        return {
            "title": scitech_field_value("Title: ", soup),
            "authors": scitech_field_value("Author(s):", soup),
            "series": scitech_field_value("Series:", soup),
            "edition": scitech_field_value("Edition:", soup),
            "language": scitech_field_value("Language:", soup),
            "year": scitech_field_value("Year:", soup),
            "publisher": scitech_field_value("Publisher:", soup),
            "isbn": scitech_field_value("ISBN:", soup),
            "md5": md5,
            "topic": "sci-tech",
            "extension": scitech_field_value("Extension:", soup),
            "size": scitech_field_value("Size:", soup),
            "description": description
        }

    def get_metadata(self, md5: str, topic: str):
        topic_url = None

        # This function scrapes all the avaiable metadata on LibraryLol. Description and Direct download link.
        # This method raises an error if a download link is not found. But no error is a description is not.
        # This is because while most files do have a d_link, a lot don't have a description.

        if topic == "sci-tech":
            return self._get_scitech_metadata(md5)
        elif topic == "fiction":
            return self._get_fiction_metadata(md5)
        else:
            raise MetadataError("Topic is not valid. Valid topics are \"fiction\" and \"sci-tech\".")

    def get_download_links(self, md5: str, topic: str):
        session = HTMLSession()
        topic_url = None

        # This function scrapes all the avaiable metadata on LibraryLol. Description and Direct download link.
        # This method raises an error if a download link is not found. But no error is a description is not.
        # This is because while most files do have a d_link, a lot don't have a description.

        if topic == "sci-tech":
            topic_url = "/main/"
        elif topic == "fiction":
            topic_url = "/fiction/"
        else:
            raise MetadataError("Topic is not valid. Valid topics are \"fiction\" and \"sci-tech\".")

        url = self._liblol_base + topic_url + md5

        # Uses a md5 to take the download links.
        # It also scrapes the book's description.
        # Ideally, this should only be done once the users actually wants to download a book.

        try:
            page = session.get(url, headers=get_request_headers(), timeout=self.timeout)
            page.raise_for_status()
        except (exceptions.Timeout, exceptions.ConnectionError, exceptions.HTTPError) as err:
            raise MetadataError("Error while connecting to Librarylol: ", err)

        soup = BeautifulSoup(page.html.raw_html, "html.parser")
        links = soup.find_all("a", string=get_mirror_sources())
        download_links = {link.string: link["href"] for link in links}

        return download_links
