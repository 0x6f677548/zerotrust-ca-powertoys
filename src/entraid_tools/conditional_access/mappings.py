import logging
import click
from ..helpers.dict import replace_with_key_value_lookup
from ..groups.graph_api import GroupsAPI
from ..users.graph_api import UsersAPI
from ..directory_roles.graph_api import DirectoryRolesAPI, DirectoryRoleTemplatesAPI
from typing import Callable
from ..helpers.graph_api import APIResponse
from ..directory_roles.builtin import ID_TO_NAME_MAPPING, NAME_TO_ID_MAPPING

_logger = logging.getLogger(__name__)


def _graph_api_lookup(
    functions: list[Callable[[str], APIResponse]], key: str, attrib_name: str
) -> str | None:
    for func in functions:
        response = func(key)
        if response.success:
            return response.json()[attrib_name]
        else:
            _logger.debug(
                f"Callable {func.__name__}: Entity with key {key} not found. Response: {response}"
            )
    return None


def names_to_ids(access_token: str, source: dict) -> dict:
    click.echo("Converting names to ids...")

    if _logger.isEnabledFor(logging.DEBUG):
        _logger.debug(f"Source: {source}")

    # we'll initialize the lookup cache with known objects, like the built-in roles
    # so we don't have to make a call to the graph api for each one of them
    lookup_cache: dict = NAME_TO_ID_MAPPING

    groups_api = GroupsAPI(access_token=access_token)
    users_api = UsersAPI(access_token=access_token)
    dir_roles_api: DirectoryRolesAPI = DirectoryRolesAPI(access_token)
    dir_role_templates_api: DirectoryRoleTemplatesAPI = DirectoryRoleTemplatesAPI(
        access_token
    )

    for policy in source:
        # let's transform groupIds to groupNames if any
        conditions = policy["conditions"]
        users = conditions["users"]
        lookup_cache = replace_with_key_value_lookup(
            parent_node=users,
            key_value_pairs=[
                ("excludeGroupNames", "excludeGroups"),
                ("includeGroupNames", "includeGroups"),
            ],
            lookup_func=lambda key: _graph_api_lookup(
                [groups_api.get_by_display_name], key, "id"
            ),
            lookup_cache=lookup_cache,
        )
        lookup_cache = replace_with_key_value_lookup(
            parent_node=users,
            key_value_pairs=[
                ("excludeUserNames", "excludeUsers"),
                ("includeUserNames", "includeUsers"),
            ],
            lookup_func=lambda key: _graph_api_lookup([users_api.get_by_id], key, "id"),
            lookup_cache=lookup_cache,
        )
        lookup_cache = replace_with_key_value_lookup(
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

    if _logger.isEnabledFor(logging.DEBUG):
        _logger.debug(f"Source: {source}")

    return source


def ids_to_names(access_token: str, source: dict) -> dict:
    click.echo("Converting ids to names...")

    if _logger.isEnabledFor(logging.DEBUG):
        _logger.debug(f"Source: {source}")

    # we'll initialize the lookup cache with known objects, like the built-in roles
    # so we don't have to make a call to the graph api for each one of them
    lookup_cache: dict = ID_TO_NAME_MAPPING

    groups_api: GroupsAPI = GroupsAPI(access_token)
    users_api: UsersAPI = UsersAPI(access_token)
    dir_roles_api: DirectoryRolesAPI = DirectoryRolesAPI(access_token)
    dir_role_templates_api: DirectoryRoleTemplatesAPI = DirectoryRoleTemplatesAPI(
        access_token
    )

    for policy in source:
        # let's transform groupIds to groupNames if any
        conditions = policy["conditions"]
        users = conditions["users"]
        lookup_cache = replace_with_key_value_lookup(
            parent_node=users,
            key_value_pairs=[
                ("excludeGroups", "excludeGroupNames"),
                ("includeGroups", "includeGroupNames"),
            ],
            lookup_func=lambda key: _graph_api_lookup([groups_api.get_by_id], key, "displayName"),
            lookup_cache=lookup_cache,
        )
        lookup_cache = replace_with_key_value_lookup(
            parent_node=users,
            key_value_pairs=[
                ("excludeUsers", "excludeUserNames"),
                ("includeUsers", "includeUserNames"),
            ],
            lookup_func=lambda key: _graph_api_lookup(
                [users_api.get_by_id], key, "userPrincipalName"
            ),
            lookup_cache=lookup_cache,
        )
        lookup_cache = replace_with_key_value_lookup(
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

    if _logger.isEnabledFor(logging.DEBUG):
        _logger.debug(f"Source: {source}")

    return source
