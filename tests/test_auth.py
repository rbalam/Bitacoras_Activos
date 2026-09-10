import os
import pytest

def test_auth_raises_value_error_if_no_jwt_secret():
    if "JWT_SECRET" in os.environ:
        del os.environ["JWT_SECRET"]

    with pytest.raises(ValueError, match="JWT_SECRET environment variable is not set"):
        # We need to force a reload since the module is evaluated at import time
        import importlib
        import backend.auth
        importlib.reload(backend.auth)

def test_auth_loads_with_jwt_secret():
    os.environ["JWT_SECRET"] = "some-secret"

    import importlib
    import backend.auth
    importlib.reload(backend.auth)
    assert backend.auth.JWT_SECRET == "some-secret"
