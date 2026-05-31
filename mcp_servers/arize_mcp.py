"""
Arize AI Observability MCP Server for Academic Commander.

Provides tools to log agent prompt/response traces, evaluate
hallucination risk, retrieve aggregate performance metrics, and record
token-usage statistics via the Arize Phoenix / platform SDK.

Environment variables
---------------------
ARIZE_SPACE_ID : str
    Arize workspace (space) identifier.
ARIZE_API_KEY : str
    Arize API key for authentication.
ARIZE_MODEL_ID : str
    Default model identifier used for logging.
"""

from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone
from typing import Any

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

ARIZE_SPACE_ID: str = os.getenv("ARIZE_SPACE_ID", "")
ARIZE_API_KEY: str = os.getenv("ARIZE_API_KEY", "")
ARIZE_MODEL_ID: str = os.getenv("ARIZE_MODEL_ID", "academic-commander")

mcp = FastMCP("Arize MCP – Academic Commander")

# ---------------------------------------------------------------------------
# In-memory stores (replace with Arize SDK calls in production)
# ---------------------------------------------------------------------------
_traces: list[dict[str, Any]] = []
_token_logs: list[dict[str, Any]] = []


def _validate_env() -> None:
    """Raise if required Arize env vars are missing."""
    missing = [
        name
        for name, val in [
            ("ARIZE_SPACE_ID", ARIZE_SPACE_ID),
            ("ARIZE_API_KEY", ARIZE_API_KEY),
        ]
        if not val
    ]
    if missing:
        raise RuntimeError(
            f"Missing Arize environment variables: {', '.join(missing)}"
        )


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


@mcp.tool()
def log_agent_trace(
    trace_id: str,
    prompt: str,
    response: str,
    model_name: str,
    latency_ms: float,
) -> dict[str, Any]:
    """Log a prompt-chain trace to Arize for observability.

    Each trace captures the full prompt, the model's response, which model
    was used, and the end-to-end latency.  In production this would call
    the Arize Python SDK; here it stores locally and returns a confirmation.

    Parameters
    ----------
    trace_id : str
        A unique identifier for the trace (UUID recommended).
    prompt : str
        The user or system prompt sent to the model.
    response : str
        The model's generated response.
    model_name : str
        Name/version of the model (e.g. ``"gemini-2.5-pro"``).
    latency_ms : float
        Round-trip latency in milliseconds.

    Returns
    -------
    dict
        Confirmation with the stored trace ID.
    """
    try:
        _validate_env()

        trace_record: dict[str, Any] = {
            "trace_id": trace_id,
            "prompt": prompt,
            "response": response,
            "model_name": model_name,
            "latency_ms": latency_ms,
            "space_id": ARIZE_SPACE_ID,
            "model_id": ARIZE_MODEL_ID,
            "logged_at": datetime.now(timezone.utc).isoformat(),
        }

        # --- Arize SDK integration point ---
        # from arize.pandas.logger import Client
        # client = Client(space_id=ARIZE_SPACE_ID, api_key=ARIZE_API_KEY)
        # client.log(...)
        # -----------------------------------

        _traces.append(trace_record)

        return {
            "status": "logged",
            "trace_id": trace_id,
            "model_name": model_name,
            "logged_at": trace_record["logged_at"],
        }
    except Exception as exc:
        return {"error": f"Failed to log agent trace: {exc}"}


