"""DuckDB connection factory."""
import duckdb
from src.config import DB_PATH


def get_connection(db_path=DB_PATH):
    """Return an open DuckDB connection to the given database path."""
    return duckdb.connect(str(db_path))
