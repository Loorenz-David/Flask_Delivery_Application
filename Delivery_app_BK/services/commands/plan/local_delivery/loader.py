from Delivery_app_BK.errors import ValidationFailed
from Delivery_app_BK.models import DeliveryPlan, LocalDeliveryPlan, RouteSolution
from Delivery_app_BK.services.context import ServiceContext
from Delivery_app_BK.services.queries.get_instance import get_instance
from Delivery_app_BK.services.requests.plan.local_delivery.update_settings import (
    LocalDeliverySettingsRequest,
)


def load_local_delivery_settings_entities(
    ctx: ServiceContext,
    request: LocalDeliverySettingsRequest,
) -> tuple[LocalDeliveryPlan, DeliveryPlan, RouteSolution]:
    local_delivery_plan: LocalDeliveryPlan = get_instance(
        ctx=ctx,
        model=LocalDeliveryPlan,
        value=request.local_delivery_plan_id,
    )

    delivery_plan: DeliveryPlan | None = local_delivery_plan.delivery_plan
    if not delivery_plan:
        raise ValidationFailed("Local delivery plan has no delivery plan.")

    route_solution: RouteSolution = get_instance(
        ctx=ctx,
        model=RouteSolution,
        value=request.route_solution.route_solution_id,
    )

    if route_solution.local_delivery_plan_id != local_delivery_plan.id:
        raise ValidationFailed("Route solution does not belong to local delivery plan.")

    return local_delivery_plan, delivery_plan, route_solution
