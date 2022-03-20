import sqlite3
from os import path

leet_db_name = "leet.db"
general_db = "db.sqlite"


def create_leet_db():
    conn = sqlite3.connect(leet_db_name)
    cursor = conn.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS "Graph_data" (
      `id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
      `day`	TEXT NOT NULL,
      `streak`	INTEGER NOT NULL,
      `user_id`	INTEGER NOT NULL,
      `server_id`	INTEGER
    )""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS "Score" (
      `user_id`	INTEGER NOT NULL,
      `score`	INTEGER NOT NULL DEFAULT 0,
      `streak`	INTEGER NOT NULL DEFAULT 0,
      `cash`	INTEGER DEFAULT 0,
      `server_id`	INTEGER NOT NULL,
      UNIQUE ('user_id', 'server_id')
    )""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS `Server` (
      `id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
      `servername`	INTEGER NOT NULL,
      `channel`	INTEGER NOT NULL
    )""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS `User` (
      `id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
      `nick`	TEXT NOT NULL UNIQUE
    )""")

    conn.commit()
    conn.close()


def create_generic_db():
    conn = sqlite3.connect(general_db)
    cursor = conn.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS "urls" (
      `id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
      `url`	TEXT NOT NULL,
      `nick`	TEXT NOT NULL,
      `added_date`	TEXT NOT NULL,
      `hostname`	TEXT NOT NULL,
      `sender`	TEXT,
      `short_url`	TEXT
    )""")

    conn.commit()
    conn.close()


# Create initial databases if they do not exist
def create_db():
    if not path.isfile("leet.db"):
        create_leet_db()
    if not path.isfile("db.sqlite"):
        create_generic_db()
