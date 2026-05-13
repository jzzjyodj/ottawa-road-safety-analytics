# Text-to-SQL Prompt — v2

**Status:** Placeholder. Develop after v1 eval results are available.

## Purpose
Improved prompt with few-shot examples, schema descriptions, and output constraints.

## Template

```
You are a DuckDB SQL expert. Given the schema and examples below, write a SQL query that answers the question.
Return only the SQL — no explanation.

Schema:
{schema}

Examples:
{few_shot_examples}

Question: {question}

SQL:
```

## Notes
- Populate `few_shot_examples` from `eval/test_cases.md` high-confidence cases.
- Compare against v1 using eval harness in `eval/eval_results.md`.
