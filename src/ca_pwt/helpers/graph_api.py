import requests
import logging
import time
from abc import ABC, abstractmethod
from enum import StrEnum
from typing import Any, Callable
from requests.models import Response
from ca_pwt.helpers.utils import assert_condition

_REQUEST_TIMEOUT = 500
_THROTTLING_STATUS_CODE = 429
_THROTTLING_RETRY_AFTER_HEADER = "Retry-After"
_THROTTLING_RETRY_AFTER_DEFAULT = 10
_THROTTLING_MAX_RETRIES = 5

_HTTP_NOT_FOUND = 404


class DuplicateActionEnum(StrEnum):
    IGNORE = "ignore"
    OVERWRITE = "overwrite"
    DUPLICATE = "duplicate"
    FAIL = "fail"


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
        self.response: requests.Response | str | dict[str, Any] = request_response
        self.expected_status_code = expected_status_code
        self.success = self.status_code == self.expected_status_code
        if self._logger.isEnabledFor(logging.DEBUG):
            self._logger.debug(f"Status code: {self.status_code}")
            self._logger.debug(f"Response: {self.response.text}")

    def json(self):
        """Returns the JSON representation of the response"""
        # check if the self.response has a json() method. If so, use it
        if hasattr(self.response, "json") and callable(self.response.json):
            text = self.response.text
            # check if the response is JSON
            if text.startswith("{") and text.endswith("}"):
                return self.response.json()
            else:
                return text
        else:
            return self.response

    def assert_success(self, error_message: str = ""):
        """Asserts that the request was successful
        - error_message: the error message to display if the request was not successful
        """
        assert_condition(
            self.success, f"{error_message}: Request failed with status code {self.status_code}; {self.json()}"
        )

    def __str__(self) -> str:
        """Returns a string representation of the object"""
        response_text = self.response.text if hasattr(self.response, "text") else self.response
        return f"APIResponse: status_code={self.status_code}, success={self.success}, response={response_text}"


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

    def _request_with_throttling_control(self, func: Callable[..., Response], *args, **kwargs) -> Response:
        """Sends a request to the API with throttling control"""
        # set the number of retries to 0
        retries = 0
        # while we have not exceeded the maximum number of retries
        while retries < _THROTTLING_MAX_RETRIES:
            # send the request
            response = func(*args, **kwargs)
            # if the request failed with a throttling error
            if response.status_code == _THROTTLING_STATUS_CODE:
                # get the retry after header
                retry_after_header = response.headers.get(_THROTTLING_RETRY_AFTER_HEADER)
                if retry_after_header is not None:
                    retry_after = int(retry_after_header)
                else:
                    retry_after = _THROTTLING_RETRY_AFTER_DEFAULT
                # log the throttling error
                self._logger.warning(
                    f"Throttling error: {response.status_code}  {response.text}. "
                    f"Retrying in {retry_after} seconds..."
                )
                # wait for the specified number of seconds
                time.sleep(retry_after)
                # increment the number of retries
                retries += 1
            else:
                break
        return response

    def _request_get(self, url: str) -> APIResponse:
        """Sends a GET request to the API"""
        self._logger.debug(f"GET {url}")
        return APIResponse(
            self._request_with_throttling_control(
                requests.get, url, headers=self.request_headers, timeout=_REQUEST_TIMEOUT
            ),
            expected_status_code=200,
        )

    def _request_post(self, url: str, entity: dict) -> APIResponse:
        """Sends a POST request to the API"""
        self._logger.debug(f"POST {url}")
        return APIResponse(
            self._request_with_throttling_control(
                requests.post, url, headers=self.request_headers, json=entity, timeout=_REQUEST_TIMEOUT
            ),
            expected_status_code=201,
        )

    def _request_delete(self, url: str) -> APIResponse:
        """Sends a DELETE request to the API"""
        self._logger.debug(f"DELETE {url}")
        return APIResponse(
            self._request_with_throttling_control(
                requests.delete, url, headers=self.request_headers, timeout=_REQUEST_TIMEOUT
            ),
            expected_status_code=204,
        )

    def _request_patch(self, url: str, entity: dict) -> APIResponse:
        """Sends a PATCH request to the API"""
        self._logger.debug(f"PATCH {url}")
        return APIResponse(
            self._request_with_throttling_control(
                requests.patch, url, headers=self.request_headers, json=entity, timeout=_REQUEST_TIMEOUT
            ),
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
        return self.get_top_entity(f"displayName eq '{display_name}'")

    def get_top_entity(self, odata_filter: str, *, 
                       use_top: bool = True) -> APIResponse:
        """Gets the top entity found with the given filter
        Returns an API_Response object and the entity is in the json property of the API_Response object
        If use_top is True, the $top query parameter is used to get only the top entity, otherwise all entities are
        returned and the first one is returned
        """

        assert_condition(odata_filter, "odata_filter cannot be None")
        response = self.get_all(odata_filter=odata_filter, odata_top=1 if use_top else None)
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

    def create_checking_duplicates(
        self, entity: dict, odata_filter: str, duplicate_action: DuplicateActionEnum = DuplicateActionEnum.IGNORE
    ) -> APIResponse:
        """Creates an entity checking for duplicates first and taking the specified action if a duplicate is found
        A duplicate is determined by the odata_filter parameter, getting the top entity with the specified filter"""
        assert_condition(entity, "entity cannot be None")
        assert_condition(odata_filter, "odata_filter cannot be None")

        # if duplicate_action is not duplicate, check if the entity already exists
        if duplicate_action != DuplicateActionEnum.DUPLICATE:
            existing_entity = self.get_top_entity(odata_filter)
            if existing_entity.success:
                if duplicate_action == DuplicateActionEnum.IGNORE:
                    self._logger.warning(
                        f"Entity {self._get_entity_path()} with filter {odata_filter} already exists. Skipping..."
                    )
                    return existing_entity
                elif duplicate_action == DuplicateActionEnum.OVERWRITE:
                    existing_entity_id = existing_entity.json()["id"]
                    self._logger.warning(
                        f"Overwriting entity {self._get_entity_path()} with id {existing_entity_id}..."
                    )
                    response = self.update(existing_entity_id, entity)
                    response.assert_success()
                    # response should be a "204 No Content" or "200 OK" response
                    # we need to return the existing_entity_id in the response body
                    response.response = {"id": existing_entity_id}
                    return response
                elif duplicate_action == DuplicateActionEnum.FAIL:
                    msg = f"Entity {self._get_entity_path()} with filter {odata_filter} already exists."
                    raise ValueError(msg)
                else:
                    msg = f"Invalid duplicate_action: {duplicate_action}"
                    raise ValueError(msg)
        return self.create(entity)

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
