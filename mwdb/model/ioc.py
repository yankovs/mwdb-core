"""
IOC (Indicator of Compromise) database model
"""

import datetime
import hashlib
from typing import Any, Dict, Optional

from sqlalchemy import TypeDecorator
from sqlalchemy.ext.hybrid import hybrid_property

from mwdb.core.ioc_consts import IOCType, IOCSeverity, validate_ioc, validate_severity

from . import db
from .object import Object


# Custom SQLAlchemy types for enum enforcement
class IOCTypeField(TypeDecorator):
    """
    SQLAlchemy type that enforces IOCType enum values at the database level.
    Stores the enum value as a string but validates on both Python and DB sides.
    """
    impl = db.String(32)
    cache_ok = True
    
    def process_bind_param(self, value, dialect):
        """Convert Python value to database value"""
        if value is None:
            return None
        if isinstance(value, IOCType):
            return value.value
        if isinstance(value, str):
            # Validate the string is a valid IOC type
            try:
                IOCType(value)
                return value
            except ValueError:
                valid = [t.value for t in IOCType]
                raise ValueError(
                    f"Invalid IOC type: {value}. Must be one of: {', '.join(valid)}"
                )
        raise TypeError(f"Expected IOCType enum or string, got {type(value)}")
    
    def process_result_value(self, value, dialect):
        """Convert database value to Python value"""
        if value is None:
            return None
        return IOCType(value)


class IOCSeverityField(TypeDecorator):
    """
    SQLAlchemy type that enforces IOCSeverity enum values at the database level.
    Stores the enum value as a string but validates on both Python and DB sides.
    """
    impl = db.String(16)
    cache_ok = True
    
    def process_bind_param(self, value, dialect):
        """Convert Python value to database value"""
        if value is None:
            return IOCSeverity.MEDIUM.value
        if isinstance(value, IOCSeverity):
            return value.value
        if isinstance(value, str):
            # Validate the string is a valid severity
            try:
                IOCSeverity(value)
                return value
            except ValueError:
                valid = [s.value for s in IOCSeverity]
                raise ValueError(
                    f"Invalid severity: {value}. Must be one of: {', '.join(valid)}"
                )
        raise TypeError(f"Expected IOCSeverity enum or string, got {type(value)}")
    
    def process_result_value(self, value, dialect):
        """Convert database value to Python value"""
        if value is None:
            return IOCSeverity.MEDIUM
        return IOCSeverity(value)


# Relationship table for IOC-Object connections
ioc_object = db.Table(
    "ioc_object",
    db.Column(
        "ioc_id", db.Integer, db.ForeignKey("object.id"), index=True, nullable=False
    ),
    db.Column(
        "object_id", db.Integer, db.ForeignKey("object.id"), index=True, nullable=False
    ),
    db.Column("creation_time", db.DateTime, default=datetime.datetime.utcnow),
    db.Index("ix_ioc_object_ioc_object", "ioc_id", "object_id", unique=True),
)


