# Cleaning Rules — `collisions_clean`

## Status: Implemented

| Property | Value |
|---|---|
| Source table | `collisions_raw` |
| Target table | `collisions_clean` |
| Implementation | `src/preprocess.py` — `build_collisions_clean()` |
| Prototype notebook | `notebooks/03_cleaning_rules_prototype.ipynb` |
| Validation script | `src/clean_schema_checks.py` |
| Row count | 94,406 in → 94,406 out (no rows dropped) |

---

## Rule 1 — Column Renaming (snake_case)

**Target:** All 28 source columns  
**Transformation:** `df.rename(columns=RENAME_MAP)`  
**Expected output:** All column names lowercase snake_case

| Original | Renamed |
|---|---|
| X | x |
| Y | y |
| X_Coordinate | x_coordinate |
| Y_Coordinate | y_coordinate |
| ID | id |
| Geo_ID | geo_id |
| Accident_Year | accident_year |
| Accident_Date | accident_date |
| Location | location |
| Classification_Of_Accident | classification_of_accident |
| Initial_Impact_Type | initial_impact_type |
| Road_1_Surface_Condition | road_1_surface_condition |
| Environment_Condition_1 | environment_condition_1 |
| Light | light |
| Traffic_Control | traffic_control |
| Max_injury | max_injury |
| Lat | lat |
| Long | long |
| ObjectId | object_id |
| num_of_* columns | unchanged (already snake_case) |

---

## Rule 2 — Strip Coded Prefix from Categorical Columns

**Target:** 6 categorical columns  
**Transformation:** `series.str.replace(r"^\d{2}\s*-\s*", "", regex=True)`  
**Expected output:** Description text only; nulls preserved unchanged

| Column | Example Before | Example After |
|---|---|---|
| classification_of_accident | `03 - P.D. only` | `P.D. only` |
| initial_impact_type | `03 - Rear end` | `Rear end` |
| light | `01 - Daylight` | `Daylight` |
| traffic_control | `01 - Traffic signal` | `Traffic signal` |
| road_1_surface_condition | `01 - Dry` | `Dry` |
| environment_condition_1 | `01 - Clear` | `Clear` |

Validated: `src/clean_schema_checks.py` check 11 confirms zero rows with `^\d{2} - ` prefix remaining in any of the six columns.

---

## Rule 3 — Derive Date Fields

**Target:** `accident_date`  
**Transformation:** pandas `.dt` accessors  
**Expected output:** Two new integer/string columns; source column preserved

| New Column | Type | Method |
|---|---|---|
| `accident_month` | INTEGER | `accident_date.dt.month` — integer 1–12 |
| `accident_day_of_week` | VARCHAR | `accident_date.dt.day_name()` — e.g. `Monday` |

`accident_year` is retained from the raw source column. `accident_date` is preserved as TIMESTAMP.

---

## Rule 4 — Count Column Null Handling

### Step 4a — Diagnostic flags (created before any filling)

**Target:** `num_of_vehicles`, `num_of_injuries`, `classification_of_accident`  
**Expected output:** Two BOOLEAN columns added

| Flag Column | Logic | Confirmed Count |
|---|---|---|
| `num_of_vehicles_missing` | `num_of_vehicles IS NULL` | 168 |
| `core_injury_count_missing` | `classification_of_accident IN ('Fatal injury', 'Non-fatal injury')` AND (`num_of_vehicles IS NULL` OR `num_of_injuries IS NULL`) | 9 |

The 9 `core_injury_count_missing` rows are genuine recording errors — injury collisions with no vehicle or injury count. They are retained in `collisions_clean` and flagged for exclusion from injury-count analysis.

### Step 4b — Fill sparse counts with 0

**Target:** 8 count columns  
**Transformation:** `fillna(0).astype(int)`  
**Expected output:** Zero nulls remaining in all eight columns

| Column | Fill Rationale |
|---|---|
| `num_of_pedestrians` | Null means no pedestrian was involved |
| `num_of_bicycles` | Null means no bicycle was involved |
| `num_of_motorcycles` | Null means no motorcycle was involved |
| `num_of_injuries` | Null on non-injury rows means zero injuries |
| `num_of_minimal` | Null on non-injury rows means zero minimal injuries |
| `num_of_minor` | Null on non-injury rows means zero minor injuries |
| `num_of_major` | Null on non-injury rows means zero major injuries |
| `num_of_fatal` | Null on non-injury rows means zero fatalities |

**`num_of_vehicles` is not filled.** Its 168 nulls are unexplained and must not be assumed to equal zero.

---

## Rule 5 — Derived Boolean Flags

**Target:** Derived from already-cleaned columns  
**Transformation:** Boolean expressions  
**Expected output:** 5 BOOLEAN columns

| Column | Logic | Note |
|---|---|---|
| `geo_valid` | `lat` and `long` non-null, non-zero, within lat 44.9–45.7 / lon -76.4–-75.2 | 72 rows are `False` |
| `involves_active_transport` | `num_of_pedestrians > 0 OR num_of_bicycles > 0` | Depends on Rule 4b zero-fill |
| `is_fatal` | `classification_of_accident == 'Fatal injury'` | Depends on Rule 2 prefix strip |
| `is_non_fatal_injury` | `classification_of_accident == 'Non-fatal injury'` | Depends on Rule 2 prefix strip |
| `is_property_damage_only` | `classification_of_accident == 'P.D. only'` | Depends on Rule 2 prefix strip |

`is_fatal`, `is_non_fatal_injury`, and `is_property_damage_only` together cover 91,843 rows. The remaining 2,563 are `Non-reportable` rows — `False` for all three flags.

---

## Rule Dependency Order

Rules must be applied in this exact sequence:

1. **Rename columns** (Rule 1) — must run first; all subsequent rules reference snake_case names
2. **Strip coded prefixes** (Rule 2) — must run before boolean flags that match on description text
3. **Derive date fields** (Rule 3) — no dependencies; can run after Rule 1
4. **Create diagnostic flags** (Rule 4a) — must run before filling so nulls are captured first
5. **Fill sparse counts with 0** (Rule 4b) — must run before `involves_active_transport`
6. **Add boolean flags** (Rule 5) — must run last; depends on Rules 2 and 4b
