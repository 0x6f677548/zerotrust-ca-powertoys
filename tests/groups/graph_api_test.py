from src.entraid_tools.groups.graph_api import GroupsAPI
import pytest


def test_get_by_id(access_token):
    groups = GroupsAPI(access_token=access_token)
    group0 = groups.get_all().json()["value"][0]

    group0_id = group0["id"]
    group0_name = group0["displayName"]
    assert groups.get_by_id(group0_id).json()["displayName"] == group0_name


def test_get_by_display_name(access_token):
    groups = GroupsAPI(access_token=access_token)
    group0 = groups.get_all(odata_top=1).json()["value"][0]

    group0_id = group0["id"]
    group0_name = group0["displayName"]
    response = groups.get_by_display_name(group0_name)
    assert response.success
    assert response.json()["displayName"] == group0_name
    assert response.json()["id"] == group0_id


def test_get_by_display_name_invalid(access_token):
    groups = GroupsAPI(access_token=access_token)

    # use a guid as display name
    response = groups.get_by_display_name("00000000-0000-0000-0000-000000000000")
    assert not response.success


def test_create(access_token):
    groups = GroupsAPI(access_token=access_token)

    group = {
        "description": "test_group_description",
        "displayName": "test_group",
        "groupTypes": ["Unified"],
        "mailEnabled": False,
        "mailNickname": "library",
        "securityEnabled": True,
    }
    response = groups.create(group)
    if not response.success:
        pytest.fail(response.json()["error"]["message"])
    created_group = response.json()
    assert group["displayName"] == created_group["displayName"]
    assert group["description"] == created_group["description"]

    # Clean up
    groups.delete(created_group["id"])
