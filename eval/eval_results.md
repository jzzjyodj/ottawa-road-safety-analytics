# Evaluation Results

## Summary

| Total Questions | Pass | Fail | Pass Rate |
|---|---|---|---|
| 10 | 9 | 1 | 90% |

---

## Named Failure Modes

1. AND/OR operator precedence in complex date range queries
When a question requires filtering across a date range that spans multiple years and months, the LLM sometimes generates SQL where AND/OR precedence is incorrect. For example, the OR condition is not wrapped in parentheses, causing it to apply globally instead of within the date range. This produced an inflated count of 4,211 in the first run of Q3. The second run fixed itself, demonstrating that the failure is non-deterministic. To fix this, I canadd an explicit prompt rule instructing the LLM to always wrap multi-condition date ranges in parentheses.
2. Null values surfacing as top results in GROUP BY queries
When grouping by a nullable text column such as location, the 2,076 null rows aggregate together and rank as the highest-collision entry which caused Q4 to return None as the top location instead of a real intersection. TO fix this, add a prompt rule to always include WHERE column IS NOT NULL when grouping by nullable text columns.
3. geo_valid over-application on non-spatial count queries
The prompt rule states to always filter geo_valid = TRUE for spatial or map-based queries to filter to non-spatial count queries in Q3, Q5, Q7, and Q9. This silently excludes 72 rows from results that should include the full dataset. For count queries the numerical impact is small but the behavior is inconsistent with the prompt intent and could mislead users comparing results. May help to clarify the prompt rule to specify that geo_valid filtering applies only when returning coordinates or rendering maps.

---

## Prompt Behavior Observations

1. Non-deterministic SQL generation
Running the same question twice produced different SQL for Q3. The first run had an AND/OR logic error. The second run was correct.
2. Boolean flag adoption is strong
The LLM correctly used is_fatal, num_of_vehicles_missing, and geo_valid flags across multiple queries without being explicitly reminded in the question. 

---

## Recommended Prompt v2 Improvements

- Add a rule: when using GROUP BY on a text column, always include WHERE column IS NOT NULL to exclude null rows from aggregation results
- Clarify the geo_valid rule: apply geo_valid = TRUE only when the query returns lat/lon coordinates or is intended for map rendering — not for count or aggregation queries
- Add a rule: when filtering by a date range that spans multiple years and months, always wrap the full range condition in explicit parentheses to prevent AND/OR precedence errors
- Add an example in the prompt showing a correct multi-condition date range filter so the LLM has a concrete pattern to follow

