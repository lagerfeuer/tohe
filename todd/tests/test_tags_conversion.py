from todd.db import adapt_list, convert_tags

import unittest


class TestConversion(unittest.TestCase):
    def test_convert_in(self):
        self.assertEqual('test|todo|cmd',
                         adapt_list('test todo cmd'.split()))

    def test_convert_out(self):
        self.assertEqual('test todo cmd'.split(),
                         convert_tags(b'test|todo|cmd'))
