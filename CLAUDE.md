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

Current phase: CIMS Sprint, Days 13–14.

Immediate goal:
- Write README.md explaining CIMS alignment, LangGraph node, RAG layer, eval results, and limitations
- Create architecture diagram showing all layers: input → LangGraph → RAG retrieval → LLM API → validator → UI
- Commit both before moving to cover letter

Do not build the ML pipeline, FastAPI backend, or Docker setup yet unless explicitly requested.

## Repository Structure

Expected structure:

```text
ottawa-road-safety-analytics/
├── src/
│   ├── config.py
│   ├── database.py
│   ├── ingest.py
│   ├── preprocess.py
│   ├── schema_checks.py
│   ├── clean_schema_checks.py
│   ├── text_to_sql.py
│   └── query_validator.py
├── prompts/
│   ├── text_to_sql_v1.md
│   └── text_to_sql_v2.md
├── eval/
│   ├── run_eval.py
│   ├── run_eval_with_results.py
│   ├── test_cases.md
│   └── eval_results.md
├── dashboard/
│   └── app.py
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
├── notebooks/
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
- Current graph has one node: text_to_sql_node
- The node reads the prompt file, calls the Groq API, and writes generated SQL to state
- Do not add additional nodes unless explicitly requested

## Streamlit Design Rules
- Cache the DuckDB connection using @st.cache_resource
- Cache the LangGraph graph using @st.cache_resource
- Always display generated SQL in a st.code block inside an expander
- Handle UNSUPPORTED QUERY with st.warning — never show it as a raw string
- Handle SQL execution errors with st.error — never let them crash the app
- Render a Folium map only when the result DataFrame contains both lat and long columns