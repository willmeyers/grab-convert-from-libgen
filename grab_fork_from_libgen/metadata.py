from bs4 import BeautifulSoup
from .exceptions import MetadataError
from .search_config import get_request_headers, get_mirror_sources
import re
import requests


class Metadata:
    def __init__(self, md5: str, topic: str, timeout: int | tuple | None = None):
        # No method here is rate-limited, use it with caution!
        # You will get blocked for abusing this.
        # 2000ms between each call is probably safe.
        # Timeout = None equals to infinite timeout in requests library.
        if topic not in ["sci-tech", "fiction"]:
            raise MetadataError(
                f"Topic '{topic}' is not valid. Valid topics are sci-tech or fiction"
            )

        if isinstance(timeout, int):
            if timeout <= 0:
                timeout = None
        elif isinstance(timeout, tuple):
            if timeout[0] <= 0 or timeout[1] <= 0:
                timeout = None

        self.timeout = timeout
        self.topic = topic
        self.md5 = md5

        # Common paterns for URLs used here.
        self.liblol_base = "http://library.lol"
        self.librocks_base = "https://libgen.rocks/ads.php?md5="
        self._3lib_base = "https://3lib.net/md5/"

    def get_cover(self) -> str:
        # Instead of raising an error if no cover is found (and if the request was suceeded), a "no cover" image link is
        # sent instead. It uses HTTP and no CORS. So it's usable in most websites.
        # Both 3lib and LibraryRocks doesn't use CORS in their cover images.

        _3lib = self._3lib_base + self.md5
        librocks = self.librocks_base + self.md5

        # This function will try for both 3lib and libraryrocks.
        try:
            page = requests.get(_3lib, headers=get_request_headers(), timeout=self.timeout)
            # If 3lib is up.
            _3libup = True

        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError, requests.exceptions.HTTPError):
            try:
                page = requests.get(librocks, headers=get_request_headers(), timeout=self.timeout)

            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError,
                    requests.exceptions.HTTPError) as err:
                raise MetadataError("Both 3lib and LibraryRocks failed to connect. The last error was: ", err)

            # If 3lib is down.
            _3libup = False

        soup = BeautifulSoup(page.text, "html.parser")

        if _3libup:
            # if 3lib is up
            cover = soup.find("img", {"class": "cover"})
            try:
                # 3lib returns a very small cover on the search page, this changes the url to render the bigger one.
                cover_url = re.sub("covers100", "covers299", cover["data-src"])
            except KeyError:
                # Sometimes there's no covers299 version of the cover.
                try:
                    cover_url = re.sub("covers100", "covers200", cover["data-src"])
                except KeyError:
                    raise MetadataError("Could not find cover for this specific md5.")

            if cover_url == "/img/cover-not-exists.png":
                # This image doesn't actually render,
                # So sending this link is equivalent.

                cover_url = "https://libgen.rocks/img/blank.png"
        else:
            # if 3lib is down
            try:
                cover = soup.find("img")
                cover_url = "https://libgen.rocks" + cover["src"]
            except KeyError:
                cover_url = "https://libgen.rocks/img/blank.png"

        return cover_url

    def get_metadata(self) -> tuple:
        # This function scrapes all the avaiable metadata on LibraryLol. Description and Direct download link.
        # This method raises an error if a download link is not found. But no error is a description is not.
        # This is because while most files do have a d_link, a lot don't have a description.

        if self.topic == "sci-tech":
            topic_url = "/main/"
        elif self.topic == "fiction":
            topic_url = "/fiction/"

        url = self.liblol_base + topic_url + self.md5

        # Uses a md5 to take the download links.
        # It also scrapes the book's description.
        # Ideally, this should only be done once the users actually wants to download a book.

        try:
            page = requests.get(url, headers=get_request_headers(), timeout=self.timeout)
            page.raise_for_status()
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError, requests.exceptions.HTTPError) as err:
            raise MetadataError("Error while connecting to Librarylol: ", err)

        soup = BeautifulSoup(page.text, "html.parser")
        links = soup.find_all("a", string=get_mirror_sources())
        # Selects the last div, which is the description div.
        descdiv = soup.select("div:last-of-type")[1].text
        # Removes "Description:" from the book's description.
        desc = re.sub("Description:", "", descdiv)
        download_links = {link.string: link["href"] for link in links}

        if download_links is None:
            raise MetadataError("Could not find any download links.")
        # If the description is empty, an empty string would be returned.
        if desc == "":
            desc = None
        return download_links, desc
