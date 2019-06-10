import socket
import ssl
import datetime
import time
import re
import sqlite3
import random
import requests
import traceback
import sys
import errno
from functions import get_sender
from functions import get_message
from functions import get_name
from functions import get_random_joke
from functions import react_leet
from functions import print_split_lines
from functions import update_streak_graph
from functions import query_place_names
from xml.etree import ElementTree as ET
from urlshortener import shorten_url


class bot:
    def __init__(self, host, port, nick, ident, realname, master, channel):
        self.host = host
        self.port = port
        self.nick = nick
        self.ident = ident
        self.realname = realname
        self.master = master
        self.channel = channel
        self.sock = None
        self.s = None
        self.leets = []
        self.errors = 0
        self.server_id = 0

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

    def connect_to_server(self):
        try:
            self.sock = socket.socket()
            self.s = ssl.wrap_socket(self.sock)
            self.s.connect((self.host, self.port))
            self.s.send(bytes("NICK {}\r\n".format(self.nick), "UTF-8"))
            self.s.send(bytes("USER {} {} bla :{}\r\n".format(self.ident, self.host, self.realname), "UTF-8"))
            return True
        except Exception as e:
            print(e)
            print("Error while connecting")
            return False
    def respond_to_ping(self, lines):
        for line in lines:
            line = str.rstrip(line)
            line = str.split(line)
            if line[0] == "PING":
                self.s.send(bytes("PONG {}\r\n".format(line[1]), "UTF-8"))

    def join_channel(self, msg):
        try:
            if len(msg):
                if "PRIVMSG" not in msg[0] and "PING" not in msg[0]:
                    self.s.send(bytes("JOIN {}\r\n".format(self.channel), "UTF-8"))
        except IndexError as e:
            print(e)
            if self.errors < 5:                
                self.errors += 1
                self.connect_to_server()
                print('Error trying to join channel.. number of errors: ' + str(self.errors))
            else:
                print('Attempting to reconnect..')

    def respond_hello(self, m, nick, sender):
        try:
            words = m.split(" ")
            if words[0].lower() == "hello" or m == 'hello\r':
                self.respond(sender, "Hello, {}".format(nick))
        except (AttributeError, IndexError):
            return ""

    def respond_roll(self, msg, nick, respondTo):
        try:
            words = [""]
            if " " in msg:
                words = msg.split(" ")
            if msg == '!roll\r':
                self.respond(respondTo, "{} rolled: {} (1 - 100)".format(nick, random.randint(1, 100)))
            elif words[0] == "!roll":
                self.respond(respondTo, "{} rolled: {} ({} - {})".format(nick, random.randint(int(words[1]), int(words[2].split('\r')[0])), words[1], words[2]))
        except Exception as e:
            print(e)
            print('Error rolling.')

    def update_score(self, nick, streakLost=False):
        conn = sqlite3.connect("leet.db")
        cursor = conn.cursor()

        # Check if there exists a score for the user
        user_score = cursor.execute("""
        SELECT User.id, Score.score, Score.streak 
        FROM User JOIN Score ON User.id = Score.user_id
        WHERE User.nick = ? AND Score.server_id = ?;""", (nick, self.server_id)).fetchone()

        if not user_score:
            # If no score or users exists, create the users and update the score.
            userid = cursor.execute("SELECT id FROM User WHERE nick = ?;", (nick,)).fetchone()
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
            cursor.execute("UPDATE Score SET streak = 0, cash = cash + 10 WHERE Score.user_id = ? AND Score.server_id = ?;", (user_score[0], self.server_id))
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
                    congr = "{} was the only leet master today... disappointing.".format(self.leets[0])
                elif current < last:
                    congr += "{}, ".format(person)
                elif current == last:
                    congr += "and {}.".format(person)
                current += 1
            self.respond(self.channel, "{}".format(congr))
            self.respond(self.channel, "Everyone else, shaaaaaame!")
        elif len(self.leets) == 0:
            self.respond(self.channel, "Noone remembered Leet! Shame on everyone! Shaaaame!")

    def log_winners(self):
        conn = sqlite3.connect("leet.db")
        users = conn.cursor().execute("SELECT DISTINCT nick FROM User JOIN Score ON  User.id = Score.user_id "
                                      "WHERE Score.server_id = ?;", (self.server_id,)).fetchall()
        uniquelist = list(set(self.leets))
        self.send_leet_masters(uniquelist)
        for user in users:
            nick = user[0]
            if nick in uniquelist:
                self.update_score(nick)
                uniquelist.remove(nick)
            else:
                self.update_score(nick, streakLost=True)

        for nick in uniquelist:
            self.update_score(nick)

        conn.commit()
        conn.close()
        update_streak_graph(self.server_id)
        self.leets = []

    def send_random_joke(self, msg, sender):
        try:
            if "!joke" in msg:
                self.respond("{}".format(sender, get_random_joke()))
        except TypeError:
            print()

    def check_time(self):
        while 1:
            d = datetime.datetime.now()
            if (d.hour == 13) and (d.minute == 38) and (d.second == 0):
                self.log_winners()
                time.sleep(5)
            time.sleep(1)

    def send_urls(self, message, sender):
        try:
            url_string = ""
            urls = []
            words = [""]
            if " " in message:
                words = message.split(" ")
            if "!urls" in message and len(words) < 2:
                conn = sqlite3.connect('db.sqlite')
                cursor = conn.cursor()
                cursor.execute('SELECT url FROM urls WHERE hostname = ? AND sender = ? ORDER BY id DESC LIMIT 5;',
                               (self.host, sender))

                url_string = "The 5 last urls: "
                urls = cursor.fetchall()
                print(urls)
                if not len(urls):
                    urls = [("", " nothing to show.")]
                conn.close()
            elif words[0] == "!urls":
                nick = words[1].strip()
                conn = sqlite3.connect('db.sqlite')
                cursor = conn.cursor()
                cursor.execute(
                    'SELECT url FROM urls WHERE nick = ? AND hostname = ? AND sender = ? ORDER BY id DESC LIMIT 5;',
                    (nick, self.host, sender))
                url_string = "The 5 last urls from " + nick + ":"
                urls = cursor.fetchall()
                if not len(urls):
                    urls = [("", " nothing to show.")]
                conn.close()
            current = 1
            if len(urls):
                for s in urls:
                    if len(urls) != current:
                        current += 1
                        url_string += s[0] + ", "
                    else:
                        url_string += s[0] + "."
                self.respond("{}".format(sender, url_string))
        except Exception as e:
            print(self.host, traceback.format_exc())

    def log_urls(self, input_string, sender, nick):
        urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
                          str(input_string))
        if len(urls):
            try:
                conn = sqlite3.connect('db.sqlite')
                cursor = conn.cursor()
                for url in urls:
                    date = datetime.datetime.now().strftime("%d/%m/%Y")
                    if len(url) > 100:
                        short_url = shorten_url(url)
                        cursor.execute("INSERT INTO urls (url, nick, added_date, hostname, sender) VALUES (?,?,?,?,?);",
                                       (short_url, nick, date, self.host, sender))
                    else:
                        cursor.execute("INSERT INTO urls (url, nick, added_date, hostname, sender) VALUES (?,?,?,?,?);",
                                       (url, nick, date, self.host, sender))
                conn.commit()
            except Exception as e:
                print(e)
                print("Error logging urls")

    def fetch_weather_forecast(self, sender, message):
        if message.startswith('!forecast'):
            params = message.rstrip().split(' ')
            if len(params) == 1:
                r = requests.get("http://www.yr.no/place/Norway/Hordaland/Bergen/Bergen/forecast_hour_by_hour.xml")
                self.send_yr_xml(sender, r.content, 'Bergen sentrum')

            elif len(params) == 2:
                places = query_place_names(params[1])[0]

                if len(places) == 1:
                    url = places[0][1].replace('forecast.xml', 'forecast_hour_by_hour.xml')
                    name = places[0][0] + ', ' + places[0][2]
                    r = requests.get(url)
                    self.send_yr_xml(sender, r.content, name)

                elif len(places) > 1:
                    response_string = 'Found several places: '
                    for place in places:
                        response_string = response_string + '(' + place[0] + ', ' + place[2] + '), '
                    response_string = response_string + 'Pick one using the order they appear(1,2 or 3). Underscores(' \
                                                        '_) are used instead of spaces. '
                    self.respond(sender, response_string)
            elif len(params) == 3:
                index = -1
                number_input = params[2]
                if number_input == '1':
                    index = 0
                elif number_input == '2':
                    index = 1
                elif number_input == '3':
                    index = 2
                else:
                    self.respond(sender, 'Choose a number between 1 and 3. ' + number_input + ' is not valid.')

                if index != -1:
                    places = query_place_names(params[1])[0]
                    if len(places) >= 1:
                        url = places[index][1].replace('forecast.xml', 'forecast_hour_by_hour.xml')
                        name = places[index][0] + ', ' + places[index][2]

                        r = requests.get(url)
                        self.send_yr_xml(sender, r.content, name)
                    else:
                        self.respond(sender, 'Could not find the place you were looking for.')

            elif len(params) > 3:
                self.respond(sender, 'Too many arguments: Use "!forecast some_place <number>"')

    def send_yr_xml(self, sender, xml, area_name):
        root = ET.fromstring(xml)
        next_hour = root.find('forecast').find('tabular')[0]
        weather = next_hour.find('symbol').attrib['name']
        temp = next_hour.find('temperature').attrib['value']
        temp_unit = next_hour.find('temperature').attrib['unit']
        wind_direction = next_hour.find('windDirection').attrib['name']
        wind_speed = next_hour.find('windSpeed').attrib['name']
        self.respond(sender, "Forecast for the next hour for {}:".format(area_name))
        self.respond(sender,
                     "Weather: {} Temp: {} WindDirection: {} WindSpeed: {}".format(weather, (temp + " " + temp_unit),
                                                                                   wind_direction, wind_speed))

    def convert_long_url(self, message, sender):
        try:
            words = message.split(" ")
            if words[0] == "!u":
                short_url = shorten_url(words[1])
                self.respond(sender, "Your short url: " + short_url)
        except Exception as e:
            print(e)

    def respond(self, sender, message):
        self.s.send(
            bytes("PRIVMSG {} :{}\n\r".format(sender, message), "UTF-8"))

    def run_bot(self):
        readbuffer = ""
        self.connect_to_server()
        self.load_leet_log()
        active_pipe = True
        while active_pipe:
            try:
                readbuffer = readbuffer + self.s.recv(1024).decode("UTF-8")
                temp = readbuffer.split("\n")
                readbuffer = temp.pop()
                print("")
                print_split_lines(temp)

                self.respond_to_ping(temp)
                self.join_channel(temp)

                nick = str(get_name(temp))
                message = str(get_message(temp))
                sender = str(get_sender(temp, nick))

                self.respond_hello(message, nick, sender)
                react_leet(message, self.leets, nick)
                self.respond_roll(message, nick, sender)
                self.send_random_joke(message, sender)
                self.log_urls(message, sender, nick)
                self.send_urls(message, sender)
                self.convert_long_url(message, sender)
                self.fetch_weather_forecast(sender, message)
            except IOError as e:
                if e.errno == errno.EPIPE:
                    attempts = 0
                    while not self.connect_to_server() and attempts < 10:
                        attempts += 1
                        time.sleep(30)
                else:
                    print(e)
                    print("Unhandled exception: Exiting {}".format(self.host))
                    active_pipe = False