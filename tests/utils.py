import os
import json

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

        assert "displayName" in data or (isinstance(data, list) and len(data) > 0 and "displayName" in data[0])


VALID_GROUPS: list[dict] = [
    {
        "id": "88ef8435-6ab4-42c5-8e8d-e5dc2d1d66a1",
        "createdDateTime": "2023-08-17T23:13:20.9225868Z",
        "modifiedDateTime": "2023-10-10T13:35:17.0858965Z",
        "description": "UNIT-TEST-GROUP-PLEASE-IGNORE",
        "displayName": "UNIT-TEST-GROUP-PLEASE-IGNORE",
        "mailEnabled": False,
        "mailNickname": "UNIT-TEST-GROUP-PLEASE-IGNORE",
        "securityEnabled": True,
    }
]

# flake8: noqa: E501
VALID_POLICIES: list[dict] = [
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
                "excludeApplications": [],
                "includeUserActions": [],
                "includeAuthenticationContextClassReferences": [],
            },
            "users": {
                "includeRoles": ["9b895d92-2cd3-44c7-9d02-a6ac2d5ea5c3"],
                "excludeRoles": ["ffd52fa5-98dc-465c-991d-fc073eb59f8f"],
                "excludeUsers": ["084f9c81-52d2-4f55-b328-1a8d03697ebe"],
                "includeUsers": [
                    "9ea4c2d7-c87a-4cb9-b04f-75e7cfcff039",
                ],
                "includeGroups": [
                    "9ae4a47f-c5e0-4d45-9948-8122a9b4e223",
                ],
                "excludeGroups": ["47eec19a-ec26-4e26-9924-a538d2c33e9d", "00000000-0000-0000-0000-000000000000"],
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

INVALID_POLICIES: list[dict] = [
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

INVALID_GROUPS: list[dict] = [
    {
        "description": "",
        "displayName": "",
        "mailEnabled": False,
        "mailNickname": "",
        "securityEnabled": True,
    }
]
