# Third-party dependecies
from sqlalchemy import Column, Integer, String, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship

# Local application imports
from Delivery_app_BK.models import db
from Delivery_app_BK.models.mixins.team_mixings.team_id import TeamScopedMixin


class ItemState(db.Model, TeamScopedMixin):
    __tablename__ = "item_state"
    
    __table_args__ = (
        UniqueConstraint("team_id", "name", name="uq_itemstate_team_name"),
    )

    id = Column(Integer, primary_key=True)
    client_id = Column(String, index=True)
    name = Column(String, nullable=False, index=True)
    color = Column(String, nullable=False)
    default = Column(Boolean, default=False)
    description = Column(String)
    index = Column(Integer)

    is_system = Column(Boolean, default=False, index=True)

    items = relationship(
        "Item",
        back_populates="item_state",
        lazy=True
    )

    team = relationship(
        "Team",
        backref="items_states",
        lazy=True
    )
