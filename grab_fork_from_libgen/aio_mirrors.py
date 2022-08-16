import time
import re
import urllib
from typing import Tuple
from abc import ABC, abstractmethod

from requests import models, exceptions
from requests_html import AsyncHTMLSession
import lxml.html as html


def get_filename_from_response(response: models.Response) -> str:
    response_header = response.headers.get("content-disposition")
    filename = re.findall('filename="(.+)"', response_header) if response_header else []

    return filename[0] if filename else "ebook"


class AIOLibgenMirror(ABC):
    netloc: str = None
    download_link: str = None
    response: models.Response = None
    session = None

    def __init__(self, url: str):
        self.url = url
        super().__init__()

    async def request(self):
        self.session = AsyncHTMLSession()
        self.response = await self.session.get(self.url)

    @abstractmethod
    async def scrape_download_link(self):
        raise NotImplementedError("AIOLibgenMirror must implement scrape_download_link")

    async def download_file(self) -> Tuple:
        if self.download_link is None:
            self.download_link = await self.scrape_download_link()

        try:
            r = await self.session.get(self.download_link, allow_redirects=True)

            if r.status_code == 200:
                filename = get_filename_from_response(r)

                return filename, r.content

            raise exceptions.RequestException("Response did not have status code 200")

        except Exception as err:
            raise Exception(err)

        return None, None


class LibrarylolMirror(AIOLibgenMirror):
    async def scrape_download_link(self) -> str:
        await self.request()
        tree = html.fromstring(self.response.content)
        download_link = tree.xpath("//a/@href")[0]

        return download_link


class LibgenlcMirror(AIOLibgenMirror):
    async def scrape_download_link(self) -> str:
        await self.request()
        tree = html.fromstring(self.response.content)
        download_link = tree.xpath("//a/@href")[0]

        return download_link
