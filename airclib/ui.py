import pygame
import sys

class UI:
    def __init__(self, screen):
        self.screen = screen

    def main_loop(self):
        while True:
            events = pygame.event.get()
            for event in events:
                match event.type:
                    case pygame.QUIT:
                        pygame.quit()
                        sys.exit()
            pygame.display.update()
