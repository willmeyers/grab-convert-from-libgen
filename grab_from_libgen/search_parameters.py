from abc import ABC, abstractmethod


def get_search_request_url(topic: str, **parameters):
    base_url = ''
    
    if topic == 'sci-tech':
        base_url = 'https://libgen.is/search.php'

    if topic == 'fiction':
        base_url = 'http://libgen.rs/fiction/'

    query_string = '?'

    for parameter, value in parameters.items():
        if value is not None:
            query_string += f'{parameter}={value}&'

    return f'{base_url}{query_string}'


class SearchParameters(ABC):
    def __init__(self, **parameters):
        self.parameters = parameters
        super().__init__()

    @abstractmethod
    def are_valid(self) -> bool:
        pass

    @abstractmethod
    def url(self) -> str:
        pass


class SciTechSearchParameters(SearchParameters):
    def __init__(self, **parameters):
        super().__init__(**parameters)

        self.q: str = self.parameters.get('q')
        self.sort: str = self.parameters.get('sort')
        self.sortmode: str = self.parameters.get('sortmode')
        self.column: str = self.parameters.get('column')
        self.phrase: str = self.parameters.get('phrase')
        self.res: str = self.parameters.get('res')
        self.view: str = self.parameters.get('view')
        self.open: str = self.parameters.get('open')
        self.page: int = self.parameters.get('page')

    def are_valid(self) -> bool:
        return True

    @property
    def url(self) -> bool:
        return get_search_request_url('sci-tech', 
            req=self.q,
            sort=self.sort,
            sortmode=self.sortmode,
            column=self.column,
            phrase=self.phrase,
            rest=self.res,
            view=self.view,
            open=self.open,
            page=self.page
        )


class FictionSearchParameters(SearchParameters):
    def __init__(self, **parameters):
        super().__init__(**parameters)

        self.q: str = self.parameters.get('q')
        self.criteria: str = self.parameters.get('criteria')
        self.language: str = self.parameters.get('language')
        self.format: str = self.parameters.get('format')
        self.wildcard: str = self.parameters.get('wildcard')

    def are_valid(self) -> bool:
        return True

    @property
    def url(self) -> str:
        return get_search_request_url('fiction', 
            q=self.q,
            criteria=self.criteria,
            language=self.language,
            format=self.format,
            wildcard=self.wildcard
        )
