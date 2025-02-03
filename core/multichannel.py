from .element import Element, State
from .generators import DelayGenerator
from .process import Process


class Channel(Element):
    def __init__(self, name: str, generator: DelayGenerator):
        super().__init__(name, generator)
        self.tnext = float("inf")


class MultiChannelProcess(Process):
    def __init__(self, name: str, generator: DelayGenerator, n_channels: int = 1):
        super().__init__(name, generator)
        self.channels = [Channel(f"{name}-{i}", generator) for i in range(n_channels)]

    def in_act(self):
        for channel in self.channels:
            if channel.state == State.FREE:
                channel.state = State.BUSY
                channel.tnext = self.tcurr + self.get_delay()
                self.tnext = min(channel.tnext for channel in self.channels)
                self.on_busy()
                return

        self.try_enqueue()

    def try_enqueue(self):
        if self.queue_maxsize is None or len(self.queue) < self.queue_maxsize:
            self.queue.append(1)
        else:
            self.failures += 1

    def out_act(self):
        for channel in self.channels:
            if channel.tnext <= self.tcurr and channel.state == State.BUSY:
                self.quantity += 1
                channel.state = State.FREE
                channel.tnext = float("inf")

                self.on_freed()

                if len(self.queue) > 0:
                    self.queue.pop(0)
                    channel.state = State.BUSY
                    channel.tnext = self.tcurr + self.get_delay()

                self.tnext = min(channel.tnext for channel in self.channels)

                next_element = self.get_next_element()
                if next_element:
                    next_element.in_act()

    def set_tcurr(self, tcurr: float):
        self.tcurr = tcurr
        for channel in self.channels:
            channel.tcurr = tcurr

    def get_state(self):
        return State.FREE if not all(channel.state != State.FREE for channel in self.channels) else State.BUSY
