import time
import re
import requests
import lxml.html as html


def get_filename_from_response(repsonse_body) -> str:
    response_header = repsonse_body.headers.get('content-disposition')
    filename = re.findall('filename=\"(.+)\"', response_header) if response_header else []

    return filename[0] if filename else 'ebook'


def library_lol_scraper(response_body) -> tuple:
    response_body = html.fromstring(response_body.content)
    download_link = response_body.xpath('//a/@href')[0]

    file_content = requests.get(download_link, allow_redirects=True)
    filename = get_filename_from_response(file_content)

    if file_content.status_code == 200:
        return filename, file_content.content
    else:
        raise ValueError('Could not resolve download URL.')


def libgen_lc_scraper(response_body: str) -> tuple:
    filename = get_filename_from_response(response_body)
    response_body = html.fromstring(response_body.content)
    download_link = response_body.xpath('//a/@href')[0]

    file_content = requests.get(download_link, allow_redirects=True)

    if file_content.status_code == 200:
        return filename, file_content.content
    else:
        raise ValueError('Could not resolve download URL.')

