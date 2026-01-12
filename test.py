# Temporary script to create connection files
import os

# Create src/connection.py
connection_py = '''"""Teradata database connection management.

This module provides functionality to connect to Teradata databases
using configuration from YAML files.
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any
from contextlib import contextmanager

import yaml
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

logger = logging.getLogger(__name__)


class TeradataConnectionError(Exception):
	"""Exception raised for Teradata connection errors."""
	pass


class TeradataConnection:
	"""Manages Teradata database connections.
    
	Args:
		config_path: Path to the YAML configuration file.
			Defaults to 'td_env.yaml' in the project root.
    
	Example:
		>>> conn = TeradataConnection()
		>>> with conn.get_connection('test') as engine:
		...     df = pd.read_sql("SELECT * FROM table", engine)
	"""
    
	def __init__(self, config_path: Optional[str] = None):
		"""Initialize the connection manager.
        
		Args:
			config_path: Path to YAML config file. Defaults to 'td_env.yaml'.
		"""
		if config_path is None:
			config_path = Path(__file__).parent.parent / "td_env.yaml"
		else:
			config_path = Path(config_path)
        
		self.config_path = config_path
		self._config: Dict[str, Dict[str, Any]] = {}
		self._engines: Dict[str, Engine] = {}
		self._load_config()
    
	def _load_config(self) -> None:
		"""Load connection configuration from YAML file.
        
		Raises:
			TeradataConnectionError: If config file not found or invalid.
		"""
		if not self.config_path.exists():
			raise TeradataConnectionError(
				f"Configuration file not found: {self.config_path}\\n"
				f"Please create td_env.yaml from td_env.yaml.template"
			)
        
		try:
			with open(self.config_path, 'r') as f:
				self._config = yaml.safe_load(f)
            
			if not isinstance(self._config, dict):
				raise TeradataConnectionError(
					f"Invalid configuration format in {self.config_path}"
				)
            
			logger.info(f"Loaded configuration for: {list(self._config.keys())}")
        
		except yaml.YAMLError as e:
			raise TeradataConnectionError(
				f"Error parsing YAML configuration: {e}"
			)
		except Exception as e:
			raise TeradataConnectionError(
				f"Error loading configuration: {e}"
			)
    
	def _build_connection_string(self, env_name: str) -> str:
		"""Build Teradata connection string from configuration.
        
		Args:
			env_name: Environment name (e.g., 'test', 'prod').
        
		Returns:
			SQLAlchemy connection string.
        
		Raises:
			TeradataConnectionError: If environment not found in config.
		"""
		if env_name not in self._config:
			available = list(self._config.keys())
			raise TeradataConnectionError(
				f"Environment '{env_name}' not found in configuration. "
				f"Available: {available}"
			)
        
		config = self._config[env_name]
        
		# Required parameters
		required = ['host', 'username', 'password', 'database']
		missing = [param for param in required if param not in config]
		if missing:
			raise TeradataConnectionError(
				f"Missing required parameters for '{env_name}': {missing}"
			)
        
		# Build connection string
		host = config['host']
		username = config['username']
		password = config['password']
		database = config['database']
        
		# Optional parameters
		logmech = config.get('logmech', 'TD2')
        
		conn_string = (
			f"teradatasql://{username}:{password}@{host}/"
			f"{database}?LOGMECH={logmech}"
		)
        
		# Add optional parameters
		if 'tmode' in config:
			conn_string += f"&TMODE={config['tmode']}"
		if 'charset' in config:
			conn_string += f"&CHARSET={config['charset']}"
        
		return conn_string
    
	def get_engine(self, env_name: str, pool_size: int = 5) -> Engine:
		"""Get or create a SQLAlchemy engine for the environment.
        
		Args:
			env_name: Environment name (e.g., 'test', 'prod').
			pool_size: Connection pool size. Defaults to 5.
        
		Returns:
			SQLAlchemy Engine instance.
        
		Raises:
			TeradataConnectionError: If connection cannot be established.
		"""
		if env_name not in self._engines:
			try:
				conn_string = self._build_connection_string(env_name)
                
				engine = create_engine(
					conn_string,
					pool_size=pool_size,
					pool_pre_ping=True,  # Verify connections before using
					echo=False
				)
                
				# Test connection
				with engine.connect() as conn:
					conn.execute("SELECT 1")
                
				self._engines[env_name] = engine
				logger.info(f"Created connection to '{env_name}' environment")
            
			except Exception as e:
				raise TeradataConnectionError(
					f"Failed to connect to '{env_name}': {e}"
				)
        
		return self._engines[env_name]
    
	@contextmanager
	def get_connection(self, env_name: str):
		"""Context manager for database connections.
        
		Args:
			env_name: Environment name (e.g., 'test', 'prod').
        
		Yields:
			SQLAlchemy Engine instance.
        
		Example:
			>>> conn_mgr = TeradataConnection()
			>>> with conn_mgr.get_connection('test') as engine:
			...     df = pd.read_sql("SELECT * FROM table", engine)
		"""
		engine = self.get_engine(env_name)
		try:
			yield engine
		finally:
			# Connection returned to pool automatically
			pass
    
	def close_all(self) -> None:
		"""Close all database connections and dispose of engines."""
		for env_name, engine in self._engines.items():
			engine.dispose()
			logger.info(f"Closed connection to '{env_name}'")
		self._engines.clear()
    
	def list_environments(self) -> list:
		"""List available environment names from configuration.
        
		Returns:
			List of environment names.
		"""
		return list(self._config.keys())


def get_connection(env_name: str, config_path: Optional[str] = None) -> Engine:
	"""Convenience function to get a database connection.
    
	Args:
		env_name: Environment name (e.g., 'test', 'prod').
		config_path: Optional path to config file.
    
	Returns:
		SQLAlchemy Engine instance.
    
	Example:
		>>> engine = get_connection('test')
		>>> df = pd.read_sql("SELECT * FROM table", engine)
	"""
	conn_mgr = TeradataConnection(config_path)
	return conn_mgr.get_engine(env_name)
'''

with open('src/connection.py', 'w', encoding='utf-8') as f:
	f.write(connection_py)
print("Created src/connection.py")

# Create td_env.yaml.template
template = """# Teradata Environment Configuration Template
# Copy this file to td_env.yaml and fill in your credentials
# DO NOT commit td_env.yaml to git (it's in .gitignore)

test:
  host: "test-teradata-server.company.com"
  username: "your_username"
  password: "your_password"
  database: "test_database"
  logmech: "TD2"  # TD2, LDAP, etc.
  tmode: "ANSI"  # ANSI or TERA
  charset: "UTF8"

prod:
  host: "prod-teradata-server.company.com"
  username: "your_username"
  password: "your_password"
  database: "prod_database"
  logmech: "TD2"
  tmode: "ANSI"
  charset: "UTF8"
"""

with open('td_env.yaml.template', 'w', encoding='utf-8') as f:
	f.write(template)
print("Created td_env.yaml.template")

print("\\nAll files created successfully!")