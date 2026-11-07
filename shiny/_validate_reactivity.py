from __future__ import annotations

import ast
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Literal

from ._validate_names import (
    ScopedNameVisitor,
    _collect_bindings,
    _function_bindings,
    _is_server_function,
    _resolve_name,
)

if TYPE_CHECKING:
    from ._validate import ValidateResult


_MUTATING_METHODS = {
    "append",
    "clear",
    "extend",
    "insert",
    "pop",
    "popitem",
    "remove",
    "reverse",
    "setdefault",
    "sort",
    "update",
    "add",
    "discard",
}
"""Container methods that can change the object held by a reactive value."""

_NON_REACTIVE_INPUT_METHODS = {"set_serializer", "set_snapshot_preprocess"}
"""``Inputs`` methods that configure the session rather than read a value."""


@dataclass
class _ReactiveReference:
    source: str
    mutated: bool = False


@dataclass
class _EffectBody:
    name: str
    reads: set[str] = field(default_factory=set[str])
    sets: list[tuple[str, int]] = field(default_factory=list[tuple[str, int]])


class ReactiveUsageValidator(ScopedNameVisitor):
    """Check known reactive objects, keeping function bindings and aliases local."""

    def __init__(self, result: ValidateResult) -> None:
        self.result = result
        self.bindings: dict[str, str] = {}
        self.references: dict[str, _ReactiveReference] = {}
        self.in_extended_task = False
        self.context: Literal["module", "server", "function"] = "module"
        """Where a reactive read happens.

        Module-level code and the body of a server function run once per
        session with no reactive context, so reading an input, value, or calc
        there raises at runtime. Any other function may be called from a
        reactive context, so reads inside it are not reported.
        """
        self.isolated = False
        """Inside ``with reactive.isolate():``, where reads are allowed anywhere."""
        self.effect: _EffectBody | None = None
        """Reads and sets seen in the body of a ``reactive.effect`` without ``reactive.event``."""
        self.calc_name: str | None = None
        """Name of the enclosing ``reactive.calc``, whose body should not set values."""

    def visit_Module(self, node: ast.Module) -> None:
        self.bindings = _collect_bindings(node.body, inherited={})
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        # Decorators and defaults are evaluated before the function body.
        for expression in [
            *node.decorator_list,
            *node.args.defaults,
            *node.args.kw_defaults,
        ]:
            if expression is not None:
                self.visit(expression)
        previous = (
            self.bindings,
            self.references,
            self.in_extended_task,
            self.context,
            self.isolated,
            self.effect,
            self.calc_name,
        )
        decorators = {
            _resolve_name(
                d.func if isinstance(d, ast.Call) else d, bindings=self.bindings
            )
            for d in node.decorator_list
        }
        self.in_extended_task = "shiny.reactive.extended_task" in decorators
        self.context = (
            "server"
            if _is_server_function(node, bindings=self.bindings)
            else "function"
        )
        self.isolated = False
        is_effect = bool(
            decorators & {"shiny.reactive.effect", "shiny.reactive.Effect"}
        )
        has_event = "shiny.reactive.event" in decorators
        self.effect = _EffectBody(node.name) if is_effect and not has_event else None
        is_calc = bool(decorators & {"shiny.reactive.calc", "shiny.reactive.Calc"})
        self.calc_name = node.name if is_calc else None
        self.bindings = _function_bindings(node, inherited=self.bindings)
        self.references = {}
        for statement in node.body:
            self.visit(statement)
        if self.effect is not None:
            for name, line in self.effect.sets:
                if name in self.effect.reads:
                    self.result.add_warning(
                        line,
                        message=f"'{self.effect.name}' reads '{name}()' and then sets '{name}', "
                        "so it re-triggers itself. Read it inside 'with reactive.isolate():', "
                        "or trigger the effect with '@reactive.event(...)'.",
                        code="EFFECT_SELF_INVALIDATION",
                    )
        (
            self.bindings,
            self.references,
            self.in_extended_task,
            self.context,
            self.isolated,
            self.effect,
            self.calc_name,
        ) = previous

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Lambda(self, node: ast.Lambda) -> None:
        for expression in [*node.args.defaults, *node.args.kw_defaults]:
            if expression is not None:
                self.visit(expression)
        previous = self.context, self.effect, self.calc_name
        self.context = "function"
        self.effect = None
        self.calc_name = None
        super().visit_Lambda(node)
        self.context, self.effect, self.calc_name = previous

    def visit_With(self, node: ast.With | ast.AsyncWith) -> None:
        isolates = any(
            isinstance(item.context_expr, ast.Call)
            and _resolve_name(item.context_expr.func, bindings=self.bindings)
            == "shiny.reactive.isolate"
            for item in node.items
        )
        previous = self.isolated
        self.isolated = self.isolated or isolates
        self.generic_visit(node)
        self.isolated = previous

    visit_AsyncWith = visit_With

    def _reactive_read(self, node: ast.AST) -> str:
        if not isinstance(node, ast.Call):
            return ""
        function = node.func
        if isinstance(function, ast.Name) and self.bindings.get(function.id) in (
            "value",
            "calc",
        ):
            return function.id
        if isinstance(function, ast.Attribute):
            if (
                self.bindings.get(getattr(function.value, "id", "")) == "value"
                and function.attr == "get"
            ):
                return ast.unparse(function.value)
        if isinstance(function, (ast.Attribute, ast.Subscript)):
            owner = function.value
            if _resolve_name(owner, bindings=self.bindings) == "inputs":
                if isinstance(function, ast.Attribute) and (
                    function.attr.startswith("_")
                    or function.attr in _NON_REACTIVE_INPUT_METHODS
                ):
                    return ""
                return ast.unparse(function)
        return ""

    def visit_Call(self, node: ast.Call) -> None:
        source = self._reactive_read(node)
        if source and self.in_extended_task:
            self.result.add_error(
                node.lineno,
                message=f"Reactive source '{source}' cannot be read inside an extended task. "
                "Read it before invoking the task and pass its value as an argument.",
                code="EXTENDED_TASK_REACTIVE_READ",
            )
        elif source and self.context != "function" and not self.isolated:
            where = (
                "at module level"
                if self.context == "module"
                else "directly in the server function body"
            )
            self.result.add_error(
                node.lineno,
                message=f"Reactive source '{source}' is read {where}, outside any reactive context. "
                "Move the read into a render function, reactive.calc, or reactive.effect, "
                "or wrap it in 'with reactive.isolate():' for a one-time read.",
                code="REACTIVE_READ_OUTSIDE_CONTEXT",
            )
        if (
            source
            and self.effect is not None
            and not self.isolated
            and self.bindings.get(source) == "value"
        ):
            self.effect.reads.add(source)
        if isinstance(node.func, ast.Attribute):
            owner = node.func.value
            if node.func.attr in _MUTATING_METHODS:
                self._mark_mutated(owner)
            if (
                node.func.attr == "set"
                and isinstance(owner, ast.Name)
                and self.bindings.get(owner.id) == "value"
            ):
                if self.effect is not None:
                    self.effect.sets.append((owner.id, node.lineno))
                if self.calc_name is not None:
                    self.result.add_warning(
                        node.lineno,
                        message=f"reactive.calc '{self.calc_name}' sets '{owner.id}'. Calcs should "
                        "only compute and return a value; move side effects into a reactive.effect.",
                        code="CALC_SIDE_EFFECT",
                    )
            if node.func.attr == "set" and isinstance(owner, ast.Name) and node.args:
                reference = self.references.get(getattr(node.args[0], "id", ""))
                if reference and reference.mutated and reference.source == owner.id:
                    self.result.add_warning(
                        node.lineno,
                        message=f"'{owner.id}.set()' receives the same object that was mutated "
                        "after reading it. Copy the object before changing it so reactive dependents are notified.",
                        code="REACTIVE_MUTATION",
                    )
        self.generic_visit(node)

    def _mark_mutated(self, node: ast.AST) -> None:
        while isinstance(node, (ast.Subscript, ast.Attribute)):
            node = node.value
        if isinstance(node, ast.Name) and node.id in self.references:
            self.references[node.id].mutated = True

    def visit_Assign(self, node: ast.Assign) -> None:
        self.generic_visit(node)
        self._assign_reference(node.targets, value=node.value)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        self.generic_visit(node)
        if node.value is not None:
            self._assign_reference([node.target], value=node.value)

    def _assign_reference(self, targets: list[ast.expr], *, value: ast.expr) -> None:
        source = self._reactive_read(value)
        reference = (
            _ReactiveReference(source=source)
            if source and self.bindings.get(source) == "value"
            else self.references.get(getattr(value, "id", ""))
        )
        for target in targets:
            if isinstance(target, ast.Name):
                self.references.pop(target.id, None)
                if reference is not None:
                    self.references[target.id] = reference
            else:
                self._mark_mutated(target)

    def visit_AugAssign(self, node: ast.AugAssign) -> None:
        if isinstance(node.target, ast.Name):
            # Augmented assignment may create a new immutable value.
            self.references.pop(node.target.id, None)
        else:
            self._mark_mutated(node.target)
        self.generic_visit(node)

    def visit_Delete(self, node: ast.Delete) -> None:
        for target in node.targets:
            if not isinstance(target, ast.Name):
                self._mark_mutated(target)
        self.generic_visit(node)

    def visit_Try(self, node: ast.Try) -> None:
        has_task_result = any(
            isinstance(child, ast.Call)
            and isinstance(child.func, ast.Attribute)
            and child.func.attr == "result"
            and self.bindings.get(getattr(child.func.value, "id", "")) == "task"
            for statement in node.body
            for child in ast.walk(statement)
        )
        if has_task_result:
            for handler in node.handlers:
                catches_all = handler.type is None or any(
                    isinstance(child, ast.Name)
                    and child.id in ("Exception", "BaseException")
                    for child in ast.walk(handler.type)
                )
                reraises = any(
                    isinstance(statement, ast.Raise)
                    and (
                        statement.exc is None
                        or isinstance(statement.exc, ast.Name)
                        and statement.exc.id == handler.name
                    )
                    for statement in handler.body
                )
                if catches_all and not reraises:
                    self.result.add_warning(
                        handler.lineno,
                        message="This handler swallows extended-task result errors, including "
                        "Shiny's pending-result signals. Let result() propagate them, or catch a specific task exception.",
                        code="SWALLOWED_TASK_ERROR",
                    )
        self.generic_visit(node)
