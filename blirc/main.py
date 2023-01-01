import pygame

from . import consts
from .ui import UI

def main():
    pygame.init()
    pygame.display.init()
    pygame.display.set_caption("{} v{}.{}.{}".format(consts.TITLE, consts.VERSION[0], consts.VERSION[1], consts.VERSION[2]))
    screen = pygame.display.set_mode((800, 600))
    ui = UI(screen)
    ui.main_loop()

if __name__ == "__main__":
    main()
