from typing import Type, Dict, List
from Delivery_app_BK.services.domain.item.item_states import ItemStateId
from Delivery_app_BK.services.domain.order.order_states import OrderStateId
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
    RouteSolutionStop,
)

from ...context import ServiceContext
from ...domain.order.order_events import OrderEvent
from ..base.create_instance import create_instance
from ..utils import extract_fields, build_create_result
from .event_emitter import emit_order_events
from .plan_objectives import apply_order_plan_objective


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
            return []
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
        if not "item_state_id" in item_fields:
            item_instance.item_state_id = ItemStateId.OPEN
        order_instance.items.append(item_instance)
        item_instances.append( item_instance )
    
    return item_instances


def create_order(ctx: ServiceContext):
    relationship_map = {
        "team_id": Team,
        "order_state_id": OrderStateId,
        "delivery_plan_id": DeliveryPlan,
        "items": Item,
        "item_state_id": ItemState,
        "item_position_id": ItemPosition,
    }
    ctx.set_relationship_map(relationship_map)

    order_instances:List[Order] = []
    item_instances:List[Item] = []
    extra_instances = []
    route_stop_links = []
    route_stop_instances = []
    has_delivery_plan = False
    orders_with_delivery_plan: List[Order] = []
    for field_set in extract_fields(ctx):
        order_fields = dict(field_set)
        plan_objective = order_fields.pop("order_plan_objective", None)
        items_payload = order_fields.pop("items", None)

        order_instance: Order = create_instance(ctx, Order, order_fields)
        if not "order_state_id" in order_fields:
            order_instance.order_state_id = OrderStateId.DRAFT
            
        order_instances.append(order_instance)

        delivery_plan_id = order_fields.get("delivery_plan_id")

        if delivery_plan_id:
            has_delivery_plan = True
            orders_with_delivery_plan.append(order_instance)
            new_instances, stop_links = apply_order_plan_objective(
                ctx,
                order_instance,
                delivery_plan_id,
                plan_objective,
            )
            extra_instances.extend(new_instances)
            route_stop_links.extend(stop_links)
            for instance in new_instances:
                if isinstance(instance, RouteSolutionStop):
                    route_stop_instances.append(instance)


        if items_payload is not None:
            item_instances = _create_items_on_order( ctx, items_payload, order_instance )

    db.session.add_all(order_instances)
    if item_instances:
        db.session.add_all(item_instances)
    
    if extra_instances:
        db.session.add_all(extra_instances)

    db.session.flush()

    if route_stop_links:
        for stop_instance, order_instance in route_stop_links:
            stop_instance.order_id = order_instance.id

    order_results = build_create_result(ctx, order_instances, extract_fields=['id',"order_plan_objective", "order_state_id"])
    item_results = build_create_result(ctx, item_instances, extract_fields=['id', 'item_state_id']) if item_instances else None
    route_stop_results = (
        build_create_result(
            ctx,
            route_stop_instances,
            extract_fields=[
                "id",
                "route_solution_id",
                "order_id",
                "stop_order",
                "in_range",
                "reason_was_skipped",
            ],
        )
        if route_stop_instances
        else None
    )

    db.session.commit()

    result = {"order": order_results}
    if item_results is not None:
        result["item"] = item_results

    if route_stop_results is not None:
        result["order_stop"] = route_stop_results


    
    events_to_emit = []
    for order_instance in order_instances:
        event_block = {
            "order_id": order_instance.id,
            "team_id":order_instance.team_id,
            "event_name": OrderEvent.CREATED.value
        }
        payload = {
            "order_state_id": order_instance.order_state_id,
            "order_plan_objective": order_instance.order_plan_objective,
        }
        
        if order_instance.delivery_plan_id:
            payload = {
                ** payload,
                ** {
                    "delivery_plan_id": order_instance.delivery_plan_id,
                    "order_plan_objective": order_instance.order_plan_objective,
                }
            }
            event_block['event_name'] = OrderEvent.CONFIRMED.value

        event_block['payload'] = payload
        events_to_emit.append(event_block)
        
    emit_order_events(
        ctx,
        events_to_emit
    )

    return result
