import click
from ca_pwt.commands import (
    export_policies_cmd,
    import_policies_cmd,
    replace_attrs_with_guids_cmd,
    cleanup_policies_cmd,
    replace_guids_with_attrs_cmd,
    acquire_token_cmd,
    export_policy_groups_cmd,
    import_groups_cmd,
    cleanup_groups_cmd,
    delete_groups_cmd,
    delete_policies_cmd,
    _access_token_option,
)


@click.group(
    name="CA-PowerToys",
    chain=True,
    help="A set of tools designed to streamline the management of Conditional Access policies in Entra ID. "
    "These tools specialize in importing and exporting CA policies and groups, optimizing files for human and machine "
    "readability as needed. Additionally, they facilitate the removal of extraneous attributes for smoother "
    "editing workflows, and facilitate a devops-like workflow for managing CA policies.",
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
cli.add_command(replace_attrs_with_guids_cmd)
cli.add_command(cleanup_policies_cmd)
cli.add_command(replace_guids_with_attrs_cmd)
cli.add_command(export_policy_groups_cmd)
cli.add_command(import_groups_cmd)
cli.add_command(cleanup_groups_cmd)
cli.add_command(delete_groups_cmd)
cli.add_command(delete_policies_cmd)


def entrypoint():
    cli(obj={})


if __name__ == "__main__":
    entrypoint()
