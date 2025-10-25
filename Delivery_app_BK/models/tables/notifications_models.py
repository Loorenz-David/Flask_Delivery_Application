from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Column, Integer, String,Boolean, Text
from sqlalchemy.orm import relationship


from Delivery_app_BK.models.mixins.smtp_mixin import SMTPMixin
from Delivery_app_BK.models.mixins.twilio_mixin import SMSMixin

from Delivery_app_BK.models import db
from Delivery_app_BK.models.mixins.teams_mixings import TeamScopedMixin
from Delivery_app_BK.models.managers.object_obtainer import ObjectObtainer
from Delivery_app_BK.models.managers.object_updator import ObjectUpdator



class EmailSMTP(db.Model, ObjectObtainer, ObjectUpdator, TeamScopedMixin, SMTPMixin):
    __tablename__ = "EmailSMTP"

    id = Column(Integer, primary_key=True)
    smtp_server = Column(String, nullable=False)
    smtp_port = Column(Integer, default=587)
    smtp_username = Column(String, nullable=False)
    smtp_password_encrypted = Column(String, nullable=False)
    use_tls = Column(Boolean, default=True)
    use_ssl = Column(Boolean, default=False)
    max_per_session = Column(Integer, default=50)

    team = relationship(
        "Team", 
        backref="email_settings", 
        lazy=True
    )



class TwilioMod(db.Model, ObjectObtainer, ObjectUpdator, TeamScopedMixin, SMSMixin):
    __tablename__ = "TwilioMod"
    
    id = Column(Integer, primary_key=True)
    twilio_sid = Column(String)
    twilio_token_encrypted = Column(String)
    sender_number = Column(String)

    team = relationship(
        "Team", 
        backref="twilio_settings", 
        lazy=True
    )

class MessageTemplate(db.Model, ObjectObtainer, ObjectUpdator, TeamScopedMixin):
    __tablename__ = "MessageTemplate"

    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    name = Column(String, nullable=False)
    channel = Column(String, nullable=False)
    
    team = relationship(
        "Team", 
        backref="message_templates", 
        lazy=True
    )

class SafeDict(dict):
    def __missing__(self, key):
        # Return the placeholder unchanged if missing
        return f"{{{key}}}"