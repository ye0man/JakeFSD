"""Tests for the JakeFSD CLI."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from jakefsd.cli import app

runner = CliRunner()


def test_version() -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "JakeFSD 0.1.0" in result.output


def test_init_creates_project(tmp_path: Path) -> None:
    project_dir = tmp_path / "myproject"
    result = runner.invoke(app, ["init", str(project_dir)])
    assert result.exit_code == 0
    assert (project_dir / "pipeline.yaml").exists()
    assert (project_dir / "data" / "sample.csv").exists()


def test_plan_outputs_yaml(tmp_path: Path) -> None:
    out = tmp_path / "plan.yaml"
    result = runner.invoke(
        app, ["plan", "load csv into duckdb and export html", "-o", str(out)]
    )
    assert result.exit_code == 0
    assert out.exists()
    text = out.read_text()
    assert "csv_file" in text
    assert "duckdb_load" in text
    assert "html_dashboard" in text


def test_run_pipeline(tmp_path: Path) -> None:
    project_dir = tmp_path / "proj"
    runner.invoke(app, ["init", str(project_dir)])
    result = runner.invoke(app, ["run", str(project_dir / "pipeline.yaml")])
    assert result.exit_code == 0
    assert "completed successfully" in result.output


def test_preview_stage(tmp_path: Path) -> None:
    project_dir = tmp_path / "proj"
    runner.invoke(app, ["init", str(project_dir)])
    result = runner.invoke(
        app, ["preview", str(project_dir / "pipeline.yaml"), "--stage", "source"]
    )
    assert result.exit_code == 0
    assert "id" in result.output
    assert "name" in result.output
