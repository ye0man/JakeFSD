"""Tests for credential storage integration."""

from __future__ import annotations

from jakefsd.credentials import delete_credential, get_credential, resolve, set_credential


def test_set_get_delete_credential() -> None:
    set_credential("__test_api_key", "secret123")
    try:
        assert get_credential("__test_api_key") == "secret123"
    finally:
        delete_credential("__test_api_key")
    assert get_credential("__test_api_key") is None


def test_resolve_keyring_reference() -> None:
    set_credential("__test_resolve", "resolved_value")
    try:
        assert resolve("keyring:__test_resolve") == "resolved_value"
    finally:
        delete_credential("__test_resolve")


def test_resolve_plain_value() -> None:
    assert resolve("plain_value") == "plain_value"
