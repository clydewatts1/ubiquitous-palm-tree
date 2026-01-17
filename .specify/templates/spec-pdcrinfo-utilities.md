# Specification: Dynamic PDCR Utility Function Generation

**Project**: Teradata PDCR Report Generator  
**Feature**: Metadata-Driven Utility Function Generation  
**Date**: January 17, 2026  
**Status**: SPECIFICATION  
**Version**: 1.0.0

---

## 1. Executive Summary

This specification defines a metadata-driven approach to generating parameterized query utility functions (`get_<table_name>()`) that retrieve data from Teradata PDCR tables. Rather than manually coding each function, a single CSV metadata file (`PDCRInfo_Columns.csv`) will drive automatic code generation, ensuring consistency, maintainability, and full alignment with Constitution v1.0.0 principles.

**Key Objectives**:
- Eliminate code duplication across similar query functions
- Provide a single source of truth for table definitions, parameters, and columns
- Maintain constitutional compliance (type hints, docstrings, timing, error logging)
- Scale easily to new PDCR tables by adding metadata rows
- Enable non-developers to extend functionality via CSV updates

---

## 2. Scope & Constraints

### In Scope
- Create PDCRInfo_Columns.csv metadata file with table definitions
- Implement code generator that parses CSV and produces Python function code
- Generated functions return pandas DataFrames with full instrumentation
- Generated functions integrate seamlessly with existing PDCRInfoReport class
- Unit tests automatically generated for each function
- Full type hints and Google-style docstrings

### Out of Scope
- Database schema discovery or introspection from live Teradata (manual metadata entry only)
- Dynamic function patching at module load time (code generation at build/dev time)
- Graphical UI for metadata management (CSV file sufficient)
- Historical versioning of table definitions

### Constraints
- CSV must be valid UTF-8 with proper escaping for special characters (commas, quotes)
- Generated functions must not exceed Flake8 line length limits (127 chars max)
- All functions must support parameterized queries (no SQL string concatenation)
- Date parameters must follow existing `_normalize_dates()` pattern
- Function generation must produce PEP 8-compliant code

---

## 3. Metadata File Specification

### 3.1 PDCRInfo_Columns.csv Structure

**File Location**: Project root or `docs/` directory  
**Format**: RFC 4180 CSV (UTF-8, comma-delimited)  
**Encoding**: UTF-8 without BOM

**Column Definitions**:

| Column Name | Type | Required | Description | Example |
|---|---|---|---|---|
| `function_name` | String | ✅ Yes | Name of generated function (without `get_` prefix) | `tablespace_history`, `dbcinfo` |
| `table_name` | String | ✅ Yes | Fully qualified Teradata table name | `PDCRINFO.TableSpace_Hst`, `DBC.DBCInfoV` |
| `parameter_columns` | String | ✅ Yes | Comma-separated parameter names (env_name always required first) | `env_name,start_date,end_date,database_name` |
| `parameter_defaults` | String | ⚠️ Optional | Comma-separated default values (None, date literals, or string literals) | `None,None,None,%` |
| `parameter_types` | String | ⚠️ Optional | Comma-separated type hints matching parameters | `str,Optional[DateLike],Optional[DateLike],str` |
| `output_columns` | String | ✅ Yes | Pipe-separated column names to select from table | `LogDate\|DatabaseName\|Tablename\|AccountName\|CURRENTPERM\|PEAKPERM` |
| `where_clause` | String | ⚠️ Optional | WHERE condition using parameter placeholders (e.g., `:date_start`, `:date_end`) | `WHERE LogDate BETWEEN :start_date AND :end_date AND DatabaseName LIKE :database_name` |
| `notes` | String | ⚠️ Optional | Documentation notes (e.g., performance warnings, deprecated status) | `Requires DBC.DBCInfoV privileges; no date filtering` |

**Key Rules**:
- `function_name` must be a valid Python identifier (alphanumeric + underscore, no leading digit)
- `function_name` cannot conflict with existing methods in PDCRInfoReport
- `table_name` must include schema prefix (PDCRINFO, DBC, etc.)
- `parameter_columns` first entry must always be `env_name` (string, no default)
- Date parameters should be named `start_date` and `end_date` for automatic normalization
- `parameter_defaults` order must match `parameter_columns`; use `None` for required params with no default
- `output_columns` use pipe (`|`) delimiter; column names are case-sensitive Teradata names
- `where_clause` parameter placeholders use `:param_name` syntax matching sqlalchemy.text()

