import pygame

from .speech import speak

class Buffer:
    __slots__ = ["hidden", "messages", "_message_idx"]

    def __init__(self):
        self.hidden = False
        self.messages = []
        self._message_idx = 0

    @property
    def message_idx(self):
        return self._message_idx

    @message_idx.setter
    def message_idx(self, val):
        if len(self.messages) > 0:
            if val < 0: self._message_idx = 0
            elif val >= len(self.messages): self._message_idx = len(self.messages) - 1
            else:
                self._message_idx = val
                speak(repr(self.messages[val]), True)

    @property
    def current_message(self):
        if len(self.messages) > self.message_idx:
            return self.messages[self.message_idx]

    def with_current_message(self, f):
        if msg := self.current_message: return f(msg)
        else: speak("Buffer is empty", True)

    def append(self, message):
        self.messages.append(message)

    def handle_event(self, event):
        match event.key:
            case pygame.K_COMMA if not event.mod&pygame.KMOD_SHIFT:
                    self.message_idx -= 1
            case pygame.K_COMMA:
                   self.message_idx = 0
            case pygame.K_PERIOD if not event.mod&pygame.KMOD_SHIFT:
                    self.message_idx += 1
            case pygame.K_PERIOD:
                    self.message_idx = len(self.messages)-1

            case pygame.K_m:
                self.with_current_message(lambda msg: speak(repr(msg), True))
            case pygame.K_c if event.mod & pygame.KMOD_CTRL:
                self.with_current_message(copy_message)

def copy_message(msg):
    data = bytes(repr(msg), 'utf-8')
    pygame.scrap.put('text/plain;charset=utf-8', data)
    speak("Copied", True)
