from __future__ import annotations

import ast
import re
import tokenize
from dataclasses import dataclass, field
from io import StringIO
from pathlib import Path
from typing import Literal, TypedDict


class ValidationIssue(TypedDict):
    line: int
    message: str
    code: str


class ValidationReport(TypedDict):
    valid: bool
    mode: str
    errors: list[ValidationIssue]
    warnings: list[ValidationIssue]
    suggestions: list[str]
    detected_inputs: list[str]
    detected_outputs: list[str]
    detected_reactives: list[str]


@dataclass
class ValidateResult:
    """Validation diagnostics and detected structure, with a serializable report."""

    mode: Literal["unknown", "core", "express"] = "unknown"
    errors: list[ValidationIssue] = field(default_factory=list[ValidationIssue])
    warnings: list[ValidationIssue] = field(default_factory=list[ValidationIssue])
    suggestions: list[str] = field(default_factory=list[str])
    input_ids: set[str] = field(default_factory=set[str])
    ui_output_ids: set[str] = field(default_factory=set[str])
    renderer_ids: set[str] = field(default_factory=set[str])
    reactive_vals: set[str] = field(default_factory=set[str])
    reactive_calcs: set[str] = field(default_factory=set[str])
    duplicate_ids: list[str] = field(default_factory=list[str])

    @property
    def valid(self) -> bool:
        return not self.errors and not self.warnings

    def add_error(self, line: int, message: str, code: str) -> None:
        self.errors.append({"line": line, "message": message, "code": code})

    def add_warning(self, line: int, message: str, code: str) -> None:
        self.warnings.append({"line": line, "message": message, "code": code})

    @property
    def detected_inputs(self) -> list[str]:
        return sorted(self.input_ids)

    @property
    def detected_outputs(self) -> list[str]:
        return sorted(self.ui_output_ids | self.renderer_ids)

    @property
    def detected_reactives(self) -> list[str]:
        return sorted(self.reactive_vals | self.reactive_calcs)

    def register_id(
        self, kind: Literal["input", "output", "renderer"], value: str, line: int
    ) -> None:
        ids = {
            "input": self.input_ids,
            "output": self.ui_output_ids,
            "renderer": self.renderer_ids,
        }[kind]
        if value in ids:
            self.duplicate_ids.append(value)
            message = (
                f"Duplicate renderer function name detected: '{value}'."
                if kind == "renderer"
                else f"Duplicate {kind} ID detected: '{value}'. {kind.title()} IDs must be unique."
            )
            self.add_warning(line, message, "DUPLICATE_ID")
        ids.add(value)

    def to_dict(self) -> ValidationReport:
        return {
            "valid": self.valid,
            "mode": self.mode,
            "errors": self.errors.copy(),
            "warnings": self.warnings.copy(),
            "suggestions": self.suggestions.copy(),
            "detected_inputs": self.detected_inputs,
            "detected_outputs": self.detected_outputs,
            "detected_reactives": self.detected_reactives,
        }