### 3.2 Sample CSV Data

```csv
function_name,table_name,parameter_columns,parameter_defaults,parameter_types,output_columns,where_clause,notes
tablespace_history,PDCRINFO.TableSpace_Hst,env_name;start_date;end_date;database_name,None;None;None;%,str;Optional[DateLike];Optional[DateLike];str,LogDate|DatabaseName|Tablename|AccountName|CURRENTPERM|PEAKPERM|CURRENTPERMSKEW|PEAKPERMSKEW,"WHERE LogDate BETWEEN :start_date AND :end_date AND DatabaseName LIKE :database_name",Returns table space usage history with peak allocations
databasespace_history,PDCRINFO.DatabaseSpace_Hst,env_name;start_date;end_date;database_name,None;None;None;%,str;Optional[DateLike];Optional[DateLike];str,LogDate|DatabaseName|CurrentPerm|PeakPerm|MaxPerm,"WHERE LogDate BETWEEN :start_date AND :end_date AND DatabaseName LIKE :database_name",Database-level space allocation history
spoolspace_history,PDCRINFO.SpoolSpace_Hst,env_name;start_date;end_date;user_name;account_name,None;None;None;%;%,str;Optional[DateLike];Optional[DateLike];str;str,LogDate|UserName|AccountName|MaxSpool|PeakSpool,"WHERE LogDate BETWEEN :start_date AND :end_date AND UserName LIKE :user_name AND AccountName LIKE :account_name",Spool space usage by user/account
dbql_summary_history,PDCRINFO.DBQLSummaryTbl_Hst,env_name;start_date;end_date;user_name,None;None;None;%,str;Optional[DateLike];Optional[DateLike];str,"LogDate|UserName|QueryCount|AMPCPUTime|ParserCPUTime|QuerySeconds|TotalIOCount|TotalIOInKB","WHERE LogDate BETWEEN :start_date AND :end_date AND UserName LIKE :user_name",DBQL summary metrics (CPU, IO, query counts)
dbcinfo,DBC.DBCInfoV,env_name,,str;,,InfoKey|InfoVal|,"WHERE 1=1",No date filtering; metadata table
```

**Delimiter Notes**:
- Parameters and defaults use semicolon (`;`) delimiter
- Output columns and type hints use pipe (`|`) delimiter
- This avoids conflicts with the CSV comma delimiter

---

## 4. Function Generation Approach

### 4.1 Architecture Decision: Code Generation at Build Time

**Chosen Approach**: Build-time code generation via Python script  
**Rationale**:
- Ensures generated code is visible and auditable (in git history)
- Enables IDE autocomplete and type checking
- Allows manual review and testing before deployment
- Simpler debugging compared to dynamic code generation
- Aligns with Python best practices (explicit is better than implicit)

**Alternative Rejected**: Runtime dynamic generation via `exec()` or metaprogramming
- Risk of security issues (code injection)
- Breaks IDE tooling and static analysis
- Difficult to debug and test
- Not idiomatic Python

### 4.2 Code Generator Script

**Script**: `scripts/generate_pdcr_utilities.py`  
**Invocation**: `python scripts/generate_pdcr_utilities.py`  
**Output**: Generated functions appended to `src/utilities.py`

**Generation Logic**:
1. Read `PDCRInfo_Columns.csv` into pandas DataFrame
2. For each row, validate metadata (column presence, format, type syntax)
3. Generate function code from template (see section 4.3)
4. Perform code quality checks (Black formatting, linting)
5. Write generated code to `src/utilities.py`
6. Generate corresponding unit tests to `tests/test_utilities_generated.py`

### 4.3 Generated Function Template

Each row in the CSV produces a function following this template:

