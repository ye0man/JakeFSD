"""JakeFSD command-line interface."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import keyring
import typer

from jakefsd.connectors import REGISTRY
from jakefsd.credentials import delete_credential, get_credential, set_credential
from jakefsd.models.manifest import Manifest, StageType
from jakefsd.planner.simple import plan_from_intent
from jakefsd.runtime.executor import execute_stage, run_file
from jakefsd.runtime.scheduler import LocalScheduler

app = typer.Typer(help="JakeFSD — local-first IDE for data pipelines")


def _version_callback(value: bool) -> None:
    if value:
        typer.echo("JakeFSD 0.1.0")
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def main(
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        callback=_version_callback,
        is_eager=True,
        help="Show the JakeFSD version.",
    ),
) -> None:
    """JakeFSD CLI entry point."""


@app.command()
def version() -> None:
    """Show the JakeFSD version."""
    typer.echo("JakeFSD 0.1.0")


@app.command()
def init(
    name: str = typer.Argument(..., help="Name of the new project directory"),
    intent: Optional[str] = typer.Option(
        None,
        "--intent",
        "-i",
        help="Optional natural-language intent to seed the manifest",
    ),
) -> None:
    """Scaffold a new JakeFSD project."""
    project_dir = Path(name)
    if project_dir.exists():
        typer.echo(f"Directory already exists: {project_dir}", err=True)
        raise typer.Exit(code=1)

    project_dir.mkdir(parents=True)
    (project_dir / "data").mkdir()
    (project_dir / "reports").mkdir()

    if intent:
        manifest = plan_from_intent(intent, project_name=name)
    else:
        manifest = plan_from_intent(
            "load a csv file into duckdb and export html report",
            project_name=name,
        )
        # Point the scaffolded source at the included sample data.
        for stage in manifest.project.pipeline.stages:
            if stage.type == StageType.COLLECT and stage.connector == "csv_file":
                stage.config["path"] = "data/sample.csv"

    manifest_path = project_dir / "pipeline.yaml"
    manifest.write(manifest_path)

    readme = project_dir / "README.md"
    readme.write_text(
        f"# {name}\n\nA JakeFSD project.\n\nRun with:\n\n```bash\n"
        f"jakefsd run {manifest_path}\n```\n",
        encoding="utf-8",
    )

    sample_csv = project_dir / "data" / "sample.csv"
    sample_csv.write_text("id,name,value\n1,alice,10\n2,bob,20\n", encoding="utf-8")

    typer.echo(f"Created project at {project_dir}")
    typer.echo(f"Manifest: {manifest_path}")


@app.command()
def plan(
    intent: str = typer.Argument(..., help="Natural-language pipeline intent"),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Path to write the generated manifest",
    ),
    project_name: str = typer.Option("pipeline", "--name", "-n"),
) -> None:
    """Generate a pipeline manifest from a natural-language intent."""
    manifest = plan_from_intent(intent, project_name=project_name)
    yaml_text = manifest.to_yaml()
    if output:
        output.write_text(yaml_text, encoding="utf-8")
        typer.echo(f"Wrote manifest to {output}")
    else:
        typer.echo(yaml_text)


@app.command()
def connect(
    source_type: str = typer.Argument(..., help="Connector name, e.g. csv_file, rest_api"),
    config: Optional[str] = typer.Option(
        None,
        "--config",
        "-c",
        help="Connector config as key=value pairs separated by commas",
    ),
) -> None:
    """Test a source connector and preview its output schema."""
    parsed_config: dict[str, str] = {}
    if config:
        for pair in config.split(","):
            key, _, value = pair.partition("=")
            parsed_config[key.strip()] = value.strip()

    try:
        connector = REGISTRY.build(source_type, parsed_config)
    except KeyError as exc:
        typer.echo(f"Unknown connector: {exc}", err=True)
        raise typer.Exit(code=1)
    except ValueError as exc:
        typer.echo(f"Invalid config: {exc}", err=True)
        raise typer.Exit(code=1)

    if not hasattr(connector, "collect"):
        typer.echo(f"Connector '{source_type}' is not a source connector", err=True)
        raise typer.Exit(code=1)

    df = connector.collect()
    typer.echo(f"Collected {len(df)} rows")
    typer.echo(df.head().to_string(index=False))


@app.command()
def run(
    manifest_path: Path = typer.Argument(..., help="Path to pipeline.yaml"),
    stage: Optional[str] = typer.Option(
        None,
        "--stage",
        "-s",
        help="Run a single stage by id",
    ),
    preview: int = typer.Option(
        0,
        "--preview",
        "-p",
        help="Limit stored output to N rows per stage",
    ),
) -> None:
    """Execute a pipeline manifest."""
    if not manifest_path.exists():
        typer.echo(f"Manifest not found: {manifest_path}", err=True)
        raise typer.Exit(code=1)

    manifest = Manifest.from_file(manifest_path)

    if stage:
        result = execute_stage(manifest.project.pipeline, stage)
        status = "OK" if result.success else "FAIL"
        typer.echo(f"[{status}] {result.stage_id}: {result.rows} rows")
        if result.error:
            typer.echo(f"  -> {result.error}", err=True)
            raise typer.Exit(code=1)
        return

    result = run_file(manifest_path, preview_rows=preview)
    for sr in result.stage_results:
        status = "OK" if sr.success else "FAIL"
        typer.echo(f"[{status}] {sr.stage_id}: {sr.rows} rows")
        if sr.error:
            typer.echo(f"  -> {sr.error}", err=True)

    if not result.success:
        typer.echo(f"Pipeline failed: {result.error}", err=True)
        raise typer.Exit(code=1)

    typer.echo(f"Pipeline '{result.pipeline_name}' completed successfully.")


@app.command()
def schedule(
    manifest_path: Path = typer.Argument(..., help="Path to pipeline.yaml"),
    cron: Optional[str] = typer.Option(
        None,
        "--cron",
        "-c",
        help="Cron expression (overrides manifest schedule)",
    ),
    once: bool = typer.Option(
        False,
        "--once",
        help="Run pending jobs once and exit instead of looping",
    ),
    poll: int = typer.Option(
        60,
        "--poll",
        "-p",
        help="Polling interval in seconds when looping",
    ),
) -> None:
    """Run a pipeline on a schedule."""
    if not manifest_path.exists():
        typer.echo(f"Manifest not found: {manifest_path}", err=True)
        raise typer.Exit(code=1)

    scheduler = LocalScheduler()
    if cron:
        scheduler.add(manifest_path, cron)
    else:
        job = scheduler.add_from_manifest(manifest_path)
        if job is None:
            typer.echo("Manifest has no schedule and --cron was not provided", err=True)
            raise typer.Exit(code=1)

    typer.echo(f"Scheduler started for {manifest_path}")
    try:
        scheduler.run_loop(poll_interval=poll, once=once)
    except KeyboardInterrupt:
        typer.echo("Scheduler stopped.")


credentials_app = typer.Typer(help="Manage OS keychain credentials")
app.add_typer(credentials_app, name="credentials")


@credentials_app.command("set")
def credentials_set(
    name: str = typer.Argument(..., help="Credential name"),
    value: str = typer.Argument(..., help="Credential value"),
) -> None:
    """Store a credential in the OS keychain."""
    set_credential(name, value)
    typer.echo(f"Stored credential: {name}")


@credentials_app.command("get")
def credentials_get(
    name: str = typer.Argument(..., help="Credential name"),
) -> None:
    """Retrieve a credential from the OS keychain."""
    value = get_credential(name)
    if value is None:
        typer.echo(f"Credential not found: {name}", err=True)
        raise typer.Exit(code=1)
    typer.echo(value)


@credentials_app.command("delete")
def credentials_delete(
    name: str = typer.Argument(..., help="Credential name"),
) -> None:
    """Delete a credential from the OS keychain."""
    try:
        delete_credential(name)
    except keyring.errors.PasswordDeleteError:
        typer.echo(f"Credential not found: {name}", err=True)
        raise typer.Exit(code=1)
    typer.echo(f"Deleted credential: {name}")


if __name__ == "__main__":
    app()
