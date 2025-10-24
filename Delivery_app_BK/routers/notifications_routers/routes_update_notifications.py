from flask import request

from . import notifications_bp
from Delivery_app_BK.routers.utils.response import Response
from Delivery_app_BK.models.managers.object_filler import ObjectFiller
from Delivery_app_BK.services import (
    service_update_email_smtp,
    service_update_twilio_mod,
    service_update_message_template,
)


@notifications_bp.route("/update_email_smtp", methods=["PUT"])
def update_email_smtp():
    response = Response()
    incoming_data = request.get_json()

    ObjectFiller.fill_object(
        data=incoming_data,
        fill_function=service_update_email_smtp,
        response=response,
        reference="Email SMTP configuration",
        add_to_session=False,
        action_type="update",
    )

    return response.build()


@notifications_bp.route("/update_twilio_mod", methods=["PUT"])
def update_twilio_mod():
    response = Response()
    incoming_data = request.get_json()

    ObjectFiller.fill_object(
        data=incoming_data,
        fill_function=service_update_twilio_mod,
        response=response,
        reference="Twilio configuration",
        add_to_session=False,
        action_type="update",
    )

    return response.build()


@notifications_bp.route("/update_message_template", methods=["PUT"])
def update_message_template():
    response = Response()
    incoming_data = request.get_json()

    ObjectFiller.fill_object(
        data=incoming_data,
        fill_function=service_update_message_template,
        response=response,
        reference="Message Template",
        add_to_session=False,
        action_type="update",
    )

    return response.build()
