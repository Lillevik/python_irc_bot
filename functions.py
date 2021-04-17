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


def is_fine(msg):
    fine = True
    # Dirty but passable
    illegal = "qazwsxedcrfvtgbyhnujmik,lo-øpåæ'¨\+0987654321!\"^\#¤%&/()=?`<>*`'"
    for c in msg:
        if c in illegal:
            fine = False

    if not fine and '.' not in msg:
        fine = False

    return fine


def is_valid_leet(msg):
    """ Check if msg is a valid 'leetable' message. """
    isspace = msg.isspace()
    ait = is_fine(msg)
    return isspace or ait


def react_leet(msg, a, n):
    if msg:
        now = datetime.now()
        is_leet = (now.hour == 13) and (now.minute == 37)
        if is_leet:
            if is_valid_leet(msg):
                print("{} is on leet. [{}:{}:{}]".format(n, now.hour, now.minute, now.second))
                a.append(n)


def print_split_lines(text):
    for line in text:
        if not "PING" in line:
            print(line)


def update_streak_graph(serverid):
    conn = sqlite3.connect("leet.db")
    score_data = conn.cursor().execute("""
    SELECT User.nick, Score.user_id, Score.score, Score.streak, Score.server_id, Score.cash
    FROM Score
    JOIN User ON Score.user_id = User.id
    WHERE server_id = ?;""", (serverid,)).fetchall()
    now = datetime.now()
    for score in score_data:
        conn.execute("INSERT INTO Graph_data (day, streak, user_id, server_id) VALUES (?,?,?,?);",
                     (now.date(), score[3], score[1], serverid))
        conn.execute("UPDATE Score SET cash = ? WHERE Score.server_id = ? AND Score.user_id = ?;", ((score[3] * 10), score[4], score[1]))
    conn.commit()
    conn.close()


def query_place_names(place_name):
    conn = sqlite3.connect('places.db')
    result = conn.execute("SELECT Stadnamn, engelskXml, Kommune FROM noreg where Stadnamn LIKE ? ORDER BY Prioritet ASC LIMIT 3;", ('%' + place_name + '%',))
    rows = result.fetchall()
    place_type = 'norge'
    if rows:
        return rows, place_type
    else:
        result = conn.execute("SELECT StadnamnBokmal, engelskXml, LandsnamnBokmål FROM verda where StadnamnBokmal LIKE ? LIMIT 3;", ('%' + place_name + '%',))
        rows = result.fetchall()
        place_type = 'verden'
    return rows, place_type

def get_help(message):
    commands = {
        "!help" : "Lists available commands.",
        "!roll" : "Responds with a number between 1-100.",
        "!forecast" : "Responds with the forecast for the next hour in Bergen, Norway",
        "!u [longurl]" : "Responds with a shortened url passed through the goo.gl api.",
        "!urls" : "Returns the last 5 urls for the sender channel or nick.",
        "!joke" : "Responds with a random joke from the chucknorris joke api, category nerdy.",
        "hello" : "Responds with hello"
    }
    words = message.split(" ")
    if len(words) > 1:
        return commands[words[1].rstrip()]
    return "Available commands are: " + ", ".join(commands.keys())


def run_bots(bots):
    for bot in bots:
        try:
            threading.Thread(target=bot.run_bot).start()
            threading.Thread(target=bot.check_time).start()
        except:
            print(bot.host)
            print("Error: unable to start thread")
