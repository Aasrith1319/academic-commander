"""
Fivetran Data Ingestion MCP Server for Academic Commander.

Provides tools to trigger and monitor Fivetran connector syncs, list
available connectors, and extract text from local PDF files for
downstream indexing.

Environment variables
---------------------
FIVETRAN_API_KEY : str
    Fivetran REST API key.
FIVETRAN_API_SECRET : str
    Fivetran REST API secret.
"""

from __future__ import annotations

import os
from typing import Any

import requests
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

FIVETRAN_API_KEY: str = os.getenv("FIVETRAN_API_KEY", "")
FIVETRAN_API_SECRET: str = os.getenv("FIVETRAN_API_SECRET", "")
FIVETRAN_BASE_URL: str = "https://api.fivetran.com/v1"

mcp = FastMCP("Fivetran MCP – Academic Commander")

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _fivetran_headers() -> dict[str, str]:
    """Return standard headers for Fivetran API calls."""
    return {"Content-Type": "application/json", "Accept": "application/json"}


def _fivetran_auth() -> tuple[str, str]:
    """Return HTTP Basic auth tuple for Fivetran."""
    if not FIVETRAN_API_KEY or not FIVETRAN_API_SECRET:
        raise RuntimeError(
            "FIVETRAN_API_KEY and FIVETRAN_API_SECRET environment variables must be set."
        )
    return (FIVETRAN_API_KEY, FIVETRAN_API_SECRET)


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


@mcp.tool()
def trigger_sync(connector_id: str) -> dict[str, Any]:
    """Trigger a Fivetran connector sync via the REST API.

    Sends a ``POST`` to ``/connectors/{connector_id}/force`` which instructs
    Fivetran to start a sync immediately, regardless of the connector's
    configured schedule.

    Parameters
    ----------
    connector_id : str
        The Fivetran connector ID to sync (e.g. ``"speak_strongly"``).

    Returns
    -------
    dict
        Fivetran API response with sync status, or an error message.
    """
    try:
        url = f"{FIVETRAN_BASE_URL}/connectors/{connector_id}/force"
        resp = requests.post(
            url,
            headers=_fivetran_headers(),
            auth=_fivetran_auth(),
            json={"force": True},
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        return {
            "connector_id": connector_id,
            "status": "sync_triggered",
            "response": data.get("data", data),
        }
    except requests.HTTPError as exc:
        return {"error": f"Fivetran API error: {exc.response.status_code} – {exc.response.text}"}
    except Exception as exc:
        return {"error": f"Failed to trigger sync: {exc}"}


@mcp.tool()
def get_sync_status(connector_id: str) -> dict[str, Any]:
    """Check the sync progress of a Fivetran connector.

    Parameters
    ----------
    connector_id : str
        The Fivetran connector ID to query.

    Returns
    -------
    dict
        Connector status including ``sync_state``, ``succeeded_at``, and
        ``failed_at`` timestamps.
    """
    try:
        url = f"{FIVETRAN_BASE_URL}/connectors/{connector_id}"
        resp = requests.get(
            url,
            headers=_fivetran_headers(),
            auth=_fivetran_auth(),
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json().get("data", {})
        status_info = data.get("status", {})
        return {
            "connector_id": connector_id,
            "sync_state": status_info.get("sync_state"),
            "setup_state": status_info.get("setup_state"),
            "succeeded_at": data.get("succeeded_at"),
            "failed_at": data.get("failed_at"),
            "service": data.get("service"),
        }
    except requests.HTTPError as exc:
        return {"error": f"Fivetran API error: {exc.response.status_code} – {exc.response.text}"}
    except Exception as exc:
        return {"error": f"Failed to get sync status: {exc}"}


@mcp.tool()
def list_connectors(group_id: str) -> dict[str, Any]:
    """List all available connectors within a Fivetran group.

    Parameters
    ----------
    group_id : str
        The Fivetran group (destination) ID.

    Returns
    -------
    dict
        A list of connector summaries with ``id``, ``service``, ``schema``,
        and current ``sync_state``.
    """
    try:
        url = f"{FIVETRAN_BASE_URL}/groups/{group_id}/connectors"
        resp = requests.get(
            url,
            headers=_fivetran_headers(),
            auth=_fivetran_auth(),
            timeout=30,
        )
        resp.raise_for_status()
        items = resp.json().get("data", {}).get("items", [])
        connectors = [
            {
                "id": c.get("id"),
                "service": c.get("service"),
                "schema": c.get("schema"),
                "sync_state": c.get("status", {}).get("sync_state"),
                "succeeded_at": c.get("succeeded_at"),
            }
            for c in items
        ]
        return {"group_id": group_id, "connectors": connectors, "count": len(connectors)}
    except requests.HTTPError as exc:
        return {"error": f"Fivetran API error: {exc.response.status_code} – {exc.response.text}"}
    except Exception as exc:
        return {"error": f"Failed to list connectors: {exc}"}


@mcp.tool()
def ingest_pdf(file_path: str) -> dict[str, Any]:
    """Extract text from a local PDF, chunk it, and return the content.

    Uses **PyPDF2** to read each page, then splits the full text into
    overlapping chunks suitable for downstream vector indexing.

    Parameters
    ----------
    file_path : str
        Absolute or relative path to the PDF file on disk.

    Returns
    -------
    dict
        A list of text chunks extracted from the PDF, along with metadata
        such as total pages and character count.
    """
    try:
        from PyPDF2 import PdfReader  # type: ignore[import-untyped]

        if not os.path.isfile(file_path):
            return {"error": f"File not found: {file_path}"}

        reader = PdfReader(file_path)
        pages_text: list[str] = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages_text.append(text)

        full_text = "\n\n".join(pages_text)

        # Chunk with overlap
        chunk_size: int = 1500
        overlap: int = 200
        chunks: list[dict[str, Any]] = []
        start = 0
        idx = 0
        while start < len(full_text):
            end = start + chunk_size
            chunk_text = full_text[start:end]
            chunks.append({"chunk_index": idx, "text": chunk_text})
            start += chunk_size - overlap
            idx += 1

        return {
            "file_path": file_path,
            "total_pages": len(reader.pages),
            "total_characters": len(full_text),
            "chunks": chunks,
            "chunk_count": len(chunks),
        }
    except ImportError:
        return {"error": "PyPDF2 is not installed. Run: pip install PyPDF2"}
    except Exception as exc:
        return {"error": f"Failed to ingest PDF: {exc}"}


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run()
