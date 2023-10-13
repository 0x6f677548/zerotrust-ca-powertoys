import logging
from typing import Callable

_logger = logging.getLogger(__name__)


def remove_element_from_dict(dict: dict, element: str) -> bool:
    """Remove an element from a dictionary if it exists."""
    if element in dict:
        dict.pop(element)
        return True
    return False


def replace_with_key_value_lookup(
    parent_node: dict,
    keys_node_name: str,
    values_node_name: str,
    lookup_func: Callable[[str], str],
    lookup_cache: dict = {},
) -> dict:
    """
    Creates a node in parent_node with the name values_node_name with the equivalent values of
    the node with the name keys_node_name, but looked up with the lookup_func.
    Usefull for replacing groupIds with groupNames (or vice versa) and similar scenarios.
    """
    if keys_node_name in parent_node:
        keys = parent_node[keys_node_name]
        if values_node_name not in parent_node:
            parent_node[values_node_name] = []
        for key in keys:
            if key not in lookup_cache:
                _logger.debug(f"Looking up {key}...")
                value = lookup_func(key)
                lookup_cache[key] = value
            else:
                value = lookup_cache[key]
                _logger.debug(f"Found {key} in cache: {value}")

            if value and value not in parent_node[values_node_name]:
                parent_node[values_node_name].append(value)
        remove_element_from_dict(parent_node, keys_node_name)
    return lookup_cache
