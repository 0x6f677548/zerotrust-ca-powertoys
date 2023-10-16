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
    lookup_func: Callable[[str | None], str],
    lookup_cache: dict = {},
) -> dict:
    """
    Creates a node in parent_node with the name values_node_name with the equivalent values of
    the node with the name keys_node_name, but looked up with the lookup_func.
    Usefull for replacing groupIds with groupNames (or vice versa) and similar scenarios.
    """
    if keys_node_name in parent_node:

        # create the values node if it doesn't exist
        if values_node_name not in parent_node:
            parent_node[values_node_name] = []

        # this will contain the keys that have been mapped
        mapped_elements = []

        keys = parent_node[keys_node_name]
        for key in keys:
            if key in lookup_cache:
                value = lookup_cache[key]
                _logger.debug(f"Found {key} in cache: {value}")
            else:
                _logger.debug(f"Looking up {key}...")
                value = lookup_func(key)
                lookup_cache[key] = value

            # we'll only add the value if it's not None
            if value:
                parent_node[values_node_name].append(value)
                mapped_elements.append(key)

        # remove all keys that have been mapped
        for key in mapped_elements:
            keys.remove(key)

        _logger.debug(f"Keys for {keys_node_name}: {keys}")
        _logger.debug(f"values for {values_node_name}: {parent_node[values_node_name]}")

        # remove the keys node if it's empty
        if not keys:
            _logger.debug(f"Removing {keys_node_name}...")
            parent_node.pop(keys_node_name)

        # remove the values node if it's empty
        if not parent_node[values_node_name]:
            _logger.debug(f"Removing {values_node_name}...")
            parent_node.pop(values_node_name)
    return lookup_cache
