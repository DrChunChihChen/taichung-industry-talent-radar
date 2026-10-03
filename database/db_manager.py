"""
Database Manager Module
Provides thread-safe connections, table initialization, and querying.
"""
import sqlite3
import pandas as pd
from typing import List, Dict, Any, Optional
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import DB_PATH, BASE_DIR

class DatabaseManager:
    def __init__(self, db_path=None):
        self.db_path = str(db_path or DB_PATH)

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self, schema_file: Optional[str] = None):
        """Initializes tables using schema.sql"""
        schema_path = schema_file or (BASE_DIR / "database" / "schema.sql")
        with open(schema_path, "r", encoding="utf-8") as f:
            ddl = f.read()
        with self.get_connection() as conn:
            conn.executescript(ddl)
            conn.commit()

    def execute(self, sql: str, params: tuple = ()) -> int:
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, params)
            conn.commit()
            return cur.rowcount

    def executemany(self, sql: str, params_list: List[tuple]) -> int:
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.executemany(sql, params_list)
            conn.commit()
            return cur.rowcount

    def fetch_all(self, sql: str, params: tuple = ()) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, params)
            rows = cur.fetchall()
            return [dict(r) for r in rows]

    def fetch_one(self, sql: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, params)
            row = cur.fetchone()
            return dict(row) if row else None

    def query_df(self, sql: str, params: tuple = ()) -> pd.DataFrame:
        with self.get_connection() as conn:
            return pd.read_sql_query(sql, conn, params=params)

    def write_df(self, df: pd.DataFrame, table_name: str, if_exists: str = "append", index: bool = False):
        with self.get_connection() as conn:
            df.to_sql(table_name, conn, if_exists=if_exists, index=index)

db = DatabaseManager()

if __name__ == "__main__":
    db.init_db()
    print("Database initialized successfully at:", DB_PATH)
