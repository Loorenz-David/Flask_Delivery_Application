# Third-party dependecies
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Index, text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime

from datetime import datetime, timezone

# Local application import

from Delivery_app_BK.models import db
from Delivery_app_BK.models.mixins.team_mixings.team_id import TeamScopedMixin





class LocalDeliveryPlan(db.Model, TeamScopedMixin):
    __tablename__ = "local_delivery_plan"

    id = Column(Integer, primary_key=True)
    client_id = Column(String, index=True)

    
    actual_start_time = Column( DateTime )
    actual_end_time = Column( DateTime )
 
    is_optimized = Column(Boolean, default=False)

    driver_id = Column(
        Integer, 
        ForeignKey("user.id")
    )


    delivery_plan_id = Column(
        Integer,
        ForeignKey("delivery_plan.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )

    

    route_solutions = relationship(
        "RouteSolution",
        back_populates = "local_delivery_plan",
        cascade = 'all, delete-orphan'
    )

    driver = relationship(
        "User",
        back_populates="local_delivery_plans",
    )

    delivery_plan = relationship(
        "DeliveryPlan",
        back_populates = "local_delivery"
    )

    team = relationship(
        "Team",
        backref="local_delivery_plans",
        lazy=True
    )
