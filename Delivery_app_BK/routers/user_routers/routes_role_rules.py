from flask import request
from flask_jwt_extended import jwt_required, get_jwt

from . import user_bp
from Delivery_app_BK.routers.utils.response import Response
from Delivery_app_BK.models.managers.object_filler import ObjectFiller
from Delivery_app_BK.routers.utils.role_decorator import role_required
from Delivery_app_BK.services import (
    service_create_role_rule,
    service_update_role_rule,
    service_delete_role_rule,
)


@user_bp.route("/create_role_rule", methods=["POST"])
@jwt_required()
@role_required([1])
def create_role_rule():
    identity = get_jwt()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)

    created_instances = ObjectFiller.fill_object(
        fill_function=service_create_role_rule,
        response=response,
        reference="Role Rule",
    )
    response.set_created_payload(created_instances)
    return response.build()


@user_bp.route("/update_role_rule", methods=["PUT"])
@jwt_required()
@role_required([1])
def update_role_rule():
    identity = get_jwt()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)

    ObjectFiller.fill_object(
        fill_function=service_update_role_rule,
        response=response,
        reference="Role Rule",
        add_to_session=False,
        action_type="update",
    )
    return response.build()


@user_bp.route("/delete_role_rule", methods=["DELETE"])
@jwt_required()
@role_required([1])
def delete_role_rule():
    identity = get_jwt()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)

    ObjectFiller.fill_object(
        fill_function=service_delete_role_rule,
        response=response,
        reference="Role Rule",
        add_to_session=False,
        action_type="delete",
    )
    return response.build()
