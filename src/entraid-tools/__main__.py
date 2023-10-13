import click
from conditional_access.commands import (
    ca_export,
    ca_import,
    ca_group_names_to_ids,
    ca_cleanup_for_import,
    ca_group_ids_to_names
)
from authentication import get_access_token
from groups.commands import group_add_user


@click.group(
    name="entraid-tools",
    chain=True,
    help="A set of tools to help manage your Entra ID environment",
)
@click.option(
    "--log_level",
    default="INFO",
    help="The log level to use for logging (default: INFO). Possible values: DEBUG, INFO, WARNING, ERROR, CRITICAL",
)
@click.pass_context
def cli(ctx: click.Context, log_level: str):
    import logging

    logging.basicConfig(level=log_level)
    pass


cli.add_command(get_access_token)
cli.add_command(ca_import)
cli.add_command(ca_export)
cli.add_command(ca_group_names_to_ids)
cli.add_command(ca_cleanup_for_import)
cli.add_command(ca_group_ids_to_names)
cli.add_command(group_add_user)

if __name__ == "__main__":
    cli(obj={})
