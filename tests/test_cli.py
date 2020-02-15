import unittest

from todd import __version__


class TestCLI(unittest.TestCase):

    def test_version(self):
        self.assertEqual(__version__, '0.1.0')


if __name__ == "__main__":
    unittest.main()
