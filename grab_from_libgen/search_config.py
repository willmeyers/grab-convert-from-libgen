from dataclasses import asdict


def get_request_headers():
    return {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://libgen.rs/',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }


def get_request_url(search_parameters):
    query_string = '?'

    for parameter, value in asdict(search_parameters).items():
        if value is not None:
            query_string += f'{parameter}={value}&'

    return f'https://libgen.is/search.php{query_string}'
