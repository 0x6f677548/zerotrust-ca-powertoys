import requests


def get_request_headers(token: str) -> dict:
    """Returns the headers for a request to the Microsoft Graph API"""
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


class API_Response:
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
