from typing import Callable
import click
from sys import exit
import logging

_logger = logging.getLogger(__name__)


def get_from_ctx_if_none(
    ctx: click.Context,
    ctx_key: str,
    value: str | None = None,
    invoke_func: Callable | None = None,
) -> str:
    """Get a value from the context if it is None,
    otherwise invoke a function to get the value."""
    ctx.ensure_object(dict)
    if value:
        return value
    elif ctx_key in ctx.obj and ctx.obj[ctx_key]:
        return ctx.obj[ctx_key]
    else:
        result = ctx.invoke(invoke_func)
        return result


def exit_with_exception(exception: Exception, exit_code: int = 1, fg: str = "red"):
    """Exit the program with an exception and exit code"""
    try:
        _logger.exception(exception)
        click.secho(
            "An error occurred. See the log for more details. (--log_level ERROR). Exiting... "
            + f"(Exception Type: {type(exception).__name__}); (Exception: {exception})",
            fg=fg,
        )
    finally:
        exit(exit_code)
