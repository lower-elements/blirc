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
                case "ctcp" if args is not None:
                    ctcp_command, *ctcp_args = args.split(maxsplit=1)
                    ui.current_network.ctcp_current(ctcp_command.upper(), *ctcp_args)
                case "join" if args is not None:
                    # maxsplit=2 is so that the two-argument form, with a channel key, works
                    join_args = args.split(maxsplit=2)
                    ui.current_network.irc.send("JOIN", *join_args)
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
