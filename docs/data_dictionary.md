# Data Dictionary

## Purpose

This document describes both the raw and cleaned versions of the City of Ottawa Traffic
Collision dataset. `collisions_raw` preserves the source CSV exactly. `collisions_clean`
is the preprocessed analysis-ready table produced by `src/preprocess.py`.

---

## Source Dataset

| Property | Value |
|---|---|
| Raw file | `data/raw/Traffic_Collision_Data.csv` |
| DuckDB database | `data/processed/ottawa_road_safety.duckdb` |
| Raw table | `collisions_raw` — 94,406 rows, 28 columns |
| Clean table | `collisions_clean` — 94,406 rows, 37 columns |
| Row meaning | Each row represents one reported traffic collision in Ottawa |
| Year range | 2017–2024 (7 distinct years; 2023 is absent) |

Source: City of Ottawa Open Data — Traffic Collision Data.
See `docs/data_sources.md` for download link and license.

---

## Table Naming Convention

| Table | Status | Description |
|---|---|---|
| `collisions_raw` | Implemented | Source-loaded table. Original column names, values, nulls, and structure preserved exactly as in the CSV. Never modified. |
| `collisions_clean` | Implemented | Analysis-ready table derived from `collisions_raw` by `src/preprocess.py`. Applies renaming, prefix stripping, date derivation, null filling, diagnostic flags, and boolean helpers. |

---

## `collisions_raw` Column Dictionary

All columns nullable. Types as inferred by DuckDB `read_csv_auto`.

| Column | DuckDB Type | Description | Notes |
|---|---|---|---|
| X | DOUBLE | Web Mercator easting (EPSG:3857) | Redundant; use `Lat`/`Long` for spatial work |
| Y | DOUBLE | Web Mercator northing (EPSG:3857) | Redundant; use `Lat`/`Long` for spatial work |
| X_Coordinate | DOUBLE | Projected easting, likely NAD83 / MTM zone 9 | Redundant |
| Y_Coordinate | DOUBLE | Projected northing, likely NAD83 / MTM zone 9 | Redundant |
| ID | VARCHAR | Unique collision identifier (`YYYY--NNN`) | 94,406 unique; suitable as primary key |
| Geo_ID | VARCHAR | Location/intersection reference code | 14,900 unique values — not a row identifier; 2,076 nulls |
| Accident_Year | BIGINT | Year the collision occurred | Range 2017–2024; 2023 absent; 0 nulls |
| Accident_Date | DATE | Date the collision occurred | Inferred as DATE by DuckDB from `M/D/YYYY` string |
| Location | VARCHAR | Human-readable intersection description | 2,076 nulls; shares null rows with `Geo_ID` |
| Classification_Of_Accident | VARCHAR | Collision severity classification | Coded prefix `NN - Description`; 4 distinct values |
| Initial_Impact_Type | VARCHAR | First point of contact | Coded prefix; 8 distinct values; 12 nulls |
| Road_1_Surface_Condition | VARCHAR | Road surface at time of collision | Coded prefix; 11 distinct values; 1 null |
| Environment_Condition_1 | VARCHAR | Weather/environment condition | Coded prefix; 9 distinct values; 13 nulls |
| Light | VARCHAR | Lighting condition | Coded prefix; 6 distinct values; 14 nulls |
| Traffic_Control | VARCHAR | Traffic control device present | Coded prefix; 14 distinct values; 30 nulls |
| num_of_vehicles | DOUBLE | Number of vehicles involved | 168 nulls (0.18%); unexplained — not filled |
| num_of_pedestrians | DOUBLE | Number of pedestrians involved | 92,575 nulls (98%); sparse by design |
| num_of_bicycles | DOUBLE | Number of bicycles involved | 92,741 nulls (98%); sparse by design |
| num_of_motorcycles | DOUBLE | Number of motorcycles involved | 93,615 nulls (99%); sparse by design |
| Max_injury | VARCHAR | Most severe injury in the collision | 79,241 nulls; null on P.D. only and Non-reportable rows |
| num_of_injuries | DOUBLE | Total persons injured | 79,183 nulls; null on non-injury rows |
| num_of_minimal | DOUBLE | Persons with minimal injuries | 87,816 nulls |
| num_of_minor | DOUBLE | Persons with minor injuries | 85,750 nulls |
| num_of_major | DOUBLE | Persons with major injuries | 93,589 nulls |
| num_of_fatal | DOUBLE | Fatalities | 94,237 nulls (99.8%) |
| Lat | DOUBLE | Latitude, WGS84 | 0 nulls; min 0.0 (invalid placeholder); 72 outliers |
| Long | DOUBLE | Longitude, WGS84 | 0 nulls; range -79.24 to -75.26 |
| ObjectId | BIGINT | Sequential source system integer | 94,406 unique; suitable as primary key |

---

## `collisions_clean` Column Dictionary

Produced by `src/preprocess.py`. 37 columns: 28 renamed from raw + 9 derived.
All columns nullable unless noted. Types as stored in DuckDB.

