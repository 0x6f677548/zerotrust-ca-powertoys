import click
import graph_api.groups
from authentication import get_access_token, ACCESS_TOKEN_OPTION
from utils import get_from_ctx_if_none


@click.command("add-user-to-group", help="Add a user to a group")
@click.option("--user_id", help="The user id to add to the group", required=True)
@click.option("--group_id", help="The group id to add the user to", required=True)
@ACCESS_TOKEN_OPTION
@click.pass_context
def add_user_to_group(
    ctx: click.Context, user_id: str, group_id: str, access_token: str | None = None
):
    """Add a user to a group."""
    access_token = get_from_ctx_if_none(
        ctx, "access_token", access_token, get_access_token
    )

    result = graph_api.groups.add_user_to_group(access_token, user_id, group_id)
    click.echo(result)
