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
        self._current_network = 0
        self.populate()

    @property
    def current_network(self):
        return self._current_network

    @current_network.setter
    def current_network(self, val):
        if len(self.networks) > 0:
            self._current_network = val % len(self.networks)
            speak(repr(self.networks[self._current_network]), True)

    def populate(self):
        for name, cfg in self.cfg.items():
            if name == configparser.DEFAULTSECT: continue
            self.networks.append(Network(name, cfg))
        self.current_network = 0

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
                            case pygame.K_EQUALS: self.current_network += 1
                            case pygame.K_MINUS: self.current_network -= 1
                            case x if x in range(pygame.K_1, pygame.K_9 + 1):
                                num = x - pygame.K_1
                                if len(self.networks) > num: self.current_network = num
                            case pygame.K_0: self.current_network = -1

            pygame.display.update()
