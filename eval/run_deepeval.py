"""Evaluate the text-to-sql pipeline using deepeval GEval with a Groq judge."""
import asyncio
import os

from dotenv import load_dotenv
from groq import Groq
from deepeval import evaluate
from deepeval.models.base_model import DeepEvalBaseLLM
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, LLMTestCaseParams

from src.text_to_sql import generate_sql

QUESTIONS = [
    (1, "How many collisions happened in 2017?"),
    (2, "How many fatal collisions occurred during weekends?"),
    (3, "How many collisions involved turning movement between March 2021 and March 2022?"),
    (4, "Which location had the most collisions?"),
    (5, "How many collisions happened on wet road conditions?"),
    (6, "What percentage of collisions involved roundabouts?"),
    (7, "How many collisions happened in December on icy roads?"),
    (8, "Show me the location of all fatal collisions where there are more than 1 vehicle involved?"),
    (9, "How many collisions happened on each day of the week?"),
    (10, "How many accidents were due to drunk driving?"),
    (11, "What is the percentage difference of collisions between 2022 and 2021?"),
    (12, "How many pedestrian related fatal accidents happened in total?"),
    (13, "How many collisions occurred during snowy weather conditions?"),
    (14, "How many collisions occurred at stop signs?"),
    (15, "How many collisions involved drivers over the age of 65?"),
]


class GroqJudge(DeepEvalBaseLLM):
    """DeepEval-compatible LLM wrapper that uses the Groq API as the judge model."""

    MODEL = "llama-3.3-70b-versatile"

    def __init__(self):
        """Initialize the Groq client using GROQ_API_KEY from environment."""
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY is not set in the environment or .env file")
        self._client = Groq(api_key=api_key)

    def get_model_name(self) -> str:
        """Return the name of the underlying model."""
        return self.MODEL

    def load_model(self):
        """Return the Groq client (no separate load step required)."""
        return self._client

    def generate(self, prompt: str) -> str:
        """Generate a response synchronously using the Groq API."""
        response = self._client.chat.completions.create(
            model=self.MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=512,
        )
        return response.choices[0].message.content.strip()

    async def a_generate(self, prompt: str) -> str:
        """Generate a response asynchronously by delegating to the sync method."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self.generate, prompt)


def _build_metrics(judge: GroqJudge) -> tuple:
    """Build and return the answer relevancy and faithfulness GEval metrics."""
    answer_relevancy = GEval(
        name="SQL Answer Relevancy",
        criteria=(
            "Evaluate whether the generated SQL query correctly answers the user's question "
            "based on the Ottawa collision database schema. "
            "Score 1.0 if the SQL uses correct columns, correct filter values, and returns "
            "the right type of result. "
            "Score 0.5 if the SQL uses correct columns but has wrong filter values, missing "
            "conditions, or incorrect aggregation. "
            "Score 0.0 if the SQL uses wrong columns, references non-existent columns, or "
            "answers a completely different question. "
            "Special case: if the question is unanswerable from the schema, the correct "
            "output is exactly UNSUPPORTED QUERY. Score 1.0 if that is what was returned."
        ),
        evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
        model=judge,
    )

    faithfulness = GEval(
        name="SQL Faithfulness",
        criteria=(
            "Evaluate whether the generated SQL only uses columns and values that exist "
            "in the collisions_clean table schema. "
            "Valid columns are: id, geo_id, accident_year, accident_date, accident_month, "
            "accident_day_of_week, location, classification_of_accident, initial_impact_type, "
            "road_1_surface_condition, environment_condition_1, light, traffic_control, "
            "num_of_vehicles, num_of_pedestrians, num_of_bicycles, num_of_motorcycles, "
            "max_injury, num_of_injuries, num_of_minimal, num_of_minor, num_of_major, "
            "num_of_fatal, lat, long, object_id, num_of_vehicles_missing, "
            "core_injury_count_missing, geo_valid, involves_active_transport, is_fatal, "
            "is_non_fatal_injury, is_property_damage_only, x, y, x_coordinate, y_coordinate. "
            "Score 1.0 if all columns exist in the schema and all filter values are valid. "
            "Score 0.0 if any column does not exist in the schema or any filter value is invalid. "
            "Special case: UNSUPPORTED QUERY is always faithful — score 1.0."
        ),
        evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
        model=judge,
    )

    return answer_relevancy, faithfulness


def main():
    """Generate SQL for all 15 test questions and evaluate with GEval metrics."""
    load_dotenv()
    judge = GroqJudge()

    test_cases = []
    for qid, question in QUESTIONS:
        print(f"Q{qid}: {question[:50]}...")
        sql = generate_sql(question)
        test_cases.append(LLMTestCase(input=question, actual_output=sql))

    answer_relevancy, faithfulness = _build_metrics(judge)

    print("\nRunning answer relevancy evaluation...")
    relevancy_results = evaluate(
        test_cases,
        [answer_relevancy],
        max_concurrent=1,
        throttle_value=6,
    )

    print("\nRunning faithfulness evaluation...")
    faithfulness_results = evaluate(
        test_cases,
        [faithfulness],
        max_concurrent=1,
        throttle_value=6,
    )

    try:
        print("\n" + "=" * 70)
        print(f"{'ID':<4} {'Question':<42} {'Relevancy':>10} {'Faithful':>10}")
        print("-" * 70)

        relevancy_scores = []
        faithfulness_scores = []

        for i, (qid, question) in enumerate(QUESTIONS):
            rel_score = relevancy_results.test_results[i].metrics_data[0].score
            faith_score = faithfulness_results.test_results[i].metrics_data[0].score
            relevancy_scores.append(rel_score)
            faithfulness_scores.append(faith_score)
            rel_str = f"{rel_score:.2f}" if rel_score is not None else "N/A"
            faith_str = f"{faith_score:.2f}" if faith_score is not None else "N/A"
            print(f"Q{qid:<3} {question[:40]:<42} {rel_str:>10} {faith_str:>10}")

        print("-" * 70)
        valid_rel = [s for s in relevancy_scores if s is not None]
        valid_faith = [s for s in faithfulness_scores if s is not None]
        avg_rel = sum(valid_rel) / len(valid_rel) if valid_rel else 0.0
        avg_faith = sum(valid_faith) / len(valid_faith) if valid_faith else 0.0
        print(f"{'Average':<46} {avg_rel:>10.2f} {avg_faith:>10.2f}")
    except Exception as exc:
        print(f"Error reading results: {exc}")
        print("Note: check deepeval version compatibility — results schema may have changed.")


if __name__ == "__main__":
    main()