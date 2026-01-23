# Third-party dependecies
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Index, text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, Text, String, Boolean, ForeignKey, DateTime

from datetime import datetime, timezone

# Local application imports
from Delivery_app_BK.models import db
from Delivery_app_BK.models.mixins.team_mixings.team_id import TeamScopedMixin



class OrderChat( db.Model, TeamScopedMixin):
    __tablename__ = "order_chat"

    id = Column( Integer, primary_key = True )
    client_id = Column(String, index=True)
    message = Column( Text )
    sender_name = Column( String )
    creation_date = Column( DateTime( timezone = True ), default=lambda: datetime.now(timezone.utc) )



    user_id = Column(
        Integer,
        ForeignKey("user.id", ondelete="SET NULL"),
        nullable= True
    )

    order_id = Column(
        Integer,
        ForeignKey("order.id", ondelete="CASCADE"),
        nullable= False
    )

    notification_reads = relationship(
        "NotificationRead",
        back_populates = "order_chat"
    )

    user = relationship(
        "User",
        back_populates = "order_chats",
    )

    order = relationship(
        "Order",
        back_populates = "order_chats",
    )
