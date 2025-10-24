# Third-party dependecies
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime,Text
from sqlalchemy import JSON
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
    client_name = Column(String, nullable=False)
    client_phones = Column(String)
    client_address = Column(JSONB().with_variant(JSON, "sqlite"))  # dict: { street_address, postal_code, building_floor, coordinates }
    client_language = Column(String,nullable=True)

    notes_chat = Column(JSONB().with_variant(JSON, "sqlite"))  # list

    expected_arrival_time = Column(String)
    actual_arrival_time = Column(String)

    # upon_purchase_message = Column(Boolean, default=False)
    # expected_arrival_time_message = Column(Boolean, default=False)
    # upon_completion_message = Column(Boolean, default=False)
    
    marketing_messages = Column(Boolean, default=False)

    creation_date = Column(DateTime(timezone=True),default=lambda: datetime.now(timezone.utc))
    delivery_after = Column(String)
    delivery_before = Column(String)

    # the order placement when being deliver
    delivery_arrangement = Column(Integer,nullable=True)
    delivery_polyline = Column(Text)

    route_id = Column(Integer,ForeignKey("Route.id"), nullable=True)

    delivery_items = db.relationship(
        "Item", 
        backref="orders", 
        lazy=True
    )

    team = relationship(
        "Team", 
        backref="orders", 
        lazy=True
    )
    
    
    
    

# model definition for a route
class Route(db.Model, ObjectObtainer, ObjectUpdator, TeamScopedMixin):
    __tablename__ = "Route"

    id = Column(Integer, primary_key=True)
    route_label = Column(String, nullable=False)
    delivery_date = Column(DateTime(timezone=True),default=lambda: datetime.now(timezone.utc))

    driver_id = Column(Integer,ForeignKey("User.id")) # Replace with ForeignKey(User.id) 


    expected_start_time = Column(String)
    expected_end_time = Column(String)
    actual_start_time = Column(String)
    actual_end_time = Column(String)

    start_location = Column(JSONB().with_variant(JSON, "sqlite"))
    end_location = Column(JSONB().with_variant(JSON, "sqlite"))

    # Foreign keys
    state_id = Column(Integer,ForeignKey("RouteState.id"))
    
    is_optimized = Column(Boolean, default=False)

    # relationships
    delivery_orders = relationship(
        "Order",
        backref="routes",
        order_by="Order.delivery_arrangement",
        cascade="all, delete-orphan"
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
    name = Column(String)

    team = relationship(
        "Team", 
        backref="route_states", 
        lazy=True
    )
