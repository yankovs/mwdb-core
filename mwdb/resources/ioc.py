"""
IOC (Indicator of Compromise) resource endpoints
"""

from flask import g, request
from werkzeug.exceptions import BadRequest, Conflict, Forbidden, NotFound

from mwdb.core.capabilities import Capabilities
from mwdb.core.hooks import hooks
from mwdb.core.ioc_consts import IOCType, validate_ioc, get_ioc_type_from_value
from mwdb.core.service import Resource
from mwdb.model import IOC, db
from mwdb.model.object import ObjectTypeConflictError
from mwdb.schema.ioc import (
    IOCCreateRequestSchema,
    IOCItemResponseSchema,
    IOCListResponseSchema,
    IOCUpdateRequestSchema,
    IOCStatsResponseSchema,
)

from . import load_schema, requires_authorization, requires_capabilities
from .object import ObjectItemResource, ObjectResource, ObjectUploader


class IOCUploader(ObjectUploader):
    """Mixin for IOC upload capabilities"""
    
    def on_created(self, object, params):
        super().on_created(object, params)
        hooks.on_created_object(object)

    def on_reuploaded(self, object, params):
        super().on_reuploaded(object, params)
        hooks.on_reuploaded_object(object)

    def _create_object(
        self, spec, parent, share_with, attributes, analysis_id, tags, share_3rd_party
    ):
        """Create IOC object from specification"""
        try:
            return IOC.get_or_create(
                ioc_type=spec["ioc_type"],
                value=spec["value"],
                severity=spec.get("severity", "medium"),
                source=spec.get("source"),
                is_active=spec.get("is_active", True),
                share_3rd_party=share_3rd_party,
                parent=parent,
                share_with=share_with,
                attributes=attributes,
                analysis_id=analysis_id,
                tags=tags,
            )
        except ObjectTypeConflictError:
            raise Conflict("Object already exists and is not an IOC")
        except ValueError as e:
            raise BadRequest(str(e))


class IOCResource(ObjectResource, IOCUploader):
    """REST resource for IOC list operations"""
    
    ObjectType = IOC
    ListResponseSchema = IOCListResponseSchema
    ItemResponseSchema = IOCItemResponseSchema

    @requires_authorization
    def get(self):
        """
        ---
        summary: Search or list IOCs
        description: |
            Returns list of IOCs matching provided query,
            ordered from the latest one.
            If you want to fetch older IOCs use `older_than` parameter.

            Number of returned IOCs is limited by 'count' parameter
            (default value is 10).
        security:
            - bearerAuth: []
        tags:
            - ioc
        parameters:
            - in: query
              name: older_than
              schema:
                type: string
              description: |
                Fetch IOCs which are older than the object specified by identifier.
                Used for pagination
              required: false
            - in: query
              name: query
              schema:
                type: string
              description: Filter results using Lucene query
              required: false
            - in: query
              name: count
              schema:
                type: integer
              description: Number of objects to return
              required: false
              default: 10
        responses:
            200:
                description: List of IOCs
                content:
                  application/json:
                    schema: IOCListResponseSchema
            400:
                description: When wrong parameters were provided or syntax error in query
            404:
                description: When user doesn't have access to the `older_than` object
        """
        return super().get()

    @requires_authorization
    @requires_capabilities(Capabilities.adding_files)
    def post(self):
        """
        ---
        summary: Create IOC
        description: |
            Creates a new IOC (Indicator of Compromise).

            Requires `adding_files` capability.
        security:
            - bearerAuth: []
        tags:
            - ioc
        requestBody:
            required: true
            content:
              application/json:
                schema: IOCCreateRequestSchema
        responses:
            200:
                description: IOC created successfully
                content:
                  application/json:
                    schema: IOCItemResponseSchema
            201:
                description: IOC created
                content:
                  application/json:
                    schema: IOCItemResponseSchema
            400:
                description: Invalid IOC data
            409:
                description: IOC already exists
        """
        schema = IOCCreateRequestSchema()
        obj = load_schema(request.get_json(), schema)

        return self.create_object(obj)


