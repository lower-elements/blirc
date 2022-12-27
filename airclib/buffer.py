from .speech import speak

class Buffer:
    def __init__(self):
        self.messages = []
        self._message_idx = 0

    @property
    def message_idx(self):
        return self._message_idx

    @message_idx.setter
    def message_idx(self, val):
        if len(self.messages) == 1:
                speak(repr(self.messages[0]), True)
        elif len(self.messages) > 0:
            if val < 0: self._message_idx = 0
            elif val >= len(self.messages): self._message_idx = len(self.messages) - 1
            else:
                self._message_idx = val
                speak(repr(self.messages[val]), True)

    def append(self, message):
        self.messages.append(message)
