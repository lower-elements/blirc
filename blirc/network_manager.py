from concurrent.futures import ThreadPoolExecutor

from .network import Network
from . import speech

class NetworkManager:
    __slots__ = ["networks", "_idx", "exec"]

    def __init__(self, cfg):
        self.exec = ThreadPoolExecutor(thread_name_prefix="irc")
        self.networks = [] # Prevents further tracebacks on error
        self.networks = [Network(n, self.exec) for n in cfg.networks]
        self._idx = 0

    def __len__(self):
        return len(self.networks)

    def __del__(self):
        self.shutdown()

    def shutdown(self, quit_msg=None):
        for network in self.networks:
            network.irc.disconnect(msg=quit_msg)
        for network in self.networks:
            network.irc.wait_until_disconnected()
        self.exec.shutdown()
        self.networks = []

    @property
    def idx(self):
        return self._idx

    @idx.setter
    def idx(self, val):
        if len(self.networks) > 0:
            new_idx = val % len(self.networks)
            self.networks[self._idx].active = False
            self._idx = new_idx
            self.networks[new_idx].active = True
            speech.speak(repr(self.current), True)
        else:
            speech.speak("No networks", True)

    @property
    def current(self):
        if len(self.networks) > self.idx:
            return self.networks[self.idx]

    def with_current(self, f):
        if net := self.current: return f(net)
        else: speech.speak("No networks", True)
