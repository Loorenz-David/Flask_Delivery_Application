from __future__ import annotations

from typing import List

from Delivery_app_BK.errors import ValidationFailed
from Delivery_app_BK.models import LocalDeliveryPlan, Order, RouteSolution, db
from Delivery_app_BK.services.commands.utils import generate_client_id
from Delivery_app_BK.route_optimization.constants.is_optimized import (
    IS_OPTIMIZED_NOT_OPTIMIZED,
)

from Delivery_app_BK.services.context import ServiceContext
from Delivery_app_BK.services.queries.get_instance import get_instance
from .stops import build_route_solution_stops_for_order_ids
from Delivery_app_BK.services.commands.utils import build_create_result


def create_route_solution(ctx: ServiceContext):
    incoming_data = ctx.incoming_data or {}
    local_delivery_plan_id = incoming_data.get("local_delivery_plan_id")
    if not local_delivery_plan_id:
        raise ValidationFailed("local_delivery_plan_id is required.")

    allowed_keys = {"local_delivery_plan_id", "client_id"}
    extra_keys = set(incoming_data.keys()) - allowed_keys
    if extra_keys:
        raise ValidationFailed(f"Unexpected fields: {sorted(extra_keys)}")

    local_delivery_plan = get_instance(
        ctx=ctx,
        model=LocalDeliveryPlan,
        value=local_delivery_plan_id,
    )

    client_id = incoming_data.get("client_id") or generate_client_id('route_solution')

    route_solution = RouteSolution(
        client_id=client_id,
        label="variant 1",
        is_selected=True,
        is_optimized=IS_OPTIMIZED_NOT_OPTIMIZED,
        stop_count=0,
        team_id=ctx.team_id,
        delivery_plan_id=local_delivery_plan.id,
    )
    local_delivery_plan.route_solutions.append(route_solution)

    if not local_delivery_plan.delivery_plan_id:
        raise ValidationFailed("Local delivery plan is missing delivery_plan_id.")
    order_ids = _get_order_ids(local_delivery_plan.delivery_plan_id)
    stop_instances, _updated_solutions = build_route_solution_stops_for_order_ids(
        ctx,
        order_ids,
        [route_solution],
    )

    db.session.add(route_solution)
    if stop_instances:
        db.session.add_all(stop_instances)

    db.session.flush()

    route_solution_result = build_create_result(
        ctx,
        [route_solution],
        extract_fields=["id", "label", "is_optimized", "is_selected", "stop_count"],
    )
    route_stop_result = build_create_result(
        ctx,
        stop_instances,
        extract_fields=[
            "id",
            "route_solution_id",
            "order_id",
            "stop_order",
            "in_range",
            "reason_was_skipped",
        ],
    )

    db.session.commit()

    return {
        "route_solution": route_solution_result,
        "route_solution_stop": route_stop_result,
    }


def _get_order_ids(delivery_plan_id: int) -> List[int]:
    return [
        row[0]
        for row in db.session.query(Order.id)
        .filter(Order.delivery_plan_id == delivery_plan_id)
        .all()
    ]
