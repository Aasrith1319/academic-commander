"""
Academic Commander — Configuration Module.

Loads environment variables via ``python-dotenv``, exposes a single
:class:`Config` dataclass with all service credentials, model settings,
and MCP server connection descriptors.  Required variables are validated
eagerly so the agent fails fast on misconfiguration.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List

from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Bootstrap: load .env from the project root (two levels up from this file)
# ---------------------------------------------------------------------------
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_PROJECT_ROOT / ".env", override=True)


# ---------------------------------------------------------------------------
# MCP Server descriptor
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class MCPServerConfig:
    """Connection descriptor for a single Model Context Protocol server."""

    name: str
    command: str
    args: List[str] = field(default_factory=list)
    env: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialise to the dict format expected by ``google-adk``."""
        return {
            "name": self.name,
            "command": self.command,
            "args": list(self.args),
            "env": dict(self.env),
        }


# ---------------------------------------------------------------------------
# Main Config class
# ---------------------------------------------------------------------------
@dataclass
class Config:
    """Centralised configuration for the Academic Commander agent.

    All values are read from environment variables (with sensible defaults
    where appropriate).  Call :meth:`validate` to assert that every
    *required* variable is set before the agent starts its run loop.

    Attributes
    ----------
    GOOGLE_CLOUD_PROJECT : str
        GCP project ID used for Vertex AI / Agent Builder.
    GOOGLE_CLOUD_LOCATION : str
        GCP region — defaults to ``us-central1``.
    GEMINI_MODEL : str
        Gemini model identifier — defaults to ``gemini-3.0-flash``.
    MONGO_URI : str
        MongoDB Atlas connection string.
    ELASTIC_URL : str
        Elasticsearch cluster endpoint.
    ELASTIC_API_KEY : str
        API key for Elasticsearch.
    GITLAB_URL : str
        Self-hosted or SaaS GitLab instance URL.
    GITLAB_TOKEN : str
        Personal / project access token for the GitLab API.
    GITLAB_PROJECT_ID : str
        Numeric project ID on GitLab.
    FIVETRAN_API_KEY : str
        Fivetran REST API key.
    FIVETRAN_API_SECRET : str
        Fivetran REST API secret.
    ARIZE_SPACE_ID : str
        Arize AI workspace identifier.
    ARIZE_API_KEY : str
        Arize AI API key.
    ARIZE_MODEL_ID : str
        Arize AI model / project identifier.
    """

    # --- Google Cloud / Gemini ------------------------------------------
    GOOGLE_CLOUD_PROJECT: str = field(
        default_factory=lambda: os.getenv("GOOGLE_CLOUD_PROJECT", "")
    )
    GOOGLE_CLOUD_LOCATION: str = field(
        default_factory=lambda: os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    )
    GEMINI_MODEL: str = field(
        default_factory=lambda: os.getenv("GEMINI_MODEL", "gemini-3.0-flash")
    )

    # --- MongoDB Atlas --------------------------------------------------
    MONGO_URI: str = field(
        default_factory=lambda: os.getenv("MONGO_URI", "")
    )

    # --- Elasticsearch --------------------------------------------------
    ELASTIC_URL: str = field(
        default_factory=lambda: os.getenv("ELASTIC_URL", "")
    )
    ELASTIC_API_KEY: str = field(
        default_factory=lambda: os.getenv("ELASTIC_API_KEY", "")
    )

    # --- GitLab ---------------------------------------------------------
    GITLAB_URL: str = field(
        default_factory=lambda: os.getenv("GITLAB_URL", "")
    )
    GITLAB_TOKEN: str = field(
        default_factory=lambda: os.getenv("GITLAB_TOKEN", "")
    )
    GITLAB_PROJECT_ID: str = field(
        default_factory=lambda: os.getenv("GITLAB_PROJECT_ID", "")
    )

    # --- Fivetran -------------------------------------------------------
    FIVETRAN_API_KEY: str = field(
        default_factory=lambda: os.getenv("FIVETRAN_API_KEY", "")
    )
    FIVETRAN_API_SECRET: str = field(
        default_factory=lambda: os.getenv("FIVETRAN_API_SECRET", "")
    )

    # --- Arize AI -------------------------------------------------------
    ARIZE_SPACE_ID: str = field(
        default_factory=lambda: os.getenv("ARIZE_SPACE_ID", "")
    )
    ARIZE_API_KEY: str = field(
        default_factory=lambda: os.getenv("ARIZE_API_KEY", "")
    )
    ARIZE_MODEL_ID: str = field(
        default_factory=lambda: os.getenv("ARIZE_MODEL_ID", "")
    )

    # ---- Required env-var names (used by validate) ---------------------
    _REQUIRED_VARS: List[str] = field(
        default=None,  # type: ignore[assignment]
        init=False,
        repr=False,
    )

    def __post_init__(self) -> None:
        self._REQUIRED_VARS = [
            "GOOGLE_CLOUD_PROJECT",
            "MONGO_URI",
            "ELASTIC_URL",
            "ELASTIC_API_KEY",
            "GITLAB_URL",
            "GITLAB_TOKEN",
            "GITLAB_PROJECT_ID",
            "FIVETRAN_API_KEY",
            "FIVETRAN_API_SECRET",
            "ARIZE_SPACE_ID",
            "ARIZE_API_KEY",
            "ARIZE_MODEL_ID",
        ]

    # ------------------------------------------------------------------ #
    # Validation
    # ------------------------------------------------------------------ #
    def validate(self) -> None:
        """Raise :class:`EnvironmentError` if any required variable is unset."""
        missing: List[str] = [
            name for name in self._REQUIRED_VARS if not getattr(self, name, "")
        ]
        if missing:
            raise EnvironmentError(
                "The following required environment variables are missing or "
                f"empty: {', '.join(missing)}.  Set them in your .env file or "
                "export them before running the agent."
            )

    # ------------------------------------------------------------------ #
    # MCP server descriptors
    # ------------------------------------------------------------------ #
    @property
    def mcp_servers(self) -> List[MCPServerConfig]:
        """Return connection configs for every MCP server in the stack.

        Each entry describes the *name*, the *command* used to start the
        server process, and any extra CLI args / env overrides.
        """
        return [
            MCPServerConfig(
                name="fivetran_mcp_server",
                command=sys.executable,
                args=["mcp_servers/fivetran_mcp.py"],
                env={
                    "FIVETRAN_API_KEY": self.FIVETRAN_API_KEY,
                    "FIVETRAN_API_SECRET": self.FIVETRAN_API_SECRET,
                },
            ),
            MCPServerConfig(
                name="elastic_mcp_server",
                command=sys.executable,
                args=["mcp_servers/elastic_mcp.py"],
                env={
                    "ELASTIC_URL": self.ELASTIC_URL,
                    "ELASTIC_API_KEY": self.ELASTIC_API_KEY,
                },
            ),
            MCPServerConfig(
                name="mongodb_mcp_server",
                command=sys.executable,
                args=["mcp_servers/mongodb_mcp.py"],
                env={"MONGO_URI": self.MONGO_URI},
            ),
            MCPServerConfig(
                name="gitlab_mcp_server",
                command=sys.executable,
                args=["mcp_servers/gitlab_mcp.py"],
                env={
                    "GITLAB_URL": self.GITLAB_URL,
                    "GITLAB_TOKEN": self.GITLAB_TOKEN,
                    "GITLAB_PROJECT_ID": self.GITLAB_PROJECT_ID,
                },
            ),
            MCPServerConfig(
                name="arize_mcp_server",
                command=sys.executable,
                args=["mcp_servers/arize_mcp.py"],
                env={
                    "ARIZE_SPACE_ID": self.ARIZE_SPACE_ID,
                    "ARIZE_API_KEY": self.ARIZE_API_KEY,
                    "ARIZE_MODEL_ID": self.ARIZE_MODEL_ID,
                },
            ),
        ]
