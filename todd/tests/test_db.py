import unittest
import tempfile
import os
from os.path import exists, join

from todd.db import ToddDB
from todd.util.status import Status

TEMP_DB_DIR = tempfile.mkdtemp(prefix='todd_test_')


# TODO: Add setup function that adds one todo (easier)
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
        db.cursor.execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='todo'")
        self.assertEqual(int(db.cursor.fetchone()[0]), 1)

    def test_add(self):
        db = ToddDB()
        test_data = ('todo', ['test', 'tags'])
        db.add('todo', tags=['test', 'tags'])
        db.cursor.execute('SELECT todo, tags FROM todo')
        self.assertEqual(db.cursor.fetchone(), test_data)
        db.cursor.execute('SELECT COUNT(*) FROM todo')
        self.assertEqual(db.cursor.fetchone()[0], 1)

    def test_list(self):
        db = ToddDB()
        test_data = (1, 'body', ['test', 'tags'])
        db.add('body', tags=['test', 'tags'])
        entries = db.list()
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries.pop(), test_data)

    @unittest.skip("Not implemented")
    def test_search_id(self):
        db = ToddDB()
        status = db.search("MyTODO")
        status = db.search("MyTOD?")
        status = db.search("My*")
        self.assertEqual(status, Status.OK)

    @unittest.skip("Not implemented")
    def test_edit_id(self):
        db = ToddDB()
        status = db.edit(id=1)
        self.assertEqual(status, Status.OK)

    def test_delete_arguments_none(self):
        db = ToddDB()
        self.assertRaises(RuntimeError, db.delete)

    def test_delete_id(self):
        db = ToddDB()
        db.add('todo 1', tags=['tag1', 'tags'])
        db.add('todo 2', tags=['tag2', 'tags'])
        status = db.delete(id=1)
        self.assertEqual(status, Status.OK)
        self.assertEqual(db.count(), 1)
        status = db.delete(id=2)
        self.assertEqual(status, Status.OK)
        self.assertEqual(db.count(), 0)


if __name__ == "__main__":
    unittest.main()
