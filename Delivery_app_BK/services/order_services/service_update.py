from Delivery_app_BK.models import Order
from Delivery_app_BK.models.managers.object_searcher import GetObject
from Delivery_app_BK.models.managers.object_inspector import ColumnInspector
from Delivery_app_BK.models.managers.object_validators import ValueValidator

def helper_order_arrangement (order_obj):
    route = order_obj.route
    if not route:
        raise Exception (f"order with id: '{order_obj.id}', has no route ")

    

def service_update_order(data: dict) -> dict:
    order_obj:Order = GetObject.get_object(Order, data.get("id"))

    fields: dict = data.get("fields", {})
    for field, value in fields.items():
        column = ColumnInspector(field, Order)
        column_name = column.column_name

        if column_name == "delivery_arrangement":
            route_obj = order_obj.route
            print("route_object: ",route_obj.delivery_orders)

            continue

        column_type = column.get_python_type()
        valid_value = ValueValidator.is_valid_value(value, column_type)
        
        setattr(order_obj, column.column_name, valid_value)

    return {"status": "ok", "instance": order_obj}
