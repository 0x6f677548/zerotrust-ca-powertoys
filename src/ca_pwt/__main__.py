import click
from .conditional_access.commands import (
    export_policies,
    import_policies,
    replace_values_by_keys,
    cleanup_policies,
    replace_keys_by_values,
)
from .authentication import get_access_token, ACCESS_TOKEN_OPTION


@click.group(
    name="CA-PowerToys",
    chain=True,
    help="A set of tools to help manage Conditional Access policies in Entra ID",
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
cli.add_command(import_policies)
cli.add_command(export_policies)
cli.add_command(replace_values_by_keys)
cli.add_command(cleanup_policies)
cli.add_command(replace_keys_by_values)

if __name__ == "__main__":
    cli(obj={})
