"""
DuckDB Client for Analytics Queries
Embedded analytics database for fast computations on Parquet files
"""

import duckdb
from pathlib import Path
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

from app.config import settings


class DuckDBClient:
    """
    DuckDB client for analytical queries
    DuckDB runs in-process, no separate server needed
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize DuckDB connection
        
        Args:
            db_path: Path to DuckDB database file (None for in-memory)
        """
        self.db_path = db_path or settings.duckdb_path
        self._connection: Optional[duckdb.DuckDBPyConnection] = None
        self.artifacts_path = Path(settings.artifacts_path)
        
    def connect(self) -> duckdb.DuckDBPyConnection:
        """
        Get or create DuckDB connection
        Connection is reused across queries (thread-safe with read-only mode)
        """
        if self._connection is None:
            try:
                # Open in read-only mode (allows multiple readers)
                self._connection = duckdb.connect(
                    database=self.db_path,
                    read_only=True
                )
                print(f"[DuckDB] Connected to: {self.db_path}")
            except Exception as e:
                print(f"[DuckDB] Connection failed: {e}")
                # Fallback to in-memory database
                self._connection = duckdb.connect(database=":memory:")
                print("[DuckDB] Using in-memory database (fallback)")
        
        return self._connection
    
    def close(self) -> None:
        """Close DuckDB connection"""
        if self._connection is not None:
            self._connection.close()
            self._connection = None
            print("[DuckDB] Connection closed")
    
    @contextmanager
    def cursor(self):
        """
        Context manager for query execution
        
        Usage:
            with duckdb_client.cursor() as cursor:
                result = cursor.execute("SELECT * FROM programs").fetchall()
        """
        conn = self.connect()
        try:
            yield conn.cursor()
        finally:
            # Don't close connection (reuse it)
            pass
    
    def query(self, sql: str, parameters: Optional[tuple] = None) -> List[tuple]:
        """
        Execute SQL query and return all results
        
        Args:
            sql: SQL query string
            parameters: Query parameters (for parameterized queries)
            
        Returns:
            List of tuples (rows)
        """
        conn = self.connect()
        try:
            if parameters:
                result = conn.execute(sql, parameters)
            else:
                result = conn.execute(sql)
            return result.fetchall()
        except Exception as e:
            print(f"[DuckDB] Query failed: {e}")
            print(f"[DuckDB] SQL: {sql}")
            raise
    
    def query_df(self, sql: str, parameters: Optional[tuple] = None):
        """
        Execute SQL query and return results as pandas DataFrame
        
        Args:
            sql: SQL query string
            parameters: Query parameters
            
        Returns:
            pandas DataFrame
        """
        conn = self.connect()
        try:
            if parameters:
                result = conn.execute(sql, parameters)
            else:
                result = conn.execute(sql)
            return result.df()
        except Exception as e:
            print(f"[DuckDB] Query failed: {e}")
            print(f"[DuckDB] SQL: {sql}")
            raise
    
    def query_one(self, sql: str, parameters: Optional[tuple] = None) -> Optional[tuple]:
        """
        Execute SQL query and return first result
        
        Args:
            sql: SQL query string
            parameters: Query parameters
            
        Returns:
            Single tuple or None
        """
        conn = self.connect()
        try:
            if parameters:
                result = conn.execute(sql, parameters)
            else:
                result = conn.execute(sql)
            return result.fetchone()
        except Exception as e:
            print(f"[DuckDB] Query failed: {e}")
            raise
    
    def query_dict(self, sql: str, parameters: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """
        Execute SQL query and return results as list of dictionaries
        
        Args:
            sql: SQL query string
            parameters: Query parameters
            
        Returns:
            List of dictionaries (column: value)
        """
        df = self.query_df(sql, parameters)
        return df.to_dict('records')
    
    def check_table_exists(self, table_name: str) -> bool:
        """
        Check if table/view exists in DuckDB
        
        Args:
            table_name: Name of table to check
            
        Returns:
            True if table exists
        """
        try:
            sql = f"""
                SELECT COUNT(*) as cnt
                FROM information_schema.tables
                WHERE table_name = '{table_name}'
            """
            result = self.query_one(sql)
            return result[0] > 0 if result else False
        except:
            return False
    
    def get_table_info(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Get column information for a table
        
        Args:
            table_name: Name of table
            
        Returns:
            List of column information dicts
        """
        sql = f"DESCRIBE {table_name}"
        return self.query_dict(sql)
    
    def load_parquet(self, parquet_path: str, table_name: str) -> None:
        """
        Load Parquet file into DuckDB table (in-memory)
        Only works with writable connection
        
        Args:
            parquet_path: Path to Parquet file
            table_name: Name for the table
        """
        conn = self.connect()
        sql = f"CREATE TABLE {table_name} AS SELECT * FROM '{parquet_path}'"
        conn.execute(sql)
        print(f"[DuckDB] Loaded {parquet_path} into table {table_name}")
    
    def healthcheck(self) -> Dict[str, Any]:
        """
        Check DuckDB health and return status
        
        Returns:
            Dict with health status information
        """
        try:
            conn = self.connect()
            version = conn.execute("SELECT version()").fetchone()[0]
            
            # Check if key tables exist
            tables_exist = {
                "programs": self.check_table_exists("programs"),
                "fmr": self.check_table_exists("fmr"),
            }
            
            return {
                "status": "healthy",
                "version": version,
                "database_path": self.db_path,
                "tables": tables_exist,
                "all_tables_ready": all(tables_exist.values())
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "database_path": self.db_path
            }


# Global DuckDB client instance
duckdb_client = DuckDBClient()


def get_duckdb() -> DuckDBClient:
    """
    Dependency for FastAPI routes to get DuckDB client
    
    Usage:
        @app.get("/analytics")
        def analytics(duckdb: DuckDBClient = Depends(get_duckdb)):
            return duckdb.query("SELECT * FROM programs LIMIT 10")
    """
    return duckdb_client