```python
def get_<function_name>(
    env_name: str,
    <other_params_with_types_and_defaults>
) -> pd.DataFrame:
    """Retrieve <table_name> data.

    Args:
        env_name: Environment name (e.g., 'test', 'prod').
        <other_params_documented>

    Returns:
        DataFrame with columns: <column_list>.

    Example:
        >>> report = PDCRInfoReport()
        >>> df = report.get_<function_name>('prod', ...)
        >>> print(df.shape)

    Notes:
        <notes_from_csv>
    """
    
    # Normalize date parameters if present
    <date_normalization_code>
    
    # Build query
    query = text("""
        SELECT <output_columns>
        FROM <table_name>
        <where_clause>
    """)
    
    # Log query execution
    logger.debug(f"Executing get_<function_name> query for env={env_name}, ...")
    
    # Execute with timing and error handling
    start_time = time.perf_counter()
    try:
        with self.conn_mgr.get_connection(env_name) as conn:
            df = pd.read_sql(
                query,
                conn,
                params={
                    'param1': value1,
                    'param2': value2,
                    ...
                }
            )
        
        duration = time.perf_counter() - start_time
        
        # Log slow queries
        if duration > 5.0:
            logger.warning(
                f"Slow <function_name> query executed in {duration:.2f}s "
                f"for env={env_name}, params=(...)"
            )
        else:
            logger.debug(
                f"<function_name> query executed in {duration:.2f}s"
            )
        
        return df
        
    except Exception as e:
        duration = time.perf_counter() - start_time
        logger.error(
            f"Error executing get_<function_name> for env={env_name}, "
            f"start_date={start_date}, end_date={end_date}, ...: {e}",
            exc_info=True
        )
        raise
```

### 4.4 Date Parameter Handling

**Automatic Detection**: If function parameters include `start_date` and/or `end_date`, code generator:
1. Imports `_normalize_dates()` static method from PDCRInfoReport
2. Calls `_normalize_dates(start_date, end_date)` to convert to ISO strings
3. Passes normalized values as SQL parameters

**Example**:
```python
if 'start_date' in params or 'end_date' in params:
    norm_start, norm_end = self._normalize_dates(start_date, end_date)
    params['start_date'] = norm_start
    params['end_date'] = norm_end
```

### 4.5 SQL Parameter Mapping

All WHERE clause parameters are automatically mapped to function parameters:

```python
params = {
    'env_name': env_name,
    'start_date': norm_start,  # (if normalized)
    'end_date': norm_end,        # (if normalized)
    'database_name': self._database_filter(database_name),  # (if applicable)
    ...  # other string/scalar params as-is
}
```

**Wildcard Handling**: String parameters ending in `_name` (e.g., `database_name`, `user_name`) are automatically filtered via `_database_filter()` to expand non-wildcarded inputs to `%<value>%`.

---

## 5. Integration with Existing Code

### 5.1 Module Organization

```
src/
├── __init__.py
├── connection.py          # TeradataConnection (unchanged)
├── reports.py             # PDCRInfoReport class (unchanged)
└── utilities.py           # NEW: Generated utility functions
```

### 5.2 Function Registration in PDCRInfoReport

**Option A** (Preferred): Mixins
```python
class PDCRInfoReport(UtilityMixin):
    """Extends PDCRInfoReport with generated utility methods."""
    pass
```

**Option B**: Separate namespace
```python
from src import utilities
utilities.get_tablespace_history(env_name='prod', ...)
```

**Decision**: Use Option B (separate utilities module) to keep code organization clean and avoid mixing generated code with handwritten PDCRInfoReport logic.

### 5.3 Backward Compatibility

Existing `PDCRInfoReport` methods (`get_tablespace_history`, `get_databasespace_history`, etc.) will be **refactored to call generated utilities**:

```python
# In src/reports.py
def get_tablespace_history(self, env_name, start_date=None, end_date=None, database_name="%"):
    """DEPRECATED: Use utilities.get_tablespace_history() instead."""
    from . import utilities
    return utilities.get_tablespace_history(
        env_name, start_date, end_date, database_name
    )
```

This ensures:
- Existing notebooks and code continue to work
- Gradual migration to new utilities module
- No breaking changes

---

## 6. Constitutional Compliance

### 6.1 Principle I: Code Quality Standards

