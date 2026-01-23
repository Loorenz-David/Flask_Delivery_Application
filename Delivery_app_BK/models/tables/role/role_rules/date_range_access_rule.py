# Thirs-party dependencies
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey, JSON, DateTime

# Local application imports
from Delivery_app_BK.models import db
from Delivery_app_BK.models.mixins.team_mixings.team_id import TeamScopedMixin


class DateRangeAccessRule(db.Model, TeamScopedMixin):
    __tablename__ = "date_range_access_rule"
    id = Column(Integer, primary_key=True)
    client_id = Column(String, index=True)
    from_date = Column(DateTime)
    to_date = Column(DateTime)
    target_model = Column(String)
    
    user_role_id = Column(
        Integer,
        ForeignKey("user_role.id"),
    )

    user_role = relationship(
        "UserRole",
        back_populates = "date_range_access_rule"
    )

    team = relationship(
        "Team",
        backref="date_range_access_rule",
        lazy=True
    )