from Delivery_app_BK.models import Route, db
from Delivery_app_BK.models.managers.object_searcher import GetObject


def service_delete_route(data: dict, identity=None) -> dict:
    route = GetObject.get_object(Route, data.get("id"), identity=identity)
    db.session.delete(route)
    return {"status": "ok", "instance": route}