✅ **Met**:
- Black formatting (88 char lines) enforced via pre-commit hook
- Type hints on all generated functions (verified by generator)
- Google-style docstrings with Args, Returns, Examples
- PEP 8 naming (snake_case functions, PascalCase classes)
- Flake8 linting (complexity ≤10, line length ≤127)

**Generator Validation**:
```python
# Check all generated functions
for func in generated_functions:
    assert isinstance(func.__annotations__, dict), "Type hints required"
    assert func.__doc__, "Docstring required"
    assert not any(line > 127 for line in func.__code__.co_code), "Line length check"
```

### 6.2 Principle II: Testing Discipline (NON-NEGOTIABLE)

✅ **Met**:
- Each generated function has corresponding unit test
- Mocked connections (no live DB dependency)
- Parameter wiring validation
- Slow-query logging verification (>5s)
- Target: ≥80% code coverage

**Test Template** (auto-generated):
```python
def test_get_<function_name>_params(report_with_engine):
    """Verify parameter wiring for <function_name>."""
    with patch('pandas.read_sql') as mock_read:
        mock_read.return_value = pd.DataFrame({...})
        
        result = report_with_engine.get_<function_name>(...)
        
        call_args = mock_read.call_args
        assert call_args[1]['params'] == {...}  # Validate params

def test_get_<function_name>_slow_warning(report_with_engine, caplog):
    """Verify slow-query warning for <function_name>."""
    with patch('time.perf_counter') as mock_timer:
        mock_timer.side_effect = [0.0, 6.5]  # 6.5 second query
        
        with patch('pandas.read_sql'):
            report_with_engine.get_<function_name>(...)
        
        assert "Slow <function_name> query" in caplog.text
        assert "6.50s" in caplog.text
```

### 6.3 Principle III: User Experience Consistency

✅ **Met**:
- Flexible date parameters (date objects or ISO strings)
- Consistent parameter naming across all functions
- Clear error messages with context (env, params, exceptions)
- Structured logging (DEBUG for normal, WARNING for slow, ERROR for failures)

### 6.4 Principle IV: Performance Requirements

✅ **Met**:
- Parameterized SQL queries (no string interpolation)
- SQLAlchemy context managers for connection cleanup
- Query result limiting (caller responsibility; documented)
- Timing instrumentation (perf_counter, logged for all queries)
- Slow-query warnings (>5s threshold, configurable)
- No N+1 query patterns in generated code

---

## 7. Implementation Plan

### Phase 1: Metadata Definition (1-2 hours)
1. Create `PDCRInfo_Columns.csv` with 5 existing table definitions
2. Validate CSV format (UTF-8, proper escaping, column presence)
3. Manual review and documentation

**Deliverables**:
- `docs/PDCRInfo_Columns.csv` with sample rows
- `docs/PDCRInfo_Columns_Schema.md` defining each column

### Phase 2: Code Generator Script (3-4 hours)
1. Create `scripts/generate_pdcr_utilities.py`
2. Implement CSV parser (pandas.read_csv with validation)
3. Implement code generation from template
4. Add validation checks (naming, syntax, line length)
5. Implement Black formatting and Flake8 linting on output
6. Test generator with sample CSV

**Deliverables**:
- `scripts/generate_pdcr_utilities.py` (executable)
- `scripts/generator_config.yaml` (template configuration)
- `GENERATOR.md` (usage documentation)

### Phase 3: Generated Utilities Module (2-3 hours)
1. Create `src/utilities.py` (empty boilerplate)
2. Run code generator to populate with functions
3. Verify generated code syntax
4. Add manual imports and helper functions as needed
5. Integration test with existing PDCRInfoReport

**Deliverables**:
- `src/utilities.py` (generated, 400+ lines)
- Updated `src/__init__.py` to export generated functions

### Phase 4: Test Generation (2-3 hours)
1. Extend code generator to produce unit tests
2. Generate `tests/test_utilities_generated.py`
3. Implement test runner to validate all generated tests pass
4. Coverage report to verify ≥80% threshold

**Deliverables**:
- `tests/test_utilities_generated.py` (auto-generated)
- Coverage report (pytest-cov)

### Phase 5: Documentation & Integration (2 hours)
1. Refactor existing PDCRInfoReport methods to call generated utilities
2. Update notebooks to use new utilities
3. Document CSV extension process in README
4. Add pre-commit hook to regenerate utilities on CSV changes