class IOC(Object):
    """
    IOC (Indicator of Compromise) object representing various types of threat indicators
    such as IP addresses, URLs, domains, hashes, etc.
    
    Each IOC is stored with its type and value, allowing for flexible storage of various
    threat indicators. IOCs can be related to files, malware configurations, or other objects
    through the ioc_object relationship table.
    """
    
    ioc_type = db.Column(
        IOCTypeField,
        index=True,
        nullable=True,
        doc="Type of IOC - enforced as IOCType enum value"
    )
    
    value = db.Column(
        db.String(1024, collation="C"),
        index=True,
        nullable=True,
        doc="The IOC value (e.g., IP address, URL, domain name)"
    )
    
    severity = db.Column(
        IOCSeverityField,
        default=IOCSeverity.MEDIUM,
        nullable=True,
        doc="Severity level - enforced as IOCSeverity enum value"
    )
    
    source = db.Column(
        db.String(256),
        nullable=True,
        doc="Source where this IOC was discovered (e.g., 'feed_name', 'external_source')"
    )
    
    is_active = db.Column(
        db.Boolean,
        default=True,
        nullable=True,
        index=True,
        doc="Whether this IOC is currently active/relevant"
    )

    __mapper_args__ = {
        "polymorphic_identity": "ioc",
    }
    
    # Relationships to other objects (e.g., files, configs) that this IOC is connected to
    related_objects = db.relationship(
        "Object",
        secondary=ioc_object,
        primaryjoin=(Object.id == ioc_object.c.ioc_id),
        secondaryjoin=(Object.id == ioc_object.c.object_id),
        order_by=ioc_object.c.creation_time.desc(),
        backref="ioc_indicators",
        lazy="selectin",
        doc="Other objects (files, configs, etc.) this IOC is connected to"
    )

    def __init__(
        self,
        ioc_type,
        value: str,
        severity=None,
        source: Optional[str] = None,
        is_active: bool = True,
        **kwargs
    ):
        """
        Initialize an IOC object.
        
        Args:
            ioc_type: Type of IOC (IOCType enum or string)
            value: The IOC value (string)
            severity: Severity level (IOCSeverity enum, string, or None for default)
            source: Source of the IOC (string, optional)
            is_active: Whether IOC is active (bool)
            
        Raises:
            TypeError: If ioc_type is not IOCType enum or string
            ValueError: If ioc_type, severity, or value is invalid
        """
        # Convert and validate IOC type
        if isinstance(ioc_type, str):
            try:
                ioc_type_enum = IOCType(ioc_type)
            except ValueError:
                valid = [t.value for t in IOCType]
                raise ValueError(
                    f"Invalid IOC type: {ioc_type}. Must be one of: {', '.join(valid)}"
                )
        elif isinstance(ioc_type, IOCType):
            ioc_type_enum = ioc_type
        else:
            raise TypeError(
                f"ioc_type must be IOCType enum or string, got {type(ioc_type)}"
            )
        
        # Validate IOC value
        value = value.strip() if value else ""
        if not value:
            raise ValueError("IOC value cannot be empty")
        
        if not validate_ioc(ioc_type_enum, value):
            raise ValueError(
                f"Invalid value for IOC type '{ioc_type_enum.value}': {value}"
            )
        
        # Convert and validate severity - None becomes MEDIUM through TypeDecorator
        if severity is None:
            severity_enum = IOCSeverity.MEDIUM
        elif isinstance(severity, str):
            severity_enum = validate_severity(severity)
        elif isinstance(severity, IOCSeverity):
            severity_enum = severity
        else:
            raise TypeError(f"severity must be IOCSeverity enum, string, or None, got {type(severity)}")
        
        # Create unique dhash from IOC type and value
        dhash_input = f"{ioc_type_enum.value}:{value}".encode("utf-8")
        dhash = hashlib.sha256(dhash_input).hexdigest()
        
        super().__init__(
            dhash=dhash,
            ioc_type=ioc_type_enum,  # TypeDecorator handles conversion
            **kwargs
        )
        
        self.value = value
        self.severity = severity_enum  # TypeDecorator handles conversion
        self.source = source
        self.is_active = is_active

    @classmethod
    def get_or_create(
        cls,
        ioc_type,
        value: str,
        severity=None,
        source: Optional[str] = None,
        is_active: bool = True,
        share_3rd_party: bool = False,
        parent: Optional[Object] = None,
        attributes: Optional[Dict[str, Any]] = None,
        share_with: Optional[list] = None,
        analysis_id: Optional[str] = None,
        tags: Optional[list] = None,
    ) -> "IOC":
        """
        Get or create an IOC object.
        
        Args:
            ioc_type: Type of IOC (IOCType enum or string)
            value: The IOC value (string)
            severity: Severity level (IOCSeverity enum or string, defaults to MEDIUM)
            source: Source of the IOC (string, optional)
            is_active: Whether IOC is active (bool)
            share_3rd_party: Whether to share with 3rd parties (bool)
            parent: Parent object if this IOC is related to another object
            attributes: List of attributes to add
            share_with: List of groups to share with
            analysis_id: Karton analysis ID if analyzed
            tags: List of tags to add
            
        Returns:
            IOC object (new or existing)
            
        Raises:
            TypeError: If parameters have wrong types
            ValueError: If parameters are invalid
        """
        # Convert ioc_type to enum if needed
        if isinstance(ioc_type, str):
            try:
                ioc_type_enum = IOCType(ioc_type)
            except ValueError:
                valid = [t.value for t in IOCType]
                raise ValueError(
                    f"Invalid IOC type: {ioc_type}. Must be one of: {', '.join(valid)}"
                )
        elif isinstance(ioc_type, IOCType):
            ioc_type_enum = ioc_type
        else:
            raise TypeError(
                f"ioc_type must be IOCType enum or string, got {type(ioc_type)}"
            )
        
        # Create unique dhash from IOC type and value
        value = value.strip() if value else ""
        dhash_input = f"{ioc_type_enum.value}:{value}".encode("utf-8")
        dhash = hashlib.sha256(dhash_input).hexdigest()
        
        ioc_obj = IOC(
            ioc_type=ioc_type_enum,
            value=value,
            severity=severity,
            source=source,
            is_active=is_active,
            dhash=dhash,
            share_3rd_party=share_3rd_party,
        )
        
        return cls._get_or_create(
            ioc_obj,
            share_3rd_party=share_3rd_party,
            parent=parent,
            attributes=attributes,
            share_with=share_with,
            analysis_id=analysis_id,
            tags=tags,
        )

    def update_severity(self, severity) -> None:
        """
        Update the severity level of this IOC.
        
        Args:
            severity: IOCSeverity enum, string, or None
            
        Raises:
            ValueError: If severity value is invalid
            TypeError: If severity type is invalid
        """
        severity_enum = validate_severity(severity)
        self.severity = severity_enum  # TypeDecorator handles conversion

    def mark_as_active(self, active: bool = True) -> None:
        """Mark IOC as active or inactive."""
        self.is_active = active
    
    def add_related_object(self, obj: Object) -> None:
        """
        Add a relationship between this IOC and another object.
        
        Args:
            obj: Object to relate this IOC to (e.g., File, Config)
            
        Raises:
            ValueError: If obj is None or same as self
        """
        if obj is None:
            raise ValueError("Cannot relate to None object")
        if obj.id == self.id:
            raise ValueError("Cannot relate IOC to itself")
        if obj not in self.related_objects:
            self.related_objects.append(obj)
    
    def remove_related_object(self, obj: Object) -> None:
        """
        Remove a relationship between this IOC and another object.
        
        Args:
            obj: Object to unrelate from this IOC
        """
        if obj in self.related_objects:
            self.related_objects.remove(obj)
    
    def get_related_objects_by_type(self, object_type: str):
        """
        Get all related objects of a specific type.
        
        Args:
            object_type: Type of object to filter by (e.g., 'file', 'config')
            
        Returns:
            List of related objects of the specified type
        """
        return [obj for obj in self.related_objects if obj.type == object_type]

    def __repr__(self) -> str:
        return f"<IOC {self.ioc_type}:{self.value}>"
