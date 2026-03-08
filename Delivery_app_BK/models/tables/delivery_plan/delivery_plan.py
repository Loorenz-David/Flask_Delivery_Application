# Third-party dependecies
from sqlalchemy.orm import validates
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Index, text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey

from datetime import datetime, timezone

# Local application imports
from Delivery_app_BK.models import db
from Delivery_app_BK.models.mixins.team_mixings.team_id import TeamScopedMixin
from Delivery_app_BK.models.utils import UTCDateTime



class DeliveryPlan(db.Model, TeamScopedMixin):
    __tablename__ = "delivery_plan"

    id = Column(Integer, primary_key=True)
    client_id = Column(String, index=True)

    label = Column(String, nullable=False, index=True)
    plan_type = Column(String, nullable=False, index=True)

  
    start_date = Column(UTCDateTime, index=True) 
    end_date = Column(UTCDateTime, index=True) 

    created_at = Column(
        UTCDateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    state_id = Column(
        Integer,
        ForeignKey("plan_state.id", ondelete="SET NULL"),
    )

    state = relationship(
        "DeliveryPlanState",
        back_populates = "delivery_plan",
        lazy= "selectin"
    )

    orders = relationship(
        "Order",
        back_populates="delivery_plan"
    )

    local_delivery = relationship(
        "LocalDeliveryPlan",
        back_populates = 'delivery_plan',
        passive_deletes=True,
        uselist=False
    )

    international_shipping = relationship(
        "InternationalShippingPlan",
        back_populates = 'delivery_plan',
        passive_deletes=True,
        uselist=False
    )

    store_pickup = relationship(
        "StorePickupPlan",
        back_populates = 'delivery_plan',
        passive_deletes=True,
        uselist=False
    )
    events = relationship(
        "DeliveryPlanEvent",
        back_populates="delivery_plan",
        lazy="selectin",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


    PLAN_TYPES = {
        "local_delivery",
        "international_shipping",
        "store_pickup",
    }

    @validates("plan_type")
    def validate_plan_type(self, key, value):
        if value not in self.PLAN_TYPES:
            raise ValueError(
                f"Invalid plan_type '{value}'. "
                f"Allowed values: {self.PLAN_TYPES}"
            )
        return value

    __table_args__ = (
        Index("ix_delivery_plan_created_at_id_desc", created_at.desc(), id.desc()),
    )
