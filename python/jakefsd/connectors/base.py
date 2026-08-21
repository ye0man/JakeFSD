"""Connector contract base classes and registry."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, ClassVar

import pandas as pd

from jakefsd.credentials import resolve as resolve_credential
from jakefsd.models.manifest import Schema, StageType, resolve_env


class Connector(ABC):
    """Base class for all pipeline stage connectors."""

    name: ClassVar[str]
    stage_type: ClassVar[StageType]
    config_schema: ClassVar[dict[str, Any]] = {}

    def __init__(self, config: dict[str, Any]) -> None:
        self.config = {
            k: resolve_credential(resolve_env(v)) for k, v in config.items()
        }

    @property
    def input_schema(self) -> Schema | None:
        """Schema this stage expects from upstream stages, if any."""
        return None

    @property
    def output_schema(self) -> Schema | None:
        """Schema this stage produces, if known statically."""
        return None

    def validate_config(self) -> None:
        """Raise ValueError if required config is missing/invalid."""
        required = self.config_schema.get("required", [])
        missing = [key for key in required if key not in self.config]
        if missing:
            raise ValueError(f"{self.name} missing required config: {missing}")

    @abstractmethod
    def run(self, inputs: dict[str, pd.DataFrame]) -> pd.DataFrame:
        """Execute the connector and return a DataFrame."""
        ...


class SourceConnector(Connector):
    """A connector that produces data without upstream inputs."""

    stage_type = StageType.COLLECT

    def run(self, inputs: dict[str, pd.DataFrame]) -> pd.DataFrame:
        # Sources ignore upstream inputs by default.
        return self.collect()

    @abstractmethod
    def collect(self) -> pd.DataFrame:
        """Read or fetch data and return a DataFrame."""
        ...


class TransformConnector(Connector):
    """A connector that transforms one or more upstream DataFrames."""

    stage_type = StageType.TRANSFORM


class LoadConnector(Connector):
    """A connector that persists data to storage."""

    stage_type = StageType.LOAD

    @abstractmethod
    def run(self, inputs: dict[str, pd.DataFrame]) -> pd.DataFrame:
        """Persist data and return a summary DataFrame."""
        ...


class ReportConnector(Connector):
    """A connector that produces an output artifact."""

    stage_type = StageType.REPORT

    @abstractmethod
    def run(self, inputs: dict[str, pd.DataFrame]) -> pd.DataFrame:
        """Write the report and return a summary DataFrame."""
        ...


class ConnectorRegistry:
    """Registry of available connectors."""

    def __init__(self) -> None:
        self._connectors: dict[str, type[Connector]] = {}

    def register(self, connector_cls: type[Connector]) -> type[Connector]:
        self._connectors[connector_cls.name] = connector_cls
        return connector_cls

    def get(self, name: str) -> type[Connector]:
        if name not in self._connectors:
            raise KeyError(f"unknown connector: {name}")
        return self._connectors[name]

    def list(self) -> list[str]:
        return sorted(self._connectors.keys())

    def build(self, name: str, config: dict[str, Any]) -> Connector:
        cls = self.get(name)
        instance = cls(config)
        instance.validate_config()
        return instance


# Global registry used by the runtime and CLI.
REGISTRY = ConnectorRegistry()
