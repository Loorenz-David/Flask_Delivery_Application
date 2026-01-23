# Third-party dependecies

from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer,  ForeignKey, String, Float, DateTime, Boolean, JSON
from sqlalchemy.dialects.postgresql import JSONB

from datetime import datetime, timezone

# Local application imports
from Delivery_app_BK.models.mixins.validation_mixins.address_validation import AddressJSONValidationMixin

from Delivery_app_BK.models import db
from Delivery_app_BK.models.mixins.team_mixings.team_id import TeamScopedMixin



class RouteSolution(db.Model, TeamScopedMixin, AddressJSONValidationMixin):
    __tablename__ = "route_optimization"


    id = Column(Integer, primary_key=True)
    client_id = Column(String, index=True)

    version = Column(Integer, default=1)
    algorithm = Column(String)
    score = Column(Float)  # distance, time, cost score, etc.

    expected_start_time = Column( DateTime )
    expected_end_time = Column( DateTime )

    start_location = Column(JSONB().with_variant(JSON, "sqlite"))
    end_location = Column(JSONB().with_variant(JSON, "sqlite"))
    
    set_start_time = Column( DateTime )
    set_end_time = Column( DateTime )

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    is_selected = Column(Boolean, default=False)

    driver_id = Column(
        Integer, 
        ForeignKey("user.id")
    )

    delivery_plan_id = Column(
        Integer,
        ForeignKey("local_delivery_plan.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    stops = relationship(
        "RouteSolutionStop",
        back_populates = "route_optimization",
        cascade = 'all, delete-orphan'
    )

    driver = relationship(
        "User",
        back_populates="route_solutions",
    )

    local_delivery_plan = relationship(
        "LocalDeliveryPlan",
        back_populates="route_solutions",
    )
