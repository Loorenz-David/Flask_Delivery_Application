from Delivery_app_BK.models.tables.notifications_models import EmailSMTP, TwilioMod, MessageTemplates
from Delivery_app_BK.models.tables.users_models import Team
from Delivery_app_BK.services.general_services.general_creation import create_general_object


def service_create_email_smtp(fields: dict) -> dict:
    rel_map = {
        "team_id": Team,
        "team": Team,
    }
    return create_general_object(fields, EmailSMTP, rel_map)


def service_create_twilio_mod(fields: dict) -> dict:
    rel_map = {
        "team_id": Team,
        "team": Team,
    }
    return create_general_object(fields, TwilioMod, rel_map)


def service_create_message_template(fields: dict) -> dict:
    rel_map = {
        "team_id": Team,
        "team": Team,
    }
    return create_general_object(fields, MessageTemplates, rel_map)
