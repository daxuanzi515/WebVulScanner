from datetime import datetime
from .helper import *

class Log:
    @classmethod
    def info(self, text):
        print("[" + Y + datetime.now().strftime("%H:%M:%S") + N + "] [" + G + "INFO" + N + "] " + text)

    @classmethod
    def warning(self, text):
        print("[" + Y + datetime.now().strftime("%H:%M:%S") + N + "] [" + Y + "WARNING" + N + "] " + text)

    @classmethod
    def high(self, text):
        print("[" + Y + datetime.now().strftime("%H:%M:%S") + N + "] [" + R + "CRITICAL" + N + "] " + text)
