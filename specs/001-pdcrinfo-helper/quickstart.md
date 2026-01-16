# Quickstart: PDCRINFO Helper Module

## Prerequisites
- Python 3.11 (>=3.8 supported)
- Dependencies installed: `pip install -r requirements.txt`
- Configure `td_env.yaml` from `td_env.yaml.template` with valid Teradata credentials and logmech settings.

## Basic Usage
```python
from src.pdcrinfo_helper import fetch_pdcr_table

# Fetch TableSpace history with defaults (start=1900-01-01, end=yesterday, pattern="%")
df = fetch_pdcr_table(
    env_name="prod",
    table_name="TableSpace_Hst",
)
print(df.head())

# Fetch DatabaseSpace history with filters
df_filtered = fetch_pdcr_table(
    env_name="prod",
    table_name="DatabaseSpace_Hst",
    start_date="2024-12-01",
    end_date="2024-12-31",
    database_pattern="Sales%",
)
print(df_filtered.head())
```

## Error Handling Examples
- Unknown environment: raises descriptive error listing available envs.
- Unsupported table: raises error listing allowed tables (`TableSpace_Hst`, `DatabaseSpace_Hst`).
- Invalid date range: raises validation error (start must be <= end).

## Testing
```bash
pytest tests/unit/test_pdcrinfo_helper.py
```
(Optional) integration tests require reachable Teradata environment and valid credentials.
