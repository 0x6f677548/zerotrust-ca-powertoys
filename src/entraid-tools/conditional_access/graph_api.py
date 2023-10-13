import requests
from helpers.graph_api import get_request_headers, API_Response


def get_policies(access_token: str) -> dict:
    """List all conditional access policies in the tenant"""
    url = "https://graph.microsoft.com/v1.0/identity/conditionalAccess/policies"

    response = API_Response(
        requests.get(url, headers=get_request_headers(access_token)), 200
    )
    return response.json()


def rename_policy(access_token: str, policy_id: str, new_name: str) -> API_Response:
    """Renames a conditional access policy"""
    url = f"https://graph.microsoft.com/v1.0/identity/conditionalAccess/policies/{policy_id}"
    payload = {"displayName": new_name}

    response = API_Response(
        requests.patch(url, headers=get_request_headers(access_token), json=payload),
        204,
    )
    return response


def create_policy(access_token: str, policy: dict) -> API_Response:
    url = "https://graph.microsoft.com/v1.0/identity/conditionalAccess/policies"
    response = API_Response(
        requests.post(url, headers=get_request_headers(access_token), json=policy), 201
    )
    return response
