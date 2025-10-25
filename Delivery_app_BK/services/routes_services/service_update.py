from Delivery_app_BK.models import Route
from Delivery_app_BK.models.managers.object_searcher import GetObject
from Delivery_app_BK.models.managers.object_inspector import ColumnInspector
from Delivery_app_BK.models.managers.object_validators import ValueValidator


def service_update_route(data: dict, identity=None) -> dict:
    route_obj = GetObject.get_object(Route, data.get("id"), identity=identity)

    fields: dict = data.get("fields", {})
    for field, value in fields.items():
        column = ColumnInspector(field, Route)


        # when notification system is set up add the push notification of route change sate to admins
        # if field == 'state_id':
           


        column_type = column.get_python_type()
        valid_value = ValueValidator.is_valid_value(value, column_type)
        
        setattr(route_obj, column.column_name, valid_value)

    return {"status": "ok", "instance": route_obj}
