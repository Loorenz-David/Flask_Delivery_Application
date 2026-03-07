from __future__ import annotations
from datetime import datetime, timezone
from Delivery_app_BK.errors import ValidationFailed, NotFound
from sqlalchemy.orm import selectinload
from Delivery_app_BK.models import LocalDeliveryPlan, RouteSolution, DeliveryPlan, Order, db
from Delivery_app_BK.route_optimization.domain.models import OptimizationContext
from Delivery_app_BK.services.queries.get_instance import get_instance
from Delivery_app_BK.services.context import ServiceContext
from Delivery_app_BK.route_optimization.constants.route_end_strategy import ROUND_TRIP, CUSTOM_END_ADDRESS
def _ensure_utc(value: datetime | None) -> datetime | None:
    if not value:
        return None
    return value.astimezone(timezone.utc) if value.tzinfo else value.replace(tzinfo=timezone.utc)


def load_optimization_context(ctx:ServiceContext) -> OptimizationContext:
    incoming_data = ctx.incoming_data or {}
    local_delivery_plan_id = incoming_data.get("local_delivery_plan_id")
    if local_delivery_plan_id is None:
        raise ValidationFailed("Missing local_delivery_plan_id.")

    local_delivery_plan = get_instance(
        ctx=ctx,
        model=LocalDeliveryPlan,
        value=local_delivery_plan_id,
    )
    delivery_plan: DeliveryPlan = local_delivery_plan.delivery_plan
    if not delivery_plan:
        raise ValidationFailed("Local delivery plan is missing delivery plan.")

    is_route_solution_end_date_valid(delivery_plan)

    route_solution = _select_route_solution(local_delivery_plan)

    orders = (
        db.session.query(Order)
        .options(selectinload(Order.delivery_windows), selectinload(Order.items))
        .filter(Order.delivery_plan_id == delivery_plan.id)
        .all()
    )
    if not orders:
        raise ValidationFailed("Delivery plan has no orders to optimize.")

    route_end_strategy = (incoming_data.get("route_end_strategy") or
                          route_solution.route_end_strategy or
                          ROUND_TRIP
                          )

    return OptimizationContext(
        local_delivery_plan=local_delivery_plan,
        delivery_plan=delivery_plan,
        route_solution=route_solution,
        orders=orders,
        identity=ctx.identity,
        incoming_data=incoming_data,
        route_end_strategy = route_end_strategy,
        interpret_injected_solutions_using_labels=bool(
            incoming_data.get("interpret_injected_solutions_using_labels", True)
        ),
        return_shape=str(incoming_data.get("return_shape") or "map_ids_object"),
        ctx=ctx,
    )


def _select_route_solution(local_delivery_plan: LocalDeliveryPlan) -> RouteSolution:
    route_solutions = list(local_delivery_plan.route_solutions or [])
    if not route_solutions:
        raise ValidationFailed("Local delivery plan has no route solutions.")

    for route_solution in route_solutions:
        if getattr(route_solution, "is_selected", False):
            return route_solution

    raise ValidationFailed("Local delivery plan has no selected route solution.")


def is_route_solution_end_date_valid (delivery_plan :DeliveryPlan):
    try:

        if delivery_plan:
            now = datetime.now(timezone.utc)
            start_date = _ensure_utc(delivery_plan.start_date) or now
            end_date = _ensure_utc(delivery_plan.end_date) or start_date
            
    except Exception:
        raise NotFound('route solution has no local delivery or local delivery plan has no delivery plan linked.')

    if end_date < now:
        raise ValidationFailed('This route has already ended and cannot be optimized. Update the delivery plan end date to a future time to re-optimize.')
