"""
Schema for IOC (Indicator of Compromise) API endpoints
"""

from marshmallow import Schema, ValidationError, fields, validates

from .object import (
    ObjectCreateRequestSchemaBase,
    ObjectItemResponseSchema,
    ObjectLegacyMetakeysMixin,
    ObjectListItemResponseSchema,
    ObjectListResponseSchemaBase,
)
from .utils import UTCDateTime


class IOCCreateSpecSchema(Schema):
    """Schema for IOC-specific creation parameters"""
    
    ioc_type = fields.Str(
        required=True,
        allow_none=False,
        description="Type of IOC (e.g., 'ip', 'url', 'domain', 'md5', 'sha1', 'sha256')"
    )
    value = fields.Str(
        required=True,
        allow_none=False,
        description="The IOC value (e.g., IP address, URL, domain name)"
    )
    severity = fields.Str(
        required=False,
        missing="medium",
        allow_none=False,
        description="Severity level (low, medium, high, critical)"
    )
    source = fields.Str(
        required=False,
        missing=None,
        allow_none=True,
        description="Source where this IOC was discovered"
    )
    is_active = fields.Bool(
        required=False,
        missing=True,
        allow_none=False,
        description="Whether this IOC is currently active/relevant"
    )
    
    @validates("ioc_type")
    def validate_ioc_type(self, value):
        """Validate IOC type"""
        from mwdb.core.ioc_consts import IOCType
        
        valid_types = [t.value for t in IOCType]
        if value not in valid_types:
            raise ValidationError(
                f"Invalid IOC type '{value}'. Must be one of: {', '.join(valid_types)}"
            )
    
    @validates("severity")
    def validate_severity(self, value):
        """Validate severity level"""
        valid_severities = {"low", "medium", "high", "critical"}
        if value not in valid_severities:
            raise ValidationError(
                f"Invalid severity '{value}'. Must be one of: {', '.join(valid_severities)}"
            )


class IOCCreateRequestSchema(ObjectCreateRequestSchemaBase, IOCCreateSpecSchema):
    """Schema for creating a new IOC"""
    pass


class IOCLegacyCreateRequestSchema(IOCCreateRequestSchema, ObjectLegacyMetakeysMixin):
    """Schema for legacy IOC creation (supporting metakeys)"""
    pass


class IOCListItemResponseSchema(ObjectListItemResponseSchema):
    """Schema for IOC item in list responses"""
    
    ioc_type = fields.Str(required=True, allow_none=False)
    value = fields.Str(required=True, allow_none=False)
    severity = fields.Str(required=True, allow_none=False)
    is_active = fields.Bool(required=True, allow_none=False)


class IOCListResponseSchema(ObjectListResponseSchemaBase, IOCListItemResponseSchema):
    """Schema for IOC list response"""
    
    __envelope_key__ = "iocs"


class IOCItemResponseSchema(ObjectItemResponseSchema):
    """Schema for full IOC response"""
    
    ioc_type = fields.Str(required=True, allow_none=False)
    value = fields.Str(required=True, allow_none=False)
    severity = fields.Str(required=True, allow_none=False)
    source = fields.Str(required=True, allow_none=True)
    last_seen = UTCDateTime(required=True, allow_none=True)
    is_active = fields.Bool(required=True, allow_none=False)


class IOCUpdateRequestSchema(Schema):
    """Schema for updating IOC properties"""
    
    severity = fields.Str(
        required=False,
        allow_none=False,
        description="Severity level"
    )
    is_active = fields.Bool(
        required=False,
        allow_none=False,
        description="Whether this IOC is active"
    )
    source = fields.Str(
        required=False,
        allow_none=True,
        description="Source of the IOC"
    )
    
    @validates("severity")
    def validate_severity(self, value):
        """Validate severity level if provided"""
        if value:
            valid_severities = {"low", "medium", "high", "critical"}
            if value not in valid_severities:
                raise ValidationError(
                    f"Invalid severity '{value}'. Must be one of: {', '.join(valid_severities)}"
                )


class IOCStatsResponseSchema(Schema):
    """Schema for IOC statistics"""
    
    total = fields.Int(required=True)
    by_type = fields.Dict(
        keys=fields.Str(),
        values=fields.Int(),
        required=True,
        description="Count of IOCs by type"
    )
    by_severity = fields.Dict(
        keys=fields.Str(),
        values=fields.Int(),
        required=True,
        description="Count of IOCs by severity"
    )
    active = fields.Int(required=True)
