import pytest
from backend.auth import get_password_hash, verify_password

def test_get_password_hash():
    password = "mysecretpassword"

    # Check that it returns a string
    hashed1 = get_password_hash(password)
    assert isinstance(hashed1, str)

    # Check that it's different from the plain text
    assert hashed1 != password

    # Check that hashing the same password twice yields different hashes (due to salting)
    hashed2 = get_password_hash(password)
    assert hashed1 != hashed2

def test_verify_password():
    password = "mysecretpassword"
    wrong_password = "wrongpassword"

    # Create a valid hash
    hashed = get_password_hash(password)

    # Check it returns True for correct plaintext
    assert verify_password(password, hashed) is True

    # Check it returns False for incorrect plaintext
    assert verify_password(wrong_password, hashed) is False
