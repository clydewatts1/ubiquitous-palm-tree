---
description: "Task list for PDCRINFO Helper Module implementation"
---

# Tasks: PDCRINFO Helper Module

**Input**: Design documents from `/specs/001-pdcrinfo-helper/`
**Prerequisites**: plan.md (✓), spec.md (✓), research.md (✓), data-model.md (✓), contracts/ (✓)

**Tests**: Tests are included per constitution requirement IV (Testing Standards).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

Single project structure: `src/`, `tests/` at repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Verify dependencies in requirements.txt (pandas, SQLAlchemy, teradatasqlalchemy, PyYAML, pytest, pytest-mock, mypy)
- [ ] T002 [P] Ensure pre-commit hooks configured with black, flake8, mypy
- [ ] T003 [P] Create src/pdcrinfo_helper.py stub file with module docstring

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T004 Define ALLOWED_TABLES constant in src/pdcrinfo_helper.py (TableSpace_Hst, DatabaseSpace_Hst)
- [ ] T005 [P] Create helper exception classes in src/pdcrinfo_helper.py (PDCRInfoError, UnsupportedTableError, InvalidDateRangeError)
- [ ] T006 [P] Implement date normalization utility (_normalize_dates) in src/pdcrinfo_helper.py
- [ ] T007 [P] Implement database pattern filter utility (_database_filter) in src/pdcrinfo_helper.py
- [ ] T008 Implement table validation utility (_validate_table) in src/pdcrinfo_helper.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Load PDCR tables into analysis-ready dataset (Priority: P1) 🎯 MVP

**Goal**: Enable loading TableSpace_Hst and DatabaseSpace_Hst into pandas DataFrame with sensible defaults

**Independent Test**: Call helper with valid env and table name; verify DataFrame columns match expected schema

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T009 [P] [US1] Create tests/unit/test_pdcrinfo_helper.py with fixtures for mocked TeradataConnection
- [ ] T010 [P] [US1] Write unit test for fetch_pdcr_table with TableSpace_Hst (mock connection, verify query shape)
- [ ] T011 [P] [US1] Write unit test for fetch_pdcr_table with DatabaseSpace_Hst (mock connection, verify query shape)
- [ ] T012 [P] [US1] Write unit test verifying default date bounds (start=1900-01-01, end=yesterday)
- [ ] T013 [P] [US1] Write unit test verifying default database pattern (%)

### Implementation for User Story 1

- [ ] T014 [US1] Implement fetch_pdcr_table function signature in src/pdcrinfo_helper.py (env_name, table_name, start_date=None, end_date=None, database_pattern="%")
- [ ] T015 [US1] Add type hints and Google-style docstring to fetch_pdcr_table (FR-008, Constitution II)
- [ ] T016 [US1] Implement table validation logic calling _validate_table (FR-005)
- [ ] T017 [US1] Implement date normalization calling _normalize_dates (FR-003)
- [ ] T018 [US1] Implement database pattern filtering calling _database_filter (FR-004)
- [ ] T019 [US1] Build query string for TableSpace_Hst with parameterized filters
- [ ] T020 [US1] Build query string for DatabaseSpace_Hst with parameterized filters
- [ ] T021 [US1] Implement connection acquisition via TeradataConnection context manager (FR-006, Constitution III)
- [ ] T022 [US1] Execute query with pd.read_sql and parameters, return DataFrame (FR-002)
- [ ] T023 [US1] Add structured logging for query intent without credentials (FR-008, Constitution VII)
- [ ] T024 [US1] Run unit tests; verify all US1 tests pass

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Apply optional filters safely (Priority: P2)

**Goal**: Support date range and database name pattern filters in retrieval requests

**Independent Test**: Call helper with explicit date range and pattern; verify only matching rows returned

### Tests for User Story 2 ⚠️

- [ ] T025 [P] [US2] Write unit test for fetch_pdcr_table with explicit start_date and end_date
- [ ] T026 [P] [US2] Write unit test for fetch_pdcr_table with database_pattern containing wildcards
- [ ] T027 [P] [US2] Write unit test for fetch_pdcr_table with database_pattern without wildcards (verify auto-wrapping with %)
- [ ] T028 [P] [US2] Write unit test verifying filter parameters passed correctly to SQL query

### Implementation for User Story 2

