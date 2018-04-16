import requests, json, datetime, threading
from datetime import datetime
import sqlite3


def get_name(msg):
    try:
        if "PRIVMSG" in msg[0]:
            return msg[0].split('!')[0].split(':')[1]
    except IndexError:
        return "Empty."


def get_message(msg):
    try:
        if "PRIVMSG" in msg[0]:
            return msg[0].split(" :")[1]
    except IndexError:
        return "Empty."


def get_sender(msg, nick):
    try:
        chan = msg[0].split("PRIVMSG")[1].split(" :")[0].split()[0]
        if "#" in chan:
            return chan
        else:
            return nick
    except IndexError:
        return nick


def get_random_joke():
    return json.loads(requests.get("http://api.icndb.com/jokes/random?limitTo=[nerdy]").text)['value']['joke']


def react_leet(msg, a, n):
    if msg:
        if msg.isspace():
            now = datetime.now()
            if (now.hour == 13) and (now.minute == 37):
                print("{} is on leet. [{}:{}:{}]".format(n, now.hour, now.minute, now.second))
                a.append(n)
            else:
                print("{} is not on leet. [{}:{}:{}]".format(n, now.hour, now.minute, now.second))


def print_split_lines(text):
    if not 'PING' in text:
        for line in text:
            print(line)


def update_streak_graph(serverid):
    conn = sqlite3.connect("leet.db")
    score_data = conn.cursor().execute("""
    SELECT User.nick, Score.user_id, Score.score, Score.streak, Score.server_id 
    FROM Score 
    JOIN User ON Score.user_id = User.id 
    WHERE server_id = ?;""", (serverid,)).fetchall()
    now = datetime.now()
    for score in score_data:
        conn.execute("INSERT INTO Graph_data (day, streak, user_id, server_id) VALUES (?,?,?,?);",
                     (now.date(), score[3], score[1], serverid))
    conn.commit()
    conn.close()


def query_place_names(place_name):
    conn = sqlite3.connect('places.db')
    result = conn.execute("SELECT Stadnamn, engelskXml FROM noreg where Stadnamn LIKE ? ORDER BY Prioritet ASC LIMIT 3;", ('%' + place_name + '%',))
    rows = result.fetchall()
    place_type = 'norge'
    if rows:
        return rows, place_type
    else:
        result = conn.execute("SELECT StadnamnBokmal, engelskXml FROM verda where StadnamnBokmal LIKE ? LIMIT 3;", ('%' + place_name + '%',))
        rows = result.fetchall()
        place_type = 'verden'

    return rows, place_type




def run_bots(bots):
    for bot in bots:
        try:
            threading.Thread(target=bot.run_bot).start()
            threading.Thread(target=bot.check_time).start()
        except:
            print(bot.host)
            print("Error: unable to start thread")