class ShinyCodeValidator(ast.NodeVisitor):
    """Subclass visitor methods and add project rules to ``self.result``.

    Pass the subclass as ``validator_class`` to the validation helpers. Call the
    superclass visitor method to retain built-in rules and child traversal.
    """

    def __init__(self) -> None:
        self.result = ValidateResult()

        self._in_server_func = False
        self._in_reactive_context = False
        self._current_func_decorators: list[str] = []
        self._parent_map: dict[ast.AST, ast.AST] = {}

    def generic_visit(self, node: ast.AST) -> None:
        for child in ast.iter_child_nodes(node):
            self._parent_map[child] = node
        super().generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            if alias.name == "shiny" or alias.name.startswith("shiny."):
                if self.result.mode == "unknown":
                    self.result.mode = "core"
            if "shiny.express" in alias.name:
                self.result.mode = "express"
            if alias.name in ("shinyApp", "fluidPage", "shinyServer"):
                self.result.errors.append(
                    {
                        "line": node.lineno,
                        "message": f"R Shiny idiom detected: '{alias.name}'. Use Python Shiny conventions instead.",
                        "code": "R_SHINY_IDIOM",
                    }
                )
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        module = node.module or ""
        if module == "shiny" or module.startswith("shiny."):
            if self.result.mode == "unknown":
                self.result.mode = "core"
        if "shiny.express" in module:
            self.result.mode = "express"
        for alias in node.names:
            if module == "shiny" and alias.name in (
                "shinyApp",
                "fluidPage",
                "reactiveVal",
                "observeEvent",
            ):
                self.result.errors.append(
                    {
                        "line": node.lineno,
                        "message": f"R Shiny idiom detected: '{alias.name}'. Use 'shiny.reactive' or 'shiny.ui' equivalents.",
                        "code": "R_SHINY_IDIOM",
                    }
                )
        self.generic_visit(node)

    def _check_func_def(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        decorators = [self._get_decorator_name(d) for d in node.decorator_list]
        prev_in_server = self._in_server_func
        prev_in_reactive = self._in_reactive_context
        prev_decorators = self._current_func_decorators

        self._current_func_decorators = decorators

        if node.name == "server" and len(node.args.args) >= 2:
            self._in_server_func = True
            if self.result.mode == "unknown":
                self.result.mode = "core"

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
            self.result.register_id("renderer", node.name, node.lineno)
            self._in_reactive_context = True
        elif is_calc:
            self.result.reactive_calcs.add(node.name)
            self._in_reactive_context = True

        render_count = sum(
            1 for d in decorators if d.startswith("render.") or d.startswith("render_")
        )
        if render_count > 1:
            self.result.errors.append(
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

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._check_func_def(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._check_func_def(node)

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
                    self.result.register_id("input", widget_id, node.lineno)
                elif call_name.startswith("ui.output_") or call_name.startswith(
                    "shinywidgets.output_widget"
                ):
                    self.result.register_id("output", widget_id, node.lineno)

        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        for target in node.targets:
            if isinstance(target, ast.Attribute):
                if isinstance(target.value, ast.Name) and target.value.id == "input":
                    self.result.errors.append(
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
                    self.result.reactive_vals.add(target.id)

        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if (
            isinstance(node.value, ast.Name)
            and node.value.id == "input"
            and not isinstance(node.ctx, ast.Store)
        ):
            parent = self._parent_map.get(node)
            is_func_call = isinstance(parent, ast.Call) and parent.func is node
            is_event_arg = False
            if isinstance(parent, ast.Call):
                parent_call_name = self._get_call_name(parent.func)
                if "event" in parent_call_name:
                    is_event_arg = True

            if not is_func_call and not is_event_arg and self._in_reactive_context:
                self.result.warnings.append(
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


def _apply_suppressions(code: str, result: ValidateResult) -> None:
    suppressed: dict[int, set[str] | None] = {}
    for token in tokenize.generate_tokens(StringIO(code).readline):
        if token.type != tokenize.COMMENT:
            continue
        match = re.fullmatch(
            r"\#\s*shiny:\s*(ignore-next-line|ignore)(?:\s+([\w., \t]+))?\s*",
            token.string,
        )
        if not match:
            continue
        line = token.start[0] + (match[1] == "ignore-next-line")
        rules = {rule for rule in re.split(r"[,\s]+", (match[2] or "").strip()) if rule}
        if line not in suppressed:
            suppressed[line] = rules or None
        elif not rules or suppressed[line] is None:
            suppressed[line] = None
        else:
            existing = suppressed[line]
            if existing is not None:
                existing.update(rules)

    def keep(issue: ValidationIssue) -> bool:
        if issue["line"] not in suppressed:
            return True
        rules = suppressed[issue["line"]]
        return rules is not None and issue["code"] not in rules

    result.errors = [issue for issue in result.errors if keep(issue)]
    result.warnings = [issue for issue in result.warnings if keep(issue)]


def validate_shiny_code(
    code: str, *, validator_class: type[ShinyCodeValidator] = ShinyCodeValidator
) -> ValidateResult:
    """Validate source, optionally using a subclass with project rules.

    ``# shiny: ignore [CODE, ...]`` suppresses diagnostics on the current line.
    ``# shiny: ignore-next-line [CODE, ...]`` suppresses the following line.
    Omitting codes suppresses all validation rules on that line. Syntax errors
    cannot be suppressed. These directives also work in the Shiny extension.
    """
    validator = validator_class()
    result = validator.result
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        result.add_error(e.lineno or 1, f"SyntaxError: {e.msg}", "SYNTAX_ERROR")
        result.suggestions.append(
            "Fix Python syntax errors before validating Shiny constructs."
        )
        return result

    validator.visit(tree)
    _apply_suppressions(code, result)
    if (
        result.mode == "express"
        and result.duplicate_ids
        and any(issue["code"] == "DUPLICATE_ID" for issue in result.warnings)
    ):
        result.suggestions.append(
            "Ensure each UI component in Express mode has a unique string ID."
        )
    if result.valid:
        result.suggestions.append("Code structure matches Python Shiny best practices.")
    return result


def validate_shiny_file(
    path: str | Path, *, validator_class: type[ShinyCodeValidator] = ShinyCodeValidator
) -> ValidateResult:
    """Validate a UTF-8 file with built-in or project-specific validation rules."""
    p = Path(path)
    if not p.is_file():
        result = ValidateResult()
        result.add_error(1, f"File not found: {path}", "FILE_NOT_FOUND")
        return result
    return validate_shiny_code(
        p.read_text(encoding="utf-8"), validator_class=validator_class
    )
