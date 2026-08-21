"""Pydantic models for the JakeFSD pipeline manifest."""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, field_validator
from pydantic import Field as PydanticField


class StageType(str, Enum):
    """Pipeline stage types."""

    COLLECT = "collect"
    CLEAN = "clean"
    TRANSFORM = "transform"
    LOAD = "load"
    ANALYZE = "analyze"
    REPORT = "report"


class Column(BaseModel):
    """A column in a stage's input/output schema."""

    name: str
    type: str = "string"
    nullable: bool = True
    description: str | None = None


class Schema(BaseModel):
    """Schema contract for a stream between stages."""

    fields: list[Column] = PydanticField(default_factory=list)


class Stage(BaseModel):
    """A node in the pipeline DAG."""

    id: str
    type: StageType
    connector: str
    config: dict[str, Any] = PydanticField(default_factory=dict)
    depends_on: list[str] = PydanticField(default_factory=list)
    input_schema: Schema | None = None
    output_schema: Schema | None = None
    description: str | None = None

    @field_validator("id")
    @classmethod
    def _id_must_be_nonempty(cls, value: str) -> str:
        if not value:
            raise ValueError("stage id must be non-empty")
        return value


class Pipeline(BaseModel):
    """A declarative data pipeline."""

    name: str
    version: str = "0.1.0"
    schedule: str | None = None
    stages: list[Stage] = PydanticField(default_factory=list)
    description: str | None = None

    @field_validator("stages")
    @classmethod
    def _stage_ids_unique(cls, stages: list[Stage]) -> list[Stage]:
        ids = [s.id for s in stages]
        if len(ids) != len(set(ids)):
            raise ValueError("stage ids must be unique")
        return stages


class Project(BaseModel):
    """Top-level JakeFSD project container."""

    pipeline: Pipeline
    metadata: dict[str, Any] = PydanticField(default_factory=dict)


class Manifest(BaseModel):
    """On-disk project manifest."""

    project: Project

    @classmethod
    def from_yaml(cls, text: str) -> Manifest:
        """Parse a YAML manifest string."""
        data = yaml.safe_load(text)
        if not isinstance(data, dict):
            raise ValueError("manifest must be a mapping")
        return cls.model_validate(data)

    @classmethod
    def from_file(cls, path: Path | str) -> Manifest:
        """Load a manifest from disk."""
        path = Path(path)
        return cls.from_yaml(path.read_text(encoding="utf-8"))

    def to_yaml(self) -> str:
        """Serialize the manifest to YAML."""
        # Pydantic dicts are JSON-serializable; dump via yaml.
        return yaml.safe_dump(
            self.model_dump(mode="json", exclude_none=True),
            sort_keys=False,
            allow_unicode=True,
        )

    def write(self, path: Path | str) -> None:
        """Write the manifest to disk."""
        path = Path(path)
        path.write_text(self.to_yaml(), encoding="utf-8")


def resolve_env(value: Any) -> Any:
    """Resolve ``${VAR}`` or ``${VAR:-default}`` placeholders in config values."""
    import os
    import re

    if isinstance(value, str):
        pattern = re.compile(r"\$\{(?P<name>[^}]+?)(?::-(?P<default>[^}]*))?\}")

        def replacer(match: re.Match[str]) -> str:
            name = match.group("name")
            default = match.group("default")
            return os.environ.get(name, default if default is not None else "")

        return pattern.sub(replacer, value)
    return value
