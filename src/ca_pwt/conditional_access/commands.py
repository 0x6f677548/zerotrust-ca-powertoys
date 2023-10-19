import click
import logging
from ..helpers.dict import remove_element_from_dict
from ..helpers.click import get_from_ctx_if_none, exit_with_exception
from .graph_api import PoliciesAPI
from ..authentication import get_access_token, ACCESS_TOKEN_OPTION
from .mappings import ids_to_names, names_to_ids

_logger = logging.getLogger(__name__)


OUTPUT_FILE_OPTION = click.option(
    "--output_file",
    type=click.Path(exists=False),
    prompt="The output file",
    prompt_required=False,
    help="The file to write the policies to",
)

INPUT_FILE_OPTION = click.option(
    "--input_file",
    type=click.Path(exists=True),
    prompt="The input file",
    prompt_required=False,
    help="The file to read the policies from",
)


def _format_policies(policies: dict) -> dict:
    remove_element_from_dict(policies, "@odata.context")

    # check if it is the graph api response format (i.e. a dict with a value key)
    # if so, let's get the value and make sure it is a list
    if (
        "value" in policies
        and policies["value"] is not None
        and isinstance(policies["value"], list)
    ):
        policies = policies["value"]

    # check if we have a single policy. If so, let's wrap it in a list
    elif policies and not isinstance(policies, list):
        policies = [policies]
    elif not policies:
        raise Exception(
            "The policies file is not in the expected format. Please check the documentation."
        )
    return policies


def _load_policies(input_file: str) -> dict:
    import json

    with open(input_file, "r") as f:
        click.echo(f"Reading policies from file {input_file}...")

        policies = json.load(f)
        policies = _format_policies(policies)
        return policies


def _save_policies(policies: dict, output_file: str):
    import json

    with open(output_file, "w") as f:
        click.echo(f"Writing policies to file {output_file}...")
        f.write(json.dumps(policies, indent=4))


def _cleanup_policies(source: dict) -> dict:
    click.echo("Cleaning up policies...")

    # exclude some elements, namely createdDateTime,
    # modifiedDateTime, id, templateId, authenticationStrength@odata.context
    for policy in source:
        remove_element_from_dict(policy, "createdDateTime")
        remove_element_from_dict(policy, "modifiedDateTime")
        remove_element_from_dict(policy, "id")
        remove_element_from_dict(policy, "templateId")
        grant_controls = policy["grantControls"]
        if grant_controls is not None:
            remove_element_from_dict(
                grant_controls, "authenticationStrength@odata.context"
            )
    return source


@click.command(
    "replace-keys-by-values",
    help="Replaces keys by values in conditional access policies" +
    " (e.g. group ids by group names, user ids by user principal names, etc.)",
)
@click.pass_context
@ACCESS_TOKEN_OPTION
@OUTPUT_FILE_OPTION
@INPUT_FILE_OPTION
def replace_keys_by_values(
    ctx: click.Context,
    input_file: str,
    output_file: str,
    access_token: str | None = None,
):
    try:
        ctx.ensure_object(dict)
        click.secho(
            "Replacing keys by values in conditional access policies...",
            fg="yellow",
        )
        access_token = get_from_ctx_if_none(
            ctx, "access_token", access_token, get_access_token
        )
        input_file = get_from_ctx_if_none(
            ctx, "output_file", input_file, lambda: click.prompt("The input file")
        )
        output_file = get_from_ctx_if_none(
            ctx, "output_file", output_file, lambda: click.prompt("The output file")
        )

        policies = _load_policies(input_file)
        policies = ids_to_names(access_token, policies)

        _save_policies(policies=policies, output_file=output_file)

        # store the output file in the context for chaining commands
        ctx.obj["output_file"] = output_file
    except Exception as e:
        exit_with_exception(e)


