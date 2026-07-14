import threading


class QueueController:
    def __init__(self):
        self.paused = threading.Event(); self.cancelled = threading.Event()
        self.paused.set()

    def pause(self): self.paused.clear()
    def resume(self): self.paused.set()
    def stop(self): self.cancelled.set(); self.paused.set()
    def wait(self): self.paused.wait(); return not self.cancelled.is_set()
