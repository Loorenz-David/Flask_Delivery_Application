
# Thirs-party dependencies
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, JSON, Float, Text
from datetime import datetime, timezone

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
    old_team_id = Column(Integer, nullable=True)
    old_role_id = Column(Integer, nullable=True)
    show_app_tutorial = Column(Boolean, default=True)
    last_online = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_location = Column(JSONB().with_variant(JSON, "sqlite")) # dict: {city, street_address, postal_code, building_floor, coordinates }
    
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


class TeamInvitesSend(db.Model, ObjectObtainer, ObjectUpdator, TeamScopedMixin):
    __tablename__ = "TeamInvitesSend"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("User.id"), nullable=True)
    username = Column(String, nullable=False)
    email = Column(String, nullable=False)
    role_id = Column(Integer, ForeignKey("UserRoles.id"), nullable=True)
    date = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    team = relationship("Team", lazy=True)
    user = relationship("User", lazy=True)
    role = relationship("UserRole", lazy=True)


class UserTeamInvitationsReceived(db.Model, ObjectObtainer, ObjectUpdator):
    __tablename__ = "UserTeamInvitationsReceived"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("User.id"), nullable=False)
    from_team_id = Column(Integer, ForeignKey("Team.id"), nullable=False)
    from_team_name = Column(String, nullable=False)
    role_id = Column(Integer, ForeignKey("UserRoles.id"), nullable=True)
    date = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", lazy=True)
    from_team = relationship("Team", lazy=True)
    role = relationship("UserRole", lazy=True)



class UserRole(db.Model,  ObjectObtainer, ObjectUpdator):
    __tablename__ = "UserRoles"
    id = Column(Integer,primary_key=True)
    role = Column(String,nullable=False, index=True)
    description = Column(String)
    rules = relationship(
        "RoleRules", 
        backref="user_role", 
        lazy=True
    )


class RoleRules(db.Model, ObjectObtainer, ObjectUpdator, TeamScopedMixin):
    __tablename__ = "RoleRules"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, index=True)
    description = Column(String)
    rule = Column(JSONB().with_variant(JSON, "sqlite"))  # dict: {date_query_range: {from: int, to: int} }
    role_id = Column(Integer, ForeignKey("UserRoles.id"), index=True)

    team = relationship(
        "Team", 
        backref="role_rules", 
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

class UserPrintLabelTemplates(db.Model, ObjectObtainer,ObjectUpdator,TeamScopedMixin):
    __tablename__ = "UserPrintLabelTemplates"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    template_string = Column(Text)
    template_target = Column(String) # Front end accepts "items" or "order"
    timestampt = Column(DateTime)

    team = relationship(
        "Team",
        backref="print_template_lable",
        lazy=True
    )
