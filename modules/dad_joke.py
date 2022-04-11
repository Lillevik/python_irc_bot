from traceback import format_exc
from utils import get_random_dad_joke


def dad_joke(bot, msg, sender):
    try:
        if "!dadjoke" in msg:
            bot.respond(sender, "{}".format(
                get_random_dad_joke()))
    except Exception as e:
        print(format_exc())
