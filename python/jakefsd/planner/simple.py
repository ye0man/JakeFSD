"""Rule-based planner for M1."""

from __future__ import annotations

from typing import Any

from jakefsd.models.manifest import Manifest, Pipeline, Project, Stage, StageType


def _detect_source(intent: str) -> tuple[str, dict[str, Any]] | None:
    intent_lower = intent.lower()
    if "json" in intent_lower:
        return "json_file", {"path": "./data/input.json"}
    if "csv" in intent_lower:
        return "csv_file", {"path": "./data/input.csv"}
    if "api" in intent_lower or "http" in intent_lower or "rest" in intent_lower:
        return "rest_api", {"url": "https://api.example.com/data"}
    return None


def _detect_load(intent: str) -> tuple[str, dict[str, Any]] | None:
    intent_lower = intent.lower()
    if "duckdb" in intent_lower:
        return "duckdb_load", {"database": "./data/pipeline.duckdb", "table": "output"}
    if "sqlite" in intent_lower:
        return "sqlite_load", {"database": "./data/pipeline.db", "table": "output"}
    return None


def _detect_report(intent: str) -> tuple[str, dict[str, Any]] | None:
    intent_lower = intent.lower()
    if "html" in intent_lower or "dashboard" in intent_lower or "report" in intent_lower:
        return "html_dashboard", {"path": "./reports/output.html", "title": "JakeFSD Report"}
    if "csv" in intent_lower and "export" in intent_lower:
        return "csv_export", {"path": "./reports/output.csv"}
    if "sheet" in intent_lower or "gsheet" in intent_lower or "google sheet" in intent_lower:
        return None  # GSheets not implemented in M1 backend
    return None


def plan_from_intent(
    intent: str,
    project_name: str = "pipeline",
) -> Manifest:
    """Generate a minimal M1 manifest from a natural-language intent."""
    source = _detect_source(intent)
    load = _detect_load(intent)
    report = _detect_report(intent)

    if source is None:
        source = ("csv_file", {"path": "./data/input.csv"})

    stages: list[Stage] = [
        Stage(
            id="source",
            type=StageType.COLLECT,
            connector=source[0],
            config=source[1],
        ),
    ]

    if load is not None:
        stages.append(
            Stage(
                id="load",
                type=StageType.LOAD,
                connector=load[0],
                config=load[1],
                depends_on=["source"],
            ),
        )

    if report is not None:
        depends_on = ["load"] if load else ["source"]
        stages.append(
            Stage(
                id="report",
                type=StageType.REPORT,
                connector=report[0],
                config=report[1],
                depends_on=depends_on,
            ),
        )

    pipeline = Pipeline(name=project_name, stages=stages)
    return Manifest(project=Project(pipeline=pipeline))
