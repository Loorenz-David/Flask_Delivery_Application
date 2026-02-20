# Third-party dependecies

from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer,  ForeignKey, String, Boolean, Enum
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime, timezone

# Local application imports

from Delivery_app_BK.models import db
from Delivery_app_BK.models.mixins.team_mixings.team_id import TeamScopedMixin
from Delivery_app_BK.models.utils import UTCDateTime



class RouteSolutionStop(db.Model, TeamScopedMixin):
    __tablename__ = "route_solution_stop"

    id = Column(Integer, primary_key=True)
    client_id = Column(String, index=True)

    route_solution_id = Column(
        Integer,
        ForeignKey("route_solution.id", ondelete="CASCADE"),
        nullable=False
    )

    order_id = Column(
        Integer, 
        ForeignKey("order.id", ondelete="CASCADE")
    )

    service_duration = Column(String) # sec
    
    

    in_range = Column(Boolean)
    # the order placement when being deliver
    stop_order = Column(Integer, nullable=True)
    reason_was_skipped = Column(String)

    has_constraint_violation = Column(Boolean, default=False)
    constraint_warnings = Column(JSONB, nullable=True)

    eta_status = Column(
        Enum("valid", "estimated", "stale", name="eta_status"),
        nullable=False,
        default="stale"
    )
    
    expected_arrival_time = Column(UTCDateTime)
    actual_arrival_time = Column(UTCDateTime)

    route_solution = relationship(
        "RouteSolution",
        back_populates="stops",

    )
