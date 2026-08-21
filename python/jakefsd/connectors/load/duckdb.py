"""DuckDB load connector."""

from __future__ import annotations

from pathlib import Path
from typing import Any, ClassVar

import duckdb
import pandas as pd

from jakefsd.connectors.base import REGISTRY, LoadConnector
from jakefsd.models.manifest import StageType


class DuckDbLoad(LoadConnector):
    """Write a DataFrame to a DuckDB table."""

    name = "duckdb_load"
    stage_type = StageType.LOAD
    config_schema: ClassVar[dict[str, Any]] = {
        "type": "object",
        "required": ["database", "table"],
        "properties": {
            "database": {"type": "string", "description": "Path to DuckDB database file"},
            "table": {"type": "string", "description": "Target table name"},
            "schema": {"type": "string", "default": "main"},
            "if_exists": {"type": "string", "default": "replace"},
        },
    }

    def run(self, inputs: dict[str, pd.DataFrame]) -> pd.DataFrame:
        if len(inputs) != 1:
            raise ValueError("duckdb_load expects exactly one upstream input")
        df = next(iter(inputs.values()))

        database = Path(self.config["database"])
        database.parent.mkdir(parents=True, exist_ok=True)
        table = self.config["table"]
        schema = self.config.get("schema", "main")
        if_exists = self.config.get("if_exists", "replace")

        with duckdb.connect(str(database)) as conn:
            conn.register("incoming_df", df)
            qualified = f"{schema}.{table}"
            if if_exists == "replace":
                conn.execute(f"CREATE OR REPLACE TABLE {qualified} AS SELECT * FROM incoming_df")
            elif if_exists == "append":
                conn.execute(f"INSERT INTO {qualified} SELECT * FROM incoming_df")
            elif if_exists == "fail":
                conn.execute(f"CREATE TABLE {qualified} AS SELECT * FROM incoming_df")
            else:
                raise ValueError(f"unsupported if_exists value: {if_exists}")
            count = conn.execute(f"SELECT COUNT(*) FROM {qualified}").fetchone()[0]

        return pd.DataFrame({"table": [qualified], "rows_loaded": [count]})


REGISTRY.register(DuckDbLoad)
