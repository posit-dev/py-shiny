from __future__ import annotations

import ast
from typing import Any, Dict, List, Set


class ShinyCodeValidator(ast.NodeVisitor):
    def __init__(self) -> None:
        self.mode = "unknown"
        self.errors: List[Dict[str, Any]] = []
        self.warnings: List[Dict[str, Any]] = []
        self.suggestions: List[str] = []
        self.input_ids: Set[str] = set()
        self.output_ids: Set[str] = set()
        self.reactive_vals: Set[str] = set()
        self.reactive_calcs: Set[str] = set()
        self.duplicate_ids: List[str] = []

        self._in_server_func = False
        self._in_reactive_context = False
        self._current_func_decorators: List[str] = []
        self._parent_map: Dict[ast.AST, ast.AST] = {}

    def generic_visit(self, node: ast.AST) -> None:
        for child in ast.iter_child_nodes(node):
            self._parent_map[child] = node
        super().generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            if "shiny.express" in alias.name:
                self.mode = "express"
            if alias.name in ("shinyApp", "fluidPage", "shinyServer"):
                self.errors.append(
                    {
                        "line": node.lineno,
                        "message": f"R Shiny idiom detected: '{alias.name}'. Use Python Shiny conventions instead.",
                        "code": "R_SHINY_IDIOM",
                    }
                )
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        module = node.module or ""
        if "shiny.express" in module:
            self.mode = "express"
        for alias in node.names:
            if module == "shiny" and alias.name in (
                "shinyApp",
                "fluidPage",
                "reactiveVal",
                "observeEvent",
            ):
                self.errors.append(
                    {
                        "line": node.lineno,
                        "message": f"R Shiny idiom detected: '{alias.name}'. Use 'shiny.reactive' or 'shiny.ui' equivalents.",
                        "code": "R_SHINY_IDIOM",
                    }
                )
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        decorators = [self._get_decorator_name(d) for d in node.decorator_list]
        prev_in_server = self._in_server_func
        prev_in_reactive = self._in_reactive_context
        prev_decorators = self._current_func_decorators

        self._current_func_decorators = decorators

        if node.name == "server" and len(node.args.args) >= 2:
            self._in_server_func = True
            if self.mode == "unknown":
                self.mode = "core"

        is_renderer = any(
            d.startswith("render.") or d.startswith("render_") for d in decorators
        )
        is_calc = any(
            d
            in (
                "reactive.calc",
                "reactive.Calc",
                "reactive.event",
                "reactive.effect",
                "reactive.Effect",
            )
            for d in decorators
        )

        if is_renderer:
            self.output_ids.add(node.name)
            self._in_reactive_context = True
        elif is_calc:
            self.reactive_calcs.add(node.name)
            self._in_reactive_context = True

        render_count = sum(
            1 for d in decorators if d.startswith("render.") or d.startswith("render_")
        )
        if render_count > 1:
            self.errors.append(
                {
                    "line": node.lineno,
                    "message": f"Function '{node.name}' has multiple render decorators. Only one renderer is allowed per output.",
                    "code": "MULTIPLE_RENDERERS",
                }
            )

        self.generic_visit(node)

        self._in_server_func = prev_in_server
        self._in_reactive_context = prev_in_reactive
        self._current_func_decorators = prev_decorators

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        fn_node = ast.FunctionDef(
            name=node.name,
            args=node.args,
            body=node.body,
            decorator_list=node.decorator_list,
            returns=node.returns,
            type_comment=node.type_comment,
            lineno=node.lineno,
            col_offset=node.col_offset,
        )
        self.visit_FunctionDef(fn_node)

    def visit_Call(self, node: ast.Call) -> None:
        call_name = self._get_call_name(node.func)

        if call_name and (
            call_name.startswith("ui.input_")
            or call_name.startswith("ui.output_")
            or call_name.startswith("shinychat.chat_ui")
            or call_name.startswith("shinywidgets.output_widget")
        ):
            if (
                node.args
                and isinstance(node.args[0], ast.Constant)
                and isinstance(node.args[0].value, str)
            ):
                widget_id = node.args[0].value
                if call_name.startswith("ui.input_"):
                    if widget_id in self.input_ids:
                        self.duplicate_ids.append(widget_id)
                        self.warnings.append(
                            {
                                "line": node.lineno,
                                "message": f"Duplicate input ID detected: '{widget_id}'. Input IDs must be unique.",
                                "code": "DUPLICATE_ID",
                            }
                        )
                    self.input_ids.add(widget_id)
                elif call_name.startswith("ui.output_") or call_name.startswith(
                    "shinywidgets.output_widget"
                ):
                    if widget_id in self.output_ids:
                        self.duplicate_ids.append(widget_id)
                        self.warnings.append(
                            {
                                "line": node.lineno,
                                "message": f"Duplicate output ID detected: '{widget_id}'. Output IDs must be unique.",
                                "code": "DUPLICATE_ID",
                            }
                        )
                    self.output_ids.add(widget_id)

        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        for target in node.targets:
            if isinstance(target, ast.Attribute):
                if isinstance(target.value, ast.Name) and target.value.id == "input":
                    self.errors.append(
                        {
                            "line": node.lineno,
                            "message": f"Attempted direct assignment to 'input.{target.attr}'. Inputs are read-only; use reactive.value or update_* functions.",
                            "code": "INPUT_ASSIGNMENT",
                        }
                    )

            if isinstance(node.value, ast.Call):
                call_name = self._get_call_name(node.value.func)
                if call_name in ("reactive.value", "reactive.Value") and isinstance(
                    target, ast.Name
                ):
                    self.reactive_vals.add(target.id)

        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if isinstance(node.value, ast.Name) and node.value.id == "input":
            parent = self._parent_map.get(node)
            is_func_call = isinstance(parent, ast.Call) and parent.func is node
            is_event_arg = False
            if isinstance(parent, ast.Call):
                parent_call_name = self._get_call_name(parent.func)
                if "event" in parent_call_name:
                    is_event_arg = True

            if not is_func_call and not is_event_arg and self._in_reactive_context:
                self.warnings.append(
                    {
                        "line": node.lineno,
                        "message": f"Input 'input.{node.attr}' accessed without parentheses '()'. Inputs are reactive callables in Python.",
                        "code": "UNCALLED_INPUT",
                    }
                )

        self.generic_visit(node)

    def _get_call_name(self, node: ast.AST) -> str:
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            val = self._get_call_name(node.value)
            return f"{val}.{node.attr}" if val else node.attr
        return ""

    def _get_decorator_name(self, node: ast.AST) -> str:
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            val = self._get_decorator_name(node.value)
            return f"{val}.{node.attr}" if val else node.attr
        elif isinstance(node, ast.Call):
            return self._get_decorator_name(node.func)
        return ""


