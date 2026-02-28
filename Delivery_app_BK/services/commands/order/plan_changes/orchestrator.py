from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable

from Delivery_app_BK.models import (
    DeliveryPlan,
    InternationalShippingPlan,
    LocalDeliveryPlan,
    RouteSolution,
    StorePickupPlan,
    db,
)

from ....context import ServiceContext
from .local_delivery import apply_local_delivery_plan_change
from .types import PlanChangeApplyContext, PlanChangeResult


PlanChangeHandler = Callable[
    [ServiceContext, object, DeliveryPlan | None, DeliveryPlan | None, PlanChangeApplyContext],
    PlanChangeResult,
]

PlanChangeContextLoader = Callable[
    [ServiceContext, list[int], PlanChangeApplyContext],
    None,
]


PLAN_CHANGE_HANDLERS: dict[str, PlanChangeHandler] = {
    "local_delivery": apply_local_delivery_plan_change,
}


def apply_order_plan_change(
    ctx: ServiceContext,
    order_instance,
    old_plan: DeliveryPlan | None,
    new_plan: DeliveryPlan | None,
    apply_context: PlanChangeApplyContext,
) -> PlanChangeResult:
    old_plan_type = getattr(old_plan, "plan_type", None)
    new_plan_type = getattr(new_plan, "plan_type", None)

    if not old_plan_type and not new_plan_type:
        return PlanChangeResult()

    handler_types = [
        plan_type
        for plan_type in (old_plan_type, new_plan_type)
        if plan_type in PLAN_CHANGE_HANDLERS
    ]
    if not handler_types:
        return PlanChangeResult()
    unique_handler_types = list(dict.fromkeys(handler_types))

    partial_results: list[PlanChangeResult] = []
    instances: list[object] = []
    post_flush_actions: list[Callable[[], None]] = []

    for plan_type in unique_handler_types:
        handler = PLAN_CHANGE_HANDLERS[plan_type]
        partial = handler(ctx, order_instance, old_plan, new_plan, apply_context)
        partial_results.append(partial)
        instances.extend(partial.instances)
        post_flush_actions.extend(partial.post_flush_actions)

    return PlanChangeResult(
        instances=instances,
        post_flush_actions=post_flush_actions,
        bundle_serializer=lambda results=partial_results: _serialize_bundle_results(results),
    )


def build_plan_change_apply_context(
    ctx: ServiceContext,
    plan_ids: list[int],
    relevant_plan_types: set[str] | None = None,
) -> PlanChangeApplyContext:
    deduped_plan_ids = list(dict.fromkeys(plan_ids))
    apply_context = PlanChangeApplyContext()
    if not deduped_plan_ids:
        return apply_context

    if relevant_plan_types is None:
        loader_keys = set(PLAN_CHANGE_CONTEXT_LOADERS.keys())
    else:
        loader_keys = {
            plan_type
            for plan_type in relevant_plan_types
            if plan_type in PLAN_CHANGE_CONTEXT_LOADERS
        }

    for plan_type in loader_keys:
        loader = PLAN_CHANGE_CONTEXT_LOADERS[plan_type]
        loader(ctx, deduped_plan_ids, apply_context)

    return apply_context


def _load_local_delivery_context(
    ctx: ServiceContext,
    plan_ids: list[int],
    apply_context: PlanChangeApplyContext,
) -> None:
    local_query = db.session.query(LocalDeliveryPlan).filter(
        LocalDeliveryPlan.delivery_plan_id.in_(plan_ids)
    )
    if ctx.team_id:
        local_query = local_query.filter(LocalDeliveryPlan.team_id == ctx.team_id)

    local_delivery_instances = local_query.all()
    apply_context.local_delivery_by_plan_id = {
        instance.delivery_plan_id: instance for instance in local_delivery_instances
    }

    route_solutions_by_local_delivery_id: defaultdict[int, list[RouteSolution]] = defaultdict(
        list
    )
    local_delivery_ids = [instance.id for instance in local_delivery_instances]
    if local_delivery_ids:
        route_query = db.session.query(RouteSolution).filter(
            RouteSolution.local_delivery_plan_id.in_(local_delivery_ids)
        )
        if ctx.team_id:
            route_query = route_query.filter(RouteSolution.team_id == ctx.team_id)

        for route_solution in route_query.all():
            route_solutions_by_local_delivery_id[
                route_solution.local_delivery_plan_id
            ].append(route_solution)

    apply_context.route_solutions_by_local_delivery_id = dict(
        route_solutions_by_local_delivery_id
    )


def _load_international_shipping_context(
    ctx: ServiceContext,
    plan_ids: list[int],
    apply_context: PlanChangeApplyContext,
) -> None:
    query = db.session.query(InternationalShippingPlan).filter(
        InternationalShippingPlan.delivery_plan_id.in_(plan_ids)
    )
    if ctx.team_id:
        query = query.filter(InternationalShippingPlan.team_id == ctx.team_id)

    apply_context.international_shipping_by_plan_id = {
        instance.delivery_plan_id: instance for instance in query.all()
    }


def _load_store_pickup_context(
    ctx: ServiceContext,
    plan_ids: list[int],
    apply_context: PlanChangeApplyContext,
) -> None:
    query = db.session.query(StorePickupPlan).filter(
        StorePickupPlan.delivery_plan_id.in_(plan_ids)
    )
    if ctx.team_id:
        query = query.filter(StorePickupPlan.team_id == ctx.team_id)

    apply_context.store_pickup_by_plan_id = {
        instance.delivery_plan_id: instance for instance in query.all()
    }


PLAN_CHANGE_CONTEXT_LOADERS: dict[str, PlanChangeContextLoader] = {
    "local_delivery": _load_local_delivery_context,
    "international_shipping": _load_international_shipping_context,
    "store_pickup": _load_store_pickup_context,
}


def _serialize_bundle_results(results: list[PlanChangeResult]) -> dict:
    bundle: dict = {}
    for result in results:
        bundle.update(result.serialize_bundle())
    return bundle
