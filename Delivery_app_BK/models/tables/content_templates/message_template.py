from sqlalchemy.orm import validates
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.orm import relationship

from Delivery_app_BK.models import db
from Delivery_app_BK.models.mixins.team_mixings.team_id import TeamScopedMixin


class MessageTemplate(db.Model, TeamScopedMixin):
    __tablename__ = "message_template"

    id = Column(Integer, primary_key=True)
    client_id = Column(String, index=True)
    content = Column(Text, nullable=False)
    name = Column(String, nullable=False, index=True)
    channel = Column(String, nullable=False, index=True)
    timestampt = Column(DateTime)

    is_system = Column(Boolean, default=False, index=True)

    team = relationship(
        "Team",
        backref="message_templates",
        lazy=True
    )


    ALLOWED_CHANNELS = {"sms", "email", "whatsapp"}
    @validates("channel")
    def validate_channel(self, key, value):
        if value not in self.ALLOWED_CHANNELS:
            raise ValueError(
                f"Invalid channel '{value}'. "
                f"Allowed values: {self.ALLOWED_CHANNELS}"
            )
        return value


class SafeDict(dict):
    def __missing__(self, key):
        # Return the placeholder unchanged if missing
        return f"{{{key}}}"
