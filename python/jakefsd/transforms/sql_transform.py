"""SQL transform connector."""

from __future__ import annotations

from pathlib import Path
from typing import Any, ClassVar

import duckdb
import pandas as pd

from jakefsd.connectors.base import REGISTRY, TransformConnector
from jakefsd.models.manifest import StageType


class SqlTransform(TransformConnector):
    """Transform a DataFrame using a SQL query against DuckDB."""

    name = "sql_transform"
    stage_type = StageType.TRANSFORM
    config_schema: ClassVar[dict[str, Any]] = {
        "type": "object",
        "required": ["sql"],
        "properties": {
            "sql": {"type": "string", "description": "SQL query referencing 'incoming'"},
            "database": {"type": "string", "description": "Optional persistent DuckDB path"},
        },
    }

    def run(self, inputs: dict[str, pd.DataFrame]) -> pd.DataFrame:
        if len(inputs) != 1:
            raise ValueError("sql_transform expects exactly one upstream input")
        df = next(iter(inputs.values()))
        sql = self.config["sql"]
        database = self.config.get("database")

        if database:
            Path(database).parent.mkdir(parents=True, exist_ok=True)

        with duckdb.connect(database or ":memory:") as conn:
            conn.register("incoming", df)
            return conn.execute(sql).fetchdf()


REGISTRY.register(SqlTransform)
