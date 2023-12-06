# import griffe.docstrings.dataclasses as ds
from typing import Union

import griffe.dataclasses as dc
import griffe.docstrings.dataclasses as ds
import griffe.expressions as exp
from _renderer import Renderer
from plum import dispatch
from quartodoc import MdRenderer, get_object, preview
from quartodoc.renderers.base import convert_rst_link_to_md, sanitize

from shiny import reactive, render, ui

# from quartodoc import Auto, blueprint, get_object, layout
# from quartodoc.renderers import MdRenderer

# package = "quartodoc.tests.example_docstring_styles"
# auto = Auto(name=f"f_{parser}", package=package)
# bp = blueprint(auto, parser=parser)
# res = renderer.render(bp)


# renderer = MdRenderer()

# obj = get_object("shiny.ui.input_action_button")
# # preview(obj)
# preview(obj.parameters)


class BarretFnSig(Renderer):
    style = "custom_greg_styles"

    # def __init__(self, header_level: int = 1):
    #     self.header_level = header_level

    # @dispatch
    # def render(self, el):
    #     raise NotImplementedError(f"Unsupported type: {type(el)}")

    @dispatch
    def render(self, el: Union[dc.Alias, dc.Object]):
        # preview(el)
        param_str = ""
        if hasattr(el, "docstring") and hasattr(el.docstring, "parsed"):
            for docstring_val in el.docstring.parsed:
                if isinstance(docstring_val, ds.DocstringSectionParameters):
                    param_str = self.render(docstring_val)
        elif hasattr(el, "parameters"):
            for param in el.parameters:
                param_str += self.render(param)
        return f"{el.name}({param_str})"
        # return f"{el.name}({self.render(el.parameters)})"
        # return self.render_annotation(el.annotation)
        # # header = "#" * self.header_level
        # # str_header = f"{header} {el.name}"
        # str_header = f"## {el.name}"
        # str_params = f"N PARAMETERS: {len(el.parameters)}"
        # str_sections = "SECTIONS: " + self.render(el.docstring)

        # # return something pretty
        # return "\n".join([str_header, str_params, str_sections])

    # Consolidate the parameter type info into a single column
    @dispatch
    def render(self, el: None):
        return "None"

    @dispatch
    def render_annotation(self, el: exp.ExprName):
        # print("exp.ExprName")
        # preview(el)
        return el.path
        return f"[{el.path}](`{el.canonical_path}`)"

    @dispatch
    def render_annotation(self, el: exp.ExprSubscript):
        # print("exp.ExprSubscript")
        # preview(el)
        return el.path
        return f"[{el.path}](`{el.canonical_path}`)"

    @dispatch
    def render(self, el: ds.DocstringParameter):
        # print("ds.DocstringParameter")
        # preview(el)

        param = self.render(el.name)
        # annotation = self.render_annotation(el.annotation)
        # if annotation:
        #     param = f"{param}: {annotation}"
        if el.default:
            return None
        # if el.default:
        #     param = f"{param} = {el.default}"
        return param

    @dispatch
    def render(self, el: ds.DocstringSectionParameters):
        # print("ds.DocstringSectionParameters")
        # preview(el)
        return ", ".join(
            [item for item in map(self.render, el.value) if item is not None]
        )
        # rows = list(map(self.render, el.value))
        # header = ["Parameter", "Description"]

        # return self._render_table(rows, header)

    # @dispatch
    # def render(self, el: dc.Docstring):
    #     return f"A docstring with {len(el.parsed)} pieces"


# TODO-barret; Add sentance in template to describe what the Relevant Function section is: "To learn more about details about the functions covered here, visit the reference links below."
# print(BarretFnSig().render(get_object("shiny:ui.input_action_button")))
# print(BarretFnSig().render(get_object("shiny:ui.input_action_button")))
# preview(get_object("shiny:ui"))
# print("")


ret = {}
for mod_name, mod in [
    ("ui", ui),
    ("render", render),
    ("reactive", reactive),
]:
    ret[mod_name] = {}
    for key, f_obj in mod.__dict__.items():
        if key.startswith("_") or key in ("AnimationOptions",):
            continue
        if not callable(f_obj):
            continue
        print(f"## {mod_name}.{key}")
        signature = BarretFnSig().render(get_object(f"shiny:{mod_name}.{key}"))
        ret[mod_name][key] = signature
preview(ret)

# TODO-barret; Include link to GitHub source
# print(BarretFnSig().render(f_obj.annotation))
# print(preview(f_obj))

# # get annotation of first parameter
# obj.parameters[0].annotation

# render annotation
# print(renderer.render_annotation(obj.parameters[0].annotation))
