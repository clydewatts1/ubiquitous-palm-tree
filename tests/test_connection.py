"""Tests for Teradata connection management."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
import yaml

from src.connection import (
    TeradataConnection,
    TeradataConnectionError,
    get_connection,
)


@pytest.fixture
def sample_config():
    """Sample configuration for testing."""
    return {
        "test": {
            "host": "test-server.com",
            "username": "testuser",
            "password": "testpass",
            "database": "testdb",
            "logmech": "TD2",
            "tmode": "ANSI",
            "charset": "UTF8",
        },
        "prod": {
            "host": "prod-server.com",
            "username": "produser",
            "password": "prodpass",
            "database": "proddb",
            "logmech": "LDAP",
        },
    }


@pytest.fixture
def temp_config_file(tmp_path, sample_config):
    """Create a temporary config file."""
    config_file = tmp_path / "td_env.yaml"
    with open(config_file, "w") as f:
        yaml.dump(sample_config, f)
    return config_file


class TestTeradataConnection:
    """Test cases for TeradataConnection class."""

    def test_init_with_missing_config(self, tmp_path):
        """Test initialization with missing config file."""
        missing_file = tmp_path / "missing.yaml"
        with pytest.raises(
            TeradataConnectionError, match="Configuration file not found"
        ):
            TeradataConnection(str(missing_file))

    def test_init_with_valid_config(self, temp_config_file):
        """Test initialization with valid config file."""
        conn = TeradataConnection(str(temp_config_file))
        assert conn.config_path == temp_config_file
        assert "test" in conn._config
        assert "prod" in conn._config

    def test_list_environments(self, temp_config_file):
        """Test listing available environments."""
        conn = TeradataConnection(str(temp_config_file))
        envs = conn.list_environments()
        assert "test" in envs
        assert "prod" in envs
        assert len(envs) == 2

    def test_build_connection_string_success(self, temp_config_file):
        """Test building connection string successfully."""
        conn = TeradataConnection(str(temp_config_file))
        conn_str = conn._build_connection_string("test")

        assert "teradatasql://" in conn_str
        assert "testuser" in conn_str
        assert "test-server.com" in conn_str
        assert "testdb" in conn_str
        assert "LOGMECH=TD2" in conn_str
        assert "TMODE=ANSI" in conn_str

    def test_build_connection_string_missing_env(self, temp_config_file):
        """Test building connection string with missing environment."""
        conn = TeradataConnection(str(temp_config_file))
        with pytest.raises(TeradataConnectionError, match="not found in configuration"):
            conn._build_connection_string("nonexistent")

    def test_build_connection_string_missing_params(self, tmp_path):
        """Test building connection string with missing required parameters."""
        incomplete_config = {
            "test": {
                "host": "test-server.com",
                "username": "testuser",
                # Missing password and database
            }
        }
        config_file = tmp_path / "incomplete.yaml"
        with open(config_file, "w") as f:
            yaml.dump(incomplete_config, f)

        conn = TeradataConnection(str(config_file))
        with pytest.raises(
            TeradataConnectionError, match="Missing required parameters"
        ):
            conn._build_connection_string("test")

    @patch("src.connection.create_engine")
    def test_get_engine_success(self, mock_create_engine, temp_config_file):
        """Test getting engine successfully."""
        # Mock engine and connection
        mock_engine = Mock()
        mock_conn = Mock()
        mock_engine.connect.return_value.__enter__ = Mock(return_value=mock_conn)
        mock_engine.connect.return_value.__exit__ = Mock(return_value=False)
        mock_create_engine.return_value = mock_engine

        conn = TeradataConnection(str(temp_config_file))
        engine = conn.get_engine("test")

        assert engine == mock_engine
        assert "test" in conn._engines
        mock_create_engine.assert_called_once()

    @patch("src.connection.create_engine")
    def test_get_engine_cached(self, mock_create_engine, temp_config_file):
        """Test that engine is cached after first creation."""
        mock_engine = Mock()
        mock_conn = Mock()
        mock_engine.connect.return_value.__enter__ = Mock(return_value=mock_conn)
        mock_engine.connect.return_value.__exit__ = Mock(return_value=False)
        mock_create_engine.return_value = mock_engine

        conn = TeradataConnection(str(temp_config_file))
        engine1 = conn.get_engine("test")
        engine2 = conn.get_engine("test")

        assert engine1 == engine2
        # Should only create engine once
        mock_create_engine.assert_called_once()

    @patch("src.connection.create_engine")
    def test_get_connection_context_manager(self, mock_create_engine, temp_config_file):
        """Test using connection as context manager."""
        mock_engine = Mock()
        mock_conn = Mock()
        mock_engine.connect.return_value.__enter__ = Mock(return_value=mock_conn)
        mock_engine.connect.return_value.__exit__ = Mock(return_value=False)
        mock_create_engine.return_value = mock_engine

        conn = TeradataConnection(str(temp_config_file))

        with conn.get_connection("test") as engine:
            assert engine == mock_engine

    @patch("src.connection.create_engine")
    def test_close_all(self, mock_create_engine, temp_config_file):
        """Test closing all connections."""
        mock_engine = Mock()
        mock_conn = Mock()
        mock_engine.connect.return_value.__enter__ = Mock(return_value=mock_conn)
        mock_engine.connect.return_value.__exit__ = Mock(return_value=False)
        mock_create_engine.return_value = mock_engine

        conn = TeradataConnection(str(temp_config_file))
        conn.get_engine("test")
        conn.get_engine("prod")

        assert len(conn._engines) == 2

        conn.close_all()

        assert len(conn._engines) == 0
        assert mock_engine.dispose.call_count == 2

    def test_invalid_yaml(self, tmp_path):
        """Test handling of invalid YAML file."""
        invalid_file = tmp_path / "invalid.yaml"
        with open(invalid_file, "w") as f:
            f.write("invalid: yaml: content: [")

        with pytest.raises(TeradataConnectionError, match="Error parsing YAML"):
            TeradataConnection(str(invalid_file))


@patch("src.connection.TeradataConnection")
def test_get_connection_convenience_function(mock_conn_class):
    """Test the convenience function."""
    mock_instance = Mock()
    mock_engine = Mock()
    mock_instance.get_engine.return_value = mock_engine
    mock_conn_class.return_value = mock_instance

    engine = get_connection("test", "/path/to/config.yaml")

    mock_conn_class.assert_called_once_with("/path/to/config.yaml")
    mock_instance.get_engine.assert_called_once_with("test")
    assert engine == mock_engine
