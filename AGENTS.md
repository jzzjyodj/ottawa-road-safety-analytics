

# AGENTS.md

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

Current phase: CIMS Sprint, Days 3–4.

Immediate goal:
- Implement src/text_to_sql.py with a LangGraph StateGraph containing one node and one state object
- The graph takes a plain English question and returns generated SQL via the Anthropic API
- Test the prompt against 8–10 hand-written questions
- Document pass/fail results honestly

Do not build the Streamlit dashboard, RAG layer, ML pipeline, FastAPI backend, or query validator yet unless explicitly requested.

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
|   ├── preprocess.py
|   └── clean_schema_checks.py

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

## LangGraph Design Rules
- Use langgraph.graph.StateGraph for all LangGraph graphs
- Define state as a TypedDict with clearly named fields
- Days 3–4: one node only — text_to_sql_node
- The node reads the prompt file, calls the Anthropic API, and writes generated SQL to state
- Do not add additional nodes unless explicitly requested

