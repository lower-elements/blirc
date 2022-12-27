import miniirc

class Network:
    def __init__(self, name, cfg):
        self._name = name
        creds = (cfg.get("nick"), cfg.get("password")) if "password" in cfg else None
        self.irc = miniirc.IRC(cfg.get("host"), cfg.getint("port"), cfg.get("nick"), ident=cfg.get("ident"), realname=cfg.get("realname"), ns_identity=creds)
        self.buffers = {}

    def __del__(self):
        self.irc.disconnect()

    @property
    def name(self):
        try:
            return self.irc.isupport["NETWORK"]
        except KeyError:
            return self._name

    def __repr__(self):
        match self.irc.connected:
            case True: s = ""
            case False: s = "[Connecting] "
            case _: s = "[Disconnected] "
        return s + f"{self.name} ({self.irc.ip})"
