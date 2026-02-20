from __future__ import annotations

from typing import List, Tuple

from ....context import ServiceContext
from .local_delivery import apply_local_delivery_plan_change


PLAN_CHANGE_HANDLERS = {
    "local_delivery": apply_local_delivery_plan_change,
}


def apply_order_plan_change(
    ctx: ServiceContext,
    order_instance,
    old_plan,
    new_plan,
) -> Tuple[List[object], List[Tuple[object, object]]]:
    old_plan_type = getattr(old_plan, "plan_type", None)
    new_plan_type = getattr(new_plan, "plan_type", None)

    if not old_plan_type and not new_plan_type:
        return [], []

    handlers = {
        plan_type
        for plan_type in (old_plan_type, new_plan_type)
        if plan_type in PLAN_CHANGE_HANDLERS
    }

    extra_instances: List[object] = []
    stop_links: List[Tuple[object, object]] = []

    for plan_type in handlers:
        handler = PLAN_CHANGE_HANDLERS[plan_type]
        new_instances, new_stop_links = handler(
            ctx, order_instance, old_plan, new_plan
        )
        extra_instances.extend(new_instances)
        stop_links.extend(new_stop_links)

    return extra_instances, stop_links
