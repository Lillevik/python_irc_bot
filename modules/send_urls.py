import sqlite3
import traceback


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
        print("Error sending urls")
        print(self.host, traceback.format_exc())
