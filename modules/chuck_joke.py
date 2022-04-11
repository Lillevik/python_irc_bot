from traceback import format_exc
from utils import get_random_chuck_joke


def chuck_joke(bot, msg, sender):
    try:
        if "!joke" in msg:
            bot.respond(sender, "{}".format(get_random_chuck_joke()))
    except Exception:
        print(format_exc())
