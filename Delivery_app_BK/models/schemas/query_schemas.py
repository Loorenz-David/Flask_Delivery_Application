# Marshmallow imports for validation
from marshmallow import Schema, fields, ValidationError

# Schema for validating query_item payload
class QuerySchema(Schema):
    queryfilters = fields.Dict(required=True)
    requested_fields = fields.List(fields.String(), required=False)
