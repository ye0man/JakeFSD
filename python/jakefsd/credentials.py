"""OS credential store integration."""

from __future__ import annotations

from typing import Any

import keyring

SERVICE_NAME = "jakefsd"


def set_credential(name: str, value: str) -> None:
    """Store a credential in the OS keychain."""
    keyring.set_password(SERVICE_NAME, name, value)


def get_credential(name: str) -> str | None:
    """Retrieve a credential from the OS keychain."""
    return keyring.get_password(SERVICE_NAME, name)


def delete_credential(name: str) -> None:
    """Delete a credential from the OS keychain."""
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
