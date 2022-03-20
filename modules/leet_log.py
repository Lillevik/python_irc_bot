from datetime import datetime
import sqlite3
from helpers.SqlHelper import get_sql_procedure
from utils import update_streak_graph


def load_leet_log(self):
    try:
        conn = sqlite3.connect("leet.db")
        cursor = conn.cursor()
        serverid = cursor.execute("SELECT id FROM Server WHERE servername = ? AND channel = ?;",
                                  (self.host, self.channel.split("#")[1])).fetchone()
        if serverid:
            self.server_id = serverid[0]
        else:
            cursor.execute("INSERT INTO Server (servername, channel) VALUES (?,?);",
                           (self.host, self.channel.split("#")[1]))
            self.server_id = cursor.lastrowid

        conn.commit()
        conn.close()
    except Exception as e:
        print(e)
        print("Error: Loading leet log.")


def update_score(self, nick, streakLost=False):
    conn = sqlite3.connect("leet.db")
    cursor = conn.cursor()

    # Check if there exists a score for the user
    user_score = cursor.execute(get_sql_procedure()(
        "score_exists"), (nick, self.server_id)).fetchone()

    if not user_score:
        # If no score or users exists, create the users and update the score.
        userid = cursor.execute(
            "SELECT id FROM User WHERE nick = ?;", (nick,)).fetchone()
        if not userid:
            cursor.execute("INSERT INTO User (nick) VALUES (?);", (nick,))
            uid = cursor.lastrowid
            cursor.execute("INSERT INTO Score (user_id, score, streak,server_id, cash) VALUES (?,?,?,?,?);",
                           (uid, 1, 1, self.server_id, 10))
            print("Added " + str(uid) + " as a new user.")
        # If a user exists, but no score. Add new score.
        else:
            cursor.execute("INSERT INTO Score (user_id, score, streak, server_id) VALUES (?,?,?,?);",
                           (userid, 1, 1, self.server_id))
    elif user_score and not streakLost:
        cursor.execute(
            "UPDATE  Score SET score = score + 1, streak = streak + 1 , cash = cash + ((streak + 1) * 10)  WHERE user_id = ? AND server_id = ?;",
            (user_score[0], self.server_id))
    elif user_score and streakLost:
        cursor.execute(
            "UPDATE Score SET streak = 0, cash = cash + 10 WHERE Score.user_id = ? AND Score.server_id = ?;", (user_score[0], self.server_id))
    else:
        print(user_score)

    conn.commit()
    conn.close()


def send_leet_masters(self, masters):
    s = self.s
    last = (len(masters) - 1)
    congr = "Leet masters today: "
    current = 0
    if len(self.leets):
        for person in masters:
            if len(masters) == 1:
                congr = "{} was the only leet master today... disappointing.".format(
                    self.leets[0])
            elif current < last:
                congr += "{}, ".format(person)
            elif current == last:
                congr += "and {}.".format(person)
            current += 1
        self.respond(self.channel, "{}".format(congr))
        self.respond(self.channel, "Everyone else, shaaaaaame!")
    elif len(self.leets) == 0:
        self.respond(
            self.channel, "Noone remembered Leet! Shame on everyone! Shaaaame!")


def log_winners(self):
    conn = sqlite3.connect("leet.db")
    users = conn.cursor().execute("SELECT DISTINCT nick FROM User JOIN Score ON  User.id = Score.user_id "
                                  "WHERE Score.server_id = ?;", (self.server_id,)).fetchall()
    uniquelist = list(set(self.leets))
    send_leet_masters(self, uniquelist)
    for user in users:
        nick = user[0]
        if nick in uniquelist:
            self.update_score(nick)
            uniquelist.remove(nick)
        else:
            self.update_score(nick, streakLost=True)

    for nick in uniquelist:
        update_score(self, nick)

    conn.commit()
    conn.close()
    update_streak_graph(self.server_id)
    self.leets = []
