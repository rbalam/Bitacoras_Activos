import os
import pytest

# Ensure we test with no JWT_SECRET env var to check the fallback
def test_jwt_secret_fallback():
    # Store original if present
    original_secret = os.environ.get("JWT_SECRET")
    if "JWT_SECRET" in os.environ:
        del os.environ["JWT_SECRET"]

    try:
        # Import after modifying environ so that fallback gets triggered on module load
        import backend.auth as auth

        # Reload module to ensure the os.environ.get is re-evaluated
        import importlib
        importlib.reload(auth)

        # Verify secret is not the vulnerable hardcoded one
        assert auth.JWT_SECRET != "your-secret-key-change-in-production"
        # Verify it has generated a reasonable length secret
        assert len(auth.JWT_SECRET) >= 32

    finally:
        # Restore environment
        if original_secret is not None:
            os.environ["JWT_SECRET"] = original_secret
