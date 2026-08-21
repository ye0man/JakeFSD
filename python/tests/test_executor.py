"""Tests for the local pipeline executor."""

from __future__ import annotations

from pathlib import Path

from jakefsd.models.manifest import (
    Manifest,
    Pipeline,
    Project,
    Stage,
    StageType,
)
from jakefsd.runtime.executor import execute_pipeline, run_file


def test_execute_simple_pipeline(tmp_path: Path) -> None:
    csv_path = tmp_path / "data.csv"
    csv_path.write_text("id,name\n1,alice\n2,bob\n")

    pipeline = Pipeline(
        name="test",
        stages=[
            Stage(
                id="source",
                type=StageType.COLLECT,
                connector="csv_file",
                config={"path": str(csv_path)},
            ),
            Stage(
                id="report",
                type=StageType.REPORT,
                connector="csv_export",
                config={"path": str(tmp_path / "out.csv")},
                depends_on=["source"],
            ),
        ],
    )

    result = execute_pipeline(pipeline)
    assert result.success
    assert len(result.stage_results) == 2
    assert result.outputs["source"].shape == (2, 2)


def test_run_file(tmp_path: Path) -> None:
    csv_path = tmp_path / "data.csv"
    csv_path.write_text("id,name\n1,alice\n2,bob\n")
    out_path = tmp_path / "out.csv"

    manifest = Manifest(
        project=Project(
            pipeline=Pipeline(
                name="file_test",
                stages=[
                    Stage(
                        id="source",
                        type=StageType.COLLECT,
                        connector="csv_file",
                        config={"path": "data.csv"},
                    ),
                    Stage(
                        id="report",
                        type=StageType.REPORT,
                        connector="csv_export",
                        config={"path": "out.csv"},
                        depends_on=["source"],
                    ),
                ],
            )
        )
    )
    manifest_path = tmp_path / "pipeline.yaml"
    manifest.write(manifest_path)

    result = run_file(manifest_path)
    assert result.success
    assert out_path.exists()
