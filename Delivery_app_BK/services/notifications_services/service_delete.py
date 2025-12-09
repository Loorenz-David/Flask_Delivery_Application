from Delivery_app_BK.models.tables.notifications_models import EmailSMTP, TwilioMod, MessageTemplate
from Delivery_app_BK.services.general_services.general_deletion import delete_general_object


def service_delete_email_smtp(data: dict, identity=None) -> dict:
    return delete_general_object(data, EmailSMTP, identity=identity)


def service_delete_twilio_mod(data: dict, identity=None) -> dict:
    return delete_general_object(data, TwilioMod, identity=identity)


def service_delete_message_template(data: dict, identity=None) -> dict:
    return delete_general_object(data, MessageTemplate, identity=identity)
