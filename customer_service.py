from core.create import Create
from core.process import Process
from core.generators import DelayGenerator
from global_state import GlobalState
from constants import STATISTICS_START_TIME, LOGGING


class CreateCustomer(Create):
    def __init__(self, shop_index: int, name: str, generator: DelayGenerator):
        super().__init__(name, generator)
        self.shop_index = shop_index

    def out_act(self):
        if self.tcurr >= STATISTICS_START_TIME:
            self.quantity += 1

        self.tnext = self.tcurr + self.get_delay()

        next_element = self.get_next_element()

        if next_element:
            next_element.in_act()


class ProcessCustomer(Process):
    def __init__(self, shop_index: int, name: str, generator: DelayGenerator, gstate=GlobalState()):
        super().__init__(name, generator)
        self.shop_index = shop_index
        self.gstate = gstate

    # def is_blocked(self):
    #     blocked = self.gstate.get_shop_stock(self.shop_index) == 0
    #     if blocked:
    #         if self.tcurr >= STATISTICS_START_TIME:
    #             self.failures += 1
    #         if LOGGING:
    #             print(f"[{self.tcurr:.6f} | ProcessCustomer({self.shop_index})]  Failure")
    #     return blocked

    def get_stock(self):
        return self.gstate.get_shop_stock(self.shop_index)

    def on_freed(self):
        self.gstate.update_shop_stock(self.shop_index, amount=-1)

    def get_failure_prob(self):
        try:
            return self.failures / (self.quantity + self.failures)
        except ZeroDivisionError:
            return 0

    def print_result(self):
        failure_prob = self.get_failure_prob()
        print(
            f"{self.name}\n\tfailure probability = {failure_prob:.12f}",
            f" ({self.failures} failures)" if failure_prob > 0 else "",
        )
