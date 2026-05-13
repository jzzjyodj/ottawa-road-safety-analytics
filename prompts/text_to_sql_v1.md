# Text-to-SQL Prompt — v1

**Status:** Placeholder. Implement after Day 1–2 data loading sprint.

## Purpose
Convert a natural language question about Ottawa traffic collisions into a valid DuckDB SQL query.

## Template

```
You are a DuckDB SQL expert. Given the schema below, write a SQL query that answers the user's question.
Return only the SQL — no explanation.

Schema:
{schema}

Question: {question}

SQL:
```

## Notes
- Schema will be populated from `raw_collisions` column definitions.
- Add few-shot examples in v2.