class IOCItemResource(ObjectItemResource):
    """REST resource for IOC item operations"""
    
    ObjectType = IOC
    ItemResponseSchema = IOCItemResponseSchema

    @requires_authorization
    def get(self, identifier):
        """
        ---
        summary: Get IOC details
        description: Returns information about specific IOC.
        security:
            - bearerAuth: []
        tags:
            - ioc
        parameters:
            - in: path
              name: identifier
              schema:
                type: string
              description: IOC identifier (dhash)
              required: true
        responses:
            200:
                description: IOC details
                content:
                  application/json:
                    schema: IOCItemResponseSchema
            404:
                description: IOC not found or user doesn't have access to it
        """
        return super().get(identifier)

    @requires_authorization
    @requires_capabilities(Capabilities.adding_files)
    def put(self, identifier):
        """
        ---
        summary: Update IOC properties
        description: |
            Updates IOC properties like severity and active status.

            Requires `adding_files` capability.
        security:
            - bearerAuth: []
        tags:
            - ioc
        parameters:
            - in: path
              name: identifier
              schema:
                type: string
              description: IOC identifier (dhash)
              required: true
        requestBody:
            required: true
            content:
              application/json:
                schema: IOCUpdateRequestSchema
        responses:
            200:
                description: IOC updated
                content:
                  application/json:
                    schema: IOCItemResponseSchema
            400:
                description: Invalid data provided
            404:
                description: IOC not found or user doesn't have access
        """
        ioc = self.access_object(identifier)
        if not ioc:
            raise NotFound("IOC not found")
        
        if ioc.type != "ioc":
            raise Conflict("Object is not an IOC")
        
        schema = IOCUpdateRequestSchema()
        data = load_schema(request.get_json(), schema)
        
        # Update fields if provided
        if "severity" in data:
            ioc.update_severity(data["severity"])
        
        if "is_active" in data:
            ioc.mark_as_active(data["is_active"])
        
        if "source" in data:
            ioc.source = data["source"]
        
        db.session.commit()
        
        return {
            **self.ItemResponseSchema().dump(ioc),
        }

    @requires_authorization
    def delete(self, identifier):
        """
        ---
        summary: Delete IOC
        description: |
            Deletes specified IOC.

            Requires `removing_objects` capability.
        security:
            - bearerAuth: []
        tags:
            - ioc
        parameters:
            - in: path
              name: identifier
              schema:
                type: string
              description: IOC identifier (dhash)
              required: true
        responses:
            200:
                description: IOC deleted
            404:
                description: IOC not found or user doesn't have access
        """
        return super().delete(identifier)


class IOCStatsResource(Resource):
    """Resource for IOC statistics"""
    
    @requires_authorization
    def get(self):
        """
        ---
        summary: Get IOC statistics
        description: |
            Returns statistics about IOCs in the database.
        security:
            - bearerAuth: []
        tags:
            - ioc
        responses:
            200:
                description: IOC statistics
                content:
                  application/json:
                    schema: IOCStatsResponseSchema
        """
        from sqlalchemy import func
        
        # Get total IOC count
        total = IOC.query.count()
        
        # Count by type
        by_type = {}
        type_counts = db.session.query(
            IOC.ioc_type, 
            func.count(IOC.id)
        ).group_by(IOC.ioc_type).all()
        
        for ioc_type, count in type_counts:
            by_type[ioc_type] = count
        
        # Count by severity
        by_severity = {}
        severity_counts = db.session.query(
            IOC.severity,
            func.count(IOC.id)
        ).group_by(IOC.severity).all()
        
        for severity, count in severity_counts:
            by_severity[severity] = count
        
        # Count active IOCs
        active = IOC.query.filter(IOC.is_active == True).count()
        
        schema = IOCStatsResponseSchema()
        return schema.dump({
            "total": total,
            "by_type": by_type,
            "by_severity": by_severity,
            "active": active,
        })


class IOCAutoDetectResource(Resource):
    """Resource for auto-detecting IOC types"""
    
    @requires_authorization
    def post(self):
        """
        ---
        summary: Auto-detect IOC type
        description: |
            Attempts to auto-detect the type of provided IOC value.
        security:
            - bearerAuth: []
        tags:
            - ioc
        requestBody:
            required: true
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    value:
                      type: string
                      description: IOC value to analyze
        responses:
            200:
                description: Detected IOC type
                content:
                  application/json:
                    schema:
                      type: object
                      properties:
                        detected_type:
                          type: string
                          nullable: true
                        value:
                          type: string
            400:
                description: No value provided
        """
        data = request.get_json()
        
        if not data or "value" not in data:
            raise BadRequest("'value' field is required")
        
        value = data["value"].strip()
        detected_type = get_ioc_type_from_value(value)
        
        return {
            "value": value,
            "detected_type": detected_type.value if detected_type else None,
        }
