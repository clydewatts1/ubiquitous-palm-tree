# Data Model: PDCRINFO Helper Module

## Entities

### EnvironmentConfig
- **Fields**: name (str), host (str), database (str), username (str|optional for BROWSER), password (str|optional for BROWSER), logmech (str, default TD2), tmode (str|optional), charset (str|optional)
- **Validation**: name unique; required host+database; if logmech != BROWSER then username and password required; if password supplied with BROWSER then username required; config file must exist.
- **Relationships**: referenced by RetrievalRequest.env_name.

### PDCRTable
- **Fields**: table_name (enum: TableSpace_Hst, DatabaseSpace_Hst)
- **Validation**: must be allow-listed; reject unknown tables with descriptive error.

### RetrievalRequest
- **Fields**: env_name (str), table (PDCRTable), start_date (date|str, default 1900-01-01), end_date (date|str, default yesterday), database_pattern (str, default "%" with auto-wrapping when no wildcard)
- **Validation**: start_date <= end_date; env_name exists in EnvironmentConfig; pattern trimmed; supports user wildcards.
- **Relationships**: uses EnvironmentConfig; targets PDCRTable.

### ResultDataset
- **Fields**: pandas DataFrame preserving source columns for chosen table.
- **Validation**: empty result allowed; types derived from database metadata; no column renaming.
- **Relationships**: produced from RetrievalRequest execution.

## State & Transitions
- **Idle → Requested**: caller constructs RetrievalRequest with table/env/filter inputs.
- **Requested → Connected**: helper acquires engine via `TeradataConnection` (pooled, context-managed).
- **Connected → Fetched**: query executed with parameters; DataFrame produced.
- **Fetched → Completed**: DataFrame returned; engine disposed to pool automatically.
- **Error States**: missing config, invalid env, unsupported table, invalid date range, query failure (all raise descriptive exceptions, no secrets logged).
