from traceback import format_exc
from utils import get_random_joke


def send_random_joke(self, msg, sender):
    try:
        if "!joke" in msg:
            self.respond(sender, "{}".format(sender, get_random_joke()))
    except Exception as e:
        print("Unknown exception joke")
        print(format_exc(e))
