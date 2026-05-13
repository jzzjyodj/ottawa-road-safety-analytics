# Configuration: file paths, DuckDB database location, and environment settings.
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
INTERIM_DIR = DATA_DIR / "interim"
PROCESSED_DIR = DATA_DIR / "processed"
DB_PATH = PROCESSED_DIR / "ottawa_road_safety.duckdb"
RAW_CSV = RAW_DIR / "Traffic_Collision_Data.csv"
