import configparser
import pygame
import sys

from . import config
from .network import Network
from .speech import speak

class UI:
    def __init__(self, screen):
        self.screen = screen
        self.cfg = config.load()
        self.networks = []
        self._network_idx = 0
        self.populate()

    @property
    def network_idx(self):
        return self._network_idx

    @network_idx.setter
    def network_idx(self, val):
        if len(self.networks) > 0:
            self._network_idx = val % len(self.networks)
            speak(repr(self.networks[self._network_idx]), True)

    @property
    def current_network(self):
        return self.networks[self.network_idx]

    def populate(self):
        for name, cfg in self.cfg.items():
            if name == configparser.DEFAULTSECT: continue
            self.networks.append(Network(name, cfg))
        self.network_idx = 0

    def main_loop(self):
        while True:
            events = pygame.event.get()
            for event in events:
                match event.type:

                    case pygame.QUIT:
                        pygame.quit()
                        sys.exit()

                    case pygame.KEYDOWN:
                        match event.key:
                            case pygame.K_EQUALS: self.network_idx += 1
                            case pygame.K_MINUS: self.network_idx -= 1
                            case x if x in range(pygame.K_1, pygame.K_9 + 1):
                                num = x - pygame.K_1
                                if len(self.networks) > num: self.network_idx = num
                            case pygame.K_0: self.network_idx = -1
                            case pygame.K_n: speak(repr(self.current_network), True)
                            case pygame.K_LEFTBRACKET: self.current_network.buffer_idx -= 1
                            case pygame.K_RIGHTBRACKET: self.current_network.buffer_idx += 1
                            case pygame.K_COMMA: self.current_network.current_buffer.message_idx -= 1
                            case pygame.K_PERIOD: self.current_network.current_buffer.message_idx += 1

            pygame.display.update()
