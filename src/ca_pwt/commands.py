import click
import logging
from sys import exit
from ca_pwt.authentication import acquire_token
from typing import Callable, Any
from ca_pwt.policies import (
    load_policies,
    save_policies,
    cleanup_policies,
    export_policies,
    import_policies,
    get_groups_in_policies,
)
from ca_pwt.groups import (
    load_groups,
    save_groups,
    cleanup_groups,
    import_groups,
)
from ca_pwt.helpers.graph_api import DuplicateActionEnum

from ca_pwt.policies_mappings import replace_keys_by_values_in_policies, replace_values_by_keys_in_policies

_logger = logging.getLogger(__name__)

_output_file_option = click.option(
    "--output_file",
    type=click.Path(exists=False),
    prompt="The output file",
    prompt_required=False,
    help="The file to write the policies to",
)

_input_file_option = click.option(
    "--input_file",
    type=click.Path(exists=False),  # although it should exists, chaining commands will fail if it does not
    prompt="The input file",
    prompt_required=False,
    help="The file to read the policies from",
)

_access_token_option = click.option(
    "--access_token",
    prompt="Your access token",
    prompt_required=False,
    help="The access token to use for authentication (leave blank if you want to logon interactively)",
)

_ignore_not_found_option = click.option(
    "--ignore_not_found",
    is_flag=True,
    default=True,
    help="Indicates if not found errors should be ignored when exporting groups",
)

_allow_duplicates_option = click.option(
    "--allow_duplicates",
    is_flag=True,
    default=False,
    help="Indicates if duplicates should be allowed and imported. "
    "Duplicates are checked by comparing the displayName of Policies/Groups",
)

_duplicate_action_option = click.option(
    "--duplicate_action",
    type=click.Choice([action.value for action in DuplicateActionEnum], case_sensitive=True),
    help="The action to take when a duplicate is found (default is ignore). ",
    default=DuplicateActionEnum.ignore.value,
)


def _exit_with_exception(exception: Exception, exit_code: int = 1, fg: str = "red"):
    """Exit the program with an exception and exit code"""
    try:
        _logger.exception(exception)
        click.secho(
            "An error occurred. See the log for more details. (--log_level ERROR). Exiting... "
            f"(Exception Type: {type(exception).__name__}); (Exception: {exception})",
            fg=fg,
        )
    finally:
        exit(exit_code)


def _get_from_ctx_if_none(
    ctx: click.Context,
    ctx_key: str,
    value: str | None,
    invoke_func: Callable[..., str],
    **kwargs: Any,
) -> str:
    """Get a value from the context if it is None,
    otherwise invoke a function to get the value."""
    ctx.ensure_object(dict)
    if value:
        return value
    elif ctx_key in ctx.obj and ctx.obj[ctx_key]:
        return ctx.obj[ctx_key]
    else:
        result = ctx.invoke(invoke_func, **kwargs)
        return result


@click.command("acquire-token", help="Acquires an access token to be used in other commands")
@click.pass_context
@click.option(
    "--client_id",
    prompt="Your client ID",
    prompt_required=False,
    help="The client ID of this Azure AD app (leave blank if you want to use Graph Command Line Tools)",
)
@click.option(
    "--tenant_id",
    prompt="Your tenant ID",
    prompt_required=False,
    help="The tenant ID (leave blank if you want to use the default tenant of your user)",
)
@click.option(
    "--client_secret",
    prompt="Your client secret",
    prompt_required=False,
    help="The client secret of your Azure AD app "
    "(leave blank if you want to use delegated permissions with a user account)",
)
@click.option(
    "--username",
    prompt="Your username",
    prompt_required=False,
    help="The username to use for authentication (leave blank if you want to logon interactively)",
)
@click.option(
    "--password",
    prompt="Your password",
    hide_input=True,
    prompt_required=False,
    help="The password to use for authentication (leave blank if you want to logon interactively)",
)
@click.option(
    "--device_code",
    is_flag=True,
    help="Use device code authentication (leave blank if you want to logon interactively)",
)
@click.option(
    "--scope",
    prompt="The scopes to be used for authentication",
    prompt_required=False,
    multiple=True,
    help="The scopes to use for authentication (leave blank if you want to use the default scopes)."
    "This parameter can be specified multiple times to specify multiple scopes",
)
@click.option(
    "--output_token",
    is_flag=True,
    help="Indicates if the access token should be output to the console",
)
def acquire_token_cmd(
    ctx: click.Context,
    tenant_id: str,
    client_id: str,
    scope: list[str],
    client_secret: str | None = None,
    username: str | None = None,
    password: str | None = None,
    *,
    device_code: bool = False,
    output_token: bool = False,
) -> str:
    """Acquires an access token to be used in other commands
    and stores it in the context for chaining commands
    (e.g. acquire-token | export-policies | import-policies)
    """

    try:
        # note: this command should not output anything to the console
        # other than the access token if the output_token flag is set or
        # any usage that relies on the access token being output will fail
        ctx.ensure_object(dict)

        access_token = acquire_token(
            tenant_id, client_id, scope, client_secret, username, password, device_code=device_code
        )

        # store the access token in the context for chaining commands
        ctx.obj["access_token"] = access_token
        if output_token:
            click.echo(access_token)
    except Exception as e:
        _exit_with_exception(e)
    return access_token


