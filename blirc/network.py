import miniirc
import pygame

from .buffer_manager import BufferManager
from .message import Message
from .speech import speak

class Network:
    __slots__ = ["active", "buffers", "_name", "irc"]

    def __init__(self, cfg, exec):
        self.active = False
        self.buffers = BufferManager()
        self._name = cfg.name

        creds = (cfg.nick, cfg.password) if cfg.password is not None else None
        self.irc = miniirc.IRC(cfg.host, cfg.port, cfg.nick,
                            ident=cfg.ident, realname=cfg.realname, ns_identity=creds,
                               channels=cfg.channels, connect_modes=cfg.modes, quit_message=cfg.quit_message,
                               ping_interval=cfg.ping_interval, ping_timeout=cfg.ping_timeout, verify_ssl=cfg.verify_ssl,
                               ircv3_caps={"echo-message"}, executor=exec)

        self.irc.CmdHandler("PRIVMSG", "NOTICE", "JOIN", "PART", "MODE", ircv3=True, colon=False)(self.on_message)

    def __del__(self):
        self.irc.disconnect()

    @property
    def name(self):
        try:
            return self.irc.isupport["NETWORK"]
        except KeyError:
            return self._name

    def map_buffer_name(self, target, nick):
        match target:
            case "*":
                return "Server Messages"
            case self.irc.current_nick if nick == self.irc.ip:
                return "Server Messages"
            case self.irc.current_nick:
                return nick
            case _:
                return target

    def on_message(self, irc, command, hostmask, tags, args):
        buf_name = self.map_buffer_name(args[0], hostmask[0])
        msg = Message(hostmask, tags, command, args)

        # Only append the message if the buffer isn't already closed
        if msg.is_part_by(self.irc.current_nick):
            print(f"{repr(self)} should be hidden")
            try: buf = self.buffers[buf_name]
            # If there isn't an existing buffer, ignore the message
            except KeyError: return
        else: buf = self.buffers.get_or_create(buf_name)

        buf.append(msg)

        if self.active and self.buffers.current_name == buf:
            speak(repr(msg), False)

    def msg_current(self, *args):
        def send(buf, buf_name):
            self.irc.msg(buf_name, *args)
            if "echo-message" not in self.irc.active_caps:
                msg = Message.synthesize_privmsg(self.irc, buf_name, *args)
                buf.append(msg)
                speak(repr(msg), True)

        self.buffers.with_current_writable(send)

    def notice_current(self, *args):
        def send(buf, buf_name):
            self.irc.notice(buf_name, *args)
            if "echo-message" not in self.irc.active_caps:
                msg = Message.synthesize_notice(self.irc, buf_name, *args)
                buf.append(msg)
                speak(repr(msg), True)

        self.buffers.with_current_writable(send)

    def me_current(self, *args):
        def send(buf, buf_name):
            self.irc.me(buf_name, *args)
            if "echo-message" not in self.irc.active_caps:
                msg = Message.synthesize_ctcp(self.irc, buf_name, "ACTION", *args)
                buf.append(msg)
                speak(repr(msg), True)

        self.buffers.with_current_writable(send)

    def ctcp_current(self, *args):
        def send(buf, buf_name):
            self.irc.ctcp(buf_name, *args)
            if "echo-message" not in self.irc.active_caps:
                msg = Message.synthesize_ctcp(self.irc, buf_name, *args)
                buf.append(msg)
                speak(repr(msg), True)

        self.buffers.with_current_writable(send)

    def part_current(self, *, part_msg=None):
        args = [part_msg] if part_msg else []
        def part(buf, buf_name):
            if buf_name != "Server Messages": # Not a virtual buffer
                self.irc.send("PART", buf_name, *args)
            self.buffers.hide(buf_name)

        self.buffers.with_current(part)

    def __repr__(self):
        match self.irc.connected:
            case True: s = ""
            case False: s = "[Connecting] "
            case _: s = "[Disconnected] "
        return s + f"{self.name} ({self.irc.ip})"

    def handle_event(self, event):
        match event.key:
            case pygame.K_LEFTBRACKET if not event.mod&pygame.KMOD_SHIFT:
                self.buffers.select_prev()
            case pygame.K_LEFTBRACKET:
                self.buffers.select_idx(0)
            case pygame.K_RIGHTBRACKET if not event.mod&pygame.KMOD_SHIFT:
                self.buffers.select_next()
            case pygame.K_RIGHTBRACKET:
                self.buffers.select_idx(-1)

            case x if x in range(pygame.K_1, pygame.K_9 + 1):
                num = x - pygame.K_1
                if len(self.buffers.tabs) > num:
                    self.buffers.select_idx(num)
            case pygame.K_0:
                self.buffers.select_idx(-1)

            case pygame.K_n:
                speak(repr(self), True)
            case pygame.K_b:
                self.buffers.with_current(lambda buf, buf_name: speak(buf_name, True))

            case _ if buf := self.buffers.current:
                buf.handle_event(event)
