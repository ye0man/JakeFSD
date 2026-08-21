"""CSV export report connector."""

from __future__ import annotations

from pathlib import Path
from typing import Any, ClassVar

import pandas as pd

from jakefsd.connectors.base import REGISTRY, ReportConnector
from jakefsd.models.manifest import StageType


class CsvExportReport(ReportConnector):
    """Write a DataFrame to a CSV file."""

    name = "csv_export"
    stage_type = StageType.REPORT
    config_schema: ClassVar[dict[str, Any]] = {
        "type": "object",
        "required": ["path"],
        "properties": {
            "path": {"type": "string", "description": "Output CSV file path"},
            "delimiter": {"type": "string", "default": ","},
            "index": {"type": "boolean", "default": False},
        },
    }

    def run(self, inputs: dict[str, pd.DataFrame]) -> pd.DataFrame:
        if len(inputs) != 1:
            raise ValueError("csv_export expects exactly one upstream input")
        df = next(iter(inputs.values()))

        path = Path(self.config["path"])
        path.parent.mkdir(parents=True, exist_ok=True)
        delimiter = self.config.get("delimiter", ",")
        index = self.config.get("index", False)
        df.to_csv(path, sep=delimiter, index=index)

        return pd.DataFrame({"path": [str(path)], "rows": [len(df)]})


REGISTRY.register(CsvExportReport)
