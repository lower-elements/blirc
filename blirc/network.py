import miniirc
import pygame

from .buffer import Buffer
from .message import Message
from .speech import speak

class Network:
    __slots__ = ["active", "buffers", "buffer_list", "_buffer_idx", "_name", "irc"]

    def __init__(self, cfg, exec):
        self.active = False
        self.buffers = {}
        self.buffer_list = []
        self._buffer_idx = 0
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
    def buffer_idx(self):
        return self._buffer_idx

    @buffer_idx.setter
    def buffer_idx(self, val):
        if len(self.buffer_list) > 0:
            self._buffer_idx = val % len(self.buffer_list)
            speak(self.buffer_list[self._buffer_idx], True)

    @property
    def current_buffer(self):
        if len(self.buffer_list) > self.buffer_idx:
            try:
                return self.buffers[self.buffer_list[self.buffer_idx]]
            except KeyError:
                return None
        else:
            return None

    @current_buffer.deleter
    def current_buffer(self):
        if len(self.buffer_list) > 0:
            self.current_buffer.hidden = True
            del self.buffer_list[self.buffer_idx]
        if len(self.buffer_list) == 0: speak("No buffers", True)
        elif len(self.buffer_list) > self.buffer_idx: self.buffer_idx = -1

    @property
    def name(self):
        try:
            return self.irc.isupport["NETWORK"]
        except KeyError:
            return self._name

    @property
    def current_buffer_name(self):
        return self.buffer_list[self.buffer_idx]

    def buffer(self, name):
        try:
            buf = self.buffers[name]
            if buf.hidden: # Reactive the buffer
                buf.hidden = False
                self.buffer_list.append(name)
                speak(f"New buffer: {name}", True)
            return buf
        except KeyError:
            self.buffers[name] = Buffer()
            self.buffer_list.append(name)
            speak(f"New buffer: {name}", True)
            return self.buffers[name]

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
        buf = self.map_buffer_name(args[0], hostmask[0])
        msg = Message(hostmask, tags, command, args)
        self.buffer(buf).append(msg)
        if self.active and self.current_buffer_name == buf:
            speak(repr(msg), True)

    def with_current_buffer(self, f):
        if buf := self.current_buffer: return f(buf, self.current_buffer_name)
        else: speak("No buffers", True)

    def with_writable_buffer(self, f):
        return self.with_current_buffer(
                lambda buf, buf_name: f(buf, buf_name) if buf_name != "Server Messages" else speak("Buffer is read-only", True))

    def msg_current(self, *args):
        def send(buf, buf_name):
            self.irc.msg(buf_name, *args)
            if "echo-message" not in self.irc.active_caps:
                msg = Message.synthesize_privmsg(self.irc, buf_name, *args)
                buf.append(msg)
                speak(repr(msg), True)

        self.with_writable_buffer(send)

    def notice_current(self, *args):
        def send(buf, buf_name):
            self.irc.notice(buf_name, *args)
            if "echo-message" not in self.irc.active_caps:
                msg = Message.synthesize_notice(self.irc, buf_name, *args)
                buf.append(msg)
                speak(repr(msg), True)

        self.with_writable_buffer(send)

    def me_current(self, *args):
        def send(buf, buf_name):
            self.irc.me(buf_name, *args)
            if "echo-message" not in self.irc.active_caps:
                msg = Message.synthesize_ctcp(self.irc, buf_name, "ACTION", *args)
                buf.append(msg)
                speak(repr(msg), True)

        self.with_writable_buffer(send)

    def ctcp_current(self, *args):
        def send(buf, buf_name):
            self.irc.ctcp(buf_name, *args)
            if "echo-message" not in self.irc.active_caps:
                msg = Message.synthesize_ctcp(self.irc, buf_name, *args)
                buf.append(msg)
                speak(repr(msg), True)

        self.with_writable_buffer(send)

    def part_current(self, *, part_msg=None):
        args = [part_msg] if part_msg else []
        def part(buf, buf_name):
            if buf_name != "Server Messages": # Not a virtual buffer
                self.irc.send("PART", buf_name, *args)
            del self.current_buffer

        self.with_current_buffer(part)

    def __repr__(self):
        match self.irc.connected:
            case True: s = ""
            case False: s = "[Connecting] "
            case _: s = "[Disconnected] "
        return s + f"{self.name} ({self.irc.ip})"

    def handle_event(self, event):
        match event.key:
            case pygame.K_LEFTBRACKET if not event.mod&pygame.KMOD_SHIFT:
                self.buffer_idx -= 1
            case pygame.K_LEFTBRACKET:
                self.buffer_idx = 0
            case pygame.K_RIGHTBRACKET if not event.mod&pygame.KMOD_SHIFT:
                self.buffer_idx += 1
            case pygame.K_RIGHTBRACKET:
                self.buffer_idx = -1

            case x if x in range(pygame.K_1, pygame.K_9 + 1):
                num = x - pygame.K_1
                if len(self.buffer_list) > num:
                    self.buffer_idx = num
            case pygame.K_0:
                self.buffer_idx = -1

            case pygame.K_n:
                speak(repr(self), True)
            case pygame.K_b:
                self.with_current_buffer(lambda buf, buf_name: speak(buf_name, True))

            case _ if buf := self.current_buffer:
                buf.handle_event(event)
