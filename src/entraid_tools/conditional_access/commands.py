import click
import logging
from ..helpers.dict import remove_element_from_dict, replace_with_key_value_lookup
from ..helpers.click import get_from_ctx_if_none
from .graph_api import PoliciesAPI
from ..groups.graph_api import GroupsAPI
from ..authentication import get_access_token, ACCESS_TOKEN_OPTION

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


def _names_to_ids_mapping(access_token: str, source: dict) -> dict:
    lookup_cache: dict = {}

    groups_api = GroupsAPI(access_token=access_token)

    def get_group_id_by_name(name: str) -> str | None:
        response = groups_api.get_by_name(name)
        if response.success:
            groups = response.json()["value"]
            if len(groups) == 0:
                return None
            else:
                return groups[0]["id"]
        else:
            return None

    for policy in source:
        # let's transform groupIds to groupNames if any
        conditions = policy["conditions"]
        users = conditions["users"]
        lookup_cache = replace_with_key_value_lookup(
            parent_node=users,
            keys_node_name="excludeGroupNames",
            values_node_name="excludeGroups",
            lookup_func=get_group_id_by_name,
            lookup_cache=lookup_cache,
        )
        lookup_cache = replace_with_key_value_lookup(
            parent_node=users,
            keys_node_name="includeGroupNames",
            values_node_name="includeGroups",
            lookup_func=get_group_id_by_name,
            lookup_cache=lookup_cache,
        )

    return source


def _ids_to_names_mapping(access_token: str, source: dict) -> dict:
    lookup_cache = {}

    groups_api: GroupsAPI = GroupsAPI(access_token)

    def get_group_name_by_id(id: str) -> str | None:
        response = groups_api.get_by_id(id)
        if response.success:
            group = response.json()
            return group["displayName"]
        else:
            return None

    for policy in source:
        # let's transform groupIds to groupNames if any
        conditions = policy["conditions"]
        users = conditions["users"]
        lookup_cache = replace_with_key_value_lookup(
            parent_node=users,
            keys_node_name="excludeGroups",
            values_node_name="excludeGroupNames",
            lookup_func=get_group_name_by_id,
            lookup_cache=lookup_cache,
        )
        lookup_cache = replace_with_key_value_lookup(
            parent_node=users,
            keys_node_name="includeGroups",
            values_node_name="includeGroupNames",
            lookup_func=get_group_name_by_id,
            lookup_cache=lookup_cache,
        )

    return source


def _ca_policies_cleanup_for_import(source: dict) -> dict:
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
    "ca-group-ids-to-names",
    help="Convert group ids to names in conditional access policies",
)
@click.pass_context
@ACCESS_TOKEN_OPTION
@OUTPUT_FILE_OPTION
@INPUT_FILE_OPTION
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

    policies = _load_policies(input_file)
    policies = _ids_to_names_mapping(access_token, policies)

    _save_policies(policies=policies, output_file=output_file)
    # store the output file in the context for chaining commands
    ctx.obj["output_file"] = output_file


@click.command(
    "ca-group-names-to-ids",
    help="Convert group names to ids in conditional access policies",
)
@click.pass_context
@ACCESS_TOKEN_OPTION
@OUTPUT_FILE_OPTION
@INPUT_FILE_OPTION
def ca_group_names_to_ids(
    ctx: click.Context,
    input_file: str,
    output_file: str,
    access_token: str | None = None,
):
    ctx.ensure_object(dict)
    click.secho(
        "Converting group names to ids in conditional access policies...", fg="yellow"
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
    policies = _names_to_ids_mapping(access_token, policies)

    _save_policies(policies=policies, output_file=output_file)

    # store the output file in the context for chaining commands
    ctx.obj["output_file"] = output_file


@click.command("ca-export", help="Export conditional access policies")
@click.pass_context
@ACCESS_TOKEN_OPTION
@click.option(
    "--filter",
    help="ODATA filter to apply to the policies (e.g. 'startswith(displayName, 'Test')')",
    default=None,
)
@OUTPUT_FILE_OPTION
def ca_export(
    ctx: click.Context,
    output_file: str,
    access_token: str | None = None,
    filter: str | None = None,
):
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


@click.command(
    "ca-cleanup-for-import",
    help="Cleanup conditional access policies file for import",
)
@click.pass_context
@OUTPUT_FILE_OPTION
@INPUT_FILE_OPTION
def ca_cleanup_for_import(ctx: click.Context, input_file: str, output_file: str):
    ctx.ensure_object(dict)
    click.secho("Cleaning up conditional access policies for import...", fg="yellow")

    input_file = get_from_ctx_if_none(
        ctx, "output_file", input_file, lambda: click.prompt("The input file")
    )
    output_file = get_from_ctx_if_none(
        ctx, "output_file", output_file, lambda: click.prompt("The output file")
    )

    policies = _load_policies(input_file)
    policies = _ca_policies_cleanup_for_import(policies)
    _save_policies(policies=policies, output_file=output_file)

    # store the output file in the context for chaining commands
    ctx.obj["output_file"] = output_file


@click.command("ca-import", help="Import conditional access policies")
@click.pass_context
@ACCESS_TOKEN_OPTION
@INPUT_FILE_OPTION
def ca_import(ctx: click.Context, input_file: str, access_token: str | None = None):
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
    policies = _ca_policies_cleanup_for_import(policies)
    policies = _names_to_ids_mapping(access_token, policies)
    policies_api = PoliciesAPI(access_token=access_token)

    for policy in policies:
        click.echo(f'Creating policy {policy["displayName"]}...')
        _logger.debug(f"Policy: {policy}")
        response = policies_api.create(policy)
        if response.success:
            click.echo("Policy created successfully")
        else:
            click.secho(
                f"Something went wrong while creating the policy: {response.status_code}",
                fg="red",
            )
            click.secho(response.json(), fg="red")
