# Research Findings: PDCRINFO Helper Module

## Decisions

### Decision: Allowed PDCRINFO tables
- **Rationale**: Align with existing reports and minimize scope. `TableSpace_Hst` and `DatabaseSpace_Hst` are already queried and represent maintenance space data needed for analysis.
- **Alternatives considered**: Include broader PDCRINFO tables (e.g., `PDCRInfoV`, `DBQL` tables); rejected to keep scope minimal and avoid new schemas.

### Decision: Default date bounds
- **Rationale**: Use start=1900-01-01 and end=yesterday to match existing report defaults and avoid partial current-day data.
- **Alternatives considered**: Require explicit dates (adds friction); default to last 30 days (could hide full history needs).

### Decision: Database name filtering
- **Rationale**: Accept caller-provided patterns; if no wildcards present, wrap with `%` for partial matches, mirroring reports.py behavior.
- **Alternatives considered**: Require explicit wildcards (less ergonomic); disable pattern filter (reduces usefulness).

### Decision: Error handling and logging
- **Rationale**: Fail fast with descriptive errors (unknown env, missing config fields, unsupported table) while avoiding credential exposure; log query intent (table, filters) at info level.
- **Alternatives considered**: Silent fallbacks (hard to debug); logging connection strings (security risk).

### Decision: Result shape
- **Rationale**: Return pandas DataFrame with source column names and types; do not rename or reorder to preserve fidelity for downstream analysis.
- **Alternatives considered**: Rename to friendlier names (could break existing consumers); return list/dict (loses DataFrame ergonomics).
