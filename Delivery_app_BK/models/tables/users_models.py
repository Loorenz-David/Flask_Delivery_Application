
# Thirs-party dependencies
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey


# Local application imports
from Delivery_app_BK.models import db
from Delivery_app_BK.models.managers.object_obtainer import ObjectObtainer

class User(db.Model, ObjectObtainer):
    __tablename__ = "User"
    id = Column(Integer,primary_key=True)
    username = Column(String,nullable=False)
    email = Column(String,nullable=False)
    password = Column(String,nullable=False)