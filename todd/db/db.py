import os
import sys
import sqlite3
from typing import Optional, List, Union

from todd.log import *  # pylint: disable=unused-wildcard-import
from todd.util.status import Status

Id = Union[List[int], int]
Tags = Union[List[str], str]


def adapt_list(lst) -> str:
    """Adapt list entries before writing to database.

    This function takes a list and serializes it in order to
    write it to the sqlite database as string.
    """
    return '|'.join(lst)


def convert_tags(tags) -> list:
    """Convert list entries after fetching it from the database.

    This function takes a serialized list entry for tags and deserializes it
    to return a Python list.
    """
    return [tag.decode('utf-8') for tag in tags.split(b'|')]


class ToddDB:
    """Class representing a Todd instance, including the database connection to
    the sqlite storage.

    This class exposes methods to manipulate the database, like add, edit, delete and list.
    """
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

    def __init__(self, db_file: Optional[str] = None) -> None:
        if not db_file:
            self.db_file = ToddDB._get_default_db_file()
        else:
            self.db_file = db_file
        INFO('DB file is: %s' % self.db_file)
        sqlite3.register_adapter(list, adapt_list)
        sqlite3.register_converter('tags', convert_tags)

        try:
            self.conn = sqlite3.connect(
                self.db_file, detect_types=sqlite3.PARSE_DECLTYPES)
            self.cursor = self.conn.cursor()
            self.cursor.execute("""CREATE TABLE IF NOT EXISTS todo (
            id INTEGER PRIMARY KEY,
            todo TEXT NOT NULL,
            tags TAGS DEFAULT ''
            )""")
            self.conn.commit()
        except Exception as e:
            ERROR('DB connection: %s' % e)
            sys.exit(1)

    def __del__(self) -> None:
        self.conn.close()

    def count(self) -> int:
        return self.cursor.execute('SELECT COUNT(*) FROM todo').fetchone()[0]

    def add(self, todo: str, tags: Optional[List[str]] = None) -> Status:
        try:
            self.cursor.execute('INSERT INTO todo(todo, tags) VALUES (?,?)',
                                (todo, tags))
            self.conn.commit()
        except sqlite3.DatabaseError as e:
            ERROR("Database error: %s" % e)
            return Status.FAIL
        return Status.OK

    def list(self, tags: Optional[Tags] = None) -> list:
        # TODO add support for tags
        self.cursor.execute('SELECT * FROM todo')
        entries = self.cursor.fetchall()
        return entries

    def search(self, term: Union[List[str], str], wildcards: bool = True) -> List[int]:
        return []

    def edit(self, id: int) -> Status:
        return Status.NOT_IMPLEMENTED

    def delete(self,
               id: Optional[Id] = None,
               tags: Optional[Tags] = None) -> Status:
        if id is None and tags is None:
            raise RuntimeError(
                'DELETE was called, but neither id nor tags was supplied.')

        # FIXME ugly code section
        # FIXME if id and tags are supplied, exit or include both in query?

        if isinstance(id, int) or isinstance(id, str):
            id = [id]
        if isinstance(tags, int) or isinstance(tags, str):
            tags = [tags]

        conditions: List[str] = []
        if id is not None:
            conditions.extend(['id = %s' % str(e) for e in id])
        if tags is not None:
            conditions.extend(['tag = %s' % e for e in tags])

        query = 'DELETE FROM todo WHERE '
        query += ' OR '.join(conditions)
        self.cursor.execute(query)
        self.conn.commit()
        return Status.OK
