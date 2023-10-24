import requests
from ca_pwt.helpers.utils import assert_condition
from abc import ABC, abstractmethod
import logging

_REQUEST_TIMEOUT = 500


class APIResponse:
    """A class to represent an API response"""

    _logger = logging.getLogger(__name__)

    def __init__(self, request_response: requests.Response, expected_status_code: int = 200):
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
        if self._logger.isEnabledFor(logging.DEBUG):
            self._logger.debug(f"Status code: {self.status_code}")
            self._logger.debug(f"Response: {self.response.text}")

    def json(self):
        """Returns the JSON representation of the response"""
        # check if the self.response has a json() method. If so, use it
        if hasattr(self.response, "json"):
            return self.response.json()
        else:
            return self.response

    def assert_success(self):
        """Asserts that the request was successful"""
        assert_condition(self.success, f"Request failed with status code {self.status_code}; {self.response.json()}")


class EntityAPI(ABC):
    """An abstract class to represent an entity in the Microsoft Graph API"""

    _logger = logging.getLogger(__name__)

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

    def _request_get(self, url: str) -> APIResponse:
        """Sends a GET request to the API"""
        self._logger.debug(f"GET {url}")
        return APIResponse(
            requests.get(url, headers=self.request_headers, timeout=_REQUEST_TIMEOUT), expected_status_code=200
        )

    def _request_post(self, url: str, entity: dict) -> APIResponse:
        """Sends a POST request to the API"""
        self._logger.debug(f"POST {url}")
        return APIResponse(requests.post(url, headers=self.request_headers, json=entity, timeout=_REQUEST_TIMEOUT), 201)

    def _request_delete(self, url: str) -> APIResponse:
        """Sends a DELETE request to the API"""
        self._logger.debug(f"DELETE {url}")
        return APIResponse(
            requests.delete(url, headers=self.request_headers, timeout=_REQUEST_TIMEOUT), expected_status_code=204
        )

    def _request_patch(self, url: str, entity: dict) -> APIResponse:
        """Sends a PATCH request to the API"""
        self._logger.debug(f"PATCH {url}")
        return APIResponse(
            requests.patch(url, headers=self.request_headers, json=entity, timeout=_REQUEST_TIMEOUT),
            expected_status_code=204,
        )

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

        return self._request_get(url)

    def get_by_id(self, entity_id: str) -> APIResponse:
        """Returns an entity by its ID
        Entity is returned as a JSON object in the response (response.json())"""
        assert_condition(entity_id, "entity_id cannot be None")
        url = f"{self.entity_url}/{entity_id}"
        return self._request_get(url)

    def get_by_display_name(self, display_name: str) -> APIResponse:
        """Gets the top entity found with the given display name
        Returns an API_Response object and the entity is in the json property of the API_Response object
        """
        assert_condition(display_name, "display_name cannot be None")

        response = self.get_all(odata_filter=f"displayName eq '{display_name}'", odata_top=1)

        # if the request was successful, transform the response to a dict
        if response.success:
            # move the value property to the response property
            value = response.json()["value"]
            # check if we have results
            if value == []:
                response.success = False
                response.status_code = 404
                response.response = "No results found"
            else:
                response.response = value[0]

        return response

    def create(self, entity: dict) -> APIResponse:
        """Creates an entity"""
        assert_condition(entity, "entity cannot be None")
        return self._request_post(self.entity_url, entity)

    def delete(self, entity_id: str) -> APIResponse:
        """Deletes an entity by its ID"""
        assert_condition(entity_id, "entity_id cannot be None")
        url = f"{self.entity_url}/{entity_id}"
        return self._request_delete(url)

    def update(self, entity_id: str, entity: dict) -> APIResponse:
        """Updates an entity by its ID"""
        assert_condition(entity_id, "entity_id cannot be None")
        assert_condition(entity, "entity cannot be None")
        url = f"{self.entity_url}/{entity_id}"
        return self._request_patch(url, entity)
