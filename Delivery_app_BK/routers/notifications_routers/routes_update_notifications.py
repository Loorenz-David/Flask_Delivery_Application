from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required

from . import notifications_bp
from Delivery_app_BK.routers.utils.response import Response
from Delivery_app_BK.models.managers.object_filler import ObjectFiller
from Delivery_app_BK.services import (
    service_update_email_smtp,
    service_update_twilio_mod,
    service_update_message_template,
)


@notifications_bp.route("/update_email_smtp", methods=["PUT"])
@jwt_required()
def update_email_smtp():
    identity = get_jwt_identity()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)

    ObjectFiller.fill_object(
        fill_function=service_update_email_smtp,
        response=response,
        reference="Email SMTP configuration",
        add_to_session=False,
        action_type="update",
    )

    return response.build()


@notifications_bp.route("/update_twilio_mod", methods=["PUT"])
@jwt_required()
def update_twilio_mod():
    identity = get_jwt_identity()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)

    ObjectFiller.fill_object(
        fill_function=service_update_twilio_mod,
        response=response,
        reference="Twilio configuration",
        add_to_session=False,
        action_type="update",
    )

    return response.build()


@notifications_bp.route("/update_message_template", methods=["PUT"])
@jwt_required()
def update_message_template():
    identity = get_jwt_identity()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)

    ObjectFiller.fill_object(
        fill_function=service_update_message_template,
        response=response,
        reference="Message Template",
        add_to_session=False,
        action_type="update",
    )

    return response.build()
