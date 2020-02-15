import unittest

from todd.cli import __VERSION__


class TestCLI(unittest.TestCase):

    def test_version(self):
        self.assertEqual(__VERSION__, '0.1.0')


if __name__ == "__main__":
    unittest.main()
