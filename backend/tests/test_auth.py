import pytest
from datetime import timedelta
from fastapi import HTTPException
from auth import decode_token, create_access_token

def test_decode_token_valid():
    # Arrange
    data = {"sub": "test_user"}
    token = create_access_token(data=data, expires_delta=timedelta(minutes=5))

    # Act
    payload = decode_token(token)

    # Assert
    assert payload["sub"] == "test_user"
    assert "exp" in payload

def test_decode_token_invalid():
    # Arrange
    invalid_token = "this.is.not.a.valid.token"

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        decode_token(invalid_token)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Token inválido o expirado"
    assert exc_info.value.headers == {"WWW-Authenticate": "Bearer"}

def test_decode_token_expired():
    # Arrange
    data = {"sub": "test_user"}
    # Create an expired token (negative timedelta)
    token = create_access_token(data=data, expires_delta=timedelta(minutes=-5))

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        decode_token(token)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Token inválido o expirado"
    assert exc_info.value.headers == {"WWW-Authenticate": "Bearer"}
