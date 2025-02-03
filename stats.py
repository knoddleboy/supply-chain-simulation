import matplotlib.pyplot as plt
from constants import N_SHOPS, MODEL_PARAMS, SHOP_SAFETY_STOCK, STATISTICS_START_TIME


class ShopStats:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ShopStats, cls).__new__(cls, *args, **kwargs)
            cls._instance.initialize()
        return cls._instance

    def initialize(self):
        self.days = [[] for _ in range(N_SHOPS)]
        self.demand = [[] for _ in range(N_SHOPS)]
        self.restock = [[] for _ in range(N_SHOPS)]
        self.rop = MODEL_PARAMS["SHOP_REORDER_POINT"]

    def add_stock_level(self, shop_index: int, time: float, n: int):
        if time < STATISTICS_START_TIME or time > STATISTICS_START_TIME + 300:
            return

        if n > 0:
            self.days[shop_index].append(time)
            self.demand[shop_index].append(n)

    def add_failure(self, shop_index: int, time: float):
        if time < STATISTICS_START_TIME or time > STATISTICS_START_TIME + 300:
            return

        days = self.days[shop_index]
        demand = self.demand[shop_index]

        if not days or not demand:
            return

        if demand[-1] > 0:
            days.extend([time, time])
            demand.extend([0, -1])

        else:
            days[-1] = time
            demand[-1] -= 1

    def add_restock_point(self, shop_index: int, time: float):
        if time < STATISTICS_START_TIME or time > STATISTICS_START_TIME + 300:
            return

        self.restock[shop_index].append(time)

    def plot_all(self):
        for shop_index in range(N_SHOPS - 1, -1, -1):
            self._plot(shop_index)
        plt.show()

    def plot(self, shop_index: int):
        self._plot(shop_index)
        plt.show()

    def _plot(self, shop_index: int):
        days = self.days[shop_index]
        demand = self.demand[shop_index]
        restock = self.restock[shop_index]

        plt.figure(figsize=(15, 8), num=f"Shop {shop_index}")

        plt.plot(days, demand, label="Рівень запасів")

        plt.fill_between(days, demand, self.rop, where=[y > self.rop for y in demand], color="green", alpha=0.1)
        plt.fill_between(days, demand, self.rop, where=[y <= self.rop for y in demand], color="steelblue", alpha=0.15)
        plt.fill_between(
            days, demand, SHOP_SAFETY_STOCK, where=[y <= SHOP_SAFETY_STOCK for y in demand], color="navy", alpha=0.12
        )
        plt.fill_between(days, demand, 0, where=[y <= 0 for y in demand], color="gray", alpha=0.45, hatch="/")

        plt.axhline(
            MODEL_PARAMS["SHOP_MAX_STOCK"],
            color="green",
            linestyle="--",
            label=f"Макс. бажаний запас: {MODEL_PARAMS["SHOP_MAX_STOCK"]}",
        )
        plt.axhline(self.rop, color="red", linestyle="--", label=f"Граничний рівень: {self.rop}")
        if SHOP_SAFETY_STOCK > 0:
            plt.axhline(
                SHOP_SAFETY_STOCK, color="navy", linestyle="--", label=f"Гарантійний запас: {SHOP_SAFETY_STOCK}"
            )
        # plt.axhline(y=0, color="gray", linestyle="-")

        lowest_peak = None
        restock_idx = 0
        for i, (x, y) in enumerate(zip(days, demand)):
            if y < 0 and (i == 0 or demand[i - 1] >= 0):
                if lowest_peak is None or y < lowest_peak[1]:
                    lowest_peak = (x, y)

                while restock_idx < len(restock) and restock[restock_idx] <= x:
                    restock_idx += 1

                if restock_idx > 0:
                    lead_time = x - restock[restock_idx - 1]
                    plt.text(
                        x,
                        y,
                        f"{lead_time:.1f}",
                        color="red",
                        fontsize=9,
                        ha="center",
                        va="top",
                    )

        if lowest_peak:
            x, y = lowest_peak
            plt.axhline(
                y=y,
                color="blue",
                linestyle="--",
                linewidth=1.3,
                label=f"Максимум відмов: {y}",
                alpha=0.6,
            )

        plt.title(f"Графік контролю запасів {shop_index}-ї торгової точки")
        plt.xlabel("Час (дні)")
        plt.ylabel("Рівень запасу (од)")
        plt.legend()
        plt.grid(visible=True, alpha=0.6)
