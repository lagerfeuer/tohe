import os
import sys
import sqlite3
from typing import Optional, List

from todd.log import *

def adapt_list(lst):
    return '|'.join(lst)

def convert_tags(tags):
    return [tag.decode('utf-8') for tag in tags.split(b'|')]


class ToddDB:
    DEFAULT_DB_FILE_NAME = 'todd.db'

    @staticmethod
    def _get_default_db_file() -> str:
        """Return the directory which contains the database file.
        Returns: database directory path (str)
        """
        data_home = os.getenv('XDG_DATA_HOME')
        if data_home is None:
            data_home = os.getenv('HOME')
            if data_home is not None:
                data_home = os.path.join(data_home, '.local', 'share')

        if data_home is None:
            raise EnvironmentError(
                'No $XDG_DATA_HOME or $HOME defined. Exiting.')

        return os.path.join(data_home, ToddDB.DEFAULT_DB_FILE_NAME)

    def __init__(self, db_file: Optional[str] = None):
        if not db_file:
            self.db_file = ToddDB._get_default_db_file()
        else:
            self.db_file = db_file
        INFO('DB file is: %s' % self.db_file)
        sqlite3.register_adapter(list, adapt_list)
        sqlite3.register_converter('tags', convert_tags)

        try:
            self.conn = sqlite3.connect(self.db_file, detect_types=sqlite3.PARSE_DECLTYPES)
            self.cursor = self.conn.cursor()
            self.cursor.execute("""CREATE TABLE IF NOT EXISTS todo (
            id INTEGER PRIMARY KEY,
            header TEXT,
            body TEXT NOT NULL,
            tags TAGS DEFAULT ''
            )""")
            self.conn.commit()
        except Exception as e:
            ERROR('DB connection: %s' % e)
            sys.exit(1)

    def __del__(self):
        self.conn.close()

    def add(self, body: str, header: Optional[str] = None, tags: Optional[List[str]] = None):
        self.cursor.execute('INSERT INTO todo(header, body, tags) VALUES (?,?,?)',
                            (header, body, tags))
        self.conn.commit()
