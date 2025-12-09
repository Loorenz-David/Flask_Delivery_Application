# Local Imports
from Delivery_app_BK.models import Order,Route,db
from Delivery_app_BK.services.general_services.general_creation import create_general_object
from Delivery_app_BK.services.item_services.service_create import service_create_item


"""
this functions call create_general_object for simple column fill
or simple link between relationships, if something more fancy is required
it can me modified on the service function
"""

# CREATE Order Instance and if Items passed to order
def service_create_order(fields:dict, identity=None)->dict:

    # provie the rel map for Route
    rel_map = {
        "route_id":Route
    }

    # gets and removes the items from the fields dictionary 
    items:list[dict] = fields.pop("delivery_items",None)
    if not items:
        raise ValueError("Order has no Items! order must contain at leats one item.")
    
    if not isinstance(items,list):
        if isinstance(items,dict):
            items = [items]
        else:
             raise ValueError("Wrong format for creating item. items fields must be in dictionary")
    print(fields)
    if not isinstance(fields.get("delivery_arrangement",None), int):
        route_id = fields.get("route_id")
        if route_id is None:
            raise ValueError("Order cannot determine delivery arrangement without route_id.")
        last_order = (
            Order.query.filter(Order.route_id == route_id)
            .order_by(Order.delivery_arrangement.desc())
            .first()
        )
        next_arrangement = (last_order.delivery_arrangement if last_order else 0) or 0
        fields["delivery_arrangement"] = next_arrangement + 1
    print('the fields before the create genereal object function call ')
    print(fields)
    # creates Order instance 
    new_order = create_general_object(fields, Order, rel_map, identity=identity)
    order_instance = new_order["instance"]
    created_items = []
    
    if new_order["status"] == "ok":
        db.session.add(order_instance)
        db.session.flush()
        
        for item_fields in items:
            
            #injects the new Order to the column that will link Item and Order
            item_fields["order_id"] = order_instance.id
          
            # creates Item instance 
            new_item = service_create_item(item_fields, identity=identity)

            
            
            if new_item["status"] == 'ok':
                item_instance = new_item["instance"]
                created_items.append(item_instance)
                db.session.add(item_instance)
               
            else:
                raise Exception(
                    f"Something whent wrong when creating item with art: {item_fields.get('article_number', 'art missing')}",
                    f"for order with client name: {fields.get('client_name', 'name missing')}" 
                )

        if created_items:
            order_instance.delivery_items = created_items

    return {'status':'ok','instance': order_instance}
        
