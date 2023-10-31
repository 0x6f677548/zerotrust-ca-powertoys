import logging
from ca_pwt.helpers.utils import remove_element_from_dict, cleanup_odata_dict, ensure_list
from ca_pwt.helpers.graph_api import EntityAPI, DuplicateActionEnum
from ca_pwt.policies_mappings import replace_attrs_with_guids_in_policies
from ca_pwt.groups import get_groups_by_ids
from typing import Any
from ca_pwt.helpers.graph_api import _HTTP_NOT_FOUND

_logger = logging.getLogger(__name__)


class PoliciesAPI(EntityAPI):
    def _get_entity_path(self) -> str:
        return "identity/conditionalAccess/policies"


def load_policies(input_file: str) -> list[dict]:
    """Loads policies from the specified file.
    It also cleans up the dictionary to remove unnecessary elements."""
    import json

    with open(input_file) as f:
        _logger.info(f"Reading policies from file {input_file}...")

        policies = cleanup_odata_dict(json.load(f))
        return ensure_list(policies)


def save_policies(policies: list[dict], output_file: str):
    """Saves policies to the specified file."""
    import json

    with open(output_file, "w") as f:
        _logger.info(f"Writing policies to file {output_file}...")
        f.write(json.dumps(policies, indent=4))


def cleanup_policies(policies: list[dict]) -> list[dict]:
    """Cleans up the policies dictionary for import by
    removing disallowed elements while importing. (e.g. id, createdDateTime,
    modifiedDateTime, templateId, id"""
    _logger.info("Cleaning up policies...")

    # exclude some elements, namely createdDateTime,
    # modifiedDateTime, id, templateId, authenticationStrength@odata.context
    for policy in policies:
        remove_element_from_dict(policy, "createdDateTime")
        remove_element_from_dict(policy, "modifiedDateTime")
        remove_element_from_dict(policy, "id")
        remove_element_from_dict(policy, "templateId")
        grant_controls = policy["grantControls"]
        if grant_controls is not None:
            remove_element_from_dict(grant_controls, "authenticationStrength@odata.context")
    return policies


def export_policies(access_token: str, odata_filter: str | None = None) -> list[dict]:
    """Exports all policies with the specified filter. Filter is
    an OData filter string."""
    policies_api = PoliciesAPI(access_token=access_token)
    response = policies_api.get_all(odata_filter=odata_filter)
    response.assert_success()
    policies = response.json()

    _logger.debug(f"Obtained policies: {policies}")
    policies = cleanup_odata_dict(policies)
    policies = ensure_list(policies)
    _logger.debug(f"Formatted policies: {policies}")
    return policies


def import_policies(
    access_token: str,
    policies: list[dict],
    duplicate_action: DuplicateActionEnum = DuplicateActionEnum.IGNORE,
) -> list[tuple[str, str]]:
    """Imports the specified policies. If allow_duplicates is False,
    it will skip policies that already exist (using the display name as
    the key). Returns a list of tuples with the display name and id of the
    imported policies.
    It also cleans up the dictionary to remove unnecessary elements that
    are not allowed when importing."""

    policies_api = PoliciesAPI(access_token=access_token)
    policies = replace_attrs_with_guids_in_policies(
        access_token, policies, lookup_groups=True, lookup_users=True, lookup_roles=True, lookup_applications=True
    )
    # make sure the policies are cleaned up
    policies = cleanup_policies(policies)
    created_policies: list[tuple[str, str]] = []
    for policy in policies:
        display_name: str = str(policy.get("displayName"))

        response = policies_api.create_checking_duplicates(policy, f"displayName eq '{display_name}'", duplicate_action)
        response.assert_success(error_message=f"Error creating policy with display name '{display_name}'")
        policy_id = response.json()["id"]
        created_policies.append((policy_id, display_name))
        _logger.info("Policy created successfully with id %s", policy_id)
    return created_policies


def get_groups_in_policies(
    access_token: str,
    policies: list[dict],
    *,
    ignore_not_found: bool = False,
) -> list[dict]:
    """Obtains all groups referenced by the policies in the policies dict.
    If ignore_not_found is True, groups that are not found are ignored.
    Returns a dictionary with the groups."""
    # make sure that all groups are in the key format
    policies = replace_attrs_with_guids_in_policies(
        access_token, policies, lookup_groups=True, lookup_users=False, lookup_roles=False, lookup_applications=False
    )

    groups_found: list[str] = []

    def add_groups(groups: Any | None):
        if groups is not None:
            for group in groups:
                if group not in groups_found:
                    groups_found.append(group)

    for policy in policies:
        conditions: dict = policy["conditions"]
        users: dict = conditions["users"]
        add_groups(users.get("excludeGroups"))
        add_groups(users.get("includeGroups"))
    _logger.debug(f"Groups found in policies: {groups_found}")
    return get_groups_by_ids(access_token, groups_found, ignore_not_found=ignore_not_found)


def delete_policies(access_token: str, policies: list[dict]):
    """Deletes policies that are in the specified list of policies (mandatory fields: id)."""
    _logger.info("Deleting policies...")
    entity_api = PoliciesAPI(access_token=access_token)

    ids = [entity["id"] for entity in policies]

    for entity_id in ids:
        response = entity_api.delete(entity_id)
        if response.status_code == _HTTP_NOT_FOUND:
            _logger.warning(f"Policy with id {entity_id} was not found.")
            continue
        response.assert_success()
        _logger.info(f"Deleting policy with id {entity_id}")
