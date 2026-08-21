"""JSON file collector connector."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, ClassVar

import pandas as pd

from jakefsd.connectors.base import REGISTRY, SourceConnector
from jakefsd.models.manifest import Schema, StageType


class JsonFileCollector(SourceConnector):
    """Read a JSON file or JSON Lines file into a DataFrame."""

    name = "json_file"
    stage_type = StageType.COLLECT
    config_schema: ClassVar[dict[str, Any]] = {
        "type": "object",
        "required": ["path"],
        "properties": {
            "path": {"type": "string", "description": "Path to the JSON file"},
            "lines": {"type": "boolean", "default": False},
        },
    }

    def collect(self) -> pd.DataFrame:
        path = Path(self.config["path"])
        if not path.exists():
            raise FileNotFoundError(f"JSON file not found: {path}")

        lines = self.config.get("lines", False)
        if lines:
            records = []
            with path.open("r", encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if line:
                        records.append(json.loads(line))
            return pd.DataFrame(records)

        with path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        if isinstance(data, list):
            return pd.DataFrame(data)
        if isinstance(data, dict):
            # Normalize a dict of lists or single record.
            return pd.json_normalize(data)
        raise ValueError("JSON content must be a list or object")

    @property
    def output_schema(self) -> Schema | None:
        return None


REGISTRY.register(JsonFileCollector)
