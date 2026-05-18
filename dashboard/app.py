"""Streamlit NLQ dashboard for Ottawa collision data."""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import duckdb
import folium
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from streamlit_folium import st_folium

from src.text_to_sql import build_graph

load_dotenv()

DB_PATH = Path(os.getenv("DB_PATH", "data/processed/ottawa_road_safety.duckdb"))
OTTAWA_CENTER = (45.4215, -75.6972)
UNSUPPORTED = "UNSUPPORTED QUERY"


@st.cache_resource
def get_db_connection():
    """Return a cached DuckDB connection to the processed database."""
    return duckdb.connect(str(DB_PATH))


@st.cache_resource
def get_graph():
    """Return a cached compiled LangGraph for text-to-SQL generation."""
    return build_graph()


def render_map(df: pd.DataFrame) -> None:
    """Render a Folium map of result rows that have valid lat/long values."""
    mappable = df[df["lat"].notna() & df["long"].notna()]
    if mappable.empty:
        return

    fmap = folium.Map(location=OTTAWA_CENTER, zoom_start=11)
    for row in mappable.itertuples(index=False):
        folium.CircleMarker(
            location=(row.lat, row.long),
            radius=4,
            fill=True,
            fill_opacity=0.7,
        ).add_to(fmap)

    st_folium(fmap, use_container_width=True, height=500)


def process_query(question: str) -> None:
    """Generate SQL, execute it, and store results in session state."""
    graph = get_graph()
    con = get_db_connection()

    with st.spinner("Generating SQL..."):
        result = graph.invoke({"question": question})
    sql = result["generated_sql"]

    st.session_state.sql = sql
    st.session_state.warning = None
    st.session_state.error = None
    st.session_state.df = None

    if sql.strip() == UNSUPPORTED:
        st.session_state.warning = "This question cannot be answered from the available collision data."
        return

    try:
        df = con.execute(sql).df()
    except Exception as exc:
        st.session_state.error = f"SQL execution failed: {exc}"
        return

    if df.empty:
        st.session_state.warning = "No results found for this query."
        return

    st.session_state.df = df


def render_results() -> None:
    """Render stored session state results — SQL, warnings, errors, table, map."""
    if st.session_state.get("sql"):
        with st.expander("Generated SQL", expanded=False):
            st.code(st.session_state.sql, language="sql")

    if st.session_state.get("warning"):
        st.warning(st.session_state.warning)

    if st.session_state.get("error"):
        st.error(st.session_state.error)

    if st.session_state.get("df") is not None:
        df = st.session_state.df
        st.dataframe(df, use_container_width=True)
        if "lat" in df.columns and "long" in df.columns:
            render_map(df)


def main():
    """Render the Streamlit page and process queries on submit."""
    st.set_page_config(page_title="Ottawa Road Safety — NLQ Interface", layout="wide")
    st.title("Ottawa Road Safety Analytics")
    st.markdown("Ask a question about Ottawa collision data in plain English")

    for key in ("sql", "df", "warning", "error"):
        if key not in st.session_state:
            st.session_state[key] = None

    question = st.text_input(
        "Your question",
        placeholder="e.g. How many fatal collisions happened in 2022?",
    )
    submitted = st.button("Run Query")

    if submitted and question.strip():
        for key in ("sql", "df", "warning", "error"):
            st.session_state[key] = None
        try:
            process_query(question.strip())
        except Exception as exc:
            st.session_state.error = f"Unexpected error: {exc}"

    render_results()


main()