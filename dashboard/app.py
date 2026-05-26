"""Streamlit NLQ dashboard for Ottawa collision data."""
import os
import sys
import time
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

EXAMPLES = [
    "How many fatal collisions happened in 2022?",
    "Show me the coordinates of cyclist collisions at night",
    "Which location had the most collisions?",
    "How many collisions happened on icy roads in December?",
]

SEVERITY_COLORS = {
    "Fatal injury": "#e74c3c",
    "Non-fatal injury": "#f39c12",
    "P.D. only": "#3498db",
    "Non-reportable": "#95a5a6",
}

TOOLTIP_FIELDS = [
    ("location", "Location"),
    ("classification_of_accident", "Classification"),
    ("accident_date", "Date"),
    ("initial_impact_type", "Impact Type"),
    ("light", "Light"),
]


@st.cache_resource
def get_db_connection():
    """Return a cached DuckDB connection to the processed database."""
    return duckdb.connect(str(DB_PATH))


@st.cache_resource
def get_graph():
    """Return a cached compiled LangGraph for text-to-SQL generation."""
    return build_graph()


def render_map(df: pd.DataFrame) -> None:
    """Render a Folium map, always showing the Ottawa base map."""
    has_coords = "lat" in df.columns and "long" in df.columns

    if not has_coords:
        fmap = folium.Map(location=OTTAWA_CENTER, zoom_start=11)
        st_folium(fmap, use_container_width=True, height=500)
        st.caption("Add lat and long to your question to see collision locations on the map.")
        return

    mappable = df[df["lat"].notna() & df["long"].notna()]
    if mappable.empty:
        return

    has_severity = "classification_of_accident" in df.columns

    fmap = folium.Map(location=OTTAWA_CENTER, zoom_start=11)
    for row in mappable.itertuples(index=False):
        if has_severity:
            color = SEVERITY_COLORS.get(row.classification_of_accident, "#3498db")
        else:
            color = "#3498db"
        tooltip_lines = []
        for col, label in TOOLTIP_FIELDS:
            if col in df.columns:
                val = getattr(row, col, None)
                display = "N/A" if pd.isna(val) else str(val)
                tooltip_lines.append(f"{label}: {display}")
        folium.CircleMarker(
            location=(row.lat, row.long),
            radius=4,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.7,
            tooltip=folium.Tooltip(text="\n".join(tooltip_lines)),
        ).add_to(fmap)

    st_folium(fmap, use_container_width=True, height=500)


def process_query(question: str) -> None:
    """Generate SQL, execute it, and store results in session state."""
    graph = get_graph()
    con = get_db_connection()

    with st.spinner("Generating SQL..."):
        result = graph.invoke({
            "question": question,
            "retrieved_context": "",
            "generated_sql": "",
            "validated_sql": "",
            "validation_error": "",
        })
    sql = result["validated_sql"]
    validation_error = result["validation_error"]

    st.session_state.sql = sql
    st.session_state.warning = None
    st.session_state.error = None
    st.session_state.df = None
    st.session_state.query_time = None

    if validation_error:
        st.session_state.warning = f"Query blocked by validator: {validation_error}"
        return

    if sql.strip() == UNSUPPORTED:
        st.session_state.warning = "This question cannot be answered from the available collision data."
        return

    try:
        t0 = time.time()
        df = con.execute(sql).df()
        st.session_state.query_time = time.time() - t0
    except Exception as exc:
        st.session_state.error = f"SQL execution failed: {exc}"
        return

    if df.empty:
        st.session_state.warning = "No results found for this query."
        return

    st.session_state.df = df


def render_results() -> None:
    """Render stored session state results — SQL, warnings, errors, table, map."""
    has_any = any(
        st.session_state.get(k) is not None for k in ("sql", "df", "warning", "error")
    )
    if not has_any:
        st.info(
            "Enter a plain English question above and click Run Query. The system will "
            "generate SQL, run it against 94,406 Ottawa collision records, and return a "
            "result table with an optional map for spatial queries."
        )
        return

    if st.session_state.get("sql"):
        with st.expander("Generated SQL", expanded=False):
            st.code(st.session_state.sql, language="sql")

    if st.session_state.get("warning"):
        st.warning(st.session_state.warning)

    if st.session_state.get("error"):
        st.error(st.session_state.error)

    if st.session_state.get("df") is not None:
        df = st.session_state.df
        m1, m2, m3 = st.columns(3)
        m1.metric("Rows", f"{len(df):,}")
        m2.metric("Columns", len(df.columns))
        qt = st.session_state.get("query_time")
        m3.metric("Query time", f"{qt:.3f}s" if qt is not None else "—")
        st.dataframe(df, use_container_width=True)
        st.download_button(
            label="Download CSV",
            data=df.to_csv(index=False),
            file_name="ottawa_collision_results.csv",
            mime="text/csv",
        )
        render_map(df)


def main():
    """Render the Streamlit page and process queries on submit."""
    st.set_page_config(page_title="Ottawa Road Safety — NLQ Interface", layout="wide")
    st.title("Ottawa Road Safety Analytics")
    st.markdown("Ask a question about Ottawa collision data in plain English")

    with st.sidebar:
        st.markdown("### Dataset")
        st.markdown("**Ottawa Traffic Collision Data**")
        st.markdown("**Records:** 94,406")
        st.markdown("**Years:** 2017–2024 *(2023 absent)*")
        st.markdown(
            "**Source:** [Open Ottawa](https://open.ottawa.ca/datasets/ottawa::traffic-collision-data)"
        )
        st.markdown("---")
        st.markdown("Powered by LangGraph · ChromaDB · Groq · DuckDB")

    for key in ("sql", "df", "warning", "error", "query_time"):
        if key not in st.session_state:
            st.session_state[key] = None

    _pending = st.session_state.pop("_pending_question", None)
    if _pending is not None:
        st.session_state["question_input"] = _pending

    question = st.text_input(
        "Your question",
        placeholder="e.g. How many fatal collisions happened in 2022?",
        key="question_input",
    )

    ex_cols = st.columns(4)
    for col, ex in zip(ex_cols, EXAMPLES):
        if col.button(ex, use_container_width=True):
            for key in ("sql", "df", "warning", "error"):
                st.session_state[key] = None
            try:
                process_query(ex)
            except Exception as exc:
                st.session_state.error = f"Unexpected error: {exc}"
            st.session_state["_pending_question"] = ex
            st.rerun()

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
