# Thirs-party dependencies
from sqlalchemy.orm import validates
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean

# Local application imports
from Delivery_app_BK.models import db
from Delivery_app_BK.models.mixins.team_mixings.team_id import TeamScopedMixin


class LabelTemplate(db.Model, TeamScopedMixin):
    __tablename__ = "label_template"
    id = Column(Integer, primary_key=True)
    client_id = Column(String, index=True)
    name = Column(String, index=True)
    template_string = Column(Text)
    template_target = Column(String)  # Front end accepts "items" or "order"
    timestampt = Column(DateTime)

    is_system = Column(Boolean, default=False, index=True)

    team = relationship(
        "Team",
        backref="print_template_lable",
        lazy=True
    )


    ALLOWED_CHANNELS = {"order", "items"}
    @validates("template_target")
    def validate_channel(self, key, value):
        if value not in self.ALLOWED_CHANNELS:
            raise ValueError(
                f"Invalid channel '{value}'. "
                f"Allowed values: {self.ALLOWED_CHANNELS}"
            )
        return value