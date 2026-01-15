"""Report generation for Teradata PDCR data.

This module provides classes for generating various reports from
Teradata PDCR (Performance Data Collection and Reporting) data.
"""

import logging
from datetime import date, timedelta
from typing import Optional, Union

import pandas as pd
from sqlalchemy import text

from .connection import TeradataConnection

logger = logging.getLogger(__name__)

DateLike = Union[str, date]


class PDCRInfoReport:
    """Generates reports from DBC.DBCInfoV table.

    This class retrieves PDCR information including system metadata,
    configuration, and performance-related data.

    Args:
        config_path: Optional path to YAML configuration file.
            Defaults to 'td_env.yaml'.

    Example:
        >>> report = PDCRInfoReport()
        >>> df = report.get_dbcinfo('prod')
        >>> print(df.head())
    """

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the PDCR info report generator.

        Args:
            config_path: Optional path to YAML configuration file.
        """
        self.conn_mgr = TeradataConnection(config_path)

    @staticmethod
    def _normalize_dates(
        start_date: Optional[DateLike], end_date: Optional[DateLike]
    ) -> tuple[str, str]:
        """Normalize date inputs to ISO strings with sensible defaults."""
        start = start_date or date(1900, 1, 1)
        end = end_date or (date.today() - timedelta(days=1))

        if isinstance(start, str):
            start_value = start
        else:
            start_value = start.isoformat()

        if isinstance(end, str):
            end_value = end
        else:
            end_value = end.isoformat()

        return start_value, end_value

    @staticmethod
    def _database_filter(database_name: str) -> str:
        """Build a LIKE filter, honoring existing wildcards if provided."""
        name = database_name.strip() if database_name else "%"
        if "%" in name or "_" in name:
            return name
        return f"%{name}"

    def get_tablespace_history(
        self,
        env_name: str,
        start_date: Optional[DateLike] = None,
        end_date: Optional[DateLike] = None,
        database_name: str = "%",
    ) -> pd.DataFrame:
        """Retrieve TableSpace history from PDCRINFO.TableSpace_Hst.

        Args:
            env_name: Environment name (e.g., 'test', 'prod').
            start_date: Inclusive start date; defaults to 1900-01-01 when None.
            end_date: Inclusive end date; defaults to yesterday when None.
            database_name: Database name pattern; '%' by default.

        Returns:
            DataFrame with LogDate, DatabaseName, Tablename, AccountName,
            CURRENTPERM, PEAKPERM, CURRENTPERMSKEW, PEAKPERMSKEW.

        Example:
            >>> report = PDCRInfoReport()
            >>> df = report.get_tablespace_history('prod', '2024-01-01', '2024-01-31')
        """

        start_value, end_value = self._normalize_dates(start_date, end_date)
        db_filter = self._database_filter(database_name)

        query = """
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
        WHERE Logdate BETWEEN :start_date AND :end_date
          AND TRIM(DatabaseName) LIKE :database_name
        ORDER BY 1, 2, 3;
        """

        logger.info(
            "Query Text: %s", query
        )



        logger.info(
            "Fetching TableSpace history for %s between %s and %s",
            env_name,
            start_value,
            end_value,
        )

        with self.conn_mgr.get_connection(env_name) as engine:
            sql_text = text(query)
            params = {
                "start_date": start_value,
                "end_date": end_value,
                "database_name": db_filter,
            }
            logger.debug(f"Query parameters: {params}")
            return pd.read_sql(sql_text, engine, params=params)

    def get_databasespace_history(
        self,
        env_name: str,
        start_date: Optional[DateLike] = None,
        end_date: Optional[DateLike] = None,
        database_name: str = "%",
    ) -> pd.DataFrame:
        """Retrieve DatabaseSpace history from PDCRINFO.DatabaseSpace_Hst.

        Args:
            env_name: Environment name (e.g., 'test', 'prod').
            start_date: Inclusive start date; defaults to 1900-01-01 when None.
            end_date: Inclusive end date; defaults to yesterday when None.
            database_name: Database name pattern; '%' by default.

        Returns:
            DataFrame with LogDate, DatabaseName, AccountName, CURRENTPERM,
            PEAKPERM, MAXPERM, CURRENTPERMSKEW, PERMPCTUSED.

        Example:
            >>> report = PDCRInfoReport()
            >>> df = report.get_databasespace_history('prod', database_name='Sales%')
        """

        start_value, end_value = self._normalize_dates(start_date, end_date)
        db_filter = self._database_filter(database_name)

        query = """
        SELECT
            LogDate,
            DatabaseName,
            AccountName,
            CURRENTPERM,
            PEAKPERM,
            MAXPERM,
            CURRENTPERMSKEW,
            PERMPCTUSED
        FROM PDCRINFO.DatabaseSpace_Hst
        WHERE Logdate BETWEEN :start_date AND :end_date
          AND TRIM(DatabaseName) LIKE :database_name
        ORDER BY 1, 2, 3;
        """
        #print(query)
        logger.info(
            "Query Text: %s", query
        )


        logger.info(
            "Fetching DatabaseSpace history for %s between %s and %s",
            env_name,
            start_value,
            end_value,
        )

        with self.conn_mgr.get_connection(env_name) as engine:
            sql_text = text(query)
            params = {
                "start_date": start_value,
                "end_date": end_value,
                "database_name": db_filter,
            }
            logger.debug(f"Query parameters: {params}")
            return pd.read_sql(sql_text, engine, params=params)

    def get_spoolspace_history(
        self,
        env_name: str,
        start_date: Optional[DateLike] = None,
        end_date: Optional[DateLike] = None,
<<<<<<< Updated upstream
        user_name: str = "%",
        account_name: str = "%",
=======
        database_name: str = "%",
>>>>>>> Stashed changes
    ) -> pd.DataFrame:
        """Retrieve SpoolSpace history from PDCRINFO.SpoolSpace_Hst.

        Args:
            env_name: Environment name (e.g., 'test', 'prod').
            start_date: Inclusive start date; defaults to 1900-01-01 when None.
            end_date: Inclusive end date; defaults to yesterday when None.
