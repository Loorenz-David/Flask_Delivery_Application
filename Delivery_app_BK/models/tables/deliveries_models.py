# Third-party dependecies
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Index, text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime,Text

from datetime import datetime, timezone

# Local application imports
from Delivery_app_BK.models import db
from Delivery_app_BK.models.managers.object_obtainer import ObjectObtainer
from Delivery_app_BK.models.managers.object_updator import ObjectUpdator
from Delivery_app_BK.models.mixins.teams_mixings import TeamScopedMixin






# model definition of an order
class Order(db.Model, ObjectObtainer, ObjectUpdator, TeamScopedMixin):
    __tablename__ = "Order"

    id = Column(Integer, primary_key=True)
    client_first_name = Column(String, nullable=False, index=True)
    client_last_name = Column(String, nullable=False, index=True)
    client_email = Column(String, nullable=False, index=True)
    client_primary_phone = Column(JSONB().with_variant(JSON, "sqlite")) #{prefix, number}
    client_secondary_phone = Column(JSONB().with_variant(JSON, "sqlite")) #{prefix, number}
    client_address = Column(JSONB().with_variant(JSON, "sqlite"))  # dict: {city, street_address, postal_code, building_floor, coordinates }
    client_language = Column(String,nullable=True)

    notes_chat = Column(JSONB().with_variant(JSON, "sqlite"))  # list [ {timestamp: y/m/d-h:m, message:str, sender:id, seenBy:[ids]} ]

    expected_arrival_time = Column(String)
    actual_arrival_time = Column(String)

    # upon_purchase_message = Column(Boolean, default=False)
    # expected_arrival_time_message = Column(Boolean, default=False)
    # upon_completion_message = Column(Boolean, default=False)

  
    
    marketing_messages = Column(Boolean, default=False)

    creation_date = Column(DateTime(timezone=True),default=lambda: datetime.now(timezone.utc))
    delivery_after = Column(String)
    delivery_before = Column(String)

    stop_time = Column(String)
    in_range = Column(Boolean)
    # the order placement when being deliver
    delivery_arrangement = Column(Integer,nullable=True)

    route_id = Column(Integer,ForeignKey("Route.id", ondelete="CASCADE"), nullable=True)

    delivery_items = db.relationship(
        "Item", 
        backref="order", 
        lazy=True,
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    team = relationship(
        "Team", 
        backref="orders", 
        lazy=True
    )
    
    __table_args__ = (
        # JSONB GIN indexes
        Index("ix_order_client_primary_phone_gin", client_primary_phone, postgresql_using="gin"),
        Index("ix_order_client_secondary_phone_gin", client_secondary_phone, postgresql_using="gin"),
        Index("ix_order_client_address_gin", client_address, postgresql_using="gin"),

        # Full-text index for partial string search
        Index(
            "ix_order_client_address_tsvector",
            text("to_tsvector('simple', client_address::text)"),
            postgresql_using="gin"
    ),
)
    
    
    

# model definition for a route
class Route(db.Model, ObjectObtainer, ObjectUpdator, TeamScopedMixin):
    __tablename__ = "Route"

    id = Column(Integer, primary_key=True)
    route_label = Column(String, nullable=False, index=True)
    delivery_date = Column(DateTime(timezone=True),default=lambda: datetime.now(timezone.utc), index=True)

    driver_id = Column(Integer,ForeignKey("User.id")) # Replace with ForeignKey(User.id) 
   

    expected_start_time = Column(String)
    expected_end_time = Column(String)
    actual_start_time = Column(String)
    actual_end_time = Column(String)

    set_start_time = Column(String)
    set_end_time = Column(String)

    start_location = Column(JSONB().with_variant(JSON, "sqlite"))
    end_location = Column(JSONB().with_variant(JSON, "sqlite"))
    arrival_time_range = Column(Integer)
    
    using_optimization_indx = Column(Integer)
    saved_optimizations = Column(JSONB().with_variant(JSON, "sqlite"))
    # Foreign keys
    state_id = Column(Integer,ForeignKey("RouteState.id"))
    
    is_optimized = Column(Boolean, default=False)

    # relationships
    delivery_orders = relationship(
        "Order",
        backref="routes",
        order_by="Order.delivery_arrangement",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    route_state = relationship(
        "RouteState",
        backref="routes",
    )

    team = relationship(
        "Team", 
        backref="routes", 
        lazy=True
    )

     # relationships
    driver = relationship(
        "User",
        backref="routes",
    )
   


class RouteState(db.Model,ObjectObtainer, ObjectUpdator, TeamScopedMixin):
    __tablename__ = "RouteState"

    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)

    team = relationship(
        "Team", 
        backref="route_states", 
        lazy=True
    )
