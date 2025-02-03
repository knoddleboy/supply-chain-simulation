from core.create import Create
from generators import ConstantGenerator


class ScheduledCreate(Create):
    def __init__(self, name: str, times: list[float]):
        super().__init__(name, ConstantGenerator(0))
        self.times = iter(times)

        self.tnext = next(self.times)

    def out_act(self):
        self.quantity += 1
        self.tnext = self.get_delay()
        next_element = self.get_next_element()
        if next_element:
            next_element.in_act()

    def get_delay(self):
        try:
            return next(self.times)
        except StopIteration:
            return float("inf")
