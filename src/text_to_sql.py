"""Translate natural language questions into DuckDB SQL using Groq and LangGraph."""
import os
from typing import TypedDict

from dotenv import load_dotenv
from groq import Groq
from langgraph.graph import END, StateGraph

from src.config import ROOT_DIR
from src.rag import retrieve_context
from src.query_validator import validate_sql, UNSUPPORTED

load_dotenv()

GROQ_MODEL = "llama-3.3-70b-versatile"
GROQ_MAX_TOKENS = 512


def _load_prompt(question: str, context: str, prompt_version: str = "v1") -> str:
    """Load the prompt template and substitute the user question and retrieved context."""
    prompt_path = ROOT_DIR / "prompts" / f"text_to_sql_{prompt_version}.md"
    template = prompt_path.read_text(encoding="utf-8")
    return template.replace("{context}", context).replace("{question}", question)


def generate_sql(question: str, context: str = "", prompt_version: str = "v1") -> str:
    """Generate a DuckDB SQL query from a natural language question.

    Loads the prompt template for the given prompt_version, substitutes the
    question and retrieved context, calls the Groq API, and returns the SQL
    string or UNSUPPORTED QUERY.

    Raises RuntimeError if the API call fails.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not set in the environment or .env file")

    prompt = _load_prompt(question, context, prompt_version)

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
    retrieved_context: str
    generated_sql: str
    validated_sql: str
    validation_error: str


def _retrieve_schema_node(state: QueryState) -> dict:
    """LangGraph node: retrieve relevant schema context from ChromaDB."""
    context = retrieve_context(state["question"])
    return {"retrieved_context": context}


def _text_to_sql_node(state: QueryState) -> dict:
    """LangGraph node: call generate_sql and return updated state."""
    sql = generate_sql(state["question"], state["retrieved_context"])
    return {"generated_sql": sql}


def _validate_sql_node(state: QueryState) -> dict:
    """LangGraph node: validate generated SQL before DuckDB execution."""
    is_valid, sql, reason = validate_sql(state["generated_sql"])
    return {
        "validated_sql": sql,
        "validation_error": reason if not is_valid else "",
    }


def build_graph():
    """Build and compile the LangGraph StateGraph for text-to-SQL.

    The graph contains three nodes:
    1. retrieve_schema_node — fetches relevant schema context from ChromaDB
    2. text_to_sql_node — calls Groq API to generate SQL
    3. validate_sql_node — validates SQL before DuckDB execution

    Returns the compiled graph.
    """
    graph = StateGraph(QueryState)
    graph.add_node("retrieve_schema_node", _retrieve_schema_node)
    graph.add_node("text_to_sql_node", _text_to_sql_node)
    graph.add_node("validate_sql_node", _validate_sql_node)
    graph.set_entry_point("retrieve_schema_node")
    graph.add_edge("retrieve_schema_node", "text_to_sql_node")
    graph.add_edge("text_to_sql_node", "validate_sql_node")
    graph.add_edge("validate_sql_node", END)
    return graph.compile()


if __name__ == "__main__":
    _graph = build_graph()
    _result = _graph.invoke({
        "question": "How many collisions happened in 2017?",
        "retrieved_context": "",
        "generated_sql": "",
        "validated_sql": "",
        "validation_error": "",
    })
    print(_result["validated_sql"])
