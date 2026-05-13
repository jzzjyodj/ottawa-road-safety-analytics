# Schema Exploration Results

This document summarizes the findings from Day 1–2 schema exploration and preprocessing
of the City of Ottawa Traffic Collision dataset. All values below are confirmed by
`src/schema_checks.py` and `src/clean_schema_checks.py`.

---

## Raw Schema Summary

- The source CSV (`data/raw/Traffic_Collision_Data.csv`) contains **94,406 rows and 28 columns**,
  covering collision records from 2017 to 2024. 2023 is entirely absent from the data with no
  explanation in the source documentation.
- Each row represents one reported traffic collision. `ID` (format `YYYY--NNN`) and `ObjectId`
  are both fully unique with 0 nulls and serve as reliable row-level identifiers. `Geo_ID` is a
  shared intersection/segment code (14,900 unique values) — not a row identifier.
- The dataset contains three redundant coordinate systems: WGS84 (`Lat`/`Long`), Web Mercator
  (`X`/`Y`), and a projected system (`X_Coordinate`/`Y_Coordinate`). Only `Lat`/`Long` is used
  in this project.
- Six categorical columns encode values as `NN - Description` (e.g. `03 - Rear end`). All
  numeric prefixes carry no analytical meaning and must be stripped before grouping or display.
- Count columns (`num_of_pedestrians`, `num_of_bicycles`, etc.) are sparse by design — they
  are populated only when the relevant road user type was involved. Null rates range from 0.18%
  (`num_of_vehicles`) to 99.82% (`num_of_fatal`).

---

## Transformation Decisions

- **Coded prefix stripping** was applied to all six categorical columns in `collisions_clean`.
  Verified by regex check in `src/clean_schema_checks.py` — zero rows with `^\d{2} - ` remain.
- **Null-to-zero filling** was applied to eight sparse count columns where null unambiguously
  means "none involved" (pedestrians, bicycles, motorcycles) or "not applicable" (injury
  breakdown columns on non-injury rows). `num_of_vehicles` was not filled: its 168 nulls
  have no obvious innocent explanation and are flagged instead.
- **Two diagnostic flags** (`num_of_vehicles_missing`, `core_injury_count_missing`) were added
  before any filling to preserve a record of which rows had suspicious nulls in the source data.
- **Five boolean helper columns** were derived (`geo_valid`, `involves_active_transport`,
  `is_fatal`, `is_non_fatal_injury`, `is_property_damage_only`) to support common query
  patterns without requiring repeated CASE expressions or substring matching on categorical fields.
- **No rows were dropped.** `collisions_clean` contains exactly 94,406 rows. Rows with corrupt
  coordinates, missing vehicle counts, or incomplete injury records are retained and flagged.

---

## Known Data Quality Issues

- **72 coordinate outliers** fall outside the rough Ottawa bounding box (lat 44.9–45.7, lon
  -76.4–-75.2), including rows with `lat = 0.0` indicating a placeholder value. These rows
  are marked `geo_valid = False` in `collisions_clean` and must be excluded from any spatial
  analysis.
- **9 injury-classified rows** (`core_injury_count_missing = True`) are missing `num_of_vehicles`
  or `num_of_injuries` despite being classified as `Fatal injury` or `Non-fatal injury`. These
  are recording errors in the source data and cannot be safely imputed.
- **168 rows** have a null `num_of_vehicles`. A collision with no vehicle count is anomalous;
  the cause is unknown. These rows are flagged `num_of_vehicles_missing = True` and should be
  excluded from vehicle-count analysis.
- **2,076 rows** have no `geo_id` or `location` — likely collisions that occurred away from a
  named intersection. These rows are otherwise complete and are retained.
- **2023 is absent** from the dataset. Any time-series analysis or year-over-year comparison
  must account for this gap explicitly.

---

## Limitations for Text-to-SQL

- **Coded prefix stripping is a prerequisite for natural language queries.** A user asking
  "show rear-end collisions" would fail against `collisions_raw` because values are stored as
  `03 - Rear end`. All NL queries should be routed to `collisions_clean`.
- **Boolean flags simplify but do not eliminate ambiguity.** `is_non_fatal_injury` and
  `is_property_damage_only` cover only two of the four classification values; `Non-reportable`
  rows are not covered by any flag and may confuse count queries if not documented in the
  schema context passed to the model.
- **Sparse count columns post-fill can mislead aggregations.** After zero-filling, `SUM(num_of_pedestrians)`
  is meaningful only on rows where a pedestrian was involved. A Text-to-SQL system must
  understand that zero does not mean "no data" — it means "not involved." This distinction
  must be surfaced in the prompt or schema description.
- **`num_of_vehicles` has 168 unexplained nulls.** Any query that aggregates vehicle counts
  will silently undercount unless the NL system is aware of this and filters or caveats accordingly.
- **The 72 coordinate outliers and missing 2023 data** are silent errors — they do not raise
  exceptions and will not be detected by a language model unless the schema context explicitly
  flags them. Queries involving spatial filtering or year-over-year trends must be treated
  with caution until these issues are resolved.
