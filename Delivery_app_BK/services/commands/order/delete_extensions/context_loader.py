from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable

from Delivery_app_BK.models import (
    InternationalShippingPlan,
    LocalDeliveryPlan,
    RouteSolution,
    StorePickupPlan,
    db,
)

from ....context import ServiceContext
from .types import OrderDeleteDelta, OrderDeleteExtensionContext

PlanTypeDeleteContextLoader = Callable[
    [ServiceContext, list[int], list[OrderDeleteDelta], OrderDeleteExtensionContext],
    None,
]


def _collect_plan_ids_by_type(
    delete_deltas: list[OrderDeleteDelta],
) -> dict[str, list[int]]:
    collected: defaultdict[str, set[int]] = defaultdict(set)
    for delta in delete_deltas:
        delivery_plan = delta.delivery_plan
        plan_id = getattr(delivery_plan, "id", None)
        plan_type = getattr(delivery_plan, "plan_type", None)
        if plan_id is None or not plan_type:
            continue
        collected[plan_type].add(plan_id)
    return {plan_type: sorted(plan_ids) for plan_type, plan_ids in collected.items()}


def _load_local_delivery_context(
    ctx: ServiceContext,
    plan_ids: list[int],
    _delete_deltas: list[OrderDeleteDelta],
    extension_context: OrderDeleteExtensionContext,
) -> None:
    local_context: dict[str, object] = {}

    local_query = db.session.query(LocalDeliveryPlan).filter(
        LocalDeliveryPlan.delivery_plan_id.in_(plan_ids)
    )
    if ctx.team_id:
        local_query = local_query.filter(LocalDeliveryPlan.team_id == ctx.team_id)
    local_delivery_instances = local_query.all()
    local_context["local_delivery_by_plan_id"] = {
        instance.delivery_plan_id: instance for instance in local_delivery_instances
    }

    local_delivery_ids = [instance.id for instance in local_delivery_instances]
    if not local_delivery_ids:
        local_context["route_solutions_by_local_delivery_id"] = {}
        local_context["route_solutions_by_id"] = {}
        extension_context.by_plan_type["local_delivery"] = local_context
        return

    route_query = db.session.query(RouteSolution).filter(
        RouteSolution.local_delivery_plan_id.in_(local_delivery_ids)
    )
    if ctx.team_id:
        route_query = route_query.filter(RouteSolution.team_id == ctx.team_id)
    route_solutions = route_query.all()

    grouped: defaultdict[int, list[RouteSolution]] = defaultdict(list)
    route_solutions_by_id: dict[int, RouteSolution] = {}
    for route_solution in route_solutions:
        grouped[route_solution.local_delivery_plan_id].append(route_solution)
        if route_solution.id is not None:
            route_solutions_by_id[route_solution.id] = route_solution

    local_context["route_solutions_by_local_delivery_id"] = dict(grouped)
    local_context["route_solutions_by_id"] = route_solutions_by_id
    extension_context.by_plan_type["local_delivery"] = local_context


def _load_international_shipping_context(
    ctx: ServiceContext,
    plan_ids: list[int],
    _delete_deltas: list[OrderDeleteDelta],
    extension_context: OrderDeleteExtensionContext,
) -> None:
    query = db.session.query(InternationalShippingPlan).filter(
        InternationalShippingPlan.delivery_plan_id.in_(plan_ids)
    )
    if ctx.team_id:
        query = query.filter(InternationalShippingPlan.team_id == ctx.team_id)
    extension_context.by_plan_type["international_shipping"] = {
        "international_shipping_by_plan_id": {
            instance.delivery_plan_id: instance for instance in query.all()
        }
    }


def _load_store_pickup_context(
    ctx: ServiceContext,
    plan_ids: list[int],
    _delete_deltas: list[OrderDeleteDelta],
    extension_context: OrderDeleteExtensionContext,
) -> None:
    query = db.session.query(StorePickupPlan).filter(
        StorePickupPlan.delivery_plan_id.in_(plan_ids)
    )
    if ctx.team_id:
        query = query.filter(StorePickupPlan.team_id == ctx.team_id)
    extension_context.by_plan_type["store_pickup"] = {
        "store_pickup_by_plan_id": {
            instance.delivery_plan_id: instance for instance in query.all()
        }
    }


PLAN_TYPE_DELETE_CONTEXT_LOADERS: dict[str, PlanTypeDeleteContextLoader] = {
    "local_delivery": _load_local_delivery_context,
    "international_shipping": _load_international_shipping_context,
    "store_pickup": _load_store_pickup_context,
}


def build_order_delete_extension_context(
    ctx: ServiceContext,
    delete_deltas: list[OrderDeleteDelta],
) -> OrderDeleteExtensionContext:
    context = OrderDeleteExtensionContext()
    if not delete_deltas:
        return context

    plan_ids_by_type = _collect_plan_ids_by_type(delete_deltas)
    for plan_type, plan_ids in plan_ids_by_type.items():
        loader = PLAN_TYPE_DELETE_CONTEXT_LOADERS.get(plan_type)
        if not loader:
            continue
        loader(ctx, plan_ids, delete_deltas, context)

    return context