@click.command(
    "replace-values-by-keys",
    help="Replaces values by keys in conditional access policies" +
    " (e.g. group names by group ids, user principal names by user ids, etc.)",
)
@click.pass_context
@ACCESS_TOKEN_OPTION
@OUTPUT_FILE_OPTION
@INPUT_FILE_OPTION
def replace_values_by_keys(
    ctx: click.Context,
    input_file: str,
    output_file: str,
    access_token: str | None = None,
):
    try:
        ctx.ensure_object(dict)
        click.secho(
            "Replacing values by keys in conditional access policies...",
            fg="yellow",
        )

        access_token = get_from_ctx_if_none(
            ctx, "access_token", access_token, get_access_token
        )

        input_file = get_from_ctx_if_none(
            ctx, "output_file", input_file, lambda: click.prompt("The input file")
        )
        output_file = get_from_ctx_if_none(
            ctx, "output_file", output_file, lambda: click.prompt("The output file")
        )

        policies = _load_policies(input_file)
        policies = names_to_ids(access_token, policies)

        _save_policies(policies=policies, output_file=output_file)

        # store the output file in the context for chaining commands
        ctx.obj["output_file"] = output_file
    except Exception as e:
        exit_with_exception(e)


@click.command("export-policies", help="Exports conditional access policies with a " +
               "filter (e.g. 'startswith(displayName, 'Test')') to a file")
@click.pass_context
@ACCESS_TOKEN_OPTION
@click.option(
    "--filter",
    help="ODATA filter to apply to the policies (e.g. 'startswith(displayName, 'Test')')",
    default=None,
)
@OUTPUT_FILE_OPTION
def export_policies(
    ctx: click.Context,
    output_file: str,
    access_token: str | None = None,
    filter: str | None = None,
):
    try:
        ctx.ensure_object(dict)
        click.secho("Exporting conditional access policies...", fg="yellow")

        access_token = get_from_ctx_if_none(
            ctx, "access_token", access_token, get_access_token
        )

        output_file = get_from_ctx_if_none(
            ctx, "output_file", output_file, lambda: click.prompt("The output file")
        )

        click.echo("Obtaining policies from tenant...")
        policies_api = PoliciesAPI(access_token=access_token)
        response = policies_api.get_all(odata_filter=filter)
        if not response.success:
            click.secho(
                f"Something went wrong while obtaining the policies: {response.status_code}",
                fg="red",
            )
            click.secho(response.json(), fg="red")
            click.Abort()

        policies = response.json()

        _logger.debug(f"Obtained policies: {policies}")
        policies = _format_policies(policies)
        _logger.debug(f"Formatted policies: {policies}")
        _save_policies(policies=policies, output_file=output_file)

        # store the output file in the context for chaining commands
        ctx.obj["output_file"] = output_file
    except Exception as e:
        exit_with_exception(e)


@click.command(
    "cleanup-policies",
    help="Cleans up conditional access policies file for import (e.g. removes " +
    "createdDateTime, modifiedDateTime, id, templateId"
)
@click.pass_context
@OUTPUT_FILE_OPTION
@INPUT_FILE_OPTION
def cleanup_policies(ctx: click.Context, input_file: str, output_file: str):
    try:
        ctx.ensure_object(dict)
        click.secho(
            "Cleaning up conditional access policies for import...", fg="yellow"
        )

        input_file = get_from_ctx_if_none(
            ctx, "output_file", input_file, lambda: click.prompt("The input file")
        )
        output_file = get_from_ctx_if_none(
            ctx, "output_file", output_file, lambda: click.prompt("The output file")
        )

        policies = _load_policies(input_file)
        policies = _cleanup_policies(policies)
        _save_policies(policies=policies, output_file=output_file)

        # store the output file in the context for chaining commands
        ctx.obj["output_file"] = output_file
    except Exception as e:
        exit_with_exception(e)


@click.command("import-policies", help="Imports conditional access policies")
@click.pass_context
@ACCESS_TOKEN_OPTION
@INPUT_FILE_OPTION
def import_policies(ctx: click.Context, input_file: str, access_token: str | None = None):
    try:
        ctx.ensure_object(dict)
        click.secho("Importing conditional access policies...", fg="yellow")
        access_token = get_from_ctx_if_none(
            ctx, "access_token", access_token, get_access_token
        )
        input_file = get_from_ctx_if_none(
            ctx, "output_file", input_file, lambda: click.prompt("The input file")
        )

        policies = _load_policies(input_file)
        # make sure the policies are cleaned up
        policies = _cleanup_policies(policies)
        policies = names_to_ids(access_token, policies)
        policies_api = PoliciesAPI(access_token=access_token)

        for policy in policies:
            displayName = policy.get("displayName")
            click.echo(f"Creating policy {displayName}...")
            _logger.debug(f"Policy: {policy}")
            response = policies_api.create(policy)
            response.assert_success()
            click.echo("Policy created successfully")
    except Exception as e:
        exit_with_exception(e)
