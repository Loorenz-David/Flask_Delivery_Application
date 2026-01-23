from sqlalchemy.orm.exc import NoResultFound

from Delivery_app_BK.errors import NotFound
from Delivery_app_BK.models import db, Order, OrderState
from ...context import ServiceContext
from ...queries.get_instance import get_instance


def update_order_state(
    ctx: ServiceContext,
    order_id: int | str,
    state_id: int | str,
):
    try:
        order_instance: Order = get_instance(ctx, Order, order_id)
        state_instance: OrderState = get_instance(ctx, OrderState, state_id)
    except NoResultFound as exc:
        raise NotFound(str(exc)) from exc

    order_instance.order_state_id = state_instance.id
    db.session.commit()
    return order_instance
