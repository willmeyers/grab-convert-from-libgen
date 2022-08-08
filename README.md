# grab-fork-from-libgen
A fork of grab-convert-from-libgen, which is an easy API/wrapper for searching and downloading books from Libgen.

## A disclaimer  
First and foremost, this library makes no effort in rate-limiting itself.  
While using it, you need to know that you are using a free "API", that requires no API key.  
Use it with care.  

There's a lot of ratelimiting options for Python out there.  
[ratelimit](https://github.com/tomasbasham/ratelimit) is a good starting point.  

## Before Installing

**If you want to download books, be sure that you have installed Calibre and have added the necessary `ebook-convert` command to your path!**

[calibre](https://calibre-ebook.com/) is "a powerful and easy to use e-book manager". It's also free, open-source, and super easy to use.

You can install an calibre executable, through MacOS Homebrew, compile from source... pick your poison. They only thing you need to be sure of 
is the command `ebook-convert` is in your PATH.

If you choose not to do so, you can still use this library for searching on LibraryGenesis and scraping metadata.

## Install

Install by 

```
pip install grab-fork-from-libgen
```

### Migrating
If you already have `grab-convert-from-libgen` installed, run this:  
```
pip uninstall grab-convert-from-libgen
```

And then:
```python
# Change
from grab_convert_from_libgen import *
# To
from grab_fork_from_libgen import *
```
That's it. Your code will still work as expected, and you can implement the new features as you go.

## v3 Overview

This new version includes some new features, all of them being optional and not code-breaking.

New async classes.  
New filtering option.  
You can now get a book's cover. (from 3lib or LibraryRocks)  
You can now get a book's direct download links. (from LibraryLol)  
You can now get a book's description (if it has one) (also from LibraryLol).  
You can now get pagination info (Check how many pages and if there's a next page in your search.)  
Fixed "page" query in Fiction search.  
Some small fixes for edge cases.  

In this version, every entry has these new properties attached:  
It's md5 (e.g.: `B86D006359AD3939907D951A20CB4EF1`)  
It's topic (either `fiction` or `sci-tech`)  
And now fiction results also have `extension` and `size` to improve consistency.

All these features are **OPT-IN**.  
This means your code won't break when migrating to this fork, and you may use the new functions how you want to.

**PS**: Pagination is slower. You are adding the extra overhead of rendering javascript, so expect longer wait times.

## Quickstart

The example below shows how to grab the first book returned from a search and save it to your current working directory as a pdf.

```python
from grab_fork_from_libgen import LibgenSearch

res = LibgenSearch('sci-tech', q='test')

res.first(convert_to='pdf')
```

This is an example that gets and downloads the first book that matches the given filter(s).

```python
from grab_fork_from_libgen import LibgenSearch

res = LibgenSearch('fiction', q='test')

res.get(title='a title', save_to='.')
# Or
res.get(language="English", save_to='.')
```

This one shows basic search usage (with pagination on).
```python
from grab_fork_from_libgen import LibgenSearch

# Refer to the documentation below to learn more about query filters.
libgen = LibgenSearch('sci-tech', q='test', res=100)
# True as an argument means you opt-in in pagination info.
libgen_search = libgen.get_results(True)

pagination_info = libgen_search["pagination"]
libgen_results = libgen_search["data"]
```

And for the async versions:
```python
from grab_fork_from_libgen import AIOLibgenSearch

async def libgen():
    # Refer to the documentation below to learn more about query filters.
    libgen = AIOLibgenSearch('fiction', q='test', language='English', criteria="title")
    # We opt-out of pagination info this time...
    # So the function returns your results directly
    libgen_results = await libgen.get_results()
    
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

`page`: Page number.

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

`get_results(self, pagination: Optional[bool]) -> OrderedDict`

Caches and returns results based on the search parameters the `LibgenSearch` objects was initialized with. 
Takes one optional boolean argument.

If it's **True**: 
Returns a dict, with two values, the first one being:  
```
pagination = {
    "current_page": `int`
    "total_pages": `int`
    "has_next_page": either `True` or `False`
}
```
And the second one being an ordered dict, which is your search results:
```
data = {
    0: "{first_book_title, first_book_md5, ...}"
    1: "{second_book_title, second_book_md5, ...}"
    ...
}
```
If the user sets pagination to **False** or doesn't provide any value, this OrderedDict is the only result returned.

Please refer to `Quickstart` for a quick guide.

Results are ordered in the same order as they would be displayed on libgen itself with the book's id serving as the key.

The async version and pagination info is powered by [requests-html](https://github.com/psf/requests-html)

**Notice**:  
Using pagination will download Chrominium to your home folder on your first run. e.g.: "~/.pyppeteer/".
This only happens once. This happens because LibraryGenesis pagination uses javascript, 
which is not rendedered by default in the HTML, to render its pagination system.  
Because of this, the pagination system is generally slower than its counterpart.

It's important to pay attention to this if you use services (like Heroku Free Tier) with limited storage space and low timeouts.

**Notice 2**:  
For now, there's a `'file'` attribute on fiction results that may seem redundant when you have `'extension'` and
`'size'`. That's because these are only available on this fork, and i didn't want to break people's logic, regex etc
when migrating.  
This probably will be removed in a distant future, just ignore it for now.

#### first

`first(save_to: str = None, convert_to: str = None) -> Dict`

Returns the first book (as a dictionary) from the cached or obtained results.
You can provide a `save_to: str` value if you want to download the book.
And you can convert it using `convert_to: str`. Only `pdf`, `epub` and `mobi` are allowed. 
If you want to get a specific book based on filters, please refer to `get`.

The async version is powered by [aiofiles](https://github.com/Tinche/aiofiles)

#### get

`get(save_to: str = None, convert_to: str = None, **filters) -> Dict`

Returns the first book (as a dictionary) from the cached or obtained results that match any given filter parameter.
You can provide a `save_to: str` value if you want to download the book.
And you can convert it using `convert_to: str`. Only `pdf`, `epub` and `mobi` are allowed.

The filters can be anything that's inside a book entry.
For example:
````python
filters = {
    "author(s)": "Adams, Jennifer",
    "language": "English"
}
````
This method returns a book if it's match **ANY** of the filters, that means it will return even if it doesn't match 
**all** of them.

If you want to match more than one book or have more strict filtering, refer to `get_all`.

The async version is powered by [aiofiles](https://github.com/Tinche/aiofiles)

#### get_all

`get_all(**filters) -> Dict`

This method returns all books that match the given filters.  

It differs from `get` in two ways:  
First, it will return **all** books that match, not just the first one.  
Second, a book will only be matched if **all** of the filters match.

#### **Why can't i save the books directly?**
This would go directly against what was mentioned about API rates.  
Downloading, say, 30 books on one go would probably mean a block from either LibraryGenesis or Librarylol (the main download
provider).  
It's also harder to implement rate limiting in a method like this.

Of course, you are free to implement your own logic using `get`.

### Metadata
This class holds the methods responsible for metadata scraping.

#### Quickstart:
```python
# First, import the Metadata class from grab_fork_from_libgen.
from grab_fork_from_libgen import LibgenSearch, Metadata

# ...
# pagination=True means you opt-in for pagination info.
my_results = LibgenSearch.get_results(pagination=True)


# Get the values from your search results
search_results = my_results["data"]

# Get the info from the first entry in the results.
md5 = search_results[0]["md5"]
topic = search_results[0]["topic"]

# Instantiate a new Metadata class.
# Please read the timeout documentation on the official requests library docs.
meta = Metadata(md5, topic, timeout=(9, 18))

# And use the respective methods.
cover = meta.get_cover()
d_links_and_desc = meta.get_metadata()

```
#### Metadata - Class
The `Metadata` class takes three arguments, one being optional:\

`md5` = An `string`, a code used to identify the file on LibraryGenesis and others databases.

`topic` = An `string`, the topic of the file on LibraryGenesis' database. Either `fiction` or `sci-tech`.

`timeout (optional)` = Either `int`, `tuple` or `None`. Defaults to `None`, which equals to infinite timeout.\

Please read more about using tuples in the official `requests` 
[docs](https://docs.python-requests.org/en/latest/user/advanced/#timeouts).

It's good practice to always provide a timeout value. As both the cover and download links providers can be down or
slow at any given moment.\
If they take too long, your code will hang.

You can expect a `MetadataError` if something goes wrong.

#### Metadata - Methods
`get_cover` returns an `string`, which is the direct link to that file's cover image. If no cover is found, returns a
`MetadataError`.

`get_metadata` returns a `tuple`, the first value being a `dict` of all the direct download links of the file, and the
second value being the file's description.   

Throws a `MetadataError` if no download link is found.
If no description is found, returns `None` on the second value instead.

Please do note that none of these methods are rate-limited. If you abuse them, you will get blocked.  
From personal experience, `1500ms-2000ms` between each call is probably safe.

### Async Classes
#### AIOLibgenSearch
This class is now truly async, even the file operations.
Converting books itself (using Calibre) is still synchronous until further testing.

Async I/O is provided by `aiofiles` and `requests-html`.

#### AIOMetadata
Async methods in this classes are made using `requests-html`.
