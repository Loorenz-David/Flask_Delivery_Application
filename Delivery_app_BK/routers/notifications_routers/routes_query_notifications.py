from flask import request

from . import notifications_bp
from Delivery_app_BK.routers.utils.response import Response
from Delivery_app_BK.models.tables.notifications_models import EmailSMTP, TwilioMod, MessageTemplates
from Delivery_app_BK.models.managers.object_searcher import FindObjects


@notifications_bp.route("/query_email_smtp", methods=["POST"])
def query_email_smtp():
    response = Response()
    incoming_data = request.get_json()

    FindObjects.find_objects(
        response=response,
        Model=EmailSMTP,
        incoming_data=incoming_data,
    )

    return response.build()


@notifications_bp.route("/query_twilio_mod", methods=["POST"])
def query_twilio_mod():
    response = Response()
    incoming_data = request.get_json()

    FindObjects.find_objects(
        response=response,
        Model=TwilioMod,
        incoming_data=incoming_data,
    )

    return response.build()


@notifications_bp.route("/query_message_template", methods=["POST"])
def query_message_template():
    response = Response()
    incoming_data = request.get_json()

    FindObjects.find_objects(
        response=response,
        Model=MessageTemplates,
        incoming_data=incoming_data,
    )

    return response.build()
