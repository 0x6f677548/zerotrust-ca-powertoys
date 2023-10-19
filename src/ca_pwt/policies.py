import logging
from .helpers.dict import remove_element_from_dict
from .helpers.graph_api import EntityAPI
from .policies_mappings import values_to_keys

_logger = logging.getLogger(__name__)


class PoliciesAPI(EntityAPI):
    def _get_entity_path(self) -> str:
        return "identity/conditionalAccess/policies"


def _format_policies(policies: dict) -> dict:
    remove_element_from_dict(policies, "@odata.context")

    # check if it is the graph api response format (i.e. a dict with a value key)
    # if so, let's get the value and make sure it is a list
    if (
        "value" in policies
        and policies["value"] is not None
        and isinstance(policies["value"], list)
    ):
        policies = policies["value"]

    # check if we have a single policy. If so, let's wrap it in a list
    elif policies and not isinstance(policies, list):
        policies = [policies]
    elif not policies:
        raise Exception(
            "The policies file is not in the expected format. Please check the documentation."
        )
    return policies


def load_policies(input_file: str) -> dict:
    import json

    with open(input_file, "r") as f:
        _logger.info(f"Reading policies from file {input_file}...")

        policies = json.load(f)
        policies = _format_policies(policies)
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
    policies = _format_policies(policies)
    _logger.debug(f"Formatted policies: {policies}")
    return policies


def import_policies(
    access_token: str,
    policies: dict
) -> list((str, str)):
    policies_api = PoliciesAPI(access_token=access_token)
    policies = values_to_keys(access_token, policies)
    # make sure the policies are cleaned up
    policies = cleanup_policies(policies)
    created_policies = []
    for policy in policies:
        displayName = policy.get("displayName")
        _logger.info(f"Creating policy {displayName}...")
        _logger.debug(f"Policy: {policy}")
        response = policies_api.create(policy)
        response.assert_success()

        id = response.json()["id"]
        created_policies.append((displayName, id))
        _logger.info("Policy created successfully with id %s", id)
    return created_policies
