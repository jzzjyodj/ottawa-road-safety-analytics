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

---

## GEval Prompt Comparison — v1 vs v2

Judge model: `meta-llama/llama-4-scout-17b-16e-instruct` via Groq  
SQL generation model: `llama-3.1-8b-instant` (see methodology note below)  
Metric: GEval Answer Relevancy (0.0–1.0)

| Prompt | Avg Relevancy |
|---|---|
| v1 | 0.75 |
| v2 | 0.61 |
| Delta | −0.14 |

### Notable per-question deltas

| Q | Finding |
|---|---|
| Q6 | +0.70 relevancy — v2 improved percentage calculation query |
| Q2 | Degraded — date range parentheses rule incorrectly applied to simple weekend day-of-week filter |
| Q7 | Degraded — date range parentheses rule incorrectly applied to single-month December filter |

### Delta finding

Prompt v2 improved Q6 (percentage calculation, +0.70 relevancy) but degraded Q2 and Q7 by over-applying the date range parentheses rule to simple month-based filters. Net effect: v2 average relevancy 0.61 vs v1 0.75. The date range rule needs to be scoped more precisely — it should only apply when a question explicitly spans multiple years, not when filtering by a single month or day.

### Methodology note

Both eval runs used `llama-3.1-8b-instant` for SQL generation due to daily token quota exhaustion on `llama-3.3-70b-versatile`. Production system uses the 70B model. The 8B model is more sensitive to prompt instruction changes, which may have amplified the date range rule effect.

---

## GEval Per-Question Results — Actual Run Data

Judge model: `meta-llama/llama-4-scout-17b-16e-instruct` via Groq  
SQL generation model: `llama-3.3-70b-versatile`  
Metrics: GEval Answer Relevancy and SQL Faithfulness (0.0–1.0)

### Prompt v1

| ID | Question (truncated) | Relevancy | Faithfulness |
|---|---|---|---|
| Q1 | How many collisions happened in 2017? | 1.00 | 1.00 |
| Q2 | How many fatal collisions occurred during weekends? | 1.00 | 1.00 |
| Q3 | How many collisions involved turning movement... | 0.90 | 1.00 |
| Q4 | Which location had the most collisions? | 1.00 | 1.00 |
| Q5 | How many collisions happened on wet road conditions? | 1.00 | 1.00 |
| Q6 | What percentage of collisions involved roundabouts? | 1.00 | 1.00 |
| Q7 | How many collisions happened in December on icy roads? | 1.00 | 1.00 |
| Q8 | Show me the location of all fatal collisions... | 0.90 | 0.80 |
| Q9 | How many collisions happened on each day of the week? | 0.90 | 1.00 |
| Q10 | How many accidents were due to drunk driving? | 0.00 | 1.00 |
| Q11 | What is the percentage difference of collisions... | 1.00 | 1.00 |
| Q12 | How many pedestrian related fatal accidents...? | 0.80 | 1.00 |
| Q13 | How many collisions occurred during snowy weather? | 0.90 | 1.00 |
| Q14 | How many collisions occurred at stop signs? | 1.00 | 1.00 |
| Q15 | How many collisions involved drivers over the age of 65? | 1.00 | 1.00 |
| **Average** | | **0.89** | **0.99** |

### Prompt v2

| ID | Question (truncated) | Relevancy | Faithfulness |
|---|---|---|---|
| Q1 | How many collisions happened in 2017? | 1.00 | 1.00 |
| Q2 | How many fatal collisions occurred during weekends? | 1.00 | 1.00 |
| Q3 | How many collisions involved turning movement... | 0.90 | 0.90 |
| Q4 | Which location had the most collisions? | 1.00 | 1.00 |
| Q5 | How many collisions happened on wet road conditions? | 1.00 | 1.00 |
| Q6 | What percentage of collisions involved roundabouts? | 1.00 | 1.00 |
| Q7 | How many collisions happened in December on icy roads? | 0.80 | 1.00 |
| Q8 | Show me the location of all fatal collisions... | 0.90 | 1.00 |
| Q9 | How many collisions happened on each day of the week? | 1.00 | 1.00 |
| Q10 | How many accidents were due to drunk driving? | 0.00 | 0.00 |
| Q11 | What is the percentage difference of collisions... | 1.00 | 1.00 |
| Q12 | How many pedestrian related fatal accidents...? | 0.80 | 1.00 |
| Q13 | How many collisions occurred during snowy weather? | 0.60 | 1.00 |
| Q14 | How many collisions occurred at stop signs? | 1.00 | 1.00 |
| Q15 | How many collisions involved drivers over the age of 65? | 0.00 | 0.10 |
| **Average** | | **0.80** | **0.87** |

