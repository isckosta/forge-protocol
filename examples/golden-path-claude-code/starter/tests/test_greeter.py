import pytest

from greeting.greeter import greet


def test_greet_returns_a_greeting() -> None:
    assert greet("Ana") == "Hello, Ana!"


def test_greet_rejects_empty_name() -> None:
    with pytest.raises(ValueError):
        greet("")
