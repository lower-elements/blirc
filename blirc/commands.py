import pygame
import sys

from .speech import speak

class CommandProcessor:
    __slots__ = []
    def __init__(self):
        pass

    def perform(self, msg, ui):
        if msg.startswith('/'):
            command, *args = msg[1:].split(maxsplit=1)
            args = args[0] if args else None
            match command.lower():
                case "ctcp" if args is not None:
                    ctcp_command, *ctcp_args = args.split(maxsplit=1)
                    ui.networks.with_current(lambda net: net.ctcp_current(ctcp_command.upper(), *ctcp_args))
                case "ctcp":
                    speak("/ctcp requires at least 1 argument", True)
                case "hide":
                    def hide(net):
                        del net.current_buffer
                    ui.networks.with_current(hide)
                case "join" if args is not None:
                    # maxsplit=2 is so that the two-argument form, with a channel key, works
                    join_args = args.split(maxsplit=2)
                    ui.networks.with_current(lambda net: net.irc.send("JOIN", *join_args))
                case "join":
                    speak("/join requires at least 1 argument", True)
                case "kick" if args is not None:
                    target, *kick_args = args.split(maxsplit=2)
                    ui.networks.with_current(lambda net: net.with_writable_buffer(lambda buf, buf_name: net.irc.send("KICK", buf_name, target, *kick_args)))
                case "kick":
                    speak("/kick requires at least 1 argument", True)
                case "me":
                    ui.networks.with_current(lambda net: net.me_current(args))
                case "mode" if args is not None:
                    target, *mode_args = args.split(maxsplit=3)
                    ui.networks.with_current(lambda net: net.irc.send("MODE", target, *mode_args))
                case "mode":
                    speak("/mode requires at least 1 argument", True)
                case "notice":
                    notice_msg = args if args else ''
                    ui.networks.with_current(lambda net: net.notice_current(notice_msg))
                case "part":
                    ui.networks.with_current(lambda net: net.part_current())
                case "quit":
                    ui.shutdown(quit_msg=args)
                    pygame.quit()
                    sys.exit()
                case command:
                    speak(f"Unknown command {command}", True)
        else:
            # Regular message
            ui.networks.with_current(lambda net: net.msg_current(msg))
