"""OS credential store integration with a file fallback."""

from __future__ import annotations

import json
import os
import stat
from pathlib import Path
from typing import Any

import keyring
from keyring.errors import NoKeyringError

SERVICE_NAME = "jakefsd"


def _fallback_path() -> Path:
    """Path to the local fallback credential file."""
    config_dir = Path.home() / ".config" / "jakefsd"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "credentials.json"


def _load_fallback() -> dict[str, str]:
    path = _fallback_path()
    if not path.exists():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def _save_fallback(creds: dict[str, str]) -> None:
    path = _fallback_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(creds, f)
    os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)


def _using_fallback() -> bool:
    """Return True if no usable OS keyring backend is available."""
    try:
        keyring.get_password(SERVICE_NAME, "__jakefsd_probe__")
        return False
    except NoKeyringError:
        return True


def set_credential(name: str, value: str) -> None:
    """Store a credential in the OS keychain, falling back to a local file."""
    if _using_fallback():
        creds = _load_fallback()
        creds[name] = value
        _save_fallback(creds)
        return
    keyring.set_password(SERVICE_NAME, name, value)


def get_credential(name: str) -> str | None:
    """Retrieve a credential, falling back to the local file if needed."""
    if _using_fallback():
        return _load_fallback().get(name)
    return keyring.get_password(SERVICE_NAME, name)


def delete_credential(name: str) -> None:
    """Delete a credential from the OS keychain or local fallback file."""
    if _using_fallback():
        creds = _load_fallback()
        creds.pop(name, None)
        _save_fallback(creds)
        return
    keyring.delete_password(SERVICE_NAME, name)


def resolve(value: Any) -> Any:
    """Resolve a credential reference like ``keyring:my_api_key``."""
    if isinstance(value, str) and value.startswith("keyring:"):
        name = value[len("keyring:"):]
        stored = get_credential(name)
        if stored is None:
            raise KeyError(f"credential not found in keyring: {name}")
        return stored
    return value
