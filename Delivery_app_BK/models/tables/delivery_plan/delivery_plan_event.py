from datetime import datetime, timezone

from sqlalchemy import Column, ForeignKey, Integer, String, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from Delivery_app_BK.models import db
from Delivery_app_BK.models.mixins.team_mixings.team_id import TeamScopedMixin
from Delivery_app_BK.models.utils import UTCDateTime


class DeliveryPlanEvent(db.Model, TeamScopedMixin):
    __tablename__ = "plan_event"

    id = Column(Integer, primary_key=True)
 
    event_name = Column(String, nullable=False, index=True)
    payload = Column(JSONB().with_variant(JSON, "sqlite"), nullable=False, default=dict)
    occurred_at = Column(UTCDateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

    delivery_plan_id = Column(
        Integer,
        ForeignKey("delivery_plan.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    actor_id = Column(
        Integer,
        ForeignKey("user.id", ondelete="SET NULL"),
        nullable=True,
    )

    delivery_plan = relationship("DeliveryPlan", back_populates="events", lazy="selectin")
    actions = relationship(
        "DeliveryPlanEventAction",
        back_populates="event",
        lazy="selectin",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    actor = relationship("User", lazy="selectin")
    team = relationship("Team", backref="delivery_plan_events", lazy=True)
