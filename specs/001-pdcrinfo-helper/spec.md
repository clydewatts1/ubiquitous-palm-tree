# Feature Specification: PDCRINFO Helper Module

**Feature Branch**: `[001-pdcrinfo-helper]`  
**Created**: 2026-01-15  
**Status**: Draft  
**Input**: User description: "I would like to generate a helper library module which reads in tables from teradata pdcrinfo database logining maintenance data , and read the data into a dataframe , see the existing connection.py and reports.py for examples."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Load PDCR tables into analysis-ready dataset (Priority: P1)

Data engineer loads a specified PDCRINFO maintenance table (e.g., TableSpace_Hst, DatabaseSpace_Hst) into an analysis-ready tabular dataset via a single helper call, using an environment defined in `td_env.yaml`.

**Why this priority**: Delivers the core value of making PDCR maintenance data quickly available for analysis without rewriting connection or query code.

**Independent Test**: Provide a valid environment config and request a supported PDCR table; verify the helper returns a dataset with expected columns and row count without requiring other stories.

**Acceptance Scenarios**:

1. **Given** a valid `td_env.yaml` entry for `prod`, **When** the helper is called to load `PDCRINFO.TableSpace_Hst`, **Then** it returns a tabular dataset with columns for LogDate, DatabaseName, and space metrics.
2. **Given** a valid environment and default parameters, **When** the helper is called with no date filters, **Then** it applies documented default date bounds and returns matching data without errors.

---

### User Story 2 - Apply optional filters safely (Priority: P2)

Analyst retrieves PDCR maintenance data with optional filters (date range, database name pattern, allowed table selection) to focus on relevant records.

**Why this priority**: Filters reduce data volume and make the helper broadly usable across reporting needs.

**Independent Test**: Call the helper with date range and database name pattern; confirm results are restricted accordingly and the helper remains usable without other stories.

**Acceptance Scenarios**:

1. **Given** a valid environment and date bounds, **When** the helper is called with a start and end date, **Then** only records within that range are returned.
2. **Given** a valid environment and database pattern `Sales%`, **When** the helper is called with that pattern, **Then** only matching databases appear in the output.

---

### User Story 3 - Fail fast with clear errors (Priority: P3)

Developer receives actionable errors when configuration is missing, credentials are invalid, or an unsupported table is requested, without exposing sensitive details.

**Why this priority**: Clear feedback reduces troubleshooting time and protects credentials.

**Independent Test**: Intentionally provide an invalid environment name or unsupported table; verify the helper raises a descriptive error and does not leak secrets.

**Acceptance Scenarios**:

1. **Given** an environment name not present in `td_env.yaml`, **When** the helper is called, **Then** it raises a descriptive error listing available environments.
2. **Given** a request for a table not in the allowed list, **When** the helper is called, **Then** it refuses execution and returns a clear message indicating allowed tables.

---

### Edge Cases

- Missing or unreadable `td_env.yaml` configuration file.
- Environment name present but missing required fields (host, database, credentials when needed).
- Unsupported table name requested (not in allowed PDCRINFO list).
- Empty result set for valid query (returns empty dataset without failure).
- Invalid or reversed date range (start after end) handled with validation error.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Helper MUST load data from a specified allow-listed PDCRINFO table (e.g., `TableSpace_Hst`, `DatabaseSpace_Hst`) using an environment defined in `td_env.yaml`.
- **FR-002**: Helper MUST return results as a tabular dataset compatible with pandas DataFrame operations, preserving source column names and types.
- **FR-003**: Helper MUST support optional date range filters with sensible defaults (start=1900-01-01, end=yesterday) when not provided.
- **FR-004**: Helper MUST support optional database name pattern filtering that safely handles user-provided wildcards.
- **FR-005**: Helper MUST validate requested table names against an allow list and reject unsupported names with a clear error.
- **FR-006**: Helper MUST use pooled connections via existing `TeradataConnection` context management to avoid connection leaks.
- **FR-007**: Helper MUST surface actionable, non-secret errors for missing config, invalid credentials, or failed queries.
- **FR-008**: Helper MUST emit structured logging for query intent (table, filters) without logging credentials or full connection strings.

### Key Entities *(include if feature involves data)*

- **Environment Config**: Named connection settings from `td_env.yaml` (host, database, auth settings, optional charset/tmode).
- **PDCR Table Selection**: Allow-listed PDCRINFO maintenance tables available for retrieval.
- **Retrieval Request**: Parameters provided by caller (environment, table name, date range, database pattern).
- **Result Dataset**: Tabular data returned for analysis, compatible with downstream pandas workflows.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For a valid environment and allowed table, the helper returns a correctly structured dataset (expected columns present) on the first call without manual query editing.
- **SC-002**: For invalid input (unknown environment or unsupported table), the helper returns a clear, actionable error message within a single call and without exposing credentials.
- **SC-003**: For empty-result scenarios (valid query with no rows), the helper returns an empty dataset and logs the condition without raising an exception.
- **SC-004**: For typical PDCR maintenance queries (<= 30-day range), data retrieval completes within 5 seconds in the target environment under normal load.
