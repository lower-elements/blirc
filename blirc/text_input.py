import pygame
from . import speech

class TextInput:
    __slots__ = ["text", "prompt", "on_cancel", "on_submit"]

    def __init__(self, *, prompt=None, on_cancel=None, on_submit=None):
        self.text = ""
        self.prompt = prompt
        self.on_cancel = on_cancel
        self.on_submit = on_submit

    def activate(self):
        pygame.key.start_text_input()
        if self.prompt: speech.speak(self.prompt, True)

    def append(self, text):
        self.text += text
        if len(text) > 0: speech.speak(text, True)

    def handle_event(self, event):
        match event.type:

            case pygame.TEXTINPUT:
                self.append(event.text)
                return True

            case pygame.KEYDOWN:
                match event.key:
                    case pygame.K_ESCAPE:
                        pygame.key.stop_text_input()
                        self.text = ""
                        if self.on_cancel() is not None: self.on_cancel()
                        speech.speak("Cancelled", True)
                        return True
                    case pygame.K_BACKSPACE if len(self.text) > 0:
                        c = self.text[-1]
                        self.text = self.text[:-1]
                        speech.speak(f"{c} deleted", True)
                        return True
                    case pygame.K_BACKSPACE:
                        # Swallow backspace when the text is empty
                        # Todo: play sound
                        return True
                    case pygame.K_RETURN:
                        if self.on_submit is not None: self.on_submit(self.text)
                        self.text = ""
                        pygame.key.stop_text_input()
                        return True
                    case _: return False
            case _: return False
