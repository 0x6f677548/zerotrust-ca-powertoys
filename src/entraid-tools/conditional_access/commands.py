import click
import logging
from helpers.dict import remove_element_from_dict, replace_with_key_value_lookup
from helpers.click import get_from_ctx_if_none
from .graph_api import get_policies, create_policy
from groups.graph_api import get_group_id_by_name, get_group_name_by_id
from authentication import get_access_token, ACCESS_TOKEN_OPTION

_logger = logging.getLogger(__name__)


def _cleanup_policies(source: dict) -> dict:
    remove_element_from_dict(source, "@odata.context")

    # remove the value element and replace it with the policies list
    if "value" in source:
        source["policies"] = source["value"]
        source.pop("value")
    elif "policies" not in source:
        raise Exception(
            "The policies file does not contain a value or policies element"
        )

    # exclude some elements, namely createdDateTime,
    # modifiedDateTime, id, templateId, authenticationStrength@odata.context
    for policy in source["policies"]:
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


def _cleanup_for_create(access_token: str, source: dict) -> dict:
    source = _cleanup_policies(source)
    for policy in source["policies"]:
        # now let's transform groupIds to groupNames if any
        conditions = policy["conditions"]
        users = conditions["users"]
        known_groups = replace_with_key_value_lookup(
            parent_node=users,
            keys_node_name="excludeGroupNames",
            values_node_name="excludeGroups",
            lookup_func=lambda name: get_group_id_by_name(access_token, name)
        )
        known_groups = replace_with_key_value_lookup(
            parent_node=users,
            values_node_name="includeGroupNames",
            keys_node_name="includeGroups",
            lookup_func=lambda name: get_group_id_by_name(access_token, name),
            lookup_cache=known_groups,
        )

    return source


def _cleanup_for_store(access_token: str, source: dict) -> dict:
    source = _cleanup_policies(source)
    lookup_cache = {}
    for policy in source["policies"]:
        # now let's transform groupIds to groupNames if any
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
            values_node_name="includeGroupNames",
            keys_node_name="includeGroups",
            lookup_func=lambda id: get_group_name_by_id(access_token, id),
            lookup_cache=lookup_cache,
        )

    return source


def _export_ca_policies(
    output_file: str,
    access_token: str,
):
    # token = get_access_token(tenant_id, client_id, client_secret)
    click.echo("Exporting policies...")
    policies = get_policies(access_token)
    click.echo("Policies exported successfully. Cleaning up policies...")
    policies = _cleanup_for_store(access_token, policies)
    click.echo("Policies cleaned up successfully. Writing policies to file...")
    import json

    with open(output_file, "w") as f:
        f.write(json.dumps(policies, indent=4))


def _import_ca_policies(
    input_file: str,
    access_token: str,
):
    click.echo("Importing policies...")
    _logger.debug("Creating policy...")

    import json

    with open(input_file, "r") as f:
        policies = json.load(f)

        click.echo("Cleaning up policies...")
        # make sure the policies are cleaned up
        policies = _cleanup_for_create(access_token, policies)
        for policy in policies["policies"]:
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


def _get_access_token(ctx: click.Context, access_token: str | None = None) -> str:
    ctx.ensure_object(dict)
    if access_token is not None:
        _logger.debug(f"Using access token {access_token}")
        return access_token
    elif "access_token" in ctx.obj:
        _logger.debug(f"Using access token {ctx.obj['access_token']}")
        return ctx.obj["access_token"]
    else:
        _logger.debug("No access token found in context. Invoking get_access_token...")
        result = ctx.invoke(get_access_token)
        _logger.debug(f"Access token is {result}")
        return result


@click.command("export-ca-policies", help="Export conditional access policies")
@click.pass_context
@ACCESS_TOKEN_OPTION
@click.option(
    "--output_file",
    prompt="The output file",
    help="The file to write the policies to",
    default="policies.json",
)
def export_ca_policies(
    ctx: click.Context, output_file: str, access_token: str | None = None
):
    access_token = get_from_ctx_if_none(
        ctx, "access_token", access_token, get_access_token
    )
    _export_ca_policies(output_file=output_file, access_token=access_token)


@click.command("import-ca-policies", help="Import conditional access policies")
@click.pass_context
@ACCESS_TOKEN_OPTION
@click.option(
    "--input_file",
    prompt="The input file",
    help="The file to read the policies from",
    default="policies.json",
)
def import_ca_policies(
    ctx: click.Context, input_file: str, access_token: str | None = None
):
    access_token = get_from_ctx_if_none(
        ctx, "access_token", access_token, get_access_token
    )
    _import_ca_policies(input_file=input_file, access_token=access_token)
