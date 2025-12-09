from Delivery_app_BK.models.tables.notifications_models import EmailSMTP, TwilioMod, MessageTemplate
from Delivery_app_BK.models.tables.users_models import Team
from Delivery_app_BK.services.general_services.general_creation import create_general_object
from Delivery_app_BK.models import db
import asyncio


def service_create_email_smtp(fields: dict, identity=None) -> dict:
    rel_map = {
        "team_id": Team,
        "team": Team,
    }
    team_id = identity.get("team_id") if isinstance(identity, dict) else None
    if team_id:
        existing = EmailSMTP.query.filter_by(team_id=team_id).all()
        for entry in existing:
            db.session.delete(entry)
    temp_instance = EmailSMTP()
    for key, value in fields.items():
        if hasattr(temp_instance, key):
            setattr(temp_instance, key, value)
    # verify connection before creating record
    try:
        
        asyncio.run(temp_instance.get_smtp_connection())
    except Exception as e:
        raise ValueError(f"SMTP connection failed: {str(e)}")

    return create_general_object(fields, EmailSMTP, rel_map, identity=identity)


def service_create_twilio_mod(fields: dict, identity=None) -> dict:
    rel_map = {
        "team_id": Team,
        "team": Team,
    }
    team_id = identity.get("team_id") if isinstance(identity, dict) else None
    if team_id:
        existing = TwilioMod.query.filter_by(team_id=team_id).all()
        for entry in existing:
            db.session.delete(entry)
    temp_instance = TwilioMod()
    for key, value in fields.items():
        if hasattr(temp_instance, key):
            setattr(temp_instance, key, value)
    try:
        asyncio.run(temp_instance.get_twilio_client())
    except Exception as e:
        raise ValueError(f"Twilio connection failed: {str(e)}")

    return create_general_object(fields, TwilioMod, rel_map, identity=identity)


def service_create_message_template(fields: dict, identity=None) -> dict:
    rel_map = {
        "team_id": Team,
        "team": Team,
    }
    return create_general_object(fields, MessageTemplate, rel_map, identity=identity)
