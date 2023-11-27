import os
import json
from src.ca_pwt.helpers.graph_api import EntityAPI
import copy
from src.ca_pwt.policies import PoliciesAPI
from src.ca_pwt.groups import GroupsAPI

# in case of rate limit errors, increase this value to 5 or more.
# This will slow down the tests but will avoid rate limit errors
SLEEP_BETWEEN_TESTS = 0


def assert_valid_output_file(output_file):
    # check if file exists
    assert os.path.isfile(output_file)
    # check if file is not empty
    assert os.stat(output_file).st_size != 0

    # open file and check if it is valid json

    with open(output_file) as f:
        data = json.load(f)
        assert data

        # check if file contains the expected data
        # check if value is a single policy or is a list with a policy

        assert "displayName" in data or (
            isinstance(data, list) and len(data) > 0 and "displayName" in data[0]
        ), "The output file does not contain the expected data"


def _remove_entities(entity_api: EntityAPI, display_names: list[str]):
    for display_name in display_names:
        get_entities_response = entity_api.get_all(f"displayName eq '{display_name}'")
        assert get_entities_response is not None
        entities = get_entities_response.json()["value"]
        assert entities is not None
        for entity in entities:
            entity_api.delete(entity["id"])


_VALID_GROUPS: list[dict] = [
    {
        "id": "88ef8435-6ab4-42c5-8e8d-e5dc2d1d66a1",
        "createdDateTime": "2023-08-17T23:13:20.9225868Z",
        "modifiedDateTime": "2023-10-10T13:35:17.0858965Z",
        "description": "UNIT-TEST-GROUP-PLEASE-IGNORE-1",
        "displayName": "UNIT-TEST-GROUP-PLEASE-IGNORE-1",
        "mailEnabled": False,
        "mailNickname": "UNIT-TEST-GROUP-PLEASE-IGNORE-1",
        "securityEnabled": True,
    },
    {
        "id": "88ef8435-6ab4-42c5-8e8d-e5dc2d1d66a2",
        "createdDateTime": "2023-08-17T23:13:20.9225868Z",
        "modifiedDateTime": "2023-10-10T13:35:17.0858965Z",
        "description": "UNIT-TEST-GROUP-PLEASE-IGNORE-2",
        "displayName": "UNIT-TEST-GROUP-PLEASE-IGNORE-2",
        "mailEnabled": True,
        "mailNickname": "UNIT-TEST-GROUP-PLEASE-IGNORE-2",
        "securityEnabled": True,
    },
]

# flake8: noqa: E501
_VALID_POLICIES: list[dict] = [
    {
        "id": "88ef8435-6ab4-42c5-8e8d-e5dc2d1d66a9",
        "displayName": "UNIT-TEST-CA-POLICY-PLEASE-IGNORE",
        "createdDateTime": "2023-08-17T23:13:20.9225868Z",
        "modifiedDateTime": "2023-10-10T13:35:17.0858965Z",
        "state": "disabled",
        "conditions": {
            "userRiskLevels": [],
            "signInRiskLevels": [],
            "clientAppTypes": ["all"],
            "servicePrincipalRiskLevels": [],
            "applications": {
                "includeApplications": ["All"],
                "excludeApplications": ["d4ebce55-015a-49b5-a083-c84d1797ae8c"],
                "includeUserActions": [],
                "includeAuthenticationContextClassReferences": [],
            },
            "users": {
                "includeRoles": ["9b895d92-2cd3-44c7-9d02-a6ac2d5ea5c3"],
                "excludeRoles": ["ffd52fa5-98dc-465c-991d-fc073eb59f8f"],
                "excludeUsers": ["084f9c81-52d2-4f55-b328-1a8d03697ebe"],
                "includeUsers": ["9ea4c2d7-c87a-4cb9-b04f-75e7cfcff039"],
                "includeGroupNames": ["UNIT-TEST-GROUP-PLEASE-IGNORE-1"],
                "excludeGroupNames": ["UNIT-TEST-GROUP-PLEASE-IGNORE-2"],
                "excludeGroups": ["00000000-0000-0000-0000-000000000000"],
            },
            "platforms": {"includePlatforms": ["all"], "excludePlatforms": []},
        },
        "grantControls": {
            "operator": "OR",
            "builtInControls": ["block"],
            "customAuthenticationFactors": [],
            "termsOfUse": [],
            "authenticationStrength@odata.context": "https://graph.microsoft.com/v1.0/$metadata#identity/conditionalAccess/policies('88ef8435-6ab4-42c5-8e8d-e5dc2d1d66a9')/grantControls/authenticationStrength/$entity",
        },
    }
]


_INVALID_POLICIES: list[dict] = [
    {
        "displayNames": "ca-test",
        "conditions": {
            "users": {
                "includeUsers": [],
                "excludeUsers": [],
                "includeGroups": [],
                "excludeGroups": [],
                "includeRoles": [],
                "excludeRoles": [],
            }
        },
        "grantControls": {},
    }
]

_INVALID_GROUPS: list[dict] = [
    {
        "description": "",
        "displayName": "",
        "mailEnabled": False,
        "mailNickname": "",
        "securityEnabled": True,
    }
]


def import_test_groups(access_token: str) -> list[tuple[str, str]]:
    from src.ca_pwt.groups import import_groups

    return import_groups(access_token, get_valid_groups())


def import_test_policies(access_token: str) -> list[tuple[str, str]]:
    from src.ca_pwt.policies import import_policies

    return import_policies(access_token, get_valid_policies())


def delete_test_policies(access_token: str):
    """Deletes test policies from the target tenant"""
    policies_api = PoliciesAPI(access_token=access_token)
    _remove_entities(policies_api, [policy["displayName"] for policy in get_valid_policies()])


def delete_test_groups(access_token: str):
    """Deletes test groups from the target tenant"""
    groups_api = GroupsAPI(access_token=access_token)
    _remove_entities(groups_api, [group["displayName"] for group in get_valid_groups()])


def get_valid_policies() -> list[dict]:
    """Returns a copy of the VALID_POLICIES list"""
    return copy.deepcopy(_VALID_POLICIES)


def get_valid_groups() -> list[dict]:
    """Returns a copy of the VALID_GROUPS list"""
    return copy.deepcopy(_VALID_GROUPS)


def get_invalid_policies() -> list[dict]:
    """Returns a copy of the INVALID_POLICIES list"""
    return copy.deepcopy(_INVALID_POLICIES)


def get_invalid_groups() -> list[dict]:
    """Returns a copy of the INVALID_GROUPS list"""
    return copy.deepcopy(_INVALID_GROUPS)
