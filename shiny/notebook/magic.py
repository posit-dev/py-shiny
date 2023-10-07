# pyright: reportUnknownVariableType=false, reportUnknownMemberType=false, reportUntypedFunctionDecorator=false
import asyncio
import uuid

from IPython.core.getipython import get_ipython
from IPython.core.magic import register_cell_magic
from IPython.core.magic_arguments import argument, magic_arguments, parse_argstring
from IPython.display import HTML, clear_output


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
    clear_output()

    args = parse_argstring(reactive, line)
    reactive_name = args.name or f"__anonymous_{uuid.uuid4().hex}"

    # TODO: If line/cell magics are still in the cell, error.

    # indented = re.sub(r"(^|\r?\n)", r"\1        ", cell)
    ipy = get_ipython()

    from shiny import reactive as shiny_reactive

    @shiny_reactive.Calc
    def calc():
        res = ipy.run_cell(cell)
        if res.success:
            return res.result
        else:
            if execution_result.error_before_exec:
                raise execution_result.error_before_exec
            if execution_result.error_in_exec:
                raise execution_result.error_in_exec

    ipy.push({reactive_name: calc})

    if not args.no_echo:
        display_id = f"__{reactive_name}_output_display__"
        display(HTML(""), display_id=display_id)

        @shiny_reactive.Effect
        def _():
            from IPython.core.display_functions import update_display

            # TODO: Handle errors
            try:
                update_display(calc(), display_id=display_id)
            except Exception as e:
                update_display(e, display_id=display_id)

    async def flush():
        async with shiny_reactive.lock():
            await shiny_reactive.flush()

    asyncio.create_task(flush())


#     code = """
# import ipywidgets as widgets
# from shiny import reactive
# from IPython.core.getipython import get_ipython

# if "__{reactive_name}_output_effect__" in globals():
#     __{reactive_name}_output_effect__.destroy()
# if "__{reactive_name}_output_sink__" in globals():
#     # Output.clear_output() does not work reliably from "threaded" contexts
#     # https://github.com/jupyter-widgets/ipywidgets/issues/3260#issuecomment-907715980
#     __{reactive_name}_output_sink__.outputs = ()

# @reactive.Calc
# def {reactive_name}():
#     res = get_ipython().run_cell('''{cell}''')
#     if res.success:
#         return res.result
#     else:
#         if execution_result.error_before_exec:
#             raise execution_result.error_before_exec
#         if execution_result.error_in_exec:
#             raise execution_result.error_in_exec
# """
#     code += (
#         """
# __{reactive_name}_output_sink__ = widgets.Output()
# @reactive.Effect
# def __{reactive_name}_output_effect__():
#     # Output.clear_output() does not work reliably from "threaded" contexts
#     # https://github.com/jupyter-widgets/ipywidgets/issues/3260#issuecomment-907715980
#     __{reactive_name}_output_sink__.outputs = ()
#     __{reactive_name}_output_sink__.append_display_data({reactive_name}())
# display(__{reactive_name}_output_sink__)
# """
#         if not args.no_echo
#         else ""
#     )

#     code = code.replace("{reactive_name}", reactive_name).replace("{cell}", cell)

#     ipy.run_cell(code)
