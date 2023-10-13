import click
import logging
from helpers.dict import remove_element_from_dict, replace_with_key_value_lookup
from helpers.click import get_from_ctx_if_none
from .graph_api import get_policies, create_policy
from groups.graph_api import get_group_id_by_name, get_group_name_by_id
from authentication import get_access_token, ACCESS_TOKEN_OPTION

_logger = logging.getLogger(__name__)


def _format_policies(policies: dict) -> dict:
    remove_element_from_dict(policies, "@odata.context")

    # remove the value element and replace it with the policies list
    if (
        "value" in policies
        and policies["value"] is not None
        and isinstance(policies["value"], list)
    ):
        policies = policies["value"]
    # check if we have a list of policies
    elif not policies or not isinstance(policies, list):
        raise Exception(
            "The policies file does not contain a value element or a list of policies"
        )
    return policies


def _names_to_ids_mapping(access_token: str, source: dict) -> dict:
    lookup_cache: dict = {}
    for policy in source:
        # let's transform groupIds to groupNames if any
        conditions = policy["conditions"]
        users = conditions["users"]
        lookup_cache = replace_with_key_value_lookup(
            parent_node=users,
            keys_node_name="excludeGroupNames",
            values_node_name="excludeGroups",
            lookup_func=lambda name: get_group_id_by_name(access_token, name),
            lookup_cache=lookup_cache,
        )
        lookup_cache = replace_with_key_value_lookup(
            parent_node=users,
            keys_node_name="includeGroupNames",
            values_node_name="includeGroups",
            lookup_func=lambda name: get_group_id_by_name(access_token, name),
            lookup_cache=lookup_cache,
        )

    return source


def _ids_to_names_mapping(access_token: str, source: dict) -> dict:
    lookup_cache = {}
    for policy in source:
        # let's transform groupIds to groupNames if any
        conditions = policy["conditions"]
        users = conditions["users"]
        lookup_cache = replace_with_key_value_lookup(
            parent_node=users,
            keys_node_name="excludeGroups",
            values_node_name="excludeGroupNames",
            lookup_func=lambda id: get_group_name_by_id(access_token, id),
            lookup_cache=lookup_cache,
        )
        lookup_cache = replace_with_key_value_lookup(
            parent_node=users,
            keys_node_name="includeGroups",
            values_node_name="includeGroupNames",
            lookup_func=lambda id: get_group_name_by_id(access_token, id),
            lookup_cache=lookup_cache,
        )

    return source


