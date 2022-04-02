from datetime import datetime
import re
import sqlite3
from traceback import format_exc
from urlshortener import shorten_url


def log_urls(self, input_string, sender, nick):
    urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
                      str(input_string))
    if len(urls):
        try:
            conn = sqlite3.connect('db.sqlite')
            cursor = conn.cursor()
            for url in urls:
                date = datetime.now().strftime("%d/%m/%Y")
                if len(url) > 100:
                    short_url = shorten_url(url)
                    cursor.execute("INSERT INTO urls (url, nick, added_date, hostname, sender) VALUES (?,?,?,?,?);",
                                   (short_url, nick, date, self.host, sender))
                else:
                    cursor.execute("INSERT INTO urls (url, nick, added_date, hostname, sender) VALUES (?,?,?,?,?);",
                                   (url, nick, date, self.host, sender))
            conn.commit()
        except Exception as e:
            print("Error logging urls")
            print(format_exc(e))
