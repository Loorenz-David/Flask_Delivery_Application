
# Thirs-party dependencies
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, JSON, Float
from datetime import datetime,timezone

# Local application imports
from Delivery_app_BK.models import db
from Delivery_app_BK.models.managers.object_obtainer import ObjectObtainer
from Delivery_app_BK.models.mixins.teams_mixings import TeamScopedMixin
from Delivery_app_BK.models.managers.object_updator import ObjectUpdator
from werkzeug.security import generate_password_hash, check_password_hash

class Team(db.Model, ObjectObtainer, ObjectUpdator):
    __tablename__ = "Team"
    id = Column(Integer,primary_key=True)
    name = Column(String, unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=lambda:  datetime.now(timezone.utc))

    # a dictionary use by the front end to notify the user that there is configuration missing
    missing_to_configure = Column(JSONB().with_variant(JSON, "sqlite")) 

    # a dictionary made to check if the user has a valid subscription to use some properties
    # last thing to develop
    subscription = Column(JSONB().with_variant(JSON, "sqlite"))

class User(db.Model,  ObjectObtainer, ObjectUpdator, TeamScopedMixin):
    __tablename__ = "User"
    id = Column(Integer,primary_key=True)
    username = Column(String,nullable=False, index=True)
    email = Column(String,nullable=False, unique=True, index=True)
    password = Column(String,nullable=False)
    phone_number = Column(JSONB().with_variant(JSON, "sqlite"))
    role_id = Column(Integer, ForeignKey("UserRoles.id"))
    profile_picture = Column(JSONB().with_variant(JSON, "sqlite"))

    team = relationship(
        "Team", 
        backref="members", 
        lazy=True
    )
    
    role = relationship(
        "UserRole", 
        backref="users", 
        lazy=True
    )

    def hash_password(self,password):
        return generate_password_hash(password)
    
    def check_password(self,password):
        return check_password_hash(self.password,password)


class UserRole(db.Model,  ObjectObtainer, ObjectUpdator, TeamScopedMixin):
    __tablename__ = "UserRoles"
    id = Column(Integer,primary_key=True)
    role = Column(String,nullable=False, index=True)
    permisions = Column(JSONB().with_variant(JSON, "sqlite")) 

    team = relationship(
        "Team", 
        backref="roles", 
        lazy=True
    )


class UserWarehouse(db.Model, ObjectObtainer, ObjectUpdator, TeamScopedMixin):
    __tablename__ = "UserWarehouses"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, index=True)

    location = Column(JSONB().with_variant(JSON, "sqlite"))  # dict: {city, street_address, postal_code, building_floor, coordinates }

    team = relationship(
        "Team", 
        backref="ware_houses", 
        lazy=True
    )


class UserVehicle(db.Model, ObjectObtainer, ObjectUpdator, TeamScopedMixin):
    __tablename__ = "UserVehicles"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, index=True)
    icon = Column(String, nullable=True)
    travel_mode = Column(JSONB().with_variant(JSON, "sqlite"))
    cost_per_hour = Column(Float, default=0)
    cost_per_kilometer = Column(Float, default=0)
    travel_duration_limit = Column(Integer)
    route_distance_limit = Column(Integer)

    team = relationship(
        "Team",
        backref="vehicles",
        lazy=True,
    )
