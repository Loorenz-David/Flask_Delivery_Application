from typing import Dict, Any

from Delivery_app_BK.models.tables.notifications_models import EmailSMTP, TwilioMod, MessageTemplate
from Delivery_app_BK.models.tables.users_models import Team
from Delivery_app_BK.models.managers.object_searcher import GetObject
from Delivery_app_BK.models.managers.object_inspector import ColumnInspector
from Delivery_app_BK.models.managers.object_validators import ValueValidator


def _update_instance(model, instance, fields: Dict[str, Any], relationship_map: Dict[str, object], identity=None) -> None:
    for field, value in fields.items():
        column = ColumnInspector(field, model)
        target_model = relationship_map.get(field)

        if target_model and (column.is_foreign_key() or column.is_relationship()):
            link = instance.update_link(
                column=column,
                value=value,
                target_model=target_model,
                identity=identity
            )
            if not link:
                raise Exception(f"Failed to update relation '{field}' on {model.__name__}")
            continue

        column_type = column.get_python_type()
        valid_value = ValueValidator.is_valid_value(value, column_type)
        setattr(instance, column.column_name, valid_value)


def service_update_email_smtp(data: dict, identity=None) -> dict:
    email_smtp = GetObject.get_object(EmailSMTP, data.get("id"), identity=identity)
    fields = data.get("fields", {})
    relationship_map = {
        "team_id": Team,
        "team": Team,
    }

    _update_instance(EmailSMTP, email_smtp, fields, relationship_map, identity=identity)
    return {"status": "ok", "instance": email_smtp}


def service_update_twilio_mod(data: dict, identity=None) -> dict:
    twilio = GetObject.get_object(TwilioMod, data.get("id"), identity=identity)
    fields = data.get("fields", {})
    relationship_map = {
        "team_id": Team,
        "team": Team,
    }

    _update_instance(TwilioMod, twilio, fields, relationship_map, identity=identity)
    return {"status": "ok", "instance": twilio}


def service_update_message_template(data: dict, identity=None) -> dict:
    message_template = GetObject.get_object(MessageTemplate, data.get("id"), identity=identity)
    fields = data.get("fields", {})
    relationship_map = {
        "team_id": Team,
        "team": Team,
    }

    _update_instance(MessageTemplate, message_template, fields, relationship_map, identity=identity)
    return {"status": "ok", "instance": message_template}
