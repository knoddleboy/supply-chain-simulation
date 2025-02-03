from core.element import Element
from core.model import Model as BaseModel
from global_state import GlobalState
from customer_service import ProcessCustomer
from wholesale_restock import ProcessWholesaleRequest
from shop_restock import DispatchShopRequest
from constants import STATISTICS_START_TIME


class Model(BaseModel):
    def __init__(self, *elements: Element, logging=False, gstate=GlobalState()):
        super().__init__(*elements, logging=logging)
        self.gstate = gstate
        self.cumulative_wholesale_stock = 0

    def simulate(self, time: float):
        while self.tcurr < time:
            closest_event_time = float("inf")

            for el in self.elements:
                if el.tnext < closest_event_time:
                    closest_event_time = el.tnext

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

                    # Once wholesale store is restocked, dispatch shop request event
                    # is fired first so that shop restock chain is not blocked
                    if isinstance(el, ProcessWholesaleRequest):
                        for el2 in self.elements:
                            if isinstance(el2, DispatchShopRequest) and self.gstate.is_shop_pending(el2.shop_index):
                                el2.tnext = self.tcurr

            if self.logging:
                self.print_info()

        if self.logging:
            self.print_result()

    def do_statistics(self, delta: float):
        if self.tcurr >= STATISTICS_START_TIME:
            super().do_statistics(delta)
            wsstock = self.gstate.get_wholesale_stock()
            self.cumulative_wholesale_stock += wsstock * delta

    def get_avg_shop_failure_prob(self):
        total_probs = []
        for el in self.elements:
            if isinstance(el, ProcessCustomer):
                total_probs.append(el.get_failure_prob())
        return sum(total_probs) / len(total_probs)

    def get_avg_wholesale_stock(self):
        try:
            return self.cumulative_wholesale_stock / (self.tcurr - STATISTICS_START_TIME)
        except ZeroDivisionError:
            return 0

    def print_result(self):
        print("\n-------- RESULTS --------")
        for el in self.elements:
            el.print_result()

        print(f"\nAverage shop failure probability = {self.get_avg_shop_failure_prob() * 100} %")
        print(f"Average wholesale stock level = {self.get_avg_wholesale_stock()}\n")
