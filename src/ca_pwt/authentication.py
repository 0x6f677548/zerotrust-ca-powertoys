import logging
from typing import Callable
from msal import PublicClientApplication, ConfidentialClientApplication

_common_tenant_id = "common"
_default_client_id = "14d82eec-204b-4c2f-b7e8-296a70dab67e"  # "Microsoft Graph Command Line Tools"
_default_scopes = ["https://graph.microsoft.com/.default"]

_logger = logging.getLogger(__name__)


def acquire_token(
    tenant_id: str = _common_tenant_id,
    client_id: str = _default_client_id,
    scopes: list[str] = _default_scopes,
    client_secret: str | None = None,
    username: str | None = None,
    password: str | None = None,
    *,
    device_code: bool = False,
) -> str:
    """Acquire an access token using the specified authentication method
    if no authentication method is specified, the interactive method will be used
    Order of precedence:
    1. device_code
    2. client_secret
    3. username/password
    4. interactive
    """
    if device_code:
        import sys

        _logger.debug("Acquiring token using device code flow")
        access_token = acquire_token_by_device_flow(
            sys.stderr.write,
            sys.stderr.flush,
            client_id=client_id,
            tenant_id=tenant_id,
            scopes=scopes,
        )
    elif client_secret:
        _logger.debug("Acquiring token using client secret")
        access_token = acquire_token_by_client_secret(
            client_id=client_id,
            client_secret=client_secret,
            tenant_id=tenant_id,
            scopes=scopes,
        )
    elif username and password:
        _logger.debug("Acquiring token using username/password")
        access_token = acquire_token_by_username_password(
            username=username,
            password=password,
            client_id=client_id,
            tenant_id=tenant_id,
            scopes=scopes,
        )
    else:
        _logger.debug("Acquiring token interactively")
        access_token = acquire_token_interactive(
            client_id=client_id,
            tenant_id=tenant_id,
            scopes=scopes,
        )

    return access_token


def acquire_token_interactive(
    client_id: str = _default_client_id,
    tenant_id: str = _common_tenant_id,
    scopes: list[str] = _default_scopes,
) -> str:
    """Acquire an access token interactively"""
    if not tenant_id:
        tenant_id = _common_tenant_id
    if not scopes:
        scopes = _default_scopes
    if not client_id:
        client_id = _default_client_id

    app = PublicClientApplication(client_id=client_id, authority=f"https://login.microsoftonline.com/{tenant_id}")
    response = app.acquire_token_interactive(scopes=scopes)

    if "error" in response:
        _logger.error(response["error_description"])
        raise Exception(response["error_description"])

    return response["access_token"]


def acquire_token_by_client_secret(
    client_id: str,
    client_secret: str,
    tenant_id: str = _common_tenant_id,
    scopes: list[str] = _default_scopes,
) -> str:
    """Acquire an access token using the client secret"""

    if not tenant_id:
        tenant_id = _common_tenant_id
    if not scopes:
        scopes = _default_scopes

    app = ConfidentialClientApplication(
        client_id=client_id,
        client_credential=client_secret,
        authority=f"https://login.microsoftonline.com/{tenant_id}",
    )

    _logger.debug("Acquiring token for client %s", client_id)
    _logger.debug("Scopes: %s", scopes)
    response = app.acquire_token_for_client(scopes=scopes)

    if "error" in response:
        _logger.error(response["error_description"])
        raise Exception(response["error_description"])

    return response["access_token"]


def acquire_token_by_username_password(
    username: str,
    password: str,
    tenant_id: str,
    client_id: str = _default_client_id,
    scopes: list[str] = _default_scopes,
) -> str:
    """Acquire an access token using the username and password"""
    if not client_id:
        client_id = _default_client_id
    if not scopes:
        scopes = _default_scopes

    app = PublicClientApplication(client_id=client_id, authority=f"https://login.microsoftonline.com/{tenant_id}")
    response = app.acquire_token_by_username_password(username=username, password=password, scopes=scopes)

    if "error" in response:
        _logger.error(response["error_description"])
        raise Exception(response["error_description"])

    return response["access_token"]


def acquire_token_by_device_flow(
    stdout_callback: Callable,
    stdout_flush: Callable,
    client_id: str = _default_client_id,
    tenant_id: str = _common_tenant_id,
    scopes: list[str] = _default_scopes,
) -> str:
    """Acquire an access token using the device flow"""
    import json

    if not client_id:
        client_id = _default_client_id
    if not tenant_id:
        tenant_id = _common_tenant_id
    if not scopes:
        scopes = _default_scopes

    app = PublicClientApplication(client_id=client_id, authority=f"https://login.microsoftonline.com/{tenant_id}")
    flow = app.initiate_device_flow(scopes=scopes)
    if "user_code" not in flow:
        raise ValueError("Fail to create device flow. Err: %s" % json.dumps(flow, indent=4))
    stdout_callback(flow["message"])
    stdout_flush()

    response = app.acquire_token_by_device_flow(flow)

    if "error" in response:
        _logger.error(response["error_description"])
        raise Exception(response["error_description"])

    return response["access_token"]
