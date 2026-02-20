from Delivery_app_BK.models import db, CaseChat, OrderCase, Team, User, NotificationRead
from Delivery_app_BK.errors import NotFound, ValidationFailed
from Delivery_app_BK.services.context import ServiceContext
from Delivery_app_BK.services.commands.base.create_instance import create_instance
from Delivery_app_BK.services.commands.utils import (
    extract_fields,
    build_create_result,
)
from Delivery_app_BK.services.queries.get_instance import get_instance


def create_case_chat(ctx: ServiceContext):
    relationship_map = {
        "team_id": Team,
        "order_case_id": OrderCase,
        "order_case": OrderCase,
        "user_id":User
    }
    ctx.set_relationship_map(relationship_map)
    instances = []


    user_id = ctx.identity.get('user_id') 
    
    if not user_id:
        raise NotFound("Could not create a chat because User not found")

    for field_set in extract_fields(ctx):

        if "order_case_id" not in field_set:
            raise ValidationFailed("Chat must pass an order_case_id")
            
        field_set['user_id'] = user_id

        
        instance: CaseChat = create_instance(ctx, CaseChat, dict(field_set))
        instances.append(instance)
        
        notification_read = create_instance(ctx, NotificationRead, {'user_id':user_id})

        instance.notification_reads.append( notification_read )
        

    db.session.add_all(instances)
    db.session.flush()
    result = build_create_result(ctx, instances)
    db.session.commit()
    return {"case_chat": result}
