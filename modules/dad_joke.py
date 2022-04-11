from traceback import format_exc
from utils import get_random_dad_joke


def dad_joke(self, msg, sender):
    try:
        if "!dadjoke" in msg:
            self.respond(sender, "{}".format(
                get_random_dad_joke()))
    except Exception as e:
        print("Unknown exception dadjoke")
        print(format_exc(e))
