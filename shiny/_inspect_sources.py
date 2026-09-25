"""Read an app's local Python imports for static inspection without importing code."""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any


def read_app_sources(
    code: str, source_path: str | Path
) -> tuple[ast.Module, dict[str, str], str]:
    entry = Path(source_path).resolve()
    root = entry.parent
    while (root / "__init__.py").is_file():
        root = root.parent
    trees: dict[Path, ast.Module] = {}
    sources: dict[str, str] = {}
    # Bindings point to (local file, exported symbol); None denotes a module.
    imports: dict[Path, dict[str, tuple[Path, str | None]]] = {}

    def locate(parts: list[str], base: Path) -> Path | None:
        target = base.joinpath(*parts)
        for candidate in (target.with_suffix(".py"), target / "__init__.py"):
            resolved = candidate.resolve()
            if resolved.is_relative_to(root) and resolved.is_file():
                return resolved
        return None

    def read(path: Path, supplied: str | None = None) -> None:
        if path in trees:
            return
        text = supplied if supplied is not None else path.read_text(encoding="utf-8")
        filename = path.relative_to(root).as_posix()
        tree = ast.parse(text, filename=filename)
        trees[path] = tree  # Register first so circular imports terminate.
        sources[filename] = text
        bindings = imports[path] = {}
        for node in ast.walk(tree):
            node.source_file = filename  # type: ignore[attr-defined]
        for node in tree.body:
            if isinstance(node, ast.Import):
                for alias in node.names:
                    target = locate(alias.name.split("."), root)
                    if target:
                        read(target)
                        bindings[alias.asname or alias.name] = (target, None)
            elif isinstance(node, ast.ImportFrom):
                base = path.parent if node.level else root
                for _ in range(max(0, node.level - 1)):
                    base = base.parent
                parts = node.module.split(".") if node.module else []
                target = locate(parts, base) if parts else locate(["__init__"], base)
                if target:
                    read(target)
                for alias in node.names:
                    if alias.name == "*":
                        continue
                    submodule = locate(parts + [alias.name], base)
                    if submodule:
                        read(submodule)
                        bindings[alias.asname or alias.name] = (submodule, None)
                    elif target:
                        bindings[alias.asname or alias.name] = (target, alias.name)

    read(entry, code)

    def qualified(path: Path, name: str) -> str:
        if path == entry:
            return name
        return (
            path.relative_to(root).with_suffix("").as_posix().replace("/", ".")
            + "."
            + name
        )

    def resolve(
        path: Path, name: str, seen: set[tuple[Path, str]] | None = None
    ) -> str:
        seen = set() if seen is None else seen
        key = (path, name)
        if key in seen:
            return qualified(path, name)
        seen.add(key)
        for alias, (target, symbol) in imports[path].items():
            if name == alias and symbol is not None:
                return resolve(target, symbol, seen)
            if symbol is None and name.startswith(alias + "."):
                return resolve(target, name[len(alias) + 1 :], seen)
        return qualified(path, name)

    class BindNames(ast.NodeTransformer):
        def __init__(self, path: Path, bindings: dict[str, str]):
            self.path = path
            self.bindings = bindings

        def visit_Name(self, node: ast.Name) -> ast.AST:
            if node.id in self.bindings:
                node.id = self.bindings[node.id]
            return node

        def visit_Attribute(self, node: ast.Attribute) -> ast.AST:
            dotted = ast.unparse(node)
            for alias, (target, symbol) in imports[self.path].items():
                if (
                    symbol is None
                    and alias.split(".")[0] in self.bindings
                    and dotted.startswith(alias + ".")
                ):
                    return ast.copy_location(
                        ast.Name(
                            id=resolve(target, dotted[len(alias) + 1 :]), ctx=node.ctx
                        ),
                        node,
                    )
            return self.generic_visit(node)

        def visit_FunctionDef(
            self, node: ast.FunctionDef | ast.AsyncFunctionDef
        ) -> Any:
            node.name = self.bindings.get(node.name, node.name)
            node.decorator_list = [self.visit(d) for d in node.decorator_list]
            # Function-local names shadow imports and file-level definitions.
            local = {
                arg.arg
                for arg in (
                    *node.args.posonlyargs,
                    *node.args.args,
                    *node.args.kwonlyargs,
                )
            }
            if node.args.vararg:
                local.add(node.args.vararg.arg)
            if node.args.kwarg:
                local.add(node.args.kwarg.arg)
            for stmt in node.body:
                if isinstance(
                    stmt, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
                ):
                    local.add(stmt.name)
                elif not isinstance(stmt, (ast.Import, ast.ImportFrom)):
                    local.update(
                        n.id
                        for n in ast.walk(stmt)
                        if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store)
                    )
            child = BindNames(
                self.path,
                {
                    name: value
                    for name, value in self.bindings.items()
                    if name not in local
                },
            )
            node.body = [child.visit(stmt) for stmt in node.body]
            return node

        visit_AsyncFunctionDef = visit_FunctionDef

    combined: list[ast.stmt] = []
    for path, tree in trees.items():
        bindings = {
            node.name: qualified(path, node.name)
            for node in tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
        }
        for alias, (_, symbol) in imports[path].items():
            bindings[alias] = resolve(path, alias) if symbol is not None else alias
            bindings.setdefault(alias.split(".")[0], alias.split(".")[0])
        combined.extend(BindNames(path, bindings).visit(tree).body)
    return (
        ast.Module(body=combined, type_ignores=[]),
        sources,
        entry.relative_to(root).as_posix(),
    )