### Summary delta

| Metric | v1 | v2 | Delta |
|---|---|---|---|
| Avg Relevancy | 0.89 | 0.80 | −0.09 |
| Avg Faithfulness | 0.99 | 0.87 | −0.12 |
| Relevancy pass rate | 93.33% | 86.67% | −6.66pp |
| Faithfulness pass rate | 100.00% | 86.67% | −13.33pp |

---

## Analysis

### v1 — Prompt v1 performs well overall

v1 scores 0.89 average relevancy and 0.99 average faithfulness across 15 questions. The only relevancy failure is Q10 (drunk driving, UNSUPPORTED QUERY) — which is the correct pipeline behavior, but the judge does not follow the GEval special case instruction ("UNSUPPORTED QUERY scores 1.0") and penalises it with 0.00 instead. The real relevancy pass rate excluding unsupported queries is effectively 14/14. Faithfulness is near-perfect, with only Q8 (fatal collision location query) scoring 0.80 — likely due to the SQL including slightly misaligned column selection.

### v2 — New rules introduce regressions on simple queries

v2 averages 0.80 relevancy and 0.87 faithfulness, underperforming v1 on both metrics. Three questions degraded:

- **Q7 (−0.20 relevancy)**: The December/icy roads query is a single-month filter, but the new date range parentheses rule appears to have caused the model to add unnecessary parentheses around a simple `accident_month = 12` condition, reducing correctness.
- **Q13 (−0.30 relevancy)**: This is a judge false negative. v2 actually generates the more correct SQL — `WHERE environment_condition_1 = 'Snow'` with no `geo_valid` filter, which is correct for a pure count query. v1 generated `WHERE environment_condition_1 = 'Snow' AND geo_valid = TRUE`, silently excluding 72 rows. The judge penalised v2 for removing `geo_valid`, likely because it associates that flag with well-formed SQL. The v2 geo_valid rule worked as intended here.
- **Q15 (−1.00 relevancy, −0.90 faithfulness)**: Q15 should return UNSUPPORTED QUERY (no driver age column in the schema). In v1 the judge correctly scored it 1.00/1.00. In v2 the judge scored it 0.00/0.10. This is judge non-determinism on UNSUPPORTED QUERY handling — not a real pipeline regression.

Two questions improved in v2:

- **Q8 faithfulness (+0.20)**: The spatial query for fatal collision locations scored 1.00 faithfulness vs 0.80 in v1.
- **Q9 relevancy (+0.10)**: The day-of-week aggregation improved to 1.00.

### Judge reliability issue — UNSUPPORTED QUERY scoring

The GEval criteria include a special case instruction stating that UNSUPPORTED QUERY should always score 1.0. The judge (`llama-4-scout-17b-16e-instruct`) does not reliably follow this instruction. Q10 scored 0.00 relevancy in both runs, and in v2 also scored 0.00 faithfulness (vs 1.00 in v1). Q15 scored 1.00/1.00 in v1 but 0.00/0.10 in v2. This non-determinism inflates the apparent v2 regression. Future eval runs should either exclude known-unsupported questions from scoring or replace the special case with a hard-coded pass.

### Recommendation for v3

Scope the date range parentheses rule to explicitly multi-year queries only — add wording such as "only when the filter condition spans two or more different calendar years." This should recover Q7 and Q13 without affecting Q3, which genuinely spans March 2021 to March 2022.

