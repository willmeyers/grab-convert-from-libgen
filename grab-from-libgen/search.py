import json
import pathlib
from dataclasses import dataclass
from typing import Optional, List

import requests
import lxml.html as html

from . import search_config
from . import convert


class LibgenSearch:
    url = None

    def __init__(self, parameters):
        if self.valid_parameters(parameters):
            self.url = search_config.get_request_url(parameters)

    def valid_parameters(parameters):
        if len(parameters.req) < 2:
            raise ValueError('Parameter \'req\' must be >= 2 characters.')
        
        return True

    def results(self, download=False, save_to=None, convert_to=None):
        """ Returns a list of search results. """
        if download:
            if convert_to:
                if convert_to.lower() not in ['pdf', 'mobi', 'epub']:
                    raise ValueError(f'Invalid extension \'{convert_to}\' provided. Only pdf, mobi, or epub is allowed.')
        
        resp = requests.get(self.url, headers=search_config.get_request_headers())
        if resp.status_code != 200:
            raise 'The requested URL did not return 200 OK.'

        parsed_content = html.fromstring(resp.content())
        results = parsed_content.xpath('')

    def first(self, download=False, save_to=None, convert_to=None):
        """ Returns the first result from the list of search results. """
        if download:
            if convert_to:
                if convert_to.lower() not in ['pdf', 'mobi', 'epub']:
                    raise ValueError(f'Invalid extension \'{convert_to}\' provided. Only pdf, mobi, or epub is allowed.') 
