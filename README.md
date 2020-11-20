# grab-from-libgen
An easy API for searching and downloading books from Libgen.

## Before Installing

**Be sure that you have installed Calibre and have added the necessary `ebook-convert` command to your path!**

[calibre](https://calibre-ebook.com/) is "a powerful and easy to use e-book manager". It's also free, open-source, and super easy to use.

You can install an calibre executable, through MacOS Homebrew, compile from source... pick your poison. They only thing you need to be sure of 
is the command `ebook-convert` is in your PATH.

## Install

Install by 

```
pip install grab-from-libgen
```

## Quickstart

The example below shows to grab the first book returned from a search and save it as a pdf.

```python
from grab_from_libgen import LibgenSearch

res = LibgenSearch(req='test')

res.first(save_to='.', convert_to='pdf')
```

## Documentation

#### Search Parameters

This package represents Libgen URL parameters internally as an object `SearchParameters`.

| Parameter | Usage |
|-----------|-------|
| req       | The phrase used to search books |


#### get_results

`get_results(self) -> OrderedDict`

Caches and returns results based on the search parameters the `LibgenSearch` objects was initialized with. Results are ordered
in the same order as they would be displayed on libgen itself with the book's id serving as the key.

#### first

`first(save_to: str = None, convert_to: str = None) -> Dict`

Returns a the first book (as a dictionary) from the cached or obtained results.


#### get_book_from_results_by_id

`get_book_from_results_by_id(book_id: int, save_to=None, convert_to=None) -> Dict`

Returns a book that matches the given id of a book (as a dictionary) from the cached or obtained results. If no book is found,
an error is raised.