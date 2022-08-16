import pathlib
import re
import urllib
from collections import OrderedDict
from typing import Dict
from bs4 import BeautifulSoup
from typing import Union, Optional

from requests_html import HTMLSession
import lxml.html as html

from . import mirrors
from .search_helpers import scitech_results_builder, fiction_results_builder
from .search_parameters import SciTechSearchParameters, FictionSearchParameters
from .search_config import get_request_headers
from .convert import ConversionError, convert_file_to_format
from .exceptions import LibgenError, InvalidSearchParameter


class LibgenSearch:
    base_url = None
    url = None

    results = None

    search_parameter_objects = {
        "sci-tech": SciTechSearchParameters,
        "fiction": FictionSearchParameters,
    }

    mirror_objects = {
        "library.lol": mirrors.LibrarylolMirror,
        "libgen.lc": mirrors.LibgenlcMirror,
    }

    def __init__(self, topic: str, **parameters):
        if topic not in ["sci-tech", "fiction"]:
            raise LibgenError(
                f"Topic '{topic}' is not valid. Valid topics are sci-tech or fiction"
            )

        self.topic = topic

        self.search_parameters = self.search_parameter_objects[self.topic](**parameters)

        if self.search_parameters.are_valid():
            self.url = self.search_parameters.url
        else:
            raise InvalidSearchParameter("Given search parameters are not valid.")

    def _grab_file_from_mirror(
            self, mirror_url: str, save_to: pathlib.Path, convert_to=None
    ) -> str:
        """Downloads file from a mirror url. If the given mirror url does not exist, it raises an error.
        Othereise, goes through the motions of downloads, converts, and saves the file to a specified path.
        """
        netloc = urllib.parse.urlparse(mirror_url).netloc

        try:
            mirror = self.mirror_objects[netloc](mirror_url)
            filename, file_content = mirror.download_file()

        except KeyError:
            raise KeyError("The given mirror URL does not match any current scrapers.")

        if filename is None:
            raise LibgenError(
                f"Could not download file from url {mirror_url}. This may be an internal issue"
            )

        with open(filename, "wb+") as fo:
            fo.write(file_content)

        if convert_to:
            if convert_to.lower() not in {"pdf", "epub", "mobi"}:
                raise ConversionError(
                    f"Invalid extension '{convert_to}' provided. Only pdf, mobi, or epub is allowed."
                )

            filename = convert_file_to_format(filename, convert_to=convert_to)

        return filename

    def _save_file(self, book: Dict, save_to: str, convert_to: str = None) -> None:
        """Given a book with list of mirror urls, run through all mirror urls until a valid response is
        returned. Executes `grab_file_from_mirror`.
        """
        save_to = pathlib.Path(save_to)
        mirror_links = None

        finished = False
        if self.topic == "sci-tech":
            mirror_links = [book["mirror1"], book["mirror2"]]
        elif self.topic == "fiction":
            mirror_links = [book["mirror1"]]
        else:
            raise LibgenError("Invalid topic.")

        for mirror in mirror_links:
            try:
                if not finished:
                    completed = self._grab_file_from_mirror(
                        mirror, save_to=save_to, convert_to=convert_to
                    )
                    if completed:
                        finished = True

            except Exception as err:
                if mirror == mirrors[-1]:
                    raise err
                else:
                    continue

    def _get_scitech_results(self, pagination: bool) -> Union[OrderedDict, Dict]:
        """Returns a dictionary of search results."""
        session = HTMLSession()

        resp = session.get(self.url, headers=get_request_headers())
        if resp.status_code != 200:
            raise LibgenError("The requested URL did not have status code 200.")

        results = scitech_results_builder(resp.content, self.topic)

        if pagination:
            has_next_page: bool = False

            resp.html.render()
            try:
                soup = BeautifulSoup(resp.html.raw_html, "lxml")
                paginator = soup.find("div", {"id": "paginator_example_bottom"})
                paginator_list = paginator.select("table > tbody > tr > td")
                # The total amount of pages avaiable.
                # One page equals to 1, and so on.
                total_pages = len(paginator_list)

            except (KeyError, AttributeError):
                total_pages = 1

            try:
                # Converts to int because the user may provide str or int as page.
                current_page: int = int(self.search_parameters.page)
            except TypeError:
                # If no page is found (meaning the user didn't provide one)
                current_page = 1

            # Sets has_next_page to True if current page is less than total pages.
            if total_pages is not None:
                has_next_page = True if current_page < total_pages else False

            pagination_data = {
                "current_page": current_page,
                "total_pages": total_pages,
                "has_next_page": has_next_page
            }

            # Weird naming to avoid messing too much with people's code.
            results_data = {
                "pagination": pagination_data,
                "data": results
            }

            self.results = results_data

            return results_data

        self.results = results

        return results

    def _get_fiction_results(self, pagination: bool) -> Union[OrderedDict, Dict]:
        session = HTMLSession()

        resp = session.get(self.url, headers=get_request_headers())
        if resp.status_code != 200:
            raise LibgenError("The requested URL did not have status code 200.")

        results = fiction_results_builder(resp.content, self.topic)

        if pagination:
            has_next_page: bool = False

            # This renders the page and enables javascript-based content
            resp.html.render()
            try:
                soup = BeautifulSoup(resp.html.raw_html, "lxml")
                # Selects the third select element on the page, which is the pagination one.
                paginator = soup.select("select")[3]
                # Then selects all the options inside it.
                paginator_list = paginator.select("option")
                # The total amount of pages avaiable.
                # One page equals to 1, and so on.
                total_pages: int | None = len(paginator_list)

            except (KeyError, IndexError):
                total_pages = 1

            try:
                current_page: int = int(self.search_parameters.page)
            except TypeError:
                # If no page is found (meaning the user didn't provide one)
                current_page: int = 1

            # Sets has_next_page to True if current page is less than total pages.
            if total_pages is not None:
                has_next_page = True if current_page < total_pages else False

            pagination = {
                "current_page": current_page,
                "total_pages": total_pages,
                "has_next_page": has_next_page
            }

            # Weird naming to avoid messing too much with people's code.
            results_data = {
                "pagination": pagination,
                "data": results
            }

            self.results = results_data

            return results_data

        self.results = results

        return results

    def get_results(self, pagination: bool = False) -> Union[OrderedDict, Dict]:
        # Returns both values, but only caches one.
        # This is to avoid messing with other functions such as first() and get().
        # Coding in compliance with someone's code is funny

        if self.topic == "sci-tech":
            self.results = self._get_scitech_results(pagination)

        if self.topic == "fiction":
            self.results = self._get_fiction_results(pagination)

        return self.results

    def first(self, save_to: str = None, convert_to: str = None) -> Dict:
        """Returns the first result from the list of search results."""
        if save_to or convert_to:
            if convert_to:
                save_to = "." if save_to is None else save_to

                if convert_to.lower() not in ["pdf", "mobi", "epub"]:
                    raise ConversionError(
                        f"Invalid extension '{convert_to}' provided. Only pdf, mobi, or epub is allowed."
                    )

        if self.results is None:
            self.results = self.get_results()

        this_results: Union[OrderedDict, Dict] = self.results

        # If this_results is a dict (meaning pagination was set to true when calling get_results() )
        if type(this_results) == dict:
            this_results = this_results.get("data")

        try:
            first_book_id = list(this_results.keys())[0]
            book = this_results[first_book_id]
        except (IndexError, KeyError):
            raise LibgenError("Could not grab any book from results list.")

        if save_to:
            self._save_file(book, save_to, convert_to=convert_to)

        return book

    def get(self, save_to: str = None, convert_to: str = None, **filters) -> Dict:
        # Returns a result from a list of filters.
        if save_to or convert_to:
            if convert_to:
                save_to = "." if save_to is None else save_to

                if convert_to.lower() not in ["pdf", "mobi", "epub"]:
                    raise ConversionError(
                        f"Invalid extension '{convert_to}' provided. Only pdf, mobi, or epub is allowed."
                    )

        if self.results is None:
            self.results = self.get_results()
        this_results: Union[OrderedDict, Dict] = self.results
        # If self.results is a dict (meaning pagination was set to true when calling get_results() )
        if type(this_results) == dict:
            this_results = this_results.get("data")

        for book in this_results.values():
            for filter_key in filters.keys():
                try:
                    if book[filter_key] == filters[filter_key]:
                        if save_to:
                            self._save_file(book, save_to, convert_to=convert_to)

                        return book

                    else:
                        continue
                except KeyError:
                    raise LibgenError(
                        f"Invalid filter. Filter '{filter_key}' is not a valid filter."
                    )

        raise LibgenError("No book matches the given filters.")

    def get_all(self, **filters) -> Dict:
        filtered_results = {}

        if self.results is None:
            self.results = self.get_results()

        this_results: Union[OrderedDict, Dict] = self.results

        if type(this_results) == dict:
            this_results = this_results.get("data")

        for book in this_results.values():
            meets_criteria = False
            for filter_key, filter_value in filters.items():
                try:
                    # Checks if the current filter exists and equals to the value inside a book's dict.
                    if book[filter_key] == filter_value:
                        # This runs if a filter matches, meaning that, for now at least, it match **all** the filters.
                        meets_criteria = True
                        continue
                    else:
                        # If one filter doesn't match, then the book doesn't meet all criteria.
                        meets_criteria = False
                        break
                except KeyError:
                    raise LibgenError(
                        f"Invalid filter. Filter '{filter_key}' is not a valid filter."
                    )

            # If, at the end of the loop, the book matches all the filters, then add it to the filtered_results.
            # Since this is still inside the first for loop, it will check for every book in the results' dict.
            if meets_criteria:
                filtered_results.update(book)

        if bool(filtered_results) is False:
            raise LibgenError("No book matches the given filters.")
        return filtered_results
