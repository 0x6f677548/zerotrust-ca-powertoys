import logging
from typing import Callable

_logger = logging.getLogger(__name__)


def cleanup_odata_dict(source: dict, *, ensure_list: bool = True) -> dict:
    """Cleans up the dictionary returned by the graph api
    It removes the @odata.context element and returns the value element if it is a list
    If the value element is not a list, it wraps it in a list
    """
    remove_element_from_dict(source, "@odata.context")
    remove_element_from_dict(source, "@microsoft.graph.tips")

    # check if it is the graph api response format (i.e. a dict with a value key)
    # if so, let's get the value and make sure it is a list
    if "value" in source and source["value"] is not None and isinstance(source["value"], list):
        source = source["value"]

    # check if we have a single policy. If so, let's wrap it in a list
    elif ensure_list and source and not isinstance(source, list):
        source = [source]
    elif not source:
        exception: Exception = ValueError("The dictionary is not in the expected format.")
        raise exception
    return source


def remove_element_from_dict(source: dict, element: str) -> bool:
    """Remove an element from a dictionary if it exists."""
    if element in source:
        source.pop(element)
        return True
    return False


def replace_with_key_value_lookup(
    parent_node: dict,
    key_value_pairs: list[tuple[str, str]],
    lookup_func: Callable[[str | None], str | None],
    lookup_cache: dict | None = None,
) -> dict:
    """
    Creates a node in parent_node with the name values_node_name with the equivalent values of
    the node with the name keys_node_name, but looked up with the lookup_func.
    Usefull for replacing groupIds with groupNames (or vice versa) and similar scenarios.
    """
    if lookup_cache is None:
        lookup_cache = {}

    for keys_node_name, values_node_name in key_value_pairs:
        _logger.debug(f"Replacing {keys_node_name} with {values_node_name}...")
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
