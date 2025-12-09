from Delivery_app_BK.models import Order, db
from Delivery_app_BK.models.managers.object_searcher import GetObject


def service_delete_order(data: dict, identity=None) -> dict:
    order = GetObject.get_object(Order, data.get("id"), identity=identity)
    db.session.delete(order)
    return {"status": "ok", "instance": order}
