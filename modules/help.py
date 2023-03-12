from utils import get_help


def send_help(self, message, sender):
    try:
        words = message.split(" ")
        if words[0].rstrip() == "!help":
            help_message = get_help(message)
            self.respond(sender, help_message)
    except Exception as e:
        print(e)
