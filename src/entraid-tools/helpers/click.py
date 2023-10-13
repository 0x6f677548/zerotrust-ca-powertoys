from typing import Callable
import click


def get_from_ctx_if_none(
    ctx: click.Context,
    ctx_key: str,
    value: str | None = None,
    invoke_func: Callable = None,
) -> str:
    """Get a value from the context if it is not None,
    otherwise invoke a function to get the value."""
    ctx.ensure_object(dict)
    if value is not None:
        return value
    elif ctx_key in ctx.obj:
        return ctx.obj[ctx_key]
    else:
        result = ctx.invoke(invoke_func)
        return result
