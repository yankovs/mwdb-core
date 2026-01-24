from typing import Dict, Tuple, Type

from mwdb.model import (
    Comment,
    Config,
    File,
    IOC,
    KartonAnalysis,
    Object,
    Tag,
    TextBlob,
    User,
)

from .exceptions import FieldNotQueryableException
from .fields import (
    AttributeField,
    BaseField,
    CommentAuthorField,
    ConfigField,
    DatetimeField,
    FavoritesField,
    FileNameField,
    IOCTypeField,
    MultiBlobField,
    MultiConfigField,
    MultiFileField,
    RelatedIOCField,
    RelationField,
    ShareField,
    SharerField,
    SizeField,
    StringField,
    StringListField,
    UploadCountField,
    UploaderField,
    UUIDField,
)
from .parse_helpers import PathSelector, parse_field_path

# Import IOC_TYPE_MAP from fields
try:
    from .fields import IOC_TYPE_MAP
except ImportError:
    # Fallback: define IOC types locally
    IOC_TYPE_MAP = {
        "ip": "ip",
        "iprange": "iprange",
        "url": "url",
        "domain": "domain",
        "email": "email",
        "md5": "md5",
        "sha1": "sha1",
        "sha256": "sha256",
        "sha512": "sha512",
        "ssdeep": "ssdeep",
        "file_path": "file_path",
        "registry_key": "registry_key",
        "c2_url": "c2_url",
        "mutex": "mutex",
        "process_name": "process_name",
    }

object_mapping: Dict[str, Type[Object]] = {
    "file": File,
    "object": Object,
    "static": Config,  # legacy
    "config": Config,
    "blob": TextBlob,
}

field_mapping: Dict[str, Dict[str, BaseField]] = {
    Object.__name__: {
        "dhash": StringField(Object.dhash),
        "tag": StringListField(Object.tags, Tag.tag),
        "comment": StringListField(Object.comments, Comment.comment),
        "meta": AttributeField(),  # legacy
        "attribute": AttributeField(),
        "shared": ShareField(),
        "sharer": SharerField(),
        "uploader": UploaderField(),
        "upload_time": DatetimeField(Object.upload_time),
        "parent": RelationField(Object.parents),
        "child": RelationField(Object.children),
        "favorites": FavoritesField(),
        "karton": UUIDField(Object.analyses, KartonAnalysis.id),
        "comment_author": CommentAuthorField(Object.comment_authors, User.login),
        "upload_count": UploadCountField(),
    },
    File.__name__: {
        "name": FileNameField(),
        "size": SizeField(File.file_size),
        "type": StringField(File.file_type),
        "md5": StringField(File.md5),
        "sha1": StringField(File.sha1),
        "sha256": StringField(File.sha256),
        "sha512": StringField(File.sha512),
        "ssdeep": StringField(File.ssdeep),
        "crc32": StringField(File.crc32),
        "multi": MultiFileField(),
        "ioc": RelatedIOCField(File),
    },
    Config.__name__: {
        "type": StringField(Config.config_type),
        "family": StringField(Config.family),
        "cfg": ConfigField(),
        "multi": MultiConfigField(),
        "ioc": RelatedIOCField(Config),
    },
    TextBlob.__name__: {
        "name": StringField(TextBlob.blob_name),
        "size": SizeField(TextBlob.blob_size),
        "type": StringField(TextBlob.blob_type),
        "content": StringField(TextBlob._content),
        "first_seen": DatetimeField(TextBlob.upload_time),
        "last_seen": DatetimeField(TextBlob.last_seen),
        "multi": MultiBlobField(),
        "ioc": RelatedIOCField(TextBlob),
    },
    IOC.__name__: {
        "ioc_type": StringField(IOC.ioc_type),
        "value": StringField(IOC.value),
        "severity": StringField(IOC.severity),
        "source": StringField(IOC.source),
        "is_active": StringField(IOC.is_active),
        "last_seen": DatetimeField(Object.last_seen),
    },
}


def get_field_mapper(
    queried_type: str, field_selector: str
) -> Tuple[BaseField, PathSelector]:
    field_path = parse_field_path(field_selector)
    field_name, asterisks = field_path[0]
    # Map object type selector
    if field_name in object_mapping:
        selected_type = object_mapping[field_name]
        field_path = field_path[1:]
    else:
        selected_type = queried_type

    if not field_path:
        # Malformed query like `blob:"*"`
        fields = ", ".join(field_mapping[selected_type.__name__].keys())
        error = f"Can't query {field_name} directly. Try one of fields: {fields}."
        raise FieldNotQueryableException(error)

    # Map object field selector
    field_name, asterisks = field_path[0]
    if field_name in field_mapping[selected_type.__name__]:
        field = field_mapping[selected_type.__name__][field_name]
    elif field_name in field_mapping[Object.__name__]:
        field = field_mapping[Object.__name__][field_name]
    elif selected_type.__name__ == IOC.__name__ and field_name in IOC_TYPE_MAP:
        # Special case: querying IOC directly with type name (e.g., ioc.ip:* or ip:* when querying IOCs)
        # Return IOCTypeField with the field_path including the IOC type
        field = IOCTypeField()
        # Return full path from field name onwards so IOCTypeField can extract the type
        return field, field_path
    else:
        raise FieldNotQueryableException(f"No such field {field_name}")

    # Return the field and the path AFTER the field name (for subpaths)
    return field, field_path[1:]
