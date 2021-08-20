import threading
import time
from typing import Callable, Optional


class InterruptibleDelay(object):
    def __init__(self, halt_callback: Optional[Callable] = None) -> None:
        self.interrupt = False
        self.active = False
        self.halt_callback = halt_callback

    def delay(self, duration: int) -> None:
        self.active = True
        count = 0
        while count < duration * 10:
            if self.interrupt:
                if self.halt_callback is not None:
                    self.halt_callback()
                break
            time.sleep(0.1)
            count += 1
        self.active = False

    def async_delay(self, duration: int) -> None:
        thread = threading.Thread(target=self.delay, args=(duration, ))
        thread.start()

    def is_active(self):
        return self.active

    def terminate(self):
        self.interrupt = True

