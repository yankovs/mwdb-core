from marshmallow import Schema, fields

from .object import ObjectListItemResponseSchema
from .ioc import IOCListItemResponseSchema
from .tag import TagItemResponseSchema


class RelatedObjectItemSchema(Schema):
    """
    Dynamic schema that selects appropriate serialization based on object type.
    For IOCs, includes the value field; for other objects, uses standard fields.
    """
    id = fields.Str(attribute="dhash", required=True, allow_none=False)
    type = fields.Str(required=True, allow_none=False)
    tags = fields.Nested(
        TagItemResponseSchema, many=True, required=True, allow_none=False
    )
    upload_time = fields.DateTime(required=True, allow_none=False)
    value = fields.Str(required=False, allow_none=True, dump_default=None)


class RelationsResponseSchema(Schema):
    parents = fields.Nested(RelatedObjectItemSchema, many=True)
    children = fields.Nested(RelatedObjectItemSchema, many=True)
