from sqlalchemy.orm.exc import NoResultFound

from Delivery_app_BK.errors import NotFound
from Delivery_app_BK.models import db, Order, DeliveryPlan
from ...context import ServiceContext
from ...queries.get_instance import get_instance


def update_order_delivery_plan(
    ctx: ServiceContext,
    order_id: int | str,
    plan_id: int | str,
):
    try:
        order_instance: Order = get_instance(ctx, Order, order_id)
        plan_instance: DeliveryPlan = get_instance(ctx, DeliveryPlan, plan_id)
    except NoResultFound as exc:
        raise NotFound(str(exc)) from exc

    order_instance.delivery_plan_id = plan_instance.id
    db.session.commit()
    return order_instance
