import click
import logging
from graph_api.authentication import (
    acquire_token_by_device_flow,
    acquire_token_by_client_secret,
    acquire_token_by_username_password,
    acquire_token_interactive,
)


CLIENT_ID_OPTION = click.option(
    "--client_id",
    prompt="Your client ID",
    prompt_required=False,
    help="The client ID of this Azure AD app "
    + "(leave blank if you want to use Graph Command Line Tools)",
)
TENANT_ID_OPTION = click.option(
    "--tenant_id",
    prompt="Your tenant ID",
    prompt_required=False,
    help="The tenant ID (leave blank if you want to use the default tenant of your user)",
)
CLIENT_SECRET_OPTION = click.option(
    "--client_secret",
    prompt="Your client secret",
    prompt_required=False,
    help="The client secret of your Azure AD app "
    + "(leave blank if you want to use delegated permissions with a user account)",
)

ACCESS_TOKEN_OPTION = click.option(
    "--access_token",
    prompt="Your access token",
    prompt_required=False,
    help="The access token to use for authentication (leave blank if you want to logon interactively)",
)

USERNAME_OPTION = click.option(
    "--username",
    prompt="Your username",
    prompt_required=False,
    help="The username to use for authentication (leave blank if you want to logon interactively)",
)

PASSWORD_OPTION = click.option(
    "--password",
    prompt="Your password",
    hide_input=True,
    prompt_required=False,
    help="The password to use for authentication (leave blank if you want to logon interactively)",
)

DEVICE_CODE_OPTION = click.option(
    "--device_code",
    is_flag=True,
    help="Use device code authentication (leave blank if you want to logon interactively)",
)

SCOPES_OPTION = click.option(
    "--scopes",
    prompt="The scopes to be used for authentication",
    prompt_required=False,
    help="The scopes to use for authentication (leave blank if you want to use the default scopes)",
)

_logger = logging.getLogger(__name__)


@click.command(
    "get-access-token", help="Gets an access token to be used in other commands"
)
@click.pass_context
@TENANT_ID_OPTION
@CLIENT_ID_OPTION
@CLIENT_SECRET_OPTION
@USERNAME_OPTION
@PASSWORD_OPTION
@DEVICE_CODE_OPTION
@SCOPES_OPTION
@click.option(
    "--output_token",
    is_flag=True,
    help="Indicates if the access token should be output to the console",
)
def get_access_token(
    ctx: click.Context,
    tenant_id: str,
    client_id: str,
    scopes: list[str],
    client_secret: str | None = None,
    username: str | None = None,
    password: str | None = None,
    device_code: bool = False,
    output_token: bool = False,
) -> str:
    ctx.ensure_object(dict)
    if device_code:
        access_token = acquire_token_by_device_flow(
            client_id=client_id,
            tenant_id=tenant_id,
            scopes=scopes,
        )
    elif client_secret:
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
    ctx.obj["access_token"] = access_token
    if output_token:
        click.echo(access_token)
    return access_token
