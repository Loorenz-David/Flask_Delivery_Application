# Third-party dependecies
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Column, Integer, String, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from Delivery_app_BK.models import db

# Local application imports

from Delivery_app_BK.models.managers.object_obtainer import ObjectObtainer
from Delivery_app_BK.models.managers.object_updator import ObjectUpdator
from Delivery_app_BK.models.mixins.teams_mixings import TeamScopedMixin

type_property_association = db.Table(
    "type_property_association",
    Column("type_id", Integer, ForeignKey("ItemType.id"), primary_key=True),
    Column("property_id", Integer, ForeignKey("ItemProperty.id"), primary_key=True)
)

item_property_association = db.Table(
    "item_property_association",
    Column("item_id",Integer,ForeignKey("Item.id"),primary_key=True),
    Column("property_id",Integer,ForeignKey("ItemProperty.id"),primary_key=True)
)

# add the ability to select the item intention, so if the item is for pick up or delivery 

class Item(db.Model, ObjectObtainer, ObjectUpdator, TeamScopedMixin):
    __tablename__ = "Item"

    id = Column(Integer, primary_key=True)
    article_number = Column(String, nullable=False)

    # Foreign key links
    item_type_id = Column(Integer, ForeignKey("ItemType.id"))
    item_category_id = Column(Integer, ForeignKey("ItemCategory.id"))
    item_state_id = Column(Integer, ForeignKey("ItemState.id"))
    item_position_id = Column(Integer, ForeignKey("ItemPosition.id"))
    order_id = Column(Integer, ForeignKey("Order.id"))

    in_range = Column(Boolean)

    # Access through relationship links
    item_type = relationship(
        "ItemType", 
        backref="items"
    )
    item_category = relationship(
        "ItemCategory", 
        backref="items"
    )
    item_state = relationship(
        "ItemState", 
        backref="items"
    )
    item_position = relationship(
        "ItemPosition", 
        backref="items"
    )
    properties = db.relationship(
        "ItemProperty",
        secondary=item_property_association,
        back_populates="items"
    )

    team = relationship(
        "Team", 
        backref="items", 
        lazy=True
    )

    # link to an extrnal page...
    page_link = Column(String)

    item_valuation = Column(Integer)
    dimensions = Column(JSONB().with_variant(JSON, "sqlite"))

   
    weight = Column(Integer)
    item_position_record = Column(JSONB().with_variant(JSON, "sqlite")) # list of dicts [ { state:label, time: date-time } ]
    item_state_record = Column(JSONB().with_variant(JSON, "sqlite")) # list of dicts [ { state:label, time: date-time } ]

    

    def __repr__(self):
        return f"<Item {self.article_number}>"


class ItemType(db.Model, ObjectObtainer, ObjectUpdator, TeamScopedMixin):
    __tablename__ = "ItemType"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    properties = db.relationship(
        "ItemProperty",
        secondary=type_property_association,
        back_populates="item_types"
    )

    team = relationship(
        "Team", 
        backref="item_types", 
        lazy=True
    )


class ItemCategory(db.Model, ObjectObtainer, ObjectUpdator, TeamScopedMixin):
    __tablename__ = "ItemCategory"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    team = relationship(
        "Team", 
        backref="item_categories", 
        lazy=True
    )


class ItemProperty(db.Model, ObjectObtainer, ObjectUpdator, TeamScopedMixin):
    __tablename__ = "ItemProperty"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    value = Column(String, nullable=False)
    field_type = Column(String, default="text")
    options = Column(JSONB().with_variant(JSON, "sqlite"))
    

    item_types = db.relationship(
        "ItemType",
        secondary=type_property_association,
        back_populates="properties"
    )

    items = db.relationship(
        "Item",
        secondary=item_property_association,
        back_populates="properties"
    )

    team = relationship(
        "Team", 
        backref="item_properties", 
        lazy=True
    )



class ItemState(db.Model,ObjectObtainer, ObjectUpdator, TeamScopedMixin):
    __tablename__ = "ItemState"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    team = relationship(
        "Team", 
        backref="items_states", 
        lazy=True
    )


class ItemPosition(db.Model,ObjectObtainer, ObjectUpdator, TeamScopedMixin):
    __tablename__ = "ItemPosition"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    team = relationship(
        "Team", 
        backref="item_positions", 
        lazy=True
    )
