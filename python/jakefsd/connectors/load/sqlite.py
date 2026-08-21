"""SQLite load connector."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, ClassVar

import pandas as pd

from jakefsd.connectors.base import REGISTRY, LoadConnector
from jakefsd.models.manifest import StageType


class SqliteLoad(LoadConnector):
    """Write a DataFrame to a SQLite table."""

    name = "sqlite_load"
    stage_type = StageType.LOAD
    config_schema: ClassVar[dict[str, Any]] = {
        "type": "object",
        "required": ["database", "table"],
        "properties": {
            "database": {"type": "string", "description": "Path to SQLite database file"},
            "table": {"type": "string", "description": "Target table name"},
            "if_exists": {"type": "string", "default": "replace"},
        },
    }

    def run(self, inputs: dict[str, pd.DataFrame]) -> pd.DataFrame:
        if len(inputs) != 1:
            raise ValueError("sqlite_load expects exactly one upstream input")
        df = next(iter(inputs.values()))

        database = Path(self.config["database"])
        database.parent.mkdir(parents=True, exist_ok=True)
        table = self.config["table"]
        if_exists = self.config.get("if_exists", "replace")

        with sqlite3.connect(str(database)) as conn:
            if if_exists == "replace":
                conn.execute(f"DROP TABLE IF EXISTS {table}")
                if_exists = "fail"
            df.to_sql(table, conn, if_exists=if_exists, index=False)
            cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]

        return pd.DataFrame({"table": [table], "rows_loaded": [count]})


REGISTRY.register(SqliteLoad)
