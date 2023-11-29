from __future__ import annotations

# pyright: reportUnknownVariableType=false, reportUnknownMemberType=false, reportUntypedFunctionDecorator=false
import asyncio
from contextlib import contextmanager
from typing import cast

from IPython.core.getipython import get_ipython
from IPython.core.interactiveshell import InteractiveShell
from IPython.core.magic import register_cell_magic
from IPython.core.magic_arguments import argument, magic_arguments, parse_argstring
from IPython.display import clear_output

from shiny import reactive as shiny_reactive
from shiny import ui

from .log import logger

NumberType = int | float
InputTypes = None | str | NumberType | bool | list[str] | tuple[NumberType, NumberType]


def inputs(**kwargs: InputTypes):
    return ui.div(*[make_input(k, v) for k, v in kwargs.items()])


def make_input(name: str, value: InputTypes, *, label: str | None = None):
    if label is None:
        label = name

    # bool must be before int, it is one!?
    if value is None:
        return ui.input_action_button(name, label, class_="btn-primary")
    if isinstance(value, bool):
        return ui.input_switch(name, label, value)
    elif isinstance(value, str):
        return ui.input_text(name, label, value)
    elif isinstance(value, (int, float)):
        return ui.input_numeric(name, label, value)
    elif isinstance(value, list):
        return ui.input_select(name, label, value, selected=value[0])
    elif isinstance(value, tuple):
        if len(value) == 2:
            return ui.input_slider(name, label, value[0], value[1], value[0])
        elif len(value) == 3:
            return ui.input_slider(name, label, value[0], value[1], value[2])
        else:
            raise TypeError(
                f"Tuple must have 2 or 3 elements, got {len(value)} elements"
            )
    else:
        raise TypeError(f"Unsupported type {type(value)}")


@magic_arguments()
@argument("name", type=str, nargs="?", help="Name of the reactive calc")
@argument(
    "--no-echo",
    action="store_const",
    const=True,
    dest="no_echo",
    help="Don't display result",
)
@register_cell_magic
def reactive(line: str, cell: str):
    args = parse_argstring(reactive, line)
    reactive_name: str | None = args.name

    # TODO: If line/cell magics are still in the cell, error.

    if get_ipython() is None:
        raise RuntimeError("ipython not found")

    ipy = cast(InteractiveShell, get_ipython())

    # This basically captures a reference to "the cell that's executing us" while we're
    # still in the main IPython event loop. We need to re-install this whenever we
    # re-execute, so that a reactive's output always goes to its originating cell.
    parent_msg = ipy.kernel.get_parent()

    @shiny_reactive.Calc
    def calc():
        # Temporarily install the parent message so that the cell's output goes to the
        # right place.
        with set_parent(ipy.kernel.shell, parent_msg):
            clear_output(wait=True)
            res = ipy.run_cell(cell)

        if reactive_name is not None:
            # The output of the cell would've been displayed by now. The purpose of the rest
            # of this is in case the magic was given a name, so that other code can consume
            # the return value.
            if res.success:
                return res.result
            else:
                if res.error_before_exec:
                    raise res.error_before_exec
                if res.error_in_exec:
                    raise res.error_in_exec

    if reactive_name is not None:
        ipy.push({reactive_name: calc})

    @shiny_reactive.Effect
    def _():
        # TODO: destroy this reactive if this cell is ever re-executed
        try:
            calc()
        except Exception as e:
            # TODO: Where to log!?!?
            logger.exception(e)

    async def flush():
        async with shiny_reactive.lock():
            await shiny_reactive.flush()

    asyncio.create_task(flush())


@contextmanager
def set_parent(shell, parent_msg):
    old_parent = shell.get_parent()
    shell.set_parent(parent_msg)
    try:
        yield
    finally:
        shell.set_parent(old_parent)
