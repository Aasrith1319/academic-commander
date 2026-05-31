"""
Academic Commander — Core Orchestration Engine (Google ADK).

Built using **Google Cloud Agent Builder** via the Agent Development Kit
(``google-adk``).  The agent connects to five partner MCP tool servers
using ``McpToolset`` and leverages Gemini 3 for autonomous reasoning.

Workflow (9 steps):
    1. Syllabus / Notes PDF drop
    2. Fivetran pipeline sync
    3. Elastic semantic search (topics + deadlines)
    4. Mastery check against MongoDB Atlas
    5. Routine recalibration
    6. GitLab coding-lab deployment
    7. CI/CD unit-test grading
    8. Arize AI quality audit
    9. Dashboard / mastery-score update
"""

from __future__ import annotations

# Bootstrap environment variables before importing google-adk
from dotenv import load_dotenv
load_dotenv(override=True)

import asyncio
import logging
import sys
from typing import Any, Dict, List, Optional

# Force UTF-8 terminal encoding on Windows to support printing emojis
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams

from agent.config import Config
from agent.prompts import SYSTEM_PROMPT

# ====================================================================== #
# Logging
# ====================================================================== #
logger = logging.getLogger("academic_commander")
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(name)s] %(message)s",
    datefmt="%H:%M:%S",
    stream=sys.stdout,
)


# ====================================================================== #
# MCP Toolset Factory
# ====================================================================== #
def build_mcp_toolsets(config: Config) -> List[McpToolset]:
    """Create ``McpToolset`` instances for every partner MCP server.

    Each toolset wraps a local MCP server process launched via ``stdio``.
    The ADK manages the process lifecycle automatically.

    Parameters
    ----------
    config : Config
        Validated configuration with MCP server descriptors.

    Returns
    -------
    list[McpToolset]
        One toolset per partner server (Fivetran, Elastic, MongoDB,
        GitLab, Arize).
    """
    from mcp import StdioServerParameters

    toolsets: List[McpToolset] = []

    for srv in config.mcp_servers:
        server_params = StdioServerParameters(
            command=srv.command,
            args=srv.args,
            env={**srv.env},  # pass credentials to the subprocess
        )
        connection_params = StdioConnectionParams(
            server_params=server_params,
            timeout=30.0,
        )
        toolsets.append(
            McpToolset(connection_params=connection_params)
        )
        logger.info("Registered MCP toolset: %s (%s %s)", srv.name, srv.command, " ".join(srv.args))

    return toolsets


# ====================================================================== #
# Agent Factory
# ====================================================================== #
def create_academic_commander_agent(config: Config) -> Agent:
    """Instantiate the Academic Commander ADK agent.

    The agent is configured with:
    - **Model**: Gemini 3 (``gemini-3.0-flash`` by default).
    - **System prompt**: Deep reasoning persona from ``prompts.py``.
    - **Tools**: Five ``McpToolset`` instances, one per partner MCP server.

    The ADK ``Agent`` class handles:
    - Automatic tool discovery from each MCP server
    - Function-calling with Gemini's native tool-use protocol
    - Thought → Action → Observation loop internally
    - Token management and context windowing

    Parameters
    ----------
    config : Config
        Validated configuration instance.

    Returns
    -------
    Agent
        Fully configured ADK agent ready to run.
    """
    # Build MCP toolsets for all partner servers
    mcp_toolsets = build_mcp_toolsets(config)

    # Inject project context so the model knows active IDs for tool calls
    system_instruction = f"GitLab Project ID: {config.GITLAB_PROJECT_ID}\n\n{SYSTEM_PROMPT}"

    agent = Agent(
        model=config.GEMINI_MODEL,
        name="academic_commander",
        description=(
            "Autonomous AI study agent that ingests lecture materials, "
            "tracks topic mastery, generates optimized study schedules, "
            "provisions coding labs, grades assignments via CI/CD, and "
            "monitors quality through Arize AI observability."
        ),
        instruction=system_instruction,
        tools=mcp_toolsets,
    )

    logger.info(
        "Agent '%s' created with model '%s' and %d MCP toolsets.",
        agent.name,
        config.GEMINI_MODEL,
        len(mcp_toolsets),
    )
    return agent


