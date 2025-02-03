from enum import Enum
from typing import Optional
from .generators import DelayGenerator
from .routing import Route


class State(Enum):
    FREE = 0
    BUSY = 1


class Element:
    def __init__(self, name: str, generator: DelayGenerator):
        self.name: str = name
        self.generator = generator

        self.state = State.FREE
        self.tcurr: float = 0.0
        self.tnext: float = 0.0

        self.next_elements: Optional[list[Route]] = None

        self.quantity: int = 0

    def get_delay(self):
        return self.generator.generate()

    def get_next_element(self):
        if self.next_elements is None:
            return None

        for route in self.next_elements:
            if not route.is_blocked():
                return route.element

        return None

    def set_tcurr(self, tcurr: float):
        self.tcurr = tcurr

    def get_state(self):
        return self.state

    def in_act(self): ...

    def out_act(self): ...

    def do_statistics(self, delta: float): ...

    def print_info(self): ...

    def print_result(self): ...
