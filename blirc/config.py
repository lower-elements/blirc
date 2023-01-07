import appdirs
import getpass
from os import path
import tomlkit

from . import consts

class Required:
    __slots__ = []

class BaseConfig:
    def __init__(self, config, global_defaults=None):
        if global_defaults is None: global_defaults = {}

        for key in self.DEFAULTS:
            try:
                setattr(self, key, config[key])
            except KeyError as e:
                try:
                    setattr(self, key, global_defaults[key])
                except KeyError:
                    if isinstance(self.DEFAULTS[key], Required): raise e
                    setattr(self, key, self.DEFAULTS[key])

class NamedConfig(BaseConfig):
    __slots__ = ["name"]

    def __init__(self, config, global_defaults=None):
        self.name = config.name
        super().__init__(config, global_defaults)

def default_slots(cls):
    try: cls.__slots__.extend(cls.DEFAULTS.keys())
    except AttributeError as e:
        if e.name != "__slots__": raise e
        cls.__slots__ = [k for k in cls.DEFAULTS.keys()]
    return cls

@default_slots
class NetworkConfig(NamedConfig):
    DEFAULTS = {
            "enabled": True,
            "host": Required(),
            "port": 6697,
            "channels": [],
            "nick": Required(),
            "ident": Required(),
            "realname": Required(),
            "password": None,
            "quit_message": consts.CTCP_VERSION ,
            "modes": None,
            "ping_interval": 60,
            "ping_timeout": None,
            "verify_ssl": True,
            }

@default_slots
class Config(BaseConfig):
    __slots__ = ["networks"]
    DEFAULTS = {
            "nick": getpass.getuser(),
            "ident": getpass.getuser(),
            "realname": getpass.getuser(),
            }

    def __init__(self, config):
        super().__init__(config)
        self.networks = [NetworkConfig(cfg, config) for cfg in config.get("network", {}).values()]

    @staticmethod
    def load():
        app_dirs = appdirs.AppDirs(consts.NAME, consts.AUTHOR)
        cfg_path = path.join(app_dirs.user_config_dir, "config.toml")
        with open(cfg_path, "rt", encoding="utf8") as f:
            cfg = tomlkit.load(f)
        return Config(cfg)
