<!--
SYNC IMPACT REPORT - Constitution Amendment
============================================
Version Change: INITIAL → 1.0.0
Amendment Type: Initial ratification
Rationale: First version establishing project governance and principles

Modified Principles:
- NEW: I. Code Quality Standards
- NEW: II. Testing Discipline (NON-NEGOTIABLE)
- NEW: III. User Experience Consistency
- NEW: IV. Performance Requirements

Added Sections:
- Core Principles (4 principles defined)
- Quality Standards
- Development Workflow
- Governance

Templates Status:
✅ plan-template.md - Aligned with constitution checks
✅ spec-template.md - Aligned with acceptance criteria requirements
✅ tasks-template.md - Aligned with testing and code quality principles

Follow-up Actions:
- None (initial version)

Date: 2026-01-16
-->

# Teradata PDCR Report Generator Constitution

## Core Principles

### I. Code Quality Standards
**MUST** maintain professional Python code quality at all times:
- Black formatting (line length: 88) applied to all Python code
- Flake8 linting (max line length: 127, complexity: 10) with zero violations
- Type hints required for all function parameters and return values
- Google-style docstrings mandatory for all public functions and classes
- PEP 8 naming conventions strictly enforced

**Rationale**: Consistent code quality ensures maintainability, reduces bugs, enables team collaboration, and makes the codebase accessible to new contributors. Type hints catch errors early and serve as inline documentation.

### II. Testing Discipline (NON-NEGOTIABLE)
**MUST** achieve and maintain comprehensive test coverage:
- Minimum 80% code coverage for all modules
- Unit tests required for every function before merge
- Integration tests mandatory for database operations (mocked for CI/CD)
- pytest fixtures used for test setup and teardown
- Test structure follows Arrange-Act-Assert pattern
- No merge permitted without passing all tests

**Rationale**: High test coverage prevents regressions, documents expected behavior, enables confident refactoring, and ensures database operations work correctly without testing against production systems.

### III. User Experience Consistency
**MUST** provide consistent, intuitive interfaces across all reports:
- DataFrame column naming: PascalCase for database columns (e.g., `LogDate`, `UserName`)
- Function naming: snake_case with descriptive verbs (e.g., `get_tablespace_history`)
- Date parameters: Accept both `date` objects and ISO strings, default to sensible ranges
- Wildcard patterns: Support SQL LIKE patterns (%, _) in filter parameters
- Error messages: Clear, actionable, include context (environment, date range)
- Logging: Structured with appropriate levels (DEBUG for params, INFO for operations, ERROR for failures)

**Rationale**: Consistent UX reduces learning curve, minimizes errors, enables predictable behavior across different report types, and improves developer productivity when using the library.

### IV. Performance Requirements
**MUST** optimize for large dataset handling and query efficiency:
- Parameterized queries mandatory (prevents SQL injection, enables query plan caching)
- Use SQLAlchemy context managers for connection management
- Pandas operations prefer vectorization over iteration
- Query result sets limited by date ranges and filters
- Memory-efficient data types (use appropriate pandas dtypes)
- Avoid N+1 query patterns; aggregate in SQL when possible
- Log slow queries (>5 seconds) with timing information

**Rationale**: Teradata PDCR tables contain millions of rows. Efficient queries reduce load on database, minimize memory usage, improve response times, and enable analysis of larger datasets without resource exhaustion.

## Quality Standards

### Documentation Requirements
- README.md updated when adding new features or changing usage patterns
- Jupyter notebooks include markdown cells explaining analysis steps
- Inline comments for complex logic (e.g., date normalization, wildcard handling)
- API changes documented in docstrings before release
- Examples provided in docstrings for all public methods

### Code Organization
- Source code: `src/` directory (connection, reports, utilities)
- Tests: `tests/` directory (mirroring source structure)
- Examples: Jupyter notebooks in project root
- Configuration: `td_env.yaml` (template provided, actual file gitignored)

### Security and Credentials
- Never commit credentials or connection strings
- Use environment-based configuration (`td_env.yaml`)
- Validate and sanitize all user inputs
- Parameterized queries prevent SQL injection
- Log messages never include sensitive data (passwords, connection strings)

## Development Workflow

### Before Starting Work
1. Review related existing code patterns
2. Check if similar functionality exists to reuse
3. Plan test cases before implementation
4. Ensure development environment configured (Python 3.8+, dependencies installed)

### During Development
1. Write failing tests first (Red)
2. Implement minimum code to pass tests (Green)
3. Refactor while keeping tests passing
4. Run formatters: `black src/ tests/`
5. Run linters: `flake8 src/ tests/`
6. Check coverage: `pytest --cov=src tests/`

### Before Merge
1. All tests passing locally
2. Code coverage ≥80%
3. No linting violations
4. Docstrings complete
5. README updated if needed
6. Jupyter notebooks tested (if modified)

### When Fixing Bugs
1. Create test reproducing the bug
2. Verify test fails with current code
3. Fix bug with minimal changes
4. Verify fix doesn't break existing tests
5. Add regression test to prevent recurrence

## Governance

This constitution supersedes all other development practices and guidelines. All code reviews, pull requests, and feature implementations **MUST** verify compliance with these principles.

### Amendment Process
- Proposals submitted via issue/PR with rationale
- Team review and discussion required
- Version increment according to semantic versioning:
  - **MAJOR**: Backward-incompatible principle changes, removal of principles
  - **MINOR**: New principles added, material expansions to guidance
  - **PATCH**: Clarifications, wording improvements, typo fixes
- Migration plan required for breaking changes
- Sync impact analysis across templates and documentation

### Compliance Review
- Constitution principles checked in plan template ("Constitution Check" gate)
- All feature specs must include testable acceptance criteria (Principle II)
- Code quality gates enforced in CI/CD pipeline (Principles I, II, IV)
- Regular audits of codebase for adherence

### Runtime Guidance
For day-to-day development guidance and agent-specific instructions, refer to `.github/copilot-instructions.md`. The constitution establishes non-negotiable principles; the guidance file provides tactical implementation advice.

**Version**: 1.0.0 | **Ratified**: 2026-01-16 | **Last Amended**: 2026-01-16
