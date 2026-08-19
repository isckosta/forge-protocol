import pytest

from accounts.users import create_username


def test_create_username_returns_the_given_name() -> None:
    assert create_username("alice") == "alice"


def test_create_username_rejects_empty_name() -> None:
    with pytest.raises(ValueError):
        create_username("")
