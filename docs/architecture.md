# System Architecture

```mermaid
flowchart TD
    A[Streamlit UI] -->|question| B[retrieve_schema_node]
    B -->|embed + query| C[(ChromaDB\n8 schema chunks)]
    C -->|top 5 chunks · all-MiniLM-L6-v2| B
    B -->|question + context| D[text_to_sql_node]
    D -->|prompt| E[Groq API\nllama-3.3-70b-versatile]
    E -->|SQL| D
    D --> F[validate_sql_node\n5 structural checks]
    F --> G{Valid SQL}
    G -->|yes| H[(DuckDB\n94,406 rows · 37 cols)]
    G -->|no / UNSUPPORTED| I[warn user]
    H -->|DataFrame| J[Streamlit results table]
    J -->|if lat + long| K[Folium map]

    classDef ui fill:#4A90D9,color:#fff
    classDef graphStyle fill:#2ECC71,color:#fff
    classDef external fill:#F5A623,color:#fff
    classDef data fill:#9B59B6,color:#fff
    classDef decision fill:#F1C40F,color:#000

    class A,J,K ui
    class B,D,F graphStyle
    class E external
    class C,H data
    class G decision
```

---

## Layers

| Layer | Role |
|---|---|
| Streamlit UI | Accepts user question, submits to graph, renders results and map |
| LangGraph StateGraph | Orchestrates 3-node pipeline, passes `QueryState` between nodes |
| `retrieve_schema_node` | Embeds question with `all-MiniLM-L6-v2`, queries ChromaDB, returns top 5 chunks |
| `text_to_sql_node` | Injects context + full schema into prompt, calls Groq, returns SQL string |
| `validate_sql_node` | Runs 5 structural checks before any database call |
| DuckDB | Executes validated SQL against `collisions_clean` (94,406 rows, 37 columns) |
| ChromaDB | In-memory collection of 8 schema chunk embeddings |
| Groq API | Hosts `llama-3.3-70b-versatile` for SQL generation |
| Folium Map | Renders collision locations when result contains `lat`/`long` columns |
