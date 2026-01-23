# IOC Search Implementation

## Overview

IOC search functionality has been added to MWDB's Lucene-based search system. IOCs can now be discovered using powerful search queries with filtering by type, value, severity, source, and more.

## Search Fields

The following fields are available for IOC queries:

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `ioc_type` | String | Type of IOC (ip, url, domain, email, md5, sha1, sha256, sha512, ssdeep, file_path, registry_key, c2_url, mutex, process_name, iprange) | `ioc_type:ip` |
| `value` | String | The IOC value | `value:192.168.1.1` |
| `severity` | String | Severity level (low, medium, high, critical) | `severity:critical` |
| `source` | String | Source where IOC was discovered | `source:threat_feed_1` |
| `is_active` | String | Whether IOC is active (true/false) | `is_active:true` |
| `last_seen` | DateTime | Last time IOC was seen | `last_seen:[2024-01-01 TO 2024-12-31]` |
| `dhash` | String | Content hash (inherited from Object) | `dhash:abc123...` |
| `tag` | String | Tagged with label (inherited from Object) | `tag:botnet` |
| `comment` | String | Has comment containing text (inherited from Object) | `comment:malicious` |
| `attribute` | JSON | Has attribute key:value (inherited from Object) | `attribute:family:trojan` |
| `parent` | Object | Related to parent object (inherited from Object) | `parent:file` |
| `upload_time` | DateTime | When IOC was created (inherited from Object) | `upload_time:[now-7d TO now]` |

## Basic Search Examples

### Search by IOC Type

```
# Find all IP IOCs
ioc_type:ip

# Find all domain IOCs
ioc_type:domain

# Find all hash IOCs (md5, sha1, sha256, sha512, ssdeep)
ioc_type:(md5 OR sha256 OR sha512)
```

### Search by Value

```
# Find IOCs with specific value
value:192.168.1.1

# Find IOCs with wildcards
value:192.168.*

# Find IOCs matching pattern
value:"example.com"
```

### Search by Severity

```
# Find critical severity IOCs
severity:critical

# Find high or critical severity
severity:(high OR critical)

# Find non-low severity
severity:-low
```

### Search by Source

```
# Find IOCs from specific source
source:threat_feed_1

# Find IOCs from multiple sources
source:(threat_feed_1 OR external_source)

# Find IOCs without source
NOT source:*
```

### Search by Active Status

```
# Find active IOCs
is_active:true

# Find inactive IOCs
is_active:false
```

## Advanced Search Examples

### Combined Queries

```
# Critical severity IPs from specific source
ioc_type:ip AND severity:critical AND source:threat_feed_1

# Domain IOCs that are active and high/critical severity
ioc_type:domain AND is_active:true AND severity:(high OR critical)

# All IOCs except from specific source
NOT source:deprecated_feed

# High severity IOCs seen in last 30 days
severity:high AND last_seen:[now-30d TO now]
```

### Search with Relationships

```
# IOCs in specific file
parent:file AND ioc_type:ip

# IOCs with specific tag
tag:botnet

# IOCs with comments containing "c2"
comment:c2

# IOCs with attribute evidence:confirmed
attribute:evidence:confirmed
```

### Complex Scenarios

```
# All IOCs that are either critical severity or tagged as "urgent"
severity:critical OR tag:urgent

# IP IOCs from threat feeds that are active
ioc_type:ip AND source:(threat_feed_* OR external_source) AND is_active:true

# Hash IOCs not yet analyzed
ioc_type:(md5 OR sha256) AND NOT parent:*

# IOCs seen in last 7 days and tagged with investigation
last_seen:[now-7d TO now] AND tag:investigation
```

## Type Selector Syntax

IOC queries can use the `ioc:` prefix to explicitly target IOC objects:

```
# These are equivalent:
ioc_type:ip
ioc:value:192.168.1.1

# Multiple fields with type selector
ioc:(severity:critical AND ioc_type:ip)

# Mix IOC and inherited fields
ioc:severity:high AND tag:botnet
```

## DateTime Queries

The `last_seen` and `upload_time` fields support date/time ranges:

```
# Last 7 days
last_seen:[now-7d TO now]

# Last 30 days
last_seen:[now-30d TO now]

# Specific date range
last_seen:[2024-01-01 TO 2024-12-31]

# Before specific date
last_seen:[* TO 2024-06-30]

# After specific date
last_seen:[2024-01-01 TO *]

# Combined with other filters
ioc_type:ip AND last_seen:[now-14d TO now]
```

## Inherited Fields

IOCs inherit search fields from the Object base class:

- **dhash**: Unique content hash
- **tag**: Tags applied to IOC
- **comment**: Comments on IOC
- **attribute**: Custom attributes
- **shared**: Shared with groups/users
- **sharer**: Users who shared the IOC
- **uploader**: User who uploaded the IOC
- **upload_time**: Creation timestamp
- **parent**: Related parent objects
- **child**: Related child objects
- **upload_count**: Number of users who uploaded this IOC
- **karton**: Linked Karton analysis

Example:
```
# IOC uploaded by specific user
uploader:analyst1

# IOC shared with specific group
shared:trusted_analysts

# IOC with rich attributes
attribute:geographical_origin:CN AND attribute:confidence:0.8

# IOC related to file
parent:file
```

## Negation

Use `-` or `NOT` to negate queries:

```
# Active IOCs that are NOT low severity
is_active:true AND -severity:low

# IOCs without source
NOT source:*

# Non-critical IOCs
NOT severity:critical

# IP IOCs that are not from specific source
ioc_type:ip AND NOT source:internal_feed
```

## Pattern Matching

- `*` - Wildcard for any characters
- `?` - Single character wildcard (not supported in all fields)
- Quoted strings for exact matching: `value:"192.168.1.1"`

