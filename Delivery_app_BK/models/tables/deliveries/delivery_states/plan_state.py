# Third-party dependecies
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship

# Local application imports
from Delivery_app_BK.models import db
from Delivery_app_BK.models.mixins.team_mixings.team_id import TeamScopedMixin


"""
current static states are:
- Scheduled 
- In Progress
- Completed

"""


class PlanState (db.Model, TeamScopedMixin):
    __tablename__ = "plan_state"

    id = Column(Integer, primary_key=True)
    client_id = Column(String, index=True)
    name = Column(String, index=True)
    index = Column( Integer )
    color = Column(String)

    is_system = Column(Boolean, default=False, index=True)

    delivery_plan = relationship(
        "DeliveryPlan",
        back_populates = "state"
    )

    team = relationship(
        "Team",
        backref="plan_states",
        lazy=True
    )
