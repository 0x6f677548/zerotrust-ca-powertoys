from typing import Any


def ensure_list(source: list[dict] | dict) -> list[dict]:
    """Ensures that the source is a list.
    If it is not a list, it will be wrapped in a list.
    If it is None, an empty list will be returned."""
    if source is None:
        return []
    elif isinstance(source, list):
        return source
    elif "value" in source and isinstance(source["value"], list):
        return source["value"]
    else:
        return [source]


def cleanup_odata_dict(source: dict) -> dict:
    """Cleans up the dictionary returned by the graph api by removing
    not needed elements like @odata.context and @microsoft.graph.tips
    """

    if not source:
        exception: Exception = ValueError("The dictionary is None or empty.")
        raise exception

    remove_element_from_dict(source, "@odata.context")
    remove_element_from_dict(source, "@microsoft.graph.tips")
    return source


def remove_element_from_dict(source: dict, element: str) -> bool:
    """Remove an element from a dictionary if it exists."""
    if element in source:
        source.pop(element)
        return True
    return False


def assert_condition(condition: Any, message: str):
    """Asserts a condition and raises an AssertionError if it is False"""
    if not condition:
        raise AssertionError(message)
