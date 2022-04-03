import unittest

from grab_convert_from_libgen.search import LibgenSearch


class TestLibgenSearch(unittest.TestCase):
    def setUp(self):
        self.parameters = {
            "q": "Concrete Mathematics",
            "sort": "def",
            "sortmode": "ASC",
            "column": "def",
            "phrase": 0,
            "rest": "25",
            "page": "1",
        }

    def test_libgen_response(self):
        search = LibgenSearch("sci-tech", **self.parameters)
        results = search.get_results()

        self.assertEqual(len(results), 25)


if __name__ == "__main__":
    unittest.main()
