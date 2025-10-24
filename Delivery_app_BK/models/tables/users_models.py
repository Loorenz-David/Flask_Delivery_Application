
# Thirs-party dependencies
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, JSON
from datetime import datetime,timezone

# Local application imports
from Delivery_app_BK.models import db
from Delivery_app_BK.models.managers.object_obtainer import ObjectObtainer
from Delivery_app_BK.models.mixins.teams_mixings import TeamScopedMixin
from Delivery_app_BK.models.managers.object_updator import ObjectUpdator


class Team(db.Model, ObjectObtainer, ObjectUpdator):
    __tablename__ = "Team"
    id = Column(Integer,primary_key=True)
    name = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=lambda:  datetime.now(timezone.utc))


class User(db.Model,  ObjectObtainer, ObjectUpdator, TeamScopedMixin):
    __tablename__ = "User"
    id = Column(Integer,primary_key=True)
    username = Column(String,nullable=False)
    email = Column(String,nullable=False)
    password = Column(String,nullable=False)

    role_id = Column(Integer, ForeignKey("UserRole.id"))


    team = relationship(
        "Team", 
        backref="members", 
        lazy=True
    )
    
    team = relationship(
        "UserRole", 
        backref="users", 
        lazy=True
    )


class UserRole(db.Model,  ObjectObtainer, ObjectUpdator, TeamScopedMixin):
    __tablename__ = "UserRoles"
    id = Column(Integer,primary_key=True)
    role = Column(String,nullable=False)
    permisions = Column(JSONB().with_variant(JSON, "sqlite")) 

    team = relationship(
        "Team", 
        backref="roles", 
        lazy=True
    )


class UserWarehouse(db.Model, ObjectObtainer, ObjectUpdator, TeamScopedMixin):
    __tablename__ = "UserWarehouses"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    location = Column(JSONB().with_variant(JSON, "sqlite"))  # dict: { street_address, postal_code, building_floor, coordinates }

    team = relationship(
        "Team", 
        backref="ware_houses", 
        lazy=True
    )

