from global_state import GlobalState
from generators import ConstantGenerator, ExponentialGenerator, BoundedNormalGenerator, LogNormalGenerator
from scheduled_create import ScheduledCreate
from core.routing import Route
from customer_service import CreateCustomer, ProcessCustomer
from shop_restock import CreateShopRequest, DispatchShopRequest, ProcessShopRequest
from wholesale_restock import CreateWholesaleRequest, ProcessWholesaleRequest
from constants import N_SHOPS, N_RUNS, MODEL_PARAMS
from stats import ShopStats
from model import Model


state = GlobalState()

shop_stats = ShopStats()


def create_ws_restock_subnet():
    create_request = CreateWholesaleRequest("Create WS restock request", ConstantGenerator(14))
    process_request = ProcessWholesaleRequest(
        "Process WS restock",
        BoundedNormalGenerator(mean=90, dev=10, min=60, max=120),
        amount=MODEL_PARAMS["WHOLESALE_RESTOCK_AMOUNT"],
    )
    create_request.next_elements = [Route(process_request)]

    create_scheduled = ScheduledCreate("Create scheduled WS restock request", [30, 60, 90])
    process_scheduled = ProcessWholesaleRequest(
        "Process scheduled WS restock",
        ConstantGenerator(0),
        amount=MODEL_PARAMS["WHOLESALE_SCHEDULED_AMOUNT"],
    )
    create_scheduled.next_elements = [Route(process_scheduled)]

    return [create_request, process_request, create_scheduled, process_scheduled]


def create_shop_restock_subnet(shop_idx: int):
    create_request = CreateShopRequest(shop_idx, f"Create shop {shop_idx} request", ConstantGenerator(1))
    dispatch_request = DispatchShopRequest(shop_idx, f"Dispatch shop {shop_idx} request", ConstantGenerator(1))
    process_request = ProcessShopRequest(shop_idx, f"Process shop {shop_idx} request", LogNormalGenerator(5, 1))

    create_request.next_elements = [
        Route(
            dispatch_request,
            block_cond=lambda: dispatch_request.get_stock() > MODEL_PARAMS["SHOP_REORDER_POINT"]
            or dispatch_request.get_is_pending() == True,
        )
    ]
    dispatch_request.next_elements = [
        Route(
            process_request,
            block_cond=lambda: process_request.get_wsstock() < process_request.get_restock_amount()
            or process_request.is_busy() == True,
        )
    ]

    return [create_request, dispatch_request, process_request]


def create_customer_service_subnet(shop_idx: int):
    create_customers = CreateCustomer(shop_idx, f"Create customer shop {shop_idx}", ExponentialGenerator(0.1))
    process_customers = ProcessCustomer(shop_idx, f"Process customer shop {shop_idx}", ConstantGenerator(0))

    create_customers.next_elements = [
        Route(
            process_customers,
            block_cond=lambda: process_customers.get_stock() == 0,
            # block_cond=lambda: process_customers.is_blocked()
        )
    ]

    return [create_customers, process_customers]


def create_model():
    state.initialize()
    shop_stats.initialize()

    elements = []
    elements.extend(create_ws_restock_subnet())

    for shop_idx in range(N_SHOPS):
        elements.extend(create_customer_service_subnet(shop_idx))
        elements.extend(create_shop_restock_subnet(shop_idx))

    model = Model(*elements, logging=False)
    model.simulate(300)

    return model


avg_retail_failure_probs = []
avg_wholesale_stocks = []

for _ in range(N_RUNS):
    model = create_model()
    avg_retail_failure_probs.append(model.get_avg_shop_failure_prob())
    avg_wholesale_stocks.append(model.get_avg_wholesale_stock())

print(f"\nAverage shop failure probability = {sum(avg_retail_failure_probs)/len(avg_retail_failure_probs) * 100} %")
print(f"Average wholesale stock level = {sum(avg_wholesale_stocks)/len(avg_wholesale_stocks)}")
