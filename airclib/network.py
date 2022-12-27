import miniirc

from .buffer import Buffer
from .message import Message
from .speech import speak

class Network:
    def __init__(self, name, cfg):
        self.buffers = {}
        self.buffer_list = []
        self._buffer_idx = 0
        self._name = name

        creds = (cfg.get("nick"), cfg.get("password")) if "password" in cfg else None
        self.irc = miniirc.IRC(cfg.get("host"), cfg.getint("port"), cfg.get("nick"), channels=cfg.get("channels", None), ident=cfg.get("ident"), realname=cfg.get("realname"), ns_identity=creds)

        self.irc.CmdHandler("PRIVMSG", "NOTICE", "JOIN", "PART", "MODE", colon=False)(self.on_message)

    def __del__(self):
        self.irc.disconnect()

    @property
    def buffer_idx(self):
        return self._buffer_idx

    @buffer_idx.setter
    def buffer_idx(self, val):
        if len(self.buffer_list) > 0:
            self._buffer_idx = val % len(self.buffer_list)
            speak(self.buffer_list[self._buffer_idx], True)

    @property
    def current_buffer(self):
        if len(self.buffer_list) > self.buffer_idx:
            try:
                return self.buffers[self.buffer_list[self.buffer_idx]]
            except KeyError:
                return None
        else:
            return None

    @property
    def name(self):
        try:
            return self.irc.isupport["NETWORK"]
        except KeyError:
            return self._name

    def buffer(self, name):
        try:
            return self.buffers[name]
        except KeyError:
            self.buffers[name] = Buffer()
            self.buffer_list.append(name)
            speak(f"New buffer: {name}", True)
            return self.buffers[name]

    def map_buffer_name(self, target, nick):
        match target:
            case "*":
                return "Server messages"
            case self.irc.current_nick:
                return nick
            case _:
                return target

    def on_message(self, irc, command, hostmask, args):
        buf = self.map_buffer_name(args[0], hostmask[0])
        self.buffer(buf).append(Message(hostmask, command, args))

    def __repr__(self):
        match self.irc.connected:
            case True: s = ""
            case False: s = "[Connecting] "
            case _: s = "[Disconnected] "
        return s + f"{self.name} ({self.irc.ip})"
