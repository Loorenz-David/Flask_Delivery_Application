# Third-party dependecies

from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer,  ForeignKey, String, Boolean

from datetime import datetime, timezone

# Local application imports

from Delivery_app_BK.models import db
from Delivery_app_BK.models.mixins.team_mixings.team_id import TeamScopedMixin



class RouteSolutionStop(db.Model, TeamScopedMixin):
    __tablename__ = "route_optimization_stop"

    id = Column(Integer, primary_key=True)
    client_id = Column(String, index=True)

    route_optimization_id = Column(
        Integer,
        ForeignKey("route_optimization.id", ondelete="CASCADE"),
        nullable=False
    )

    order_id = Column(Integer, ForeignKey("order.id"))
    waiting_time = Column(String)
    
    in_range = Column(Boolean)
    # the order placement when being deliver
    stop_order = Column(Integer, nullable=True)

    expected_arrival_time = Column(String)
    actual_arrival_time = Column(String)

    route_optimization = relationship(
        "RouteSolution",
        back_populates="stops",

    )
