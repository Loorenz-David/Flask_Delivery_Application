# Thirs-party dependencies
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, JSON

# Local application imports
from Delivery_app_BK.models import db
from Delivery_app_BK.models.mixins.team_mixings.team_id import TeamScopedMixin
from Delivery_app_BK.models.mixins.validation_mixins.address_validation import (
    AddressJSONValidationMixin,
)


class Warehouse(db.Model, TeamScopedMixin, AddressJSONValidationMixin):
    __tablename__ = "warehouse"

    __address_fields__ = ( "location" )

    id = Column(Integer, primary_key=True)
    client_id = Column(String, index=True)
    name = Column(String, nullable=False, index=True)

    property_location = Column(JSONB().with_variant(JSON, "sqlite"))  # dict: {city, street_address, postal_code, building_floor, coordinates }


    

    team = relationship(
        "Team",
        backref="ware_houses",
        lazy=True
    )
