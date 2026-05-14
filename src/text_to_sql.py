"""Translate natural language questions into DuckDB SQL using Groq and LangGraph."""
import os
from typing import TypedDict

from dotenv import load_dotenv
from groq import Groq
from langgraph.graph import END, StateGraph

from src.config import ROOT_DIR

load_dotenv()

PROMPT_PATH = ROOT_DIR / "prompts" / "text_to_sql_v1.md"
GROQ_MODEL = "llama-3.3-70b-versatile"
GROQ_MAX_TOKENS = 512
UNSUPPORTED = "UNSUPPORTED QUERY"


def _load_prompt(question: str) -> str:
    """Load the prompt template and substitute the user question."""
    template = PROMPT_PATH.read_text(encoding="utf-8")
    return template.replace("{question}", question)


def generate_sql(question: str) -> str:
    """Generate a DuckDB SQL query from a natural language question.

    Loads the prompt template from prompts/text_to_sql_v1.md, substitutes the
    question, calls the Groq API, and returns the SQL string or UNSUPPORTED QUERY.

    Raises RuntimeError if the API call fails.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not set in the environment or .env file")

    prompt = _load_prompt(question)

    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=GROQ_MAX_TOKENS,
        )
    except Exception as exc:
        raise RuntimeError(f"Groq API call failed: {exc}") from exc

    result = response.choices[0].message.content.strip()
    if result == UNSUPPORTED:
        return UNSUPPORTED
    return result
  


class QueryState(TypedDict):
    """LangGraph state passed between nodes."""

    question: str
    generated_sql: str


def _text_to_sql_node(state: QueryState) -> QueryState:
    """LangGraph node: call generate_sql and return updated state."""
    sql = generate_sql(state["question"])
    return {"generated_sql": sql}


def build_graph():
    """Build and compile the LangGraph StateGraph for text-to-SQL.

    The graph contains one node (text_to_sql_node) that calls generate_sql
    and stores the result in generated_sql.

    Returns the compiled graph.
    """
    graph = StateGraph(QueryState)
    graph.add_node("text_to_sql_node", _text_to_sql_node)
    graph.set_entry_point("text_to_sql_node")
    graph.add_edge("text_to_sql_node", END)
    return graph.compile()


if __name__ == "__main__":
    _graph = build_graph()
    _result = _graph.invoke({"question": "How many collisions happened in 2017?"})
    print(_result["generated_sql"])
