from Delivery_app_BK.models import Route
from Delivery_app_BK.models.managers import GetObject, ColumnInspector, ValueValidator


def service_update_route(data: dict) -> dict:
    route_obj = GetObject.get_object(Route, data.get("id"))

    fields: dict = data.get("fields", {})
    for field, value in fields.items():
        column = ColumnInspector(field, Route)


        # when notification system is set up add the push notification of route change sate to admins
        # if field == 'state_id':
           


        column_type = column.get_python_type()
        valid_value = ValueValidator.is_valid_value(value, column_type)
        
        setattr(route_obj, column.column_name, valid_value)

    return {"status": "ok", "instance": route_obj}
