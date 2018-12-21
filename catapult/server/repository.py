import sqlite3
from json import dumps, loads


class Repository:
    def __init__(self, sqlite_path):
        self.sqlite_path = sqlite_path

    def initialize(self):
        db = sqlite3.connect(self.sqlite_path)
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE deploys(
                name TEXT PRIMARY KEY,
                request TEXT,
                status TEXT,
                logger TEXT,
                time_end TEXT
            )
        ''')
        db.commit()

    def get_release(self, release_name):
        db = sqlite3.connect(self.sqlite_path)
        cursor = db.cursor()

        cursor.execute(
            '''
              SELECT
                name,
                request,
                status,
                logger,
                time_end
              FROM
                deploys
              WHERE
                name = ?
          ''',
            (release_name,)
        )
        release = cursor.fetchone()
        db.close()

        if not release:
            return None

        return {
            'name': release[0],
            'request': loads(release[1]),
            'status': release[2],
            'logger': loads(release[3]),
            'time_end': release[4]
        }

    def insert_release(self, name, request, status):
        db = sqlite3.connect(self.sqlite_path)
        cursor = db.cursor()

        cursor.execute(
            '''
                INSERT INTO deploys
                (name, request, status, logger)
                VALUES
                (?, ?, ?, ?)
            ''',
            (
                name, dumps(request), status, dumps([]),
            )
        )
        db.commit()

        db.close()

    def update_release(self, name, status, logger, time_end):
        logger = dumps(logger)

        db = sqlite3.connect(self.sqlite_path)

        cursor = db.cursor()
        cursor.execute(
            '''
                UPDATE deploys SET
                  status = ?,
                  logger = ?,
                  time_end = ?
                WHERE
                  name = ?
            ''',
            (
                status,
                logger,
                time_end,
                name,
            )
        )
        db.commit()

        db.close()