@click.command(
    "ca-group-ids-to-names",
    help="Convert group ids to names in conditional access policies",
)
@click.pass_context
@ACCESS_TOKEN_OPTION
@click.option(
    "--input_file",
    type=click.Path(exists=True),
    prompt="The input file",
    prompt_required=False,
    help="The file to read the policies from",
)
@click.option(
    "--output_file",
    type=click.Path(exists=False),
    prompt="The output file",
    prompt_required=False,
    help="The file to write the policies to",
)
def ca_group_ids_to_names(
    ctx: click.Context,
    input_file: str,
    output_file: str,
    access_token: str | None = None,
):
    ctx.ensure_object(dict)
    click.secho(
        "Converting group ids to names in conditional access policies...", fg="yellow"
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

    click.echo(f"Reading policies from file {input_file}...")

    import json

    with open(input_file, "r") as f:
        policies = json.load(f)
        policies = _ids_to_names_mapping(access_token, policies)
        import json

        with open(output_file, "w") as f:
            click.echo(f"Writing policies to file {output_file}...")
            f.write(json.dumps(policies, indent=4))
    # store the output file in the context for chaining commands
    ctx.obj["output_file"] = output_file


@click.command(
    "ca-group-names-to-ids",
    help="Convert group names to ids in conditional access policies",
)
@click.pass_context
@ACCESS_TOKEN_OPTION
@click.option(
    "--input_file",
    type=click.Path(exists=True),
    prompt="The input file",
    prompt_required=False,
    help="The file to read the policies from",
)
@click.option(
    "--output_file",
    type=click.Path(exists=False),
    prompt="The output file",
    prompt_required=False,
    help="The file to write the policies to",
)
def ca_group_names_to_ids(
    ctx: click.Context,
    input_file: str,
    output_file: str,
    access_token: str | None = None,
):
    ctx.ensure_object(dict)
    click.secho("Converting group names to ids in conditional access policies...")
    access_token = get_from_ctx_if_none(
        ctx, "access_token", access_token, get_access_token
    )

    input_file = get_from_ctx_if_none(
        ctx, "output_file", input_file, lambda: click.prompt("The input file")
    )
    output_file = get_from_ctx_if_none(
        ctx, "output_file", output_file, lambda: click.prompt("The output file")
    )

    click.echo(f"Reading policies from file {input_file}...")

    import json

    with open(input_file, "r") as f:
        policies = json.load(f)
        policies = _names_to_ids_mapping(access_token, policies)
        import json

        with open(output_file, "w") as f:
            click.echo(f"Writing policies to file {output_file}...")
            f.write(json.dumps(policies, indent=4))
    # store the output file in the context for chaining commands
    ctx.obj["output_file"] = output_file


@click.command("ca-export", help="Export conditional access policies")
@click.pass_context
@ACCESS_TOKEN_OPTION
@click.option(
    "--output_file",
    type=click.Path(exists=False),
    prompt="The output file",
    help="The file to write the policies to",
    default="policies.json",
)
def ca_export(ctx: click.Context, output_file: str, access_token: str | None = None):
    ctx.ensure_object(dict)
    click.secho("Exporting conditional access policies...", fg="yellow")

    access_token = get_from_ctx_if_none(
        ctx, "access_token", access_token, get_access_token
    )

    click.echo("Obtaining policies from tenant...")
    policies = get_policies(access_token)

    # limit the policies to 1 for testing purposes
    policies = policies["value"][:1]

    _logger.debug(f"Obtained policies: {policies}")
    policies = _format_policies(policies)
    _logger.debug(f"Formatted policies: {policies}")
    import json

    with open(output_file, "w") as f:
        click.echo(f"Writing policies to file {output_file}...")
        f.write(json.dumps(policies, indent=4))

    # store the output file in the context for chaining commands
    ctx.obj["output_file"] = output_file


def _ca_policies_cleanup_for_import(policies: dict) -> dict:
    # exclude some elements, namely createdDateTime,
    # modifiedDateTime, id, templateId, authenticationStrength@odata.context
    for policy in policies:
        remove_element_from_dict(policy, "createdDateTime")
        remove_element_from_dict(policy, "modifiedDateTime")
        remove_element_from_dict(policy, "id")
        remove_element_from_dict(policy, "templateId")
        grant_controls = policy["grantControls"]
        if grant_controls is not None:
            remove_element_from_dict(
                grant_controls, "authenticationStrength@odata.context"
            )
    return policies


@click.command(
    "ca-cleanup-for-import",
    help="Cleanup conditional access policies file for import",
)
@click.pass_context
@click.option(
    "--input_file",
    type=click.Path(exists=True),
    prompt="The input file",
    prompt_required=False,
    help="The file to read the policies from",
)
@click.option(
    "--output_file",
    type=click.Path(exists=False),
    prompt="The output file",
    prompt_required=False,
    help="The file to write the policies to",
)
def ca_cleanup_for_import(ctx: click.Context, input_file: str, output_file: str):
    ctx.ensure_object(dict)
    click.secho("Cleaning up conditional access policies for import...", fg="yellow")

    input_file = get_from_ctx_if_none(
        ctx, "output_file", input_file, lambda: click.prompt("The input file")
    )
    output_file = get_from_ctx_if_none(
        ctx, "output_file", output_file, lambda: click.prompt("The output file")
    )

    click.echo(f"Reading policies from file {input_file}...")
    import json

    with open(input_file, "r") as f:
        policies = json.load(f)
        policies = _ca_policies_cleanup_for_import(policies)

        import json

        with open(output_file, "w") as f:
            click.echo(f"Writing policies to file {output_file}...")
            f.write(json.dumps(policies, indent=4))

    # store the output file in the context for chaining commands
    ctx.obj["output_file"] = output_file


@click.command("ca-import", help="Import conditional access policies")
@click.pass_context
@ACCESS_TOKEN_OPTION
@click.option(
    "--input_file",
    prompt="The input file",
    prompt_required=False,
    help="The file to read the policies from",
)
def ca_import(ctx: click.Context, input_file: str, access_token: str | None = None):
    ctx.ensure_object(dict)
    click.secho("Importing conditional access policies...", fg="yellow")
    access_token = get_from_ctx_if_none(
        ctx, "access_token", access_token, get_access_token
    )
    input_file = get_from_ctx_if_none(
        ctx, "output_file", input_file, lambda: click.prompt("The input file")
    )
    click.echo(f"Importing policies from file {input_file}...")

    import json

    with open(input_file, "r") as f:
        source = json.load(f)
        click.echo("Cleaning up policies...")
        # if we get a single policy, we need to convert it to a list
        if not isinstance(source, list):
            source = [source]

        # make sure the policies are cleaned up
        policies = _ca_policies_cleanup_for_import(source)
        policies = _names_to_ids_mapping(access_token, policies)
        for policy in source:
            _logger.debug(f"Creating policy {policy['displayName']}...")
            _logger.debug(f"Policy: {policy}")
            click.echo(f'Creating policy {policy["displayName"]}...')
            response = create_policy(access_token, policy)
            if response.success:
                click.echo("Policy created successfully")
            else:
                click.secho(
                    f"Something went wrong while creating the policy: {response.status_code}",
                    fg="red",
                )
                click.secho(response.json(), fg="red")
