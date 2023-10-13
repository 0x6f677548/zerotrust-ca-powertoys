import logging
from msal import PublicClientApplication, ConfidentialClientApplication

COMMON_TENANT_ID = "common"
DEFAULT_CLIENT_ID = "14d82eec-204b-4c2f-b7e8-296a70dab67e"
DEFAULT_SCOPES = ["https://graph.microsoft.com/.default"]

_logger = logging.getLogger(__name__)


def _replace_with_default_if_none(
    value: str | list[str] | None, default: str | list[str]
) -> str:
    if value is None:
        return default
    return value


def acquire_token_interactive(
    client_id: str = DEFAULT_CLIENT_ID,
    tenant_id: str = COMMON_TENANT_ID,
    scopes: list[str] = DEFAULT_SCOPES,
) -> str:
    client_id = _replace_with_default_if_none(client_id, DEFAULT_CLIENT_ID)
    tenant_id = _replace_with_default_if_none(tenant_id, COMMON_TENANT_ID)
    scopes = _replace_with_default_if_none(scopes, DEFAULT_SCOPES)

    # dump all the parameters
    print(f"tenant_id: {tenant_id}")
    print(f"client_id: {client_id}")
    print(f"scopes: {scopes}")

    app = PublicClientApplication(
        client_id=client_id, authority=f"https://login.microsoftonline.com/{tenant_id}"
    )
    response = app.acquire_token_interactive(scopes=scopes)

    if "error" in response:
        _logger.error(response["error_description"])
        raise Exception(response["error_description"])

    return response["access_token"]


def acquire_token_by_client_secret(
    client_id: str,
    client_secret: str,
    tenant_id: str = COMMON_TENANT_ID,
    scopes: list[str] = DEFAULT_SCOPES,
) -> str:
    tenant_id = _replace_with_default_if_none(tenant_id, COMMON_TENANT_ID)
    scopes = _replace_with_default_if_none(scopes, DEFAULT_SCOPES)

    app = ConfidentialClientApplication(
        client_id=client_id,
        client_credential=client_secret,
        authority=f"https://login.microsoftonline.com/{tenant_id}",
    )

    response = app.acquire_token_for_client(scopes=scopes)

    if "error" in response:
        _logger.error(response["error_description"])
        raise Exception(response["error_description"])

    return response["access_token"]


def acquire_token_by_username_password(
    username: str,
    password: str,
    tenant_id: str,
    client_id: str = DEFAULT_CLIENT_ID,
    scopes: list[str] = DEFAULT_SCOPES,
) -> str:
    client_id = _replace_with_default_if_none(client_id, DEFAULT_CLIENT_ID)
    scopes = _replace_with_default_if_none(scopes, DEFAULT_SCOPES)

    app = PublicClientApplication(
        client_id=client_id, authority=f"https://login.microsoftonline.com/{tenant_id}"
    )
    response = app.acquire_token_by_username_password(
        username=username, password=password, scopes=scopes
    )

    if "error" in response:
        _logger.error(response["error_description"])
        raise Exception(response["error_description"])

    return response["access_token"]


def acquire_token_by_device_flow(
    stdout_callback: callable,
    stdout_flush: callable,
    client_id: str = DEFAULT_CLIENT_ID,
    tenant_id: str = COMMON_TENANT_ID,
    scopes: list[str] = DEFAULT_SCOPES,
) -> str:
    import json

    client_id = _replace_with_default_if_none(client_id, DEFAULT_CLIENT_ID)
    tenant_id = _replace_with_default_if_none(tenant_id, COMMON_TENANT_ID)
    scopes = _replace_with_default_if_none(scopes, DEFAULT_SCOPES)

    app = PublicClientApplication(
        client_id=client_id, authority=f"https://login.microsoftonline.com/{tenant_id}"
    )
    flow = app.initiate_device_flow(scopes=scopes)
    if "user_code" not in flow:
        raise ValueError(
            "Fail to create device flow. Err: %s" % json.dumps(flow, indent=4)
        )
    stdout_callback(flow["message"])
    stdout_flush()

    response = app.acquire_token_by_device_flow(flow)

    if "error" in response:
        _logger.error(response["error_description"])
        raise Exception(response["error_description"])

    return response["access_token"]
