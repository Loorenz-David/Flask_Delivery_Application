from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from Delivery_app_BK.models.mixins.external_integrations.twilio_mixin import SMSMixin

from Delivery_app_BK.models import db
from Delivery_app_BK.models.mixins.team_mixings.team_id import TeamScopedMixin


class TwilioMod(db.Model, TeamScopedMixin, SMSMixin):
    __tablename__ = "twilio_mod"

    id = Column(Integer, primary_key=True)
    client_id = Column(String, index=True)
    twilio_sid = Column(String)
    twilio_token_encrypted = Column(String)
    sender_number = Column(String)

    team = relationship(
        "Team",
        backref="twilio_settings",
        lazy=True
    )
