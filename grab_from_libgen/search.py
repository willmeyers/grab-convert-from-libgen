import pathlib
import urllib
from collections import OrderedDict
from typing import List, Dict
from dataclasses import dataclass

import requests
import lxml.html as html

from .mirrors import libgen_lc_scraper, library_lol_scraper
from .search_config import get_request_headers, get_request_url
from .convert import ConversionError, convert_file_to_format


class LibgenError(Exception):
    pass


@dataclass
class SearchParameters:
    req: str
    lg_topic: str = None
    open: int = None
    view: str = None
    res: int = None
    phrase: int = None
    column: str = None
    sort: str = None
    sortmode: str = None
    page: int = None


class LibgenSearch:
    url = None
    results = None
    netloc_map = {
        'library.lol': library_lol_scraper,
        'libgen.lc': libgen_lc_scraper,
    }

    def __init__(self, **parameters):
        sp = SearchParameters(**parameters)

        if self.valid_parameters(sp):
            self.url = get_request_url(sp)

    def valid_parameters(self, parameters: SearchParameters) -> bool:
        """ Checks if given search parameters are valid. Raises exception if False. Otherwise returns True.

            TODO: enforce types?
        """
        if not isinstance(parameters.req, str):
            raise TypeError('Parameter \'req\' must be type str.')

        if len(parameters.req) < 2:
            raise LibgenError('Parameter \'req\' must be >= 2 characters.')

        return True

    def grab_file_from_mirror(self, mirror_url: str, save_to: pathlib.Path, convert_to=None) -> str:
        """ Downloads file from a mirror url. If the given mirror url does not exist, it raises an error.
            Othereise, goes through the motions of downloads, converts, and saves the file to a specified path.
        """
        netloc = urllib.parse.urlparse(mirror_url).netloc
        resp = requests.get(mirror_url)

        try:
            filename, file_content = self.netloc_map[netloc](resp)
        except KeyError:
            raise KeyError('The given mirror URL does not match any current scrapers.')

        with open(filename, 'wb+') as fo:
            fo.write(file_content)

        if convert_to:
            if convert_to.lower() not in {'pdf', 'epub', 'mobi'}:
                raise ConversionError(f'Invalid extension \'{convert_to}\' provided. Only pdf, mobi, or epub is allowed.')

            filename = convert_file_to_format(filename, convert_to=convert_to)

        return filename

    def _save_file(self, book: Dict, save_to: str, convert_to: str = None) -> None:
        """ Given a book with list of mirror urls, run through all mirror urls until a valid response is
            returned. Executes `grab_file_from_mirror`. 
        """
        save_to = pathlib.Path(save_to)

        mirrors = [book['mirror1']]

        for mirror in mirrors:
            try:
                self.grab_file_from_mirror(mirror, save_to=save_to, convert_to=convert_to)
            except LibgenError as err:
                if mirror == mirrors[-1]:
                    raise err
                else:
                    continue

    def get_results(self) -> OrderedDict:
        """ Returns a dictionary of search results.
        """
        results = OrderedDict()

        resp = requests.get(self.url, headers=get_request_headers())
        if resp.status_code != 200:
            raise LibgenError('The requested URL did not return 200 OK.')

        parsed_content = html.fromstring(resp.content)
        results_table = parsed_content.xpath('/html/body/table[3]')[0]

        for tr in results_table.xpath('tr')[1:]:
            row = {}
            for header, value in zip(
                    ['id', 'author(s)', 'title', 'publisher', 'year', 'pages', 'language', 'size', 'extension',
                     'mirror1', 'mirror2', 'mirror3', 'mirror4', 'mirror5', 'edit'], tr.getchildren()):
                if header in ['mirror1', 'mirror2', 'mirror3', 'mirror4', 'mirror5', 'edit'] and list(
                        value.iterlinks()):
                    value = list(value.iterlinks())[0][2]
                else:
                    value = value.text_content()

                row.update({header: value})

            results[int(row.pop('id'))] = row

        self.results = results

        return results

    def first(self, save_to: str = None, convert_to: str = None) -> Dict:
        """ Returns the first result from the list of search results.
         """
        if convert_to:
            if convert_to.lower() not in ['pdf', 'mobi', 'epub']:
                raise ConversionError(f'Invalid extension \'{convert_to}\' provided. Only pdf, mobi, or epub is allowed.')

        if self.results is None:
            self.results = self.get_results()

        try:
            first_book_id = list(self.results.keys())[0]
            book = self.results[first_book_id]
        except (IndexError, KeyError):
            raise LibgenError('Could not grab any book from results list.')

        if save_to:
            self._save_file(book, save_to, convert_to=convert_to)

        return book

    def get_from_result_list(self, book_id: int, save_to=None, convert_to=None) -> Dict:
        """ Resutns 
        """
        if save_to:
            if convert_to:
                if convert_to.lower() not in ['pdf', 'mobi', 'epub']:
                    raise ConversionError(f'Invalid extension \'{convert_to}\' provided. Only pdf, mobi, or epub is allowed.')

        if self.results is None:
            self.results = self.get_results()

        try:
            book = self.results[book_id]
        except KeyError:
            raise LibgenError(f'The book id \'{book_id}\' does not exist in this list of results.')

        if save_to:
            self._save_file(book, save_to, convert_to=convert_to)

        return book