@click.command(
    "replace-keys-by-values",
    help="Replaces keys by values in CA policies"
    " (e.g. group ids by group names, user ids by user principal names, etc.)",
)
@click.pass_context
@_access_token_option
@_output_file_option
@_input_file_option
def replace_keys_by_values_cmd(
    ctx: click.Context,
    input_file: str,
    output_file: str,
    access_token: str | None = None,
):
    """Replaces keys by values in CA policies"""

    try:
        ctx.ensure_object(dict)
        click.secho(
            "Replacing keys by values in CA policies...",
            fg="yellow",
        )
        access_token = _get_from_ctx_if_none(ctx, "access_token", access_token, acquire_token_cmd)
        input_file = _get_from_ctx_if_none(ctx, "output_file", input_file, lambda: click.prompt("The input file"))
        output_file = _get_from_ctx_if_none(ctx, "output_file", output_file, lambda: click.prompt("The output file"))
        click.echo(f"Input file: {input_file}; Output file: {output_file}")

        policies = load_policies(input_file)
        policies = replace_keys_by_values_in_policies(access_token, policies)

        save_policies(policies=policies, output_file=output_file)

        # store the output file in the context for chaining commands
        ctx.obj["output_file"] = output_file
    except Exception as e:
        _exit_with_exception(e)


@click.command(
    "replace-values-by-keys",
    help="Replaces values by keys in CA policies"
    " (e.g. group names by group ids, user principal names by user ids, etc.)",
)
@click.pass_context
@_access_token_option
@_output_file_option
@_input_file_option
def replace_values_by_keys_cmd(
    ctx: click.Context,
    input_file: str,
    output_file: str,
    access_token: str | None = None,
):
    """Replaces values by keys in CA policies"""

    try:
        ctx.ensure_object(dict)
        click.secho(
            "Replacing values by keys in CA policies...",
            fg="yellow",
        )

        access_token = _get_from_ctx_if_none(ctx, "access_token", access_token, acquire_token_cmd)

        input_file = _get_from_ctx_if_none(ctx, "output_file", input_file, lambda: click.prompt("The input file"))
        output_file = _get_from_ctx_if_none(ctx, "output_file", output_file, lambda: click.prompt("The output file"))
        click.echo(f"Input file: {input_file}; Output file: {output_file}")

        policies = load_policies(input_file)
        policies = replace_values_by_keys_in_policies(access_token, policies)

        save_policies(policies=policies, output_file=output_file)

        # store the output file in the context for chaining commands
        ctx.obj["output_file"] = output_file
    except Exception as e:
        _exit_with_exception(e)


@click.command(
    "export-policies",
    help="Exports CA policies with a filter (e.g. 'startswith(displayName, 'Test')') to a file",
)
@click.pass_context
@_access_token_option
@click.option(
    "--odata_filter",
    help="ODATA filter to apply to the policies (e.g. 'startswith(displayName, 'Test')')",
    default=None,
)
@_output_file_option
def export_policies_cmd(
    ctx: click.Context,
    output_file: str,
    access_token: str | None = None,
    odata_filter: str | None = None,
):
    """Exports CA policies with a filter (e.g. 'startswith(displayName, 'Test')') to a file"""

    try:
        ctx.ensure_object(dict)
        click.secho("Exporting ca policies...", fg="yellow")

        access_token = _get_from_ctx_if_none(ctx, "access_token", access_token, acquire_token_cmd)

        output_file = _get_from_ctx_if_none(ctx, "output_file", output_file, lambda: click.prompt("The output file"))
        click.echo(f"Output file: {output_file}")

        policies = export_policies(access_token, odata_filter)
        save_policies(policies=policies, output_file=output_file)

        # store the output file in the context for chaining commands
        ctx.obj["output_file"] = output_file
    except Exception as e:
        _exit_with_exception(e)


@click.command(
    "cleanup-policies",
    help="Cleans up CA policies file for import (e.g. removes createdDateTime, modifiedDateTime, id, templateId",
)
@click.pass_context
@_output_file_option
@_input_file_option
def cleanup_policies_cmd(ctx: click.Context, input_file: str, output_file: str):
    """Cleans up CA policies file for import (e.g. removes
    createdDateTime, modifiedDateTime, id, templateId)"""
    try:
        ctx.ensure_object(dict)
        click.secho("Cleaning up CA policies for import...", fg="yellow")

        input_file = _get_from_ctx_if_none(ctx, "output_file", input_file, lambda: click.prompt("The input file"))
        output_file = _get_from_ctx_if_none(ctx, "output_file", output_file, lambda: click.prompt("The output file"))
        click.echo(f"Input file: {input_file}; Output file: {output_file}")

        policies = load_policies(input_file)
        policies = cleanup_policies(policies)
        save_policies(policies=policies, output_file=output_file)

        # store the output file in the context for chaining commands
        ctx.obj["output_file"] = output_file
    except Exception as e:
        _exit_with_exception(e)


