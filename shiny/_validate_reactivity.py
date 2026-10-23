from __future__ import annotations

import ast
from dataclasses import dataclass
from typing import TYPE_CHECKING

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


def _resolve_name(node: ast.AST, bindings: dict[str, str]) -> str:
    if isinstance(node, ast.Name):
        return bindings.get(node.id, "")
    if isinstance(node, ast.Attribute):
        return f"{_resolve_name(node.value, bindings=bindings)}.{node.attr}"
    return ""


class _Bindings(ast.NodeVisitor):
    """Collect lexical bindings without entering nested function bodies."""

    def __init__(self, inherited: dict[str, str]) -> None:
        self.names = inherited.copy()

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self.names[alias.asname or alias.name.split(".")[0]] = (
                alias.name if alias.asname else alias.name.split(".")[0]
            )

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        for alias in node.names:
            if alias.name != "*":
                self.names[alias.asname or alias.name] = f"{node.module}.{alias.name}"

    def visit_FunctionDef(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        decorators = {
            _resolve_name(d.func if isinstance(d, ast.Call) else d, bindings=self.names)
            for d in node.decorator_list
        }
        if decorators & {"shiny.reactive.calc", "shiny.reactive.Calc"}:
            self.names[node.name] = "calc"
        elif "shiny.reactive.extended_task" in decorators:
            self.names[node.name] = "task"
        else:
            self.names[node.name] = ""

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.names[node.name] = ""

    def visit_Assign(self, node: ast.Assign) -> None:
        kind = ""
        if isinstance(node.value, ast.Call) and _resolve_name(
            node.value.func, bindings=self.names
        ) in (
            "shiny.reactive.Value",
            "shiny.reactive.value",
        ):
            kind = "value"
        for target in node.targets:
            for name in ast.walk(target):
                if isinstance(name, ast.Name) and isinstance(name.ctx, ast.Store):
                    self.names[name.id] = kind

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        if isinstance(node.target, ast.Name):
            self.names[node.target.id] = self.annotation_kind(node.annotation)

    def annotation_kind(self, node: ast.AST | None) -> str:
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            try:
                node = ast.parse(node.value, mode="eval").body
            except SyntaxError:
                return ""
        if isinstance(node, ast.Subscript):
            node = node.value
        name = _resolve_name(node, bindings=self.names) if node is not None else ""
        if name in ("shiny.reactive.Value", "shiny.reactive.value"):
            return "value"
        if name == "shiny.Inputs":
            return "inputs"
        return ""


@dataclass
class _ReactiveReference:
    source: str
    mutated: bool = False


class ReactiveUsageValidator(ast.NodeVisitor):
    """Check known reactive objects, keeping function bindings and aliases local."""

    def __init__(self, result: ValidateResult) -> None:
        self.result = result
        self.bindings: dict[str, str] = {}
        self.references: dict[str, _ReactiveReference] = {}
        self.in_extended_task = False

    def visit_Module(self, node: ast.Module) -> None:
        bindings = _Bindings({})
        for statement in node.body:
            bindings.visit(statement)
        self.bindings = bindings.names
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        previous = self.bindings, self.references, self.in_extended_task
        self.in_extended_task = any(
            _resolve_name(
                d.func if isinstance(d, ast.Call) else d, bindings=self.bindings
            )
            == "shiny.reactive.extended_task"
            for d in node.decorator_list
        )
        bindings = _Bindings(self.bindings)
        for argument in [
            *node.args.posonlyargs,
            *node.args.args,
            *node.args.kwonlyargs,
        ]:
            bindings.names[argument.arg] = bindings.annotation_kind(argument.annotation)
            if argument.arg == "input" and argument.annotation is None:
                bindings.names[argument.arg] = "inputs"
        for argument in (node.args.vararg, node.args.kwarg):
            if argument is not None:
                bindings.names[argument.arg] = ""
        for statement in node.body:
            bindings.visit(statement)
        self.bindings = bindings.names
        self.references = {}
        for statement in node.body:
            self.visit(statement)
        self.bindings, self.references, self.in_extended_task = previous

    visit_AsyncFunctionDef = visit_FunctionDef

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
            if isinstance(owner, ast.Name) and self.bindings.get(owner.id) in (
                "inputs",
                "shiny.express.input",
            ):
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
        if isinstance(node.func, ast.Attribute):
            owner = node.func.value
            if node.func.attr in _MUTATING_METHODS:
                self._mark_mutated(owner)
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

    def _uncalled(self, node: ast.Attribute | ast.Subscript) -> None:
        if isinstance(node.value, ast.Name) and self.bindings.get(node.value.id) in (
            "value",
            "calc",
        ):
            self.result.add_error(
                node.lineno,
                message=f"Reactive object '{node.value.id}' must be called before accessing its contents. "
                f"Use '{node.value.id}()' to read its value.",
                code="UNCALLED_REACTIVE",
            )

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if node.attr in _MUTATING_METHODS | {
            "items",
            "keys",
            "values",
            "copy",
            "iloc",
            "loc",
        }:
            self._uncalled(node)
        self.generic_visit(node)

    def visit_Subscript(self, node: ast.Subscript) -> None:
        self._uncalled(node)
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
