from typing import Any


def assert_condition(condition: Any, message: str):
    """Asserts a condition and raises an AssertionError if it is False"""
    if not condition:
        raise AssertionError(message)
