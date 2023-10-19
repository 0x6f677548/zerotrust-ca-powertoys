import requests
from ..helpers.graph_api import APIResponse, EntityAPI


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
