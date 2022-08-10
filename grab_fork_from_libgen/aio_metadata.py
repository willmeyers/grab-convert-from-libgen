from bs4 import BeautifulSoup
from .exceptions import MetadataError
from .search_config import get_request_headers, get_mirror_sources
from .models.metadata_models import MetadataResponse
from .models.search_models import ValidTopics
import re
from requests import exceptions
from requests_html import AsyncHTMLSession




class AIOMetadata:
    def __init__(self, timeout: int | tuple | None = None):
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
        self.liblol_base = "http://library.lol"
        self.librocks_base = "https://libgen.rocks/ads.php?md5="
        self._3lib_base = "https://3lib.net/md5/"

    async def get_cover(self, md5: str) -> str:
        session = AsyncHTMLSession()

        # Instead of raising an error if no cover is found (and if the request was suceeded), a "no cover" image link is
        # sent instead. It uses HTTP and no CORS. So it's usable in most websites.
        # Both 3lib and LibraryRocks doesn't use CORS in their cover images.

        _3lib = self._3lib_base + md5
        librocks = self.librocks_base + md5

        # This function will try for both 3lib and libraryrocks.
        try:
            page = await session.get(_3lib, headers=get_request_headers(), timeout=self.timeout)
            # If 3lib is up.
            _3libup = True

        except (exceptions.Timeout, exceptions.ConnectionError, exceptions.HTTPError):
            # If 3lib is down.
            _3libup = False
            try:
                page = await session.get(librocks, headers=get_request_headers(), timeout=self.timeout)

            except (exceptions.Timeout, exceptions.ConnectionError, exceptions.HTTPError) as err:
                raise MetadataError("Both 3lib and LibraryRocks failed to connect. The last error was: ", err)

        soup = BeautifulSoup(page.html.raw_html, "html.parser")

        if _3libup:
            # if 3lib is up
            cover = soup.find("img", {"class": "cover"})
            try:
                # 3lib returns a very small cover on the search page, this changes the url to render the bigger one.
                if cover is not None:
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

    async def get_metadata(self, md5: str, topic: str) -> MetadataResponse:
        session = AsyncHTMLSession()
        topic_url = None
        # This function scrapes all the avaiable metadata on LibraryLol. Description and Direct download link.
        # This method raises an error if a download link is not found. But no error is a description is not.
        # This is because while most files do have a d_link, a lot don't have a description.


        if topic == "sci-tech":
            topic_url = "/main/"
        elif topic == "fiction":
            topic_url = "/fiction/"
        else:
            raise MetadataError("Topic is not valid.")

        url = self.liblol_base + topic_url + md5

        # Uses a md5 to take the download links.
        # It also scrapes the book's description.
        # Ideally, this should only be done once the users actually wants to download a book.

        try:
            page = await session.get(url, headers=get_request_headers(), timeout=self.timeout)
            page.raise_for_status()
        except (exceptions.Timeout, exceptions.ConnectionError, exceptions.HTTPError) as err:
            raise MetadataError("Error while connecting to the download provider: ", err)

        soup = BeautifulSoup(page.html.raw_html, "html.parser")
        links = soup.find_all("a", string=get_mirror_sources())
        # Selects the last div, which is the description div.
        description = soup.select("div:last-of-type")[1].text

        # Removes "Description:" from the book's description.
        fdescription = re.sub("Description:", "", description) if description is not None else None
        download_links = {link.string: link["href"] for link in links}
        title = soup.select_one("#info > h1").text
        authors = soup.select_one("#info > p:nth-child(4)").text
        # Removes "Author(s): " from the book's authors paragraph.
        fauthors = authors.replace("Author(s): ", "")

        metadata_results = MetadataResponse(download_links=download_links,
                                            description=fdescription, authors=fauthors, title=title)
        return metadata_results
