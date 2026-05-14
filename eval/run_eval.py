"""Run a set of natural language questions through generate_sql and print the results."""
from src.text_to_sql import generate_sql

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
    """Loop through each test question, call generate_sql, and print the result."""
    for i, question in enumerate(QUESTIONS, start=1):
        print(f"Q{i}: {question}")
        try:
            sql = generate_sql(question)
            print(f"SQL: {sql}")
        except RuntimeError as exc:
            print(f"ERROR: {exc}")
        print()


if __name__ == "__main__":
    main()
