import sqlite3


def get_db_conn():
    """
    Create and return a database connection.
    """
    db = sqlite3.connect('movies-extended.db')
    db.execute("PRAGMA foreign_keys = ON")
    db.row_factory = sqlite3.Row
    return db