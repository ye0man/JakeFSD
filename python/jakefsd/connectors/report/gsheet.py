"""Google Sheets report connector."""

from __future__ import annotations

from pathlib import Path
from typing import Any, ClassVar

import gspread
import pandas as pd
from google.oauth2.service_account import Credentials

from jakefsd.connectors.base import REGISTRY, ReportConnector
from jakefsd.models.manifest import StageType


class GoogleSheetsReport(ReportConnector):
    """Write a DataFrame to a Google Sheet.

    Authenticates with a service-account JSON file. The Google Sheet must be
    shared with the service account email (viewable in the credentials file).
    """

    name = "gsheet_writer"
    stage_type = StageType.REPORT
    config_schema: ClassVar[dict[str, Any]] = {
        "type": "object",
        "required": ["spreadsheet_id", "credentials_path"],
        "properties": {
            "spreadsheet_id": {"type": "string"},
            "worksheet": {"type": "string", "default": "Sheet1"},
            "credentials_path": {"type": "string"},
        },
    }

    def run(self, inputs: dict[str, pd.DataFrame]) -> pd.DataFrame:
        if len(inputs) != 1:
            raise ValueError("gsheet_writer expects exactly one upstream input")
        df = next(iter(inputs.values()))

        spreadsheet_id = self.config["spreadsheet_id"]
        worksheet_name = self.config.get("worksheet", "Sheet1")
        credentials_path = Path(self.config["credentials_path"])

        if not credentials_path.exists():
            raise FileNotFoundError(f"Google credentials file not found: {credentials_path}")

        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_file(str(credentials_path), scopes=scopes)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(spreadsheet_id)

        try:
            ws = sheet.worksheet(worksheet_name)
        except gspread.WorksheetNotFound:
            ws = sheet.add_worksheet(title=worksheet_name, rows=1, cols=1)

        ws.clear()
        ws.update([df.columns.values.tolist()] + df.values.tolist())

        return pd.DataFrame({
            "spreadsheet_id": [spreadsheet_id],
            "worksheet": [worksheet_name],
            "rows": [len(df)],
        })


REGISTRY.register(GoogleSheetsReport)
