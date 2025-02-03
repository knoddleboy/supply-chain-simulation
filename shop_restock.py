from core.create import Create
from core.generators import DelayGenerator
from core.process import Process, State
from global_state import GlobalState
from constants import LOGGING, MODEL_PARAMS
from stats import ShopStats


class CreateShopRequest(Create):
    def __init__(self, shop_index: int, name: str, generator: DelayGenerator, gstate=GlobalState()):
        super().__init__(name, generator)
        self.shop_index = shop_index
        self.gstate = gstate

    def print_info(self):
        stock = self.gstate.get_shop_stock(self.shop_index)
        print(f"[{self.tcurr:.6f} | CreateShopRequest({self.shop_index})]  Current stock = {stock}")


class DispatchShopRequest(Process):
    def __init__(self, shop_index: int, name: str, generator: DelayGenerator, gstate=GlobalState()):
        super().__init__(name, generator)
        self.shop_index = shop_index
        self.gstate = gstate

    def get_stock(self):
        return self.gstate.get_shop_stock(self.shop_index)

    def get_is_pending(self):
        return self.gstate.is_shop_pending(self.shop_index)

    def on_busy(self):
        order_quantity = MODEL_PARAMS["SHOP_MAX_STOCK"] - self.get_stock() + 6 * 10  # 10 items per each of 6 days
        self.gstate.set_shop_restock_amount(self.shop_index, order_quantity)
        self.gstate.set_shop_pending_status(self.shop_index, is_pending=True)

        ShopStats().add_restock_point(self.shop_index, self.tcurr)
        if LOGGING:
            print(f"[{self.tcurr:.6f} | DispatchShopRequest({self.shop_index})]  Restock needed -- Request dispatched")

    def print_info(self):
        print(f"[{self.tcurr:.6f} | DispatchShopRequest({self.shop_index})]  Request received")


class ProcessShopRequest(Process):
    def __init__(self, shop_index: int, name: str, generator: DelayGenerator, gstate=GlobalState()):
        super().__init__(name, generator)
        self.shop_index = shop_index
        self.gstate = gstate

    def get_wsstock(self):
        return self.gstate.get_wholesale_stock()

    def get_restock_amount(self):
        return self.gstate.get_shop_restock_amount(self.shop_index)

    def is_busy(self):
        return self.state == State.BUSY

    def on_busy(self):
        restock_amount = self.gstate.get_shop_restock_amount(self.shop_index)
        self.gstate.update_wholesale_stock(amount=-restock_amount)

        if LOGGING:
            print(
                f"[{self.tcurr:.6f} | ProcessShopRequest({self.shop_index})]  Delivery initiated. wsstock = {self.get_wsstock()} | Due: {self.tnext}"
            )

    def on_freed(self):
        restock_amount = self.gstate.get_shop_restock_amount(self.shop_index)
        self.gstate.update_shop_stock(self.shop_index, amount=restock_amount)
        self.gstate.set_shop_pending_status(self.shop_index, is_pending=False)

    def print_info(self):
        stock = self.gstate.get_shop_stock(self.shop_index)
        print(f"[{self.tcurr:.6f} | ProcessShopRequest({self.shop_index})]  Restock complete. New stock = {stock}")
