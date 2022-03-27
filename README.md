# grab-convert-from-libgen
An easy API for searching and downloading books from Libgen.

## Before Installing

**Be sure that you have installed Calibre and have added the necessary `ebook-convert` command to your path!**

[calibre](https://calibre-ebook.com/) is "a powerful and easy to use e-book manager". It's also free, open-source, and super easy to use.

You can install an calibre executable, through MacOS Homebrew, compile from source... pick your poison. They only thing you need to be sure of 
is the command `ebook-convert` is in your PATH.

## Install

Install by 

```
pip install grab-convert-from-libgen
```

## Quickstart

The example below shows to grab the first book returned from a search and save it to your current working directory as a pdf.

```python
from grab_from_libgen import LibgenSearch

res = LibgenSearch('sci-tech', q='test')

res.first(convert_to='pdf')
```

This is an example the gets and downloads a book that matches a given title.

```python
from grab_from_libgen import LibgenSearch

res = LibgenSearch('fiction', q='test')

res.get(title='a title', save_to='.')
```

You must specify a `topic` when creating a search instance. Choices are `fiction` or `sci-tech`.

## Documentation

Only search parameters marked as required are needed when searching.

### Libgen Non-fiction/Sci-tech
#### Search Parameters

`q`: The search query (required)

`sort`: Sort results. Choices are `def` (default), `id`, `title`, `author`, `publisher`, `year`

`sortmode`: Ascending or decending. Choices are `ASC` or `DESC`

`column`: The column to search against. Choices are `def` (default), `title`, `author`, `publisher`, `year`, `series`, `ISBN`, `Language`, or `md5`.

`phrase`: Search with mask (word*). Choices are `0` or `1`.

`res`: Results per page. Choices are `25`, `50`, or `100`.

`page`: Page number

### Libgen Fiction
#### Search Parameters

`q`: The search query (required)

`criteria`: The column to search against. Choices are `title`, `authors`, or `series`.

`language`: Language code

`format`: File format

`wildcard`: Wildcarded words (word*). Set to `1`.

`page`: Page number

### LibgenSearch
#### get_results

`get_results(self) -> OrderedDict`

Caches and returns results based on the search parameters the `LibgenSearch` objects was initialized with. Results are ordered
in the same order as they would be displayed on libgen itself with the book's id serving as the key.

#### first

`first(save_to: str = None, convert_to: str = None) -> Dict`

Returns a the first book (as a dictionary) from the cached or obtained results.

#### get

`get(save_to: str = None, convert_to: str = None, **filters) -> Dict`

Returns the first book (as a dictionary) from the cached or obtained results that match the given filter parameters.

The filter parameters must be pulled from the keys that the book dictionary object returns.
