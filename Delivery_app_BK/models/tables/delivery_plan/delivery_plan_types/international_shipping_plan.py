# Third-party dependecies
from sqlalchemy.dialects.postgresql import JSONB

from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey

from datetime import datetime, timezone

# Local application imports
from Delivery_app_BK.models import db
from Delivery_app_BK.models.mixins.team_mixings.team_id import TeamScopedMixin




class InternationalShippingPlan(db.Model, TeamScopedMixin):
    __tablename__ = "international_shipping_plan"

    id = Column(Integer, primary_key=True)
    client_id = Column(String, index=True)
    
    carrier_name = Column(String)
    
    delivery_plan_id = Column(
        Integer,
        ForeignKey("delivery_plan.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )

    delivery_plan = relationship(
        "DeliveryPlan",
        back_populates = "international_shipping"
    )
