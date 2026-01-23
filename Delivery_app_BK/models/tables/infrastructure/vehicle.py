# Thirs-party dependencies
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, JSON, Float, ForeignKey, Boolean

# Local application imports
from Delivery_app_BK.models import db
from Delivery_app_BK.models.mixins.team_mixings.team_id import TeamScopedMixin


class Vehicle(db.Model, TeamScopedMixin):
    __tablename__ = "vehicle"

    id = Column(Integer, primary_key=True)
    client_id = Column(String, index=True)
    name = Column(String, nullable=False, index=True)
    icon = Column(String, nullable=True)

    travel_mode = Column(JSONB().with_variant(JSON, "sqlite"))

    cost_per_hour = Column(Float, default=0)
    cost_per_kilometer = Column(Float, default=0)

    travel_duration_limit = Column(Integer)
    route_distance_limit = Column(Integer)

    max_load = Column( Integer )
    min_load = Column( Integer )

    is_system = Column(Boolean, default=False, index=True)

    user_id = Column(
        Integer, 
        ForeignKey("user.id")
    )

    user = relationship(
        "User",
        back_populates="vehicle",
        lazy="selectin"
    )

    team = relationship(
        "Team",
        backref="vehicles",
        lazy=True,
    )