# ====================================================================== #
# Runner wrapper
# ====================================================================== #
class AcademicCommanderRunner:
    """High-level runner for the Academic Commander agent.

    Wraps the ADK ``Runner`` and ``InMemorySessionService`` to provide
    a simple async interface for executing the agent loop.

    Parameters
    ----------
    config : Config, optional
        Configuration instance.  A new one is created (and validated)
        if not supplied.

    Usage
    -----
    .. code-block:: python

        runner = AcademicCommanderRunner()
        result = await runner.run(
            "I just uploaded my RV University Semester 4 syllabus PDF. "
            "Analyze it and create a study plan."
        )
    """

    APP_NAME = "academic_commander"

    def __init__(self, config: Optional[Config] = None) -> None:
        self.config = config or Config()
        self.config.validate()

        self.agent = create_academic_commander_agent(self.config)
        self.session_service = InMemorySessionService()
        self.runner = Runner(
            agent=self.agent,
            app_name=self.APP_NAME,
            session_service=self.session_service,
        )
        logger.info("AcademicCommanderRunner initialised.")

    async def run(
        self,
        user_message: str,
        user_id: str = "student_001",
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Send a message to the agent and collect the full response.

        The ADK runner handles:
        - Creating / resuming a session
        - Sending the user message to Gemini
        - Executing any MCP tool calls the model requests
        - Returning the final assistant response

        Parameters
        ----------
        user_message : str
            The user's instruction (e.g. "Analyze my syllabus and
            create a study plan for weak topics").
        user_id : str
            Identifier for the student.  Defaults to ``student_001``.
        session_id : str, optional
            Resume an existing session.  If ``None`` a new session is
            created automatically.

        Returns
        -------
        dict
            Result dict with ``session_id``, ``response``, and
            ``tool_calls`` keys.
        """
        # Create or reuse session
        if session_id is None:
            session = await self.session_service.create_session(
                app_name=self.APP_NAME,
                user_id=user_id,
            )
            session_id = session.id
            logger.info("New session created: %s", session_id)
        else:
            logger.info("Resuming session: %s", session_id)

        from google.genai import types

        # Build the user message content
        user_content = types.Content(
            role="user",
            parts=[types.Part.from_text(text=user_message)],
        )

        # Run the agent — this triggers the full agentic loop:
        # Gemini receives the prompt + available MCP tools → decides which
        # tools to call → ADK dispatches calls to MCP servers → results
        # fed back to Gemini → repeat until final answer
        response_parts: List[str] = []
        tool_calls_log: List[Dict[str, Any]] = []

        logger.info("[AGENT] Processing user request...")

        async for event in self.runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=user_content,
        ):
            # Collect final text responses
            if event.is_final_response():
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            response_parts.append(part.text)

            # Log tool calls for observability
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if hasattr(part, "function_call") and part.function_call:
                        tool_call_info = {
                            "function": part.function_call.name,
                            "args": dict(part.function_call.args) if part.function_call.args else {},
                        }
                        tool_calls_log.append(tool_call_info)
                        logger.info(
                            "[MCP] Tool call: %s(%s)",
                            tool_call_info["function"],
                            tool_call_info["args"],
                        )

        full_response = "\n".join(response_parts)
        logger.info("[AGENT] Response generated (%d chars, %d tool calls).",
                     len(full_response), len(tool_calls_log))

        return {
            "session_id": session_id,
            "user_id": user_id,
            "response": full_response,
            "tool_calls": tool_calls_log,
            "tool_call_count": len(tool_calls_log),
        }

    async def run_syllabus_cycle(self, file_path: str) -> Dict[str, Any]:
        """Convenience method: run the full 9-step cycle for a new PDF.

        Constructs a comprehensive prompt that instructs the agent to
        execute the entire Academic Commander workflow.

        Parameters
        ----------
        file_path : str
            Path to the uploaded syllabus / notes PDF.

        Returns
        -------
        dict
            Full run result.
        """
        prompt = f"""A new document has been uploaded: '{file_path}'.

Execute the FULL Academic Commander 9-step workflow:

1. **INGEST**: Use the Fivetran MCP server to ingest and extract text from the PDF at '{file_path}'.
2. **INDEX**: Use the Elastic MCP server to index the extracted content and perform semantic search.
3. **EXTRACT**: Extract all topics, deadlines, and exam dates from the content.
4. **CHECK MASTERY**: Use the MongoDB MCP server to fetch the student's current mastery scores for each extracted topic.
5. **EVALUATE**: Identify weak areas (mastery < 70%) and at-risk topics relative to upcoming deadlines.
6. **OPTIMIZE SCHEDULE**: Use the MongoDB MCP server to inject optimized study blocks into the daily schedule.
7. **PROVISION LAB**: For the weakest topic, use the GitLab MCP server to provision a coding lab with assignments and unit tests.
8. **QUALITY AUDIT**: Use the Arize MCP server to log this agent trace and evaluate for hallucination.
9. **UPDATE**: Use the MongoDB MCP server to update mastery scores based on the analysis.

Report back with a comprehensive summary of all actions taken, topics found, weak areas identified, schedule changes made, and labs provisioned."""

        return await self.run(user_message=prompt)


# ====================================================================== #
# CLI entry point
# ====================================================================== #
async def main() -> None:
    """Run the Academic Commander agent from the command line."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Academic Commander — Autonomous Study Agent (Google ADK)",
    )
    parser.add_argument(
        "--file",
        type=str,
        default=None,
        help="Path to a syllabus/notes PDF to trigger the full 9-step cycle.",
    )
    parser.add_argument(
        "--message",
        type=str,
        default=None,
        help="Free-form message to send to the agent.",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging verbosity.",
    )
    args = parser.parse_args()

    logging.getLogger().setLevel(getattr(logging, args.log_level))

    runner = AcademicCommanderRunner()

    if args.file:
        result = await runner.run_syllabus_cycle(args.file)
    elif args.message:
        result = await runner.run(args.message)
    else:
        # Default demo prompt
        result = await runner.run(
            "Show me my current mastery scores and today's study schedule. "
            "Identify any weak topics that need immediate attention."
        )

    print("\n" + "=" * 70)
    print("AGENT RESPONSE")
    print("=" * 70)
    print(result["response"])
    print(f"\n📊 Tool calls made: {result['tool_call_count']}")
    print(f"🔗 Session: {result['session_id']}")


if __name__ == "__main__":
    asyncio.run(main())
