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


# add the ability to select the item intention, so if the item is for pick up or delivery 

class Item(db.Model, ObjectObtainer, ObjectUpdator, TeamScopedMixin):
    __tablename__ = "Item"

    id = Column(Integer, primary_key=True)
    article_number = Column(String, nullable=False, index=True)

    # Foreign key links
    item_type = Column(String)
    item_category = Column(String)
    item_state_id = Column(Integer, ForeignKey("ItemState.id"))
    item_position_id = Column(Integer, ForeignKey("ItemPosition.id"))
    order_id = Column(Integer, ForeignKey("Order.id", ondelete="CASCADE"))
    properties = Column(JSONB().with_variant(JSON, "sqlite")) # a list of dicts imprinted by the table ItemProperties


    # Access through relationship links

    item_state = relationship(
        "ItemState", 
        backref="items"
    )
    item_position = relationship(
        "ItemPosition", 
        backref="items"
    )
   

    team = relationship(
        "Team", 
        backref="items", 
        lazy=True
    )

    # link to an extrnal page...
    page_link = Column(String)

    item_valuation = Column(Integer)
    dimensions = Column(JSONB().with_variant(JSON, "sqlite")) #{ height: int, width: int, depth: int }

   
    weight = Column(Integer)
    item_position_record = Column(JSONB().with_variant(JSON, "sqlite")) # list of dicts [ { state:label, time: date-time } ]
    item_state_record = Column(JSONB().with_variant(JSON, "sqlite")) # list of dicts [ { state:label, time: date-time } ]

    

    def __repr__(self):
        return f"<Item {self.article_number}>"


class ItemType(db.Model, ObjectObtainer, ObjectUpdator, TeamScopedMixin):
    __tablename__ = "ItemType"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False, index=True)
    item_category_id = Column(Integer, ForeignKey("ItemCategory.id"))

    item_category = relationship(
        "ItemCategory",
        back_populates="item_types"
    )
    
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
    name = Column(String, unique=True, nullable=False, index=True)

    item_types = db.relationship(
        "ItemType",
        back_populates="item_category"
    )

    team = relationship(
        "Team", 
        backref="item_categories", 
        lazy=True
    )


class ItemProperty(db.Model, ObjectObtainer, ObjectUpdator, TeamScopedMixin):
    __tablename__ = "ItemProperty"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, index=True)
    field_type = Column(String, default="text") # 
    options = Column(JSONB().with_variant(JSON, "sqlite")) # used for when the field_type is select list of dicts
    required = Column(Boolean, nullable=False)
    
    item_types = db.relationship(
        "ItemType",
        secondary=type_property_association,
        back_populates="properties"
    )

    team = relationship(
        "Team", 
        backref="item_properties", 
        lazy=True
    )


# there is a constructue that builds default states upon team creation
# pending, in progress, ready, delivered.

class ItemState(db.Model,ObjectObtainer, ObjectUpdator, TeamScopedMixin):
    __tablename__ = "ItemState"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, index=True)
    color = Column(String, nullable=False) 
    default = Column(Boolean, nullable=False)
    description = Column(String, nullable=False)
    priority = Column(Integer)

    team = relationship(
        "Team", 
        backref="items_states", 
        lazy=True
    )


# there is a constructue that builds default positions upon team creation
# in-storage, in-packing, in-loading dock, in-truck, in-client

class ItemPosition(db.Model,ObjectObtainer, ObjectUpdator, TeamScopedMixin):
    __tablename__ = "ItemPosition"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, index=True)
    default = Column(Boolean, nullable=False)
    description = Column(String, nullable=False)

    team = relationship(
        "Team", 
        backref="item_positions", 
        lazy=True
    )
