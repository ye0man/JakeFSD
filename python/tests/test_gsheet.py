"""Tests for the Google Sheets report connector."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd

from jakefsd.connectors import REGISTRY


def test_gsheet_writer_registers() -> None:
    assert "gsheet_writer" in REGISTRY.list()


def test_gsheet_writer_config_validation() -> None:
    with patch("pathlib.Path.exists", return_value=True):
        connector = REGISTRY.build(
            "gsheet_writer",
            {
                "spreadsheet_id": "abc123",
                "credentials_path": "/fake/creds.json",
                "worksheet": "Data",
            },
        )
    assert connector.config["spreadsheet_id"] == "abc123"


def test_gsheet_writer_runs_with_mocked_gspread(tmp_path: Path) -> None:
    df = pd.DataFrame({"id": [1, 2], "name": ["a", "b"]})
    creds_path = tmp_path / "creds.json"
    creds_path.write_text('{"type": "service_account"}', encoding="utf-8")

    mock_ws = MagicMock()
    mock_sheet = MagicMock()
    mock_sheet.worksheet.return_value = mock_ws
    mock_client = MagicMock()
    mock_client.open_by_key.return_value = mock_sheet

    with patch("jakefsd.connectors.report.gsheet.gspread.authorize", return_value=mock_client):
        with patch(
            "jakefsd.connectors.report.gsheet.Credentials.from_service_account_file"
        ) as mock_creds:
            connector = REGISTRY.build(
                "gsheet_writer",
                {
                    "spreadsheet_id": "abc123",
                    "credentials_path": str(creds_path),
                    "worksheet": "Data",
                },
            )
            result = connector.run({"source": df})

    mock_creds.assert_called_once()
    mock_ws.clear.assert_called_once()
    mock_ws.update.assert_called_once()
    assert result["rows"][0] == 2
