import pytest
from backend.auth import verify_password, get_password_hash

def test_verify_password_correct():
    plain_password = "my_strong_password_123"
    hashed_password = get_password_hash(plain_password)
    assert verify_password(plain_password, hashed_password) is True

def test_verify_password_incorrect():
    plain_password = "my_strong_password_123"
    wrong_password = "wrong_password"
    hashed_password = get_password_hash(plain_password)
    assert verify_password(wrong_password, hashed_password) is False

def test_verify_password_empty_password():
    plain_password = "my_strong_password_123"
    hashed_password = get_password_hash(plain_password)
    assert verify_password("", hashed_password) is False
