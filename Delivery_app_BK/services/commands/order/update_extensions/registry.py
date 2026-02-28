from __future__ import annotations

from collections.abc import Callable

from ....context import ServiceContext
from .local_delivery import handle_local_delivery_order_update_extension
from .types import OrderUpdateDelta, OrderUpdateExtensionContext, OrderUpdateExtensionResult


OrderUpdateExtensionHandler = Callable[
    [ServiceContext, list[OrderUpdateDelta], OrderUpdateExtensionContext],
    OrderUpdateExtensionResult,
]


PLAN_TYPE_UPDATE_EXTENSION_HANDLERS: dict[str, OrderUpdateExtensionHandler] = {
    "local_delivery": handle_local_delivery_order_update_extension,
}


def resolve_update_extension_handler(
    plan_type: str,
) -> OrderUpdateExtensionHandler | None:
    return PLAN_TYPE_UPDATE_EXTENSION_HANDLERS.get(plan_type)
