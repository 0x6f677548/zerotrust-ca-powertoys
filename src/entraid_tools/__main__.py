import click
from .conditional_access.commands import (
    ca_export,
    ca_import,
    ca_names_to_ids,
    ca_cleanup_for_import,
    ca_ids_to_names
)
from .authentication import get_access_token, ACCESS_TOKEN_OPTION


@click.group(
    name="entraid-tools",
    chain=True,
    help="A set of tools to help manage your Entra ID environment",
)
@click.option(
    "--log_level",
    default="CRITICAL",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]),
    help="The log level to use for logging (default: INFO). Possible values: DEBUG, INFO, WARNING, ERROR, CRITICAL",
)
@ACCESS_TOKEN_OPTION
@click.pass_context
def cli(ctx: click.Context, access_token: str, log_level: str):
    ctx.ensure_object(dict)
    # persist the access token in the context for use in subcommands
    ctx.obj["access_token"] = access_token

    import logging
    logging.basicConfig(level=log_level)
    pass


cli.add_command(get_access_token)
cli.add_command(ca_import)
cli.add_command(ca_export)
cli.add_command(ca_names_to_ids)
cli.add_command(ca_cleanup_for_import)
cli.add_command(ca_ids_to_names)

if __name__ == "__main__":
    cli(obj={})
