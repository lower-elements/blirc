import platform

if platform.system() == "Windows":
    from cytolk import tolk
    tolk.try_sapi(True)
    tolk.load("__compiled__" not in globals())

elif platform.system() == "Darwin":
    from . import NSSS
    speaker = NSSS.NSSS ()

elif platform.system() == "Linux":
    import speechd
    from time import perf_counter
    linux_speaker = speechd.Speaker("airc")
    linux_speaker.set_priority(speechd.Priority.TEXT)
    last = perf_counter()

def speak (text, interupt = True):
    if platform.system() == "Windows":
        tolk.speak(text, interupt)

    elif platform.system() == "Linux":
        global last
        elapsed = perf_counter() - last
        if elapsed > 0.1:
            if interupt:
                linux_speaker.cancel()
                linux_speaker.speak(text)
                last = perf_counter()

    elif platform.system() == "Darwin":
        speaker.set ("rate", 300)
        speaker.speak (text, interupt)
