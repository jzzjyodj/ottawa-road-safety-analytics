"""Validate the DuckDB load of collisions_raw against known expected values."""
from src.database import get_connection

EXPECTED = {
    "row_count": 94_406,
    "col_count": 28,
    "year_min": 2017,
    "year_max": 2024,
    "year_distinct": 7,
    "id_unique": 94_406,
    "object_id_unique": 94_406,
    "geo_id_unique": 14_900,
    "coord_outliers": 72,
}


def _pass_fail(label, actual, expected):
    """Print a labelled PASS/FAIL line comparing actual vs expected."""
    status = "PASS" if actual == expected else "FAIL"
    print(f"  [{status}] {label}: {actual:,}  (expected {expected:,})")


def check_row_count(con):
    """Check that collisions_raw contains the expected number of rows."""
    print("1. Row count")
    actual = con.execute("SELECT COUNT(*) FROM collisions_raw").fetchone()[0]
    _pass_fail("row count", actual, EXPECTED["row_count"])


def check_column_count(con):
    """Check that collisions_raw contains the expected number of columns."""
    print("2. Column count")
    actual = len(con.execute("SELECT * FROM collisions_raw LIMIT 0").description)
    _pass_fail("column count", actual, EXPECTED["col_count"])


def check_year_range(con):
    """Check the min, max, and distinct count of Accident_Year."""
    print("3. Year range")
    row = con.execute("""
        SELECT MIN(Accident_Year), MAX(Accident_Year), COUNT(DISTINCT Accident_Year)
        FROM collisions_raw
    """).fetchone()
    year_min, year_max, year_distinct = row
    _pass_fail("year min", year_min, EXPECTED["year_min"])
    _pass_fail("year max", year_max, EXPECTED["year_max"])
    _pass_fail("distinct years", year_distinct, EXPECTED["year_distinct"])


def check_identifier_uniqueness(con):
    """Check unique counts for ID, ObjectId, and Geo_ID."""
    print("4. Identifier uniqueness")
    checks = [
        ("ID",       "ID",       "id_unique"),
        ("ObjectId", "ObjectId", "object_id_unique"),
        ("Geo_ID",   "Geo_ID",   "geo_id_unique"),
    ]
    for label, col, key in checks:
        actual = con.execute(
            f"SELECT COUNT(DISTINCT {col}) FROM collisions_raw"
        ).fetchone()[0]
        _pass_fail(f"{label} unique count", actual, EXPECTED[key])


def check_coordinate_outliers(con):
    """Count rows with coordinates outside Ottawa's rough bounding box or null."""
    print("5. Coordinate outliers")
    actual = con.execute("""
        SELECT COUNT(*) FROM collisions_raw
        WHERE Lat IS NULL
           OR Long IS NULL
           OR Lat  < 44.9 OR Lat  > 45.7
           OR Long < -76.4 OR Long > -75.2
    """).fetchone()[0]
    _pass_fail("coordinate outliers", actual, EXPECTED["coord_outliers"])


def main():
    """Run all schema checks against collisions_raw and print results."""
    con = get_connection()
    print("=== collisions_raw schema checks ===\n")
    check_row_count(con)
    check_column_count(con)
    check_year_range(con)
    check_identifier_uniqueness(con)
    check_coordinate_outliers(con)
    print("\n=== done ===")
    con.close()


if __name__ == "__main__":
    main()
