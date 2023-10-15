from src.entraid_tools.groups.graph_api import GroupsAPI
import pytest


class TestGroups:
    def test_get_by_id(self, access_token):
        groups = GroupsAPI(access_token=access_token)
        group0 = groups.get_all().json()["value"][0]

        group0_id = group0["id"]
        group0_name = group0["displayName"]
        assert groups.get_by_id(group0_id).json()["displayName"] == group0_name

    def test_get_by_name(self, access_token):
        groups = GroupsAPI(access_token=access_token)
        group0 = groups.get_all().json()["value"][0]

        group0_id = group0["id"]
        group0_name = group0["displayName"]
        results = groups.get_by_name(group0_name).json()["value"]
        assert results[0]["id"] == group0_id

    def test_create(self, access_token):
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


