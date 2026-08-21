"""Tests for built-in connectors."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from jakefsd.connectors import REGISTRY


def test_csv_file_collector(tmp_path: Path) -> None:
    path = tmp_path / "data.csv"
    path.write_text("id,name\n1,alice\n2,bob\n")

    connector = REGISTRY.build("csv_file", {"path": str(path)})
    df = connector.collect()
    assert len(df) == 2
    assert list(df.columns) == ["id", "name"]


def test_json_file_collector_object(tmp_path: Path) -> None:
    path = tmp_path / "data.json"
    path.write_text(json.dumps([{"id": 1, "name": "alice"}, {"id": 2, "name": "bob"}]))

    connector = REGISTRY.build("json_file", {"path": str(path)})
    df = connector.collect()
    assert len(df) == 2


def test_json_lines_collector(tmp_path: Path) -> None:
    path = tmp_path / "data.jsonl"
    path.write_text('{"id":1}\n{"id":2}\n')

    connector = REGISTRY.build("json_file", {"path": str(path), "lines": True})
    df = connector.collect()
    assert len(df) == 2


def test_duckdb_load_and_read(tmp_path: Path) -> None:
    db_path = tmp_path / "test.duckdb"
    df = pd.DataFrame({"id": [1, 2], "value": ["a", "b"]})

    connector = REGISTRY.build(
        "duckdb_load", {"database": str(db_path), "table": "items"}
    )
    result = connector.run({"source": df})
    assert result["rows_loaded"][0] == 2


def test_sqlite_load_and_read(tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"
    df = pd.DataFrame({"id": [1, 2], "value": ["a", "b"]})

    connector = REGISTRY.build(
        "sqlite_load", {"database": str(db_path), "table": "items"}
    )
    result = connector.run({"source": df})
    assert result["rows_loaded"][0] == 2


def test_csv_export_report(tmp_path: Path) -> None:
    out = tmp_path / "out.csv"
    df = pd.DataFrame({"id": [1, 2]})

    connector = REGISTRY.build("csv_export", {"path": str(out)})
    result = connector.run({"source": df})
    assert result["rows"][0] == 2
    assert out.exists()


def test_html_dashboard_report(tmp_path: Path) -> None:
    out = tmp_path / "out.html"
    df = pd.DataFrame({"id": [1, 2]})

    connector = REGISTRY.build("html_dashboard", {"path": str(out)})
    result = connector.run({"source": df})
    assert result["rows"][0] == 2
    assert out.exists()
    assert "JakeFSD Report" in out.read_text()


def test_pandas_transform() -> None:
    df = pd.DataFrame({"id": [1, 2, 3]})
    connector = REGISTRY.build(
        "pandas_transform", {"expression": "df[df['id'] > 1]"}
    )
    result = connector.run({"source": df})
    assert len(result) == 2


def test_sql_transform() -> None:
    df = pd.DataFrame({"id": [1, 2, 3]})
    connector = REGISTRY.build(
        "sql_transform", {"sql": "SELECT * FROM incoming WHERE id > 1"}
    )
    result = connector.run({"source": df})
    assert len(result) == 2