Examples:
```
# Values starting with 192.168
value:192.168.*

# Sources starting with threat
source:threat*

# Exact domain match
value:"example.com"
```

## API Usage

### Via REST API

Search IOCs through the REST API using the search parameter:

```bash
# Simple search
curl "http://localhost:5000/api/search?type=ioc&query=severity:critical"

# Complex search
curl "http://localhost:5000/api/search?type=ioc&query=ioc_type:ip%20AND%20severity:critical%20AND%20source:threat_feed_1"
```

### Via Python Client

```python
from mwdb import MWDB

mwdb = MWDB()

# Search for critical IP IOCs
results = mwdb.search("ioc_type:ip AND severity:critical", type="ioc")

for ioc in results:
    print(f"{ioc.ioc_type}: {ioc.value} ({ioc.severity})")
```

### Via SQLAlchemy

```python
from mwdb.core.search import build_query
from mwdb.model import IOC

# Complex search query
query = build_query(
    "ioc_type:ip AND severity:critical AND is_active:true",
    queried_type=IOC
)

results = query.all()
```

## Common Use Cases

### 1. Finding All IOCs of a Specific Type

```
ioc_type:ip
ioc_type:domain
ioc_type:url
ioc_type:(md5 OR sha256)
```

### 2. Finding Critical/High Severity IOCs

```
severity:(critical OR high)
severity:critical AND ioc_type:ip
```

### 3. Finding Recently Discovered IOCs

```
# Last 24 hours
upload_time:[now-1d TO now]

# Last 7 days
upload_time:[now-7d TO now]

# Last 30 days with specific type
upload_time:[now-30d TO now] AND ioc_type:domain
```

### 4. Finding IOCs from Specific Source

```
source:threat_feed_1
source:(threat_feed_1 OR threat_feed_2)
source:internal AND severity:critical
```

### 5. Finding Active IOCs Ready for Detection

```
is_active:true AND severity:(critical OR high)
is_active:true AND ioc_type:(ip OR domain)
```

### 6. Finding IOCs Related to Incidents

```
# IOCs tagged with specific incident
tag:incident_2024_001

# IOCs with investigation comments
comment:investigation

# IOCs with specific attributes
attribute:incident_id:2024-001
```

### 7. Finding IOCs Not Yet Analyzed

```
NOT parent:*
NOT tag:*
```

### 8. Finding Duplicates

```
# Multiple IOCs with same value
value:192.168.1.1

# All hash IOCs across all families
ioc_type:(md5 OR sha256)
```

## Performance Tips

1. **Use specific types**: `ioc_type:ip` is faster than searching all IOCs
2. **Combine filters**: `severity:critical AND ioc_type:ip` filters early
3. **Use ranges for dates**: Date ranges are more efficient than wildcards
4. **Limit results**: Use pagination to avoid returning huge result sets

## Error Handling

Common error messages and solutions:

| Error | Cause | Solution |
|-------|-------|----------|
| "Invalid IOC type: xyz" | Misspelled or unsupported IOC type | Check valid types: ip, url, domain, email, md5, sha1, sha256, sha512, ssdeep, file_path, registry_key, c2_url, mutex, process_name, iprange |
| "Invalid severity: xyz" | Misspelled severity | Use: low, medium, high, critical |
| "No such field ioc_xyz" | Field doesn't exist | Check available fields above |
| "Can't query ioc directly" | Missing field selector | Use: `ioc:ioc_type:ip` or just `ioc_type:ip` |

## Examples in Frontend

### Search Bar Usage

```
# User types into search bar and hits Enter
Query: severity:critical AND is_active:true
Results: All critical, active IOCs

# Search for IOCs related to file
Query: parent:file AND ioc_type:ip
Results: All IP IOCs in any file

# Advanced search with date range
Query: upload_time:[now-7d TO now] AND severity:critical
Results: Critical IOCs uploaded in last 7 days
```

## Migration Notes

IOC search was added after initial IOC implementation. No migration needed - search queries automatically work once code is deployed.

## Backward Compatibility

✅ Fully backward compatible
- Existing object searches unaffected
- New IOC search uses same infrastructure
- No changes to search API structure
- Inherited fields (tag, comment, attribute) work the same

## Future Enhancements

Potential improvements:
- Full-text search on IOC value with stemming
- Range queries on severity (severity > medium)
- Relationship search helpers
- Saved search templates
- Search analytics

## Implementation Details

### How It Works

1. **Query Parsing**: Lucene query string parsed to AST
2. **Field Resolution**: Field name mapped to IOC column/relationship
3. **Condition Building**: SQLAlchemy condition generated from AST
4. **Query Execution**: SQL executed with proper type casting
5. **Results Return**: IOC objects returned with proper enum types

### Files Modified

- `mwdb/core/search/mappings.py`: Added IOC to object_mapping and field_mapping

### Supported Field Types

- **StringField**: Direct column comparison (ioc_type, value, severity, source, is_active)
- **DatetimeField**: Range and datetime queries (last_seen)
- **Inherited Fields**: From Object base class (dhash, tag, comment, attribute, etc.)

### Type Coercion

IOC search automatically handles:
- IOCType enum: Converts string to IOCType internally
- IOCSeverity enum: Converts string to IOCSeverity internally
- Boolean: Converts "true"/"false" strings to boolean
- DateTime: Parses date strings and ranges

## Related Documentation

- **IOC Model**: See IOC_SQLALCHEMY_ENHANCEMENTS.md for model details
- **IOC Examples**: See IOC_RELATIONSHIPS_EXAMPLES.md for usage patterns
- **Search System**: Check mwdb/core/search/ documentation for general search info
- **API Endpoints**: See IOC API documentation for search endpoint usage
