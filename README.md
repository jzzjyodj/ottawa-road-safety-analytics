# Ottawa Road Safety Analytics

A DuckDB-backed analytics pipeline and natural language query interface for the City of Ottawa Traffic Collision dataset.

## Current Sprint: Day 1–2

**Objective:** Load the Ottawa Traffic Collision CSV into DuckDB, inspect the schema, run basic schema checks, and document the dataset.

Not yet built: Text-to-SQL interface, dashboard, Docker workflow, CI pipeline.

## Setup

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy environment config
cp .env.example .env

# 4. Place the Ottawa Traffic Collision CSV in data/raw/ as Traffic_Collision_Data.csv
#    See docs/data_sources.md for download instructions.

# 5. Run ingestion to create collisions_raw in DuckDB
python -m src.ingest
```

## Repository Structure

```
ottawa-road-safety-analytics/
├── src/                  # Python modules (ingest, schema checks, text-to-sql)
├── sql/                  # DuckDB SQL scripts
├── prompts/              # LLM prompt templates
├── eval/                 # Evaluation test cases and results
├── dashboard/            # Interactive dashboard (placeholder)
├── data/
│   ├── raw/              # Source CSV (git-ignored)
│   ├── interim/          # Intermediate outputs (git-ignored)
│   └── processed/        # Final outputs (git-ignored)
├── docs/                 # Data dictionary, schema notes, data sources
├── tests/                # pytest test suite
└── .github/workflows/    # CI pipeline (placeholder)
```

## Next Steps

- [x] Download Ottawa Traffic Collision CSV → `data/raw/Traffic_Collision_Data.csv`
- [x] Implement `src/ingest.py` — load CSV into DuckDB as `collisions_raw`
- [x] Run `DESCRIBE collisions_raw` and document the schema
- [x] Implement `src/schema_checks.py` for Day 1–2 validation
- [ ] Write Day 1–2 tests in `tests/test_database.py` and `tests/test_schema_checks.py`
- [ ] Begin text-to-sql sprint (Day 3+)
