import unittest
import tempfile
import os
from os.path import exists, join

from todd.db import ToddDB

TEMP_DB_DIR = tempfile.mkdtemp(prefix='todd_test_')


class ToddDBTest(unittest.TestCase):
    def setUp(self):
        os.environ['XDG_DATA_HOME'] = TEMP_DB_DIR

        db_file = join(TEMP_DB_DIR, ToddDB.DEFAULT_DB_FILE_NAME)
        if exists(db_file):
            os.remove(db_file)

    def test_defaults(self):
        self.assertEqual(ToddDB.DEFAULT_DB_FILE_NAME, 'todd.db')

    def test_dbfile_creation(self):
        db = ToddDB()
        db.cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='todo'")
        self.assertEqual(int(db.cursor.fetchone()[0]), 1)

    def test_add(self):
        db = ToddDB()
        test_data = ('header', 'body', ['test', 'tags'])
        db.add('body', header='header', tags=['test', 'tags'])
        db.cursor.execute('SELECT header, body, tags FROM todo')
        self.assertEqual(db.cursor.fetchone(), test_data)


if __name__ == "__main__":
    unittest.main()
