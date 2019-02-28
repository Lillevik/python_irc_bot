from sqlite3 import connect


def get_conn():
    return connect("leet.db")
