import unittest

from festoon.docstring_tools import docfill


class TestDocfill(unittest.TestCase):
    def test_doc_is_filled(self):

        @docfill("foo", bar="baz")
        def func():
            """{0} {bar}"""

        self.assertEqual("foo baz", func.__doc__)
