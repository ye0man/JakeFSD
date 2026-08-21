"""REST API collector connector."""

from __future__ import annotations

from typing import Any, ClassVar

import httpx
import pandas as pd

from jakefsd.connectors.base import REGISTRY, SourceConnector
from jakefsd.models.manifest import StageType


class RestApiCollector(SourceConnector):
    """Fetch JSON data from a REST API, with optional API-key auth."""

    name = "rest_api"
    stage_type = StageType.COLLECT
    config_schema: ClassVar[dict[str, Any]] = {
        "type": "object",
        "required": ["url"],
        "properties": {
            "url": {"type": "string", "description": "Request URL"},
            "method": {"type": "string", "default": "GET"},
            "headers": {"type": "object", "default": {}},
            "params": {"type": "object", "default": {}},
            "api_key": {"type": "string", "description": "API key value"},
            "api_key_header": {"type": "string", "default": "Authorization"},
            "api_key_prefix": {"type": "string", "default": "Bearer "},
            "json_path": {"type": "string", "description": "JSONPath-like dotted path to records"},
            "timeout": {"type": "number", "default": 30},
        },
    }

    def collect(self) -> pd.DataFrame:
        url = self.config["url"]
        method = self.config.get("method", "GET").upper()
        headers = dict(self.config.get("headers", {}))
        params = dict(self.config.get("params", {}))

        if "api_key" in self.config:
            header_name = self.config.get("api_key_header", "Authorization")
            prefix = self.config.get("api_key_prefix", "Bearer ")
            headers[header_name] = f"{prefix}{self.config['api_key']}".strip()

        timeout = self.config.get("timeout", 30)
        with httpx.Client(timeout=timeout) as client:
            response = client.request(method, url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()

        json_path = self.config.get("json_path")
        if json_path:
            for part in json_path.split("."):
                if isinstance(data, dict):
                    data = data[part]
                elif isinstance(data, list):
                    data = [item[part] for item in data]
                else:
                    raise ValueError(f"cannot traverse json_path at {part}")

        if isinstance(data, list):
            return pd.json_normalize(data)
        return pd.json_normalize([data])


REGISTRY.register(RestApiCollector)
