import unittest

from grab_convert_from_libgen.search import LibgenSearch
from grab_convert_from_libgen.metadata import Metadata


class TestLibgenSearch(unittest.TestCase):
    def setUp(self):
        self.parameters = {
            "q": "Concrete Mathematics",
            "sort": "def",
            "sortmode": "ASC",
            "column": "def",
            "phrase": 0,
            "res": "25",
            "page": "1",
        }

    def test_libgen_response(self):
        search = LibgenSearch("sci-tech", **self.parameters)
        results = search.get_results()

        self.assertEqual(len(results), 25)

    def test_pagination(self):
        search = LibgenSearch("sci-tech", **self.parameters)
        results = search.get_results(True)

        self.assertTrue(isinstance(results, dict))

    def test_metadata(self):
        search = LibgenSearch("sci-tech", **self.parameters)
        results = search.get_results()
        md5 = results[0]["md5"]
        topic = results[0]["topic"]

        meta = Metadata(md5, topic)
        self.assertEqual(len(meta.get_metadata()), 2)
        self.assertTrue(isinstance(meta.get_cover(), str))


if __name__ == "__main__":
    unittest.main()
