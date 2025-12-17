from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from Delivery_app_BK.routers.utils.role_decorator import role_required


from . import notifications_bp
from Delivery_app_BK.routers.utils.response import Response
from Delivery_app_BK.models.tables.notifications_models import EmailSMTP, TwilioMod, MessageTemplate
from Delivery_app_BK.models.managers.object_searcher import FindObjects
from .notifications_default_data_request import (
    MESSAGE_TEMPLATE_REQUESTED_DATA,
)


@notifications_bp.route("/query_message_template", methods=["POST"])
@jwt_required()
@role_required([1, 2])
def query_message_template():
    identity = get_jwt()
    incoming_data = request.get_json(silent=True)
    response = Response(incoming_data=incoming_data, identity=identity)
    payload = response.incoming_data or {}
    if not isinstance(payload, dict):
        payload = {}
    if not payload.get('requested_data'):
        payload['requested_data'] = MESSAGE_TEMPLATE_REQUESTED_DATA
        response.incoming_data = payload

    FindObjects.find_objects(
        response=response,
        Model=MessageTemplate,
        identity=identity,
    )

    return response.build()


@notifications_bp.route("/are_services_active", methods=["GET"])
@jwt_required()
@role_required([1, 2])
def are_services_active():
    identity = get_jwt()
    response = Response(identity=identity)
    try:
        team_id = identity.get('team_id') if isinstance(identity, dict) else None
        if team_id is None:
            raise ValueError("Missing team_id in identity")

        smtp_exists = EmailSMTP.query.filter_by(team_id=team_id).first() is not None
        twilio_exists = TwilioMod.query.filter_by(team_id=team_id).first() is not None

        response.set_payload({
            "smtp": smtp_exists,
            "twilio": twilio_exists
        })
        response.set_message("Service status fetched successfully.")
    except Exception as e:
        response.set_error(message=str(e), status=400)
        response.set_message("Failed to check notification services.")

    return response.build()
