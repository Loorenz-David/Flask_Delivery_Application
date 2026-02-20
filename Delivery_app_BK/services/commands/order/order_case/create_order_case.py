from Delivery_app_BK.models import db, OrderCase, Order, Team, User
from Delivery_app_BK.errors import NotFound, ValidationFailed
from Delivery_app_BK.services.context import ServiceContext
from Delivery_app_BK.services.commands.base.create_instance import create_instance
from Delivery_app_BK.services.commands.utils import (
    extract_fields,
    build_create_result,
)
from Delivery_app_BK.services.domain.order.order_case_states import OrderCaseState 


def create_order_case(ctx: ServiceContext):
    relationship_map = {
        "team_id": Team,
        "order_id": Order,
        "created_by": User,
    }
    ctx.set_relationship_map(relationship_map)
    instances = []
    user_id = ctx.identity.get('user_id') 

    if not user_id:
        raise NotFound("Could not create a chat because User not found")


    for field_set in extract_fields(ctx):

        if 'order_id' not in field_set:
            raise ValidationFailed("Case must have an order id.")

        if isinstance(user_id, int):
            field_set['created_by'] = user_id

        
        instance: OrderCase = create_instance(ctx, OrderCase, dict(field_set))

       
        if 'state' not in field_set:
            instance.state = OrderCaseState.OPEN.value

        instances.append(instance)

    db.session.add_all(instances)
    db.session.flush()
    result = build_create_result(ctx, instances, extract_fields=['id',"state"])
    db.session.commit()
    return {"order_case": result}
