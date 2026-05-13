

# CLAUDE.md

## Project Context

This repository is for `ottawa-road-safety-analytics`, a data science portfolio project focused on Ottawa road safety analytics using City of Ottawa collision data.

The project will eventually include:
- DuckDB-backed collision analytics
- geospatial collision analysis
- exposure-adjusted risk scoring
- a natural language Text-to-SQL interface
- a Streamlit dashboard
- a classical ML pipeline
- FastAPI backend components
- CI, Docker, and documentation

## Current Sprint Phase

Current phase: CIMS Sprint, Day 1–2.

Immediate goal:
- Load the City of Ottawa Traffic Collision Data CSV into DuckDB
- Inspect and document the schema
- Run basic schema and spatial checks
- Keep the implementation minimal and reliable

Do not build the full Text-to-SQL app, ML pipeline, FastAPI backend, dashboard, or LLM summarizer yet unless explicitly requested.

## Repository Structure

Expected structure:

```text
ottawa-road-safety-analytics/
├── src/
│   ├── config.py
│   ├── database.py
│   ├── ingest.py
│   ├── schema_checks.py
│   ├── text_to_sql.py
│   └── query_validator.py
├── sql/
│   ├── 00_extensions.sql
│   ├── 01_create_raw_tables.sql
│   ├── 02_schema_checks.sql
│   └── 03_spatial_checks.sql
├── data/
│   ├── raw/
│   ├── interim/
│   └── processed/
├── docs/
│   ├── data_dictionary.md
│   ├── schema_notes.md
│   └── data_sources.md
└── tests/
```
## Coding Conventions
- All functions must have docstrings
- Use pathlib.Path for all file paths, not raw strings
- Environment variables loaded via python-dotenv from .env
- No hardcoded file paths anywhere in src/

## Data Layer Rules

Use a two-layer DuckDB table design:

- `collisions_raw`: exact raw source-loaded table
- `collisions_clean`: future cleaned analysis-ready table

For Day 1–2, only implement `collisions_raw`.

`src/ingest.py` should only:
- read `data/raw/Traffic_Collision_Data.csv`
- create/connect to `data/processed/ottawa_road_safety.duckdb`
- load the CSV into DuckDB as `collisions_raw`
- preserve original column names
- preserve raw categorical values
- preserve nulls/blanks
- preserve rows as-is
- print row count, column count, and schema summary

`src/ingest.py` must not:
- rename columns
- parse `Accident_Date`
- strip coded prefixes from categorical columns
- fill nulls with zero
- cast count columns to integers
- drop coordinate columns
- drop `ObjectId`
- remove coordinate outliers
- create derived features

Future preprocessing should happen in a separate module such as `src/preprocess.py`, which will create `collisions_clean` from `collisions_raw` after cleaning rules are documented.