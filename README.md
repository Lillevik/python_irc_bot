# python_irc_bot

Leet counter, and more.

This is an irc bot written in python 3.5.

The bot was made for counting counting leet score when people type a space at 1337.
The score is simply stored in a json file.

To run the bot, just enter valid server information in run.py.

There are known issues with disconnection handling at this time.

### example:
```
b = bot('irc.example.com', 6697, 'Nick', 'ident', 'realname', 'master', '#channel')
bots.append(b)
run_bots(bots)
```

### Available commands:
```!roll```
Responds with a number between 1-100

```!roll <minNum> <maxNum>```
Responds with a number between the given parameters.

```!forecast```
Responds with the forecast for the latest hour in Bergen, Norway```

```!u <longurl>```
Responds with a shortened url passed through the goo.gl api.

```!urls```
Returns the last 5 urls for the sender channel or nick.

```!urls <nick>```
Responds with the 5 last urls for the given nick from the channel.

```!joke``` Responds with a random joke from the chucknorris joke api, category nerdy.

```Hello ```
Responds with hello, Nick.
