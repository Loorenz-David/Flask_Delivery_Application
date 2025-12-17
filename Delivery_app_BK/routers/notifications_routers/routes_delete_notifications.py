from flask import request
from flask_jwt_extended import jwt_required, get_jwt
from Delivery_app_BK.routers.utils.role_decorator import role_required

from Delivery_app_BK.models.managers.object_filler import ObjectFiller
from Delivery_app_BK.routers.utils.response import Response
from Delivery_app_BK.services import (
    service_delete_email_smtp,
    service_delete_twilio_mod,
    service_delete_message_template,
)
from . import notifications_bp


@notifications_bp.route("/delete_email_smtp", methods=["DELETE"])
@jwt_required()
@role_required([1])
def delete_email_smtp():
    identity = get_jwt()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)

    ObjectFiller.fill_object(
        fill_function=service_delete_email_smtp,
        response=response,
        reference="Email SMTP configuration",
        add_to_session=False,
        action_type='delete',
    )

    return response.build()


@notifications_bp.route("/delete_twilio_mod", methods=["DELETE"])
@jwt_required()
@role_required([1])
def delete_twilio_mod():
    identity = get_jwt()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)

    ObjectFiller.fill_object(
        fill_function=service_delete_twilio_mod,
        response=response,
        reference="Twilio configuration",
        add_to_session=False,
        action_type='delete',
    )

    return response.build()


@notifications_bp.route("/delete_message_template", methods=["DELETE"])
@jwt_required()
@role_required([1])
def delete_message_template():
    identity = get_jwt()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)

    ObjectFiller.fill_object(
        fill_function=service_delete_message_template,
        response=response,
        reference="Message Template",
        add_to_session=False,
        action_type='delete',
    )

    return response.build()
