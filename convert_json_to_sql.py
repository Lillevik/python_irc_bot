import sqlite3, json

domain1_score = json.load(open("leetlog/domain1.json"))
domain1_graph = json.load(open("leetlog/domain1.graph.json"))

domain2_score = json.load(open("leetlog/domain2.no.json"))
domain2_graph = json.load(open("leetlog/domain2.graph.json"))

conn = sqlite3.connect("leet.db")
cursor = conn.cursor()

conn.execute("""
CREATE TABLE IF NOT EXISTS "Graph_data" (
	`id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	`day`	TEXT NOT NULL,
	`streak`	INTEGER NOT NULL,
	`user_id`	INTEGER NOT NULL,
	`server_id`	INTEGER
)""")

conn.execute("""
CREATE TABLE IF NOT EXISTS `Server` (
	`id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	`servername`	INTEGER NOT NULL,
	`channel`	INTEGER NOT NULL
)""")

conn.execute("""
CREATE TABLE IF NOT EXISTS `User` (
	`id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	`nick`	TEXT NOT NULL UNIQUE
)""")

conn.execute("""
CREATE TABLE IF NOT EXISTS "Score" (
	`user_id`	INTEGER NOT NULL,
	`score`	INTEGER NOT NULL DEFAULT 0,
	`streak`	INTEGER NOT NULL DEFAULT 0,
	`cash`	INTEGER DEFAULT 0,
	`server_id`	INTEGER NOT NULL,
	UNIQUE ('user_id', 'server_id')
)""")


def convert(servername, channel, score, graph):
    cursor.execute("INSERT INTO Server (servername, channel) VALUES (?,?)", (servername, channel))
    server_id = cursor.lastrowid

    for key in score:
        try:
            cursor.execute("INSERT INTO User (nick) VALUES(?);", (key,))
        except Exception as e:
            pass
    users = conn.execute("SELECT nick, id FROM User;").fetchall()
    u_dict = {}

    for user in users:
        try:
            o = score[user[0]]
            u_dict[user[0]] = user[1]
            cursor.execute("INSERT INTO Score (user_id, score, streak, cash, server_id) VALUES(?,?,?,?,?)",
                           (user[1], o["score"], o["streak"], o["score"] * 100, server_id))
        except Exception as e:
            print(e)

    for nick in graph:
        for o in graph[nick]['graph']:
            date = list(o.keys())[0]
            streak = o[date]
            conn.execute("INSERT INTO Graph_data (day, streak, user_id, server_id) VALUES (?, ?, ?, ?);", (date,
                                                                                                           streak,
                                                                                                           u_dict[nick],
                                                                                                           server_id))


convert("domain1", "channel", domain1_score, domain1_graph)
convert("domain2", "channel", domain2_score, domain2_graph)

conn.commit()
conn.close()
