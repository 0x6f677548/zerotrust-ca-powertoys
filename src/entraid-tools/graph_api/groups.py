import requests
from graph_api.api_requests import get_request_headers, API_Response


def add_user_to_group(access_token: str, user_id: str, group_id: str) -> API_Response:
    """Adds a user to a group
    Returns an API_Response object
    To check if the request was successful, use the success property of the API_Response object
    """
    add_user_url = f"https://graph.microsoft.com/v1.0/groups/{group_id}/members/$ref"

    # Define the payload to add user to group
    payload = {
        "@odata.id": f"https://graph.microsoft.com/v1.0/directoryObjects/{user_id}"
    }

    # Make the request to add user to group
    return API_Response(
        requests.post(
            add_user_url, headers=get_request_headers(access_token), json=payload
        ), 204
    )


def get_group_name_by_id(access_token: str, group_id: str) -> str:
    """Gets the name of a group by its ID
    Returns None if the group is not found
    """
    url = f"https://graph.microsoft.com/v1.0/groups/{group_id}"

    response = API_Response(requests.get(url, headers=get_request_headers(access_token)), expected_status_code=200)
    if response.success:
        group = response.json()
        return group["displayName"]
    else:
        return None


def get_group_id_by_name(access_token: str, group_name: str) -> str:
    """Gets the ID of a group by its name
    Returns None if the group is not found
    """
    url = (
        f"https://graph.microsoft.com/v1.0/groups?$filter=displayName eq '{group_name}'"
    )

    response = API_Response(requests.get(url, headers=get_request_headers(access_token)), 200)
    if response.success:
        groups = response.json()["value"]
        if len(groups) == 0:
            return None
        else:
            return groups[0]["id"]
    else:
        return None
