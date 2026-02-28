from __future__ import annotations

from collections.abc import Callable
from typing import List, Tuple

from Delivery_app_BK.errors import ValidationFailed
from Delivery_app_BK.models import (
    InternationalShippingPlan,
    LocalDeliveryPlan,
    RouteSolution,
    StorePickupPlan,
)
from Delivery_app_BK.route_optimization.constants.is_optimized import (
    IS_OPTIMIZED_NOT_OPTIMIZED,
)
from Delivery_app_BK.services.commands.utils import generate_client_id

from ...context import ServiceContext
from ..base.create_instance import create_instance


PlanTypeFactory = Callable[[ServiceContext, str | None], Tuple[object, List[object]]]


PLAN_TYPE_MODEL_MAP = {
    "local_delivery": LocalDeliveryPlan,
    "international_shipping": InternationalShippingPlan,
    "store_pickup": StorePickupPlan,
}


def _resolve_client_id(client_id: str | None, prefix: str) -> str:
    if isinstance(client_id, str):
        normalized = client_id.strip()
        if normalized:
            return normalized
    return generate_client_id(prefix)


def _build_local_delivery_plan_type(
    ctx: ServiceContext,
    client_id: str | None,
) -> Tuple[LocalDeliveryPlan, List[object]]:
    local_delivery_client_id = _resolve_client_id(client_id, "local_delivery")
    plan_type_instance = create_instance(
        ctx,
        LocalDeliveryPlan,
        {"client_id": local_delivery_client_id},
    )

    route_solution = RouteSolution(
        client_id=generate_client_id("route_solution"),
        label="variant 1",
        is_selected=True,
        is_optimized=IS_OPTIMIZED_NOT_OPTIMIZED,
        stop_count=0,
        team_id=ctx.team_id,
    )
    plan_type_instance.route_solutions.append(route_solution)
    return plan_type_instance, [route_solution]


def _build_simple_plan_type(
    ctx: ServiceContext,
    plan_type_model,
    client_id: str | None,
    client_id_prefix: str,
) -> Tuple[object, List[object]]:
    plan_type_instance = create_instance(
        ctx,
        plan_type_model,
        {"client_id": _resolve_client_id(client_id, client_id_prefix)},
    )
    return plan_type_instance, []


PLAN_TYPE_FACTORIES: dict[str, PlanTypeFactory] = {
    "local_delivery": _build_local_delivery_plan_type,
    "international_shipping": lambda ctx, client_id: _build_simple_plan_type(
        ctx,
        InternationalShippingPlan,
        client_id,
        "international_shipping",
    ),
    "store_pickup": lambda ctx, client_id: _build_simple_plan_type(
        ctx,
        StorePickupPlan,
        client_id,
        "store_pickup",
    ),
}


def build_plan_type_instances(
    ctx: ServiceContext,
    plan_type: str,
    plan_instance,
    client_id: str | None = None,
) -> Tuple[object, List[object]]:
    if not plan_type:
        raise ValidationFailed("Missing plan_type.")
    if plan_type not in PLAN_TYPE_MODEL_MAP:
        raise ValidationFailed(f"Invalid plan_type: {plan_type}")

    factory = PLAN_TYPE_FACTORIES.get(plan_type)
    if not factory:
        raise ValidationFailed(f"No builder registered for plan_type: {plan_type}")

    plan_type_instance, extra_instances = factory(ctx, client_id)
    setattr(plan_instance, plan_type, plan_type_instance)
    return plan_type_instance, extra_instances
