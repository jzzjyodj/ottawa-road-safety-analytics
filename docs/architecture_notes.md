# Architecture Notes

## System Architecture

User question → Streamlit UI → LangGraph graph → DuckDB → Result table + Folium map

LangGraph graph (two nodes):
1. retrieve_schema_node — queries ChromaDB, retrieves top 5 relevant schema chunks, writes to state
2. text_to_sql_node — reads retrieved context, calls Groq API, generates SQL, writes to state

## Design Decisions

- DuckDB over PostgreSQL: serverless, no infrastructure, fast for analytical queries on a single flat table
- In-memory ChromaDB over persistent: schema has 8 chunks, rebuild takes milliseconds, eliminates stale collection risk
- Column groups over per-column chunking: 8 groups ensure related columns are always retrieved together
- Groq over Anthropic API: free tier sufficient for sprint eval runs
- Single flat table over normalized schema: simplifies LLM-generated SQL, no joins required
- Full static schema retained in prompt alongside RAG context: acts as safety net when retrieval misses a relevant column

## Known Limitations

- all-MiniLM-L6-v2 does not consistently match time-of-day references like "night" to the light column. Scheduled for prompt v2 review on Days 11-12.
- geo_valid filter is over-applied to non-spatial count queries. Prompt v2 will clarify when to apply it.
- Null locations surface as top result in GROUP BY queries on location column. Mitigated in identity_location chunk with WHERE location IS NOT NULL instruction.
- SQL generation is non-deterministic — same question can produce different SQL on repeated runs.

## RAG Retrieval Evidence

Question: "How many cyclist collisions happened at night?"
Retrieved chunks: active_transport, table_overview, spatial, severity_injury, date_time
Generated SQL: SELECT COUNT(*) FROM collisions_clean WHERE involves_active_transport = TRUE AND num_of_bicycles > 0 AND light = 'Dark' AND geo_valid = TRUE AND num_of_vehicles_missing = FALSE
Assessment: active_transport chunk correctly surfaced. environmental_conditions chunk missed due to semantic gap between "night" and "Dark" in light column description. Full static schema compensated.
