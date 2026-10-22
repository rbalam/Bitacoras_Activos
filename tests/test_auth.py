from backend.auth import get_password_hash, verify_password

def test_get_password_hash():
    password = "my_secret_password"
    hashed_password = get_password_hash(password)

    # Assert that it returns a string
    assert isinstance(hashed_password, str)

    # Assert that the hash is different from the plain password
    assert hashed_password != password

    # Assert that the hash can be verified successfully
    assert verify_password(password, hashed_password) is True

    # Assert that a wrong password doesn't verify
    assert verify_password("wrong_password", hashed_password) is False
