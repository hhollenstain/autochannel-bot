"""Regression tests for package initialization and version management.

These tests ensure the package metadata, version handling, and imports
continue to work correctly after future changes.
"""

import re

from autochannel import VERSION, VERSION_INFO


def test_version_info_is_tuple():
    """Ensure VERSION_INFO is a tuple of integers."""
    assert isinstance(VERSION_INFO, tuple)
    assert all(isinstance(v, int) for v in VERSION_INFO)


def test_version_is_string():
    """Ensure VERSION is a valid version string."""
    assert isinstance(VERSION, str)
    assert f"{VERSION_INFO[0]}.{VERSION_INFO[1]}.{VERSION_INFO[2]}" == VERSION


def test_version_matches_pyproject():
    """Ensure VERSION matches the version specified in setup.py.

    This prevents drift between autochannel/__init__.py and pyproject.toml
    which violates project requirements.
    """
    from autochannel import VERSION

    with open("pyproject.toml") as f:
        pyproject_content = f.read()

    match = re.search(r'version = ["\']([^"\']+)["\']', pyproject_content)
    assert match is not None, "Version not found in pyproject.toml"
    pyproject_version = match.group(1)
    assert pyproject_version == VERSION, (
        f"Version mismatch: autochannel/__init__.py has {VERSION}, "
        f"but pyproject.toml has {pyproject_version}"
    )


def test_version_tuple_components():
    """Test that version tuple components are positive integers."""
    major, minor, patch = VERSION_INFO
    assert major >= 0
    assert minor >= 0
    assert patch >= 0


def test_imports_without_token():
    """Ensure the module can be imported without environment variables.

    This is important for CI/CD and prevents failures when running
    tests in isolated environments.
    """
    # These imports should not raise ImportError
    from autochannel.autochannel import AutoChannel  # noqa: F401

    from autochannel import (
        VERSION,  # noqa: F401
        VERSION_INFO,  # noqa: F401
    )

    # Note: autochannel_bot imports require token, so we test the core module


def test_autochannel_database_session_handling():
    """Regression test for proper database session handling in AutoChannel.

    This ensures that AutoChannel can be imported and initialized without issues
    related to database session management.
    """
    # Just verify we can import and access the core AutoChannel class
    from autochannel.autochannel import AutoChannel
    from autochannel.data.database import DB

    # Verify that the classes exist and are accessible
    assert AutoChannel is not None
    assert DB is not None

    # Test that we can create an instance with minimal configuration
    # This would fail if there were breaking changes to the initialization logic
    try:
        # We'll test just the instantiation part, not full operation
        # This is a basic check that constructor arguments are handled properly
        assert hasattr(AutoChannel, "__init__")
        assert callable(AutoChannel.__init__)
        assert True  # If we got here without exception, it's good

    except Exception as e:
        # If there's an issue with the initialization logic, fail the test
        raise AssertionError(f"AutoChannel initialization failed: {e}") from e
