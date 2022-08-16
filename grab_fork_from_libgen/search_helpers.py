from lxml import html
from typing import Any
from collections import OrderedDict

from grab_fork_from_libgen.exceptions import LibgenError
import re


def fiction_results_builder(content: Any, topic: str) -> OrderedDict:
    results = OrderedDict()
    html_tree = html.fromstring(content)

    try:
        results_table = html_tree.xpath("//table")[0]
    except KeyError:
        raise LibgenError("No results returned.")
    except IndexError:
        raise LibgenError("No results returned, this may be an parameter issue.")

    for idx, tr in enumerate(results_table.xpath("//tr")[1:]):
        row = {}
        for header, value in zip(
                [
                    "author(s)",
                    "series",
                    "title",
                    "language",
                    "file",
                    "mirror1",
                    "mirror2",
                    "mirror3",
                    "edit",
                ],
                tr.getchildren(),
        ):
            if header in ["mirror1", "mirror2", "mirror3", "edit"] and list(
                    value.iterlinks()
            ):
                value = list(value.iterlinks())[0][2]
            else:
                value = (
                    value.text_content().strip().replace("\n", "").replace("\t", "")
                )

            row.update({header: value})

        mirror1 = row.get("mirror1")
        md5 = re.sub('[\\Wa-z]', "", mirror1)
        row["md5"] = md5
        row["topic"] = topic
        # This changes \xa0 to a whitespace character.
        row["file"] = re.sub("\xa0", " ", row.get("file"))

        file_info = row.get("file")
        extension = re.findall(".*/", file_info)[0]
        extension = re.sub(" /", "", extension)
        size = re.findall("/.*", file_info)[0]
        size = re.sub("/ ", "", size)
        row["extension"] = extension.lower()
        row["size"] = size

        results[idx] = row

    return results


def scitech_results_builder(content: Any, topic: str) -> OrderedDict:
    results = OrderedDict()
    html_tree = html.fromstring(content)
    try:
        results_table = html_tree.xpath("/html/body/table[3]")[0]
    except KeyError:
        raise LibgenError("No results returned.")
    except IndexError:
        raise LibgenError("No results returned, this may be an parameter issue.")

    for idx, tr in enumerate(results_table.xpath("tr")[1:]):
        row = {}
        for header, value in zip(
                [
                    "id",
                    "author(s)",
                    "title",
                    "publisher",
                    "year",
                    "pages",
                    "language",
                    "size",
                    "extension",
                    "mirror1",
                    "mirror2",
                    "mirror3",
                    "mirror4",
                    "mirror5",
                    "edit",
                ],
                tr.getchildren(),
        ):
            if header in [
                "mirror1",
                "mirror2",
                "mirror3",
                "mirror4",
                "mirror5",
                "edit",
            ] and list(value.iterlinks()):
                value = list(value.iterlinks())[0][2]
            else:
                value = (
                    value.text_content().strip().replace("\n", "").replace("\t", "")
                )

            row.update({header: value})
        mirror1 = row.get("mirror1")
        md5 = re.sub('[\\Wa-z]', "", mirror1)
        row["md5"] = md5
        row["topic"] = topic
        results[idx] = row

    return results
