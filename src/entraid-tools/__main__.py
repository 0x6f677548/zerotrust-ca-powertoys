import click
import logging
from conditional_access import (
    export_ca_policies,
    import_ca_policies,
)
from authentication import get_access_token
from groups import add_user_to_group


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
    logging.basicConfig(level=log_level)
    pass


cli.add_command(get_access_token)
cli.add_command(import_ca_policies)
cli.add_command(export_ca_policies)
cli.add_command(add_user_to_group)

if __name__ == "__main__":
    cli(obj={})
