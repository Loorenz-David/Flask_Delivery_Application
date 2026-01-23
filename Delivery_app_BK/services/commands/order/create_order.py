from typing import Type, Dict, List
from Delivery_app_BK.errors import ValidationFailed
from Delivery_app_BK.models import (
    db,
    Order,
    Item,
    Team,
    DeliveryPlan,
    OrderState,
    ItemState,
    ItemPosition,
    OrderChat
)

from ...context import ServiceContext
from ..base.create_instance import create_instance
from ..utils import extract_fields, build_create_result


def _create_items_on_order( 
        ctx: ServiceContext, 
        items_payload: Dict[str, any], 
        order_instance: Order 
) -> List[Item] :
    
    item_instances = []

    if isinstance(items_payload, dict):
        item_sets = [items_payload]
    elif isinstance(items_payload, list) and all(
        isinstance(item, dict) for item in items_payload
    ):
        if not items_payload:
            raise ValidationFailed("Items list cannot be empty.")
        item_sets = items_payload
    else:
        raise ValidationFailed(
            "Items must be a dictionary or a list of dictionaries."
        )

    for item_fields in item_sets:
        order_id = item_fields.get('order_id')
        if not isinstance(order_id, int ):
            item_fields.pop('order_id', None)

        item_instance: Type[ Item ] = create_instance(ctx, Item, dict(item_fields))
        order_instance.items.append(item_instance)
        item_instances.append( item_instance )
    
    return item_instances


def _create_chats_on_order(
        ctx: ServiceContext, 
        chats_payload: Dict[str, any], 
        order_instance: Order 
) -> List[OrderChat] :
    
    chat_instances = []

    if isinstance(chats_payload, dict):
        chat_sets = [chats_payload]
    elif isinstance(chats_payload, list) and all(
        isinstance(chat, dict) for chat in chats_payload
    ):
        if not chats_payload:
            raise ValidationFailed("Chats list cannot be empty.")
        chat_sets = chats_payload
    else:
        raise ValidationFailed(
            "Chats must be a dictionary or a list of dictionaries."
        )

    for chat_fields in chat_sets:
        chat_instance: Type[ Item ] = create_instance(ctx, OrderChat, dict(chat_fields))
        order_instance.order_chats.append( chat_instance )
        chat_instances.append( chat_instance )
    

    return chat_instances


def create_order(ctx: ServiceContext):
    relationship_map = {
        "team_id": Team,
        "order_state_id": OrderState,
        "delivery_plan_id": DeliveryPlan,
        "items": Item,
        "item_state_id": ItemState,
        "item_position_id": ItemPosition,
    }
    ctx.set_relationship_map(relationship_map)

    order_instances = []
    item_instances = []
    chat_instances = []
    for field_set in extract_fields(ctx):
        order_fields = dict(field_set)
        items_payload = order_fields.pop("items", None)
        chats_payload = order_fields.pop( "order_chats", None )

        order_instance: Type[ Order ] = create_instance(ctx, Order, order_fields)
        order_instances.append(order_instance)


        if items_payload is not None:
            item_instances = _create_items_on_order( ctx, items_payload, order_instance )
        
        if chats_payload is not None:
            chat_instances = _create_chats_on_order( ctx, chats_payload, order_instance )

    db.session.add_all(order_instances)
    if item_instances:
        db.session.add_all(item_instances)
    
    if chat_instances:
        db.session.add_all( chat_instances )

    db.session.flush()

    order_results = build_create_result(ctx, order_instances)
    item_results = build_create_result(ctx, item_instances) if item_instances else None
    chat_results = build_create_result(ctx, chat_instances) if chat_instances else None

    db.session.commit()

    result = {"order": order_results}
    if item_results is not None:
        result["item"] = item_results

    if chat_results is not None:
        result["order_chat"] = chat_results

    return result
