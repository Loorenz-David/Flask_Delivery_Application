from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt


from . import notifications_bp
from Delivery_app_BK.routers.utils.response import Response
from Delivery_app_BK.models.managers.object_filler import ObjectFiller
from Delivery_app_BK.services import (
    service_create_email_smtp,
    service_create_twilio_mod,
    service_create_message_template,
)


@notifications_bp.route("/create_email_smtp", methods=["POST"])
@jwt_required()
def create_email_smtp():
    identity = get_jwt()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)

    created_instances = ObjectFiller.fill_object(
        fill_function=service_create_email_smtp,
        response=response,
        reference="Email SMTP configuration",
    )
    response.set_created_payload(created_instances)

    return response.build()


@notifications_bp.route("/create_twilio_mod", methods=["POST"])
@jwt_required()
def create_twilio_mod():
    identity = get_jwt()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)

    created_instances = ObjectFiller.fill_object(
        fill_function=service_create_twilio_mod,
        response=response,
        reference="Twilio configuration",
    )
    response.set_created_payload(created_instances)

    return response.build()


@notifications_bp.route("/create_message_template", methods=["POST"])
@jwt_required()
def create_message_template():
    identity = get_jwt()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)

    created_instances = ObjectFiller.fill_object(
        fill_function=service_create_message_template,
        response=response,
        reference="Message Template",
    )
    response.set_created_payload(created_instances)

    return response.build()
