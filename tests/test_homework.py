"""
Academic Commander — Database Indexing Coding-Lab Tests.

This pytest module is auto-deployed by the GitLab MCP server into a
student's coding-lab branch.  The CI/CD pipeline executes these tests
to grade the student's database-optimisation solution.

Grading rubric (100 points total):
    test_create_index         — 20 pts  (basic correctness)
    test_query_optimization   — 20 pts  (basic correctness)
    test_index_performance    — 20 pts  (performance check)
    test_composite_index      — 20 pts  (edge-case / advanced)
    test_index_selectivity    — 20 pts  (analytical reasoning)
"""

from __future__ import annotations

import time
from typing import Any, Dict, List

import pytest


# ====================================================================== #
# Simulated database engine (stands in for the student's submission)
# ====================================================================== #
class InMemoryTable:
    """A minimal, list-backed 'table' that supports naive scans and
    optional B-tree-style index lookups for grading purposes."""

    def __init__(self, rows: List[Dict[str, Any]]) -> None:
        self.rows: List[Dict[str, Any]] = list(rows)
        self.indexes: Dict[str, Dict[Any, List[int]]] = {}

    # ── student-facing API ────────────────────────────────────────── #

    def create_index(self, column: str) -> None:
        """Build a hash index on *column*.

        Students must implement this so that subsequent queries on the
        indexed column avoid a full table scan.
        """
        index: Dict[Any, List[int]] = {}
        for pos, row in enumerate(self.rows):
            key = row.get(column)
            index.setdefault(key, []).append(pos)
        self.indexes[column] = index

    def create_composite_index(self, columns: List[str]) -> None:
        """Build a composite hash index across multiple *columns*.

        The key is a tuple of column values in the order given.
        """
        composite_key = tuple(columns)
        index: Dict[tuple, List[int]] = {}
        for pos, row in enumerate(self.rows):
            key = tuple(row.get(c) for c in columns)
            index.setdefault(key, []).append(pos)
        self.indexes[str(composite_key)] = index  # type: ignore[assignment]

    def query(self, column: str, value: Any) -> List[Dict[str, Any]]:
        """Return rows where *column* == *value*.

        If an index exists on *column*, the implementation must use it
        instead of scanning every row.
        """
        if column in self.indexes:
            positions = self.indexes[column].get(value, [])
            return [self.rows[p] for p in positions]
        # Fallback: full scan (slow path — should be avoided after indexing)
        return [r for r in self.rows if r.get(column) == value]

    def query_composite(
        self, columns: List[str], values: List[Any]
    ) -> List[Dict[str, Any]]:
        """Return rows matching all *columns*==*values* via composite index."""
        composite_key = str(tuple(columns))
        lookup = tuple(values)
        if composite_key in self.indexes:
            positions = self.indexes[composite_key].get(lookup, [])
            return [self.rows[p] for p in positions]
        return [
            r
            for r in self.rows
            if all(r.get(c) == v for c, v in zip(columns, values))
        ]

    def index_selectivity(self, column: str) -> float:
        """Return the selectivity ratio of the index on *column*.

        Selectivity = (number of distinct keys) / (total rows).
        A value close to 1.0 indicates a highly selective (good) index.
        """
        if column not in self.indexes:
            raise ValueError(f"No index on column '{column}'")
        distinct_keys = len(self.indexes[column])
        return distinct_keys / len(self.rows) if self.rows else 0.0


# ====================================================================== #
# Fixtures
# ====================================================================== #
@pytest.fixture()
def sample_table() -> InMemoryTable:
    """Provide a 10 000-row table with realistic student-record data."""
    rows: List[Dict[str, Any]] = []
    departments = ["CSE", "ECE", "ME", "CE", "EEE"]
    for i in range(10_000):
        rows.append(
            {
                "student_id": f"STU{i:05d}",
                "name": f"Student_{i}",
                "department": departments[i % len(departments)],
                "gpa": round(2.0 + (i % 20) * 0.1, 2),
                "semester": (i % 8) + 1,
            }
        )
    return InMemoryTable(rows)


