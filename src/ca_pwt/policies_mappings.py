import logging
import json
import os
from ca_pwt.groups import GroupsAPI
from ca_pwt.users import UsersAPI
from ca_pwt.directory_roles import (
    DirectoryRolesAPI,
    DirectoryRoleTemplatesAPI,
    _BUILTIN_ROLES_ID_NAME,
    _BUILTIN_ROLES_NAME_ID,
)
from ca_pwt.applications import ServicePrincipalsAPI, _BUILTIN_APPS_ID_NAME, _BUILTIN_APPS_NAME_ID
from typing import Callable
from ca_pwt.helpers.graph_api import APIResponse
from copy import deepcopy

_logger = logging.getLogger(__name__)


def _graph_api_lookup(functions: list[Callable[[str], APIResponse]], key: str, attrib_name: str) -> str | None:
    for func in functions:
        response = func(key)
        if response.success:
            return response.json()[attrib_name]
        else:
            _logger.warning(f"Could not lookup '{key}' with {func.__name__}. Response: {response}")
    return None


def _replace_with_key_value_lookup(
    parent_node: dict,
    key_value_pairs: list[tuple[str, str]],
    lookup_func: Callable[[str], str | None],
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


def load_lookup_cache_from_file(
    file_path: str,
    *,
    reverse_format: bool = False,
) -> dict[str, str]:
    """Loads a lookup cache from a json file
    The file should be a dictionary with the keys being the values to lookup and the values being the values to replace
    if reverse_format is True, the keys and values will be reversed,
    so the keys will be the values to replace and the values
    will be the values to lookup"""

    # check if the file exists
    if not os.path.exists(file_path):
        _logger.warning(f"File {file_path} does not exist. Returning empty lookup cache.")
        return {}

    with open(file_path) as f:
        data = json.load(f)
        if reverse_format:
            return {v: k for k, v in data.items()}
        else:
            return data


def replace_attrs_with_guids_in_policies(
    access_token: str,
    policies: list[dict],
    lookup_cache: dict[str, str] | None = None,
    *,
    lookup_groups: bool = True,
    lookup_users: bool = True,
    lookup_roles: bool = True,
    lookup_applications: bool = True,
) -> list[dict]:
    """Replaces attributes with guids in a policies file (e.g. group names by group ids)
    This is useful when you want to import a policies file that was exported from
    a different tenant and groups have different ids.
    """

    _logger.info("Replacing attributes with guids...")

    if _logger.isEnabledFor(logging.DEBUG):
        _logger.debug(f"Source: {policies}")
        _logger.debug(f"Lookup cache: {lookup_cache}")

    if lookup_cache is None:
        # we'll initialize the lookup cache with known objects, like the built-in roles
        # so we don't have to make a call to the graph api for each one of them
        lookup_cache: dict[str, str] = deepcopy(_BUILTIN_ROLES_NAME_ID)
        # append the built-in apps
        lookup_cache.update(_BUILTIN_APPS_NAME_ID)

    groups_api = GroupsAPI(access_token=access_token)
    users_api = UsersAPI(access_token=access_token)
    dir_roles_api: DirectoryRolesAPI = DirectoryRolesAPI(access_token)
    dir_role_templates_api: DirectoryRoleTemplatesAPI = DirectoryRoleTemplatesAPI(access_token)
    svc_principals_api = ServicePrincipalsAPI(access_token=access_token)

    for policy in policies:
        # let's transform groupIds to groupNames if any
        conditions = policy["conditions"]
        users = conditions["users"]
        if lookup_groups:
            lookup_cache = _replace_with_key_value_lookup(
                parent_node=users,
                key_value_pairs=[
                    ("excludeGroupNames", "excludeGroups"),
                    ("includeGroupNames", "includeGroups"),
                ],
                lookup_func=lambda key: _graph_api_lookup([groups_api.get_by_display_name], key, "id"),
                lookup_cache=lookup_cache,
            )
        if lookup_users:
            lookup_cache = _replace_with_key_value_lookup(
                parent_node=users,
                key_value_pairs=[
                    ("excludeUserNames", "excludeUsers"),
                    ("includeUserNames", "includeUsers"),
                ],
                lookup_func=lambda key: _graph_api_lookup([users_api.get_by_id], key, "id"),
                lookup_cache=lookup_cache,
            )
        if lookup_roles:
            lookup_cache = _replace_with_key_value_lookup(
                parent_node=users,
                key_value_pairs=[
                    ("includeRoleNames", "includeRoles"),
                    ("excludeRoleNames", "excludeRoles"),
                ],
                lookup_func=lambda key: _graph_api_lookup(
                    [
                        dir_roles_api.get_by_display_name,
                        dir_role_templates_api.get_by_display_name,
                    ],
                    key,
                    "id",
                ),
                lookup_cache=lookup_cache,
            )
        if lookup_applications:
            applications = conditions["applications"]
            lookup_cache = _replace_with_key_value_lookup(
                parent_node=applications,
                key_value_pairs=[
                    ("includeApplicationNames", "includeApplications"),
                    ("excludeApplicationNames", "excludeApplications"),
                ],
                # in CA policies, applications are represented by service principals app id
                lookup_func=lambda key: _graph_api_lookup([svc_principals_api.get_by_display_name], key, "appId"),
                lookup_cache=lookup_cache,
            )

    if _logger.isEnabledFor(logging.DEBUG):
        _logger.debug(f"Source: {policies}")

    return policies


def replace_guids_with_attrs_in_policies(
    access_token: str,
    policies: list[dict],
    lookup_cache: dict[str, str] | None = None,
    *,
    lookup_groups: bool = True,
    lookup_users: bool = True,
    lookup_roles: bool = True,
    lookup_applications: bool = True,
) -> list[dict]:
    """Replaces guids with attributes in a policies file
    e.g.: "includeGroups": ["<group-id>"] -> "includeGroupNames": ["<group-name>"]
    This is useful when you want to export a policies file that can be imported in a
    different tenant and groups have different ids or when you want to maintain a policies
    file in a source control system and you want to use group names instead of ids.
    """
    _logger.info("Replacing guids with attributes in policies file...")

    if _logger.isEnabledFor(logging.DEBUG):
        _logger.debug(f"Source: {policies}")

    if lookup_cache is None:
        # we'll initialize the lookup cache with known objects, like the built-in roles
        # so we don't have to make a call to the graph api for each one of them
        lookup_cache: dict[str, str] = deepcopy(_BUILTIN_ROLES_ID_NAME)
        # append the built-in apps
        lookup_cache.update(_BUILTIN_APPS_ID_NAME)

    groups_api: GroupsAPI = GroupsAPI(access_token)
    users_api: UsersAPI = UsersAPI(access_token)
    dir_roles_api: DirectoryRolesAPI = DirectoryRolesAPI(access_token)
    dir_role_templates_api: DirectoryRoleTemplatesAPI = DirectoryRoleTemplatesAPI(access_token)
    svc_principals_api: ServicePrincipalsAPI = ServicePrincipalsAPI(access_token)

    for policy in policies:
        # let's transform groupIds to groupNames if any
        conditions = policy["conditions"]
        users = conditions["users"]
        if lookup_groups:
            lookup_cache = _replace_with_key_value_lookup(
                parent_node=users,
                key_value_pairs=[
                    ("excludeGroups", "excludeGroupNames"),
                    ("includeGroups", "includeGroupNames"),
                ],
                lookup_func=lambda key: _graph_api_lookup([groups_api.get_by_id], key, "displayName"),
                lookup_cache=lookup_cache,
            )
        if lookup_users:
            lookup_cache = _replace_with_key_value_lookup(
                parent_node=users,
                key_value_pairs=[
                    ("excludeUsers", "excludeUserNames"),
                    ("includeUsers", "includeUserNames"),
                ],
                lookup_func=lambda key: _graph_api_lookup([users_api.get_by_id], key, "userPrincipalName"),
                lookup_cache=lookup_cache,
            )
        if lookup_roles:
            lookup_cache = _replace_with_key_value_lookup(
                parent_node=users,
                key_value_pairs=[
                    ("excludeRoles", "excludeRoleNames"),
                    ("includeRoles", "includeRoleNames"),
                ],
                lookup_func=lambda key: _graph_api_lookup(
                    [dir_roles_api.get_by_id, dir_role_templates_api.get_by_id],
                    key,
                    "displayName",
                ),
                lookup_cache=lookup_cache,
            )
        if lookup_applications:
            applications = conditions["applications"]
            lookup_cache = _replace_with_key_value_lookup(
                parent_node=applications,
                key_value_pairs=[
                    ("excludeApplications", "excludeApplicationNames"),
                    ("includeApplications", "includeApplicationNames"),
                ],
                # in CA policies, applications are represented by service principals app id
                lookup_func=lambda key: _graph_api_lookup([svc_principals_api.get_by_app_id], key, "displayName"),
                lookup_cache=lookup_cache,
            )

    if _logger.isEnabledFor(logging.DEBUG):
        _logger.debug(f"Output: {policies}")

    return policies
