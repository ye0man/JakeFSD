"""Tests for bundled example projects."""

from __future__ import annotations

from pathlib import Path

from jakefsd.models.manifest import Manifest
from jakefsd.runtime.executor import run_file


def test_sales_report_example_runs() -> None:
    example_dir = Path(__file__).parents[2] / "examples" / "sales_report"
    manifest_path = example_dir / "pipeline.yaml"
    assert manifest_path.exists()

    manifest = Manifest.from_file(manifest_path)
    assert manifest.project.pipeline.name == "sales_report"

    result = run_file(manifest_path)
    assert result.success
