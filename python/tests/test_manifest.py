"""Tests for the pipeline manifest model."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from jakefsd.models.manifest import Manifest, Pipeline, Project, Stage, StageType


def test_stage_requires_id() -> None:
    with pytest.raises(ValidationError):
        Stage(id="", type=StageType.COLLECT, connector="csv_file")


def test_pipeline_requires_unique_stage_ids() -> None:
    with pytest.raises(ValidationError):
        Pipeline(
            name="bad",
            stages=[
                Stage(id="a", type=StageType.COLLECT, connector="csv_file"),
                Stage(id="a", type=StageType.LOAD, connector="duckdb_load"),
            ],
        )


def test_manifest_roundtrip_yaml() -> None:
    manifest = Manifest(
        project=Project(
            pipeline=Pipeline(
                name="test",
                stages=[
                    Stage(id="s", type=StageType.COLLECT, connector="csv_file"),
                ],
            )
        )
    )
    yaml_text = manifest.to_yaml()
    loaded = Manifest.from_yaml(yaml_text)
    assert loaded.project.pipeline.name == "test"
    assert loaded.project.pipeline.stages[0].id == "s"


def test_resolve_env_with_default() -> None:
    from jakefsd.models.manifest import resolve_env

    assert resolve_env("${UNSET_VAR:-default}") == "default"
