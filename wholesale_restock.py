from core.create import Create
from core.multichannel import MultiChannelProcess
from core.generators import DelayGenerator
from global_state import GlobalState
from constants import LOGGING


class CreateWholesaleRequest(Create):
    def out_act(self):
        if LOGGING:
            print(f"[{self.tcurr:.6f} | CreateWholesaleRestock]  Create wholesale restock request")
        return super().out_act()


class ProcessWholesaleRequest(MultiChannelProcess):
    def __init__(self, name: str, generator: DelayGenerator, amount: int, n_channels: int = 25, gstate=GlobalState()):
        super().__init__(name, generator, n_channels)
        self.gstate = gstate
        self.amount = amount

    def on_busy(self):
        if LOGGING:
            print(f"[{self.tcurr:.6f} | ProcessWholesaleRestock]  Wholesale restock due: {self.tnext}")

    def on_freed(self):
        self.gstate.update_wholesale_stock(amount=+self.amount)

        if LOGGING:
            print(
                f"[{self.tcurr:.6f} | ProcessWholesaleRestock]  Wholesale restock complete. New stock = {self.gstate.get_wholesale_stock()}"
            )