def validate_shiny_code(code: str) -> Dict[str, Any]:
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return {
            "valid": False,
            "mode": "unknown",
            "errors": [
                {
                    "line": e.lineno or 1,
                    "message": f"SyntaxError: {e.msg}",
                    "code": "SYNTAX_ERROR",
                }
            ],
            "warnings": [],
            "suggestions": [
                "Fix Python syntax errors before validating Shiny constructs."
            ],
            "detected_inputs": [],
            "detected_outputs": [],
            "detected_reactives": [],
        }

    validator = ShinyCodeValidator()
    validator.visit(tree)

    if validator.mode == "unknown":
        if (
            "from shiny import ui" in code
            or "import shiny.ui" in code
            or "from shiny import render" in code
        ):
            validator.mode = "core"

    suggestions: List[str] = []
    if validator.mode == "express" and validator.duplicate_ids:
        suggestions.append(
            "Ensure each UI component in Express mode has a unique string ID."
        )
    if not validator.errors:
        suggestions.append("Code structure matches Python Shiny best practices.")

    return {
        "valid": len(validator.errors) == 0,
        "mode": validator.mode,
        "errors": validator.errors,
        "warnings": validator.warnings,
        "suggestions": suggestions,
        "detected_inputs": sorted(list(validator.input_ids)),
        "detected_outputs": sorted(list(validator.output_ids)),
        "detected_reactives": sorted(
            list(validator.reactive_vals | validator.reactive_calcs)
        ),
    }
