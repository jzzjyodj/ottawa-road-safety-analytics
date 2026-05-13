"""Load the raw City of Ottawa Traffic Collision CSV into DuckDB as collisions_raw."""
from src.config import RAW_CSV
from src.database import get_connection


def load_collisions_raw():
    """Create or replace collisions_raw from the raw CSV, preserving all data as-is."""
    if not RAW_CSV.exists():
        raise FileNotFoundError(f"Raw CSV not found: {RAW_CSV}")

    con = get_connection()

    con.execute(f"""
        CREATE OR REPLACE TABLE collisions_raw AS
        SELECT * FROM read_csv_auto('{RAW_CSV.as_posix()}', header=true, all_varchar=false)
    """)

    row_count = con.execute("SELECT COUNT(*) FROM collisions_raw").fetchone()[0]
    col_count = len(con.execute("SELECT * FROM collisions_raw LIMIT 0").description)
    describe = con.execute("DESCRIBE collisions_raw").df()

    print(f"collisions_raw loaded: {row_count:,} rows, {col_count} columns")
    print("\nDESCRIBE collisions_raw:")
    print(describe.to_string(index=False))

    con.close()
    return row_count, col_count, describe


if __name__ == "__main__":
    load_collisions_raw()
