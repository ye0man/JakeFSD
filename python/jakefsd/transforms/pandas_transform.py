"""Pandas transform connector."""

from __future__ import annotations

from typing import Any, ClassVar

import pandas as pd

from jakefsd.connectors.base import REGISTRY, TransformConnector
from jakefsd.models.manifest import StageType


class PandasTransform(TransformConnector):
    """Transform a DataFrame using a Pandas expression.

    The expression runs in a sandboxed namespace where the upstream DataFrame
    is available as ``df``. The expression must evaluate to a DataFrame.
    """

    name = "pandas_transform"
    stage_type = StageType.TRANSFORM
    config_schema: ClassVar[dict[str, Any]] = {
        "type": "object",
        "required": ["expression"],
        "properties": {
            "expression": {
                "type": "string",
                "description": "Python expression operating on 'df' returning a DataFrame",
            },
        },
    }

    def run(self, inputs: dict[str, pd.DataFrame]) -> pd.DataFrame:
        if len(inputs) != 1:
            raise ValueError("pandas_transform expects exactly one upstream input")
        df = next(iter(inputs.values()))
        expression = self.config["expression"]

        namespace: dict[str, Any] = {"pd": pd, "df": df}
        result = eval(expression, {"__builtins__": {}}, namespace)
        if not isinstance(result, pd.DataFrame):
            raise ValueError("pandas expression must return a DataFrame")
        return result


REGISTRY.register(PandasTransform)
