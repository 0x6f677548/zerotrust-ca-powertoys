from pytest import fixture


def pytest_addoption(parser):
    parser.addoption("--tenant_id", action="store")
    parser.addoption("--client_id", action="store")
    parser.addoption("--client_secret", action="store")
    parser.addoption("--username", action="store")
    parser.addoption("--password", action="store")
    parser.addoption("--scopes", action="store")



@fixture()
def access_token(request):
    from src.entraid_tools.authentication.auth_lib import (
        acquire_token_by_client_secret,
        acquire_token_by_username_password,
        acquire_token_interactive,
    )

    tenant_id = request.config.getoption("--tenant_id")
    client_id = request.config.getoption("--client_id")
    client_secret = request.config.getoption("--client_secret")
    username = request.config.getoption("--username")
    password = request.config.getoption("--password")
    scopes = request.config.getoption("--scopes")

    if client_secret:
        access_token = acquire_token_by_client_secret(
            client_id=client_id,
            client_secret=client_secret,
            tenant_id=tenant_id,
            scopes=scopes,
        )
    elif username and password:
        access_token = acquire_token_by_username_password(
            username=username,
            password=password,
            client_id=client_id,
            tenant_id=tenant_id,
            scopes=scopes,
        )
    else:
        access_token = acquire_token_interactive(
            client_id=client_id,
            tenant_id=tenant_id,
            scopes=scopes,
        )
    return access_token
