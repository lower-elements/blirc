class Message:
    def __init__(self, hostmask, command, args):
        self.hostmask = hostmask
        self.command = command
        self.args = args

    def __repr__(self):
        match self.command:
            case "JOIN":
                return f"{self.hostmask[0]} joined {self.args[0]}"
            case "PART":
                return f"{self.hostmask[0]} left {self.args[0]}"
            case "PRIVMSG":
                return f"{self.hostmask[0]}: {self.args[-1]}"
            case _:
                return self.hostmask[0] + ": " + ' '.join(self.args)