- [ ] T029 [US2] Verify date filter logic handles string and date objects (already in _normalize_dates from T006)
- [ ] T030 [US2] Verify pattern filter logic handles user wildcards and auto-wraps when needed (already in _database_filter from T007)
- [ ] T031 [US2] Test integration: call fetch_pdcr_table with filters and verify query parameters constructed correctly
- [ ] T032 [US2] Run unit tests; verify all US2 tests pass

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Fail fast with clear errors (Priority: P3)

**Goal**: Provide actionable error messages for invalid inputs without exposing credentials

**Independent Test**: Intentionally provide bad inputs; verify descriptive errors raised and no secrets logged

### Tests for User Story 3 ⚠️

- [ ] T033 [P] [US3] Write unit test for fetch_pdcr_table with unknown environment (verify error lists available envs)
- [ ] T034 [P] [US3] Write unit test for fetch_pdcr_table with unsupported table name (verify error lists allowed tables)
- [ ] T035 [P] [US3] Write unit test for fetch_pdcr_table with invalid date range (start > end)
- [ ] T036 [P] [US3] Write unit test verifying no credentials appear in error messages or logs

### Implementation for User Story 3

- [ ] T037 [US3] Implement environment validation in fetch_pdcr_table (catch TeradataConnectionError, re-raise with available envs list) (FR-007)
- [ ] T038 [US3] Implement table name validation raising UnsupportedTableError with allowed list (FR-005)
- [ ] T039 [US3] Implement date range validation raising InvalidDateRangeError if start > end
- [ ] T040 [US3] Add exception handling for query failures with actionable messages (FR-007, Constitution VII)
- [ ] T041 [US3] Review logging calls to ensure no connection strings or credentials logged (FR-008, Constitution VII)
- [ ] T042 [US3] Run unit tests; verify all US3 tests pass

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Edge Cases & Refinement

**Purpose**: Handle edge cases identified in spec.md

- [ ] T043 [P] Write unit test for missing td_env.yaml (verify TeradataConnectionError raised with helpful message)
- [ ] T044 [P] Write unit test for empty result set (verify empty DataFrame returned, no exception)
- [ ] T045 [P] Implement empty result handling in fetch_pdcr_table (log condition, return empty DataFrame)
- [ ] T046 [P] Add edge case documentation to docstring examples in src/pdcrinfo_helper.py
- [ ] T047 Run mypy on src/pdcrinfo_helper.py; fix any type errors (Constitution V)
- [ ] T048 Run flake8 on src/pdcrinfo_helper.py; ensure complexity <= 10, line length compliant (Constitution V)
- [ ] T049 Run black on src/ and tests/; verify formatting (Constitution V)

---

## Phase 7: Integration Testing (Optional - requires live Teradata environment)

**Purpose**: End-to-end validation with real database connection

- [ ] T050 Create tests/integration/test_pdcrinfo_helper_integration.py with @pytest.mark.integration decorator
- [ ] T051 Write integration test for TableSpace_Hst retrieval with real connection (if td_env.yaml configured)
- [ ] T052 Write integration test for DatabaseSpace_Hst retrieval with real connection (if td_env.yaml configured)
- [ ] T053 Document how to run integration tests in quickstart.md

---

## Phase 8: Documentation & Quality Gates

**Purpose**: Final polish and compliance verification

- [ ] T054 Update quickstart.md with complete usage examples including error handling
- [ ] T055 Add module-level example to src/pdcrinfo_helper.py docstring
- [ ] T056 Run pytest with coverage report; verify >80% coverage (Constitution IV)
- [ ] T057 Review constitution compliance checklist in plan.md; verify all gates passed
- [ ] T058 Update README.md with PDCRINFO helper usage section
- [ ] T059 Run pre-commit hooks on all changed files; ensure all checks pass

---

## Completion Criteria

- [ ] All unit tests passing (pytest tests/unit/)
- [ ] Code coverage >80% (pytest --cov=src)
- [ ] Type checking passes (mypy src/)
- [ ] Linting passes (flake8 src/ tests/)
- [ ] Formatting correct (black --check src/ tests/)
- [ ] Pre-commit hooks pass
- [ ] Constitution compliance verified in plan.md
- [ ] Documentation complete (docstrings, quickstart.md, README.md)
- [ ] Integration tests documented (even if skipped due to env unavailability)