<<<<<<< Updated upstream
            user_name: User name pattern; '%' by default.
            account_name: Account name pattern; '%' by default.


        Returns:
            DataFrame with LogDate, UserName, AccountName, CURRENTSPOOL,
=======
            database_name: Database name pattern; '%' by default.

        Returns:
            DataFrame with LogDate, DatabaseName, AccountName, CURRENTSPOOL,
>>>>>>> Stashed changes
            PEAKSPOOL, MAXSPOOL, CURRENTSPOOLSKEW.

        Example:
            >>> report = PDCRInfoReport()
<<<<<<< Updated upstream
            >>> df = report.get_spoolspace_history('prod', user_name='Sales%')
        """

        start_value, end_value = self._normalize_dates(start_date, end_date)
        user_filter = self._database_filter(user_name)
        account_filter = self._database_filter(account_name)

        query = """
        SELECT
            LogDate, UserName, AccountName, CURRENTSPOOL, PEAKSPOOL,
		MAXSPOOL, PEAKSPOOLSKEW, CURRENTTEMP, PEAKTEMP, MAXTEMP, PEAKTEMPSKEW
        FROM PDCRINFO.SpoolSpace_Hst
        WHERE Logdate BETWEEN :start_date AND :end_date
          AND TRIM(UserName) LIKE :user_name
          AND TRIM(AccountName) LIKE :account_name
=======
            >>> df = report.get_spoolspace_history('prod', database_name='Sales%')
        """

        start_value, end_value = self._normalize_dates(start_date, end_date)
        db_filter = self._database_filter(database_name)

        query = """
        SELECT
            LogDate,
            DatabaseName,
            AccountName,
            CURRENTSPOOL,
            PEAKSPOOL,
            MAXSPOOL,
            CURRENTSPOOLSKEW
        FROM PDCRINFO.SpoolSpace_Hst
        WHERE Logdate BETWEEN :start_date AND :end_date
          AND TRIM(DatabaseName) LIKE :database_name
