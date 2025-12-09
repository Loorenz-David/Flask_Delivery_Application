# Local Imports
from Delivery_app_BK.models import db
from Delivery_app_BK.models.managers.object_searcher import GetObject

# import types
from typing import Type
from flask_sqlalchemy.model import Model


def delete_general_object(
    data: dict,
    Model: Type[Model],
    identity=None,
) -> dict:
    """
    Deletes a single instance by id using the provided SQLAlchemy model.
    """
    instance = GetObject.get_object(Model, data.get("id"), identity=identity)
    db.session.delete(instance)
    return {"status": "ok", "instance": instance}
