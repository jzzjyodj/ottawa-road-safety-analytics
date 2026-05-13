"""Validate collisions_clean against expected values after preprocessing."""
import sys

from src.database import get_connection

EXPECTED = {
    "row_count":                  94_406,
    "col_count":                  37,
    "id_unique":                  94_406,
    "object_id_unique":           94_406,
    "num_of_vehicles_nulls":      168,
    "num_of_vehicles_missing":    168,
    "core_injury_count_missing":  9,
    "geo_valid_false":            72,
    "non_reportable":             2_563,
}

FILL_ZERO_COLS = [
    "num_of_pedestrians",
    "num_of_bicycles",
    "num_of_motorcycles",
    "num_of_injuries",
    "num_of_minimal",
    "num_of_minor",
    "num_of_major",
    "num_of_fatal",
]

CODED_COLS = [
    "classification_of_accident",
    "initial_impact_type",
    "light",
    "traffic_control",
    "road_1_surface_condition",
    "environment_condition_1",
]

_failed = False


def _pass_fail(label, actual, expected):
    """Print a PASS/FAIL line and set the global failure flag on mismatch."""
    global _failed
    status = "PASS" if actual == expected else "FAIL"
    if status == "FAIL":
        _failed = True
    print(f"  [{status}] {label}: {actual:,}  (expected {expected:,})")


def check_table_exists(con):
    """Check that collisions_clean is queryable."""
    global _failed
    print("1. Table exists")
    try:
        con.execute("SELECT 1 FROM collisions_clean LIMIT 1").fetchone()
        print("  [PASS] collisions_clean is queryable")
    except Exception as e:
        _failed = True
        print(f"  [FAIL] collisions_clean is not queryable: {e}")


def check_row_count(con):
    """Check that collisions_clean contains the expected number of rows."""
    print("2. Row count")
    actual = con.execute("SELECT COUNT(*) FROM collisions_clean").fetchone()[0]
    _pass_fail("row count", actual, EXPECTED["row_count"])


def check_column_count(con):
    """Check that collisions_clean contains the expected number of columns."""
    print("3. Column count")
    actual = len(con.execute("SELECT * FROM collisions_clean LIMIT 0").description)
    _pass_fail("column count", actual, EXPECTED["col_count"])


def check_identifier_uniqueness(con):
    """Check that id and object_id are each unique across all rows."""
    print("4. Identifier uniqueness")
    for label, col, key in [("id", "id", "id_unique"), ("object_id", "object_id", "object_id_unique")]:
        actual = con.execute(f"SELECT COUNT(DISTINCT {col}) FROM collisions_clean").fetchone()[0]
        _pass_fail(f"{label} unique count", actual, EXPECTED[key])


def check_raw_clean_row_parity(con):
    """Check that collisions_raw and collisions_clean have the same row count."""
    print("5. Raw and clean row count parity")
    raw = con.execute("SELECT COUNT(*) FROM collisions_raw").fetchone()[0]
    clean = con.execute("SELECT COUNT(*) FROM collisions_clean").fetchone()[0]
    _pass_fail("collisions_raw rows", raw, EXPECTED["row_count"])
    _pass_fail("collisions_clean rows", clean, EXPECTED["row_count"])


def check_filled_count_nulls(con):
    """Check that all FILL_ZERO_COLS have zero nulls in collisions_clean."""
    print("6. Filled count columns have zero nulls")
    for col in FILL_ZERO_COLS:
        actual = con.execute(
            f"SELECT COUNT(*) FROM collisions_clean WHERE {col} IS NULL"
        ).fetchone()[0]
        _pass_fail(f"{col} nulls", actual, 0)


def check_vehicles_not_filled(con):
    """Check that num_of_vehicles nulls were preserved (not filled with 0)."""
    print("7. num_of_vehicles nulls were NOT filled")
    actual = con.execute(
        "SELECT COUNT(*) FROM collisions_clean WHERE num_of_vehicles IS NULL"
    ).fetchone()[0]
    _pass_fail("num_of_vehicles null count", actual, EXPECTED["num_of_vehicles_nulls"])


def check_diagnostic_flags(con):
    """Check counts of num_of_vehicles_missing and core_injury_count_missing flags."""
    print("8. Diagnostic flag counts")
    veh = con.execute(
        "SELECT COUNT(*) FROM collisions_clean WHERE num_of_vehicles_missing = true"
    ).fetchone()[0]
    _pass_fail("num_of_vehicles_missing = true", veh, EXPECTED["num_of_vehicles_missing"])

    core = con.execute(
        "SELECT COUNT(*) FROM collisions_clean WHERE core_injury_count_missing = true"
    ).fetchone()[0]
    _pass_fail("core_injury_count_missing = true", core, EXPECTED["core_injury_count_missing"])


def check_geo_valid(con):
    """Check the count of rows where geo_valid is false."""
    print("9. geo_valid = False count")
    actual = con.execute(
        "SELECT COUNT(*) FROM collisions_clean WHERE geo_valid = false"
    ).fetchone()[0]
    _pass_fail("geo_valid=False rows", actual, EXPECTED["geo_valid_false"])


def check_non_reportable(con):
    """Check the count of Non-reportable rows after prefix stripping."""
    print("10. Non-reportable rows")
    actual = con.execute(
        "SELECT COUNT(*) FROM collisions_clean WHERE classification_of_accident = 'Non-reportable'"
    ).fetchone()[0]
    _pass_fail("Non-reportable rows", actual, EXPECTED["non_reportable"])


def check_no_coded_prefixes(con):
    """Check that no coded 'NN - ' prefixes remain in categorical columns."""
    global _failed
    print("11. No coded prefixes remain")
    for col in CODED_COLS:
        actual = con.execute(f"""
            SELECT COUNT(*) FROM collisions_clean
            WHERE regexp_matches({col}, '^\\d{{2}} - ')
        """).fetchone()[0]
        status = "PASS" if actual == 0 else "FAIL"
        if status == "FAIL":
            _failed = True
        print(f"  [{status}] {col}: {actual:,} rows with coded prefix remaining")


def main():
    """Run all schema checks against collisions_clean and exit 1 if any fail."""
    global _failed
    con = get_connection()
    print("=== collisions_clean schema checks ===\n")
    check_table_exists(con)
    check_row_count(con)
    check_column_count(con)
    check_identifier_uniqueness(con)
    check_raw_clean_row_parity(con)
    check_filled_count_nulls(con)
    check_vehicles_not_filled(con)
    check_diagnostic_flags(con)
    check_geo_valid(con)
    check_non_reportable(con)
    check_no_coded_prefixes(con)
    con.close()
    print("\n=== done ===")
    if _failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