@click.command("cleanup-groups", help="Cleans up groups file for import")
@click.pass_context
@_output_file_option
@_input_file_option
def cleanup_groups_cmd(ctx: click.Context, input_file: str, output_file: str):
    """Cleans up groups file for import (e.g. removes
    createdDateTime, modifiedDateTime, id)"""
    try:
        ctx.ensure_object(dict)
        click.secho("Cleaning up groups for import...", fg="yellow")

        input_file = _get_from_ctx_if_none(ctx, "output_file", input_file, lambda: click.prompt("The input file"))
        output_file = _get_from_ctx_if_none(ctx, "output_file", output_file, lambda: click.prompt("The output file"))
        click.echo(f"Input file: {input_file}; Output file: {output_file}")

        groups = load_groups(input_file)
        groups = cleanup_groups(groups)
        save_groups(groups=groups, output_file=output_file)

        # store the output file in the context for chaining commands
        ctx.obj["output_file"] = output_file
    except Exception as e:
        _exit_with_exception(e)


@click.command("import-policies", help="Imports CA policies from a file")
@click.pass_context
@_access_token_option
@_input_file_option
@_duplicate_action_option
def import_policies_cmd(
    ctx: click.Context,
    input_file: str,
    access_token: str | None = None,
    duplicate_action: DuplicateActionEnum = DuplicateActionEnum.ignore,
):
    """Imports CA policies from a file"""
    try:
        ctx.ensure_object(dict)
        click.secho("Importing CA policies...", fg="yellow")
        access_token = _get_from_ctx_if_none(ctx, "access_token", access_token, acquire_token_cmd)
        input_file = _get_from_ctx_if_none(
            ctx,
            "output_file",
            input_file,
            lambda: click.prompt("The input file", type=click.Path(exists=True)),
        )
        click.echo(f"Input file: {input_file}")

        policies = load_policies(input_file)

        created_policies = import_policies(
            access_token=access_token, policies=policies, duplicate_action=duplicate_action
        )

        click.echo("Successfully created policies:")
        for policy in created_policies:
            click.echo(f"{policy[0]}: {policy[1]}")
    except Exception as e:
        _exit_with_exception(e)


@click.command("export-groups", help="Exports groups found in a CA policies file to a file")
@click.pass_context
@_access_token_option
@_input_file_option
@_output_file_option
@_ignore_not_found_option
def export_groups_cmd(
    ctx: click.Context,
    input_file: str,
    output_file: str,
    access_token: str | None = None,
    *,
    ignore_not_found: bool = False,
):
    """Exports groups found in a CA policies file to a group file"""
    try:
        ctx.ensure_object(dict)
        click.secho("Exporting groups found in CA policies...", fg="yellow")
        access_token = _get_from_ctx_if_none(ctx, "access_token", access_token, acquire_token_cmd)
        input_file = _get_from_ctx_if_none(ctx, "output_file", input_file, lambda: click.prompt("The input file"))
        output_file = _get_from_ctx_if_none(ctx, "output_file", output_file, lambda: click.prompt("The output file"))
        click.echo(f"Input file: {input_file}; Output file: {output_file}")
        policies = load_policies(input_file)
        groups = get_groups_in_policies(access_token, policies, ignore_not_found=ignore_not_found)
        save_groups(groups=groups, output_file=output_file)

        # store the output file in the context for chaining commands
        ctx.obj["output_file"] = output_file
    except Exception as e:
        _exit_with_exception(e)


@click.command(
    "import-groups",
    help="Imports groups from a file."
    "This commands needs the following scopes: "
    "Group.ReadWrite.All, Directory.ReadWrite.All ",
)
@click.pass_context
@_access_token_option
@_input_file_option
@_duplicate_action_option
def import_groups_cmd(
    ctx: click.Context,
    input_file: str,
    access_token: str | None = None,
    duplicate_action: DuplicateActionEnum = DuplicateActionEnum.ignore,
):
    """Imports groups from a file"""
    try:
        ctx.ensure_object(dict)
        click.secho("Importing groups...", fg="yellow")

        # this command needs the following scopes:
        # Group.ReadWrite.All, Directory.ReadWrite.All
        # so let's make sure they are present if the access token is not specified
        access_token = _get_from_ctx_if_none(
            ctx,
            "access_token",
            access_token,
            acquire_token_cmd,
            scope=["Group.ReadWrite.All", "Directory.ReadWrite.All"],
        )
        input_file = _get_from_ctx_if_none(ctx, "output_file", input_file, lambda: click.prompt("The input file"))
        click.echo(f"Input file: {input_file}")
        groups = load_groups(input_file)
        created_groups = import_groups(access_token=access_token, groups=groups, duplicate_action=duplicate_action)
        click.echo("Successfully created groups:")
        for group in created_groups:
            click.echo(f"{group[0]}: {group[1]}")
    except Exception as e:
        _exit_with_exception(e)
