# Thirs-party dependencies
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Column, Integer, String, DateTime, JSON
from datetime import datetime, timezone

# Local application imports
from Delivery_app_BK.models import db


class Team(db.Model):
    __tablename__ = "team"
    id = Column(Integer, primary_key=True)
    client_id = Column(String, index=True)
    name = Column(String, nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # a dictionary use by the front end to notify the user that there is configuration missing
    missing_to_configure = Column(JSONB().with_variant(JSON, "sqlite"))

    # a dictionary made to check if the user has a valid subscription to use some properties
    # last thing to develop
    subscription = Column(JSONB().with_variant(JSON, "sqlite"))
