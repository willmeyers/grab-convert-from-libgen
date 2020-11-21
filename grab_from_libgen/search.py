import pathlib
import urllib
from collections import OrderedDict
from typing import List, Dict

import requests
import lxml.html as html

from . import mirrors
from .search_parameters import SciTechSearchParameters, FictionSearchParameters, ComicSearchParameters
from .search_config import get_request_headers
from .convert import ConversionError, convert_file_to_format
from .exceptions import LibgenError, InvalidSearchParameter


class LibgenSearch:
    base_url = None
    url = None
    
    results = None

    search_parameter_objects = {
        'sci-tech': SciTechSearchParameters,
        'fiction': FictionSearchParameters,
        'comics': ComicSearchParameters
    }

    mirror_objects = {
        'library.lol': mirrors.LibrarylolMirror,
        'libgen.lc': mirrors.LibgenlcMirror,
    }

    def __init__(self, topic: str, **parameters):
        if topic not in ['sci-tech', 'fiction', 'comics']:
            raise LibgenError(f'Topic \'{topic}\' is not valid. Valid topics are sci-tech, fiction, or comics')

        self.topic = topic
        
        self.search_parameters = self.search_parameter_objects[self.topic](**parameters)
        
        if self.search_parameters.are_valid():
            self.url = self.search_parameters.url
        else:
            raise InvalidSearchParameter('Given search parameters are not valid.')

    def _grab_file_from_mirror(self, mirror_url: str, save_to: pathlib.Path, convert_to=None) -> str:
        """ Downloads file from a mirror url. If the given mirror url does not exist, it raises an error.
            Othereise, goes through the motions of downloads, converts, and saves the file to a specified path.
        """
        netloc = urllib.parse.urlparse(mirror_url).netloc

        try:
            mirror = self.mirror_objects[netloc](mirror_url)
            filename, file_content = mirror.download_file()

        except KeyError:
            raise KeyError('The given mirror URL does not match any current scrapers.')

        if filename is None:
            raise LibgenError(f'Could not download file from url {mirror_url}. This may be an internal issue')

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

        finished = False
        mirrors = [book['mirror1'], book['mirror2']]

        for mirror in mirrors:
            try:
                if not finished:
                    completed = self._grab_file_from_mirror(mirror, save_to=save_to, convert_to=convert_to)
                    if completed:
                        finished = True

            except Exception as err:
                if mirror == mirrors[-1]:
                    raise err
                else:
                    continue

    def _get_scitech_results(self) -> OrderedDict:
        """ Returns a dictionary of search results.
        """
        results = OrderedDict()

        resp = requests.get(self.url, headers=get_request_headers())
        if resp.status_code != 200:
            raise LibgenError('The requested URL did not have status code 200.')

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
                    value = value.text_content().strip().replace('\n', '').replace('\t', '')

                row.update({header: value})

            results[int(row.pop('id'))] = row

        self.results = results

        return results

    def _get_fiction_results(self) -> OrderedDict:
        results = OrderedDict()
        
        resp = requests.get(self.url, headers=get_request_headers())
        if resp.status_code != 200:
            raise LibgenError('The requested URL did not have status code 200.')

        parsed_content = html.fromstring(resp.content)
        results_table = parsed_content.xpath('//table')[0]

        for idx, tr in enumerate(results_table.xpath('//tr')[1:]):
            row = {}
            for header, value in zip(
                    ['author(s)', 'series', 'title', 'language', 'file', 'mirror1', 
                    'mirror2', 'mirror3', 'edit'], tr.getchildren()):
                if header in ['mirror1', 'mirror2', 'mirror3', 'edit'] and list(value.iterlinks()):
                    value = list(value.iterlinks())[0][2]
                else:
                    value = value.text_content().strip().replace('\n', '').replace('\t', '')

                row.update({header: value})

            results[idx] = row

        self.results = results

        return results

    def _get_comic_results(self) -> OrderedDict:
        results = OrderedDict()

    def get_results(self) -> OrderedDict:
        if self.topic == 'sci-tech':
            self.results = self._get_scitech_results()

        if self.topic == 'fiction':
            self.results = self._get_fiction_results()

        if self.topic == 'comics':
            self.results = self._get_comic_results()

        return self.results

    def first(self, save_to: str = None, convert_to: str = None) -> Dict:
        """ Returns the first result from the list of search results.
        """
        if save_to or convert_to:
            if convert_to:
                save_to = '.' if save_to is None else save_to

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
