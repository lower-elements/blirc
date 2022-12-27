import miniirc

class Network:
    def __init__(self, name, cfg):
        self.name = name
        creds = (cfg.get("nick"), cfg.get("password")) if "password" in cfg else None
        self.irc = miniirc.IRC(cfg.get("host"), cfg.getint("port"), cfg.get("nick"), ident=cfg.get("ident"), realname=cfg.get("realname"), ns_identity=creds)
        self.buffers = {}

    @property
    def server_name(self):
        try:
            return self.irc.isupport["NETWORK"]
        except KeyError:
            return self.irc.ip

    def __repr__(self):
        match self.irc.connected:
            case True: s = ""
            case False: s = "[Connecting] "
            case _: s = "[Disconnected] "
        return s + f"{self.name} ({self.server_name})"
