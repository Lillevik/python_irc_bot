import traceback
from urlshortener import shorten_url


def convert_long_url(self, message, sender):
    try:
        words = message.split(" ")
        if words[0] == "!u":
            short_url = shorten_url()(words[1])
            self.respond(sender, "Your short url: " + short_url)
    except Exception as e:
        print(self.host, traceback.format_exc())
