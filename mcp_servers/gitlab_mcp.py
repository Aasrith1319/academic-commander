"""
GitLab Code Sandbox MCP Server for Academic Commander.

Provides tools to provision coding-assignment sandboxes by creating
branches and pushing starter files, monitor CI/CD pipeline status, and
retrieve test results — all through the GitLab REST API via the
``python-gitlab`` library.

Environment variables
---------------------
GITLAB_URL : str
    GitLab instance URL (e.g. ``https://gitlab.com``).
GITLAB_TOKEN : str
    Personal access token with ``api`` scope.
GITLAB_PROJECT_ID : str
    Default project ID used when provisioning sandboxes.
"""

from __future__ import annotations

import os
import re
from typing import Any

import gitlab
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

GITLAB_URL: str = os.getenv("GITLAB_URL", "https://gitlab.com")
GITLAB_TOKEN: str = os.getenv("GITLAB_TOKEN", "")
GITLAB_PROJECT_ID: str = os.getenv("GITLAB_PROJECT_ID", "")

mcp = FastMCP("GitLab MCP – Academic Commander")

# ---------------------------------------------------------------------------
# Helper: lazy GitLab client
# ---------------------------------------------------------------------------
_gl: gitlab.Gitlab | None = None


def _get_gl() -> gitlab.Gitlab:
    """Return a reusable ``gitlab.Gitlab`` instance."""
    global _gl
    if _gl is None:
        if not GITLAB_TOKEN:
            raise RuntimeError("GITLAB_TOKEN environment variable is not set.")
        _gl = gitlab.Gitlab(GITLAB_URL, private_token=GITLAB_TOKEN)
        _gl.auth()
    return _gl


def _get_project(project_id: str | None = None):
    """Resolve a project by ID, falling back to the env-var default."""
    pid = project_id or GITLAB_PROJECT_ID
    if not pid:
        raise RuntimeError(
            "No project_id provided and GITLAB_PROJECT_ID is not set."
        )
    return _get_gl().projects.get(pid)


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


@mcp.tool()
def provision_coding_sandbox(
    topic: str,
    assignment_content: str,
) -> dict[str, Any]:
    """Create a new branch from ``main``, add assignment files, and push.

    This provisions a self-contained sandbox where a student can work on a
    coding assignment without affecting the main branch.

    Parameters
    ----------
    topic : str
        Topic slug used to name the branch (e.g. ``"linked-lists"``).
    assignment_content : str
        The assignment instructions or starter code to commit.

    Returns
    -------
    dict
        Branch name, commit SHA, and URLs for the new sandbox.
    """
    try:
        project = _get_project()

        # Sanitise topic for branch name
        branch_name = "sandbox/" + re.sub(r"[^a-zA-Z0-9_-]", "-", topic).strip("-").lower()

        # Create branch from main
        try:
            branch = project.branches.create({"branch": branch_name, "ref": "main"})
        except gitlab.exceptions.GitlabCreateError as exc:
            # If the branch already exists, we can still proceed with commits to it
            if "already exists" not in str(exc).lower():
                raise exc

        # Commit assignment files
        readme_content = (
            f"# Assignment: {topic}\n\n"
            f"Created automatically by Academic Commander.\n\n"
            f"## Instructions\n\n{assignment_content}\n"
        )

        # Check if README.md exists to determine commit action
        try:
            project.files.get(file_path="README.md", ref=branch_name)
            readme_action = "update"
        except gitlab.exceptions.GitlabGetError:
            readme_action = "create"

        # Check if solution.py exists to determine commit action
        try:
            project.files.get(file_path="solution.py", ref=branch_name)
            solution_action = "update"
        except gitlab.exceptions.GitlabGetError:
            solution_action = "create"

        commit_data = {
            "branch": branch_name,
            "commit_message": f"chore: scaffold assignment – {topic}",
            "actions": [
                {
                    "action": readme_action,
                    "file_path": "README.md",
                    "content": readme_content,
                },
                {
                    "action": solution_action,
                    "file_path": "solution.py",
                    "content": (
                        f'"""Solution file for: {topic}"""\n\n'
                        "# Write your solution below\n"
                    ),
                },
            ],
        }
        commit = project.commits.create(commit_data)

        return {
            "branch": branch_name,
            "commit_sha": commit.id,
            "web_url": f"{project.web_url}/-/tree/{branch_name}",
        }
    except gitlab.exceptions.GitlabCreateError as exc:
        return {"error": f"GitLab branch/commit creation failed: {exc}"}
    except Exception as exc:
        return {"error": f"Failed to provision sandbox: {exc}"}


