from .element import Element


class Model:
    def __init__(self, *elements: Element, logging=False):
        self.elements = elements
        self.tcurr = 0.0
        self.logging = logging

    def simulate(self, time: float):
        while self.tcurr < time:
            closest_event_time = float("inf")

            for el in self.elements:
                if el.tnext < closest_event_time:
                    closest_event_time = el.tnext

            if self.logging:
                print(self.tcurr)

            delta = closest_event_time - self.tcurr
            self.do_statistics(delta)
            for el in self.elements:
                el.do_statistics(delta)

            self.tcurr = closest_event_time
            for el in self.elements:
                el.set_tcurr(self.tcurr)

            for el in self.elements:
                if el.tnext == self.tcurr:
                    el.out_act()

            if self.logging:
                self.print_info()

        self.print_result()

    def do_statistics(self, delta: float): ...

    def print_info(self):
        for el in self.elements:
            el.print_info()

    def print_result(self): ...
