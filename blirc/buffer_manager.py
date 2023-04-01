from .buffer import Buffer
from . import speech

class BufferManager:
    __slots__  = ["buffers", "tabs", "_idx"]

    def __init__(self):
        self.buffers = {}
        self.tabs = []
        self._idx = 0

    def __len__(self):
        return len(self.buffers)

    def new_tab(self, name, buf):
        self.tabs.append(name)
        buf.hidden = False
        speech.speak(f"New buffer: {name}", True)

    def append(self, name, buf):
        self.buffers[name] = buf
        self.new_tab(name, buf)

    @property
    def current_name(self):
        if len(self.tabs) > 0:
            return self.tabs[self._idx]

    @property
    def current(self):
        if name := self.current_name:
            try: return self.buffers[name]
            except KeyError: return None

    def with_current(self, f):
        if buf := self.current: return f(buf, self.current_name)
        else: speech.speak("No open buffers", True)

    def with_current_writable(self, f):
        return self.with_current(
                lambda buf, name: f(buf, name) if name != "Server Messages" else speech.speak("Buffer is read-only", True))

    def select_idx(self, idx):
        if len(self.tabs) > 0:
            self._idx = idx
            speech.speak(self.current_name, True)
        else: speech.speak("No open buffers", True)

    def select_name(self, name):
        self._idx = self.tabs.index(name)
        speech.speak(name, True)

    def select_next(self):
        if len(self.tabs) > 0:
            self._idx = (self._idx + 1) % len(self.tabs)
            speech.speak(self.current_name, True)
        else: speech.speak("No open buffers", True)

    def select_prev(self):
        if len(self.tabs) > 0:
            self._idx = (self._idx - 1) % len(self.tabs)
            speech.speak(self.current_name, True)
        else: speech.speak("No open buffers", True)

    def hide(self, name):
        self.buffers[name].hidden = True
        self.tabs.remove(name)
        self.select_idx(min(self._idx, len(self.tabs) - 1))

    def get_or_create(self, name):
        try:
            buf = self.buffers[name]
            if buf.hidden:
                self.new_tab(name, buf)
            return buf
        except KeyError:
            buf = Buffer()
            self.append(name, buf)
            return buf
