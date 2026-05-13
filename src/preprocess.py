"""Apply cleaning rules to collisions_raw and write collisions_clean to DuckDB."""
import pandas as pd

from src.config import DB_PATH
from src.database import get_connection

RENAME_MAP = {
    "X":                          "x",
    "Y":                          "y",
    "X_Coordinate":               "x_coordinate",
    "Y_Coordinate":               "y_coordinate",
    "ID":                         "id",
    "Geo_ID":                     "geo_id",
    "Accident_Year":              "accident_year",
    "Accident_Date":              "accident_date",
    "Location":                   "location",
    "Classification_Of_Accident": "classification_of_accident",
    "Initial_Impact_Type":        "initial_impact_type",
    "Road_1_Surface_Condition":   "road_1_surface_condition",
    "Environment_Condition_1":    "environment_condition_1",
    "Light":                      "light",
    "Traffic_Control":            "traffic_control",
    "Max_injury":                 "max_injury",
    "Lat":                        "lat",
    "Long":                       "long",
    "ObjectId":                   "object_id",
}

CODED_COLS = [
    "classification_of_accident",
    "initial_impact_type",
    "light",
    "traffic_control",
    "road_1_surface_condition",
    "environment_condition_1",
]

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

LAT_MIN, LAT_MAX = 44.9, 45.7
LON_MIN, LON_MAX = -76.4, -75.2


def load_raw(con) -> pd.DataFrame:
    """Load collisions_raw from DuckDB into a pandas DataFrame."""
    return con.execute("SELECT * FROM collisions_raw").df()


def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Rename source columns to snake_case using RENAME_MAP."""
    return df.rename(columns=RENAME_MAP)


def strip_code_prefixes(df: pd.DataFrame) -> pd.DataFrame:
    """Remove 'NN - ' coded prefix from categorical columns. Nulls are preserved."""
    df = df.copy()
    for col in CODED_COLS:
        df[col] = df[col].str.replace(r"^\d{2}\s*-\s*", "", regex=True)
    return df


def derive_date_fields(df: pd.DataFrame) -> pd.DataFrame:
    """Add accident_month and accident_day_of_week derived from accident_date."""
    df = df.copy()
    df["accident_date"] = pd.to_datetime(df["accident_date"], errors="coerce")
    df["accident_month"] = df["accident_date"].dt.month
    df["accident_day_of_week"] = df["accident_date"].dt.day_name()
    return df


def add_diagnostic_flags(df: pd.DataFrame) -> pd.DataFrame:
    """Flag rows with suspicious nulls before any filling occurs."""
    df = df.copy()
    df["num_of_vehicles_missing"] = df["num_of_vehicles"].isna()
    is_injury_class = df["classification_of_accident"].isin(["Fatal injury", "Non-fatal injury"])
    core_null = df["num_of_vehicles"].isna() | df["num_of_injuries"].isna()
    df["core_injury_count_missing"] = is_injury_class & core_null
    return df


def fill_sparse_counts(df: pd.DataFrame) -> pd.DataFrame:
    """Fill sparse count columns with 0. num_of_vehicles is not filled."""
    df = df.copy()
    df[FILL_ZERO_COLS] = df[FILL_ZERO_COLS].fillna(0).astype(int)
    return df


def add_boolean_flags(df: pd.DataFrame) -> pd.DataFrame:
    """Add geo_valid, involves_active_transport, is_fatal, is_non_fatal_injury, is_property_damage_only."""
    df = df.copy()
    df["geo_valid"] = (
        df["lat"].notna()
        & df["long"].notna()
        & (df["lat"] != 0.0)
        & (df["long"] != 0.0)
        & df["lat"].between(LAT_MIN, LAT_MAX)
        & df["long"].between(LON_MIN, LON_MAX)
    )
    df["involves_active_transport"] = (
        (df["num_of_pedestrians"] > 0) | (df["num_of_bicycles"] > 0)
    )
    df["is_fatal"] = df["classification_of_accident"] == "Fatal injury"
    df["is_non_fatal_injury"] = df["classification_of_accident"] == "Non-fatal injury"
    df["is_property_damage_only"] = df["classification_of_accident"] == "P.D. only"
    return df


def write_clean(df: pd.DataFrame, con) -> None:
    """Write the cleaned DataFrame to DuckDB as collisions_clean."""
    con.register("df_clean_temp", df)
    con.execute("""
        CREATE OR REPLACE TABLE collisions_clean AS
        SELECT * FROM df_clean_temp
    """)
    con.unregister("df_clean_temp")


def print_validation(df_raw: pd.DataFrame, df_clean: pd.DataFrame) -> None:
    """Print a concise validation summary comparing raw and clean row counts."""
    print("=== preprocess validation ===")
    print(f"  collisions_raw rows        : {len(df_raw):,}")
    print(f"  collisions_clean rows      : {len(df_clean):,}")
    print(f"  collisions_clean cols      : {len(df_clean.columns)}")
    print(f"  num_of_vehicles_missing    : {df_clean['num_of_vehicles_missing'].sum():,}  (expected 168)")
    print(f"  core_injury_count_missing  : {df_clean['core_injury_count_missing'].sum():,}  (expected 9)")
    print(f"  geo_valid=False            : {(~df_clean['geo_valid']).sum():,}  (expected 72)")
    non_reportable = (df_clean["classification_of_accident"] == "Non-reportable").sum()
    print(f"  Non-reportable rows        : {non_reportable:,}  (expected 2,563)")
    print("=== done ===")


def build_collisions_clean(con) -> pd.DataFrame:
    """Load collisions_raw, apply all cleaning rules in order, and return the cleaned DataFrame."""
    df_raw = load_raw(con)
    df = rename_columns(df_raw)
    df = strip_code_prefixes(df)
    df = derive_date_fields(df)
    df = add_diagnostic_flags(df)
    df = fill_sparse_counts(df)
    df = add_boolean_flags(df)
    write_clean(df, con)
    print_validation(df_raw, df)
    return df


def main():
    """Run the full preprocessing pipeline and write collisions_clean to DuckDB."""
    con = get_connection()
    build_collisions_clean(con)
    con.close()


if __name__ == "__main__":
    main()
