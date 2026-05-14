# Evaluation Test Cases

**Status:** Questions finalized. Expected SQL to be filled in after 
text_to_sql.py is running.

## Format

| ID | Question | Expected Columns Used | Generated SQL | Pass/Fail | Notes |
|----|----------|-----------------------|---------------|-----------|-------|
| 1  | How many collisions happened in 2017? | accident_year | TBD | TBD | Simple count with year filter |
| 2  | How many fatal collisions occurred during weekends? | classification_of_accident, accident_day_of_week | TBD | TBD | Two conditions |
| 3  | How many collisions involved turning movement between March 2021 and March 2022? | initial_impact_type, accident_date | TBD | TBD | Date range filter |
| 4  | Which location had the most collisions? | location | TBD | TBD | Raw geo_id suffix will appear in result — known display limitation |
| 5  | How many collisions happened on wet road conditions? | road_1_surface_condition | TBD | TBD | Single filter |
| 6  | What percentage of collisions involved roundabouts? | traffic_control | TBD | TBD | Requires percentage calculation |
| 7  | How many collisions happened in December on icy roads? | accident_month, road_1_surface_condition | TBD | TBD | Two filters |
| 8  | Show me the location of all fatal collisions where there are more than 1 vehicle involved? | is_fatal, num_of_vehicles, lat, long, geo_valid | TBD | TBD | Spatial query — geo_valid must be TRUE |
| 9  | How many collisions happened on each day of the week? | accident_day_of_week | TBD | TBD | GROUP BY query |
| 10 | How many accidents were due to drunk driving? | none | UNSUPPORTED QUERY | TBD | Schema has no impairment column |

## Guidelines
- Expected SQL column is filled after running text_to_sql.py against each question
- Pass = generated SQL is valid DuckDB syntax AND returns correct results
- Fail = wrong columns, wrong values, invalid syntax, or hallucinated schema
- Question 10 passes only if the system returns exactly: UNSUPPORTED QUERY