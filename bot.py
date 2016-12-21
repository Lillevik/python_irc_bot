import socket
import ssl
import datetime
import json
import random
import time
from functions import get_sender, get_message, get_name, get_random_joke, react_leet, print_split_lines


class bot:
    def __init__(self, host, port, nick, ident, realname, master, channel):
        self.host = host
        self.port = port
        self.nick = nick
        self.ident = ident
        self.realname = realname
        self.master = master
        self.channel = channel
        self.sock = socket.socket()
        self.s = None
        self.leets = []
        self.score = {}

    def load_leet_log(self):
        try:
            with open("leetlog/" + self.host + '.json') as data_file:
                self.score = json.load(data_file)
                print("Score for: " + self.host + "  " + str(self.score))
        except:
            print("Error: Loading leet log.")

    def connect_to_server(self):
        self.s = ssl.wrap_socket(self.sock)
        self.s.connect((self.host, self.port))

        self.s.send(bytes("NICK {}\r\n".format(self.nick), "UTF-8"))
        self.s.send(bytes("USER {} {} bla :{}\r\n".format(self.ident, self.host, self.realname), "UTF-8"))

    def respond_to_ping(self, lines):
        for line in lines:
            line = str.rstrip(line)
            line = str.split(line)
            if line[0] == "PING":
                self.s.send(bytes("PONG {}\r\n".format(line[1]), "UTF-8"))

    def join_channel(self, msg):
        try:
            if "PRIVMSG" not in msg[0]:
                self.s.send(bytes("JOIN {}\r\n".format(self.channel), "UTF-8"))
        except IndexError:
            print("IndexError.")

    def respond_hello(self, m, nick, sender):
        try:
            words = m.split(" ")
            if words[0].lower() == "hello" or m == 'hello\r':
                self.s.send(bytes("PRIVMSG {} :Hello, {}\r\n".format(sender, nick), "UTF-8"))
        except (AttributeError, IndexError):
            return ""

    def respond_roll(self, msg, nick, respondTo):
        try:
            words = msg.split(" ")
            if msg == '!roll\r':
                self.s.send(
                    bytes("PRIVMSG {} :{} rolled: {} (1 - 100)\n\r".format(respondTo, nick, random.randint(1, 100)),
                          "UTF-8"))
            elif words[0] == "!roll":
                self.s.send(bytes("PRIVMSG {} :{} rolled: {} ({} - {})\n\r".format(respondTo, nick, random.randint(
                    int(words[1]), int(words[2].split('\r')[0])), words[1], words[2]), "UTF-8"))
        except:
            print()

    def update_score(self, nick):
        if nick not in self.score:
            self.score[nick] = 1
        else:
            self.score[nick] += 1

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
            s.send(bytes("PRIVMSG {} :{}\n\r".format(self, self.channel, congr), "UTF-8"))
            s.send(bytes("PRIVMSG {} :Everyone else, shaaaaaame!\n\r".format(self.channel), "UTF-8"))
        elif len(self.leets) == 0:
            s.send(
                bytes("PRIVMSG {} :Noone remembered Leet! Shame on everyone! Shaaaame!\n\r".format(self.channel),
                      "UTF-8"))
            print(self.score)


    def log_winners(self):
        print(self.score)
        uniquelist = list(set(self.leets))
        for person in uniquelist:
            self.update_score(person)
        # send_leet_masters(uniquelist) gets annoying after some time.
        self.leets = []
        with open("leetlog/" + self.host + self.channel + '.json', 'w') as outfile:
            json.dump(self.score, outfile)
        print(self.score)

    def send_random_joke(self, msg, sender):
        try:
            if "!joke" in msg:
                self.s.send(
                    bytes("PRIVMSG {} :{}\n\r".format(sender, get_random_joke()), "UTF-8"))
        except TypeError:
            print()

    def check_time(self):
        while 1:
            d = datetime.datetime.now()
            if (d.hour == 13) and (d.minute == 38) and (d.second == 5):
                self.log_winners()
                time.sleep(5)
            time.sleep(1)

    def run_bot(self):
        readbuffer = ""
        self.connect_to_server()
        self.load_leet_log()
        while 1:
            readbuffer = readbuffer + self.s.recv(1024).decode("UTF-8")
            temp = readbuffer.split("\n")
            readbuffer = temp.pop()
            print_split_lines(temp)

            self.respond_to_ping(temp)
            self.join_channel(temp)

            nick = get_name(temp)
            message = get_message(temp)
            sender = get_sender(temp, nick)

            self.respond_hello(message, nick, sender)
            react_leet(message, self.leets, nick)
            self.respond_roll(message, nick, sender)
            self.send_random_joke(message, sender)
