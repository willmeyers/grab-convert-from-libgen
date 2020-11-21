import time
import re
import urllib
from typing import Tuple
from abc import ABC, abstractmethod

import requests
import lxml.html as html


def get_filename_from_response(repsonse: requests.models.Response) -> str:
    response_header = repsonse.headers.get('content-disposition')
    filename = re.findall('filename=\"(.+)\"', response_header) if response_header else []

    return filename[0] if filename else 'ebook'


class LibgenMirror(ABC):
    netloc: str = None
    download_link: str = None
    response: requests.models.Response = None

    def __init__(self, url: str):
        self.url = url
        self.response = requests.get(self.url)

        super().__init__()

    @abstractmethod
    def scrape_download_link(self) -> str:
        pass

    def download_file(self) -> Tuple:
        if self.download_link is None:
            self.download_link = self.scrape_download_link()

        try:
            r = requests.get(self.download_link, allow_redirects=True)

            if r.status_code == 200:
                filename = get_filename_from_response(r)
                
                return filename, r.content
            
            raise requests.RequestException('Response did not have status code 200')

        except Exception as err:
            raise Exception(err)

        return None, None


class LibrarylolMirror(LibgenMirror):
    def scrape_download_link(self) -> str:
        tree = html.fromstring(self.response.content)
        download_link = tree.xpath('//a/@href')[0]

        return download_link


class LibgenlcMirror(LibgenMirror):
    def scrape_download_link(self) -> str:
        tree = html.fromstring(self.response.content)
        download_link = tree.xpath('//a/@href')[0]

        return download_link        
