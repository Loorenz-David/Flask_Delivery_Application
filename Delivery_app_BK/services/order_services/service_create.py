# Local Imports
from Delivery_app_BK.models import Order,Route,db
from Delivery_app_BK.services import create_general_object
from Delivery_app_BK.services import service_create_item


"""
this functions call create_general_object for simple column fill
or simple link between relationships, if something more fancy is required
it can me modified on the service function
"""

# CREATE Order Instance and if Items passed to order
def service_create_order(fields:dict)->dict:

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
    
    # creates Order instance 
    new_order = create_general_object(fields, Order, rel_map)
    order_instance = new_order["instance"]
    
    if new_order["status"] == "ok":
        db.session.add(order_instance)
        db.session.flush()
        
        for item_fields in items:
            
            #injects the new Order to the column that will link Item and Order
            item_fields["order_id"] = order_instance.id
          
            # creates Item instance 
            new_item = service_create_item(item_fields)

            
            
            if new_item["status"] == 'ok':
                db.session.add(new_item["instance"])
               
            else:
                raise Exception(f"Something whent wrong when creating item with art: {item_fields.get("article_number","art missing")}",
                                f"for order with client name: {fields.get("client_name","name missing")}. "
                                )


    return {'status':'ok','instance': []}
        



