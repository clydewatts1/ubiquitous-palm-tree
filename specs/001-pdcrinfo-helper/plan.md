# Implementation Plan: PDCRINFO Helper Module

**Branch**: `[001-pdcrinfo-helper]` | **Date**: 2026-01-15 | **Spec**: [specs/001-pdcrinfo-helper/spec.md](specs/001-pdcrinfo-helper/spec.md)
**Input**: Feature specification from `/specs/001-pdcrinfo-helper/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Helper library module to load allow-listed PDCRINFO maintenance tables (e.g., TableSpace_Hst, DatabaseSpace_Hst) into pandas-friendly datasets with optional date and database filters, using existing Teradata connection pooling. Emphasizes safe allow-listing, clear errors, and structured logging without exposing credentials.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.11 (>=3.8 supported)  
**Primary Dependencies**: pandas, SQLAlchemy, teradatasqlalchemy, PyYAML, pytest, mypy, black, flake8  
**Storage**: Teradata PDCRINFO tables (read-only access)  
**Testing**: pytest with pytest-mock; mypy for type checking  
**Target Platform**: Linux/Windows development; Teradata backend  
**Project Type**: Single library project (src/, tests/)  
**Performance Goals**: Typical PDCR queries (<=30-day window) return within 5 seconds (SC-004)  
**Constraints**: No credentials in code/logs; use allow-listed tables only; keep pydantic-free to minimize deps  
**Scale/Scope**: Focused helper for PDCRINFO maintenance tables; no write operations or schema changes

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Verify compliance with Constitution v1.0.0 principles:

- [x] **I. Library-First Architecture**: Helper lives in `src/` as reusable library
- [x] **II. Type Safety & Documentation**: Public functions will include type hints and Google-style docstrings
- [x] **III. Database Connection Management**: Reuse `TeradataConnection` context management and pooling
- [x] **IV. Testing Standards**: Plan unit tests with mocking and integration test skeletons; target >80% coverage
- [x] **V. Code Quality**: Black/Flake8/Mypy/pre-commit enforced
- [x] **VI. Data Processing**: Pandas vectorized reads; explicit handling for missing data and empty sets
- [x] **VII. Security**: No credentials in code/logs; use env config (`td_env.yaml`) and allow-listing

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
src/
├── connection.py          # existing
├── reports.py             # existing PDCR reports
└── pdcrinfo_helper.py     # new helper module (this feature)

tests/
├── unit/
│   └── test_pdcrinfo_helper.py
└── integration/
  └── test_pdcrinfo_helper_integration.py (placeholder if env available)
```

**Structure Decision**: Single library project under `src/` with unit and integration tests under `tests/`.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | n/a | n/a |
