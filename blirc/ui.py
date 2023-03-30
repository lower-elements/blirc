import miniirc
import pygame
import sys

from .config import Config
from . import consts
from .commands import CommandProcessor
from .network_manager import NetworkManager
from .text_input import TextInput
from . import speech

class UI:
    __slots__ = ["cfg", "screen", "networks", "cmd_proc", "entering_message", "message_input"]

    def __init__(self):
        self.cfg = Config.load()

        pygame.init()
        pygame.display.init()

        pygame.display.set_caption(consts.VERSION_STRING)
        self.screen = pygame.display.set_mode((800, 600))

        pygame.key.set_text_input_rect((0, 0, 800, 600))
        pygame.key.stop_text_input()

        self.networks = NetworkManager(self.cfg)
        self.cmd_proc = CommandProcessor()

        # UI state
        self.entering_message = False
        self.message_input = TextInput(
                prompt = "Message",
                on_cancel = self.on_message_cancel,
                on_submit = self.on_message_submit,
                )

        # IRC state
        miniirc.version = consts.CTCP_VERSION

    def shutdown(self, *, quit_msg=None):
        self.networks.shutdown(quit_msg)

    def on_message_cancel(self):
        self.entering_message = False

    def on_message_submit(self, msg):
        self.cmd_proc.perform(msg, self)
        self.entering_message = False

    def main_loop(self):
        while True:
            events = pygame.event.get()
            for event in events:
                self.handle_event(event)

            pygame.display.update()

    def handle_event(self, event):
        # Let the text input handle it if it wants
        if self.entering_message:
            if self.message_input.handle_event(event):
                return # Event handled

        match event.type:

            case pygame.QUIT:
                self.shutdown()
                pygame.quit()
                sys.exit()

            case pygame.KEYDOWN:
                if event.mod & pygame.KMOD_CTRL: speech.stop()

                if not self.entering_message:
                    match event.key:
                        case pygame.K_SLASH:
                            self.entering_message = True
                            self.message_input.activate()
                        case pygame.K_EQUALS: self.networks.select_next()
                        case pygame.K_MINUS: self.networks.select_prev()
                        case x if event.mod & pygame.KMOD_CTRL and x in range(pygame.K_1, pygame.K_9 + 1):
                            num = x - pygame.K_1
                            if len(self.networks) > num:
                                self.networks.select(num)
                        case pygame.K_0 if event.mod & pygame.KMOD_CTRL:
                            self.networks.select(-1)

                        case _ if network := self.networks.current:
                            network.handle_event(event)
