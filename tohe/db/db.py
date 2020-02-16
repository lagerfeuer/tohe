import os
import sys
import sqlite3
from typing import Optional, List, Union, Tuple

from tohe.log import *  # pylint: disable=unused-wildcard-import
from tohe.util.status import Status

Id = Union[List[int], int]
Tags = Union[List[str], str]


def adapt_list(lst) -> str:
    """
    Adapt list entries before writing to database.

    This function takes a list and serializes it in order to
    write it to the sqlite database as string.
    """
    return '|'.join(lst)


def convert_tags(tags) -> list:
    """
    Convert list entries after fetching it from the database.

    This function takes a serialized list entry for tags and deserializes it
    to return a Python list.
    """
    result = [tag.decode('utf-8') for tag in tags.split(b'|')]
    if result is None:
        return []
    return result


class ToheDB:
    """
    Class representing a Tohe instance, including the database connection to
    the sqlite storage.

    This class exposes methods to manipulate the database, like add, edit, delete and list.
    """
    DEFAULT_DB_FILE_NAME = 'tohe.db'

    @staticmethod
    def _get_default_db_file() -> str:
        """
        Return the directory which contains the database file.
        Returns: database directory path (str)
        """
        data_home = os.getenv('XDG_DATA_HOME')
        home = os.getenv('HOME')
        if data_home is None and home is not None:
            data_home = os.path.join(home, '.local', 'share')  # type: ignore

        if data_home is None:
            raise EnvironmentError(
                'No $XDG_DATA_HOME or $HOME defined.')

        return os.path.join(data_home, 'tohe', ToheDB.DEFAULT_DB_FILE_NAME)

    def __init__(self, db_file: Optional[str] = None) -> None:
        self.loaded = False

        if not db_file:
            self.db_file = ToheDB._get_default_db_file()
            try:
                db_dir = os.path.dirname(self.db_file)
                if not os.path.exists(db_dir):
                    INFO('Creating DB path @ %s' % db_dir)
                    os.makedirs(db_dir, exist_ok=True)
            except OSError as e:
                ERROR(e)
                sys.exit(1)
        else:
            self.db_file = db_file
        INFO('DB file is: %s' % self.db_file)

        # register adapters and converters
        sqlite3.register_adapter(list, adapt_list)
        sqlite3.register_converter('tags', convert_tags)

        try:
            self.conn = sqlite3.connect(
                self.db_file, detect_types=sqlite3.PARSE_DECLTYPES)
            self.cursor = self.conn.cursor()
            self.cursor.execute(
                """CREATE TABLE IF NOT EXISTS todo (
                id INTEGER PRIMARY KEY,
                todo TEXT NOT NULL,
                tags TAGS DEFAULT ''
                )"""
            )
            self.conn.commit()
        except Exception as e:
            ERROR('Database error: %s @ %s' % (e, self.db_file))
            sys.exit(1)

        self.loaded = True

    def __del__(self) -> None:
        if self.loaded:
            self.conn.close()

    def _check_id(self, id):
        self.cursor.execute('SELECT id FROM todo')
        ids = [i for (i,) in self.cursor.fetchall()]
        if id not in ids:
            ERROR("ID '%d' does not exist!" % (id,))
            return Status.FAIL
        return Status.OK

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

    def get(self, id: int) -> Union[Tuple, Status]:
        if self._check_id(id) != Status.OK:
            return Status.FAIL

        entry: Tuple
        try:
            self.cursor.execute('SELECT * FROM todo WHERE id = ?', (id,))
            entry = self.cursor.fetchone()
        except sqlite3.DatabaseError as e:
            ERROR("Database error: %s" % e)
            return Status.FAIL
        return entry

    def get_last(self) -> Union[Tuple, Status]:
        if self.count == 0:
            return Status.EMPTY

        entry: Tuple
        try:
            self.cursor.execute('SELECT * FROM todo ORDER BY id DESC LIMIT 1')
            entry = self.cursor.fetchone()
        except sqlite3.DatabaseError as e:
            ERROR("Database error: %s" % e)
            return Status.FAIL
        return entry

    def list(self, tags: Optional[Tags] = None) -> List[Tuple]:
        # TODO add support for tags
        self.cursor.execute('SELECT * FROM todo')
        entries = self.cursor.fetchall()
        return entries

    def search(self, term: str, wildcards: bool = True) -> List[int]:
        if wildcards:
            term = term.replace('*', '%').replace('?', '_')
            query = "SELECT * FROM todo WHERE todo LIKE ?"
        else:
            term = f"%{term}%"
            query = "SELECT * FROM todo WHERE todo LIKE ?"
        self.cursor.execute(query, (term,))
        entries = self.cursor.fetchall()
        return entries

    def edit(self,
             id: int,
             todo: Optional[str] = None,
             tags: Optional[List[str]] = None) -> Status:
        if todo is None and tags is None:
            raise RuntimeError(
                'EDIT: neither todo nor tags was supplied to be changed.')
        if todo is not None and tags is not None:
            raise RuntimeError(
                'EDIT: both todo and tags should be changed. You can only change one at a time.')

        if self._check_id(id) != Status.OK:
            return Status.FAIL

        column = 'todo' if todo else 'tags'
        new = todo if todo else tags
        query = f'UPDATE todo SET {column} = ? WHERE id = ?'
        self.cursor.execute(query, (new, id))
        self.conn.commit()

        return Status.OK

    def delete(self,
               id: Optional[Id] = None,
               tags: Optional[Tags] = None) -> Status:
        if id is not None and self._check_id(id) != Status.OK:
            return Status.FAIL

        if id is None and tags is None:
            raise RuntimeError(
                'DELETE: but neither id nor tags was supplied.')

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
