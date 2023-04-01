import sys

match sys.platform:
    case "win32":
        from cytolk import tolk
        tolk.try_sapi(True)
        tolk.load("__compiled__" not in globals())
    case "darwin":
        from . import NSSS
        speaker = NSSS.NSSS ()
        speaker.set ("rate", 300)
    case "linux":
        import speechd
        from time import perf_counter
        from . import consts
        linux_speaker = speechd.Speaker(consts.NAME)
        linux_speaker.set_priority(speechd.Priority.TEXT)

def speak (text, interupt = True):
    match sys.platform:
        case "win32": tolk.speak(text, interupt)
        case "linux":
            linux_speaker.cancel()
            linux_speaker.speak(text)
        case "darwin": speaker.speak (text, interupt)

def stop():
    match sys.platform:
        case "darwin": speaker.stop()
        case "linux": linux_speaker.cancel()
        case "win32": tolk.silence()
