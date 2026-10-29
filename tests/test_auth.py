import pytest
from fastapi import HTTPException
from backend.auth import decode_token

def test_decode_token_invalid():
    invalid_token = "invalid.token.string"

    with pytest.raises(HTTPException) as exc_info:
        decode_token(invalid_token)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Token inválido o expirado"
    assert exc_info.value.headers == {"WWW-Authenticate": "Bearer"}
