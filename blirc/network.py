import miniirc
import pygame

from .buffer import Buffer
from .message import Message
from .speech import speak

class Network:
    def __init__(self, name, cfg, exec):
        self.active = False
        self.buffers = {}
        self.buffer_list = []
        self._buffer_idx = 0
        self._name = name

        creds = (cfg.get("nick"), cfg.get("password")) if "password" in cfg else None
        self.irc = miniirc.IRC(cfg.get("host"), cfg.getint("port"), cfg.get("nick"),
                            ident=cfg.get("ident"), realname=cfg.get("realname"), ns_identity=creds,
                               channels=cfg.get("channels", None), connect_modes=cfg.get("modes", None), quit_message=cfg.get("quit_message"),
                               ping_interval=cfg.getint("ping_interval"), ping_timeout=cfg.getint("ping_timeout"), verify_ssl=cfg.getboolean("verify_ssl", True),
                               ircv3_caps=set(), executor=exec)

        self.irc.CmdHandler("PRIVMSG", "NOTICE", "JOIN", "PART", "MODE", colon=False)(self.on_message)

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
            return self.buffers[name]
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

    def on_message(self, irc, command, hostmask, args):
        buf = self.map_buffer_name(args[0], hostmask[0])
        msg = Message(hostmask, command, args)
        self.buffer(buf).append(msg)
        if self.active and self.current_buffer_name == buf:
            speak(repr(msg), True)

    def with_writable_buffer(self, f):
        if buf := self.current_buffer:
            if self.current_buffer_name == "Server Messages": speak("Buffer is read-only", True)
            else: return f(buf, self.current_buffer_name)
        else: speak("No buffers", True)

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
                speak(self.buffer_list[self.buffer_idx], True)

            case _ if buf := self.current_buffer:
                buf.handle_event(event)
