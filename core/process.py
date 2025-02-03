from .element import Element, State
from .generators import DelayGenerator


class Process(Element):
    def __init__(self, name: str, generator: DelayGenerator):
        super().__init__(name, generator)
        self.tnext = float("inf")

        self.queue = []
        self.queue_maxsize = 0

        self.failures = 0

    def in_act(self):
        if self.state == State.FREE:
            self.state = State.BUSY
            self.tnext = self.tcurr + self.get_delay()
            self.on_busy()

        else:
            self.try_enqueue()

    def on_busy(self): ...

    def try_enqueue(self):
        if not self.queue_maxsize or len(self.queue) < self.queue_maxsize:
            self.queue.append(1)
        else:
            self.failures += 1

    def out_act(self):
        self.quantity += 1
        self.tnext = float("inf")
        self.state = State.FREE
        self.on_freed()

        if len(self.queue) > 0:
            self.queue.pop(0)
            self.state = State.BUSY
            self.tnext = self.tcurr + self.get_delay()

        next_element = self.get_next_element()
        if next_element:
            next_element.in_act()

    def on_freed(self): ...

    def set_queue_maxsize(self, maxsize: int | None):
        self.queue_maxsize = maxsize
