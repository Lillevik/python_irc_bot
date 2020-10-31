from bot import bot
from functions import run_bots


bots = []
b = bot('irc.example.com', 6697, 'Nick', 'ident', 'realname', 'master', '#channel')
bots.append(b)
run_bots(bots)