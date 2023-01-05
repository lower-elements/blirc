from appdirs import AppDirs
from configparser import ConfigParser
import getpass
from os import path

from . import consts

DEFAULTS = {
            "port": 6697,
            "nick": getpass.getuser(),
            "ident": getpass.getuser(),
            "realname": getpass.getuser(),
            "quit_message": consts.VERSION_STRING,
            "ping_interval": "60",
            "ping_timeout": "60",
            "verify_ssl": "true",
        }

def load():
    app_dirs = AppDirs(consts.NAME, consts.AUTHOR)
    cfg = ConfigParser(defaults=DEFAULTS)
    cfg.read(path.join(app_dirs.site_config_dir, "config.ini"))
    cfg.read(path.join(app_dirs.user_config_dir, "config.ini"))
    return cfg
