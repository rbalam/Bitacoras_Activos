import pytest
from datetime import datetime, timedelta, timezone
from jose import jwt
from backend.auth import create_access_token, JWT_EXPIRE_MINUTES, JWT_SECRET, JWT_ALGORITHM

def test_create_access_token_default_expiration():
    data = {"sub": "test_user"}
    token = create_access_token(data)

    assert isinstance(token, str)

    payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    assert payload["sub"] == "test_user"
    assert "exp" in payload

    # Check if exp is approximately datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES)
    exp_timestamp = payload["exp"]
    exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)

    expected_exp = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES)

    # Allow some tolerance for execution time
    assert abs((exp_datetime - expected_exp).total_seconds()) < 5

def test_create_access_token_custom_expiration():
    data = {"sub": "test_user_custom"}
    custom_delta = timedelta(minutes=15)
    token = create_access_token(data, expires_delta=custom_delta)

    assert isinstance(token, str)

    payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    assert payload["sub"] == "test_user_custom"
    assert "exp" in payload

    exp_timestamp = payload["exp"]
    exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)

    expected_exp = datetime.now(timezone.utc) + custom_delta

    assert abs((exp_datetime - expected_exp).total_seconds()) < 5
