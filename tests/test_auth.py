from backend.auth import get_password_hash, verify_password

def test_password_hashing():
    password = "mysecretpassword123"
    hashed = get_password_hash(password)

    assert hashed != password
    assert isinstance(hashed, str)
    assert len(hashed) > 0

def test_verify_correct_password():
    password = "mysecretpassword123"
    hashed = get_password_hash(password)

    is_valid = verify_password(password, hashed)
    assert is_valid is True

def test_verify_incorrect_password():
    password = "mysecretpassword123"
    wrong_password = "wrongpassword"
    hashed = get_password_hash(password)

    is_valid = verify_password(wrong_password, hashed)
    assert is_valid is False
