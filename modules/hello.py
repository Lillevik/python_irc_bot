def respond_hello(self, m, nick, sender):
    try:
        words = m.split(" ")
        if words[0].lower() == "hello" or m == 'hello\r':
            self.respond(sender, "Hello, {}".format(nick))
    except (AttributeError, IndexError):
        return ""
