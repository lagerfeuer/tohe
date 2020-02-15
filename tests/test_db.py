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

        db_file = join(TEMP_DB_DIR, 'todd', ToddDB.DEFAULT_DB_FILE_NAME)
        if exists(db_file):
            os.remove(db_file)

    def test_defaults(self):
        self.assertEqual(ToddDB.DEFAULT_DB_FILE_NAME, 'todd.db')
        self.assertEqual(ToddDB._get_default_db_file(), os.path.join(
            TEMP_DB_DIR, 'todd', ToddDB.DEFAULT_DB_FILE_NAME))
        del os.environ['XDG_DATA_HOME']
        self.assertEqual(ToddDB._get_default_db_file(), os.path.join(
            os.environ['HOME'], '.local', 'share', 'todd', ToddDB.DEFAULT_DB_FILE_NAME))
        del os.environ['HOME']
        self.assertRaises(EnvironmentError, ToddDB._get_default_db_file)

    def test_dbfile_creation(self):
        db = ToddDB()
        db.cursor.execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='todo'")
        self.assertEqual(int(db.cursor.fetchone()[0]), 1)
        del os.environ['XDG_DATA_HOME']
        os.environ['HOME'] = TEMP_DB_DIR
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

    def test_get(self):
        db = ToddDB()
        db.add('todo', tags=['test', 'tags'])
        entry = db.get(1)
        self.assertEqual(entry, (1, 'todo', ['test', 'tags']))

    def test_get_fail(self):
        db = ToddDB()
        db.add('todo', tags=['test', 'tags'])
        entry = db.get(3)
        self.assertEqual(entry, Status.FAIL)

    def test_list(self):
        db = ToddDB()
        test_data = (1, 'body', ['test', 'tags'])
        db.add('body', tags=['test', 'tags'])
        entries = db.list()
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries.pop(), test_data)

    def test_search_id(self):
        db = ToddDB()
        db.add('MyTODO', ['tag'])
        ref = db.list()
        entries = db.search("MyTODO")
        self.assertEqual(ref, entries)
        entries = db.search("MyTOD?")
        self.assertEqual(ref, entries)
        entries = db.search("My*")
        self.assertEqual(ref, entries)
        entries = db.search("Your*")
        self.assertEqual([], entries)

    def test_edit_id(self):
        db = ToddDB()
        db.add('body', tags=['test', 'tags'])
        # todo
        status = db.edit(id=1, todo='changed body')
        self.assertEqual(status, Status.OK)
        db.cursor.execute('SELECT todo FROM todo')
        self.assertEqual(db.cursor.fetchone()[0], 'changed body')
        # tags
        status = db.edit(id=1, tags='notag')
        self.assertEqual(status, Status.OK)
        db.cursor.execute('SELECT tags FROM todo')
        self.assertEqual(db.cursor.fetchone()[0], ['notag'])

    def test_edit_wrong_id(self):
        db = ToddDB()
        db.add('body', tags=['test', 'tags'])
        # todo
        status = db.edit(id=2, todo='changed body')

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
