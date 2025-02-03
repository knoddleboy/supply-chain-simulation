from constants import N_SHOPS, MODEL_PARAMS


class GlobalState:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(GlobalState, cls).__new__(cls, *args, **kwargs)
            cls._instance.initialize()
        return cls._instance

    def initialize(self):
        self.shop_stock = [MODEL_PARAMS["INITIAL_SHOP"]] * N_SHOPS
        self.shop_pending_status = [False] * N_SHOPS
        self.shop_restock_amount = [0] * N_SHOPS

        self.wholesale_stock = MODEL_PARAMS["INITIAL_WHOLESALE"]

    def set_shop_restock_amount(self, shop_index: int, amount: int):
        self.shop_restock_amount[shop_index] = amount

    def get_shop_restock_amount(self, shop_index: int):
        return self.shop_restock_amount[shop_index]

    def update_shop_stock(self, shop_index: int, amount: int):
        if 0 <= shop_index < N_SHOPS:
            self.shop_stock[shop_index] += amount
        else:
            raise IndexError("Invalid shop index.")

    def get_shop_stock(self, shop_index: int):
        if 0 <= shop_index < N_SHOPS:
            return self.shop_stock[shop_index]
        else:
            raise IndexError("Invalid shop index.")

    def set_shop_pending_status(self, shop_index: int, is_pending: bool):
        self.shop_pending_status[shop_index] = is_pending

    def is_shop_pending(self, shop_index: int):
        return self.shop_pending_status[shop_index]

    def update_wholesale_stock(self, amount: int):
        self.wholesale_stock += amount

    def get_wholesale_stock(self):
        return self.wholesale_stock
