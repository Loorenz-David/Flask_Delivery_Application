from sqlalchemy.exc import InvalidRequestError
from Delivery_app_BK.errors import NotFound
from Delivery_app_BK.models import DeliveryPlan, db
from Delivery_app_BK.services.context import ServiceContext
from Delivery_app_BK.services.requests.plan.update_plan_state import (
    parse_update_plan_state_request,
)
from Delivery_app_BK.services.utils import model_requires_team, require_team_id


def update_plan_state(
    ctx: ServiceContext,
    plan_ids: int | list[int],
    state_id: int,
) -> list[int]:
    request = parse_update_plan_state_request(plan_ids, state_id)

    def _apply() -> list[int]:
        plans = _resolve_plans_for_update(ctx, request.plan_ids)
        for plan in plans:
            plan.state_id = request.state_id
        return [plan.id for plan in plans]

    try:
        with db.session.begin():
            return _apply()
    except InvalidRequestError as exc:
        if "already begun" not in str(exc).lower():
            raise
        return _apply()


def _resolve_plans_for_update(
    ctx: ServiceContext,
    plan_ids: list[int],
) -> list[DeliveryPlan]:
    query = db.session.query(DeliveryPlan).filter(DeliveryPlan.id.in_(plan_ids))
    if model_requires_team(DeliveryPlan) and ctx.check_team_id:
        query = query.filter(DeliveryPlan.team_id == require_team_id(ctx))

    plans = query.all()
    plans_by_id = {plan.id: plan for plan in plans}
    missing_ids = [plan_id for plan_id in plan_ids if plan_id not in plans_by_id]
    if missing_ids:
        raise NotFound(f"Delivery plans not found: {missing_ids}")

    return [plans_by_id[plan_id] for plan_id in plan_ids]
