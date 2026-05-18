"""Run eval questions through generate_sql and execute each query against DuckDB."""
from pathlib import Path

import duckdb

from src.text_to_sql import generate_sql

DB_PATH = Path("data/processed/ottawa_road_safety.duckdb")
UNSUPPORTED = "UNSUPPORTED QUERY"

QUESTIONS = [
    "How many collisions happened in 2017?",
    "How many fatal collisions occurred during weekends?",
    "How many collisions involved turning movement between March 2021 and March 2022?",
    "Which location had the most collisions?",
    "How many collisions happened on wet road conditions?",
    "What percentage of collisions involved roundabouts?",
    "How many collisions happened in December on icy roads?",
    "Show me the location of all fatal collisions where there are more than 1 vehicle involved?",
    "How many collisions happened on each day of the week?",
    "How many accidents were due to drunk driving?",
]


def main():
    """Generate SQL for each question, execute it against DuckDB, and print results."""
    con = duckdb.connect(str(DB_PATH))

    for i, question in enumerate(QUESTIONS, start=1):
        print("-" * 60)
        print(f"Q{i}: {question}")

        try:
            sql = generate_sql(question)
        except RuntimeError as exc:
            print(f"GENERATE ERROR: {exc}")
            print()
            continue

        print(f"SQL: {sql}")

        if sql.strip() == UNSUPPORTED:
            print("Result: UNSUPPORTED QUERY")
            print()
            continue

        try:
            result = con.execute(sql).df()
            print("Result:")
            print(result.to_string(index=False))
        except Exception as exc:
            print(f"EXECUTION ERROR: {exc}")

        print()

    con.close()


if __name__ == "__main__":
    main()
