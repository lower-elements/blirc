from datetime import datetime, timezone
import human_readable as hm

class Message:
    __slots__ = ["hostmask", "command", "args", "sent"]

    def __init__(self, hostmask, tags, command, args):
        self.hostmask = hostmask
        self.command = command
        self.args = args

        try: # Message time
            server_time = tags["time"]
            self.sent = server_time_to_datetime(server_time)
        except KeyError:
            # No time from the server, so assume now
            self.sent = datetime.utcnow()

    @staticmethod
    def synthesize_privmsg(irc, *args):
        return Message((irc.current_nick, irc.ident, irc.realname), {}, "PRIVMSG", args)

    @staticmethod
    def synthesize_notice(irc, *args):
        return Message((irc.current_nick, irc.ident, irc.realname), {}, "NOTICE", args)

    @staticmethod
    def synthesize_ctcp(irc, target, *args):
        return Message((irc.current_nick, irc.ident, irc.realname), {}, "PRIVMSG", [target, f"\x01{' '.join(args)}\x01"])

    def is_part_by(self, nick):
        return self.command.upper() == "PART" and self.hostmask[0] == nick

    def __repr__(self):
        match self.command:
            case "JOIN":
                msg = f"{self.hostmask[0]} joined {self.args[0]}"
            case "KICK" if len(self.args) > 2:
                msg = f"{self.args[1]} was kicked from {self.args[0]} by {self.hostmask[0]} - {self.args[-1]}"
            case "KICK":
                msg = f"{self.args[1]} was kicked from {self.args[0]} by {self.hostmask[0]}"
            case "PART":
                msg = f"{self.hostmask[0]} left {self.args[0]}"
            case "QUIT":
                if len(self.args) > 0 and len(self.args[0]) > 0:
                    msg = f"{self.hostmask[0]} quit IRC - {self.args[0]}"
                else:
                    msg = f"{self.hostmask[0]} quit IRC"
            case "PRIVMSG" | "NOTICE" if self.args[-1].startswith('\x01'):
                # CTCP
                command, *args = self.args[-1].strip('\x01').split(maxsplit=1)
                args = args[0] if args else None
                match command.upper():
                    case "ACTION":
                        args = args if args is not None else ''
                        msg = f"* {self.hostmask[0]} {args}"
                    case "VERSION" if args is not None:
                        msg = f"{self.hostmask[0]} is running {args}"
                    case _ if args is None:
                        msg = f"CTCP {command} request from {self.hostmask[0]}"
                    case _:
                        msg = f"{self.hostmask[0]}: [CTCP] {command} {args}"
            case "PRIVMSG":
                msg = f"{self.hostmask[0]}: {self.args[-1]}"
            case "NOTICE":
                msg = f"{self.hostmask[0]}: [Notice] {self.args[-1]}"
            case "MODE":
                msg = f"Mode {' '.join(self.args[1:])} {self.args[0]} by {self.hostmask[0]}"
            case _:
                msg = self.hostmask[0] + ": " + ' '.join(self.args)
        return msg if self.sent is None else msg + " -  " + hm.date_time(self.sent, when=datetime.utcnow())

def server_time_to_datetime(server_time: str):
    if server_time.endswith('Z'):
        dt = datetime.fromisoformat(server_time[:-1])
        dt.replace(tzinfo=timezone.utc)
        return dt
    else:
        return datetime.fromisoformat(server_time)
