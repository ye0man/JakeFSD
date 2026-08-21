"""Local cron-like scheduler for JakeFSD pipelines."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from croniter import croniter

from jakefsd.runtime.executor import RunResult, run_file


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class ScheduledJob:
    """A pipeline scheduled to run on a cron expression."""

    manifest_path: Path
    schedule: str
    last_run: datetime | None = None
    results: list[RunResult] = field(default_factory=list)

    def next_run(self, base_time: datetime | None = None) -> datetime:
        """Return the next scheduled run time."""
        itr = croniter(self.schedule, base_time or _utc_now())
        return itr.get_next(datetime)

    def is_due(self, now: datetime | None = None) -> bool:
        """Return True if the job is due to run."""
        now = now or _utc_now()
        if self.last_run is None:
            return True
        return now >= self.next_run(self.last_run)

    def run(self) -> RunResult:
        """Execute the scheduled pipeline and record the result."""
        result = run_file(self.manifest_path)
        self.last_run = _utc_now()
        self.results.append(result)
        return result


class LocalScheduler:
    """Simple cron-like scheduler for pipeline manifests."""

    def __init__(self) -> None:
        self.jobs: list[ScheduledJob] = []

    def add(self, manifest_path: Path | str, schedule: str) -> ScheduledJob:
        """Add a scheduled job."""
        job = ScheduledJob(manifest_path=Path(manifest_path), schedule=schedule)
        self.jobs.append(job)
        return job

    def add_from_manifest(self, manifest_path: Path | str) -> ScheduledJob | None:
        """Add a job from a manifest if it defines a schedule."""
        from jakefsd.models.manifest import Manifest

        manifest = Manifest.from_file(manifest_path)
        schedule = manifest.project.pipeline.schedule
        if schedule:
            return self.add(manifest_path, schedule)
        return None

    def run_pending(self) -> list[RunResult]:
        """Run all jobs that are due."""
        results: list[RunResult] = []
        for job in self.jobs:
            if job.is_due():
                results.append(job.run())
        return results

    def run_loop(self, poll_interval: int = 60, once: bool = False) -> None:
        """Run the scheduler loop until interrupted.

        If ``once`` is True, only one pending pass is executed and the loop exits.
        """
        while True:
            self.run_pending()
            if once:
                break
            time.sleep(poll_interval)
