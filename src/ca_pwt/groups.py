import requests
import logging
from .helpers.graph_api import APIResponse, EntityAPI
from .helpers.dict import cleanup_odata_dict, remove_element_from_dict

_logger = logging.getLogger(__name__)


class GroupsAPI(EntityAPI):
    def _get_entity_path(self) -> str:
        return "groups"

    def add_user_to_group(self, user_id: str, group_id: str) -> APIResponse:
        """Adds a user to a group
        Returns an API_Response object
        To check if the request was successful, use the success property of the API_Response object
        """
        add_user_url = (
            f"https://graph.microsoft.com/v1.0/groups/{group_id}/members/$ref"
        )

        # Define the payload to add user to group
        payload = {
            "@odata.id": f"https://graph.microsoft.com/v1.0/directoryObjects/{user_id}"
        }

        # Make the request to add user to group
        return APIResponse(
            requests.post(add_user_url, headers=self.request_headers, json=payload), 204
        )


def load_groups(input_file: str) -> dict:
    """Loads groups from the specified file.
    It also cleans up the dictionary to remove unnecessary elements."""
    import json

    with open(input_file, "r") as f:
        _logger.info(f"Reading groups from file {input_file}...")

        groups = json.load(f)
        return cleanup_odata_dict(groups, ensure_list=True)


def save_groups(groups: dict, output_file: str):
    """Saves groups to the specified file."""
    import json

    with open(output_file, "w") as f:
        _logger.info(f"Writing groups to file {output_file}...")
        f.write(json.dumps(groups, indent=4))


def cleanup_groups(source: dict) -> dict:
    """Cleans up the groups dictionary for import by
    removing disallowed elements while importing. (e.g. id, createdDateTime,
    modifiedDateTime, templateId, deletedDateTime, renewedDateTime)"""
    _logger.info("Cleaning up groups...")

    # exclude some elements, namely createdDateTime,
    # modifiedDateTime, id, templateId, authenticationStrength@odata.context
    for group in source:
        remove_element_from_dict(group, "createdDateTime")
        remove_element_from_dict(group, "modifiedDateTime")
        remove_element_from_dict(group, "id")
        remove_element_from_dict(group, "templateId")
        remove_element_from_dict(group, "deletedDateTime")
        remove_element_from_dict(group, "renewedDateTime")

        # remove all null elements or empty lists
        for key in list(group.keys()):
            if group[key] is None or group[key] == []:
                group.pop(key)

    return source


def get_groups_by_ids(
    access_token: str, group_ids: list[str], ignore_not_found: bool = True
) -> dict:
    """Exports groups with the specified ids."""
    assert group_ids is not None
    _logger.info("Getting groups by ids...")
    _logger.debug(f"Ignoring not found groups: {ignore_not_found}")

    result: list[dict] = []
    groups_api = GroupsAPI(access_token=access_token)
    for group_id in group_ids:
        group_response = groups_api.get_by_id(group_id)
        if group_response.status_code == 404 and ignore_not_found:
            _logger.warning(f"Group with id {group_id} was not found.")
            continue
        else:
            group_response.assert_success()
        group_detail = group_response.json()
        group_detail = cleanup_odata_dict(group_detail, ensure_list=False)
        result.append(group_detail)
    return result


def import_groups(
    access_token: str, groups: dict, allow_duplicates: bool = False
) -> list[tuple[str, str]]:
    """Imports groups from the specified dictionary.
    Returns a list of tuples with the group id and name of the imported groups.
    """
    _logger.info("Importing groups...")
    groups_api = GroupsAPI(access_token=access_token)
    result: list[tuple[str, str]] = []
    for group in groups:
        group_name = group["displayName"]

        if not allow_duplicates:
            existing_group = groups_api.get_by_display_name(group_name)
            if existing_group.success:
                _logger.warning(
                    f"Group with display name {group_name} already exists. Skipping..."
                )
                continue

        group_response = groups_api.create(group)
        group_response.assert_success()
        group_detail = group_response.json()
        group_id = group_detail["id"]
        result.append((group_id, group_name))
        _logger.info(f"Imported group {group_name} with id {group_id}")
    return result
