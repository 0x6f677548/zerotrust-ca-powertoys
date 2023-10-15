import requests
from abc import ABC, abstractmethod


class APIResponse:
    """A class to represent an API response"""

    def __init__(
        self, request_response: requests.Response, expected_status_code: int = 200
    ):
        """Creates an API_Response object
        - request_response: the response from the API request
        - expected_status_code: the expected status code for the request
        if the status code of the response matches the expected status code,
        the success property will be set to True
        """
        self.status_code = request_response.status_code
        self.response = request_response
        self.expected_status_code = expected_status_code
        self.success = self.status_code == self.expected_status_code

    def json(self):
        """Returns the JSON representation of the response"""
        return self.response.json()


class EntityAPI(ABC):
    """An abstract class to represent an entity in the Microsoft Graph API"""

    def __init__(self, access_token: str):
        """Creates an EntityAPI object
        - access_token: the access token to use for requests to the API
        """
        self.entity_url = f"https://graph.microsoft.com/v1.0/{self._get_entity_path()}"
        self.access_token = access_token
        self.request_headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    @abstractmethod
    def _get_entity_path(self) -> str:
        """Returns the path to the entity in the Microsoft Graph API"""
        pass

    def get_all(
        self,
        odata_filter: str | None = None,
        odata_top: int | None = None,
    ) -> APIResponse:
        """Returns all entities in the API"""
        url = f"{self.entity_url}?"

        if odata_filter:
            url += f"$filter={odata_filter}&"

        if odata_top:
            url += f"$top={odata_top}&"

        # remove the last character if it is a & or ?
        # this is here for future use if we add more query parameters
        if url[-1] in ["&", "?"]:
            url = url[:-1]

        response = APIResponse(requests.get(url, headers=self.request_headers), 200)
        return response

    def get_by_id(self, entity_id: str) -> APIResponse:
        """Returns an entity by its ID
        Entity is returned as a JSON object in the response (response.json())"""
        url = f"{self.entity_url}/{entity_id}"

        return APIResponse(
            requests.get(url, headers=self.request_headers), expected_status_code=200
        )

    def create(self, entity: dict) -> APIResponse:
        """Creates an entity"""
        return APIResponse(
            requests.post(self.entity_url, headers=self.request_headers, json=entity),
            201,
        )

    def delete(self, entity_id: str) -> APIResponse:
        """Deletes an entity by its ID"""
        url = f"{self.entity_url}/{entity_id}"
        return APIResponse(
            requests.delete(url, headers=self.request_headers), expected_status_code=204
        )

    def update(self, entity_id: str, entity: dict) -> APIResponse:
        """Updates an entity by its ID"""
        url = f"{self.entity_url}/{entity_id}"
        return APIResponse(
            requests.patch(url, headers=self.request_headers, json=entity),
            expected_status_code=204,
        )
