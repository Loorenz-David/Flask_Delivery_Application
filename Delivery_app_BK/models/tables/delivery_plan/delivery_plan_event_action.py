from datetime import datetime, timezone

from sqlalchemy import Column, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from Delivery_app_BK.models import db
from Delivery_app_BK.models.mixins.team_mixings.team_id import TeamScopedMixin
from Delivery_app_BK.models.utils import UTCDateTime


class DeliveryPlanEventAction(db.Model, TeamScopedMixin):
    __tablename__ = "plan_event_action"

    STATUS_PENDING = "PENDING"
    STATUS_SUCCESS = "SUCCESS"
    STATUS_FAILED = "FAILED"

    id = Column(Integer, primary_key=True)
    
    action_name = Column(String, nullable=False)

    status = Column(String, nullable=False, index=True, default=STATUS_PENDING)
    attempts = Column(Integer, nullable=False, default=0)
    last_error = Column(Text, nullable=True)
    created_at = Column(UTCDateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        UTCDateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    event_id = Column(
        Integer,
        ForeignKey("plan_event.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    event = relationship("DeliveryPlanEvent", back_populates="actions", lazy="selectin")
    team = relationship("Team", backref="delivery_plan_event_actions", lazy=True)

    __table_args__ = (
        UniqueConstraint("event_id", "action_name", name="uq_plan_event_action_event_name"),
    )
