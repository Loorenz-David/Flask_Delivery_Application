from Delivery_app_BK.models import Warehouse
from Delivery_app_BK.errors import NotFound

from ....context import ServiceContext
from ...get_instance import get_instance
from .serialize_warehouses import serialize_warehouses


def get_warehouse(warehouse_id: int, ctx: ServiceContext):
    found_warehouse = get_instance(
        ctx=ctx,
        model=Warehouse,
        value=warehouse_id,
    )

    if not found_warehouse:
        raise NotFound(f"Warehouse with id: {warehouse_id} does not exist.")

    serialized = serialize_warehouses(
        instances=[found_warehouse],
        ctx=ctx,
    )

    return {
        "warehouse": serialized[0] if isinstance(serialized, list) else serialized
    }
