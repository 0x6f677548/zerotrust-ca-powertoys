import click
from ca_pwt.commands import (
    export_policies_cmd,
    import_policies_cmd,
    replace_values_by_keys_cmd,
    cleanup_policies_cmd,
    replace_keys_by_values_cmd,
    acquire_token_cmd,
    export_groups_cmd,
    import_groups_cmd,
    cleanup_groups_cmd,
    _access_token_option,
)


@click.group(
    name="CA-PowerToys",
    chain=True,
    help="A set of tools to help manage Conditional Access policies in Entra ID",
)
@click.option(
    "--log_level",
    default="WARNING",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]),
    help="The log level to use for logging (default: INFO). Possible values: DEBUG, INFO, WARNING, ERROR, CRITICAL",
)
@_access_token_option
@click.pass_context
def cli(ctx: click.Context, access_token: str, log_level: str):
    ctx.ensure_object(dict)
    # persist the access token in the context for use in subcommands
    ctx.obj["access_token"] = access_token

    import logging

    logging.basicConfig(level=log_level)
    pass


cli.add_command(acquire_token_cmd)
cli.add_command(import_policies_cmd)
cli.add_command(export_policies_cmd)
cli.add_command(replace_values_by_keys_cmd)
cli.add_command(cleanup_policies_cmd)
cli.add_command(replace_keys_by_values_cmd)
cli.add_command(export_groups_cmd)
cli.add_command(import_groups_cmd)
cli.add_command(cleanup_groups_cmd)


def entrypoint():
    cli(obj={})


if __name__ == "__main__":
    entrypoint()
