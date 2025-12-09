from Delivery_app_BK.models import Order,Route,db, Item
from Delivery_app_BK.models.managers.object_searcher import GetObject
from Delivery_app_BK.models.managers.object_inspector import ColumnInspector
from Delivery_app_BK.models.managers.object_validators import ValueValidator, DataStructureValidators

from Delivery_app_BK.services.item_services.service_create import service_create_item
from Delivery_app_BK.services.item_services.service_update import service_update_item

def write_order ( current_obj_id, val_1, val_2, to_add, obj_list:list[Order], add_loop= 0 ):
    for indx in range( val_1, val_2 + add_loop ):
        obj = obj_list[indx]

        if obj.id == current_obj_id:
            continue
        
        obj.delivery_arrangement += to_add
    


def helper_order_arrangement (order_obj:Order, new_arrangement:int | None, route:Route):

    orders_list = route.delivery_orders
    previous_arrangement = order_obj.delivery_arrangement 
    
    if previous_arrangement is None:
        previous_arrangement = len(orders_list) - 1
    
    if new_arrangement is None:
        new_arrangement = len(orders_list) - 1
        
    
    if new_arrangement < previous_arrangement:
        write_order( order_obj.id, new_arrangement, previous_arrangement, 1, orders_list )

    elif new_arrangement > previous_arrangement:
        write_order(order_obj.id,  previous_arrangement, new_arrangement, -1, orders_list, 1)

    order_obj.delivery_arrangement = new_arrangement


def service_update_order_arrangement(order_obj: Order, new_arrangement: int | None, route: Route):
    helper_order_arrangement(order_obj=order_obj, new_arrangement=new_arrangement, route=route)
    return order_obj
   

def service_update_order(data: dict, identity=None) -> dict:
    order_obj:Order = GetObject.get_object(Order, data.get("id"), identity=identity)
    route_has_change = False
    new_route = 0
    fields: dict = data.get("fields", {})
    items_created = []
    created_items_payload = []
    # if change of route it must update the arrengament to None and flush, 
    # so that later in the loop if there is delivery_arrangement it will update the object on the new route
    if 'route_id' in fields:
        
        route_obj:Route = GetObject.get_object(Route, order_obj.route_id, identity=identity)
        service_update_order_arrangement(
            order_obj = order_obj,
            new_arrangement = None,
            route = route_obj
        )

        order_obj.delivery_arrangement = None
        setattr( order_obj, 'route_id', fields['route_id'] )
        
        # flags that route has change for later in the loop to query on the new route
        # if the delivery_arrangemnt is pass 
        route_has_change = True
        new_route = fields['route_id']

        # removes the key so that loop does not update twice
        del fields['route_id']

    # updates the Order fields 
    for field, value in fields.items():
        column = ColumnInspector(field, Order)
        column_name = column.column_name

        # updates the delivery_arranegement on current or new route
        if column_name == "delivery_arrangement":
           
            if route_has_change:
                route_obj = GetObject.get_object(Route, new_route, identity=identity)
            else:
                route_obj = GetObject.get_object(Route, order_obj.route_id, identity=identity)

            service_update_order_arrangement(
                order_obj = order_obj,
                new_arrangement = value,
                route = route_obj,
            )

            continue

        # creates items on order 
        if column_name == 'delivery_items':
            value = DataStructureValidators.is_list_of_dicts(value)

            for item_fields in value:
                action = (item_fields.get("action") or "create").lower()
                client_reference = item_fields.get("client_reference")

                if action == "create":
                    payload_fields = item_fields.get("fields", item_fields)
                    payload_fields = dict(payload_fields)
                    client_reference = payload_fields.pop("client_reference", client_reference)
                    if "order_id" not in payload_fields:
                        payload_fields["order_id"] = order_obj
                    new_item = service_create_item(payload_fields, identity=identity)
                    if new_item['status'] == 'ok':
                        item_instance = new_item["instance"]
                        items_created.append(item_instance)
                        db.session.add(item_instance)
                        db.session.flush()
                        created_items_payload.append(
                            {
                                "id": item_instance.id,
                                "client_reference": client_reference
                            }
                        )
                        if item_instance not in order_obj.delivery_items:
                            order_obj.delivery_items.append(item_instance)
                    continue

                if action == "update":
                    item_id = item_fields.get("id")
                    update_fields = item_fields.get("fields")
                    if item_id is None or update_fields is None:
                        continue
                    
                    service_update_item({"id": item_id, "fields": update_fields}, identity=identity)
                    continue

                if action == "delete":
                    item_id = item_fields.get("id")
                    if item_id is None:
                        continue
                    # TODO: replace with dedicated delete service when available.
                    item_obj = GetObject.get_object(Item, item_id, identity=identity)
                    db.session.delete(item_obj)
                    continue

            continue


        column_type = column.get_python_type()
        valid_value = ValueValidator.is_valid_value(value, column_type)
        
        setattr(order_obj, column.column_name, valid_value)

    # if items where created it will add them to the session
    if items_created:
        db.session.add_all(items_created)
        if created_items_payload:
            setattr(order_obj, "_created_items_payload", created_items_payload)

    return {"status": "ok", "instance": order_obj}
