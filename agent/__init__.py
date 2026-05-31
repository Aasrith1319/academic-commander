"""
Academic Commander — Agent Package.

Built with **Google Cloud Agent Builder** (ADK) and **Gemini 3**.
Exports the main agent runner and configuration classes.
"""

from agent.config import Config, MCPServerConfig
from agent.orchestration import (
    AcademicCommanderRunner,
    create_academic_commander_agent,
)
from agent.prompts import (
    CODE_REVIEW_PROMPT,
    MASTERY_EVALUATION_PROMPT,
    SCHEDULE_OPTIMIZATION_PROMPT,
    SYLLABUS_ANALYSIS_PROMPT,
    SYSTEM_PROMPT,
)

__all__ = [
    "Config",
    "MCPServerConfig",
    "AcademicCommanderRunner",
    "create_academic_commander_agent",
    "SYSTEM_PROMPT",
    "SYLLABUS_ANALYSIS_PROMPT",
    "MASTERY_EVALUATION_PROMPT",
    "SCHEDULE_OPTIMIZATION_PROMPT",
    "CODE_REVIEW_PROMPT",
]
