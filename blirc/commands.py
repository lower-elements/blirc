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
                    ui.if_has_network(lambda net: net.ctcp_current(ctcp_command.upper(), *ctcp_args))
                case "ctcp":
                    speak("/ctcp requires at least 1 argument", True)
                case "join" if args is not None:
                    # maxsplit=2 is so that the two-argument form, with a channel key, works
                    join_args = args.split(maxsplit=2)
                    ui.if_has_network(lambda net: net.irc.send("JOIN", *join_args))
                case "join":
                    speak("/join requires at least 1 argument", True)
                case "me":
                    ui.if_has_network(lambda net: net.me_current(args))
                case "notice":
                    notice_msg = args if args else ''
                    ui.if_has_network(lambda net: net.notice_current(notice_msg))
                case "quit":
                    ui.shutdown()
                    pygame.quit()
                    sys.exit()
                case command:
                    speak(f"Unknown command {command}", True)
        else:
            # Regular message
            ui.if_has_network(lambda net: net.msg_current(msg))
