import unittest
import tempfile
import os
from os.path import exists, join

import todd.db
# from todd.db import *

TEMP_DB_DIR = tempfile.mkdtemp(prefix='todd_test_')


class ToddDBTest(unittest.TestCase):
    def setUp(self):
        os.environ['XDG_DATA_HOME'] = TEMP_DB_DIR

        db_file = join(TEMP_DB_DIR, ToddDB.DEFAULT_DB_FILE_NAME)
        if exists(db_file):
            os.remove(db_file)

    def test_add(self):
        self.assertTrue(False)

if __name__ == "__main__":
    unittest.main()