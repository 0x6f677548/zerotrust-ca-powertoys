import click
import logging
from .authentication import acquire_token
from .helpers.click import get_from_ctx_if_none, exit_with_exception
from .policies import (
    load_policies,
    save_policies,
    cleanup_policies,
    export_policies,
    import_policies,
)

from .policies_mappings import keys_to_values, values_to_keys

_logger = logging.getLogger(__name__)


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


OUTPUT_FILE_OPTION = click.option(
    "--output_file",
    type=click.Path(exists=False),
    prompt="The output file",
    prompt_required=False,
    help="The file to write the policies to",
)

INPUT_FILE_OPTION = click.option(
    "--input_file",
    type=click.Path(exists=False),  # although it should exists, chaining commands will fail if it does not
    prompt="The input file",
    prompt_required=False,
    help="The file to read the policies from",
)


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
def get_access_token_cmd(
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
    access_token = acquire_token(
        tenant_id, client_id, scopes, client_secret, username, password, device_code
    )
    # store the access token in the context for chaining commands
    ctx.obj["access_token"] = access_token
    if output_token:
        click.echo(access_token)
    return access_token


@click.command(
    "replace-keys-by-values",
    help="Replaces keys by values in CA policies"
    + " (e.g. group ids by group names, user ids by user principal names, etc.)",
)
@click.pass_context
@ACCESS_TOKEN_OPTION
@OUTPUT_FILE_OPTION
@INPUT_FILE_OPTION
def replace_keys_by_values_cmd(
    ctx: click.Context,
    input_file: str,
    output_file: str,
    access_token: str | None = None,
):
    try:
        ctx.ensure_object(dict)
        click.secho(
            "Replacing keys by values in CA policies...",
            fg="yellow",
        )
        access_token = get_from_ctx_if_none(
            ctx, "access_token", access_token, get_access_token_cmd
        )
        input_file = get_from_ctx_if_none(
            ctx, "output_file", input_file, lambda: click.prompt("The input file")
        )
        output_file = get_from_ctx_if_none(
            ctx, "output_file", output_file, lambda: click.prompt("The output file")
        )

        policies = load_policies(input_file)
        policies = keys_to_values(access_token, policies)

        save_policies(policies=policies, output_file=output_file)

        # store the output file in the context for chaining commands
        ctx.obj["output_file"] = output_file
    except Exception as e:
        exit_with_exception(e)


@click.command(
    "replace-values-by-keys",
    help="Replaces values by keys in CA policies"
    + " (e.g. group names by group ids, user principal names by user ids, etc.)",
)
@click.pass_context
@ACCESS_TOKEN_OPTION
@OUTPUT_FILE_OPTION
@INPUT_FILE_OPTION
def replace_values_by_keys_cmd(
    ctx: click.Context,
    input_file: str,
    output_file: str,
    access_token: str | None = None,
):
    try:
        ctx.ensure_object(dict)
        click.secho(
            "Replacing values by keys in CA policies...",
            fg="yellow",
        )

        access_token = get_from_ctx_if_none(
            ctx, "access_token", access_token, get_access_token_cmd
        )

        input_file = get_from_ctx_if_none(
            ctx, "output_file", input_file, lambda: click.prompt("The input file")
        )
        output_file = get_from_ctx_if_none(
            ctx, "output_file", output_file, lambda: click.prompt("The output file")
        )

        policies = load_policies(input_file)
        policies = values_to_keys(access_token, policies)

        save_policies(policies=policies, output_file=output_file)

        # store the output file in the context for chaining commands
        ctx.obj["output_file"] = output_file
    except Exception as e:
        exit_with_exception(e)


@click.command(
    "export-policies",
    help="Exports CA policies with a "
    + "filter (e.g. 'startswith(displayName, 'Test')') to a file",
)
@click.pass_context
@ACCESS_TOKEN_OPTION
@click.option(
    "--filter",
    help="ODATA filter to apply to the policies (e.g. 'startswith(displayName, 'Test')')",
    default=None,
)
@OUTPUT_FILE_OPTION
def export_policies_cmd(
    ctx: click.Context,
    output_file: str,
    access_token: str | None = None,
    filter: str | None = None,
):
    try:
        ctx.ensure_object(dict)
        click.secho("Exporting ca policies...", fg="yellow")

        access_token = get_from_ctx_if_none(
            ctx, "access_token", access_token, get_access_token_cmd
        )

        output_file = get_from_ctx_if_none(
            ctx, "output_file", output_file, lambda: click.prompt("The output file")
        )

        policies = export_policies(access_token, filter)
        save_policies(policies=policies, output_file=output_file)

        # store the output file in the context for chaining commands
        ctx.obj["output_file"] = output_file
    except Exception as e:
        exit_with_exception(e)


@click.command(
    "cleanup-policies",
    help="Cleans up CA policies file for import (e.g. removes "
    + "createdDateTime, modifiedDateTime, id, templateId",
)
@click.pass_context
@OUTPUT_FILE_OPTION
@INPUT_FILE_OPTION
def cleanup_policies_cmd(ctx: click.Context, input_file: str, output_file: str):
    try:
        ctx.ensure_object(dict)
        click.secho(
            "Cleaning up CA policies for import...", fg="yellow"
        )

        input_file = get_from_ctx_if_none(
            ctx, "output_file", input_file, lambda: click.prompt("The input file")
        )
        output_file = get_from_ctx_if_none(
            ctx, "output_file", output_file, lambda: click.prompt("The output file")
        )

        policies = load_policies(input_file)
        policies = cleanup_policies(policies)
        save_policies(policies=policies, output_file=output_file)

        # store the output file in the context for chaining commands
        ctx.obj["output_file"] = output_file
    except Exception as e:
        exit_with_exception(e)


@click.command("import-policies", help="Imports CA policies from a file")
@click.pass_context
@ACCESS_TOKEN_OPTION
@INPUT_FILE_OPTION
def import_policies_cmd(
    ctx: click.Context, input_file: str, access_token: str | None = None
):
    try:
        ctx.ensure_object(dict)
        click.secho("Importing CA policies...", fg="yellow")
        access_token = get_from_ctx_if_none(
            ctx, "access_token", access_token, get_access_token_cmd
        )
        input_file = get_from_ctx_if_none(
            ctx, "output_file", input_file, lambda: click.prompt("The input file", type=click.Path(exists=True))
        )

        policies = load_policies(input_file)
        created_policies = import_policies(access_token, policies)
        click.echo("Successfully created policies:")
        for policy in created_policies:
            click.echo(f"{policy[0]}: {policy[1]}")
    except Exception as e:
        exit_with_exception(e)
