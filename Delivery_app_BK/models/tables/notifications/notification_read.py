# Third-party dependecies
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Index, text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, Text, String, Boolean, ForeignKey, DateTime

from datetime import datetime, timezone

# Local application imports
from Delivery_app_BK.models import db
from Delivery_app_BK.models.mixins.team_mixings.team_id import TeamScopedMixin


class NotificationRead( db.Model ):
    __tablename__ = "notification_read"
    id = Column( Integer, primary_key = True )
    client_id = Column(String, index=True, nullable=True )

    reader_name = Column( String )
    seen_at = Column(
        DateTime(timezone=True),
        default= lambda: datetime.now(timezone.utc),
        nullable = False
    )

    user_id = Column(
        Integer,
        ForeignKey("user.id", ondelete="SET NULL"),
        nullable= True
    )

    order_chat_id = Column(
        Integer,
        ForeignKey("order_chat.id", ondelete="CASCADE")
    )

    order_chat = relationship(
        "OrderChat",
        back_populates = "notification_reads"
    )
