import json
import pathlib
from dataclasses import dataclass
from typing import Optional, List

import requests
import lxml.html as html

from .search_config import SearchParameters, get_request_headers, get_request_url
from . import convert


class LibgenSearch:
    url = None

    def __init__(self, parameters: SearchParameters):
        if self.valid_parameters(parameters):
            self.url = search_config.get_request_url(parameters)

    def valid_parameters(parameters: SearchParameters) -> bool:
        if len(parameters.req) < 2:
            raise ValueError('Parameter \'req\' must be >= 2 characters.')
        
        return True

    def grab_file_from_mirror(self, mirror_url: str, mirror_number=1, save_to=None, convert_to=None):
        if save_to is None:
            raise ValueError('A location to save the file (save_to) must be provided.')

        if convert_to:
            if convert_to.lower() not in ['pdf', 'epub', 'mobi']:
                raise ValueError(f'Invalid extension \'{convert_to}\' provided. Only pdf, mobi, or epub is allowed.')

        resp = requests.get(mirror_number)


    def results(self, download=False, save_to=None, convert_to=None) -> str:
        """ Returns a list of search results. """
        if download:
            if convert_to:
                if convert_to.lower() not in ['pdf', 'mobi', 'epub']:
                    raise ValueError(f'Invalid extension \'{convert_to}\' provided. Only pdf, mobi, or epub is allowed.')
        
        results = {}

        resp = requests.get(self.url, headers=search_config.get_request_headers())
        if resp.status_code != 200:
            raise 'The requested URL did not return 200 OK.'

        parsed_content = html.fromstring(resp.content())
        results_table = parsed_content.xpath('/html/body/table[3]')[0]
        
        for tr in results_table.xpath('tr')[1:]:
            row = {}
            for td in tr.xpath('td'):
                for header, value in zip(['id', 'author(s)', 'title', 'publisher', 'year', 'pages', 'language', 'size', 'extension', 'mirror1', 'mirror2', 'mirror3', 'mirror4', 'mirror5', 'edit'], td):
                    if header in ['mirror1', 'mirror2', 'mirror3', 'mirror4', 'mirror5', 'edit'] and list(value.iterlinks()):
                        value = list(value.iterlinks())[0][2]
                    
                    row.update({header: value})

            results[row.pop('id')] = row

        return json.dumps(results)

    def first(self, download=False, save_to=None, convert_to=None) -> str:
        """ Returns the first result from the list of search results. """
        if download:
            if convert_to:
                if convert_to.lower() not in ['pdf', 'mobi', 'epub']:
                    raise ValueError(f'Invalid extension \'{convert_to}\' provided. Only pdf, mobi, or epub is allowed.') 

        results = {}

        resp = requests.get(self.url, headers=search_config.get_request_headers())
        if resp.status_code != 200:
            raise 'The requested URL did not return 200 OK.'

        parsed_content = html.fromstring(resp.content())
        results_table = parsed_content.xpath('/html/body/table[3]')[0]
        
        for tr in results_table.xpath('tr')[1:2]:
            row = {}
            for td in tr.xpath('td'):
                for header, value in zip(['id', 'author(s)', 'title', 'publisher', 'year', 'pages', 'language', 'size', 'extension', 'mirror1', 'mirror2', 'mirror3', 'mirror4', 'mirror5', 'edit'], td):
                    if header in ['mirror1', 'mirror2', 'mirror3', 'mirror4', 'mirror5', 'edit'] and list(value.iterlinks()):
                        value = list(value.iterlinks())[0][2]
                    
                    row.update({header: value})

            results[row.pop('id')] = row

        return json.dumps(results)
