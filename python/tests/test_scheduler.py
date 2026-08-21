"""Tests for the local scheduler."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from jakefsd.models.manifest import Manifest, Pipeline, Project, Stage, StageType
from jakefsd.runtime.scheduler import LocalScheduler, ScheduledJob


def test_scheduled_job_next_run() -> None:
    # A schedule that runs every minute should have a next run within ~2 minutes.
    job = ScheduledJob(manifest_path=Path("pipeline.yaml"), schedule="* * * * *")
    next_run = job.next_run(datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc))
    assert next_run == datetime(2024, 1, 1, 0, 1, 0, tzinfo=timezone.utc)


def test_scheduler_runs_due_job(tmp_path: Path) -> None:
    csv_path = tmp_path / "data.csv"
    csv_path.write_text("id\n1\n2\n")

    manifest = Manifest(
        project=Project(
            pipeline=Pipeline(
                name="scheduled",
                schedule="* * * * *",
                stages=[
                    Stage(
                        id="source",
                        type=StageType.COLLECT,
                        connector="csv_file",
                        config={"path": str(csv_path)},
                    ),
                ],
            )
        )
    )
    manifest_path = tmp_path / "pipeline.yaml"
    manifest.write(manifest_path)

    scheduler = LocalScheduler()
    scheduler.add_from_manifest(manifest_path)
    results = scheduler.run_pending()
    assert len(results) == 1
    assert results[0].success
