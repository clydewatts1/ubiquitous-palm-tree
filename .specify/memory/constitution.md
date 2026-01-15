<!--
SYNC IMPACT REPORT - Constitution v1.0.0
========================================
Version Change: NEW → 1.0.0
Reason: Initial ratification of project constitution

Principles Defined:
- I. Library-First Architecture
- II. Type Safety & Documentation
- III. Database Connection Management
- IV. Testing Standards
- V. Code Quality & Formatting
- VI. Data Processing Excellence
- VII. Security & Credentials

Sections Added:
- Core Principles (7 principles)
- Technology Stack Requirements
- Development Workflow & Quality Gates
- Governance

Templates Status:
- ✅ plan-template.md - Reviewed, aligns with principles
- ✅ spec-template.md - Reviewed, aligns with testing standards
- ✅ tasks-template.md - Reviewed, aligns with workflow requirements
- ✅ checklist-template.md - Not reviewed (not critical for constitution alignment)
- ✅ agent-file-template.md - Not reviewed (not critical for constitution alignment)

Follow-up Items: None
-->

# Teradata PDCR Report Generator Constitution

## Core Principles

### I. Library-First Architecture

All functionality MUST be implemented as modular, reusable libraries within the `src/` directory. Each module MUST be self-contained, independently testable, and serve a clear purpose. Libraries MUST expose well-defined interfaces through functions and classes, not through direct script execution. No organizational-only modules—every component must provide concrete functionality.

**Rationale**: Modularity enables independent testing, easier maintenance, and code reuse across different report types and use cases.

### II. Type Safety & Documentation

All public functions and classes MUST include:
- Complete type hints for parameters and return values
- Google-style docstrings with descriptions, arguments, returns, and raises sections
- Examples in docstrings for complex functionality

**Rationale**: Type hints enable static analysis with mypy, improve IDE support, and serve as inline documentation. Comprehensive docstrings ensure maintainability and ease onboarding.

### III. Database Connection Management

Database connections MUST:
- Use SQLAlchemy with Teradata dialect (teradatasqlalchemy)
- Be managed exclusively through context managers (with statements)
- Implement connection pooling for production use
- Handle connection failures gracefully with appropriate error messages
- Never expose credentials in logs or error messages

**Rationale**: Proper connection management prevents resource leaks, ensures consistent cleanup, and improves application reliability. Security is paramount when handling database credentials.

### IV. Testing Standards

Testing is MANDATORY for all new functionality:
- Unit tests for all functions and methods (>80% coverage target)
- Use pytest as the testing framework
- Mock external dependencies (database connections) in unit tests
- Integration tests for end-to-end database operations
- All tests MUST pass before code review approval

**Rationale**: High test coverage catches regressions early, documents expected behavior, and enables confident refactoring.

### V. Code Quality & Formatting

All code MUST adhere to:
- **Black** formatting (line length: 88 characters)
- **Flake8** linting (max line length: 127, complexity: 10)
- **PEP 8** naming conventions
- **Mypy** type checking (strict mode recommended)
- Pre-commit hooks to enforce standards

**Rationale**: Consistent code style reduces cognitive load, prevents bikeshedding, and makes code reviews focus on logic rather than formatting.

### VI. Data Processing Excellence

Data processing MUST follow pandas best practices:
- Use vectorized operations over row-by-row iteration
- Validate data types and ranges after loading
- Handle missing data explicitly (document assumptions)
- Optimize queries to minimize data transfer from database
- Document performance considerations for large datasets

**Rationale**: Pandas is powerful but can be inefficient if misused. Following best practices ensures scalable, maintainable data processing pipelines.

### VII. Security & Credentials

Credentials and sensitive information MUST:
- Never be committed to version control
- Be loaded from environment variables or secure configuration files
- Use template files (e.g., `td_env.yaml.template`) to document required settings
- Be validated before use (fail fast on missing credentials)
- Follow principle of least privilege for database access

**Rationale**: Security breaches can have severe consequences. Proper credential management is non-negotiable for production systems.

## Technology Stack Requirements

### Core Stack (MUST USE)
- **Python**: 3.8+ (target 3.11 for development)
- **pandas**: ≥2.0.0 for data manipulation
- **SQLAlchemy**: ≥1.4.0 for database abstraction
- **teradatasqlalchemy**: ≥17.20.0.0 for Teradata connectivity
- **pytest**: ≥7.4.0 for testing

### Development Tools (MUST USE)
- **black**: Code formatting (line length: 88)
- **flake8**: Linting (max line length: 127, complexity: 10)
- **mypy**: Static type checking
- **pre-commit**: Automated quality checks

### Optional Tools (MAY USE)
- **Jupyter**: For interactive development and report prototyping
- **plotly**: For data visualization in reports
- **pytest-cov**: For coverage reporting

All dependencies MUST be specified in `requirements.txt` with minimum version constraints.

## Development Workflow & Quality Gates

### Before Implementation
1. Feature specification created (if using speckit workflow)
2. Test cases defined for new functionality
3. Dependencies and environment validated

### During Implementation
1. Write tests first (test-driven development encouraged)
2. Implement functionality to pass tests
3. Run formatters and linters (`black`, `flake8`)
4. Run type checker (`mypy`)
5. Ensure all tests pass locally

### Before Code Review
1. All tests passing (`pytest tests/`)
2. No linting errors (`flake8 src/ tests/`)
3. Type checking passes (`mypy src/`)
4. Code formatted (`black src/ tests/`)
5. Pre-commit hooks pass
6. Documentation updated (README, docstrings)

### Code Review Requirements
1. At least one approval required
2. All conversations resolved
3. CI/CD checks pass (if configured)
4. Constitution compliance verified (principles I-VII)

### Complexity Justification
Any functionality that violates complexity limits (flake8 complexity: 10) MUST:
- Document why complexity is unavoidable
- Include extra tests for edge cases
- Be reviewed by at least two team members
- Have a plan for future simplification if possible

## Governance

This constitution supersedes all other development practices and guidelines. All code reviews, pull requests, and architectural decisions MUST verify compliance with these principles.

### Amendment Process
1. Proposed changes documented with rationale
2. Team discussion and consensus
3. Version bump according to semantic versioning:
   - **MAJOR**: Backward-incompatible principle changes or removals
   - **MINOR**: New principles added or significant expansions
   - **PATCH**: Clarifications, typos, or minor refinements
4. Migration plan for existing code (if needed)
5. Update all dependent templates and documentation

### Compliance Verification
- Constitution checks integrated into code review checklists
- Automated checks via pre-commit hooks and CI/CD where applicable
- Quarterly constitution review to ensure principles remain relevant

### Runtime Development Guidance
For detailed implementation guidance, refer to `.github/copilot-instructions.md` which provides specific coding patterns, examples, and best practices that align with this constitution.

**Version**: 1.0.0 | **Ratified**: 2026-01-15 | **Last Amended**: 2026-01-15