@mcp.tool()
def get_pipeline_status(
    project_id: str,
    pipeline_id: str,
) -> dict[str, Any]:
    """Check the CI/CD pipeline status for a given project and pipeline.

    Parameters
    ----------
    project_id : str
        GitLab project ID.
    pipeline_id : str
        Pipeline ID to query.

    Returns
    -------
    dict
        Pipeline status, ref, duration, and timestamps.
    """
    try:
        project = _get_project(project_id)
        pipeline = project.pipelines.get(int(pipeline_id))
        return {
            "pipeline_id": pipeline.id,
            "status": pipeline.status,
            "ref": pipeline.ref,
            "sha": pipeline.sha,
            "duration": pipeline.duration,
            "created_at": pipeline.created_at,
            "updated_at": pipeline.updated_at,
            "web_url": pipeline.web_url,
        }
    except gitlab.exceptions.GitlabGetError as exc:
        return {"error": f"Pipeline not found: {exc}"}
    except Exception as exc:
        return {"error": f"Failed to get pipeline status: {exc}"}


@mcp.tool()
def get_test_results(
    project_id: str,
    pipeline_id: str,
) -> dict[str, Any]:
    """Parse test job results from a CI/CD pipeline.

    Iterates over all jobs in the pipeline, identifies jobs whose name
    contains ``test``, and returns their status, duration, and log tails.

    Parameters
    ----------
    project_id : str
        GitLab project ID.
    pipeline_id : str
        Pipeline ID whose test jobs should be inspected.

    Returns
    -------
    dict
        A list of test-job summaries including status and last 50 log lines.
    """
    try:
        project = _get_project(project_id)
        pipeline = project.pipelines.get(int(pipeline_id))
        jobs = pipeline.jobs.list(all=True)

        test_jobs: list[dict[str, Any]] = []
        for job in jobs:
            if "test" in job.name.lower():
                # Fetch the job trace (build log)
                try:
                    trace: str = job.trace().decode("utf-8", errors="replace")
                    log_tail = "\n".join(trace.splitlines()[-50:])
                except Exception:
                    log_tail = "(log unavailable)"

                test_jobs.append(
                    {
                        "job_id": job.id,
                        "name": job.name,
                        "status": job.status,
                        "duration": job.duration,
                        "stage": job.stage,
                        "log_tail": log_tail,
                    }
                )

        return {
            "pipeline_id": int(pipeline_id),
            "test_jobs": test_jobs,
            "count": len(test_jobs),
        }
    except Exception as exc:
        return {"error": f"Failed to get test results: {exc}"}


@mcp.tool()
def list_branches(project_id: str) -> dict[str, Any]:
    """List all branches in a GitLab project.

    Parameters
    ----------
    project_id : str
        GitLab project ID.

    Returns
    -------
    dict
        A list of branch names with their latest commit info.
    """
    try:
        project = _get_project(project_id)
        branches = project.branches.list(all=True)
        branch_list = [
            {
                "name": b.name,
                "commit_sha": b.commit["id"],
                "commit_message": b.commit["message"][:120],
                "protected": b.protected,
                "web_url": f"{project.web_url}/-/tree/{b.name}",
            }
            for b in branches
        ]
        return {"project_id": project_id, "branches": branch_list, "count": len(branch_list)}
    except Exception as exc:
        return {"error": f"Failed to list branches: {exc}"}


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run()
