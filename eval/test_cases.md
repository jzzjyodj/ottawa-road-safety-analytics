# Evaluation Test Cases

**Status:** Placeholder. Populate after text_to_sql is implemented.

## Format

| ID | Question | Expected SQL | Notes |
|----|----------|--------------|-------|
| 1  | How many collisions occurred in 2023? | `SELECT COUNT(*) FROM raw_collisions WHERE YEAR(collision_date) = 2023` | Date column TBD |
| 2  | Which intersection had the most collisions? | TBD | |

## Guidelines
- Cover: aggregations, filters, date ranges, spatial queries, joins.
- Each case should have a verified expected SQL and expected result row count.
