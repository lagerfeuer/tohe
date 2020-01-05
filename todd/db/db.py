import os
import sys
import sqlite3
from typing import Optional


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
