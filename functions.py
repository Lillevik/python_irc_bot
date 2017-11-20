import requests, json, datetime, threading
from datetime import datetime


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
            now = datetime.now()
            if (now.hour == 13) and (now.minute == 37):
                print("{} is on leet. [{}:{}:{}]".format(n, now.hour, now.minute, now.second))
                a.append(n)
            else:
                print("{} is not on leet. [{}:{}:{}]".format(n, now.hour, now.minute, now.second))


def print_split_lines(text):
    for line in text:
        print(line)


def update_streak_graph(graph_filename, score_filename, masters):
    graph_data = {}
    score_data = {}
    try:
        graph_data_file = open(graph_filename, "r")  # Open the JSON file for reading
        graph_data = json.load(graph_data_file)  # Read the JSON into the buffer
        graph_data_file.close()  # Close the JSON file
    except FileNotFoundError:
        print("Graph file not found...")

    try:
        score_data_file = open(score_filename, "r")  # Open the JSON file for reading
        score_data = json.load(score_data_file)  # Read the JSON into the buffer
        score_data_file.close()  # Close the JSON file
    except FileNotFoundError:
        print("Score file not found...")

    current_date = str(datetime.now().date())

    for nick in score_data:
        tmp = []
        if nick in masters:
            current_streak = score_data[nick]['streak']
            try:
                tmp = graph_data[nick]['graph']
                tmp.append({current_date: current_streak})
                graph_data[nick]['graph'] = tmp
            except KeyError:
                graph_data[nick] = {'graph': [{current_date: current_streak}]}
        elif nick not in masters and nick in graph_data:
            tmp = graph_data[nick]['graph']
            tmp.append({current_date: 0})
            graph_data[nick]['graph'] = tmp
        elif nick in masters and nick not in graph_data:
            graph_data[nick] = {'graph': [{current_date: 1}]}
        elif nick not in masters and nick not in graph_data:
            graph_data[nick] = {'graph': [{current_date: 0}]}

    jsonFile = open(graph_filename, "w+")
    print(graph_data)
    jsonFile.write(json.dumps(graph_data))
    jsonFile.close()



def run_bots(bots):
    for bot in bots:
        try:
            threading.Thread(target=bot.run_bot).start()
            threading.Thread(target=bot.check_time).start()
        except:
            print(bot.host)
            print("Error: unable to start thread")
