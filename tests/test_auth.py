import pytest
import os
from datetime import datetime, timedelta, timezone
from jose import jwt

# We need to import the function and constants from the module
from backend.auth import create_access_token, JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRE_MINUTES

def test_create_access_token_default_expiration():
    # Given
    data = {"sub": "user123"}

    # When
    token = create_access_token(data)

    # Then
    # Decode the token directly to verify its payload
    decoded_payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

    # Check the data payload
    assert decoded_payload["sub"] == "user123"

    # Check the expiration time
    assert "exp" in decoded_payload

    # The default expiration is JWT_EXPIRE_MINUTES minutes from now
    expected_exp = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES)

    # Allow for a 1-second margin of error due to execution time
    assert abs(decoded_payload["exp"] - expected_exp.timestamp()) < 2


def test_create_access_token_custom_expiration():
    # Given
    data = {"sub": "admin1"}
    custom_delta = timedelta(minutes=30)

    # When
    token = create_access_token(data, expires_delta=custom_delta)

    # Then
    decoded_payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

    # Check the data payload
    assert decoded_payload["sub"] == "admin1"

    # Check the expiration time
    assert "exp" in decoded_payload

    expected_exp = datetime.now(timezone.utc) + custom_delta

    # Allow for a 1-second margin of error due to execution time
    assert abs(decoded_payload["exp"] - expected_exp.timestamp()) < 2
