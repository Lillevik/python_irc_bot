import socket
import ssl
import datetime
import time
import errno
from utils import get_sender
from utils import get_message
from utils import get_name
from utils import react_leet
from utils import print_split_lines
from modules.convert_long_url import convert_long_url
from modules.forecast import fetch_weather_forecast
from modules.hello import respond_hello
from modules.help import send_help
from modules.joke import send_random_joke
from modules.leet_log import load_leet_log, log_winners
from modules.log_urls import log_urls
from modules.roll import respond_roll
from modules.send_urls import send_urls


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

    def connect_to_server(self):
        try:
            self.sock = socket.socket()
            self.s = ssl.wrap_socket(self.sock)
            self.s.connect((self.host, self.port))
            self.s.send(bytes("NICK {}\r\n".format(self.nick), "UTF-8"))
            self.s.send(bytes("USER {} {} bla :{}\r\n".format(
                self.ident, self.host, self.realname), "UTF-8"))
            return True
        except Exception as e:
            print("Error while connecting: ", e)
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
                    self.s.send(
                        bytes("JOIN {}\r\n".format(self.channel), "UTF-8"))
        except IndexError as e:
            print(e)
            if self.errors < 5:
                self.errors += 1
                self.connect_to_server()
                print(
                    'Error trying to join channel.. number of errors: ' + str(self.errors))
            else:
                print('Attempting to reconnect..')

    def respond(self, sender, message):
        self.s.send(
            bytes("PRIVMSG {} :{}\n\r".format(sender, message), "UTF-8"))

    def check_time(self):
        while 1:
            d = datetime.datetime.now()
            if (d.hour == 13) and (d.minute == 38) and (d.second == 0):
                log_winners(self)
                time.sleep(5)
            time.sleep(1)

    def run_bot(self):
        readbuffer = ""
        self.connect_to_server()
        load_leet_log(self)
        active_pipe = True
        while active_pipe:
            try:
                readbuffer = readbuffer + self.s.recv(1024).decode("UTF-8")
                lines = readbuffer.split("\n")
                readbuffer = lines.pop()
                print_split_lines(lines)

                self.respond_to_ping(lines)
                self.join_channel(lines)

                nick = str(get_name(lines))
                message = str(get_message(lines))
                sender = str(get_sender(lines, nick))

                log_urls(self, message, sender, nick)
                respond_hello(self, message, nick, sender)
                react_leet(message, self.leets, nick)
                respond_roll(self, message, nick, sender)
                send_random_joke(self, message, sender)
                send_urls(self, message, sender)
                send_help(self, message, sender)
                convert_long_url(self, message, sender)

                # Deprecated and needs a rewrite
                fetch_weather_forecast(self, sender, message)
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
            except Exception as e:
                print("Unknown exception", e)
