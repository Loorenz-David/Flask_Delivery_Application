# Third-party dependecies
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy import JSON
from datetime import datetime, timezone

# Local application imports
from Delivery_app_BK.models import db
from Delivery_app_BK.models.managers.object_obtainer import ObjectObtainer





# model definition of an order
class Order(db.Model, ObjectObtainer):
    __tablename__ = "Order"

    id = Column(Integer, primary_key=True)
    client_name = Column(String, nullable=False)
    client_phones = Column(String)
    client_address = Column(JSONB().with_variant(JSON, "sqlite"))  # dict: { street_address, postal_code, building_floor, coordinates }

    notes_chat = Column(JSONB().with_variant(JSON, "sqlite"))  # list

    expected_arrival_time = Column(String)
    actual_arrival_time = Column(String)

    upon_purchase_message = Column(Boolean, default=False)
    expected_arrival_time_message = Column(Boolean, default=False)
    upon_completion_message = Column(Boolean, default=False)
    marketing_messages = Column(Boolean, default=False)

    creation_date = Column(DateTime(timezone=True),default=lambda: datetime.now(timezone.utc))
    delivery_after = Column(String)
    delivery_before = Column(String)

    # the order placement when being deliver
    delivery_arrangement = Column(Integer,nullable=True)

    route_id = Column(Integer,ForeignKey("Route.id"), nullable=True)

    delivery_items = db.relationship(
        "Item", 
        backref="order", 
        lazy=True
    )
    
    
    def __repr__(self):
        return f"<Order {self.client_name}>"
    

# model definition for a route
class Route(db.Model, ObjectObtainer):
    __tablename__ = "Route"

    id = Column(Integer, primary_key=True)
    route_label = Column(String, nullable=False)
    delivery_date = Column(DateTime(timezone=True),default=lambda: datetime.now(timezone.utc))

    assigned_driver = Column(String)  # Replace with ForeignKey(User.id) if you have a User model

    expected_start_time = Column(String)
    expected_end_time = Column(String)
    actual_start_time = Column(String)
    actual_end_time = Column(String)

    start_location = Column(JSONB().with_variant(JSON, "sqlite"))
    end_location = Column(JSONB().with_variant(JSON, "sqlite"))

    state = Column(String)
    is_optimized = Column(Boolean, default=False)

    delivery_orders = relationship(
        "Order",
        backref="route",
        order_by="Order.delivery_arrangement",
        cascade="all, delete-orphan"
    )
   

    def __repr__(self):
        return f"<Route {self.label}>"