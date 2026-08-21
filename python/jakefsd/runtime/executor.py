"""Local pipeline executor."""

from __future__ import annotations

import os
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Generator

import pandas as pd

from jakefsd.connectors import REGISTRY  # registers all built-in connectors
from jakefsd.models.manifest import Manifest, Pipeline, Stage


@contextmanager
def cwd(path: Path) -> Generator[None, None, None]:
    """Temporarily change the working directory."""
    original = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(original)


class ExecutionError(RuntimeError):
    """Raised when a pipeline stage fails."""


@dataclass
class StageResult:
    """Result of executing a single stage."""

    stage_id: str
    success: bool
    rows: int = 0
    error: str | None = None
    output: pd.DataFrame | None = None


@dataclass
class RunResult:
    """Result of executing a pipeline."""

    pipeline_name: str
    success: bool
    stage_results: list[StageResult] = field(default_factory=list)
    outputs: dict[str, pd.DataFrame] = field(default_factory=dict)
    error: str | None = None


def _topological_order(stages: list[Stage]) -> list[Stage]:
    """Return stages in dependency order."""
    by_id = {s.id: s for s in stages}
    visited: set[str] = set()
    ordered: list[Stage] = []

    def visit(stage: Stage) -> None:
        if stage.id in visited:
            return
        for dep in stage.depends_on:
            if dep not in by_id:
                raise ExecutionError(f"stage '{stage.id}' depends on unknown stage '{dep}'")
            visit(by_id[dep])
        visited.add(stage.id)
        ordered.append(stage)

    for stage in stages:
        visit(stage)
    return ordered


def _build_inputs(
    stage: Stage, outputs: dict[str, pd.DataFrame]
) -> dict[str, pd.DataFrame]:
    """Collect upstream DataFrames for a stage."""
    inputs: dict[str, pd.DataFrame] = {}
    for dep in stage.depends_on:
        if dep not in outputs:
            raise ExecutionError(f"missing upstream output for stage '{dep}'")
        inputs[dep] = outputs[dep]
    return inputs


def execute_stage(
    pipeline: Pipeline,
    stage_id: str,
    upstream_outputs: dict[str, pd.DataFrame] | None = None,
) -> StageResult:
    """Execute a single stage, optionally with pre-computed upstream outputs."""
    by_id = {s.id: s for s in pipeline.stages}
    if stage_id not in by_id:
        raise ExecutionError(f"stage '{stage_id}' not found")

    stage = by_id[stage_id]
    outputs = upstream_outputs or {}
    inputs = _build_inputs(stage, outputs)
    connector = REGISTRY.build(stage.connector, stage.config)
    try:
        output = connector.run(inputs)
    except Exception as exc:
        return StageResult(stage_id=stage.id, success=False, error=str(exc))

    return StageResult(
        stage_id=stage.id,
        success=True,
        rows=len(output),
        output=output,
    )


def execute_pipeline(
    pipeline: Pipeline,
    stop_on_error: bool = True,
    preview_rows: int = 0,
) -> RunResult:
    """Execute a pipeline locally and return the run result."""
    outputs: dict[str, pd.DataFrame] = {}
    stage_results: list[StageResult] = []

    for stage in _topological_order(pipeline.stages):
        connector = REGISTRY.build(stage.connector, stage.config)
        inputs = _build_inputs(stage, outputs)
        try:
            output = connector.run(inputs)
        except Exception as exc:  # pragma: no cover - caught and reported
            result = StageResult(stage_id=stage.id, success=False, error=str(exc))
            stage_results.append(result)
            if stop_on_error:
                return RunResult(
                    pipeline_name=pipeline.name,
                    success=False,
                    stage_results=stage_results,
                    outputs=outputs,
                    error=f"stage '{stage.id}' failed: {exc}",
                )
            continue

        rows = len(output)
        if preview_rows > 0:
            output = output.head(preview_rows)
        outputs[stage.id] = output
        stage_results.append(StageResult(stage_id=stage.id, success=True, rows=rows, output=output))

    return RunResult(
        pipeline_name=pipeline.name,
        success=True,
        stage_results=stage_results,
        outputs=outputs,
    )


def run_manifest(
    manifest: Manifest,
    stop_on_error: bool = True,
    preview_rows: int = 0,
) -> RunResult:
    """Execute the pipeline in a manifest."""
    return execute_pipeline(manifest.project.pipeline, stop_on_error, preview_rows)


def run_file(path: Path | str, stop_on_error: bool = True, preview_rows: int = 0) -> RunResult:
    """Load a manifest file and execute its pipeline.

    Relative paths in connector configs are resolved against the manifest's directory.
    """
    path = Path(path).resolve()
    manifest = Manifest.from_file(path)
    with cwd(path.parent):
        return run_manifest(manifest, stop_on_error, preview_rows)
