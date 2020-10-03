import json
import pathlib
import urllib

from subprocess import Popen

import requests
import lxml.html as html

from mirrors import libgen_lc_scraper, library_lol_scraper, bookfi_net_scraper
from search_config import SearchParameters, get_request_headers, get_request_url
from convert import convert_file_to_format


class LibgenSearch:
    url = None

    netloc_map = {
        'library.lol': library_lol_scraper,
        'libgen.lc': libgen_lc_scraper,
        'en.bookfi.net': bookfi_net_scraper
    }

    def __init__(self, parameters: SearchParameters):
        if self.valid_parameters(parameters):
            self.url = get_request_url(parameters)

    def valid_parameters(self, parameters: SearchParameters) -> bool:
        if len(parameters.req) < 2:
            raise ValueError('Parameter \'req\' must be >= 2 characters.')
        
        return True

    def grab_file_from_mirror(self, mirror_url: str, save_to=None, convert_to=None) -> str:
        if save_to is None:
            raise ValueError('A location to save the file (save_to) must be provided.')
        
        netloc = urllib.parse.urlparse(mirror_url).netloc
        resp = requests.get(mirror_url)

        filename, file_content = self.netloc_map[netloc](resp)

        with open(filename, 'wb+') as fo:
            fo.write(file_content)

        if convert_to:
            if convert_to.lower() not in ['pdf', 'epub', 'mobi']:
                raise ValueError(f'Invalid extension \'{convert_to}\' provided. Only pdf, mobi, or epub is allowed.')
            
            filename = convert_file_to_format(filename, convert_to=convert_to)
        
        return filename


    def results(self, to_json=False) -> str:
        """ Returns a list of search results. """
        results = {}

        resp = requests.get(self.url, headers=get_request_headers())
        if resp.status_code != 200:
            raise 'The requested URL did not return 200 OK.'

        parsed_content = html.fromstring(resp.content)
        results_table = parsed_content.xpath('/html/body/table[3]')[0]
        
        for tr in results_table.xpath('tr')[1:]:
            row = {}
            for header, value in zip(['id', 'author(s)', 'title', 'publisher', 'year', 'pages', 'language', 'size', 'extension', 'mirror1', 'mirror2', 'mirror3', 'mirror4', 'mirror5', 'edit'], tr.getchildren()):
                if header in ['mirror1', 'mirror2', 'mirror3', 'mirror4', 'mirror5', 'edit'] and list(value.iterlinks()):
                    value = list(value.iterlinks())[0][2]
                else:
                    value = value.text_content()
                
                row.update({header: value})

            results[row.pop('id')] = row

        if to_json:
            return json.dumps(results)
        
        return results

    def first(self, to_json=False, download=False, save_to=None, convert_to=None) -> str:
        """ Returns the first result from the list of search results. """
        if download:
            if convert_to:
                if convert_to.lower() not in ['pdf', 'mobi', 'epub']:
                    raise ValueError(f'Invalid extension \'{convert_to}\' provided. Only pdf, mobi, or epub is allowed.') 

        results = {}

        resp = requests.get(self.url, headers=get_request_headers())
        if resp.status_code != 200:
            raise 'The requested URL did not return 200 OK.'

        parsed_content = html.fromstring(resp.content)
        results_table = parsed_content.xpath('/html/body/table[3]')[0]
        
        for tr in results_table.xpath('tr')[1:2]:
            row = {}
            for td in tr.xpath('td'):
                for header, value in zip(['id', 'author(s)', 'title', 'publisher', 'year', 'pages', 'language', 'size', 'extension', 'mirror1', 'mirror2', 'mirror3', 'mirror4', 'mirror5', 'edit'], td):
                    if header in ['mirror1', 'mirror2', 'mirror3', 'mirror4', 'mirror5', 'edit'] and list(value.iterlinks()):
                        value = list(value.iterlinks())[0][2]
                    
                    row.update({header: value})

            results[row.pop('id')] = row

        try:
            first_book_id = list(results.keys())[0]
            book = results[first_book_id]
        except (IndexError, KeyError):
            raise ValueError('Could not grab any book from results list.')

        if download:
            mirrors = [book['mirror1']]
            
            for mirror in mirrors:
                try:
                    self.grab_file_from_mirror(mirror, save_to=save_to, convert_to=convert_to)
                except Exception as err:
                    continue

        if to_json:
            return json.dumps(book)
        
        return book
    
    def get_from_result_list(self, book_id, to_json=False, download=False, save_to=None, convert_to=None) -> str:
        if download:
            if convert_to:
                if convert_to.lower() not in ['pdf', 'mobi', 'epub']:
                    raise ValueError(f'Invalid extension \'{convert_to}\' provided. Only pdf, mobi, or epub is allowed.')
                    
        results = {}

        resp = requests.get(self.url, headers=get_request_headers())
        if resp.status_code != 200:
            raise 'The requested URL did not return 200 OK.'

        parsed_content = html.fromstring(resp.content)
        results_table = parsed_content.xpath('/html/body/table[3]')[0]
        
        for tr in results_table.xpath('tr')[1:]:
            row = {}
            for td in tr.xpath('td'):
                for header, value in zip(['id', 'author(s)', 'title', 'publisher', 'year', 'pages', 'language', 'size', 'extension', 'mirror1', 'mirror2', 'mirror3', 'mirror4', 'mirror5', 'edit'], td):
                    if header in ['mirror1', 'mirror2', 'mirror3', 'mirror4', 'mirror5', 'edit'] and list(value.iterlinks()):
                        value = list(value.iterlinks())[0][2]
                    
                    row.update({header: value})

            results[row.pop('id')] = row

        try:
            book = results[book_id]
        except KeyError:
            raise KeyError(f'The book id \'{book_id}\' does not exist in this list of results.')

        if download:
            mirrors = [book['mirror1']]
            
            for mirror in mirrors:
                try:
                    self.grab_file_from_mirror(mirror, save_to=save_to, convert_to=convert_to)
                except Exception as err:
                    continue
        
        if to_json:
            return json.dumps(book)
        
        return book
