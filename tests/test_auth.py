import pytest
from datetime import datetime, timedelta, timezone

from backend.auth import create_access_token, decode_token, JWT_EXPIRE_MINUTES

def test_create_access_token_without_expires_delta():
    data = {"sub": "testuser"}
    before_creation = datetime.now(timezone.utc)
    token = create_access_token(data=data)
    after_creation = datetime.now(timezone.utc)

    payload = decode_token(token)
    assert "exp" in payload
    assert payload["sub"] == "testuser"

    exp = payload["exp"]

    expected_min = before_creation + timedelta(minutes=JWT_EXPIRE_MINUTES)
    expected_max = after_creation + timedelta(minutes=JWT_EXPIRE_MINUTES)

    assert expected_min.timestamp() - 1 <= exp <= expected_max.timestamp() + 1

def test_create_access_token_with_expires_delta():
    data = {"sub": "testuser"}
    delta = timedelta(minutes=15)
    before_creation = datetime.now(timezone.utc)
    token = create_access_token(data=data, expires_delta=delta)
    after_creation = datetime.now(timezone.utc)

    payload = decode_token(token)
    assert "exp" in payload
    assert payload["sub"] == "testuser"

    exp = payload["exp"]

    expected_min = before_creation + delta
    expected_max = after_creation + delta

    assert expected_min.timestamp() - 1 <= exp <= expected_max.timestamp() + 1
