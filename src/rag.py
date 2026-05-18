"""In-memory ChromaDB RAG layer for collisions_clean schema retrieval."""
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

_IDS = [
    "table_overview",
    "identity_location",
    "date_time",
    "severity_injury",
    "active_transport",
    "vehicle_counts",
    "environmental_conditions",
    "spatial",
]

_DOCUMENTS = [
    # table_overview
    (
        "The main analysis table is collisions_clean, containing 94,406 rows and 37 columns. "
        "Each row represents one reported traffic collision in Ottawa. "
        "The primary key is id (VARCHAR, format YYYY--NNN). "
        "Year range is 2017–2024 with 2023 entirely absent from the dataset — "
        "any year-over-year analysis must account for this gap. "
        "The table is stored in a DuckDB database at data/processed/ottawa_road_safety.duckdb."
    ),
    # identity_location
    (
        "id (VARCHAR) is the unique collision identifier in YYYY--NNN format and serves as the "
        "primary key (94,406 unique values, 0 nulls). "
        "object_id (BIGINT) is an alternative sequential integer primary key (94,406 unique). "
        "location (VARCHAR) is a human-readable intersection description such as "
        "'BANK ST / RIVERSIDE DR'; it has 2,076 null values. "
        "Always include WHERE location IS NOT NULL when grouping or ordering by location. "
        "geo_id (VARCHAR) is an intersection reference code shared across rows, not a row "
        "identifier; it has 2,076 nulls."
    ),
    # date_time
    (
        "accident_date (TIMESTAMP) is the date the collision occurred, stored as TIMESTAMP in "
        "DuckDB. "
        "accident_year (BIGINT) is the year, ranging 2017–2024 with 2023 absent. "
        "accident_month (INTEGER) is the month number from 1 (January) to 12 (December). "
        "accident_day_of_week (VARCHAR) is the full day name: Monday, Tuesday, Wednesday, "
        "Thursday, Friday, Saturday, Sunday. "
        "Use accident_year for year filtering and accident_month for month filtering rather "
        "than extracting from accident_date."
    ),
    # severity_injury
    (
        "classification_of_accident (VARCHAR) classifies collision severity with four values: "
        "'Fatal injury', 'Non-fatal injury', 'Non-reportable', 'P.D. only'. "
        "The boolean flags is_fatal (BOOLEAN, 170 true rows), is_non_fatal_injury (BOOLEAN, "
        "15,002 true rows), and is_property_damage_only (BOOLEAN, 76,671 true rows) are "
        "derived from this column and are preferred for filtering. "
        "max_injury (VARCHAR) records the most severe injury and is null for P.D. only and "
        "Non-reportable rows. "
        "num_of_injuries, num_of_minimal, num_of_minor, num_of_major, num_of_fatal are all "
        "BIGINT injury count columns filled with 0 where originally null. "
        "Use is_fatal = TRUE to filter fatal collisions."
    ),
    # active_transport
    (
        "involves_active_transport (BOOLEAN) is TRUE when num_of_pedestrians > 0 or "
        "num_of_bicycles > 0; use it to find collisions involving pedestrians or cyclists. "
        "num_of_pedestrians (BIGINT), num_of_bicycles (BIGINT), and num_of_motorcycles (BIGINT) "
        "count respective participants; all three are filled with 0 where originally null so "
        "null checks are not required. "
        "High null rates in the raw data (98–99%) reflect that most collisions involve only "
        "motor vehicles."
    ),
    # vehicle_counts
    (
        "num_of_vehicles (BIGINT) records the number of vehicles involved; it has 168 null "
        "values that were not filled during cleaning. "
        "num_of_vehicles_missing (BOOLEAN) is a diagnostic flag that is TRUE for those 168 "
        "rows — use num_of_vehicles_missing = FALSE to exclude them from vehicle count analysis."
    ),
    # environmental_conditions
    (
        "road_1_surface_condition (VARCHAR) describes road surface with values including 'Dry', "
        "'Wet', 'Ice', 'Loose snow', 'Packed snow', 'Slush', 'Mud'; 1 null. "
        "environment_condition_1 (VARCHAR) weather or environment condition valid values "
        "Clear Drifting Snow Fog mist smoke dust Freezing Rain Other Rain Snow Strong wind "
        "Unknown 13 nulls. "
        "light (VARCHAR) lighting condition valid values Dark Dawn Daylight Dusk Other Unknown "
        "14 nulls. "
        "traffic_control (VARCHAR) traffic control device valid values IPS MPS No control "
        "Other Ped. crossover Police control Roundabout School bus School guard Stop sign "
        "Traffic controller Traffic gate Traffic signal Yield sign 30 nulls. "
        "initial_impact_type (VARCHAR) first point of contact valid values Angle Approaching "
        "Other Rear end SMV other SMV unattended vehicle Sideswipe Turning movement 12 nulls."
    ),
    # spatial
    (
        "lat (DOUBLE) is the WGS84 latitude and long (DOUBLE) is the WGS84 longitude of the "
        "collision. "
        "geo_valid (BOOLEAN) is TRUE when both coordinates are non-null, non-zero, and within "
        "the Ottawa bounding box; 72 rows have geo_valid = FALSE including rows where "
        "lat = 0.0. "
        "Always filter WHERE geo_valid = TRUE before running spatial queries, map-based "
        "queries, or any query that returns lat/long coordinates. "
        "Do not apply geo_valid filtering to pure count or aggregation queries that do not "
        "use coordinates."
    ),
]

_ef = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
_client = chromadb.EphemeralClient()
_collection = _client.get_or_create_collection(
    name="schema_chunks",
    embedding_function=_ef,
)
_collection.add(documents=_DOCUMENTS, ids=_IDS)


def retrieve_context(question: str, n_results: int = 5) -> str:
    """Query the schema collection and return the top-n chunks joined by double newline.

    Args:
        question: Natural language question to retrieve context for.
        n_results: Number of schema chunks to return (default 5).

    Returns:
        Relevant schema chunks concatenated with double newlines.
    """
    results = _collection.query(query_texts=[question], n_results=n_results)
    return "\n\n".join(results["documents"][0])
