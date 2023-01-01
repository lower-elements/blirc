from concurrent.futures import ThreadPoolExecutor
import configparser
import platform
import pygame
import sys

from . import config
from .network import Network
from . import speech

class UI:
    def __init__(self, screen):
        self.screen = screen
        self.cfg = config.load()
        self.exec = ThreadPoolExecutor(thread_name_prefix="irc")
        self.entering_message = False
        self.message = ""
        self.networks = []
        self._network_idx = 0
        self.populate()

    def __del__(self):
        self.shutdown()

    def shutdown(self):
        for network in self.networks:
            network.irc.disconnect()
        for network in self.networks:
            network.irc.wait_until_disconnected()
        self.exec.shutdown()
        self.networks = []

    @property
    def network_idx(self):
        return self._network_idx

    @network_idx.setter
    def network_idx(self, val):
        if len(self.networks) > 0:
            new_idx = val % len(self.networks)
            self.current_network.active = False
            self._current_idx = new_idx
            self.current_network.active = True
            speech.speak(repr(self.current_network), True)

    @property
    def current_network(self):
        return self.networks[self.network_idx]

    def populate(self):
        for name, cfg in self.cfg.items():
            if name == configparser.DEFAULTSECT: continue
            self.networks.append(Network(name, cfg, self.exec))
        self.network_idx = 0

    def main_loop(self):
        while True:
            events = pygame.event.get()
            for event in events:
                match event.type:

                    case pygame.QUIT:
                        self.shutdown()
                        pygame.quit()
                        sys.exit()

                    case pygame.TEXTINPUT if self.entering_message:
                        text = event.text
                        speech.speak(text, True)
                        self.message += text
                    case pygame.TEXTINPUT if not self.entering_message and event.text == "/":
                        self.entering_message = True
                        speech.speak("Message: ", True)

                    case pygame.KEYDOWN:
                        if platform.system() == "Linux" and event.mod & pygame.KMOD_CTRL:
                            speech.linux_speaker.cancel()

                        if self.entering_message:
                            match event.key:
                                case pygame.K_ESCAPE:
                                    self.entering_message = False
                                    self.message = ""
                                    speech.speak("Cancelled", True)
                                case pygame.K_BACKSPACE if len(self.message) > 0:
                                    c = self.message[-1]
                                    self.message = self.message[:-1]
                                    speech.speak(f"{c} deleted", True)
                                case pygame.K_RETURN:
                                    if self.message.startswith("/me "):
                                        self.current_network.me_current(self.message[4:])
                                    else:
                                        self.current_network.msg_current(self.message)
                                    self.message = ""
                                    self.entering_message = False

                        else:
                            match event.key:
                                case pygame.K_EQUALS: self.network_idx += 1
                                case pygame.K_MINUS: self.network_idx -= 1
                                case x if x in range(pygame.K_1, pygame.K_9 + 1):
                                    num = x - pygame.K_1
                                    if event.mod & pygame.KMOD_CTRL and len(self.networks) > num:
                                        self.network_idx = num
                                    elif len(self.current_network.buffer_list) > num:
                                        self.current_network.buffer_idx = num
                                case pygame.K_0:
                                    if event.mod & pygame.KMOD_CTRL:
                                        self.network_idx = -1
                                    else:
                                        self.current_network.buffer_idx = -1

                                case pygame.K_LEFTBRACKET if not event.mod&pygame.KMOD_SHIFT: self.current_network.buffer_idx -= 1
                                case pygame.K_LEFTBRACKET: self.current_network.buffer_idx = 0
                                case pygame.K_RIGHTBRACKET if not event.mod&pygame.KMOD_SHIFT: self.current_network.buffer_idx += 1
                                case pygame.K_RIGHTBRACKET: self.current_network.buffer_idx = len(self.current_network.buffer_list)-1
                                case pygame.K_COMMA if not event.mod&pygame.KMOD_SHIFT:
                                    if buf := self.current_network.current_buffer:
                                        buf.message_idx -= 1
                                case pygame.K_COMMA:
                                    if buf := self.current_network.current_buffer:
                                        buf.message_idx = 0
                                case pygame.K_PERIOD if not event.mod&pygame.KMOD_SHIFT:
                                    if buf := self.current_network.current_buffer:
                                        buf.message_idx += 1
                                case pygame.K_PERIOD:
                                    if buf := self.current_network.current_buffer:
                                        buf.message_idx = len(self.current_network.current_buffer.messages)-1

                                case pygame.K_n:
                                    speech.speak(repr(self.current_network), True)
                                case pygame.K_b:
                                    speech.speak(self.current_network.buffer_list[self.current_network.buffer_idx], True)

            pygame.display.update()
