from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required

from . import notifications_bp
from Delivery_app_BK.routers.utils.response import Response
from Delivery_app_BK.models.tables.notifications_models import EmailSMTP, TwilioMod, MessageTemplate
from Delivery_app_BK.models.managers.object_searcher import FindObjects


@notifications_bp.route("/query_email_smtp", methods=["POST"])
@jwt_required()
def query_email_smtp():
    identity = get_jwt_identity()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)

    FindObjects.find_objects(
        response=response,
        Model=EmailSMTP,
        identity=identity,
    )

    return response.build()


@notifications_bp.route("/query_twilio_mod", methods=["POST"])
@jwt_required()
def query_twilio_mod():
    identity = get_jwt_identity()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)

    FindObjects.find_objects(
        response=response,
        Model=TwilioMod,
        identity=identity,
    )

    return response.build()


@notifications_bp.route("/query_message_template", methods=["POST"])
@jwt_required()
def query_message_template():
    identity = get_jwt_identity()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)

    FindObjects.find_objects(
        response=response,
        Model=MessageTemplate,
        identity=identity,
    )

    return response.build()