**Deliverables**:
- Updated `src/reports.py` (delegating methods)
- Updated `README.md` with extension instructions
- `.pre-commit-config.yaml` updates

### Phase 6: Validation & Review (1-2 hours)
1. Full test suite execution (unit + integration)
2. Constitution compliance checklist
3. Code review and approval
4. Documentation review

**Deliverables**:
- Test execution report
- Compliance checklist (signed off)
- Review comments addressed

---

## 8. Success Criteria

### Functional Requirements
- [ ] `PDCRInfo_Columns.csv` created with ≥5 table definitions
- [ ] Code generator script produces syntactically valid Python
- [ ] Generated functions all follow Black/Flake8 standards
- [ ] Generated functions work with mocked connections (no DB required)
- [ ] Generated functions produce DataFrames matching expected schema
- [ ] Parameter normalization and SQL injection prevention verified

### Quality Requirements
- [ ] Type hints on all generated functions (100% coverage)
- [ ] Google-style docstrings on all functions (100% coverage)
- [ ] Unit tests for all generated functions (100% coverage)
- [ ] Overall code coverage ≥80%
- [ ] All tests pass (pytest execution)
- [ ] No linting errors (Flake8 clean)
- [ ] Mypy type checking passes (strict mode)

### Compliance Requirements
- [ ] All 4 Constitutional Principles verified
- [ ] Performance instrumentation (timing + slow-query logging)
- [ ] Error handling with contextual information
- [ ] Parameterized SQL queries (no string interpolation)
- [ ] Context manager usage for connections
- [ ] No credentials or secrets in generated code

### Documentation Requirements
- [ ] `PDCRInfo_Columns_Schema.md` documents CSV format
- [ ] `GENERATOR.md` documents how to add new functions (extend CSV)
- [ ] README updated with utilities module usage
- [ ] Sample notebooks updated to use new utilities
- [ ] Changelog entry documenting this feature

---

## 9. Risk Mitigation

| Risk | Impact | Probability | Mitigation |
|---|---|---|---|
| CSV format errors break generator | HIGH | MEDIUM | Validate CSV schema before processing; detailed error messages |
| Generated code has SQL injection vulnerability | CRITICAL | LOW | Mandatory parameterized queries; code review; automated validation |
| Generated functions exceed line length | MEDIUM | MEDIUM | Generator includes line-breaking logic; Flake8 validation |
| Test coverage drops below 80% | MEDIUM | LOW | Auto-generate tests for each function; coverage report in CI |
| Performance overhead from wrapper functions | LOW | LOW | Measure with perf_counter; log slow queries for visibility |
| Backward compatibility breaks | HIGH | LOW | Delegate existing methods to generated utilities; notebooks tested |

---

## 10. Testing Strategy

### 10.1 Unit Tests (Auto-Generated)

**Per Function**:
1. Parameter wiring validation (correct params passed to SQL)
2. Return type validation (pandas.DataFrame returned)
3. Column schema validation (expected columns present)
4. Date normalization (date objects converted to ISO strings)
5. Wildcard expansion (non-wildcarded strings wrapped with %)
6. Slow-query warning logging (duration >5s triggers WARNING log)
7. Error handling (exception raises, logged with context)

### 10.2 Integration Tests (Manual)

1. Generated utilities called through PDCRInfoReport delegation
2. Utilities used in existing notebooks (teradata_*.ipynb)
3. Multiple calls in sequence (connection reuse, cleanup)
4. Mock connection lifecycle (open → query → close)

### 10.3 Code Quality Tests

1. Flake8 linting on all generated code
2. Black formatting check (88 char lines)
3. Mypy type checking (strict mode)
4. Bandit security scan (SQL injection detection)

---

## 11. Future Extensions

### Potential Enhancements
1. **CSV-based filtering**: Add filter templates to CSV (e.g., `CURRENTPERM > :min_perm`)
2. **Result caching**: Decorator for caching query results by parameters
3. **Aggregation functions**: Auto-generate summary functions (top N users, daily rollups)
4. **Dynamic documentation**: Generate HTML documentation from CSV metadata
5. **Schema discovery**: Introspect live Teradata to auto-populate CSV (advanced)

