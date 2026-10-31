from __future__ import annotations

import ast
import importlib
import os
import re
import sys
import tokenize
from dataclasses import dataclass, field
from importlib.metadata import entry_points
from io import StringIO
from pathlib import Path
from typing import (
    Any,
    Callable,
    Iterator,
    Literal,
    Sequence,
    TypedDict,
    Union,
    cast,
)

from typing_extensions import NotRequired

from ._validate_reactivity import ReactiveUsageValidator

VALIDATOR_ENTRY_POINT_GROUP = "shiny.validators"

_CLEAN_MESSAGE = "No issues found by the enabled static checks."
"""Success wording shared by source validation, file validation, and the CLI."""


class ValidationIssue(TypedDict):
    line: int
    message: str
    code: str
    file: NotRequired[str]


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
    app_outputs: dict[str, int] = field(default_factory=dict[str, int])
    """``ui.output_*`` placeholder IDs outside modules, with the line they appear on."""
    app_renderers: dict[str, int] = field(default_factory=dict[str, int])
    """``@render.*`` output IDs outside modules, with the line they are defined on."""
    app_functions: set[str] = field(default_factory=set[str])
    """Function names (and ``@output(id=)`` IDs) outside modules; custom renderers live here."""
    _seen_ids: set[tuple[str, str, str]] = field(
        default_factory=set[tuple[str, str, str]], repr=False
    )
    _issue_files: dict[str, str] = field(default_factory=dict[str, str], repr=False)
    """Source file per ``app_outputs``/``app_renderers`` key when merged across files."""

    def check_output_pairing(self) -> None:
        """Warn about Core-mode outputs with no renderer and renderers with no output.

        Runs only when both placeholders and renderers were found, so an app
        whose UI or server lives outside the inspected files is not reported.
        Express apps place their renderers directly and are skipped.
        """
        if self.mode != "core" or not self.app_outputs or not self.app_renderers:
            return
        for output_id, line in self.app_outputs.items():
            if (
                output_id not in self.app_renderers
                and output_id not in self.app_functions
            ):
                self._add_pairing_warning(
                    f"output:{output_id}",
                    line,
                    f"UI output '{output_id}' has no matching render function, so it will stay empty. "
                    f"Define '@render.* def {output_id}()' in the server, or remove the placeholder.",
                    "OUTPUT_WITHOUT_RENDERER",
                )
        for output_id, line in self.app_renderers.items():
            if output_id not in self.app_outputs:
                self._add_pairing_warning(
                    f"renderer:{output_id}",
                    line,
                    f"Render function '{output_id}' has no matching 'ui.output_*(\"{output_id}\")' placeholder, "
                    "so it will never be shown.",
                    "RENDERER_WITHOUT_OUTPUT",
                )

    def _add_pairing_warning(
        self, key: str, line: int, message: str, code: str
    ) -> None:
        issue: ValidationIssue = {"line": line, "message": message, "code": code}
        if key in self._issue_files:
            issue["file"] = self._issue_files[key]
        self.warnings.append(issue)

    @property
    def valid(self) -> bool:
        return not self.errors

    @property
    def clean(self) -> bool:
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
        self,
        kind: Literal["input", "output", "renderer"],
        value: str,
        line: int,
        *,
        scope: str = "",
    ) -> None:
        """Record a detected ID; repeated input/output IDs in one ``scope`` warn.

        ``scope`` is the enclosing function (``""`` for module level), so module
        UI functions that reuse the same IDs do not collide with each other.
        Renderer names are recorded for structure detection only: a repeated
        function name is a Python redeclaration that type checkers already report.
        """
        ids = {
            "input": self.input_ids,
            "output": self.ui_output_ids,
            "renderer": self.renderer_ids,
        }[kind]
        if kind != "renderer":
            if (kind, scope, value) in self._seen_ids:
                self.duplicate_ids.append(value)
                self.add_warning(
                    line,
                    f"Duplicate {kind} ID detected: '{value}'. {kind.title()} IDs must be unique.",
                    "DUPLICATE_ID",
                )
            self._seen_ids.add((kind, scope, value))
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

        self._in_reactive_context = False
        self._current_func_decorators: list[str] = []
        self._parent_map: dict[ast.AST, ast.AST] = {}
        self._aliases: dict[str, str] = {}
        self._scope = ""
        """Enclosing function name used to namespace IDs; ``""`` at module level."""
        self._in_module = False
        """Inside a ``@module.ui`` / ``@module.server`` function, whose IDs are namespaced."""

    def generic_visit(self, node: ast.AST) -> None:
        for child in ast.iter_child_nodes(node):
            self._parent_map[child] = node
        super().generic_visit(node)

    def _normalize_name(self, name: str) -> str:
        if not name:
            return ""
        head, sep, tail = name.partition(".")
        if head in self._aliases:
            target = self._aliases[head]
            name = f"{target}.{tail}" if sep else target
        if name.startswith("shiny.express."):
            return name[len("shiny.express.") :]
        if name.startswith("shiny."):
            return name[len("shiny.") :]
        return name

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            if alias.name == "shiny" or alias.name.startswith("shiny."):
                if self.result.mode == "unknown":
                    self.result.mode = "core"
                bound = alias.asname or alias.name.partition(".")[0]
                self._aliases[bound] = alias.name if alias.asname else "shiny"
            if "shiny.express" in alias.name:
                self.result.mode = "express"
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        module = node.module or ""
        if module == "shiny" or module.startswith("shiny."):
            if self.result.mode == "unknown":
                self.result.mode = "core"
        if "shiny.express" in module:
            self.result.mode = "express"
        for alias in node.names:
            if module == "shiny" or module.startswith("shiny."):
                if alias.name != "*":
                    bound = alias.asname or alias.name
                    self._aliases[bound] = f"{module}.{alias.name}"
        self.generic_visit(node)

    def _check_func_def(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        decorators = [
            self._normalize_name(self._get_decorator_name(d))
            for d in node.decorator_list
        ]
        prev_in_reactive = self._in_reactive_context
        prev_decorators = self._current_func_decorators
        prev_scope = self._scope

        self._current_func_decorators = decorators
        self._scope = f"{prev_scope}.{node.name}" if prev_scope else node.name

        if node.name == "server" and len(node.args.args) >= 2:
            if self.result.mode == "unknown":
                self.result.mode = "core"

        is_renderer = any(
            (d.startswith("render.") and not d.startswith("render.transformer."))
            or d.startswith("render_")
            for d in decorators
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

        is_effect = any(d in ("reactive.effect", "reactive.Effect") for d in decorators)
        prev_in_module = self._in_module
        if any(d in ("module.ui", "module.server") for d in decorators):
            self._in_module = True

        if not self._in_module:
            # Any function may back a `ui.output_*()` placeholder through a
            # custom renderer, so names count as candidates for pairing.
            self.result.app_functions.add(node.name)
        if is_renderer:
            output_id = self._output_id(node)
            self.result.register_id("renderer", output_id, node.lineno)
            # Only Shiny's own renderers pair with `ui.output_*()` placeholders;
            # third-party `render_*` decorators have their own UI functions, and
            # a renderer created inside another render function places itself.
            if (
                not self._in_module
                and not prev_in_reactive
                and any(d.startswith("render.") for d in decorators)
            ):
                self.result.app_renderers.setdefault(output_id, node.lineno)
            self._in_reactive_context = True
        elif "output" in decorators and not self._in_module:
            self.result.app_functions.add(self._output_id(node))
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

        self._check_decorator_order(node, decorators)
        if is_effect:
            self._check_effect_return(node)

        self.generic_visit(node)

        self._in_reactive_context = prev_in_reactive
        self._current_func_decorators = prev_decorators
        self._scope = prev_scope
        self._in_module = prev_in_module

    def _output_id(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
        """The output ID a renderer registers under: ``@output(id=...)`` or its name."""
        for decorator in node.decorator_list:
            if (
                isinstance(decorator, ast.Call)
                and self._normalize_name(self._get_decorator_name(decorator))
                == "output"
            ):
                for keyword in decorator.keywords:
                    if (
                        keyword.arg == "id"
                        and isinstance(keyword.value, ast.Constant)
                        and isinstance(keyword.value.value, str)
                    ):
                        return keyword.value.value
        return node.name

    def _check_decorator_order(
        self, node: ast.FunctionDef | ast.AsyncFunctionDef, decorators: list[str]
    ) -> None:
        """``@reactive.event`` must sit below the effect/calc/render decorator it feeds."""
        if "reactive.event" not in decorators:
            return
        event_index = decorators.index("reactive.event")
        for index, name in enumerate(decorators):
            if index > event_index and (
                name.startswith("render.")
                or name
                in (
                    "reactive.effect",
                    "reactive.Effect",
                    "reactive.calc",
                    "reactive.Calc",
                )
            ):
                self.result.add_error(
                    node.lineno,
                    f"'@reactive.event' on '{node.name}' must be placed below '@{name}'. "
                    "Decorators apply bottom-up, so reactive.event has to wrap the plain function "
                    "before the effect, calc, or renderer wraps it.",
                    "DECORATOR_ORDER",
                )
                return

    def _check_effect_return(
        self, node: ast.FunctionDef | ast.AsyncFunctionDef
    ) -> None:
        """A ``reactive.effect`` that returns a value is usually meant to be a calc or renderer."""
        for statement in node.body:
            if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for child in _walk_without_nested_functions(statement):
                if isinstance(child, ast.Return) and child.value is not None:
                    if (
                        isinstance(child.value, ast.Constant)
                        and child.value.value is None
                    ):
                        continue
                    # `return state.set(...)` returns None; a style quirk, not a lost value.
                    if (
                        isinstance(child.value, ast.Call)
                        and isinstance(child.value.func, ast.Attribute)
                        and child.value.func.attr == "set"
                    ):
                        continue
                    self.result.add_warning(
                        child.lineno,
                        f"'{node.name}' is a reactive.effect but returns a value, which is discarded. "
                        "Use @reactive.calc to compute a value or @render.* to show one.",
                        "EFFECT_RETURNS_VALUE",
                    )
                    return

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._check_func_def(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._check_func_def(node)

    def visit_Call(self, node: ast.Call) -> None:
        call_name = self._normalize_name(self._get_call_name(node.func))

        if call_name and (
            call_name.startswith("ui.input_") or call_name.startswith("ui.output_")
        ):
            if (
                node.args
                and isinstance(node.args[0], ast.Constant)
                and isinstance(node.args[0].value, str)
            ):
                kind = "input" if call_name.startswith("ui.input_") else "output"
                self.result.register_id(
                    kind, node.args[0].value, node.lineno, scope=self._scope
                )
                if kind == "output" and not self._in_module:
                    self.result.app_outputs.setdefault(node.args[0].value, node.lineno)
        elif (
            call_name in ("ui.download_button", "ui.download_link")
            and not self._in_module
            and node.args
            and isinstance(node.args[0], ast.Constant)
            and isinstance(node.args[0].value, str)
        ):
            # Pairs with `@render.download`, so count it as an output placeholder.
            self.result.app_outputs.setdefault(node.args[0].value, node.lineno)

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
                call_name = self._normalize_name(self._get_call_name(node.value.func))
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
            is_attr_access = isinstance(parent, ast.Attribute) and parent.value is node
            is_event_arg = False
            if isinstance(parent, ast.Call):
                parent_call_name = self._get_call_name(parent.func)
                if "event" in parent_call_name:
                    is_event_arg = True

            if (
                not is_func_call
                and not is_attr_access
                and not is_event_arg
                and self._in_reactive_context
            ):
                self.result.add_error(
                    node.lineno,
                    f"Input 'input.{node.attr}' accessed without parentheses '()'. Inputs are reactive callables in Python.",
                    "UNCALLED_INPUT",
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


def _walk_without_nested_functions(node: ast.AST) -> Iterator[ast.AST]:
    """Yield ``node`` and its descendants, without entering nested function bodies."""
    yield node
    for child in ast.iter_child_nodes(node):
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
            continue
        yield from _walk_without_nested_functions(child)


class ValidationRule(ast.NodeVisitor):
    """Plugin rule that visits the shared parsed tree and records issues on ``self.result``.

    Register a subclass (or a ``(tree, result) -> None`` callable) under the
    ``shiny.validators`` entry-point group so ``shiny validate`` and ``shiny run``
    load it automatically.
    """

    def __init__(self, result: ValidateResult) -> None:
        self.result = result

    def check(self, tree: ast.Module) -> None:
        self.visit(tree)


ValidationRuleFunc = Callable[[ast.Module, ValidateResult], None]
ValidationRuleLike = Union[type[ValidationRule], ValidationRuleFunc]


def _rule_name(rule: ValidationRuleLike) -> str:
    return getattr(rule, "__qualname__", type(rule).__name__)


def _check_rule(obj: object, name: str) -> ValidationRuleLike:
    if isinstance(obj, type):
        if issubclass(obj, ValidationRule):
            return obj
        raise TypeError(f"'{name}' must subclass shiny.validate.ValidationRule.")
    if callable(obj):
        return cast(ValidationRuleFunc, val=obj)
    raise TypeError(f"'{name}' is not a ValidationRule subclass or callable.")


def _failed_rule(name: str, error: Exception) -> ValidationRuleFunc:
    def rule(tree: ast.Module, result: ValidateResult) -> None:
        raise error

    rule.__qualname__ = name
    return rule


_installed_rules: tuple[ValidationRuleLike, ...] | None = None
"""Entry-point rules, loaded on first use. An explicit cache rather than
``functools.cache`` because the wrapper object makes griffe (quartodoc) report
a cyclic alias when documenting the re-export in ``shiny.validate``."""


def installed_validation_rules() -> tuple[ValidationRuleLike, ...]:
    """Rules registered by installed packages under ``shiny.validators``, loaded once."""
    global _installed_rules
    if _installed_rules is None:
        rules: list[ValidationRuleLike] = []
        for ep in entry_points(group=VALIDATOR_ENTRY_POINT_GROUP):
            name = f"{ep.name} ({ep.value})"
            try:
                rules.append(_check_rule(ep.load(), name))
            except Exception as e:
                rules.append(_failed_rule(name, e))
        _installed_rules = tuple(rules)
    return _installed_rules


def _clear_installed_rules() -> None:
    """Forget loaded entry-point rules so the next call reloads them (tests)."""
    global _installed_rules
    _installed_rules = None


def load_validation_rule(spec: str) -> ValidationRuleLike:
    """Load a rule from a ``module:attr`` spec, importing relative to the working directory."""
    module_name, sep, attr = spec.partition(":")
    if not sep or not module_name or not attr:
        raise ValueError(f"Expected 'module:attr', got '{spec}'.")
    cwd = os.getcwd()
    if cwd not in sys.path:
        sys.path.insert(0, cwd)
    obj: Any = importlib.import_module(module_name)
    for part in attr.split("."):
        obj = getattr(obj, part)
    return _check_rule(obj, spec)


def _run_rules(
    rules: Sequence[ValidationRuleLike], tree: ast.Module, result: ValidateResult
) -> None:
    for rule in rules:
        try:
            if isinstance(rule, type):
                rule(result).check(tree)
            else:
                rule(tree, result)
        except Exception as e:
            result.add_warning(
                1,
                f"Validation plugin '{_rule_name(rule)}' failed: {type(e).__name__}: {e}",
                "VALIDATOR_PLUGIN_ERROR",
            )


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
    code: str,
    *,
    validator_class: type[ShinyCodeValidator] = ShinyCodeValidator,
    rules: Sequence[ValidationRuleLike] | None = None,
) -> ValidateResult:
    """Validate source with the built-in validator plus plugin rules.

    ``rules`` defaults to :func:`installed_validation_rules`; pass ``()`` to run
    only the built-in validator. Every rule visits the same parsed tree.

    ``# shiny: ignore [CODE, ...]`` suppresses diagnostics on the current line.
    ``# shiny: ignore-next-line [CODE, ...]`` suppresses the following line.
    Omitting codes suppresses all validation rules on that line. Syntax errors
    cannot be suppressed.
    """
    return _validate_source(
        code, validator_class=validator_class, rules=rules, pair_outputs=True
    )


def _validate_source(
    code: str,
    *,
    validator_class: type[ShinyCodeValidator],
    rules: Sequence[ValidationRuleLike] | None,
    pair_outputs: bool,
) -> ValidateResult:
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
    ReactiveUsageValidator(result).visit(tree)
    _run_rules(installed_validation_rules() if rules is None else rules, tree, result)
    if pair_outputs:
        result.check_output_pairing()
    _apply_suppressions(code, result)
    if (
        result.mode == "express"
        and result.duplicate_ids
        and any(issue["code"] == "DUPLICATE_ID" for issue in result.warnings)
    ):
        result.suggestions.append(
            "Ensure each UI component in Express mode has a unique string ID."
        )
    if result.clean:
        result.suggestions.append(_CLEAN_MESSAGE)
    return result


def validate_shiny_file(
    path: str | Path,
    *,
    validator_class: type[ShinyCodeValidator] = ShinyCodeValidator,
    rules: Sequence[ValidationRuleLike] | None = None,
) -> ValidateResult:
    """Validate a UTF-8 file and its local Python imports without executing them.

    Imports are followed only within the entry file's directory. Installed
    packages, unresolved imports, and dynamic imports are not inspected.
    Diagnostics include a ``file`` path as well as their line number. Each
    file has its own ID namespace and suppression comments.
    """
    p = Path(path)
    if not p.is_file():
        result = ValidateResult()
        result.add_error(1, f"File not found: {path}", "FILE_NOT_FOUND")
        return result
    entry = p.resolve()
    root = entry.parent
    pending = [entry]
    seen: set[Path] = set()
    sources: dict[str, str] = {}
    result = ValidateResult()
    while pending:
        current = pending.pop()
        if current in seen:
            continue
        seen.add(current)
        try:
            code = current.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            report = ValidateResult()
            report.add_error(
                1, message=f"Could not read file: {error}", code="FILE_READ_ERROR"
            )
        else:
            sources[str(current)] = code
            report = _validate_source(
                code, validator_class=validator_class, rules=rules, pair_outputs=False
            )
            if not any(issue["code"] == "SYNTAX_ERROR" for issue in report.errors):
                pending.extend(
                    reversed(
                        _local_imports(ast.parse(code), current=current, root=root)
                    )
                )
        if current == entry:
            result.mode = report.mode
        for issue in [*report.errors, *report.warnings]:
            issue["file"] = str(current)
        result.errors.extend(report.errors)
        result.warnings.extend(report.warnings)
        result.input_ids.update(report.input_ids)
        result.ui_output_ids.update(report.ui_output_ids)
        result.renderer_ids.update(report.renderer_ids)
        result.reactive_vals.update(report.reactive_vals)
        result.reactive_calcs.update(report.reactive_calcs)
        result.duplicate_ids.extend(report.duplicate_ids)
        for output_id, line in report.app_outputs.items():
            if output_id not in result.app_outputs:
                result.app_outputs[output_id] = line
                result._issue_files[f"output:{output_id}"] = str(current)
        for output_id, line in report.app_renderers.items():
            if output_id not in result.app_renderers:
                result.app_renderers[output_id] = line
                result._issue_files[f"renderer:{output_id}"] = str(current)
        result.app_functions.update(report.app_functions)
        result.suggestions.extend(s for s in report.suggestions if s != _CLEAN_MESSAGE)
    _pair_outputs_across_files(result, sources)
    if result.clean:
        result.suggestions.append(_CLEAN_MESSAGE)
    return result


def _pair_outputs_across_files(result: ValidateResult, sources: dict[str, str]) -> None:
    """Match UI placeholders with renderers over the whole file set, honoring each
    file's ``# shiny: ignore`` comments for the warnings it receives."""
    pairing = ValidateResult(
        mode=result.mode,
        app_outputs=result.app_outputs,
        app_renderers=result.app_renderers,
        app_functions=result.app_functions,
        _issue_files=result._issue_files,
    )
    pairing.check_output_pairing()
    for file, code in sources.items():
        per_file = ValidateResult(
            warnings=[w for w in pairing.warnings if w.get("file") == file]
        )
        if per_file.warnings:
            # Only files that parsed contribute IDs, so tokenizing here is safe.
            _apply_suppressions(code, per_file)
            result.warnings.extend(per_file.warnings)


def _local_imports(tree: ast.Module, *, current: Path, root: Path) -> list[Path]:
    paths: list[Path] = []
    for node in ast.walk(tree):
        names: list[list[str]] = []
        base = root
        if isinstance(node, ast.Import):
            names = [alias.name.split(".") for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                base = current.parent
                for _ in range(node.level - 1):
                    base = base.parent
            parts: list[str] = node.module.split(".") if node.module else []
            names = [
                parts,
                *[parts + [alias.name] for alias in node.names if alias.name != "*"],
            ]
        for parts in names:
            first = 0 if isinstance(node, ast.ImportFrom) and node.level else 1
            for length in range(first, len(parts) + 1):
                candidate = base.joinpath(*parts[:length])
                package = candidate / "__init__.py"
                file = candidate.with_suffix(".py")
                path = package if package.is_file() else file
                if path.is_file() and path.resolve().is_relative_to(root):
                    paths.append(path.resolve())
    return paths
