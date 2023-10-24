from pytest import fixture


def pytest_addoption(parser):
    parser.addoption("--tenant_id", action="store")
    parser.addoption("--client_id", action="store")
    parser.addoption("--client_secret", action="store")
    parser.addoption("--username", action="store")
    parser.addoption("--password", action="store")
    parser.addoption("--scopes", action="store")
    parser.addoption("--access_token", action="store")


@fixture()
def access_token(request):
    from src.ca_pwt.authentication import (
        acquire_token_by_client_secret,
        acquire_token_by_username_password,
        acquire_token_interactive,
    )

    access_token = request.config.getoption("--access_token")

    tenant_id = request.config.getoption("--tenant_id")
    client_id = request.config.getoption("--client_id")
    client_secret = request.config.getoption("--client_secret")
    username = request.config.getoption("--username")
    password = request.config.getoption("--password")
    scopes = request.config.getoption("--scopes")

    if access_token:
        return access_token
    elif client_secret:
        return acquire_token_by_client_secret(
            client_id=client_id,
            client_secret=client_secret,
            tenant_id=tenant_id,
            scopes=scopes,
        )
    elif username and password:
        return acquire_token_by_username_password(
            username=username,
            password=password,
            client_id=client_id,
            tenant_id=tenant_id,
            scopes=scopes,
        )
    else:
        return acquire_token_interactive(
            client_id=client_id,
            tenant_id=tenant_id,
            scopes=scopes,
        )
