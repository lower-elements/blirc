from concurrent.futures import ThreadPoolExecutor
import miniirc
import pygame
import sys

from .config import Config
from . import consts
from .commands import CommandProcessor
from .network import Network
from . import speech

class UI:
    __slots__ = ["cfg", "screen", "networks", "_network_idx", "exec", "cmd_proc", "entering_message", "message"]

    def __init__(self):
        self.cfg = Config.load()

        pygame.init()
        pygame.display.init()

        pygame.display.set_caption(consts.VERSION_STRING)
        self.screen = pygame.display.set_mode((800, 600))

        pygame.key.set_text_input_rect((0, 0, 800, 600))
        pygame.key.stop_text_input()

        self.exec = ThreadPoolExecutor(thread_name_prefix="irc")
        self.cmd_proc = CommandProcessor()

        # UI state
        self.entering_message = False
        self.message = ""

        # IRC state
        miniirc.version = consts.CTCP_VERSION
        self.networks = [Network(n, self.exec) for n in self.cfg.networks]
        self._network_idx = 0

    def __del__(self):
        self.shutdown()

    def shutdown(self, *, quit_msg=None):
        for network in self.networks:
            network.irc.disconnect(msg=quit_msg)
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
            self.networks[self._network_idx].active = False
            self._network_idx = new_idx
            self.networks[new_idx].active = True
            speech.speak(repr(self.current_network), True)
        else:
            speech.speak("No networks", True)

    @property
    def current_network(self):
        if len(self.networks) > self.network_idx:
            return self.networks[self.network_idx]

    def with_current_network(self, f):
        if net := self.current_network: return f(net)
        else: speech.speak("No networks", True)

    def main_loop(self):
        while True:
            events = pygame.event.get()
            for event in events:
                self.handle_event(event)

            pygame.display.update()

    def handle_event(self, event):
        match event.type:

            case pygame.QUIT:
                self.shutdown()
                pygame.quit()
                sys.exit()

            case pygame.TEXTINPUT if self.entering_message:
                text = event.text
                speech.speak(text, True)
                self.message += text

            case pygame.KEYDOWN:
                if event.mod & pygame.KMOD_CTRL: speech.stop()

                if self.entering_message:
                    match event.key:
                        case pygame.K_ESCAPE:
                            pygame.key.stop_text_input()
                            self.entering_message = False
                            self.message = ""
                            speech.speak("Cancelled", True)
                        case pygame.K_BACKSPACE if len(self.message) > 0:
                            c = self.message[-1]
                            self.message = self.message[:-1]
                            speech.speak(f"{c} deleted", True)
                        case pygame.K_RETURN:
                            self.cmd_proc.perform(self.message, self)
                            self.message = ""
                            pygame.key.stop_text_input()
                            self.entering_message = False

                else:
                    match event.key:
                        case pygame.K_SLASH:
                            self.entering_message = True
                            pygame.key.start_text_input()
                            speech.speak("Message: ", True)
                        case pygame.K_EQUALS: self.network_idx += 1
                        case pygame.K_MINUS: self.network_idx -= 1
                        case x if event.mod & pygame.KMOD_CTRL and x in range(pygame.K_1, pygame.K_9 + 1):
                            num = x - pygame.K_1
                            if len(self.networks) > num:
                                self.network_idx = num
                        case pygame.K_0 if event.mod & pygame.KMOD_CTRL:
                            self.network_idx = -1

                        case _ if network := self.current_network:
                            network.handle_event(event)
