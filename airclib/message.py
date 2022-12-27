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
            case "QUIT":
                if len(self.args) > 0 and len(self.args[0]) > 0:
                    return f"{self.hostmask[0]} quit IRC - {self.args[0]}"
                else:
                    return f"{self.hostmask[0]} quit IRC"
            case "PRIVMSG":
                return f"{self.hostmask[0]}: {self.args[-1]}"
            case "NOTICE":
                return f"{self.hostmask[0]}: [Notice] {self.args[-1]}"
            case "MODE":
                return f"Mode {' '.join(self.args[1:])} {self.args[0]} by {self.hostmask[0]}"
            case _:
                return self.hostmask[0] + ": " + ' '.join(self.args)
