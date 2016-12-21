from bot import bot
from functions import run_bots

bots = []

b = bot('host', 0000, 'nick', 'ident', 'realname', 'master', '#channel')
b1 = bot('host', 0000, 'nick', 'ident', 'realname', 'master', '#channel')
bots.append(b)
bots.append(b1)

run_bots(bots)
