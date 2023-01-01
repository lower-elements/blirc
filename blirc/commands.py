import pygame
import sys

from .speech import speak

class CommandProcessor:
    def __init__(self):
        pass

    def perform(self, msg, ui):
        if msg.startswith('/'):
            command, *args = msg[1:].split(maxsplit=1)
            args = args[0] if args else None
            match command.lower():
                case "me":
                    ui.current_network.me_current(args)
                case "quit":
                    ui.shutdown()
                    pygame.quit()
                    sys.exit()
                case command:
                    speak(f"Unknown command {command}", True)
        else:
            # Regular message
            ui.current_network.msg_current(msg)
