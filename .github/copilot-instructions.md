# GitHub Copilot Instructions

## Project Overview
This is a Teradata PDCR (Performance Data Collection and Reporting) report generator using Python, pandas, and teradatasqlalchemy. The project provides tools to connect to Teradata databases, extract performance data, and generate analytical reports.

## Coding Standards

### Python Style
- **Formatter**: Black (line length: 88)
- **Linter**: Flake8 (max line length: 127, complexity: 10)
- **Type Checker**: Mypy (strict mode recommended)
- **Python Version**: 3.8+ (target 3.11)

### Code Structure
- Place all source code in `src/` directory
- Place all tests in `tests/` directory
- Use meaningful module and function names
- Follow PEP 8 naming conventions

### Documentation
- Write comprehensive docstrings for all public functions/classes
- Use Google-style docstrings format
- Include type hints for all function parameters and return values
- Update README.md when adding new features

## Architecture Guidelines

### Module Organization
```
src/
├── __init__.py          # Package initialization
├── connection.py        # Database connection management
├── queries.py           # SQL query builders
├── reports.py           # Report generation logic
└── utils.py             # Utility functions
```

### Database Connections
- Use SQLAlchemy with Teradata dialect
- Implement connection pooling for efficiency
- Always use context managers for connections
- Handle connection errors gracefully

### Data Processing
- Use pandas DataFrames for data manipulation
- Optimize queries to minimize data transfer
- Handle missing data appropriately
- Validate data types and ranges

## Testing Requirements

### Test Coverage
- Aim for >80% code coverage
- Write unit tests for all functions
- Include integration tests for database operations
- Use pytest fixtures for test setup

### Test Structure
```python
def test_function_name():
    # Arrange
    expected = ...
    
    # Act
    result = function_under_test()
    
    # Assert
    assert result == expected
```

### Mocking
- Mock external dependencies (database connections)
- Use `pytest-mock` or `unittest.mock`
- Don't test external systems directly

## Common Tasks

### Adding a New Feature
1. Create feature branch: `git checkout -b feature/feature-name`
2. Write tests first (TDD approach)
3. Implement feature in `src/`
4. Update documentation
5. Run tests and linters
6. Submit PR with comprehensive description

### Database Queries
- Parameterize all queries (prevent SQL injection)
- Use SQLAlchemy ORM or Core when possible
- Optimize for performance (indexes, query structure)
- Log slow queries for debugging

### Error Handling
- Use specific exception types
- Provide meaningful error messages
- Log errors with appropriate severity
- Don't expose sensitive information in errors

## Dependencies Management
- Add dependencies to `requirements.txt`
- Specify minimum versions for stability
- Keep dependencies up to date
- Document why each dependency is needed

## Performance Considerations
- Profile code for bottlenecks
- Use vectorized operations with pandas
- Batch database operations when possible
- Cache expensive computations

## Security
- Never commit credentials or secrets
- Use environment variables for configuration
- Validate and sanitize all inputs
- Follow least privilege principle for database access

## Agent-Specific Guidelines

### When Implementing Features
1. Review related existing code first
2. Follow established patterns in the codebase
3. Write self-documenting code with clear names
4. Add logging for debugging purposes
5. Handle edge cases and error conditions

### When Fixing Bugs
1. Reproduce the bug with a test
2. Identify root cause
3. Fix with minimal changes
4. Verify fix doesn't break existing functionality
5. Add regression test

### When Refactoring
1. Ensure test coverage before refactoring
2. Make incremental changes
3. Run tests after each change
4. Don't mix refactoring with feature additions
5. Update documentation to reflect changes

## Questions to Ask Before Implementation
- Does this change align with project architecture?
- Are there existing patterns I should follow?
- What edge cases need handling?
- What tests are needed?
- Does documentation need updating?
- Are there performance implications?
- Are there security considerations?
