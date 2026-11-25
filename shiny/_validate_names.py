from __future__ import annotations

import ast


def _resolve_name(node: ast.AST, bindings: dict[str, str]) -> str:
    if isinstance(node, ast.Name):
        name = bindings.get(node.id, node.id)
    elif isinstance(node, ast.Attribute):
        owner = _resolve_name(node.value, bindings=bindings)
        name = f"{owner}.{node.attr}" if owner else ""
    else:
        return ""
    if name == "shiny.express.input":
        return "inputs"
    if name.startswith("shiny.express."):
        return "shiny." + name[len("shiny.express.") :]
    return name


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
        if isinstance(node.value, ast.Call):
            constructor = node.value.func
            if isinstance(constructor, ast.Subscript):
                constructor = constructor.value
            if _resolve_name(constructor, bindings=self.names) in (
                "shiny.reactive.Value",
                "shiny.reactive.value",
            ):
                kind = "value"
        for target in node.targets:
            for name in ast.walk(target):
                if isinstance(name, ast.Name) and isinstance(name.ctx, ast.Store):
                    self.names[name.id] = kind

    def visit_Name(self, node: ast.Name) -> None:
        if isinstance(node.ctx, ast.Store):
            self.names[node.id] = ""

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        if node.name is not None:
            self.names[node.name] = ""
        self.generic_visit(node)

    def visit_Lambda(self, node: ast.Lambda) -> None:
        pass

    def visit_ListComp(
        self, node: ast.ListComp | ast.SetComp | ast.DictComp | ast.GeneratorExp
    ) -> None:
        pass

    visit_SetComp = visit_ListComp
    visit_DictComp = visit_ListComp
    visit_GeneratorExp = visit_ListComp

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
        if name in ("shiny.Inputs", "shiny.session.Inputs"):
            return "inputs"
        if name in ("shiny.Outputs", "shiny.session.Outputs"):
            return "output"
        if name in ("shiny.Session", "shiny.session.Session"):
            return "session"
        return ""


def _collect_bindings(
    body: list[ast.stmt], *, inherited: dict[str, str]
) -> dict[str, str]:
    bindings = _Bindings(inherited)
    for statement in body:
        bindings.visit(statement)
    return bindings.names


def _is_server_function(
    node: ast.FunctionDef | ast.AsyncFunctionDef, *, bindings: dict[str, str]
) -> bool:
    decorators = {
        _resolve_name(d.func if isinstance(d, ast.Call) else d, bindings=bindings)
        for d in node.decorator_list
    }
    names = [a.arg for a in [*node.args.posonlyargs, *node.args.args]]
    return (
        node.name == "server"
        or "shiny.module.server" in decorators
        or len(names) >= 3
        and names[1:3] == ["output", "session"]
    )


def _argument_bindings(
    arguments: ast.arguments, *, inherited: dict[str, str]
) -> dict[str, str]:
    bindings = _Bindings(inherited)
    for argument in [*arguments.posonlyargs, *arguments.args, *arguments.kwonlyargs]:
        bindings.names[argument.arg] = bindings.annotation_kind(argument.annotation)
    for argument in (arguments.vararg, arguments.kwarg):
        if argument is not None:
            bindings.names[argument.arg] = ""
    return bindings.names


def _function_bindings(
    node: ast.FunctionDef | ast.AsyncFunctionDef, *, inherited: dict[str, str]
) -> dict[str, str]:
    bindings = _argument_bindings(node.args, inherited=inherited)
    if _is_server_function(node, bindings=inherited):
        arguments = [*node.args.posonlyargs, *node.args.args]
        for argument, kind in zip(arguments, ("inputs", "output", "session")):
            if argument.annotation is None:
                bindings[argument.arg] = kind
    return _collect_bindings(node.body, inherited=bindings)


class ScopedNameVisitor(ast.NodeVisitor):
    """Keep lambda and comprehension bindings local in both validators."""

    bindings: dict[str, str]

    def visit_Lambda(self, node: ast.Lambda) -> None:
        previous = self.bindings
        self.bindings = _argument_bindings(node.args, inherited=previous)
        self.visit(node.body)
        self.bindings = previous

    def visit_ListComp(
        self, node: ast.ListComp | ast.SetComp | ast.DictComp | ast.GeneratorExp
    ) -> None:
        previous = self.bindings
        self.bindings = previous.copy()
        for generator in node.generators:
            self.visit(generator.iter)
            bindings = _Bindings(self.bindings)
            bindings.visit(generator.target)
            self.bindings = bindings.names
            for condition in generator.ifs:
                self.visit(condition)
        if isinstance(node, ast.DictComp):
            self.visit(node.key)
            self.visit(node.value)
        else:
            self.visit(node.elt)
        self.bindings = previous

    visit_SetComp = visit_ListComp
    visit_DictComp = visit_ListComp
    visit_GeneratorExp = visit_ListComp
