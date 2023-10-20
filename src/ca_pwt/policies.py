import logging
from .helpers.dict import remove_element_from_dict, cleanup_odata_dict
from .helpers.graph_api import EntityAPI
from .policies_mappings import values_to_keys
from .groups import get_groups_by_ids

_logger = logging.getLogger(__name__)


class PoliciesAPI(EntityAPI):
    def _get_entity_path(self) -> str:
        return "identity/conditionalAccess/policies"


def load_policies(input_file: str) -> dict:
    import json

    with open(input_file, "r") as f:
        _logger.info(f"Reading policies from file {input_file}...")

        policies = json.load(f)
        policies = cleanup_odata_dict(policies, ensure_list=True)
        return policies


def save_policies(policies: dict, output_file: str):
    import json

    with open(output_file, "w") as f:
        _logger.info(f"Writing policies to file {output_file}...")
        f.write(json.dumps(policies, indent=4))


def cleanup_policies(source: dict) -> dict:
    _logger.info("Cleaning up policies...")

    # exclude some elements, namely createdDateTime,
    # modifiedDateTime, id, templateId, authenticationStrength@odata.context
    for policy in source:
        remove_element_from_dict(policy, "createdDateTime")
        remove_element_from_dict(policy, "modifiedDateTime")
        remove_element_from_dict(policy, "id")
        remove_element_from_dict(policy, "templateId")
        grant_controls = policy["grantControls"]
        if grant_controls is not None:
            remove_element_from_dict(
                grant_controls, "authenticationStrength@odata.context"
            )
    return source


def export_policies(access_token: str, filter: str | None = None) -> dict:
    policies_api = PoliciesAPI(access_token=access_token)
    response = policies_api.get_all(odata_filter=filter)
    response.assert_success()
    policies = response.json()

    _logger.debug(f"Obtained policies: {policies}")
    policies = cleanup_odata_dict(policies, ensure_list=True)
    _logger.debug(f"Formatted policies: {policies}")
    return policies


def import_policies(
    access_token: str,
    policies: dict,
    allow_duplicates: bool = False,
) -> list[(str, str)]:
    policies_api = PoliciesAPI(access_token=access_token)
    policies = values_to_keys(access_token, policies)
    # make sure the policies are cleaned up
    policies = cleanup_policies(policies)
    created_policies = []
    for policy in policies:
        displayName = policy.get("displayName")

        # check if the policy already exists
        if not allow_duplicates:
            existing_policy = policies_api.get_by_display_name(displayName)
            if existing_policy.success:
                _logger.warning(
                    f"Policy with display name {displayName} already exists. Skipping..."
                )
                continue

        _logger.info(f"Creating policy {displayName}...")
        _logger.debug(f"Policy: {policy}")
        response = policies_api.create(policy)
        response.assert_success()

        id = response.json()["id"]
        created_policies.append((displayName, id))
        _logger.info("Policy created successfully with id %s", id)
    return created_policies


def get_groups_in_policies(
    access_token: str,
    policies: dict,
    ignore_not_found: bool = False,
) -> dict:
    """Obtains all groups referenced by the policies in the policies dict.
    If ignore_not_found is True, groups that are not found are ignored.
    Returns a dictionary with the groups."""
    # make sure that all groups are in the key format
    policies = values_to_keys(
        access_token,
        policies,
        lookup_groups=True,
        lookup_users=False,
        lookup_roles=False,
    )

    groups_found: list[str] = []
    for policy in policies:
        conditions: dict = policy["conditions"]
        users: dict = conditions["users"]
        exclude_groups = users.get("excludeGroups")
        if exclude_groups is not None:
            for group in exclude_groups:
                if group not in groups_found:
                    groups_found.append(group)
        include_groups = users.get("includeGroups")
        if include_groups is not None:
            for group in include_groups:
                if group not in groups_found:
                    groups_found.append(group)
    _logger.debug(f"Groups found in policies: {groups_found}")
    return get_groups_by_ids(access_token, groups_found, ignore_not_found)
