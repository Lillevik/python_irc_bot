import requests, json, datetime, threading, re, sqlite3


def get_name(msg):
    try:
        if "PRIVMSG" in msg[0]:
            return msg[0].split('!')[0].split(':')[1]
    except IndexError:
        return "Empty."


def get_message(msg):
    try:
        if "PRIVMSG" in msg[0]:
            return msg[0].split(" :")[1]
    except IndexError:
        return "Empty."


def get_sender(msg, nick):
    try:
        chan = msg[0].split("PRIVMSG")[1].split(" :")[0].split()[0]
        if "#" in chan:
            return chan
        else:
            return nick
    except IndexError:
        return nick


def get_random_joke():
    return json.loads(requests.get("http://api.icndb.com/jokes/random?limitTo=[nerdy]").text)['value']['joke']


def react_leet(msg, a, n):
    if msg:
        if msg.isspace():
            now = datetime.datetime.now()
            if (now.hour == 13) and (now.minute == 37):
                print("{} is on leet. [{}:{}:{}]".format(n, now.hour, now.minute, now.second))
                a.append(n)
            else:
                print("{} is not on leet. [{}:{}:{}]".format(n, now.hour, now.minute, now.second))


def print_split_lines(text):
    for line in text:
        print(line)


def run_bots(bots):
    for bot in bots:
        try:
            threading.Thread(target=bot.run_bot).start()
            threading.Thread(target=bot.check_time).start()
        except:
            print(bot.host)
            print("Error: unable to start thread")

def log_urls(inputString, sender):
    urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',inputString)
    conn = sqlite3.connect('db.sqlite')
    cursor = conn.cursor()
    for url in urls:
        date = datetime.datetime.now().strftime("%d/%m/%Y")
        cursor.execute("INSERT INTO urls (url, nick, added_date) VALUES (?,?,?);", (url, sender, date))
    conn.commit()