### Considerations for Scaling
- CSV row count grows → split into multiple files per domain
- Function count grows → consider lazy-loading utilities
- Performance instrumentation → consider centralized metrics collection

---

## 12. Appendix: Sample Generated Function

**Input CSV Row**:
```csv
tablespace_history,PDCRINFO.TableSpace_Hst,env_name;start_date;end_date;database_name,None;None;None;%,str;Optional[DateLike];Optional[DateLike];str,LogDate|DatabaseName|Tablename|AccountName|CURRENTPERM|PEAKPERM|CURRENTPERMSKEW|PEAKPERMSKEW,"WHERE LogDate BETWEEN :start_date AND :end_date AND DatabaseName LIKE :database_name",Returns table space usage history
```

**Generated Function Output** (formatted):
```python
def get_tablespace_history(
    env_name: str,
    start_date: Optional[DateLike] = None,
    end_date: Optional[DateLike] = None,
    database_name: str = "%",
) -> pd.DataFrame:
    """Retrieve PDCRINFO.TableSpace_Hst data.

    Returns table space usage history with detailed allocation metrics.

    Args:
        env_name: Environment name (e.g., 'test', 'prod').
        start_date: Inclusive start date; defaults to 1900-01-01.
        end_date: Inclusive end date; defaults to yesterday.
        database_name: Database name pattern; '%' matches all.

    Returns:
        DataFrame with columns: LogDate, DatabaseName, Tablename, 
        AccountName, CURRENTPERM, PEAKPERM, CURRENTPERMSKEW, PEAKPERMSKEW.

    Example:
        >>> df = get_tablespace_history(
        ...     env_name='prod',
        ...     start_date='2024-01-01',
        ...     end_date='2024-12-31',
        ...     database_name='MyDB'
        ... )
        >>> print(df.shape)
        (1000000, 8)

    Notes:
        Returns table space usage history with detailed allocation metrics.
    """
    from .reports import PDCRInfoReport
    
    # Normalize dates
    norm_start, norm_end = PDCRInfoReport._normalize_dates(
        start_date, end_date
    )
    db_filter = PDCRInfoReport._database_filter(database_name)
    
    # Build parameterized query
    query = text("""
        SELECT 
            LogDate,
            DatabaseName,
            Tablename,
            AccountName,
            CURRENTPERM,
            PEAKPERM,
            CURRENTPERMSKEW,
            PEAKPERMSKEW
        FROM PDCRINFO.TableSpace_Hst
        WHERE LogDate BETWEEN :start_date AND :end_date 
          AND DatabaseName LIKE :database_name
    """)
    
    logger.debug(
        f"Executing get_tablespace_history query for env={env_name}, "
        f"start_date={norm_start}, end_date={norm_end}"
    )
    
    start_time = time.perf_counter()
    try:
        from .connection import TeradataConnection
        conn_mgr = TeradataConnection()
        
        with conn_mgr.get_connection(env_name) as conn:
            df = pd.read_sql(
                query,
                conn,
                params={
                    'start_date': norm_start,
                    'end_date': norm_end,
                    'database_name': db_filter,
                }
            )
        
        duration = time.perf_counter() - start_time
        
        if duration > 5.0:
            logger.warning(
                f"Slow tablespace_history query executed in {duration:.2f}s "
                f"for env={env_name}, start_date={norm_start}, "
                f"end_date={norm_end}"
            )
        else:
            logger.debug(f"tablespace_history query executed in {duration:.2f}s")
        
        return df
        
    except Exception as e:
        duration = time.perf_counter() - start_time
        logger.error(
            f"Error executing get_tablespace_history for env={env_name}, "
            f"start_date={norm_start}, end_date={norm_end}, "
            f"database_name={db_filter}: {e}",
            exc_info=True
        )
        raise
```

---

## Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2026-01-17 | Specification | Initial specification for dynamic utility generation |

---

## Approval Sign-Off

| Role | Name | Date | Approved |
|------|------|------|----------|
| Architecture | Clyde Watts | 2026-01-17 | ☐ |
| Code Review | TBD | - | ☐ |
| QA | TBD | - | ☐ |

