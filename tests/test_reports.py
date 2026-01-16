"""Tests for PDCRInfoReport query methods."""

from datetime import date
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from src.reports import PDCRInfoReport


class _DummyContext:
    """Simple context manager that returns a provided engine mock."""

    def __init__(self, engine: object) -> None:
        self.engine = engine

    def __enter__(self) -> object:  # pragma: no cover - trivial
        return self.engine

    def __exit__(self, exc_type, exc, tb) -> bool:  # pragma: no cover - trivial
        return False


@pytest.fixture()
def report_with_engine() -> tuple[PDCRInfoReport, object, Mock]:
    """Provide a PDCRInfoReport wired to a mocked connection manager."""

    engine = object()
    conn_mgr = Mock()
    conn_mgr.get_connection.return_value = _DummyContext(engine)

    report = PDCRInfoReport()
    report.conn_mgr = conn_mgr  # Inject mock to avoid real DB access
    return report, engine, conn_mgr


@patch("src.reports.pd.read_sql")
def test_get_tablespace_history_params(mock_read_sql: Mock, report_with_engine: tuple) -> None:
    report, engine, _ = report_with_engine
    mock_read_sql.return_value = pd.DataFrame()

    report.get_tablespace_history(
        env_name="test",
        start_date="2024-01-01",
        end_date="2024-01-02",
        database_name="Sales",
    )

    mock_read_sql.assert_called_once()
    _, call_kwargs = mock_read_sql.call_args
    assert call_kwargs["params"] == {
        "start_date": "2024-01-01",
        "end_date": "2024-01-02",
        "database_name": "%Sales",
    }
    assert call_kwargs["con"] == engine


@patch("src.reports.pd.read_sql")
def test_get_databasespace_history_params(mock_read_sql: Mock, report_with_engine: tuple) -> None:
    report, engine, _ = report_with_engine
    mock_read_sql.return_value = pd.DataFrame()

    report.get_databasespace_history(
        env_name="prod",
        start_date="2024-02-01",
        end_date="2024-02-05",
        database_name="Finance%",
    )

    mock_read_sql.assert_called_once()
    _, call_kwargs = mock_read_sql.call_args
    assert call_kwargs["params"] == {
        "start_date": "2024-02-01",
        "end_date": "2024-02-05",
        "database_name": "Finance%",
    }
    assert call_kwargs["con"] == engine


@patch("src.reports.pd.read_sql")
def test_get_spoolspace_history_params(mock_read_sql: Mock, report_with_engine: tuple) -> None:
    report, engine, _ = report_with_engine
    mock_read_sql.return_value = pd.DataFrame()

    report.get_spoolspace_history(
        env_name="test",
        start_date=date(2024, 3, 1),
        end_date=date(2024, 3, 2),
        user_name="etl_user",
        account_name="acct",
    )

    mock_read_sql.assert_called_once()
    _, call_kwargs = mock_read_sql.call_args
    assert call_kwargs["params"] == {
        "start_date": "2024-03-01",
        "end_date": "2024-03-02",
        "user_name": "%etl_user",
        "account_name": "%acct",
    }
    assert call_kwargs["con"] == engine


@patch("src.reports.time.perf_counter", side_effect=[0.0, 6.2])
@patch("src.reports.pd.read_sql")
def test_get_dbql_summary_slow_warning(
    mock_read_sql: Mock, mock_perf: Mock, report_with_engine: tuple, caplog
) -> None:
    report, engine, _ = report_with_engine
    caplog.set_level("WARNING")
    mock_read_sql.return_value = pd.DataFrame()

    report.get_DBQLSummaryTable_History(
        env_name="prod",
        start_date="2024-04-01",
        end_date="2024-04-02",
        user_name="etl%",
    )

    mock_read_sql.assert_called_once()
    _, call_kwargs = mock_read_sql.call_args
    assert call_kwargs["params"] == {
        "start_date": "2024-04-01",
        "end_date": "2024-04-02",
        "user_name": "etl%",
    }
    assert call_kwargs["con"] == engine
    assert any("Slow DBQL Summary query" in message for message in caplog.messages)