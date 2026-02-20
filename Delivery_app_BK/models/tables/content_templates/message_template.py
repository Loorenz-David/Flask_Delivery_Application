from sqlalchemy.orm import validates
from sqlalchemy import Column, Integer, String,  Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship

from Delivery_app_BK.errors import ValidationFailed
from Delivery_app_BK.models import db
from Delivery_app_BK.models.mixins.team_mixings.team_id import TeamScopedMixin
from Delivery_app_BK.models.utils import UTCDateTime
from Delivery_app_BK.services.domain.order.order_events import OrderEvent
from Delivery_app_BK.services.domain.plan.plan_events import DeliveryPlanEvent

class MessageTemplate(db.Model, TeamScopedMixin):
    __tablename__ = "message_template"
    __table_args__ = (
        UniqueConstraint(
            "team_id",
            "event",
            "channel",
            name="uq_message_template_team_event_channel"
        ),
    )

    id = Column(Integer, primary_key=True)
    client_id = Column(String, index=True)
    event = Column(String)
    enable = Column(Boolean)
    template = Column(JSONB)
    name = Column(String)
    ask_permission = Column(Boolean, default=False)
    channel = Column(String, nullable=False)


    timestampt = Column(UTCDateTime)

    team = relationship(
        "Team",
        backref="message_templates",
        lazy=True
    )


    ALLOWED_CHANNELS = set(["sms", "email", "whatsapp","telegram"])
    @validates("channel")
    def validate_channel(self, key, value):
        if value not in self.ALLOWED_CHANNELS:
            raise ValidationFailed(
                f"Invalid channel '{value}'. "
                f"Allowed values: {self.ALLOWED_CHANNELS}"
            )
        return value
    

    @validates("event")
    def validate_event(self, key, value):
        if (value not in OrderEvent._value2member_map_ and value not in DeliveryPlanEvent._value2member_map_):
            raise ValidationFailed(
                f"Invalid event '{value}'. "
                f"Allowed events: {[e.value for e in OrderEvent]}"
            )
        return value


class SafeDict(dict):
    def __missing__(self, key):
        # Return the placeholder unchanged if missing
        return f"{{{key}}}"
