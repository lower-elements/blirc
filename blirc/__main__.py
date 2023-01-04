import pygame

from . import consts
from .ui import UI

def main():
    pygame.init()
    pygame.display.init()
    pygame.display.set_caption("{} v{}.{}.{}".format(consts.TITLE, consts.VERSION[0], consts.VERSION[1], consts.VERSION[2]))
    screen = pygame.display.set_mode((800, 600))
    pygame.key.set_text_input_rect((0, 0, 800, 600))
    pygame.key.stop_text_input()
    ui = UI(screen)
    ui.main_loop()

if __name__ == "__main__":
    main()