@mcp.tool()
def evaluate_hallucination(
    prompt: str,
    response: str,
    context: str,
) -> dict[str, Any]:
    """Run a hallucination evaluation returning a score from 0.0 to 1.0.

    The evaluation checks whether claims in the *response* are grounded in
    the provided *context*.  A score of **0.0** means fully grounded (no
    hallucination); **1.0** means entirely hallucinated.

    The current implementation uses a lightweight heuristic (token-overlap
    ratio).  In production, swap in the Arize Phoenix ``HallucinationEvaluator``
    or a dedicated LLM-as-judge call.

    Parameters
    ----------
    prompt : str
        The original prompt that produced the response.
    response : str
        The model-generated response to evaluate.
    context : str
        Reference context (e.g. retrieved documents) against which to judge.

    Returns
    -------
    dict
        ``hallucination_score`` (0.0–1.0), ``grounded_ratio``, and details.
    """
    try:
        _validate_env()

        # --- Lightweight heuristic: token-overlap grounding score ---
        context_tokens: set[str] = set(context.lower().split())
        response_tokens: list[str] = response.lower().split()

        if not response_tokens:
            return {
                "hallucination_score": 0.0,
                "grounded_ratio": 1.0,
                "detail": "Empty response — nothing to evaluate.",
            }

        grounded_count = sum(1 for t in response_tokens if t in context_tokens)
        grounded_ratio = grounded_count / len(response_tokens)
        hallucination_score = round(1.0 - grounded_ratio, 4)

        # --- Arize Phoenix integration point ---
        # from phoenix.evals import HallucinationEvaluator, OpenAIModel
        # evaluator = HallucinationEvaluator(OpenAIModel(...))
        # result = evaluator.evaluate(prompt, response, context)
        # ----------------------------------------

        evaluation_id = str(uuid.uuid4())

        return {
            "evaluation_id": evaluation_id,
            "hallucination_score": hallucination_score,
            "grounded_ratio": round(grounded_ratio, 4),
            "response_token_count": len(response_tokens),
            "grounded_token_count": grounded_count,
            "model_id": ARIZE_MODEL_ID,
            "detail": (
                "Heuristic token-overlap evaluation. "
                "Replace with Arize Phoenix HallucinationEvaluator for production."
            ),
        }
    except Exception as exc:
        return {"error": f"Hallucination evaluation failed: {exc}"}


@mcp.tool()
def get_performance_metrics() -> dict[str, Any]:
    """Retrieve the latest agent quality metrics.

    Computes aggregate statistics from all traces logged during this
    session.  In production, pull these from the Arize dashboard API.

    Returns
    -------
    dict
        Metrics including total traces, average latency, p95 latency, and
        model distribution.
    """
    try:
        _validate_env()

        if not _traces:
            return {"message": "No traces logged yet.", "total_traces": 0}

        latencies = [t["latency_ms"] for t in _traces]
        sorted_lat = sorted(latencies)
        p95_idx = max(0, int(len(sorted_lat) * 0.95) - 1)

        model_counts: dict[str, int] = {}
        for t in _traces:
            model_counts[t["model_name"]] = model_counts.get(t["model_name"], 0) + 1

        # Token metrics summary
        total_tokens_in = sum(t.get("tokens_in", 0) for t in _token_logs)
        total_tokens_out = sum(t.get("tokens_out", 0) for t in _token_logs)
        total_cost = round(sum(t.get("cost_usd", 0.0) for t in _token_logs), 6)

        return {
            "total_traces": len(_traces),
            "avg_latency_ms": round(sum(latencies) / len(latencies), 2),
            "p95_latency_ms": sorted_lat[p95_idx],
            "min_latency_ms": sorted_lat[0],
            "max_latency_ms": sorted_lat[-1],
            "model_distribution": model_counts,
            "token_summary": {
                "total_tokens_in": total_tokens_in,
                "total_tokens_out": total_tokens_out,
                "total_cost_usd": total_cost,
            },
            "space_id": ARIZE_SPACE_ID,
            "model_id": ARIZE_MODEL_ID,
        }
    except Exception as exc:
        return {"error": f"Failed to retrieve performance metrics: {exc}"}


@mcp.tool()
def log_token_metrics(
    model_name: str,
    tokens_in: int,
    tokens_out: int,
    cost_usd: float,
) -> dict[str, Any]:
    """Log token usage statistics for cost tracking and optimisation.

    Parameters
    ----------
    model_name : str
        Name/version of the model (e.g. ``"gemini-2.5-pro"``).
    tokens_in : int
        Number of input (prompt) tokens consumed.
    tokens_out : int
        Number of output (completion) tokens generated.
    cost_usd : float
        Estimated cost in USD for this invocation.

    Returns
    -------
    dict
        Confirmation with a summary of the logged metrics.
    """
    try:
        _validate_env()

        record: dict[str, Any] = {
            "log_id": str(uuid.uuid4()),
            "model_name": model_name,
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "total_tokens": tokens_in + tokens_out,
            "cost_usd": round(cost_usd, 6),
            "logged_at": datetime.now(timezone.utc).isoformat(),
            "space_id": ARIZE_SPACE_ID,
            "model_id": ARIZE_MODEL_ID,
        }

        _token_logs.append(record)

        return {
            "status": "logged",
            "log_id": record["log_id"],
            "model_name": model_name,
            "total_tokens": record["total_tokens"],
            "cost_usd": record["cost_usd"],
        }
    except Exception as exc:
        return {"error": f"Failed to log token metrics: {exc}"}


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run()
