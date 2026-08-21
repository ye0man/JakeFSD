"""CSV file collector connector."""

from __future__ import annotations

from pathlib import Path
from typing import Any, ClassVar

import pandas as pd

from jakefsd.connectors.base import REGISTRY, SourceConnector
from jakefsd.models.manifest import Schema, StageType


class CsvFileCollector(SourceConnector):
    """Read a CSV file into a DataFrame."""

    name = "csv_file"
    stage_type = StageType.COLLECT
    config_schema: ClassVar[dict[str, Any]] = {
        "type": "object",
        "required": ["path"],
        "properties": {
            "path": {"type": "string", "description": "Path to the CSV file"},
            "delimiter": {"type": "string", "default": ","},
            "encoding": {"type": "string", "default": "utf-8"},
        },
    }

    def collect(self) -> pd.DataFrame:
        path = Path(self.config["path"])
        if not path.exists():
            raise FileNotFoundError(f"CSV file not found: {path}")
        delimiter = self.config.get("delimiter", ",")
        encoding = self.config.get("encoding", "utf-8")
        return pd.read_csv(path, delimiter=delimiter, encoding=encoding)

    @property
    def output_schema(self) -> Schema | None:
        # CSV schema is dynamic; discovered at runtime.
        return None


REGISTRY.register(CsvFileCollector)