>>>>>>> Stashed changes
        ORDER BY 1, 2, 3;
        """

        logger.info(
            "Query Text: %s", query
        )

        logger.info(
            "Fetching SpoolSpace history for %s between %s and %s",
            env_name,
            start_value,
            end_value,
        )

        with self.conn_mgr.get_connection(env_name) as engine:
            sql_text = text(query)
            params = {
                "start_date": start_value,
                "end_date": end_value,
<<<<<<< Updated upstream
                "user_name": user_filter,
                "account_name": account_filter,
=======
                "database_name": db_filter,
            }
            logger.debug(f"Query parameters: {params}")
            return pd.read_sql(sql_text, engine, params=params)

    def get_DBQLSummaryTable_History(
        self,
        env_name: str,
        start_date: Optional[DateLike] = None,
        end_date: Optional[DateLike] = None,
        user_name: str = "%",
    ) -> pd.DataFrame:
        """Retrieve DBQL Summary Table history from PDCRINFO.DBQLSummaryTbl_Hst.

        Args:
            env_name: Environment name (e.g., 'test', 'prod').
            start_date: Inclusive start date; defaults to 1900-01-01 when None.
            end_date: Inclusive end date; defaults to 2999-01-01 when None.
            user_name: User name pattern; '%' by default.

        Returns:
            DataFrame with LogDate, ProcID, CollectTimeStamp, UserID, ZoneID,
            UserName, AcctString, LogicalHostID, AppID, ClientID, ClientAddr,
            ProfileID, SessionID, QueryCount, ValueType, QuerySeconds,
            TotalIOCount, AMPCPUTime, ParserCPUTime, AMPCPUTimeNorm,
            ParserCPUTimeNorm, LowHist, HighHist, UsedIota, ReqPhysIO,
            ReqPhysIOKB, StartTime, StopTime, ProfileName, TotalIOInKB,
            and ExtraField2-9.

        Example:
            >>> report = PDCRInfoReport()
            >>> df = report.get_DBQLSummaryTable_History('prod', user_name='ETL%')
        """

        start_value, end_value = self._normalize_dates(start_date, end_date)
        
        if end_value == date(2999, 1, 1):
            end_value = date(2999, 1, 1)

        query = """
        SELECT
            LogDate, ProcID, CollectTimeStamp, UserID, ZoneID, UserName,
            AcctString, LogicalHostID, AppID, ClientID, ClientAddr, ProfileID,
            SessionID, QueryCount, ValueType, QuerySeconds, TotalIOCount,
            AMPCPUTime, ParserCPUTime, AMPCPUTimeNorm, ParserCPUTimeNorm,
            LowHist, HighHist, UsedIota, ReqPhysIO, ReqPhysIOKB, StartTime,
            StopTime, ProfileName, ExtraField1 AS TotalIOInKB, ExtraField2, ExtraField3,
            ExtraField4, ExtraField5, ExtraField6, ExtraField7, ExtraField8,
            ExtraField9
        FROM PDCRINFO.DBQLSummaryTbl_Hst
        WHERE LogDate BETWEEN :start_date AND :end_date
          AND TRIM(UserName) LIKE :user_name
        ORDER BY 1, 6;
        """

        logger.info(
            "Query Text: %s", query
        )

        logger.info(
            "Fetching DBQL Summary Table history for %s between %s and %s",
            env_name,
            start_value,
            end_value,
        )

        with self.conn_mgr.get_connection(env_name) as engine:
            sql_text = text(query)
            params = {
                "start_date": start_value,
                "end_date": end_value,
                "user_name": user_name,
>>>>>>> Stashed changes
            }
            logger.debug(f"Query parameters: {params}")
            return pd.read_sql(sql_text, engine, params=params)

    def get_dbcinfo(self, env_name: str) -> pd.DataFrame:
        """Retrieve PDCR info data from DBC.DBCInfoV.

        Args:
            env_name: Environment name (e.g., 'test', 'prod').

        Returns:
            DataFrame containing InfoKey and InfoData columns.

        Raises:
            TeradataConnectionError: If connection or query fails.

        Example:
            >>> report = PDCRInfoReport()
            >>> df = report.get_dbcinfo('prod')
            >>> info_keys = df['InfoKey'].unique()
        """

        query = """
        SELECT
            InfoKey,
            InfoData
        FROM DBC.DBCInfoV
        ORDER BY InfoKey;
        """

        logger.info(f"Executing PDCR info query on '{env_name}' environment")

        try:
            with self.conn_mgr.get_connection(env_name) as engine:
                df = pd.read_sql(query, engine)
                logger.info(f"Retrieved {len(df)} rows from DBC.DBCInfoV")
                return df

        except Exception as e:
            logger.error(f"Failed to retrieve PDCR info data: {e}")
            raise

    def close(self) -> None:
        """Close all database connections."""
        self.conn_mgr.close_all()
