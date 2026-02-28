from __future__ import annotations

from collections.abc import Callable

from ....context import ServiceContext
from .local_delivery import handle_local_delivery_order_delete_extension
from .types import OrderDeleteDelta, OrderDeleteExtensionContext, OrderDeleteExtensionResult


OrderDeleteExtensionHandler = Callable[
    [ServiceContext, list[OrderDeleteDelta], OrderDeleteExtensionContext],
    OrderDeleteExtensionResult,
]


PLAN_TYPE_DELETE_EXTENSION_HANDLERS: dict[str, OrderDeleteExtensionHandler] = {
    "local_delivery": handle_local_delivery_order_delete_extension,
}


def resolve_delete_extension_handler(
    plan_type: str,
) -> OrderDeleteExtensionHandler | None:
    return PLAN_TYPE_DELETE_EXTENSION_HANDLERS.get(plan_type)