# ====================================================================== #
# Graded test cases
# ====================================================================== #


class TestDatabaseIndexingLab:
    """Grading suite for the database-indexing coding lab (5/5 tests)."""

    # ── Test 1: Basic index creation (20 pts) ──────────────────────── #
    def test_create_index(self, sample_table: InMemoryTable) -> None:
        """Student must build an index on 'department' and the lookup
        structure should contain exactly the expected distinct keys."""
        sample_table.create_index("department")

        assert "department" in sample_table.indexes, (
            "Index was not registered — did you store it in self.indexes?"
        )

        index = sample_table.indexes["department"]
        assert len(index) == 5, (
            f"Expected 5 distinct department keys, got {len(index)}"
        )
        # Every key must map to exactly 2 000 rows (10 000 / 5)
        for dept, positions in index.items():
            assert len(positions) == 2_000, (
                f"Department '{dept}' should map to 2000 rows, "
                f"got {len(positions)}"
            )

    # ── Test 2: Query uses the index (20 pts) ─────────────────────── #
    def test_query_optimization(self, sample_table: InMemoryTable) -> None:
        """After indexing, a query on the indexed column should return
        correct results and use the index path (no full scan)."""
        sample_table.create_index("department")

        results = sample_table.query("department", "CSE")

        assert len(results) == 2_000, (
            f"Expected 2000 CSE students, got {len(results)}"
        )
        assert all(r["department"] == "CSE" for r in results), (
            "Returned rows contain non-CSE departments — index lookup "
            "is returning incorrect positions."
        )

    # ── Test 3: Index improves query speed (20 pts) ────────────────── #
    def test_index_performance(self, sample_table: InMemoryTable) -> None:
        """Indexed query must be measurably faster than a full scan on
        a 10 000-row table."""
        # --- unindexed (full-scan) timing ---
        start = time.perf_counter()
        for _ in range(100):
            sample_table.query("department", "ME")
        scan_duration = time.perf_counter() - start

        # --- indexed timing ---
        sample_table.create_index("department")
        start = time.perf_counter()
        for _ in range(100):
            sample_table.query("department", "ME")
        index_duration = time.perf_counter() - start

        speedup = scan_duration / index_duration if index_duration else float("inf")
        assert speedup > 1.5, (
            f"Index speedup ({speedup:.2f}x) is below the 1.5x minimum "
            "threshold — the query may not be using the index."
        )

    # ── Test 4: Composite index creation (20 pts) ──────────────────── #
    def test_composite_index(self, sample_table: InMemoryTable) -> None:
        """Student must create a composite index on (department, semester)
        and use it to answer multi-column equality queries."""
        sample_table.create_composite_index(["department", "semester"])

        results = sample_table.query_composite(
            ["department", "semester"], ["CSE", 1]
        )

        # 10 000 rows / 5 depts / 8 semesters = 250
        assert len(results) == 250, (
            f"Expected 250 rows for (CSE, sem 1), got {len(results)}"
        )
        assert all(
            r["department"] == "CSE" and r["semester"] == 1 for r in results
        ), "Composite query returned rows that don't match both predicates."

    # ── Test 5: Index selectivity calculation (20 pts) ─────────────── #
    def test_index_selectivity(self, sample_table: InMemoryTable) -> None:
        """Student must compute selectivity = distinct_keys / total_rows.
        'student_id' is unique → selectivity ≈ 1.0.
        'department' has 5 distinct → selectivity = 0.0005."""
        sample_table.create_index("student_id")
        sample_table.create_index("department")

        sel_id = sample_table.index_selectivity("student_id")
        sel_dept = sample_table.index_selectivity("department")

        assert sel_id == pytest.approx(1.0, abs=1e-6), (
            f"student_id selectivity should be ~1.0, got {sel_id}"
        )
        assert sel_dept == pytest.approx(0.0005, abs=1e-6), (
            f"department selectivity should be ~0.0005, got {sel_dept}"
        )

        # High-selectivity indexes are better for point queries
        assert sel_id > sel_dept, (
            "student_id (unique) should have higher selectivity than "
            "department — verify your formula."
        )
