from random import random


def respond_roll(self, msg, nick, respondTo):
    try:
        words = [""]
        if " " in msg:
            words = msg.split(" ")
        if msg == '!roll\r':
            self.respond(
                respondTo, "{} rolled: {} (1 - 100)".format(nick, random.randint(1, 100)))
        elif words[0] == "!roll":
            self.respond(respondTo, "{} rolled: {} ({} - {})".format(nick, random.randint(
                int(words[1]), int(words[2].split('\r')[0])), words[1], words[2]))
    except Exception as e:
        print(e)
        print('Error rolling.')
