# Third-party dependecies

from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer,  ForeignKey, String, Float, Boolean, JSON, Enum
from sqlalchemy.dialects.postgresql import JSONB

from datetime import datetime, timezone

# Local application imports
from Delivery_app_BK.models.mixins.validation_mixins.address_validation import AddressJSONValidationMixin

from Delivery_app_BK.models import db
from Delivery_app_BK.models.mixins.team_mixings.team_id import TeamScopedMixin
from Delivery_app_BK.models.utils import UTCDateTime
from Delivery_app_BK.route_optimization.constants.is_optimized import (
    IS_OPTIMIZED_NOT_OPTIMIZED,
    IS_OPTIMIZED_VALUES,
)
from Delivery_app_BK.route_optimization.constants.route_end_strategy import ROUND_TRIP, CUSTOM_END_ADDRESS,LAST_STOP



class RouteSolution(db.Model, TeamScopedMixin, AddressJSONValidationMixin):
    __tablename__ = "route_solution"


    id = Column(Integer, primary_key=True)
    client_id = Column(String, index=True)

    label = Column(String)
    version = Column(Integer, default=1)
    algorithm = Column(String)
    score = Column(Float)  # distance, time, cost score, etc.

    total_distance_meters = Column(Integer)
    total_travel_time_seconds = Column(Integer)
    


    # expected times are what the optimization fill in 
    expected_start_time = Column(UTCDateTime)
    expected_end_time = Column(UTCDateTime)

    has_route_warnings = Column(Boolean, default=False)
    route_warnings = Column(JSONB, nullable=True)

    start_location = Column(JSONB().with_variant(JSON, "sqlite"))
    end_location = Column(JSONB().with_variant(JSON, "sqlite"))
    
    route_end_strategy = Column(
        Enum(
            ROUND_TRIP,
            CUSTOM_END_ADDRESS,
            LAST_STOP,
            name="route_end_strategy"
        ),
        nullable=False,
        default=ROUND_TRIP
    )
    
    # set times are what the user inputed
    # maybe this should be string times also...
    # and they infer a repeated allowed time accross the delivery plan date range
    set_start_time = Column( String )
    set_end_time = Column( String )

    created_at = Column(
        UTCDateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    is_selected = Column(Boolean, default=False)

    """
    must add a schema validator for is_optimize values:
    "optimize","partial optimize", "not optimize"
    """
    is_optimized = Column(
                            Enum(*IS_OPTIMIZED_VALUES, name="is_optimized"),
                            nullable=False,
                            default=IS_OPTIMIZED_NOT_OPTIMIZED
    )

    stop_count = Column(Integer, default=0)

    driver_id = Column(
        Integer, 
        ForeignKey("user.id")
    )

    local_delivery_plan_id = Column(
        Integer,
        ForeignKey("local_delivery_plan.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    start_leg_polyline = Column(JSONB, nullable=True)
    end_leg_polyline = Column(JSONB, nullable=True)
    stops = relationship(
        "RouteSolutionStop",
        back_populates = "route_solution",
        cascade = 'all, delete-orphan',
        order_by="RouteSolutionStop.stop_order"
    )


    driver = relationship(
        "User",
        back_populates="route_solutions",
    )

    local_delivery_plan = relationship(
        "LocalDeliveryPlan",
        back_populates="route_solutions",
    )