| column_name | type | description | notes |
|---|---|---|---|
| x | DOUBLE | Web Mercator easting | Renamed from `X` |
| y | DOUBLE | Web Mercator northing | Renamed from `Y` |
| x_coordinate | DOUBLE | Projected easting | Renamed from `X_Coordinate` |
| y_coordinate | DOUBLE | Projected northing | Renamed from `Y_Coordinate` |
| id | VARCHAR | Unique collision identifier (`YYYY--NNN`) | Renamed from `ID`; 94,406 unique |
| geo_id | VARCHAR | Location/intersection reference code | Renamed from `Geo_ID`; 2,076 nulls |
| accident_year | BIGINT | Year the collision occurred | Retained from raw; range 2017–2024 |
| accident_date | TIMESTAMP | Date the collision occurred | Renamed from `Accident_Date`; source was DATE, stored as TIMESTAMP |
| location | VARCHAR | Human-readable intersection description | Renamed from `Location`; 2,076 nulls |
| classification_of_accident | VARCHAR | Collision severity — prefix stripped | Renamed + cleaned; values: `P.D. only`, `Non-fatal injury`, `Non-reportable`, `Fatal injury` |
| initial_impact_type | VARCHAR | First point of contact — prefix stripped | Renamed + cleaned; 12 nulls |
| road_1_surface_condition | VARCHAR | Road surface — prefix stripped | Renamed + cleaned; 1 null |
| environment_condition_1 | VARCHAR | Weather/environment — prefix stripped | Renamed + cleaned; 13 nulls |
| light | VARCHAR | Lighting condition — prefix stripped | Renamed + cleaned; 14 nulls |
| traffic_control | VARCHAR | Traffic control device — prefix stripped | Renamed + cleaned; 30 nulls |
| num_of_vehicles | BIGINT | Number of vehicles involved | 168 nulls preserved — not filled |
| num_of_pedestrians | BIGINT | Number of pedestrians involved | Filled: null → 0 |
| num_of_bicycles | BIGINT | Number of bicycles involved | Filled: null → 0 |
| num_of_motorcycles | BIGINT | Number of motorcycles involved | Filled: null → 0 |
| max_injury | VARCHAR | Most severe injury in the collision | Renamed from `Max_injury`; nulls preserved |
| num_of_injuries | BIGINT | Total persons injured | Filled: null → 0 |
| num_of_minimal | BIGINT | Persons with minimal injuries | Filled: null → 0 |
| num_of_minor | BIGINT | Persons with minor injuries | Filled: null → 0 |
| num_of_major | BIGINT | Persons with major injuries | Filled: null → 0 |
| num_of_fatal | BIGINT | Fatalities | Filled: null → 0 |
| lat | DOUBLE | Latitude, WGS84 | Renamed from `Lat`; 72 rows outside Ottawa bbox |
| long | DOUBLE | Longitude, WGS84 | Renamed from `Long` |
| object_id | BIGINT | Sequential source system integer | Renamed from `ObjectId`; 94,406 unique |
| accident_month | INTEGER | Month of collision (1–12) | Derived from `accident_date` |
| accident_day_of_week | VARCHAR | Day of week (`Monday`…`Sunday`) | Derived from `accident_date` |
| num_of_vehicles_missing | BOOLEAN | True when `num_of_vehicles` is null | Diagnostic flag; 168 true rows |
| core_injury_count_missing | BOOLEAN | True on injury-classified rows missing `num_of_vehicles` or `num_of_injuries` | Diagnostic flag; 9 true rows — genuine recording errors |
| geo_valid | BOOLEAN | True if coordinates are non-null, non-zero, and within Ottawa bounding box | 72 false rows; use to filter before spatial analysis |
| involves_active_transport | BOOLEAN | True if `num_of_pedestrians > 0` or `num_of_bicycles > 0` | Evaluated after zero-fill |
| is_fatal | BOOLEAN | True if `classification_of_accident == 'Fatal injury'` | 170 true rows |
| is_non_fatal_injury | BOOLEAN | True if `classification_of_accident == 'Non-fatal injury'` | 15,002 true rows |
| is_property_damage_only | BOOLEAN | True if `classification_of_accident == 'P.D. only'` | 76,671 true rows |

---

## Data Quality Notes

- `id` and `object_id` are each unique across all 94,406 rows with 0 nulls. Either is a valid primary key.
- `geo_id` is a location/intersection code shared across rows, not a row identifier. 2,076 nulls.
- Six categorical columns used `NN - Description` coded prefixes in raw; all stripped in `collisions_clean`. Verified by `src/clean_schema_checks.py`.
- `num_of_vehicles` has 168 unexplained nulls; not filled in `collisions_clean`. Use `num_of_vehicles_missing` to exclude these rows from count-based analysis.
- 9 rows (`core_injury_count_missing = True`) are injury-classified collisions missing core count fields. Retained in the table; should be excluded from injury-count aggregations.
- 72 rows have coordinates outside the Ottawa bounding box (`geo_valid = False`), including rows with `lat = 0.0`. Filter on `geo_valid = True` before any spatial analysis.
- `accident_date` arrives as DATE from `collisions_raw` and is stored as TIMESTAMP in `collisions_clean`.
- 2023 is entirely absent from the dataset. Any year-over-year analysis must account for this gap.
