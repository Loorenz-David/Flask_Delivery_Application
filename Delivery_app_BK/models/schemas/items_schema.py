# Third-part dependencies
from marshmallow import Schema, fields


class ItemCreation(Schema):
    article_number = fields.String(required=True)
    item_type_id = fields.Integer(required=True)
    item_category_id = fields.Integer(required=True)
    property_id = fields.Integer(required=True)
    sold_price = fields.Integer(required=False)
    item_dimensions = fields.Dict(required=False)
    weight = fields.Integer(required=False)
    location = fields.String(required=True)
    location_record = fields.Dict(required=False)
    state = fields.String(required=True)
    state_record = fields.Dict(required=False)
    order_id = fields.Integer(required=True)

class ItemTypeCreation(Schema):
    name = fields.String(required=True)
    properties = fields.List(fields.Integer(), required=False)


class ItemCategoryCreation(Schema):
    name = fields.String(required=True)


class ItemPropertyCreation(Schema):
    name = fields.String(required=True)
    value = fields.String(required=True)
    field_type = fields.String(required=False)
    options = fields.Dict(required=False)