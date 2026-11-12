from __future__ import annotations

import ast
import asyncio
import concurrent.futures
import copy
import html as html_lib
import inspect
import io
import json
import keyword
import os
import shutil
import sys
import tempfile
import time
import tokenize
from collections import deque
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, cast


def _expand_module_calls(tree: ast.Module) -> tuple[ast.Module, Dict[str, str]]:
    """Expand same-file modules with literal IDs for static analysis, never execution.

    Each call gets its own namespaced inputs/functions. Reactive parameters and a
    directly returned reactive are aliases, preserving edges across the boundary.
    Dynamic IDs cannot be resolved statically. Local imports are combined before expansion.
    """
    definitions = {
        node.name: node
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and any(
            isinstance(d, ast.Attribute)
            and isinstance(d.value, ast.Name)
            and d.value.id == "module"
            and d.attr in ("ui", "server")
            for d in node.decorator_list
        )
    }
    members: Dict[str, str] = {}
    expanded: List[ast.stmt] = []
    active: Set[str] = set()

    class Expander(ast.NodeTransformer):
        def __init__(
            self, namespace: str = "", aliases: Optional[Dict[str, ast.expr]] = None
        ):
            self.namespace = namespace
            self.aliases = dict(aliases or {})

        def qualify(self, name: str) -> str:
            qualified = f"{self.namespace}-{name}" if self.namespace else name
            if self.namespace:
                members[qualified] = self.namespace
            return qualified

        def visit_Name(self, node: ast.Name) -> ast.expr:
            return copy.deepcopy(self.aliases.get(node.id, node))

        def visit_Attribute(self, node: ast.Attribute) -> ast.AST:
            if isinstance(node.value, ast.Name) and node.value.id == "input":
                node.attr = self.qualify(node.attr)
                return node
            return self.generic_visit(node)

        def visit_FunctionDef(
            self, node: ast.FunctionDef | ast.AsyncFunctionDef
        ) -> Any:
            if node.name in definitions:
                return None
            child = Expander(self.namespace, self.aliases)
            # Register all reactive functions before visiting their bodies (forward references).
            for stmt in node.body:
                if (
                    isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef))
                    and stmt.decorator_list
                ):
                    child.aliases[stmt.name] = ast.Name(
                        id=self.qualify(stmt.name), ctx=ast.Load()
                    )
            alias = self.aliases.get(node.name)
            if isinstance(alias, ast.Name):
                node.name = alias.id
            node.decorator_list = [
                cast(ast.expr, self.visit(d)) for d in node.decorator_list
            ]
            node.body = [
                result
                for stmt in node.body
                if (result := child.visit(stmt)) is not None
            ]
            return node

        visit_AsyncFunctionDef = visit_FunctionDef

        def visit_Assign(self, node: ast.Assign) -> ast.AST:
            is_module = (
                isinstance(node.value, ast.Call)
                and isinstance(node.value.func, ast.Name)
                and node.value.func.id in definitions
            )
            node.value = cast(ast.expr, self.visit(node.value))
            if is_module and isinstance(node.value, ast.Name):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        self.aliases[target.id] = node.value
            return node

        def visit_Call(self, node: ast.Call) -> ast.AST:
            name = node.func.id if isinstance(node.func, ast.Name) else ""
            if name in definitions:
                definition = definitions[name]
                if (
                    not node.args
                    or not isinstance(node.args[0], ast.Constant)
                    or not isinstance(node.args[0].value, str)
                    or name in active
                ):
                    return ast.Constant(value=None)
                namespace = self.qualify(node.args[0].value)
                params = definition.args.args
                is_server = any(
                    isinstance(d, ast.Attribute) and d.attr == "server"
                    for d in definition.decorator_list
                )
                params = params[3:] if is_server else params
                aliases = {
                    param.arg: cast(ast.expr, self.visit(copy.deepcopy(arg)))
                    for param, arg in zip(params, node.args[1:])
                }
                aliases.update(
                    {
                        kw.arg: cast(ast.expr, self.visit(copy.deepcopy(kw.value)))
                        for kw in node.keywords
                        if kw.arg
                    }
                )
                child = Expander(namespace, aliases)
                for stmt in definition.body:
                    if (
                        isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef))
                        and stmt.decorator_list
                    ):
                        child.aliases[stmt.name] = ast.Name(
                            id=child.qualify(stmt.name), ctx=ast.Load()
                        )
                active.add(name)
                result: ast.expr = ast.Constant(value=None)
                for stmt in copy.deepcopy(definition.body):
                    if isinstance(stmt, ast.Return):
                        if is_server and stmt.value is not None:
                            result = cast(ast.expr, child.visit(stmt.value))
                        elif stmt.value is not None:
                            expanded.append(
                                ast.Expr(value=cast(ast.expr, child.visit(stmt.value)))
                            )
                    else:
                        visited = child.visit(stmt)
                        if visited is not None:
                            expanded.append(visited)
                active.remove(name)
                return ast.copy_location(result, node)
            if (
                isinstance(node.func, ast.Attribute)
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "ui"
                and node.func.attr.startswith(("input_", "output_"))
                and node.args
                and isinstance(node.args[0], ast.Constant)
                and isinstance(node.args[0].value, str)
            ):
                node.args[0].value = self.qualify(node.args[0].value)
            return self.generic_visit(node)

    transformed = cast(ast.Module, Expander().visit(copy.deepcopy(tree)))
    transformed.body.extend(expanded)
    return transformed, members


class GraphVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.inputs: Dict[str, int] = {}
        self.input_defaults: Dict[str, Any] = {}
        self.input_files: Dict[str, str] = {}
        self.calcs: Dict[str, Dict[str, Any]] = {}
        self.outputs: Dict[str, Dict[str, Any]] = {}
        self.effects: Dict[str, Dict[str, Any]] = {}
        self.current_calc: Optional[str] = None
        self.current_output: Optional[str] = None
        self.current_effect: Optional[str] = None
        self.isolated_depth: int = 0
        self.event_depth: int = 0

    def visit_With(self, node: ast.With) -> None:
        is_isolate_block = False
        for item in node.items:
            ctx = item.context_expr
            if isinstance(ctx, ast.Call):
                func_name = self._get_decorator_name(ctx.func)
                if func_name in ("reactive.isolate", "isolate") or func_name.endswith(
                    ".isolate"
                ):
                    is_isolate_block = True
            elif isinstance(ctx, (ast.Attribute, ast.Name)):
                func_name = self._get_decorator_name(ctx)
                if func_name in ("reactive.isolate", "isolate") or func_name.endswith(
                    ".isolate"
                ):
                    is_isolate_block = True

        if is_isolate_block:
            self.isolated_depth += 1
        self.generic_visit(node)
        if is_isolate_block:
            self.isolated_depth -= 1

    def visit_Call(self, node: ast.Call) -> None:
        func_name = self._get_decorator_name(node.func)

        if (
            func_name.startswith("ui.input_")
            and node.args
            and isinstance(node.args[0], ast.Constant)
            and isinstance(node.args[0].value, str)
        ):
            input_id = node.args[0].value
            if input_id not in self.inputs:
                self.inputs[input_id] = node.lineno
                self.input_files[input_id] = getattr(node, "source_file", "")
            is_password_input = func_name == "ui.input_password" or any(
                s in input_id.lower()
                for s in ("password", "secret", "token", "api_key", "apikey")
            )
            if is_password_input:
                self.input_defaults[input_id] = "[REDACTED]"
            else:
                default_val = None
                for kw in node.keywords:
                    if kw.arg == "value" and isinstance(kw.value, ast.Constant):
                        default_val = kw.value.value
                if default_val is None:
                    if (
                        func_name
                        in (
                            "ui.input_numeric",
                            "ui.input_text",
                            "ui.input_text_area",
                        )
                        and len(node.args) >= 3
                        and isinstance(node.args[2], ast.Constant)
                    ):
                        default_val = node.args[2].value
                    elif (
                        func_name == "ui.input_slider"
                        and len(node.args) >= 5
                        and isinstance(node.args[4], ast.Constant)
                    ):
                        default_val = node.args[4].value
                if default_val is not None:
                    self.input_defaults[input_id] = default_val

        is_isolate_call = func_name in (
            "reactive.isolate",
            "isolate",
        ) or func_name.endswith(".isolate")
        if is_isolate_call:
            self.isolated_depth += 1
            for arg in node.args:
                self.visit(arg)
            for kw in node.keywords:
                self.visit(kw.value)
            self.isolated_depth -= 1
            return

        # Event handlers isolate body reads; keep those relationships visible
        # without treating them as invalidation triggers.
        isolated = self.isolated_depth > 0 or self.event_depth > 0
        dep_key = "isolated_deps" if isolated else "deps"
        calc_key = "isolated_calc_deps" if isolated else "calc_deps"

        if (
            isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "input"
        ):
            target_input = node.func.attr
            self.input_files.setdefault(target_input, getattr(node, "source_file", ""))
            if self.current_output and self.current_output in self.outputs:
                self.outputs[self.current_output][dep_key].add(target_input)
            elif self.current_effect and self.current_effect in self.effects:
                self.effects[self.current_effect][dep_key].add(target_input)
            elif self.current_calc and self.current_calc in self.calcs:
                self.calcs[self.current_calc][dep_key].add(target_input)

        if isinstance(node.func, ast.Name):
            called_name = node.func.id
            if self.current_output and self.current_output in self.outputs:
                self.outputs[self.current_output][calc_key].add(called_name)
            elif self.current_effect and self.current_effect in self.effects:
                self.effects[self.current_effect][calc_key].add(called_name)
            elif self.current_calc and self.current_calc in self.calcs:
                self.calcs[self.current_calc][calc_key].add(called_name)

        self.generic_visit(node)

    def _get_decorator_name(self, d: ast.AST) -> str:
        if isinstance(d, ast.Call):
            d = d.func
        parts: List[str] = []
        while isinstance(d, ast.Attribute):
            parts.append(d.attr)
            d = d.value
        if isinstance(d, ast.Name):
            parts.append(d.id)
            return ".".join(reversed(parts)).removeprefix("shiny.")
        return ""

    def _extract_event_triggers(self, d: ast.AST) -> tuple[Set[str], Set[str]]:
        input_deps: Set[str] = set()
        calc_deps: Set[str] = set()

        if not isinstance(d, ast.Call):
            return input_deps, calc_deps

        def _process_expr(expr: ast.AST) -> None:
            if (
                isinstance(expr, ast.Attribute)
                and isinstance(expr.value, ast.Name)
                and expr.value.id == "input"
            ):
                input_deps.add(expr.attr)
            elif isinstance(expr, ast.Call):
                if (
                    isinstance(expr.func, ast.Attribute)
                    and isinstance(expr.func.value, ast.Name)
                    and expr.func.value.id == "input"
                ):
                    input_deps.add(expr.func.attr)
                elif isinstance(expr.func, ast.Name):
                    calc_deps.add(expr.func.id)
            elif isinstance(expr, ast.Name):
                calc_deps.add(expr.id)
            elif isinstance(expr, (ast.Tuple, ast.List)):
                for elt in expr.elts:
                    _process_expr(elt)

        for arg in d.args:
            _process_expr(arg)

        return input_deps, calc_deps

    def _handle_func_def(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        decorators: List[str] = [
            name for d in node.decorator_list if (name := self._get_decorator_name(d))
        ]

        has_event_decorator = False
        event_input_deps: Set[str] = set()
        event_calc_deps: Set[str] = set()

        for d in node.decorator_list:
            d_name = self._get_decorator_name(d)
            if d_name in ("event", "reactive.event"):
                has_event_decorator = True
                inp_d, c_d = self._extract_event_triggers(d)
                event_input_deps.update(inp_d)
                event_calc_deps.update(c_d)

        is_effect = any(
            d in ("effect", "Effect", "reactive.effect", "reactive.Effect")
            for d in decorators
        )
        is_render = any(
            d.startswith("render.") or d.startswith("render_") for d in decorators
        )
        is_calc = (
            any(
                d in ("calc", "Calc", "reactive.calc", "reactive.Calc")
                for d in decorators
            )
            and not is_effect
            and not is_render
        )

        prev_out = self.current_output
        prev_effect = self.current_effect
        prev_calc = self.current_calc

        if is_render:
            self.current_output = node.name
            self.outputs[node.name] = {
                "render_type": next(
                    (d.split(".")[-1] for d in decorators if d.startswith("render.")),
                    "output",
                ),
                "line": node.lineno,
                "source_file": getattr(node, "source_file", ""),
                "deps": set(event_input_deps),
                "calc_deps": set(event_calc_deps),
                "isolated_deps": set(),
                "isolated_calc_deps": set(),
                "is_async": isinstance(node, ast.AsyncFunctionDef),
            }
        elif is_effect:
            self.current_effect = node.name
            self.effects[node.name] = {
                "line": node.lineno,
                "source_file": getattr(node, "source_file", ""),
                "deps": set(event_input_deps),
                "calc_deps": set(event_calc_deps),
                "isolated_deps": set(),
                "isolated_calc_deps": set(),
                "is_async": isinstance(node, ast.AsyncFunctionDef),
            }
        elif is_calc:
            self.current_calc = node.name
            self.calcs[node.name] = {
                "line": node.lineno,
                "source_file": getattr(node, "source_file", ""),
                "deps": set(event_input_deps),
                "calc_deps": set(event_calc_deps),
                "isolated_deps": set(),
                "isolated_calc_deps": set(),
                "is_async": isinstance(node, ast.AsyncFunctionDef),
            }

        if has_event_decorator:
            self.event_depth += 1

        for stmt in node.body:
            self.visit(stmt)

        if has_event_decorator:
            self.event_depth -= 1

        self.current_output = prev_out
        self.current_effect = prev_effect
        self.current_calc = prev_calc

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._handle_func_def(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._handle_func_def(node)


def inspect_reactive_graph(
    code: str, source_path: str | Path | None = None
) -> Dict[str, Any]:
    sources: Dict[str, str] = {}
    entry_file = ""
    try:
        if source_path is not None:
            from ._inspect_sources import read_app_sources

            tree, sources, entry_file = read_app_sources(code, source_path)
        else:
            tree = ast.parse(code)
    except SyntaxError as e:
        return {
            "success": False,
            "error": f"SyntaxError: {e.msg} ({e.filename}:{e.lineno})",
            "nodes": [],
            "edges": [],
            "summary": "Syntax error in source code",
        }

    tree, module_members = _expand_module_calls(tree)
    visitor = GraphVisitor()
    visitor.visit(tree)

    known_calcs = set(visitor.calcs.keys())

    referenced_inputs: Set[str] = set()
    for meta in visitor.outputs.values():
        referenced_inputs.update(meta["deps"])
        referenced_inputs.update(meta.get("isolated_deps", set()))
    for meta in visitor.effects.values():
        referenced_inputs.update(meta["deps"])
        referenced_inputs.update(meta.get("isolated_deps", set()))
    for meta in visitor.calcs.values():
        referenced_inputs.update(meta["deps"])
        referenced_inputs.update(meta.get("isolated_deps", set()))

    all_inputs = set(visitor.inputs.keys()) | referenced_inputs

    nodes: List[Dict[str, Any]] = []
    for inp in sorted(all_inputs):
        is_declared = inp in visitor.inputs
        line = visitor.inputs.get(inp)
        default_val = visitor.input_defaults.get(inp)
        nodes.append(
            {
                "id": f"input:{inp}",
                "name": inp,
                "type": "input",
                "role": "source",
                "label": f"input.{inp}",
                "line": line,
                "value": default_val,
                "declaration": "declared" if is_declared else "unresolved",
                "source_file": visitor.input_files.get(inp, ""),
            }
        )
    for c, meta in sorted(visitor.calcs.items()):
        nodes.append(
            {
                "id": f"calc:{c}",
                "name": c,
                "type": "calc",
                "role": "conductor",
                "label": f"calc:{c}",
                "line": meta["line"],
                "source_file": meta.get("source_file", ""),
            }
        )
    for eff, meta in sorted(visitor.effects.items()):
        nodes.append(
            {
                "id": f"effect:{eff}",
                "name": eff,
                "type": "effect",
                "role": "observer",
                "label": f"effect:{eff}",
                "line": meta["line"],
                "source_file": meta.get("source_file", ""),
            }
        )
    for out, meta in sorted(visitor.outputs.items()):
        nodes.append(
            {
                "id": f"output:{out}",
                "name": out,
                "type": "output",
                "role": "observer",
                "label": f"output:{out}",
                "render_type": meta["render_type"],
                "line": meta["line"],
                "source_file": meta.get("source_file", ""),
            }
        )

    edges: List[Dict[str, Any]] = []
    for out_name, meta in visitor.outputs.items():
        for dep in sorted(meta["deps"]):
            edges.append({"from": f"input:{dep}", "to": f"output:{out_name}"})
        for cdep in sorted(meta["calc_deps"]):
            if cdep in known_calcs:
                edges.append({"from": f"calc:{cdep}", "to": f"output:{out_name}"})
        for dep in sorted(meta.get("isolated_deps", set())):
            if dep not in meta["deps"]:
                edges.append(
                    {
                        "from": f"input:{dep}",
                        "to": f"output:{out_name}",
                        "isolated": True,
                    }
                )
        for cdep in sorted(meta.get("isolated_calc_deps", set())):
            if cdep in known_calcs and cdep not in meta["calc_deps"]:
                edges.append(
                    {
                        "from": f"calc:{cdep}",
                        "to": f"output:{out_name}",
                        "isolated": True,
                    }
                )

    for eff_name, meta in visitor.effects.items():
        for dep in sorted(meta["deps"]):
            edges.append({"from": f"input:{dep}", "to": f"effect:{eff_name}"})
        for cdep in sorted(meta["calc_deps"]):
            if cdep in known_calcs:
                edges.append({"from": f"calc:{cdep}", "to": f"effect:{eff_name}"})
        for dep in sorted(meta.get("isolated_deps", set())):
            if dep not in meta["deps"]:
                edges.append(
                    {
                        "from": f"input:{dep}",
                        "to": f"effect:{eff_name}",
                        "isolated": True,
                    }
                )
        for cdep in sorted(meta.get("isolated_calc_deps", set())):
            if cdep in known_calcs and cdep not in meta["calc_deps"]:
                edges.append(
                    {
                        "from": f"calc:{cdep}",
                        "to": f"effect:{eff_name}",
                        "isolated": True,
                    }
                )

    for calc_name, meta in visitor.calcs.items():
        for dep in sorted(meta["deps"]):
            edges.append({"from": f"input:{dep}", "to": f"calc:{calc_name}"})
        for cdep in sorted(meta["calc_deps"]):
            if cdep in known_calcs and cdep != calc_name:
                edges.append({"from": f"calc:{cdep}", "to": f"calc:{calc_name}"})
        for dep in sorted(meta.get("isolated_deps", set())):
            if dep not in meta["deps"]:
                edges.append(
                    {
                        "from": f"input:{dep}",
                        "to": f"calc:{calc_name}",
                        "isolated": True,
                    }
                )
        for cdep in sorted(meta.get("isolated_calc_deps", set())):
            if (
                cdep in known_calcs
                and cdep != calc_name
                and cdep not in meta["calc_deps"]
            ):
                edges.append(
                    {
                        "from": f"calc:{cdep}",
                        "to": f"calc:{calc_name}",
                        "isolated": True,
                    }
                )

    for node in nodes:
        if node["name"] in module_members:
            node["module"] = module_members[node["name"]]

    total_observers = len(visitor.outputs) + len(visitor.effects)
    return {
        "success": True,
        "nodes": nodes,
        "edges": edges,
        "input_defaults": visitor.input_defaults,
        "sources": sources,
        "entry_file": entry_file,
        "summary": f"{len(all_inputs)} inputs (sources), {len(visitor.calcs)} reactives (conductors), {total_observers} outputs & effects (observers)",
    }


def _is_plot_data_url(src: Any) -> bool:
    return isinstance(src, str) and src.startswith(
        (
            "data:image/png;base64,",
            "data:image/jpeg;base64,",
            "data:image/gif;base64,",
            "data:image/webp;base64,",
        )
    )


def _make_event(
    step: int,
    event: str,
    phase: str,
    provenance: str,
    node_id: Optional[str] = None,
    node_label: Optional[str] = None,
    node_type: Optional[str] = None,
    status: str = "idle",
    timestamp: int = 0,
    time_sec: float = 0.0,
    value: Optional[str] = None,
    edge_from: Optional[str] = None,
    edge_to: Optional[str] = None,
    details: str = "",
    session: str = "default",
    action: Optional[str] = None,
) -> Dict[str, Any]:
    act = action
    if not act:
        if event == "analysisInit":
            act = "createContext"
        elif event in ("define",):
            act = "define"
        elif event in ("inputChange", "assumeValue", "outputUpdated"):
            act = "valueChange"
        elif event in ("userClick",):
            act = "userAction"
        elif event in ("propagate",):
            act = "invalidate"
        elif event in ("orderingStart", "orderingComplete", "recordingComplete"):
            act = "idle"
        elif event in ("wouldEvaluate",):
            act = "enter"
        elif event in ("dependsOn",):
            act = "dependsOn"
        elif event in ("ordered",):
            act = "exit"
        else:
            act = event

    if provenance == "observed" and event in (
        "inputChange",
        "userClick",
        "userAction",
        "recalculate",
        "output",
        "render",
        "outputUpdated",
        "valueChange",
    ):
        semantic_state = "observed_execution"
    elif event in ("wouldEvaluate", "inferred"):
        semantic_state = "inferred_execution"
    elif event in ("propagate", "invalidate"):
        semantic_state = "invalidated"
    elif event in (
        "define",
        "dependsOn",
        "createContext",
        "sessionInit",
        "analysisInit",
    ):
        semantic_state = "dependency_only"
    else:
        semantic_state = "idle"

    item: Dict[str, Any] = {
        "step": step,
        "action": act,
        "event": event,
        "semantic_state": semantic_state,
        "id": node_id,
        "reactId": node_id,
        "node_id": node_id,
        "label": node_label,
        "node_label": node_label,
        "type": node_type,
        "node_type": node_type,
        "status": status,
        "phase": phase,
        "provenance": provenance,
        "time": time_sec,
        "time_sec": time_sec,
        "timestamp": timestamp,
        "value": value,
        "session": session,
        "details": details,
    }
    if act == "dependsOn" or edge_from:
        item["dependsOn"] = edge_from
        item["depOnReactId"] = edge_from
        item["edge_from"] = edge_from
        item["edge_to"] = edge_to
    elif edge_from or edge_to:
        item["edge_from"] = edge_from
        item["edge_to"] = edge_to
    return item


def generate_reactlog(
    code: str,
    inputs: Optional[Dict[str, Any]] = None,
    recorded_actions: Optional[List[Dict[str, Any]]] = None,
    video_path: Optional[str] = None,
    session: str = "default",
    source_path: str | Path | None = None,
    marks: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    user_marks: List[Dict[str, Any]] = list(marks) if marks is not None else []

    graph = inspect_reactive_graph(code, source_path=source_path)
    if not graph.get("success"):
        return graph

    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])
    entry_file = graph.get("entry_file")
    source_files: dict[Path, str] = {}
    if source_path and entry_file:
        source_root = (
            Path(source_path).resolve().parents[len(Path(entry_file).parts) - 1]
        )
        source_files = {
            (source_root / filename).resolve(): filename
            for filename in graph.get("sources", {})
        }
    events: List[Dict[str, Any]] = []
    step = 0

    adj_downstream: Dict[str, List[str]] = {}
    adj_upstream: Dict[str, List[str]] = {}
    for edge in edges:
        # Isolated reads are visible relationships, not invalidation triggers.
        if edge.get("isolated"):
            continue
        f, t = edge["from"], edge["to"]
        adj_downstream.setdefault(f, []).append(t)
        adj_upstream.setdefault(t, []).append(f)

    nodes_by_id = {n["id"]: n for n in nodes}

    events.append(
        _make_event(
            step=step,
            event="analysisInit",
            phase="init",
            provenance="inferred",
            node_id=None,
            node_label="session",
            node_type="session",
            status="active",
            timestamp=0,
            time_sec=0.0,
            details=(
                "Initialized reactive session with recorded Playwright interactions"
                if recorded_actions
                else "Started static AST dependency analysis; app code was not executed"
            ),
            session=session,
        )
    )
    step += 1

    for node in nodes:
        initial_val = (inputs or {}).get(node.get("name", ""))
        if initial_val is None:
            initial_val = node.get("value")
        events.append(
            _make_event(
                step=step,
                event="define",
                phase="init",
                provenance="inferred",
                node_id=node["id"],
                node_label=node["label"],
                node_type=node["role"],
                status="discovered",
                timestamp=0,
                time_sec=0.0,
                value=str(initial_val) if initial_val is not None else None,
                details=f"Discovered {node['role']} node '{node['label']}' at line {node.get('line', '?')}",
                session=session,
            )
        )
        step += 1

    def compute_evaluation_order(invalidated: Set[str]) -> List[Dict[str, Any]]:
        conductor_ids = {
            n["id"]
            for n in nodes
            if n["role"] == "conductor" and n["id"] in invalidated
        }
        conductor_in_degree: Dict[str, int] = {cid: 0 for cid in conductor_ids}
        for cid in conductor_ids:
            for up in adj_upstream.get(cid, []):
                if up in conductor_ids:
                    conductor_in_degree[cid] += 1

        queue = deque(
            [cid for cid, deg in sorted(conductor_in_degree.items()) if deg == 0]
        )
        sorted_conductors: List[str] = []
        while queue:
            curr = queue.popleft()
            sorted_conductors.append(curr)
            for down in adj_downstream.get(curr, []):
                if down in conductor_in_degree:
                    conductor_in_degree[down] -= 1
                    if conductor_in_degree[down] == 0:
                        queue.append(down)

        for cid in sorted(conductor_ids):
            if cid not in sorted_conductors:
                sorted_conductors.append(cid)

        observer_nodes = [
            n for n in nodes if n["role"] == "observer" and n["id"] in invalidated
        ]

        return [
            nodes_by_id[cid] for cid in sorted_conductors if cid in nodes_by_id
        ] + observer_nodes

    def cascade_record_invalidate(
        nid: str, cur_step: int, invalidated: Set[str], ts_ms: int, ts_s: float
    ) -> int:
        nid_lbl = nodes_by_id.get(nid, {}).get("label", nid)
        for down in adj_downstream.get(nid, []):
            if down not in invalidated:
                invalidated.add(down)
                node_obj = nodes_by_id.get(down, {})
                down_lbl = node_obj.get("label", down)
                events.append(
                    _make_event(
                        step=cur_step,
                        event="propagate",
                        phase="interaction",
                        provenance="inferred",
                        node_id=down,
                        node_label=down_lbl,
                        node_type=node_obj.get("role", "conductor"),
                        status="affected",
                        timestamp=ts_ms,
                        time_sec=ts_s,
                        edge_from=nid,
                        edge_to=down,
                        details=f"Inferred invalidation of '{down_lbl}' by '{nid_lbl}'",
                        session=session,
                    )
                )
                cur_step += 1
                cur_step = cascade_record_invalidate(
                    down, cur_step, invalidated, ts_ms, ts_s
                )
        return cur_step

    unmatched_inputs: List[str] = []
    action_waves: List[Dict[str, Any]] = [
        {
            "action_id": "burst-init",
            "index": 0,
            "is_init": True,
            "start_time": 0.0,
            "end_time": 0.0,
            "start_step": 0,
            "end_step": step - 1,
            "trigger": "Init",
            "trigger_label": "Init",
            "short_label": "Init",
            "human_action": "Init",
            "trigger_node_id": "",
            "trigger_value": None,
            "invalidated_nodes": [],
            "inferred_executions": [n["id"] for n in nodes if n["role"] != "source"],
            "observed_executions": [],
            "observed_outputs": [],
        }
    ]

    epoch_marks = [
        float(m.get("time") or 0.0)
        for m in user_marks
        if float(m.get("time") or 0.0) > 1_000_000_000
    ]
    if epoch_marks:
        min_epoch = min(epoch_marks)
        for m in user_marks:
            t = float(m.get("time") or 0.0)
            if t > 1_000_000_000:
                rel_t = round(max(0.0, t - min_epoch), 2)
                m["time"] = rel_t
                m["timestamp"] = int(rel_t * 1000)

    def append_single_mark(m: Dict[str, Any], cur_step: int) -> int:
        mark_label = str(m.get("label", "Bookmark"))
        mark_time = float(m.get("time") or 0.0)
        mark_ms = int(m.get("timestamp") or (mark_time * 1000))
        events.append(
            _make_event(
                step=cur_step,
                event="userMark",
                action="userMark",
                phase="interaction",
                provenance="observed",
                node_id=None,
                node_label=f"🔖 {mark_label}",
                node_type="mark",
                status="active",
                timestamp=mark_ms,
                time_sec=mark_time,
                details=f"User mark: {mark_label}",
                session=session,
            )
        )
        filename = m.get("source_file")
        if isinstance(filename, str):
            source_file = source_files.get(Path(filename).resolve())
            if source_file:
                events[-1].update(source_file=source_file, line=m.get("line"))
        action_waves.append(
            {
                "action_id": f"mark-{len(action_waves)}",
                "index": len(action_waves),
                "is_init": False,
                "is_mark": True,
                "start_time": mark_time,
                "end_time": mark_time,
                "start_step": cur_step,
                "end_step": cur_step,
                "trigger": f"Bookmark: {mark_label}",
                "trigger_label": f"🔖 {mark_label}",
                "short_label": f"🔖 {mark_label[:20]}",
                "human_action": f"Mark: {mark_label}",
                "trigger_node_id": "",
                "trigger_value": None,
                "invalidated_nodes": [],
                "inferred_executions": [],
                "observed_executions": [],
                "observed_outputs": [],
            }
        )
        return cur_step + 1

    def append_user_marks(cur_step: int) -> int:
        for m in user_marks:
            cur_step = append_single_mark(m, cur_step)
        return cur_step

    if recorded_actions:
        deduped_actions: List[Dict[str, Any]] = []
        last_input_action: Dict[str, tuple[Any, int]] = {}
        for act in recorded_actions:
            atype = act.get("type")
            aname = act.get("name")
            aval = act.get("value")
            ats = int(act.get("timestamp") or 0)
            if atype == "input" and aname:
                last_val, last_time = last_input_action.get(aname, (None, -999999))
                if str(last_val) == str(aval) and (ats - last_time) < 250:
                    continue
                last_input_action[aname] = (aval, ats)
            deduped_actions.append(act)

        last_known_vals: Dict[str, Any] = {
            n.get("name", n["id"]): n.get("value") for n in nodes
        }

        def _mark_time(m: Dict[str, Any]) -> float:
            return float(m.get("time") or 0.0)

        sorted_user_marks = sorted(user_marks, key=_mark_time)
        mark_idx = 0
        last_ts = 0
        for action in deduped_actions:
            ts = action.get("timestamp")
            if ts is not None:
                last_ts = int(ts)
            ts_ms = last_ts
            ts_sec = round(ts_ms / 1000.0, 2)

            while (
                mark_idx < len(sorted_user_marks)
                and float(sorted_user_marks[mark_idx].get("time") or 0.0) <= ts_sec
            ):
                step = append_single_mark(sorted_user_marks[mark_idx], step)
                mark_idx += 1

            action_start_step = step
            action_type = action.get("type", "action")
            raw_name = str(action.get("name") or action.get("target") or "unknown")
            action_val = action.get("value")

            if action_type == "input":
                node_id = (
                    f"input:{raw_name}"
                    if f"input:{raw_name}" in nodes_by_id
                    else (raw_name if raw_name in nodes_by_id else None)
                )
                if node_id and node_id in nodes_by_id:
                    node_obj = nodes_by_id[node_id]
                    events.append(
                        _make_event(
                            step=step,
                            event="inputChange",
                            phase="interaction",
                            provenance="observed",
                            node_id=node_id,
                            node_label=node_obj["label"],
                            node_type="source",
                            status="assumed",
                            timestamp=ts_ms,
                            time_sec=ts_sec,
                            value=str(action_val),
                            details=f"Observed browser input change: {node_obj['label']} = {action_val!r}",
                            session=session,
                        )
                    )
                    step += 1

                    invalidated_nodes: Set[str] = set()
                    step = cascade_record_invalidate(
                        node_id, step, invalidated_nodes, ts_ms, ts_sec
                    )

                    eval_order = compute_evaluation_order(invalidated_nodes)
                    for target in eval_order:
                        tid = target["id"]
                        tlabel = target["label"]
                        trole = target["role"]

                        events.append(
                            _make_event(
                                step=step,
                                event="wouldEvaluate",
                                phase="interaction",
                                provenance="inferred",
                                node_id=tid,
                                node_label=tlabel,
                                node_type=trole,
                                status="scheduled",
                                timestamp=ts_ms,
                                time_sec=ts_sec,
                                details=f"Inferred evaluation: '{tlabel}' (static topological order)",
                                session=session,
                            )
                        )
                        step += 1

                        for dep in adj_upstream.get(tid, []):
                            dep_lbl = nodes_by_id.get(dep, {}).get("label", dep)
                            events.append(
                                _make_event(
                                    step=step,
                                    event="dependsOn",
                                    phase="interaction",
                                    provenance="inferred",
                                    node_id=tid,
                                    node_label=tlabel,
                                    node_type=trole,
                                    status="scheduled",
                                    timestamp=ts_ms,
                                    time_sec=ts_sec,
                                    edge_from=dep,
                                    edge_to=tid,
                                    details=f"Inferred dependency: '{dep_lbl}' used by '{tlabel}'",
                                    session=session,
                                )
                            )
                            step += 1

                        events.append(
                            _make_event(
                                step=step,
                                event="ordered",
                                phase="interaction",
                                provenance="inferred",
                                node_id=tid,
                                node_label=tlabel,
                                node_type=trole,
                                status="scheduled",
                                timestamp=ts_ms,
                                time_sec=ts_sec,
                                details=f"Inferred completed state for '{tlabel}'",
                                session=session,
                            )
                        )
                        step += 1

                    prev_v = last_known_vals.get(raw_name)
                    if (
                        prev_v is not None
                        and action_val is not None
                        and str(prev_v) != str(action_val)
                    ):
                        human_trigger = f"{raw_name}: {prev_v} → {action_val}"
                    elif action_val is not None:
                        human_trigger = f"{raw_name}: {action_val}"
                    else:
                        human_trigger = f"{raw_name} changed"
                    if action_val is not None:
                        last_known_vals[raw_name] = action_val

                    action_waves.append(
                        {
                            "action_id": f"burst-{len(action_waves)}",
                            "index": len(action_waves),
                            "is_init": False,
                            "start_time": ts_sec,
                            "end_time": ts_sec,
                            "start_step": action_start_step,
                            "end_step": step - 1,
                            "trigger": human_trigger,
                            "trigger_label": raw_name,
                            "short_label": raw_name,
                            "human_action": human_trigger,
                            "trigger_node_id": node_id,
                            "trigger_value": (
                                str(action_val) if action_val is not None else None
                            ),
                            "invalidated_nodes": sorted(list(invalidated_nodes)),
                            "inferred_executions": [t["id"] for t in eval_order],
                            "observed_executions": [node_id],
                            "observed_outputs": [
                                t["id"] for t in eval_order if t["role"] == "observer"
                            ],
                        }
                    )
                else:
                    unmatched_inputs.append(raw_name)
                    events.append(
                        _make_event(
                            step=step,
                            event="inputChange",
                            phase="interaction",
                            provenance="observed",
                            node_id=None,
                            node_label=f"input.{raw_name}",
                            node_type="source",
                            status="assumed",
                            timestamp=ts_ms,
                            time_sec=ts_sec,
                            value=str(action_val),
                            details=f"Observed browser input change (unmatched node): input.{raw_name} = {action_val!r}",
                            session=session,
                        )
                    )
                    step += 1

            elif action_type in ("output", "outputError"):
                is_error = action_type == "outputError"
                out_id = (
                    f"output:{raw_name}"
                    if f"output:{raw_name}" in nodes_by_id
                    else (raw_name if raw_name in nodes_by_id else None)
                )
                node_lbl = (
                    nodes_by_id[out_id]["label"]
                    if out_id and out_id in nodes_by_id
                    else f"output:{raw_name}"
                )
                events.append(
                    _make_event(
                        step=step,
                        event="outputError" if is_error else "outputUpdated",
                        phase="interaction",
                        provenance="observed",
                        node_id=out_id,
                        node_label=node_lbl,
                        node_type="observer",
                        status="scheduled",
                        timestamp=ts_ms,
                        time_sec=ts_sec,
                        details=(
                            f"Observed browser output error: {node_lbl}"
                            if is_error
                            else f"Observed browser output render: {node_lbl}"
                        ),
                        session=session,
                    )
                )
                if is_error:
                    events[-1]["error"] = str(action.get("error", ""))
                preview = action.get("plot")
                if isinstance(preview, dict):
                    plot_dict = cast(Dict[str, Any], preview)
                    plot_src = plot_dict.get("src")
                    if _is_plot_data_url(plot_src):
                        plot_alt = plot_dict.get("alt")
                        events[-1]["plot"] = {
                            "src": str(plot_src),
                            "alt": str(plot_alt) if plot_alt else node_lbl,
                        }
                step += 1

            elif action_type == "click":
                events.append(
                    _make_event(
                        step=step,
                        event="userClick",
                        phase="interaction",
                        provenance="observed",
                        node_id=None,
                        node_label=raw_name,
                        node_type="user",
                        status="active",
                        timestamp=ts_ms,
                        time_sec=ts_sec,
                        details=f"Observed user click: {action.get('text', raw_name)}",
                        session=session,
                    )
                )
                step += 1

                action_waves.append(
                    {
                        "action_id": f"burst-{len(action_waves)}",
                        "index": len(action_waves),
                        "is_init": False,
                        "start_time": ts_sec,
                        "end_time": ts_sec,
                        "start_step": action_start_step,
                        "end_step": step - 1,
                        "trigger": f"Click: {action.get('text', raw_name)}",
                        "trigger_label": f"Click: {action.get('text', raw_name)}",
                        "short_label": f"Click: {action.get('text', raw_name)[:12]}",
                        "human_action": f"Click: {action.get('text', raw_name)}",
                        "trigger_node_id": "",
                        "trigger_value": None,
                        "invalidated_nodes": [],
                        "inferred_executions": [],
                        "observed_executions": [],
                        "observed_outputs": [],
                    }
                )

        while mark_idx < len(sorted_user_marks):
            step = append_single_mark(sorted_user_marks[mark_idx], step)
            mark_idx += 1

        events.append(
            _make_event(
                step=step,
                event="recordingComplete",
                phase="interaction",
                provenance="inferred",
                node_id=None,
                node_label="session",
                node_type="engine",
                status="idle",
                timestamp=last_ts,
                time_sec=round(last_ts / 1000.0, 2),
                details="Playwright recording complete",
                session=session,
            )
        )
        step += 1

        obs_count = len([e for e in events if e.get("provenance") == "observed"])
        inf_count = len([e for e in events if e.get("provenance") == "inferred"])
        events[-1][
            "details"
        ] = f"Playwright recording finished: {obs_count} observed browser event(s), {inf_count} inferred dependency step(s)"

        init_count = len([e for e in events if e.get("phase") == "init"])
        interact_count = len([e for e in events if e.get("phase") == "interaction"])
        first_interact = next(
            (i for i, e in enumerate(events) if e.get("phase") == "interaction"), 0
        )

        return {
            "success": True,
            "version": "1.0",
            "session": session,
            "trace_kind": "inferred_simulation_with_recorded_browser_events",
            "nodes": nodes,
            "sources": graph.get("sources", {}),
            "entry_file": graph.get("entry_file", ""),
            "edges": edges,
            "events": events,
            "log": events,
            "action_waves": action_waves,
            "marks": user_marks,
            "steps_total": len(events),
            "init_steps_count": init_count,
            "interaction_steps_count": interact_count,
            "first_interaction_step": first_interact,
            "observed_events_count": obs_count,
            "inferred_events_count": inf_count,
            "unmatched_inputs": unmatched_inputs,
            "unmatched_inputs_count": len(unmatched_inputs),
            "recorded_actions": deduped_actions,
            "video_path": video_path,
            "disclaimer": "Server reactive execution is statically inferred from AST dependency analysis. Dynamic dependencies or isolated reactives may not appear in this graph.",
            "summary": f"Observed {obs_count} browser event(s); inferred {inf_count} simulated dependency steps across {len(nodes)} graph nodes",
        }

    sim_inputs = dict(inputs or {})
    if not sim_inputs:
        input_nodes = [n for n in nodes if n["role"] == "source"]
        for n in input_nodes:
            sim_inputs[n["name"]] = 10

    invalidated_nodes_static: Set[str] = set()

    def cascade_invalidate(nid: str, cur_step: int) -> int:
        nid_lbl = nodes_by_id.get(nid, {}).get("label", nid)
        for down in adj_downstream.get(nid, []):
            if down not in invalidated_nodes_static:
                invalidated_nodes_static.add(down)
                node_obj = nodes_by_id.get(down, {})
                down_lbl = node_obj.get("label", down)
                events.append(
                    _make_event(
                        step=cur_step,
                        event="propagate",
                        phase="interaction",
                        provenance="inferred",
                        node_id=down,
                        node_label=down_lbl,
                        node_type=node_obj.get("role", "conductor"),
                        status="affected",
                        timestamp=0,
                        time_sec=0.0,
                        edge_from=nid,
                        edge_to=down,
                        details=f"Inferred invalidation of '{down_lbl}' from '{nid_lbl}'",
                        session=session,
                    )
                )
                cur_step += 1
                cur_step = cascade_invalidate(down, cur_step)
        return cur_step

    for input_name, input_val in sim_inputs.items():
        node_id = (
            f"input:{input_name}"
            if f"input:{input_name}" in nodes_by_id
            else (input_name if input_name in nodes_by_id else input_name)
        )
        node_lbl = nodes_by_id.get(node_id, {}).get("label", f"input.{input_name}")
        events.append(
            _make_event(
                step=step,
                event="assumeValue",
                phase="interaction",
                provenance="inferred",
                node_id=node_id,
                node_label=node_lbl,
                node_type="source",
                status="assumed",
                timestamp=0,
                time_sec=0.0,
                value=str(input_val),
                details=f"Simulation assumes {node_lbl} is set to {input_val!r}",
                session=session,
            )
        )
        step += 1
        step = cascade_invalidate(node_id, step)

    events.append(
        _make_event(
            step=step,
            event="orderingStart",
            phase="interaction",
            provenance="inferred",
            node_id=None,
            node_label="reactiveEnvironment",
            node_type="engine",
            status="active",
            timestamp=0,
            time_sec=0.0,
            details=f"Simulating static ordering for {len(invalidated_nodes_static)} affected node(s)",
            session=session,
        )
    )
    step += 1

    eval_order = compute_evaluation_order(invalidated_nodes_static)
    for target in eval_order:
        tid = target["id"]
        tlabel = target["label"]
        trole = target["role"]

        events.append(
            _make_event(
                step=step,
                event="wouldEvaluate",
                phase="interaction",
                provenance="inferred",
                node_id=tid,
                node_label=tlabel,
                node_type=trole,
                status="scheduled",
                timestamp=0,
                time_sec=0.0,
                details=f"Inferred evaluation: '{tlabel}' (static topological order; not executed)",
                session=session,
            )
        )
        step += 1

        for dep in adj_upstream.get(tid, []):
            dep_lbl = nodes_by_id.get(dep, {}).get("label", dep)
            events.append(
                _make_event(
                    step=step,
                    event="dependsOn",
                    phase="interaction",
                    provenance="inferred",
                    node_id=tid,
                    node_label=tlabel,
                    node_type=trole,
                    status="scheduled",
                    timestamp=0,
                    time_sec=0.0,
                    edge_from=dep,
                    edge_to=tid,
                    details=f"Inferred dependency edge: '{dep_lbl}' used by '{tlabel}'",
                    session=session,
                )
            )
            step += 1

        events.append(
            _make_event(
                step=step,
                event="ordered",
                phase="interaction",
                provenance="inferred",
                node_id=tid,
                node_label=tlabel,
                node_type=trole,
                status="scheduled",
                timestamp=0,
                time_sec=0.0,
                details=f"Inferred completed state for '{tlabel}'",
                session=session,
            )
        )
        step += 1

    step = append_user_marks(step)

    events.append(
        _make_event(
            step=step,
            event="orderingComplete",
            phase="interaction",
            provenance="inferred",
            node_id=None,
            node_label="reactiveEnvironment",
            node_type="engine",
            status="idle",
            timestamp=0,
            time_sec=0.0,
            details=f"Static ordering contains {len(eval_order)} nodes; no reactive update occurred",
            session=session,
        )
    )

    init_count = len([e for e in events if e.get("phase") == "init"])
    interact_count = len([e for e in events if e.get("phase") == "interaction"])
    first_interact = next(
        (i for i, e in enumerate(events) if e.get("phase") == "interaction"), 0
    )

    return {
        "success": True,
        "version": "1.0",
        "session": session,
        "trace_kind": "static_inferred_simulation",
        "sources": graph.get("sources", {}),
        "entry_file": graph.get("entry_file", ""),
        "nodes": nodes,
        "edges": edges,
        "events": events,
        "log": events,
        "action_waves": action_waves,
        "marks": user_marks,
        "steps_total": len(events),
        "init_steps_count": init_count,
        "interaction_steps_count": interact_count,
        "first_interaction_step": first_interact,
        "observed_events_count": 0,
        "inferred_events_count": len(events),
        "unmatched_inputs": [],
        "unmatched_inputs_count": 0,
        "disclaimer": "Server reactive execution is statically inferred from AST dependency analysis. Dynamic dependencies or isolated reactives may not appear in this graph.",
        "summary": f"Static dependency simulation: {len(events)} steps across {len(nodes)} nodes ({len(invalidated_nodes_static)} affected); app code was not executed",
    }


def load_reactlog_json(
    json_data: str | Dict[str, Any] | List[Any] | Any,
    source_code: Optional[str] = None,
) -> Dict[str, Any]:
    if isinstance(json_data, str):
        try:
            parsed: Any = json.loads(json_data)
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"Invalid JSON reactlog: {e}",
                "nodes": [],
                "edges": [],
                "events": [],
                "log": [],
                "summary": "Invalid JSON reactlog",
            }
    else:
        parsed = json_data

    version = "1.0"
    session_name = "default"
    raw_events: List[Dict[str, Any]] = []
    existing_nodes: Optional[List[Dict[str, Any]]] = None
    existing_edges: Optional[List[Dict[str, Any]]] = None

    if isinstance(parsed, list):
        for e in cast(List[Any], parsed):
            if isinstance(e, dict):
                raw_events.append(cast(Dict[str, Any], e))
    elif isinstance(parsed, dict):
        dict_data = cast(Dict[str, Any], parsed)
        version = str(dict_data.get("version", "1.0"))
        session_name = str(dict_data.get("session", "default"))
        nodes_field = dict_data.get("nodes")
        if isinstance(nodes_field, list):
            existing_nodes = []
            for n in cast(List[Any], nodes_field):
                if isinstance(n, dict):
                    existing_nodes.append(cast(Dict[str, Any], n))
        edges_field = dict_data.get("edges")
        if isinstance(edges_field, list):
            existing_edges = []
            for ed in cast(List[Any], edges_field):
                if isinstance(ed, dict):
                    existing_edges.append(cast(Dict[str, Any], ed))

        log_field = dict_data.get("log")
        events_field = dict_data.get("events")
        entries_field = dict_data.get("entries")
        target_field: Optional[List[Any]] = None
        if isinstance(log_field, list):
            target_field = cast(List[Any], log_field)
        elif isinstance(events_field, list):
            target_field = cast(List[Any], events_field)
        elif isinstance(entries_field, list):
            target_field = cast(List[Any], entries_field)

        if target_field is not None:
            for ev_item in target_field:
                if isinstance(ev_item, dict):
                    raw_events.append(cast(Dict[str, Any], ev_item))

    nodes_map: Dict[str, Dict[str, Any]] = {}
    edges_set: Set[tuple[str, str]] = set()

    if existing_nodes:
        for n in existing_nodes:
            nid = str(n.get("reactId") or n.get("id") or n.get("node_id") or "")
            if nid:
                nodes_map[nid] = dict(n)

    if existing_edges:
        for e in existing_edges:
            f = str(e.get("depOnReactId") or e.get("from") or e.get("dependsOn") or "")
            t = str(e.get("reactId") or e.get("to") or "")
            if f and t:
                edges_set.add((f, t))

    raw_times: List[float] = []
    for item in raw_events:
        t_val = (
            item.get("time")
            or item.get("time_sec")
            or (
                float(item.get("timestamp", 0)) / 1000.0
                if item.get("timestamp")
                else None
            )
        )
        if t_val is not None:
            try:
                raw_times.append(float(t_val))
            except (ValueError, TypeError):
                pass

    min_epoch_time = 0.0
    if raw_times and min(raw_times) > 100000.0:
        min_epoch_time = min(raw_times)

    for item in raw_events:
        act = str(item.get("action") or item.get("event") or "")
        nid = item.get("reactId") or item.get("node_id") or item.get("id")
        if not nid:
            continue
        nid_str = str(nid)
        raw_lbl = item.get("label") or item.get("node_label")
        existing = nodes_map.get(nid_str, {})
        if (
            nid_str not in nodes_map
            or act == "define"
            or (
                raw_lbl
                and str(raw_lbl) != nid_str
                and existing.get("label") in (None, "", nid_str)
            )
        ):
            ntype = (
                item.get("type")
                or item.get("node_type")
                or existing.get("type")
                or "calc"
            )
            role = "conductor"
            clean_type = str(ntype).lower()
            if clean_type in (
                "input",
                "reactiveval",
                "reactivevalueskey",
                "reactivevaluesnames",
                "reactivevaluesaslist",
            ) or nid_str.startswith("input:"):
                role = "source"
                clean_type = "input"
            elif (
                clean_type in ("observer", "output", "effect")
                or nid_str.startswith("output:")
                or nid_str.startswith("effect:")
            ):
                role = "observer"
                clean_type = "output"
            elif clean_type in ("calc", "reactive", "observable"):
                role = "conductor"
                clean_type = "calc"

            resolved_lbl = (
                str(raw_lbl)
                if raw_lbl and str(raw_lbl) != nid_str
                else str(existing.get("label") or raw_lbl or nid_str)
            )
            name_val = (
                nid_str.split(":", 1)[1]
                if ":" in nid_str
                else (resolved_lbl if resolved_lbl != nid_str else nid_str)
            )
            merged_meta = {**existing, **item}
            nodes_map[nid_str] = {
                "id": nid_str,
                "name": name_val,
                "type": clean_type,
                "role": role,
                "label": resolved_lbl,
                "line": merged_meta.get("line"),
                **{
                    key: value
                    for key, value in merged_meta.items()
                    if key in ("module", "render_type", "line", "source_file")
                    and value is not None
                },
            }

    def _resolve_node_label(raw_id: Any, fallback_label: Any = None) -> str:
        sid = str(raw_id or "")
        mapped = str(nodes_map.get(sid, {}).get("label") or "")
        fb = str(fallback_label or "")
        if mapped and mapped != sid:
            return mapped
        if fb and fb != sid:
            return fb
        return mapped or fb or sid

    normalized_events: List[Dict[str, Any]] = []
    step_idx = 0

    for item in raw_events:
        action = str(item.get("action") or item.get("event") or "")
        nid = item.get("reactId") or item.get("node_id") or item.get("id")
        lbl = _resolve_node_label(nid, item.get("label") or item.get("node_label"))
        ntype = item.get("type") or item.get("node_type") or "calc"
        val = item.get("value")
        val_str = str(val) if val is not None else None

        dep_from = (
            item.get("depOnReactId") or item.get("dependsOn") or item.get("edge_from")
        )
        dep_to = nid or item.get("reactId") or item.get("edge_to")

        t_raw = float(
            item.get("time")
            or item.get("time_sec")
            or (
                float(item.get("timestamp", 0)) / 1000.0
                if item.get("timestamp")
                else 0.0
            )
            or 0.0
        )
        t_sec = (
            round(max(0.0, t_raw - min_epoch_time), 4)
            if min_epoch_time > 0
            else round(max(0.0, t_raw), 4)
        )
        t_ms = int(t_sec * 1000)

        prov = item.get("provenance") or (
            "observed"
            if action in ("valueChange", "inputChange", "userClick", "userAction")
            else "inferred"
        )
        phase = item.get("phase") or (
            "init"
            if action in ("define", "analysisInit", "createContext", "sessionInit")
            else "interaction"
        )
        status = item.get("status")
        if not status:
            if action in ("define",):
                status = "discovered"
            elif action in ("invalidate", "propagate"):
                status = "affected"
            elif action in ("enter", "wouldEvaluate", "outputUpdated"):
                status = "scheduled"
            elif action in ("exit", "ordered", "idle", "recordingComplete"):
                status = "idle"
            elif action in ("valueChange", "inputChange", "assumeValue"):
                status = "assumed"
            else:
                status = "active"

        details = item.get("details")
        if not details:
            if action == "define":
                details = f"Defined reactive node '{lbl}'"
            elif action == "dependsOn":
                details = f"Dependency: '{dep_from}' used by '{dep_to}'"
            elif action == "dependsOnRemove":
                details = (
                    f"Removed dependency: '{dep_from}' no longer used by '{dep_to}'"
                )
            elif action in ("invalidate", "invalidateStart", "invalidateEnd"):
                details = f"Invalidated '{lbl}'"
            elif action in ("valueChange", "inputChange"):
                details = f"Value change for '{lbl}': {val_str}"
            elif action in ("enter", "wouldEvaluate"):
                details = f"Evaluating '{lbl}'"
            elif action in ("exit", "ordered"):
                details = f"Completed evaluation of '{lbl}'"
            elif action in ("idle", "queueEmpty"):
                details = "Idle"
            elif action == "freeze":
                details = f"Froze '{lbl}'"
            elif action == "thaw":
                details = f"Thawed '{lbl}'"
            else:
                details = f"Event '{action}' on '{lbl}'" if lbl else f"Event '{action}'"

        if action == "dependsOn" and dep_from and dep_to:
            edges_set.add((str(dep_from), str(dep_to)))

        ev_dict = _make_event(
            step=step_idx,
            event=action,
            phase=phase,
            provenance=prov,
            node_id=str(nid) if nid else None,
            node_label=str(lbl) if lbl else None,
            node_type=str(ntype) if ntype else None,
            status=status,
            timestamp=t_ms,
            time_sec=round(t_sec, 3),
            value=val_str,
            edge_from=str(dep_from) if (action == "dependsOn" or dep_from) else None,
            edge_to=str(dep_to) if (action == "dependsOn" or dep_to) else None,
            details=details,
            session=str(item.get("session") or session_name),
            action=action,
        )
        for key in ("error", "source_file", "line", "isolate"):
            if key in item:
                ev_dict[key] = item[key]
        preview = item.get("plot")
        if isinstance(preview, dict):
            plot_dict = cast(Dict[str, Any], preview)
            plot_src = plot_dict.get("src")
            if _is_plot_data_url(plot_src):
                plot_alt = plot_dict.get("alt")
                ev_dict["plot"] = {
                    "src": str(plot_src),
                    "alt": str(plot_alt) if plot_alt else lbl,
                }
        normalized_events.append(ev_dict)
        step_idx += 1

    final_nodes = list(nodes_map.values())
    final_edges = [{"from": f, "to": t} for f, t in sorted(edges_set)]

    if not normalized_events and final_nodes:
        for i, n in enumerate(final_nodes):
            normalized_events.append(
                _make_event(
                    step=i,
                    event="define",
                    phase="init",
                    provenance="inferred",
                    node_id=n["id"],
                    node_label=n["label"],
                    node_type=n["role"],
                    status="discovered",
                    details=f"Defined {n['role']} node '{n['label']}'",
                )
            )

    init_count = len([e for e in normalized_events if e.get("phase") == "init"])
    interact_count = len(
        [e for e in normalized_events if e.get("phase") == "interaction"]
    )
    first_interact = next(
        (i for i, e in enumerate(normalized_events) if e.get("phase") == "interaction"),
        0,
    )
    obs_count = len([e for e in normalized_events if e.get("provenance") == "observed"])
    inf_count = len([e for e in normalized_events if e.get("provenance") == "inferred"])

    parsed_dict: Optional[Dict[str, Any]] = (
        cast(Dict[str, Any], parsed) if isinstance(parsed, dict) else None
    )
    sources_val: Any = parsed_dict.get("sources", {}) if parsed_dict is not None else {}
    entry_file_val: str = (
        str(parsed_dict.get("entry_file", "")) if parsed_dict is not None else ""
    )

    return {
        "success": True,
        "version": version,
        "session": session_name,
        "trace_kind": "loaded_reactlog_json",
        "sources": sources_val,
        "entry_file": entry_file_val,
        "nodes": final_nodes,
        "edges": final_edges,
        "events": normalized_events,
        "log": normalized_events,
        "steps_total": len(normalized_events),
        "init_steps_count": init_count,
        "interaction_steps_count": interact_count,
        "first_interaction_step": first_interact,
        "observed_events_count": obs_count,
        "inferred_events_count": inf_count,
        "unmatched_inputs": [],
        "unmatched_inputs_count": 0,
        "disclaimer": "Imported reactive log data from JSON format.",
        "summary": f"Imported Reactlog graph: {len(final_nodes)} nodes, {len(final_edges)} edges, {len(normalized_events)} log events",
    }


def _record_session_sync(
    app_path: str,
    video_path: Optional[str] = "recording.webm",
    headless: bool = False,
    record_script: Optional[Callable[[Any], None]] = None,
    timeout_secs: float = 60.0,
    auto_interact: bool = False,
    redact_inputs: bool = False,
    viewport_size: Optional[Dict[str, int]] = None,
) -> Dict[str, Any]:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return {
            "success": False,
            "error": "Playwright is not installed. Install it with: pip install playwright && playwright install chromium",
            "actions": [],
            "video_path": None,
        }

    app_target = Path(app_path).resolve()
    if not app_target.exists():
        return {
            "success": False,
            "error": f"App file not found: {app_path}",
            "actions": [],
            "video_path": None,
        }

    from .run._run import run_shiny_app

    start_time = time.time()
    try:
        sa = run_shiny_app(
            app_target,
            wait_for_start=True,
            timeout_secs=min(timeout_secs, 30.0),
            env={"SHINY_TESTMODE": "1", "PYTHONUNBUFFERED": "1", "SHINY_REACTLOG": "1"},
        )
    except Exception as err:
        return {
            "success": False,
            "error": f"Failed to start Shiny app: {err}",
            "actions": [],
            "video_path": None,
        }

    app_url = sa.url
    temp_dir = tempfile.mkdtemp(prefix="shiny_record_")
    recorded_actions: List[Dict[str, Any]] = []
    saved_video_path: Optional[str] = None

    try:
        with sync_playwright() as p:
            ws_endpoint = os.environ.get("PW_TEST_CONNECT_WS_ENDPOINT")
            if ws_endpoint:
                connect_kwargs: Dict[str, Any] = {}
                connect_param_name = (
                    "endpoint"
                    if "endpoint" in inspect.signature(p.chromium.connect).parameters
                    else "ws_endpoint"
                )
                connect_kwargs[connect_param_name] = ws_endpoint
                expose_net = os.environ.get("PW_TEST_CONNECT_EXPOSE_NETWORK")
                if expose_net:
                    connect_kwargs["expose_network"] = expose_net
                browser = p.chromium.connect(**connect_kwargs)
            else:
                browser = p.chromium.launch(headless=headless)
            v_width = (
                int(viewport_size["width"])
                if viewport_size and "width" in viewport_size
                else 1280
            )
            v_height = (
                int(viewport_size["height"])
                if viewport_size and "height" in viewport_size
                else 1440
            )
            context = browser.new_context(
                record_video_dir=temp_dir,
                record_video_size={"width": v_width, "height": v_height},
                viewport={"width": v_width, "height": v_height},
            )
            page = context.new_page()
            page_start_time = time.time()

            redact_all_js = "true" if redact_inputs else "false"
            recorder_init_script = f"""
            window.__recordedActions = [];
            window.__recordStartTime = Date.now();
            const recentInputs = new Map();
            let lastClickTime = 0;
            let lastClickTarget = '';
            const shouldRedactAll = {redact_all_js};

            function isSensitiveInput(name, el) {{
                if (shouldRedactAll) return true;
                if (el && (el.type === 'password' || el.getAttribute('type') === 'password')) return true;
                const lower = (name || '').toLowerCase();
                return lower.includes('password') || lower.includes('secret') || lower.includes('token') || lower.includes('api_key') || lower.includes('apikey');
            }}

            function trackAction(item) {{
                item.timestamp = Date.now() - window.__recordStartTime;
                window.__recordedActions.push(item);
            }}

            function attachShinyListeners() {{
                if (window.$ && window.Shiny) {{
                    $(document).off('.shinyRecorder');
                    $(document).on('shiny:inputchanged.shinyRecorder', (e) => {{
                        if (e.name.startsWith('.')) return;
                        const el = document.getElementById(e.name) || document.querySelector('[name="' + e.name + '"]');
                        const sensitive = isSensitiveInput(e.name, el);
                        const safeVal = sensitive ? '[REDACTED]' : e.value;
                        const valKey = typeof safeVal === 'object' ? JSON.stringify(safeVal) : String(safeVal);
                        recentInputs.set(e.name, {{ val: valKey, t: Date.now() }});
                        trackAction({{
                            type: 'input',
                            name: e.name,
                            value: safeVal,
                            inputType: e.inputType || 'shiny'
                        }});
                    }});
                    $(document).on('shiny:value.shinyRecorder', (e) => {{
                        trackAction({{
                            type: 'output',
                            name: e.name,
                            plot: e.value && typeof e.value.src === 'string' && /^data:image\\/(png|jpeg|gif|webp);base64,/.test(e.value.src)
                                ? {{ src: e.value.src, alt: e.value.alt || e.name }} : undefined
                        }});
                    }});
                    $(document).on('shiny:error.shinyRecorder', (e) => {{
                        trackAction({{ type: 'outputError', name: e.name, error: e.error.message }});
                    }});
                }}
            }}

            document.addEventListener('DOMContentLoaded', attachShinyListeners);
            window.addEventListener('load', attachShinyListeners);
            document.addEventListener('shiny:connected', attachShinyListeners);

            document.addEventListener('change', (e) => {{
                const target = e.target;
                if (!target || !target.id || target.id.startsWith('.')) return;
                const id = target.id;
                const sensitive = isSensitiveInput(id, target);
                const rawVal = target.value !== undefined ? target.value : target.checked;
                const val = sensitive ? '[REDACTED]' : rawVal;
                const valKey = String(val);
                const rec = recentInputs.get(id);
                if (rec && (Date.now() - rec.t < 350) && rec.val === valKey) {{
                    return;
                }}
                if (window.Shiny && window.Shiny.setInputValue && target.closest('.shiny-input-container')) {{
                    return;
                }}
                recentInputs.set(id, {{ val: valKey, t: Date.now() }});
                trackAction({{
                    type: 'input',
                    name: id,
                    value: val,
                    inputType: target.type || target.tagName.toLowerCase()
                }});
            }}, true);

            document.addEventListener('click', (e) => {{
                const target = e.target.closest('button, input, select, textarea, a, .btn');
                if (!target) return;
                const tgtName = target.id || target.name || target.tagName.toLowerCase();
                const now = Date.now();
                if (tgtName === lastClickTarget && (now - lastClickTime < 200)) {{
                    return;
                }}
                lastClickTime = now;
                lastClickTarget = tgtName;
                trackAction({{
                    type: 'click',
                    target: tgtName,
                    text: (target.innerText || target.value || '').trim().slice(0, 50)
                }});
            }}, true);
            """
            page.add_init_script(recorder_init_script)

            page.goto(app_url, wait_until="domcontentloaded")
            time.sleep(0.5)

            if record_script:
                record_script(page)
                time.sleep(0.5)
            elif not headless:
                try:
                    sys.stderr.write(
                        "\n🔴 Recording browser session... Interact with your Shiny app.\n"
                        "Press [Enter] here (or close the browser window) when done recording: "
                    )
                    sys.stderr.flush()
                    deadline = time.time() + timeout_secs
                    while time.time() < deadline:
                        if page.is_closed():
                            break
                        import select

                        empty_r: List[Any] = []
                        empty_w: List[Any] = []
                        r, _, _ = select.select([sys.stdin], empty_r, empty_w, 0.3)
                        if r:
                            sys.stdin.readline()
                            break
                except Exception:
                    time.sleep(2.0)
            elif auto_interact:
                try:
                    time.sleep(0.8)
                    input_locators = page.locator(
                        "input.shiny-input-number, input.shiny-input-text, input[type='number'], input[type='text']"
                    ).all()
                    for inp in input_locators[:3]:
                        try:
                            val = inp.input_value()
                            if val.isdigit():
                                inp.fill(str(int(val) + 5))
                            elif val:
                                inp.fill(f"{val} Updated")
                            time.sleep(0.4)
                        except Exception:
                            pass

                    buttons = page.locator(
                        "button.action-button, button.btn-primary, button.btn"
                    ).all()
                    for btn in buttons[:2]:
                        try:
                            btn.click()
                            time.sleep(0.5)
                        except Exception:
                            pass
                except Exception:
                    time.sleep(1.0)
            else:
                time.sleep(1.0)

            try:
                if not page.is_closed():
                    raw_actions = page.evaluate("() => window.__recordedActions || []")
                    if isinstance(raw_actions, list):
                        recorded_actions = cast(List[Dict[str, Any]], raw_actions)
            except Exception:
                pass

            app_marks: List[Dict[str, Any]] = []
            try:
                import urllib.request

                req = urllib.request.Request(f"{app_url.rstrip('/')}/__reactlog__/mark")
                with urllib.request.urlopen(req, timeout=3.0) as resp:
                    mark_data = json.loads(resp.read().decode())
                    if isinstance(mark_data, dict) and "marks" in mark_data:
                        raw_marks = cast(List[Dict[str, Any]], mark_data["marks"])
                        for rm in raw_marks:
                            item = dict(rm)
                            raw_t = float(item.get("time") or 0.0)
                            if raw_t > 1_000_000_000:
                                rel_sec = max(0.0, round(raw_t - page_start_time, 2))
                                item["time"] = rel_sec
                                item["timestamp"] = int(rel_sec * 1000)
                            app_marks.append(item)
            except Exception:
                pass

            page_video = page.video

            page.close()
            context.close()

            if page_video and video_path:
                out_v = Path(video_path).resolve()
                out_v.parent.mkdir(parents=True, exist_ok=True)
                try:
                    page_video.save_as(str(out_v))
                    saved_video_path = str(out_v)
                except Exception:
                    pass
            elif page_video:
                temp_video = Path(temp_dir) / "recording.webm"
                try:
                    page_video.save_as(str(temp_video))
                    saved_video_path = str(temp_video)
                except Exception:
                    pass

            browser.close()

        if not saved_video_path:
            video_files = list(Path(temp_dir).glob("*.webm"))
            if video_files and video_path:
                out_v = Path(video_path).resolve()
                out_v.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(video_files[0], out_v)
                saved_video_path = str(out_v)
            elif video_files:
                saved_video_path = str(video_files[0])

        if not app_marks:
            try:
                import urllib.request

                req = urllib.request.Request(f"{app_url.rstrip('/')}/__reactlog__/mark")
                with urllib.request.urlopen(req, timeout=3.0) as resp:
                    mark_data = json.loads(resp.read().decode())
                    if isinstance(mark_data, dict) and "marks" in mark_data:
                        raw_marks = cast(List[Dict[str, Any]], mark_data["marks"])
                        for rm in raw_marks:
                            item = dict(rm)
                            raw_t = float(item.get("time") or 0.0)
                            if raw_t > 1_000_000_000:
                                rel_sec = max(0.0, round(raw_t - page_start_time, 2))
                                item["time"] = rel_sec
                                item["timestamp"] = int(rel_sec * 1000)
                            app_marks.append(item)
            except Exception:
                pass

        return {
            "success": True,
            "actions": recorded_actions,
            "marks": app_marks,
            "video_path": saved_video_path,
            "duration_secs": round(time.time() - start_time, 2),
        }

    finally:
        sa.close()
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception:
            pass


def record_shiny_session(
    app_path: str,
    video_path: Optional[str] = "recording.webm",
    headless: bool = False,
    record_script: Optional[Callable[[Any], None]] = None,
    timeout_secs: float = 60.0,
    auto_interact: bool = False,
    redact_inputs: bool = False,
    viewport_size: Optional[Dict[str, int]] = None,
) -> Dict[str, Any]:
    try:
        asyncio.get_running_loop()
        has_running_loop = True
    except RuntimeError:
        has_running_loop = False

    if has_running_loop:
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(
                _record_session_sync,
                app_path,
                video_path,
                headless,
                record_script,
                timeout_secs,
                auto_interact,
                redact_inputs,
                viewport_size,
            )
            return future.result()
    return _record_session_sync(
        app_path,
        video_path,
        headless,
        record_script,
        timeout_secs,
        auto_interact,
        redact_inputs,
        viewport_size,
    )


def format_graph_mermaid(graph: Dict[str, Any]) -> str:
    lines = ["graph TD"]
    node_id_map: Dict[str, str] = {}
    for idx, node in enumerate(graph.get("nodes", [])):
        raw_id = str(node["id"])
        syn_id = f"n{idx}"
        node_id_map[raw_id] = syn_id
        ntype = node.get("type", "")
        label = str(node.get("label", raw_id)).replace('"', '\\"')
        if ntype == "input":
            lines.append(f'    {syn_id}["{label}"]:::inputClass')
        elif ntype == "calc":
            lines.append(f'    {syn_id}["{label}"]:::calcClass')
        elif ntype == "effect":
            lines.append(f'    {syn_id}["{label}"]:::effectClass')
        else:
            lines.append(f'    {syn_id}["{label}"]:::outputClass')

    for edge in graph.get("edges", []):
        f = node_id_map.get(str(edge["from"]))
        t = node_id_map.get(str(edge["to"]))
        if f and t:
            lines.append(f"    {f} --> {t}")

    lines.append(
        "    classDef inputClass fill:#e0f2fe,stroke:#0284c7,stroke-width:2px;"
    )
    lines.append("    classDef calcClass fill:#fef3c7,stroke:#d97706,stroke-width:2px;")
    lines.append(
        "    classDef effectClass fill:#f3e8ff,stroke:#9333ea,stroke-width:2px;"
    )
    lines.append(
        "    classDef outputClass fill:#dcfce7,stroke:#16a34a,stroke-width:2px;"
    )
    return "\n".join(lines)


def format_graph_dot(graph: Dict[str, Any]) -> str:
    lines = [
        "digraph ReactiveGraph {",
        "    rankdir=LR;",
        "    node [shape=box, style=rounded];",
    ]
    node_id_map: Dict[str, str] = {}
    for idx, node in enumerate(graph.get("nodes", [])):
        raw_id = str(node["id"])
        syn_id = f"n{idx}"
        node_id_map[raw_id] = syn_id
        label = str(node.get("label", raw_id)).replace('"', '\\"')
        ntype = node.get("type", "")
        if ntype == "input":
            color = "#0284c7"
        elif ntype == "calc":
            color = "#d97706"
        elif ntype == "effect":
            color = "#9333ea"
        else:
            color = "#16a34a"
        lines.append(f'    "{syn_id}" [label="{label}", color="{color}"];')

    for edge in graph.get("edges", []):
        f = node_id_map.get(str(edge["from"]))
        t = node_id_map.get(str(edge["to"]))
        if f and t:
            lines.append(f'    "{f}" -> "{t}";')

    lines.append("}")
    return "\n".join(lines)


def _format_python_source_html(source: str) -> str:
    lines = source.splitlines(keepends=True)
    line_offsets: List[int] = []
    offset = 0
    for line in lines:
        line_offsets.append(offset)
        offset += len(line)

    def absolute_offset(position: tuple[int, int]) -> int:
        row, column = position
        if row < 1 or row > len(line_offsets):
            return len(source)
        return line_offsets[row - 1] + column

    token_classes = {
        tokenize.COMMENT: "syntax-comment",
        tokenize.NUMBER: "syntax-number",
        tokenize.OP: "syntax-operator",
        tokenize.STRING: "syntax-string",
    }
    fragments: List[str] = []
    cursor = 0
    try:
        tokens = tokenize.generate_tokens(io.StringIO(source).readline)
        for token_info in tokens:
            if token_info.type == tokenize.ENDMARKER:
                break
            start = max(cursor, absolute_offset(token_info.start))
            end = max(start, absolute_offset(token_info.end))
            if end <= cursor:
                continue
            fragments.append(html_lib.escape(source[cursor:start]))
            token_source = source[start:end]
            css_class = token_classes.get(token_info.type)
            if token_info.type == tokenize.NAME and keyword.iskeyword(
                token_info.string
            ):
                css_class = "syntax-keyword"
            escaped_token = html_lib.escape(token_source)
            if css_class:
                fragments.append(f'<span class="{css_class}">{escaped_token}</span>')
            else:
                fragments.append(escaped_token)
            cursor = end
        fragments.append(html_lib.escape(source[cursor:]))
        full_html = "".join(fragments)
    except (IndentationError, tokenize.TokenError):
        full_html = html_lib.escape(source)

    code_lines = full_html.split("\n")
    if len(code_lines) > 0 and code_lines[-1] == "":
        code_lines.pop()

    output_lines: List[str] = []
    for i, line_content in enumerate(code_lines, 1):
        output_lines.append(
            f'<div class="source-line" data-line="{i}">'
            f'<span class="source-line-num" aria-hidden="true">{i}</span>'
            f'<span class="source-line-content">{line_content}</span>'
            f"</div>"
        )
    return "".join(output_lines)


def format_reactlog_html(
    reactlog: Dict[str, Any],
    source_code: str,
    title: str = "Shiny App",
    video_path: Optional[str] = None,
    html_path: Optional[str] = None,
    theme: str = "dark",
) -> str:
    clean_title = title
    for suffix in (" · Reactlog report", " - Reactlog report", " : Reactlog report"):
        if clean_title.endswith(suffix):
            clean_title = clean_title[: -len(suffix)].strip()
    if clean_title == "Reactlog report":
        clean_title = "Shiny App"
    escaped_title = html_lib.escape(clean_title)
    formatted_source = _format_python_source_html(source_code)
    actual_video = video_path or reactlog.get("video_path")

    video_tab_btn = ""
    video_panel = ""
    if actual_video:
        if html_path:
            html_dir = os.path.dirname(os.path.abspath(html_path))
            try:
                rel_video_str = os.path.relpath(
                    os.path.abspath(actual_video), start=html_dir
                )
            except ValueError:
                rel_video_str = actual_video
            rel_video = html_lib.escape(rel_video_str.replace("\\", "/"))
        else:
            rel_video = html_lib.escape(os.path.basename(actual_video))

        video_tab_btn = (
            '<button class="btn icon" id="video-tab" '
            'aria-label="Toggle recording" title="Toggle recording" aria-expanded="true" '
            'onclick="toggleRecording()"><svg width="16" height="16" viewBox="0 0 24 24" '
            'fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="5" '
            'width="14" height="14" rx="2"/><path d="m16 10 6-4v12l-6-4"/></svg></button>'
        )
        video_panel = f"""
        <section class="video-panel" id="video-panel" aria-label="Recording">
          <div class="video-meta">
            <span id="video-sync-status" class="video-sync-status" role="status">Recording</span>
            <button class="btn icon mini" onclick="toggleRecording(false)" aria-label="Hide recording" title="Hide recording">×</button>
          </div>
          <div class="video-container">
            <video id="session-video" controls preload="metadata" playsinline>
              <source src="{rel_video}" type="video/webm">
              Your browser does not support the video tag.
            </video>
          </div>
        </section>
        """

    source_tab = (
        '<button class="btn icon" id="source-tab" aria-label="App code" title="App code" role="tab" '
        'aria-selected="false" aria-controls="source-panel" '
        'onclick="showSidebarPanel(\'source\')"><span aria-hidden="true">&lt;/&gt;</span></button>'
    )
    source_panel = (
        '<pre class="source-panel sidebar-panel" id="source-panel" role="tabpanel" '
        'aria-labelledby="source-tab" hidden>'
        '<select id="source-file-select" aria-label="Source file" onchange="showSourceFile(this.value)" hidden></select><code>'
        f"{formatted_source}</code></pre>"
    )
    escaped_json = (
        json.dumps(reactlog, indent=2)
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("&", "\\u0026")
    )
    escaped_source_raw = (
        json.dumps(source_code)
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("&", "\\u0026")
    )
    safe_theme = html_lib.escape(
        theme if theme in ("dark", "light", "auto") else "dark"
    )

    return f"""<!DOCTYPE html>
<html lang="en" data-theme="{safe_theme}">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="theme-color" content="#090d12" />
  <title>{escaped_title}</title>
  <style>
    :root {{
      --state-ready: #a3c586;
      --state-calculating: #fcbf49;
      --state-invalidating: #969696;
      --state-invalidated: #d9d9d9;
      --state-frozen: #0b5384;
      --state-error: #f3a6af;
      --timeline-idle: var(--state-ready);
    }}
    :root, [data-theme="dark"] {{
      color-scheme: dark;
      --bg: #090d12;
      --surface: #111821;
      --surface-2: #17212d;
      --surface-3: #1d2a38;
      --surface-elevated: #223243;
      --border: #293747;
      --border-strong: #3a4b5f;
      --text: #edf4fb;
      --text-muted: #91a1b3;
      --accent: #63b3ff;
      --accent-hover: #82c4ff;
      --source: #56b4e9;
      --calc: #e9b44c;
      --effect: #e3a4c8;
      --module-text: #c4b5fd;
      --output: #5fc7a7;
      --warning: #e69f00;
      --danger: #f28c50;
      --grid-line: rgba(105, 128, 151, 0.035);
      --header-bg: rgba(17, 24, 33, 0.96);
      --node-fill: #121b25;
      --node-stroke: #64748b;
      --node-text: #edf4fb;
      --node-subtext: #91a1b3;
      --source-panel-bg: #0c1219;
      --source-panel-text: #d9e7f5;
      --trace-bg: #0b1119;
      --trace-lane-bg: #0d1520;
      --trace-burst-bg: #111a26;
      --burst-column-bg: rgba(99, 179, 255, 0.03);
      --burst-column-active: rgba(99, 179, 255, 0.12);
      --toast-bg: rgba(23, 33, 45, 0.95);
      --legend-bg: rgba(17, 24, 33, 0.92);
      --card-bg: #141e2b;
      --track-bg: #1b2634;
      --track-fill: #24384d;
      --timeline-idle-outline: #355c23;
      --timeline-output: #56b4e9;
      --timeline-mark: #f59e0b;
      --timeline-error: #ff8e91;
      --playhead-bg: #f8fafc;
      --playhead-ring: #17212b;
      --mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      --sans: Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    [data-theme="light"] {{
      color-scheme: light;
      --bg: #f8fafc;
      --surface: #ffffff;
      --surface-2: #f1f5f9;
      --surface-3: #e2e8f0;
      --surface-elevated: #ffffff;
      --border: #cbd5e1;
      --border-strong: #94a3b8;
      --text: #0f172a;
      --text-muted: #526277;
      --accent: #005a9c;
      --accent-hover: #0369a1;
      --source: #005a9c;
      --calc: #9c4f00;
      --effect: #994a78;
      --module-text: #6d28d9;
      --output: #006e59;
      --warning: #925f00;
      --danger: #a64700;
      --grid-line: rgba(15, 23, 42, 0.04);
      --header-bg: rgba(255, 255, 255, 0.96);
      --node-fill: #ffffff;
      --node-stroke: #475569;
      --node-text: #0f172a;
      --node-subtext: #64748b;
      --source-panel-bg: #f8fafc;
      --source-panel-text: #1e293b;
      --trace-bg: #f8fafc;
      --trace-lane-bg: #ffffff;
      --trace-burst-bg: #f1f5f9;
      --burst-column-bg: rgba(2, 132, 199, 0.03);
      --burst-column-active: rgba(2, 132, 199, 0.12);
      --toast-bg: rgba(255, 255, 255, 0.95);
      --legend-bg: rgba(255, 255, 255, 0.92);
      --card-bg: #f8fafc;
      --track-bg: #e2e8f0;
      --track-fill: #cbd5e1;
      --timeline-output: #026aa7;
      --timeline-mark: #b45309;
      --timeline-error: #a92334;
      --playhead-bg: #0f172a;
      --playhead-ring: #ffffff;
    }}
    @media (prefers-color-scheme: light) {{
      [data-theme="auto"] {{
        color-scheme: light;
        --bg: #f8fafc;
        --surface: #ffffff;
        --surface-2: #f1f5f9;
        --surface-3: #e2e8f0;
        --surface-elevated: #ffffff;
        --border: #cbd5e1;
        --border-strong: #94a3b8;
        --text: #0f172a;
        --text-muted: #526277;
        --accent: #005a9c;
        --accent-hover: #0369a1;
        --source: #005a9c;
        --calc: #9c4f00;
        --effect: #994a78;
        --module-text: #6d28d9;
        --output: #006e59;
        --warning: #925f00;
        --danger: #a64700;
        --grid-line: rgba(15, 23, 42, 0.04);
        --header-bg: rgba(255, 255, 255, 0.96);
        --node-fill: #ffffff;
        --node-stroke: #475569;
        --node-text: #0f172a;
        --node-subtext: #64748b;
        --source-panel-bg: #f8fafc;
        --source-panel-text: #1e293b;
        --trace-bg: #f8fafc;
        --trace-lane-bg: #ffffff;
        --trace-burst-bg: #f1f5f9;
        --burst-column-bg: rgba(2, 132, 199, 0.03);
        --burst-column-active: rgba(2, 132, 199, 0.12);
        --toast-bg: rgba(255, 255, 255, 0.95);
        --legend-bg: rgba(255, 255, 255, 0.92);
        --card-bg: #f8fafc;
        --track-bg: #e2e8f0;
        --track-fill: #cbd5e1;
        --timeline-output: #026aa7;
        --timeline-mark: #b45309;
        --timeline-error: #a92334;
        --playhead-bg: #0f172a;
        --playhead-ring: #ffffff;
      }}
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    button, input, select {{ font: inherit; }}
    button:focus-visible, input:focus-visible, select:focus-visible {{ outline: 2px solid var(--accent); outline-offset: 2px; }}
    [hidden] {{ display:none !important; }}
    body {{ background: var(--bg); color: var(--text); font-family: var(--sans); height: 100vh; display: flex; flex-direction: column; overflow: hidden; }}
    .app-header {{ min-height: 50px; background: var(--header-bg); border-bottom: 1px solid var(--border); padding: 0.5rem 1.1rem; display: flex; justify-content: space-between; gap: 1rem; align-items: center; z-index: 40; position: relative; }}
    .brand {{ display: flex; align-items: center; gap: 0.7rem; min-width: 0; }}
    .brand-mark {{ width: 28px; height: 28px; border-radius: 7px; display: grid; place-items: center; color: #07111c; background: linear-gradient(145deg, #82c9ff, #3b9ced); font-family: var(--mono); font-weight: 900; box-shadow: 0 3px 12px rgba(58, 158, 239, 0.2); flex-shrink: 0; }}
    .brand-copy {{ min-width: 0; }}
    .brand-title {{ font-weight: 760; font-size: 0.9rem; letter-spacing: -0.01em; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
    .brand-subtitle {{ color: var(--text-muted); font-size: 0.68rem; }}
    .header-center {{ display: flex; align-items: center; gap: .5rem; flex: 1; min-width: 0; flex-wrap: wrap; }}
    .header-actions {{ display: flex; align-items: center; gap: 0.45rem; position: relative; }}
    /* Streamlined Toolbar & Buttons */
    .toolbar {{ position: relative; z-index: 19; min-height: 38px; background: var(--surface-2); border-top: 1px solid var(--border); padding: 0.2rem 0.75rem; display: flex; align-items: center; justify-content: space-between; gap: 0.6rem; }}
    .toolbar-group {{ display: flex; align-items: center; gap: 0.35rem; flex-wrap: wrap; min-width: 0; }}
    .toolbar-divider {{ width: 1px; height: 20px; background: var(--border); margin: 0 0.15rem; }}
    .btn {{ min-height: 26px; background: var(--surface-2); border: 1px solid var(--border); color: var(--text); padding: 0.22rem 0.5rem; border-radius: 5px; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; gap: 0.3rem; transition: background 120ms ease, border-color 120ms ease, transform 120ms ease; font-size: 0.72rem; font-weight: 700; }}
    .btn:hover {{ background: var(--surface-3); border-color: var(--border-strong); }}
    .btn:active {{ transform: translateY(1px); }}
    .btn.icon {{ width: 28px; height: 28px; padding: 0; font-family: var(--mono); }}
    .btn.primary {{ background: #1f69a3; border-color: #2d86c8; color: #fff; }}
    .btn.primary:hover {{ background: #267ec4; }}
    .btn.active-filter {{ background: var(--surface-3); border-color: var(--accent); color: var(--accent); }}
    .inline-icon {{ display: inline-block; vertical-align: -0.15em; margin-right: 0.25rem; flex-shrink: 0; }}
    .btn.icon svg {{ display: block; margin: auto; }}
    .search-wrap {{ position: relative; width: 210px; flex-shrink: 0; }}
    .search-results {{ position: absolute; top: calc(100% + 4px); left: 0; right: auto; min-width: 340px; max-width: min(540px, calc(100vw - 32px)); width: max-content; max-height: 340px; overflow-y: auto; overflow-x: hidden; background: var(--surface); border: 1px solid var(--border-strong); border-radius: 8px; padding: 6px; z-index: 1000; box-shadow: 0 10px 28px rgba(0,0,0,0.28); }}
    .search-results button {{ display: flex; align-items: center; justify-content: space-between; gap: 12px; width: 100%; text-align: left; padding: 7px 10px; background: var(--surface-2); color: var(--text); border: 1px solid transparent; border-radius: 6px; cursor: pointer; word-break: break-word; font-family: var(--mono); font-size: 0.73rem; line-height: 1.4; white-space: normal; }}
    .search-results button + button {{ margin-top: 2px; }}
    .search-results button:hover, .search-results button:focus {{ background: var(--surface-3); outline: 1px solid var(--accent); }}
    .search-results button.is-selected {{ background: color-mix(in srgb, var(--accent) 16%, var(--surface-2)); border-color: color-mix(in srgb, var(--accent) 45%, transparent); color: var(--accent); }}
    .search-item-main {{ display: inline-flex; align-items: center; gap: 7px; min-width: 0; }}
    .search-check {{ display: inline-flex; align-items: center; justify-content: center; width: 14px; height: 14px; flex-shrink: 0; color: var(--accent); opacity: 0; }}
    .search-results button.is-selected .search-check {{ opacity: 1; }}
    .search-icon {{ position: absolute; left: 0.6rem; top: 50%; transform: translateY(-50%); color: var(--text-muted); pointer-events: none; }}
    .search-input {{ width: 100%; height: 28px; color: var(--text); background: var(--bg); border: 1px solid var(--border); border-radius: 6px; padding: 0 3.1rem 0 1.75rem; font-size: 0.72rem; }}
    .search-input::-webkit-search-cancel-button, .search-input::-webkit-search-decoration {{ -webkit-appearance: none; appearance: none; display: none; }}
    .search-clear {{ position: absolute; right: 24px; top: 2px; width: 22px; height: 24px; border: 0; border-radius: 4px; background: transparent; color: var(--accent); cursor: pointer; display: inline-flex; align-items: center; justify-content: center; font-size: 0.92rem; font-weight: 700; line-height: 1; padding: 0; }}
    .search-clear:hover {{ background: var(--surface-3); color: var(--accent-hover); }}
    .search-toggle {{ position: absolute; right: 2px; top: 2px; width: 24px; height: 24px; border: 0; border-radius: 4px; background: transparent; color: var(--text-muted); cursor: pointer; }}
    .search-input::placeholder {{ color: var(--text-muted); }}
    .filter-select {{ height: 28px; color: var(--text); background: var(--bg); border: 1px solid var(--border); border-radius: 6px; padding: 0 0.5rem; font-size: 0.72rem; font-weight: 600; cursor: pointer; }}
    .filter-select:hover {{ border-color: var(--border-strong); background: var(--surface-2); }}
    .empty-graph-message {{ position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: var(--text-muted); background: var(--surface); border: 1px solid var(--border); border-radius: 6px; padding: .75rem; text-align: center; z-index: 1; }}
    .step-display {{ white-space: nowrap; flex-shrink: 0; font: 700 0.68rem var(--mono); color: var(--accent); min-width: 72px; text-align: right; font-variant-numeric: tabular-nums; }}

    /* Workspace Layout: Left Sidebar + Center Canvas + On Demand Right Sidebar */
    .workspace-layout {{ display: flex; flex: 1; min-height: 0; overflow: hidden; position: relative; }}

    /* Timeline playback controls */
    .bottom-timeline-bar {{ flex-shrink: 0; background: transparent; border: none; display: grid; grid-template-columns: minmax(0, 1fr) auto minmax(0, 1fr); align-items: center; padding: 0; gap: 0.75rem; z-index: 30; user-select: none; }}
    .status-left, .status-center, .status-right {{ display: flex; align-items: center; gap: 0.4rem; }}
    .trace-status-line, #active-flush-label {{ color: var(--text-muted); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
    .trace-status-line {{ font: 600 .75rem var(--sans); }}
    #active-flush-label {{ font: 650 .72rem var(--sans); text-align: end; }}
    .status-time-group {{ display: flex; align-items: center; gap: 0.25rem; font: 700 0.68rem var(--mono); color: var(--accent); }}

    /* Main View & Graph */
    .main-view {{ display: flex; flex: 1; min-height: 0; min-width: 0; overflow: hidden; position: relative; }}
    .graph-container {{ flex: 1; min-width: 0; min-height: 0; overflow: hidden; position: relative; background-color: var(--bg); background-image: linear-gradient(var(--grid-line) 1px, transparent 1px), linear-gradient(90deg, var(--grid-line) 1px, transparent 1px); background-size: 24px 24px; display: flex; flex-direction: column; }}

    /* Graph Topbar */
    .graph-topbar {{ position: relative; z-index: 3; padding: 0.6rem 0.8rem; display: flex; flex-direction: column; gap: 0.45rem; flex-shrink: 0; }}
    .graph-top-row {{ display: flex; align-items: center; justify-content: space-between; gap: 0.6rem; flex-wrap: wrap; }}
    .legend {{ display: flex; gap: 0.35rem; flex-wrap: wrap; padding: 0.25rem 0.45rem; border: 1px solid var(--border); border-radius: 6px; background: var(--legend-bg); backdrop-filter: blur(8px); pointer-events: auto; }}
    .legend-item {{ display: inline-flex; align-items: center; gap: 0.35rem; color: var(--text-muted); font: 650 0.65rem var(--mono); padding: 0.1rem 0.2rem; }}
    .legend-dot {{ width: 12px; height: 12px; flex-shrink: 0; display: inline-flex; align-items: center; justify-content: center; color: var(--role-color); }}
    .legend-dot svg {{ width: 12px; height: 12px; display: block; }}
    .zoom-controls {{ display: flex; gap: 0.25rem; pointer-events: auto; align-items: center; }}
    .action-toast[hidden] {{ display: none; }}
    .action-toast {{ position: absolute; z-index: 4; bottom: 1rem; left: 50%; transform: translateX(-50%); background: var(--toast-bg); border: 1px solid var(--accent); border-radius: 999px; padding: 0.4rem 1rem; color: var(--text); font: 650 0.74rem var(--mono); box-shadow: 0 10px 30px rgba(0,0,0,0.25); display: flex; align-items: center; gap: 0.5rem; pointer-events: none; }}

    #reactlog-svg {{ width: 100%; height: 100%; min-height: 430px; display: block; }}
    .graph-node, .graph-edge {{ transition: opacity 180ms ease, filter 180ms ease, stroke 180ms ease, stroke-width 180ms ease; }}
    .graph-edge {{ opacity: 1; stroke: var(--text-muted); stroke-width: 2px; pointer-events: stroke; cursor: pointer; }}
    .graph-edge:hover {{ opacity: 1 !important; stroke: var(--accent) !important; stroke-width: 2.8px !important; }}
    .graph-edge.is-isolated {{ opacity: 1; stroke: var(--text-muted); stroke-dasharray: 5 4; }}
    .graph-edge.is-inactive {{ stroke: var(--text-muted); stroke-dasharray: 1 5; opacity: 1; }}
    .graph-edge-pulse {{ fill: var(--text); stroke: var(--bg); stroke-width: 1.5px; pointer-events: none; }}
    .legend-swatch {{ width: 14px; height: 14px; border: 1.5px solid var(--node-stroke); border-radius: 4px; }}
    .legend-line {{ display: inline-block; width: 16px; border-top: 2px solid var(--text-muted); }}
    .legend-line.is-isolated {{ border-top-style: dashed; }}
    .legend-line.is-inactive {{ border-top-style: dotted; }}
    .legend-sep {{ width: 1px; height: 14px; background: var(--border); margin: 0 2px; align-self: center; }}
    .graph-node.is-clientdata {{ opacity: 0.78; }}
    .burst-anchor.is-mark {{ border-color: #f59e0b; background: rgba(245, 158, 11, 0.15); color: #b45309; }}
    [data-theme="dark"] .burst-anchor.is-mark {{ color: #fbbf24; }}
    .burst-anchor.is-mark .burst-anchor-dot {{ background: #f59e0b; }}
    .node-exec-badge {{ pointer-events: none; }}
    .hotspot-badge {{ display: inline-block; padding: 2px 6px; border-radius: 4px; background: rgba(239, 68, 68, 0.2); color: var(--danger); font-weight: 700; font-size: 0.72rem; margin-left: 6px; }}
    .node-meta-exec {{ font-size: 0.75rem; color: var(--text-muted); margin-top: 4px; }}
    .modal-backdrop {{ position: fixed; inset: 0; background: rgba(0, 0, 0, 0.65); backdrop-filter: blur(4px); z-index: 9999; display: flex; align-items: center; justify-content: center; }}
    .modal-backdrop[hidden] {{ display: none; }}
    .modal-dialog {{ background: var(--surface); border: 1px solid var(--border-strong); border-radius: 12px; padding: 1.25rem 1.5rem; max-width: 520px; width: 90%; box-shadow: 0 20px 40px rgba(0,0,0,0.5); }}
    .modal-header {{ display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem; border-bottom: 1px solid var(--border); padding-bottom: 0.5rem; }}
    .modal-title {{ font-size: 0.95rem; font-weight: 700; color: var(--text); margin: 0; }}
    .modal-close-btn {{ background: transparent; border: none; color: var(--text-muted); cursor: pointer; font-size: 1.1rem; padding: 0.2rem 0.4rem; border-radius: 4px; }}
    .modal-close-btn:hover {{ color: var(--text); background: var(--surface-2); }}
    .shortcuts-table {{ width: 100%; border-collapse: collapse; font-size: 0.8rem; }}
    .shortcuts-table td {{ padding: 0.4rem 0.2rem; border-bottom: 1px solid var(--border); color: var(--text); }}
    .shortcut-key {{ display: inline-block; padding: 0.15rem 0.45rem; background: var(--surface-2); border: 1px solid var(--border-strong); border-radius: 4px; font-family: var(--mono); font-size: 0.75rem; color: var(--accent); font-weight: 600; }}
    .graph-edge[data-active="true"] {{ opacity: 1 !important; stroke: var(--accent) !important; stroke-width: 2.8px !important; }}
    .graph-node.is-dimmed, .module-box.is-dimmed, .app-box.is-dimmed {{ opacity: 0.3; filter: grayscale(1); }}
    .graph-edge.is-dimmed {{ opacity: 0.15 !important; stroke: var(--text-muted) !important; stroke-width: 1.8px !important; filter: grayscale(1); animation: none; }}
    #btn-clear-selection[hidden], #btn-inspect-selection[hidden] {{ display: none; }}
    #btn-toggle-inspector-bottom.has-selection {{ border-color: var(--accent); color: var(--accent); position: relative; }}
    #btn-toggle-inspector-bottom.has-selection::after {{ content: ''; position: absolute; top: 3px; right: 3px; width: 6px; height: 6px; border-radius: 50%; background: var(--accent); }}
    @media (prefers-reduced-motion: reduce) {{
      .graph-node, .graph-edge, .source-line, .trace-chip, .trace-playhead {{ transition: none; }}
      .graph-edge[data-active="true"] {{ animation: none; }}
      .graph-edge-pulse {{ display: none; }}
      .action-toast[hidden] {{ display: none; }}
    .action-toast {{ animation: none; }}
    }}
    .graph-node {{ cursor: pointer; }}
    .graph-node:hover .node-card {{ filter: brightness(1.06); }}
    .graph-node.is-selected .node-card {{ stroke: var(--node-selection-stroke) !important; stroke-width: 3.5px !important; filter: drop-shadow(0 0 12px color-mix(in srgb, var(--accent) 65%, transparent)); }}
    .graph-node.is-active:not(.is-selected) .node-card {{ stroke: var(--node-selection-stroke) !important; stroke-width: 2.5px !important; }}
    .module-box {{ cursor: default; }}
    .module-box:focus {{ outline: none; }}
    .module-box:focus rect {{ stroke: var(--accent); stroke-width: 2.5; }}
    .module-collapse-btn {{ cursor: pointer; }}
    .module-collapse-btn:focus {{ outline: none; }}
    .module-collapse-btn:focus text {{ fill: var(--accent) !important; text-decoration: underline; }}
    .module-collapse-btn:hover text {{ fill: var(--accent) !important; }}
    .module-collapse-icon {{ opacity: 0; transition: opacity 120ms ease; pointer-events: none; }}
    .module-collapse-btn:hover .module-collapse-icon,
    .module-collapse-btn:focus .module-collapse-icon {{ opacity: 1; }}
    #insp-plot {{ margin: 12px 0; }}
    #insp-plot-image {{ width: 100%; border-radius: 8px; background: white; }}
    #insp-plot-caption {{ font-size: 12px; color: var(--text-muted); margin-top: 6px; }}

    /* Sidebar */
    .sidebar {{ min-width: 0; background: var(--surface); border-left: 1px solid var(--border); display: flex; flex-direction: column; overflow: hidden; }}
    .sidebar[hidden] {{ display: none !important; }}
    .sidebar-header {{ min-height: 42px; padding: 0.45rem 0.75rem; border-bottom: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between; gap: 0.5rem; }}
    .sidebar-panel {{ min-height: 0; flex: 1; overflow-y: auto; display: flex; flex-direction: column; }}
    .sidebar-panel[hidden] {{ display: none; }}
    .inspector-container {{ flex-shrink: 0; min-width: 0; padding: 0.8rem; display: flex; flex-direction: column; gap: 0.75rem; overflow-wrap: anywhere; }}

    /* Why Card */
    .why-card {{ background: var(--card-bg); border: 1.5px solid var(--accent); border-radius: 9px; padding: 0.85rem; display: flex; flex-direction: column; gap: 0.6rem; box-shadow: 0 4px 16px rgba(0,0,0,0.14); position: relative; }}
    .why-header {{ display: flex; align-items: center; justify-content: space-between; gap: 0.5rem; }}
    .why-title {{ font: 800 0.86rem var(--sans); color: var(--text); line-height: 1.3; }}
    .why-narrative {{ font-size: 0.74rem; color: var(--text); line-height: 1.5; background: var(--surface-2); border-radius: 6px; padding: 0.6rem 0.7rem; border-left: 3px solid var(--accent); display: flex; flex-direction: column; gap: 0.35rem; }}
    .why-section-title {{ font: 750 0.66rem var(--mono); color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; margin-top: 0.2rem; }}
    .why-causes-list {{ list-style: none; padding-left: 0; display: flex; flex-direction: column; gap: 0.2rem; font-size: 0.72rem; }}
    .why-causes-list li {{ display: flex; align-items: center; gap: 0.35rem; }}
    .why-causes-list li::before {{ content: "•"; color: var(--accent); font-weight: bold; }}
    .why-dag-tree {{ display: flex; align-items: center; gap: 0.5rem; padding: 0.5rem; background: var(--surface-3); border-radius: 7px; border: 1px solid var(--border); overflow-x: auto; }}
    .dag-parents-col {{ display: flex; flex-direction: column; gap: 0.35rem; justify-content: center; }}
    .dag-bracket {{ color: var(--accent); font-size: 0.9rem; font-weight: bold; }}
    .dag-target-col {{ display: flex; align-items: center; }}
    .flow-node-pill {{ font: 700 0.68rem var(--mono); padding: 0.22rem 0.48rem; border-radius: 5px; background: var(--surface-2); border: 1px solid var(--border); cursor: pointer; color: var(--text); display: inline-flex; align-items: center; gap: 0.25rem; white-space: nowrap; }}
    .flow-node-pill:hover {{ border-color: var(--accent); color: var(--accent); background: var(--surface); }}
    .flow-node-pill.is-trigger {{ background: color-mix(in srgb, var(--source) 18%, var(--surface)); border-color: var(--source); color: var(--source); }}
    .flow-node-pill.is-target {{ background: color-mix(in srgb, var(--output) 18%, var(--surface)); border-color: var(--output); color: var(--output); font-weight: 800; }}

    /* Simplified Node Details */
    .node-details-card {{ background: var(--card-bg); border: 1px solid var(--border); border-radius: 8px; padding: 0.75rem; display: flex; flex-direction: column; gap: 0.45rem; }}
    .node-details-header {{ display: flex; flex-wrap: wrap; align-items: baseline; justify-content: space-between; gap: 0.5rem; }}
    .node-details-name {{ flex: 1 1 12rem; min-width: 0; font: 750 0.84rem var(--mono); color: var(--text); }}
    .node-details-meta {{ font: 600 0.68rem var(--mono); color: var(--text-muted); }}
    .node-connections {{ display: flex; flex-direction: column; gap: 0.3rem; margin-top: 0.2rem; }}
    .connections-label {{ font-size: 0.66rem; font-weight: 700; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.04em; }}
    .connections-pills {{ display: flex; flex-wrap: wrap; gap: 0.3rem; }}
    .conn-pill {{ font: 650 0.68rem var(--mono); padding: 0.18rem 0.4rem; border-radius: 4px; background: var(--surface); border: 1px solid var(--border); color: var(--text); cursor: pointer; }}
    .conn-pill:hover {{ border-color: var(--accent); color: var(--accent); }}
    .conn-pill-empty {{ font: 500 0.68rem var(--mono); color: var(--text-muted); font-style: italic; }}

    /* Code Preview Drawer */
    .source-drawer {{ background: var(--surface); border: 1px solid var(--border); border-radius: 8px; overflow: hidden; }}
    .source-drawer-toggle {{ width: 100%; padding: 0.45rem 0.65rem; background: var(--surface-2); border: none; border-bottom: 1px solid var(--border); color: var(--text); font: 700 0.7rem var(--mono); text-align: left; cursor: pointer; display: flex; justify-content: space-between; align-items: center; }}
    .source-drawer-toggle:hover {{ background: var(--surface-3); }}
    .source-drawer-code {{ padding: 0.4rem 0; font: 500 0.72rem/1.55 var(--mono); background: var(--source-panel-bg); color: var(--source-panel-text); white-space: pre; overflow-x: auto; max-height: 220px; }}
    .source-drawer-code .source-line {{ display: flex; padding: 0 0.6rem 0 0; line-height: 1.55em; min-height: 1.55em; }}
    .source-drawer-code .source-line-num {{ width: 2.2rem; min-width: 2.2rem; padding-right: 0.6rem; text-align: right; color: var(--text-muted); user-select: none; -webkit-user-select: none; opacity: 0.6; font-size: 0.68rem; }}
    .source-drawer-refs {{ padding: 0.4rem 0.65rem; font: 600 0.66rem var(--mono); color: var(--text-muted); border-top: 1px solid var(--border); background: var(--surface-2); display: flex; align-items: center; gap: 0.4rem; flex-wrap: wrap; }}


    .timeline-panel {{ display: flex; flex-direction: column; }}
    .source-panel {{ position: relative; overflow: auto; padding: 0.75rem 0; background: var(--source-panel-bg); color: var(--source-panel-text); font: 500 0.76rem/1.62 var(--mono); white-space: pre; tab-size: 4; }}
    #source-file-select {{ display: block; position: sticky; top: 0; z-index: 2; margin: 0 1rem 0.5rem; max-width: calc(100% - 2rem); background: var(--surface); color: var(--text); }}
    #source-file-select[hidden] {{ display: none; }}
    .source-panel code {{ position: relative; z-index: 1; font: inherit; display: block; min-width: 100%; }}
    .source-line {{ display: flex; padding: 0 1rem 0 0; min-height: 1.62em; line-height: 1.62em; transition: background 120ms ease; }}
    .source-line:hover {{ background: color-mix(in srgb, var(--surface-3) 40%, transparent); }}
    .source-line.is-active {{ background: color-mix(in srgb, var(--line-accent, var(--accent)) 14%, transparent); box-shadow: inset 3px 0 var(--line-accent, var(--accent)); }}
    .source-line.is-active.is-mark {{ --line-accent: var(--timeline-mark); }}
    .source-line.is-active.is-error {{ --line-accent: var(--timeline-error); }}
    .source-line.is-active.is-mark .source-line-content, .source-line.is-active.is-mark .source-line-content span {{ color: var(--timeline-mark); }}
    .source-line-num {{ display: inline-block; width: 3.2rem; min-width: 3.2rem; padding-right: 1rem; text-align: right; color: var(--text-muted); user-select: none; -webkit-user-select: none; font-size: 0.7rem; opacity: 0.65; }}
    .source-line-content {{ flex: 1; white-space: pre; }}
    .video-panel {{ display: flex; flex-direction: column; padding: 1rem; gap: 0.8rem; background: var(--surface); overflow: auto; }}
    .video-container {{ width: 100%; border-radius: 8px; overflow: hidden; border: 1px solid var(--border); background: #000; }}
    .video-container video {{ width: 100%; display: block; }}
    .video-meta {{ display: flex; align-items: center; justify-content: space-between; gap: 0.5rem; flex-wrap: wrap; }}
    .video-badge {{ background: color-mix(in srgb, var(--accent) 18%, var(--surface-2)); border: 1px solid var(--accent); color: var(--accent); border-radius: 999px; padding: 0.2rem 0.55rem; font: 700 0.68rem var(--mono); }}
    .video-sync-status {{ color: var(--output); font: 700 0.68rem var(--mono); display: inline-flex; align-items: center; gap: 0.3rem; }}
    .video-filename {{ color: var(--text-muted); font: 500 0.7rem var(--mono); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
    .video-help {{ color: var(--text-muted); font-size: 0.72rem; line-height: 1.5; text-wrap: pretty; }}
    .syntax-keyword {{ color: var(--effect); font-weight: 700; }}
    [data-theme="light"] .syntax-keyword {{ color: #7e22ce; font-weight: 700; }}
    .syntax-string {{ color: var(--output); }}
    [data-theme="light"] .syntax-string {{ color: #15803d; }}
    .syntax-number {{ color: var(--calc); }}
    [data-theme="light"] .syntax-number {{ color: #b45309; }}
    .syntax-operator {{ color: var(--text-muted); }}
    .syntax-comment {{ color: var(--text-muted); font-style: italic; }}
    .event-history {{ flex-shrink: 0; min-width: 0; padding:.5rem; }}
    .event-history summary {{ cursor:pointer; font-size:.75rem; }}
    .event-list {{ padding: 0 0.6rem 0.6rem; display: flex; flex-direction: column; gap: 0.35rem; }}
    .event-phase-label {{ position: sticky; top: 0; z-index: 2; margin: 0 -0.6rem; padding: 0.65rem 0.75rem 0.4rem; color: var(--text-muted); background: linear-gradient(var(--surface) 78%, transparent); font: 800 0.64rem var(--mono); letter-spacing: 0.08em; text-transform: uppercase; }}
    .event-item {{ width: 100%; padding: 0.55rem 0.7rem; border-radius: 7px; border: 1px solid var(--border); border-left: 3px solid var(--border-strong); background: var(--surface-2); color: var(--text); text-align: left; cursor: pointer; display: flex; flex-direction: column; gap: 0.25rem; }}
    .event-item:hover {{ background: var(--surface-3); border-color: var(--border-strong); }}
    .event-item.is-current {{ border-color: var(--accent); background: color-mix(in srgb, var(--accent) 12%, var(--surface-2)); }}
    .event-item.kind-input {{ border-left-color: var(--source); }}
    .event-item.kind-calc {{ border-left-color: var(--calc); }}
    .event-item.kind-output {{ border-left-color: var(--output); }}
    .event-item.kind-effect {{ border-left-color: var(--effect); }}
    .event-header {{ display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 0.5rem; }}
    .event-name-wrap {{ flex: 1 1 12rem; min-width: 0; display: flex; align-items: baseline; gap: 0.45rem; }}
    .event-step {{ color: var(--text-muted); font: 650 0.62rem var(--mono); font-variant-numeric: tabular-nums; }}
    .event-name {{ min-width: 0; overflow-wrap: anywhere; font: 700 0.76rem var(--mono); color: var(--text); }}
    .event-badges {{ display: flex; align-items: center; justify-content: flex-end; gap: 0.3rem; flex-wrap: wrap; }}
    .event-time {{ font: 600 0.64rem var(--mono); font-variant-numeric: tabular-nums; color: var(--accent); background: var(--surface-3); border-radius: 4px; padding: 0.1rem 0.3rem; }}
    .event-badge {{ font: 700 0.62rem var(--mono); border-radius: 4px; padding: 0.1rem 0.35rem; text-transform: uppercase; }}
    .event-badge.provenance-observed {{ background: color-mix(in srgb, var(--source) 18%, var(--surface)); color: var(--source); border: 1px solid var(--source); }}
    .event-badge.provenance-inferred {{ background: color-mix(in srgb, var(--effect) 18%, var(--surface)); color: var(--effect); border: 1px solid var(--effect); }}
    .event-badge.assumed {{ background: color-mix(in srgb, var(--output) 18%, var(--surface)); color: var(--output); }}
    .event-badge.affected {{ background: color-mix(in srgb, var(--warning) 18%, var(--surface)); color: var(--warning); }}
    .event-badge.scheduled {{ background: color-mix(in srgb, var(--accent) 18%, var(--surface)); color: var(--accent); }}
    .event-badge.discovered {{ background: var(--surface-3); color: var(--text); }}
    .event-badge.idle {{ background: var(--surface-3); color: var(--text-muted); }}
    .event-badge.active {{ background: color-mix(in srgb, var(--effect) 20%, var(--surface)); color: var(--effect); }}
    .event-details {{ overflow-wrap: anywhere; font-size: 0.72rem; color: var(--text-muted); line-height: 1.35; }}

    .filter-state {{ display: flex; align-items: center; gap: 0.4rem; font-size: 0.75rem; color: var(--text-muted); margin-right: 0.35rem; }}
    #filter-node-count {{ font: 600 0.74rem var(--sans); white-space: nowrap; color: var(--text-muted); }}
    #active-filters {{ display:flex; flex-wrap:wrap; gap:.5rem; }}
    #why-card {{ order:-2; }}
    #node-details-card {{ order:-1; }}

    /* Flush Card in Inspector */
    .flush-card {{ background: var(--card-bg); border: 1.5px solid var(--accent); border-radius: 9px; padding: 0.85rem; display: flex; flex-direction: column; gap: 0.55rem; box-shadow: 0 4px 16px rgba(0,0,0,0.12); }}
    .flush-card-header {{ display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid var(--border); padding-bottom: 0.4rem; }}
    .flush-card-title {{ font: 800 0.84rem var(--sans); color: var(--text); }}
    .flush-card-time {{ font: 700 0.64rem var(--mono); color: var(--accent); background: var(--surface-2); padding: 0.1rem 0.35rem; border-radius: 4px; }}
    .flush-card-body {{ display: flex; flex-direction: column; gap: 0.4rem; }}
    .flush-stage-row {{ display: flex; align-items: baseline; gap: 0.45rem; font-size: 0.72rem; }}
    .stage-tag {{ font: 700 0.6rem var(--mono); text-transform: uppercase; padding: 0.1rem 0.35rem; border-radius: 3px; flex-shrink: 0; }}
    .stage-tag.tag-trigger {{ background: color-mix(in srgb, var(--source) 20%, var(--surface)); color: var(--source); border: 1px solid var(--source); }}
    .stage-tag.tag-invalidated {{ background: color-mix(in srgb, var(--warning) 20%, var(--surface)); color: var(--warning); border: 1px solid var(--warning); }}
    .stage-tag.tag-calcs {{ background: color-mix(in srgb, var(--calc) 20%, var(--surface)); color: var(--calc); border: 1px solid var(--calc); }}
    .stage-tag.tag-outputs {{ background: color-mix(in srgb, var(--output) 20%, var(--surface)); color: var(--output); border: 1px solid var(--output); }}
    .stage-text {{ color: var(--text); font-family: var(--mono); font-size: 0.7rem; word-break: break-word; }}
    .flush-execution-order {{ display: flex; flex-direction: column; gap: 0.25rem; margin-top: 0.35rem; padding-top: 0.35rem; border-top: 1px solid var(--border); max-height: 140px; overflow-y: auto; }}
    .flush-order-item {{ display: flex; align-items: center; gap: 0.4rem; font: 650 0.66rem var(--mono); color: var(--text); padding: 0.18rem 0.35rem; border-radius: 4px; background: var(--surface-2); cursor: pointer; }}
    .flush-order-item:hover {{ background: var(--surface-3); color: var(--accent); }}
    .flush-order-idx {{ color: var(--text-muted); font-size: 0.58rem; width: 14px; text-align: right; }}
    .flush-order-role {{ width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; }}

    /* Keep controls readable and reserve the canvas for the graph. */
    .app-header, .toolbar, .trace-timeline-bar {{ flex-shrink: 0; }}
    .btn, .search-input, .filter-select {{ min-height: 32px; }}
    .btn.icon {{ width: 32px; flex-shrink: 0; }}
    .search-wrap {{ flex: 1 1 200px; max-width: 320px; }}
    .search-results {{ top: calc(100% + 6px); right: 0; left: auto; padding: 8px; }}
    .search-results button {{ border-radius: 5px; margin-top: 4px; line-height: 1.5; }}
    .search-summary {{ padding: 6px; color: var(--text-muted); font-size: 0.75rem; }}
    .graph-container {{ display: flex; flex-direction: column; }}
    .graph-topbar {{ position: relative; top: auto; left: auto; right: auto; padding: 12px; flex-shrink: 0; }}
    .graph-top-row {{ display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 10px; }}
    .causal-summary-banner {{ grid-column: 1 / -1; line-height: 1.5; border-color: var(--border-strong); box-shadow: none; }}
    .legend {{ flex-wrap: wrap; }}
    .zoom-controls {{ align-items: center; }}
    #reactlog-svg {{ flex: 1; min-height: 0; height: 0; }}
    @media (max-width: 1000px) {{
      html, body {{ overflow-x: hidden; max-width: 100vw; }}
      body {{ height: auto; min-height: 100vh; overflow: auto; }}
      .workspace-layout {{ display: flex; flex-direction: column; overflow: visible; flex: none; width: 100%; }}
      .main-view {{ display: flex; flex-direction: column; overflow: visible; flex: none; width: 100%; }}
      .graph-container {{ height: 520px; flex: none; width: 100%; }}
      .sidebar {{ width: 100%; height: 560px; border-top: 1px solid var(--border); }}
      .app-header {{ flex-wrap: wrap; }}
      .header-center {{ order: 3; width: 100%; flex: 1 0 100%; }}
      .toolbar-group {{ width: 100%; }}
      .bottom-timeline-bar.toolbar {{ width: 100%; max-width: 100%; box-sizing: border-box; overflow: visible; height: auto; min-height: 0; }}
    }}
    @media (max-width: 520px) {{
      html, body {{ overflow-x: hidden; max-width: 100vw; }}
      .app-header {{ flex-wrap: wrap; padding: 12px; gap: 10px; }}
      .brand {{ width: 100%; }}
      .header-center {{ flex-wrap: wrap; max-width: 100%; }}
      .header-actions {{ margin-left: auto; }}
      .search-wrap {{ flex-basis: 100%; max-width: none; }}
      .graph-container {{ height: 440px; }}
      .graph-top-row {{ grid-template-columns: 1fr; }}
      .zoom-controls {{ justify-content: flex-end; }}
      .trace-controls {{ flex-wrap: wrap; }}
      .bottom-timeline-bar {{ grid-template-columns: minmax(0, 1fr) auto; }}
      #active-flush-label {{ grid-column: 1 / -1; text-align: start; }}
    }}

    .sidebar-rail {{ width: 40px; min-width: 40px; flex: 0 0 40px; border-left: 1px solid var(--border); background: var(--surface); display: flex; flex-direction: column; align-items: center; gap: 8px; padding: 8px 0; box-sizing: border-box; z-index: 20; }}
    .sidebar {{ position: relative; width: clamp(340px, 28vw, 480px); min-width: 0; max-width: calc(100vw - 42px); flex: 0 0 clamp(340px, 28vw, 480px); height: 100%; border-left: 1px solid var(--border); border-right: none; border-top: none; border-bottom: none; border-radius: 0; box-shadow: none; z-index: 10; }}
    .sidebar-header {{ justify-content: space-between; font: 650 .75rem var(--sans); }}
    .video-panel {{ position: absolute; right: 48px; bottom: 12px; width: min(440px, 48vw, calc(100% - 64px)); padding: 0; gap: 0; z-index: 26; border: 1px solid var(--border-strong); border-radius: 8px; box-shadow: 0 6px 24px #0005; overflow: hidden; transition: left 180ms ease, right 180ms ease; }}
    .main-view.is-inspector-open .video-panel {{ right: auto; left: 12px; }}
    .video-panel[hidden] {{ display: none; }}
    .video-meta {{ padding: 3px 6px; flex-wrap: nowrap; }}
    .video-sync-status {{ font: 600 .65rem var(--sans); }}
    .video-container {{ border: 0; border-radius: 0; aspect-ratio: 16 / 9; }}
    .video-container video {{ width: 100%; height: 100%; object-fit: contain; }}
    .trace-timeline-bar {{ display: flex; flex-direction: column; flex-shrink: 0; border-bottom: 1px solid var(--border); background: var(--bg); padding: 8px 16px; gap: 8px; }}
    .trace-track-wrap {{ position: relative; height: 24px; flex: none; background: var(--track-bg); touch-action: none; }}
    .header-center .search-wrap {{ flex: 1 1 250px; min-width: min(250px, 100%); max-width: 420px; }}
    #scrubber-range {{ appearance: none; -webkit-appearance: none; background: transparent; position: absolute; inset: 0; width: 100%; height: 24px; margin: 0; cursor: pointer; }}
    #scrubber-range::-webkit-slider-runnable-track {{ height: 18px; background: linear-gradient(to right, var(--track-fill) var(--progress, 0%), transparent var(--progress, 0%)); }}
    #scrubber-range::-moz-range-track {{ height: 18px; background: transparent; }}
    #scrubber-range::-moz-range-progress {{ height: 18px; background: var(--track-fill); }}
    #scrubber-range::-webkit-slider-thumb {{ appearance: none; -webkit-appearance: none; height: 24px; width: 3px; margin-top: -3px; background: transparent; }}
    #scrubber-range::-moz-range-thumb {{ height: 24px; width: 3px; border: 0; border-radius: 0; background: transparent; }}
    #scrubber-range:focus-visible {{ outline: 2px solid var(--accent); outline-offset: 3px; }}
    #trace-markers {{ position: absolute; inset: 0 1.5px; pointer-events: none; z-index: 1; }}
    .timeline-marker {{ position: absolute; top: 0; height: 100%; min-width: 3px; padding: 0; border: 0; border-radius: 0; background: var(--timeline-idle); pointer-events: auto; cursor: pointer; }}
    .timeline-marker.is-output {{ top: 5px; height: 14px; border-radius: 2px; background: var(--timeline-output); }}
    .timeline-marker.is-mark {{ background: var(--timeline-mark); z-index: 2; }}
    .timeline-marker.is-error {{ background: var(--timeline-error); min-width: 5px; z-index: 3; }}
    .timeline-marker.is-idle, .timeline-key .key-idle {{ box-shadow: inset 1px 0 var(--timeline-idle-outline); }}
    .timeline-marker:hover, .timeline-marker:focus-visible {{ outline: 2px solid var(--text); outline-offset: 1px; z-index: 3; }}
    .timeline-playhead {{ position: absolute; top: -3px; bottom: -3px; width: 2px; background: var(--playhead-bg); box-shadow: 0 0 0 1px var(--playhead-ring); pointer-events: none; z-index: 4; }}
    .timeline-playhead::before {{ content: ''; position: absolute; left: -3px; top: -3px; border-left: 4px solid transparent; border-right: 4px solid transparent; border-top: 5px solid var(--playhead-bg); }}
    .timeline-key {{ display: flex; align-items: center; flex-wrap: wrap; gap: 12px; color: var(--text-muted); font: .7rem var(--sans); }}
    .timeline-key span {{ display: inline-flex; align-items: center; gap: 5px; }}
    .timeline-key i {{ display: inline-block; width: 3px; height: 14px; border-radius: 1px; background: var(--timeline-idle); }}
    .timeline-key .key-output {{ height: 8px; border-radius: 2px; background: var(--timeline-output); }}
    .timeline-key .key-mark {{ background: var(--timeline-mark); border-radius: 1px; }}
    .timeline-key .key-error {{ background: var(--timeline-error); width: 5px; }}
    .timeline-key .key-position {{ width: 2px; background: var(--playhead-bg); box-shadow: 0 0 0 1px var(--playhead-ring); }}
    .timeline-tooltip {{ position: absolute; top: calc(100% + 6px); left: 0; max-width: min(440px, 100%); padding: 6px 9px; border: 1px solid var(--border-strong); border-radius: 4px; background: var(--surface); color: var(--text); font: .75rem var(--sans); box-shadow: 0 3px 12px #0004; z-index: 50; pointer-events: none; }}
    .timeline-tooltip[hidden] {{ display: none; }}
    .timeline-navigation {{ display: flex; align-items: center; gap: 6px; white-space: nowrap; }}
    .status-center {{ gap: 3px; }}
    .status-center .btn {{ width: 28px; min-height: 28px; height: 28px; }}
    .status-center .nav-idle svg {{ color: var(--timeline-idle); }}
    .status-center .nav-output svg {{ color: var(--timeline-output); }}
    .status-center .nav-mark svg {{ color: var(--timeline-mark); }}
    .settings-wrap {{ position: relative; display: inline-flex; }}
    .settings-menu {{ position: absolute; top: calc(100% + 6px); right: 0; width: 220px; background: var(--surface); border: 1px solid var(--border-strong); border-radius: 8px; padding: 10px 12px; box-shadow: 0 10px 28px rgba(0, 0, 0, 0.28); z-index: 100; display: flex; flex-direction: column; gap: 10px; }}
    .settings-menu[hidden] {{ display: none !important; }}
    .settings-menu-header {{ font: 700 0.72rem var(--sans); color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.04em; padding-bottom: 5px; border-bottom: 1px solid var(--border); }}
    .settings-menu-item {{ display: flex; flex-direction: column; gap: 4px; }}
    .settings-menu-label {{ font: 650 0.7rem var(--sans); color: var(--text); }}
    .settings-select {{ width: 100%; }}
    .settings-menu-divider {{ height: 1px; background: var(--border); margin: 2px 0; }}
    .settings-menu-actions {{ display: flex; flex-direction: column; gap: 6px; }}
    .settings-action-btn {{ width: 100%; justify-content: center; }}
    .status-left, .status-center, .status-right {{ flex-wrap: wrap; }}
    @media (max-width: 1000px) {{
      .workspace-layout {{ flex: 1; min-height: 350px; overflow: hidden; }}
      .main-view {{ flex: 1; flex-direction: row; min-height: 350px; overflow: hidden; }}
      .graph-container {{ flex: 1; width: auto; height: auto; min-height: 350px; }}
      .sidebar {{ width: clamp(280px, 35vw, 420px); flex: 0 0 clamp(280px, 35vw, 420px); height: 100%; border-top: none; border-left: 1px solid var(--border); }}
    }}

    /* Readable graph keys, controls, and keyboard focus in both themes. */
    .legend {{ gap: 6px 14px; align-items: center; }}
    .legend-group {{ display: flex; flex-wrap: wrap; align-items: center; gap: 4px 7px; }}
    .legend-label {{ color: var(--text); font: 700 12px var(--sans); }}
    .legend-item {{ font: 600 12px var(--sans); }}
    .legend-dot {{ width: 12px; height: 12px; }}
    .legend-swatch {{ border-color: var(--node-stroke); }}
    .graph-top-row {{ align-items: start; }}
    .node-focus-ring {{ opacity: 0; stroke: var(--text); stroke-width: 4px; stroke-linejoin: round; pointer-events: none; }}
    .graph-node:focus-visible {{ outline: none; }}
    .graph-node:focus-visible .node-focus-ring {{ opacity: 1; }}
    .graph-node.is-clientdata {{ opacity: 1; }}
    .source-line-num, .source-drawer-code .source-line-num {{ opacity: 1; }}
    @media (prefers-reduced-motion: reduce) {{
      *, *::before, *::after {{ scroll-behavior: auto !important; transition: none !important; }}
    }}
    @media (forced-colors: active) {{
      .legend-swatch, .timeline-marker {{ forced-color-adjust: none; }}
      .graph-node.is-selected .node-card {{ stroke: Highlight !important; }}
    }}
    .module-name {{ color: var(--module-text); fill: var(--module-text); font-weight: 700; }}
    .graph-node .module-name {{ fill: #3b0764; }}
    .graph-node[data-state="frozen"] .module-name {{ fill: #e9d5ff; }}
    .step-display {{ margin-left: 8px; color: var(--text-muted); }}
  </style>
</head>
<body>
  <header class="app-header">
    <div class="brand">
      <div class="brand-mark" aria-hidden="true">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
      </div>
      <div class="brand-copy">
        <h1 class="brand-title">{escaped_title}</h1>
        <div class="brand-subtitle">Reactlog report</div>
      </div>
    </div>
    <div class="header-center">
      <div class="search-wrap">
        <svg class="search-icon" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
        <input type="search" class="search-input" id="search-input" name="reactive-node-filter" autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false" placeholder="Search names or module:name" onfocus="handleSearch(this.value, false)" oninput="handleSearch(this.value, true)" aria-label="Filter reactive nodes by name, type, id, or module" role="combobox" aria-autocomplete="list" aria-expanded="false" aria-controls="search-results" onkeydown="handleSearchKey(event)" />
        <button type="button" class="search-clear" id="search-clear" aria-label="Clear node filter" title="Clear filter" onclick="clearSearchFilter()" hidden>×</button>
        <button type="button" class="search-toggle" aria-label="Show node choices" aria-controls="search-results" aria-expanded="false" onclick="toggleSearchChoices()">▾</button>
        <div id="search-results" class="search-results" role="listbox" aria-label="Node search results" onkeydown="handleSearchKey(event)" hidden></div>
      </div>
    </div>
    <div class="header-actions">
      <button class="btn icon" id="btn-theme-toggle" onclick="toggleTheme()" aria-label="Toggle light/dark theme" title="Toggle theme"></button>
      <input type="file" id="reactlog-file-input" accept=".json" style="display:none" onchange="handleReactlogFileUpload(event)" />
      <button class="btn" id="btn-open-json" onclick="document.getElementById('reactlog-file-input').click()" title="Open Reactlog JSON recording"><svg class="inline-icon" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="12" y1="18" x2="12" y2="12"/><line x1="9" y1="15" x2="15" y2="15"/></svg>Open JSON</button>
      <button class="btn icon" id="btn-shortcuts" aria-label="Keyboard shortcuts" onclick="toggleShortcutsModal()" title="Keyboard shortcuts (?)"><svg class="inline-icon" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="20" height="16" x="2" y="4" rx="2"/><path d="M6 8h.001"/><path d="M10 8h.001"/><path d="M14 8h.001"/><path d="M18 8h.001"/><path d="M8 12h.001"/><path d="M12 12h.001"/><path d="M16 12h.001"/><path d="M7 16h10"/></svg></button>
      <button class="btn icon" id="btn-toggle-inspector" onclick="toggleInspector()" aria-label="Toggle inspector details" title="Toggle inspector details panel"><svg class="inline-icon" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="18" x="3" y="3" rx="2"/><path d="M15 3v18"/></svg></button>
    </div>
  </header>

  <div class="trace-timeline-bar" id="trace-timeline-bar" aria-label="Execution timeline">
    <div class="bottom-timeline-bar toolbar" id="bottom-timeline-bar" role="toolbar" aria-label="Timeline controls">
      <span class="trace-status-line" id="trace-status-line">Step 0 of 0</span>
      <div class="timeline-navigation">
        <button class="btn mini" id="btn-play" onclick="togglePlay()" aria-label="Play timeline" title="Play / Pause (Space)">▶ Play</button>
        <div class="status-time-group">
          <span class="trace-clock" id="trace-current-time">0.0s</span><span class="trace-sep">/</span><span class="trace-total" id="trace-total-time">0.0s</span><span class="step-display" id="step-display">Step 0 / 0</span>
        </div>
      </div>
      <span id="active-flush-label" role="status"></span>
    </div>
    <div id="trace-track-wrap" class="trace-track-wrap">
      <div id="trace-markers" role="group" aria-label="Timeline marks"></div>
      <div id="timeline-playhead" class="timeline-playhead" aria-hidden="true"></div>
      <div id="timeline-tooltip" class="timeline-tooltip" role="tooltip" hidden></div>
      <input type="range" id="scrubber-range" min="0" max="0" value="0" oninput="seekTo(Number(this.value))" aria-label="Timeline step scrubber" />
    </div>
    <div class="timeline-key" id="timeline-key" aria-label="Timeline key">
      <span><i class="key-idle"></i>Idle</span><span><i class="key-output"></i>Output calculation</span>
      <span><i class="key-mark"></i>User mark</span><span><i class="key-error"></i>Error</span><span><i class="key-position"></i>Current step</span>
    </div>
  </div>

  <div class="workspace-layout">
    <!-- Main View & Graph Canvas -->
    <main class="main-view" id="main-view">
      <div class="graph-container" id="graph-container">
        <div class="graph-topbar">
          <div class="graph-top-row">
            <div class="legend" aria-label="Graph legend">
              <div class="legend-group"><span class="legend-label">State</span>
              <div class="legend-item"><span class="legend-swatch" style="background:var(--state-ready)"></span>Ready</div>
              <div class="legend-item"><span class="legend-swatch" style="background:var(--state-calculating)"></span>Calculating</div>
              <div class="legend-item"><span class="legend-swatch" style="background:var(--state-invalidating)"></span>Invalidating</div>
              <div class="legend-item"><span class="legend-swatch" style="background:var(--state-invalidated)"></span>Invalidated</div>
              <div class="legend-item"><span class="legend-swatch" style="background:var(--state-frozen)"></span>Frozen</div>
              <div class="legend-item"><span class="legend-swatch" style="background:var(--state-error)"></span>Error</div>
              </div>
              <div class="legend-group"><span class="legend-label">Links</span>
              <div class="legend-item"><span class="legend-line"></span>Dependency</div>
              <div class="legend-item"><span class="legend-line is-isolated"></span>Isolated dependency</div>
              <div class="legend-item"><span class="legend-line is-inactive"></span>Inactive dependency</div>
              </div>
            </div>
            <div class="zoom-controls">
              <div class="filter-state" aria-label="Current exploration scope">
                <span id="filter-node-count" role="status" aria-live="polite"></span>
                <div id="active-filters"></div>
              </div>
              <button class="btn icon mini" onclick="zoomIn()" aria-label="Zoom in" title="Zoom in"><svg width="18" height="18" aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" x2="16.65" y1="21" y2="16.65"/><line x1="11" x2="11" y1="8" y2="14"/><line x1="8" x2="14" y1="11" y2="11"/></svg></button>
              <button class="btn icon mini" onclick="zoomOut()" aria-label="Zoom out" title="Zoom out"><svg width="18" height="18" aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" x2="16.65" y1="21" y2="16.65"/><line x1="8" x2="14" y1="11" y2="11"/></svg></button>
              <button class="btn icon mini" id="btn-fullscreen" onclick="toggleFullscreen()" aria-label="Full screen" title="Full screen"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 3H5a2 2 0 0 0-2 2v3"/><path d="M21 8V5a2 2 0 0 0-2-2h-3"/><path d="M3 16v3a2 2 0 0 0 2 2h3"/><path d="M16 21h3a2 2 0 0 0 2-2v-3"/></svg></button>
              <div class="settings-wrap" id="settings-wrap">
                <button class="btn icon mini" id="btn-settings" onclick="toggleSettingsMenu()" aria-label="Graph settings" aria-expanded="false" title="Graph view settings"><svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg></button>
                <div class="settings-menu" id="settings-menu" hidden>
                  <div class="settings-menu-header">View Settings</div>
                  <div class="settings-menu-item">
                    <label for="clientdata-select" class="settings-menu-label">Clientdata</label>
                    <select class="filter-select settings-select" id="clientdata-select" aria-label="Clientdata visibility" onchange="setClientDataVisibility(this.value)">
                      <option value="hide">Hide clientdata</option>
                      <option value="show">Show clientdata</option>
                    </select>
                  </div>
                  <div class="settings-menu-item">
                    <label for="activity-select" class="settings-menu-label">Activity</label>
                    <select class="filter-select settings-select" id="activity-select" aria-label="Activity view" onchange="setViewMode(this.value)">
                      <option value="full">Show all activity</option>
                      <option value="flush">Show current activity</option>
                    </select>
                  </div>
                  <div class="settings-menu-divider"></div>
                  <div class="settings-menu-actions">
                    <button type="button" class="btn mini settings-action-btn" id="btn-toggle-collapse-all" onclick="toggleCollapseAllModules()" title="Collapse all modules into macro boxes">Collapse modules</button>
                    <button type="button" class="btn mini settings-action-btn" id="btn-reset-view" onclick="resetGraphView()" title="Clear node selection and filters, then fit the full graph">Reset view</button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div id="live-action-toast" class="action-toast" role="status" aria-live="polite" hidden></div>
        <button class="btn mini primary" id="btn-inspect-selection" onclick="showSidebarPanel('timeline')" aria-label="Open selected node details" hidden style="position:absolute;left:1rem;bottom:1rem;z-index:28;">Inspect node</button>

        <div class="empty-graph-message" id="empty-graph-message" role="status" hidden>No recorded changes or executions in this view. Select Show all nodes to see the full graph.</div>
        <svg id="reactlog-svg" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6.5" markerHeight="6.5" orient="auto">
              <path d="M 0.5 1.5 L 8.5 5 L 0.5 8.5 L 2.3 5 z" fill="var(--text-muted)" />
            </marker>
            <marker id="arrow-isolated" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6.5" markerHeight="6.5" orient="auto">
              <path d="M 0.8 1.8 L 8 5 L 0.8 8.2 z" fill="var(--bg)" stroke="var(--text-muted)" stroke-width="1.5" stroke-linejoin="round" />
            </marker>
            <marker id="arrow-active" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7.5" markerHeight="7.5" orient="auto">
              <path d="M 0.5 1.5 L 8.5 5 L 0.5 8.5 L 2.3 5 z" fill="var(--accent)" />
            </marker>
            <filter id="card-shadow" x="-10%" y="-10%" width="120%" height="130%">
              <feDropShadow dx="0" dy="3" stdDeviation="5" flood-color="#000" flood-opacity="0.22" />
            </filter>
          </defs>
          <g id="viewport-g">
            <g id="graph-content"></g>
            <g id="graph-edge-pulses" aria-hidden="true"></g>
          </g>
        </svg>
      </div>

      <aside class="sidebar" id="sidebar" aria-label="Details and events" hidden>
        <div class="sidebar-header">
          <span id="detail-panel-title">Node details</span>
          <button class="btn icon mini" id="btn-close-sidebar" onclick="closeSidebarAndClearSelection()" aria-label="Close Inspector" title="Close Inspector">✕</button>
        </div>

        <div class="timeline-panel sidebar-panel" id="timeline-panel" role="tabpanel" aria-label="Node details">
          <div class="inspector-container">
            <details class="flush-card" id="flush-card">
              <summary class="flush-card-header">
                <div class="flush-card-title" id="flush-card-title">Activity 1: Initial render</div>
                <span class="flush-card-time" id="flush-card-time">0.0s</span>
              </summary>
              <div class="flush-card-body">
                <div class="flush-stage-row">
                  <span class="stage-tag tag-trigger">Trigger</span>
                  <span class="stage-text" id="flush-card-trigger">Application Initialization</span>
                </div>
                <div class="flush-stage-row">
                  <span class="stage-tag tag-invalidated">Invalidated</span>
                  <span class="stage-text" id="flush-card-invalidated">0 nodes</span>
                </div>
                <div class="flush-stage-row">
                  <span class="stage-tag tag-calcs">Recalculated</span>
                  <span class="stage-text" id="flush-card-calcs">0 calcs</span>
                </div>
                <div class="flush-stage-row">
                  <span class="stage-tag tag-outputs">Rendered</span>
                  <span class="stage-text" id="flush-card-outputs">0 outputs</span>
                </div>
                <div class="flush-execution-order" id="flush-execution-order"></div>
              </div>
            </details>

            <div class="why-card" id="why-card">
              <div class="why-header">
                <div class="why-title" id="why-title">Select a node to inspect causality</div>
              </div>
              <div class="why-narrative" id="why-story">
                Click any node in the reactive graph or step through the timeline to see why it ran and what caused it.
              </div>
              <div class="why-dag-tree" id="why-cascade-flow"></div>
            </div>

            <div class="node-details-card" id="node-details-card">
              <div class="node-details-header">
                <div class="node-details-name" id="insp-title">session</div>
                <span class="node-details-meta" id="insp-meta-line">Line —</span>
                <span class="node-details-meta" id="insp-runs-badge" style="margin-left: 6px; font-weight: 600;"></span>
                <button class="btn mini" id="btn-filter-lineage" onclick="filterLineageForNode(selectedNodeId)" title="Filter graph to this node, its ancestors, and descendants" style="display:none;margin-left:auto;">Filter lineage</button>
                <span id="insp-type" style="display:none">Initialization event</span>
                <span id="insp-status" style="display:none">active</span>
              </div>
              <div class="node-connections" id="insp-downstream-section">
                <div class="connections-label">Feeds into (Downstream):</div>
                <div class="connections-pills" id="insp-downstream-list"><span class="conn-pill-empty">None</span></div>
              </div>
              <div class="node-connections" id="insp-upstream-section">
                <div class="connections-label">Depends on (Upstream):</div>
                <div class="connections-pills" id="insp-upstream-list"><span class="conn-pill-empty">None</span></div>
              </div>
            </div>

            <figure id="insp-plot" hidden>
              <img id="insp-plot-image" alt="Recorded plot" hidden />
              <figcaption id="insp-plot-caption"></figcaption>
            </figure>
            <div class="source-drawer" id="insp-source-drawer" hidden>
              <button class="source-drawer-toggle" id="btn-toggle-source-drawer" onclick="toggleSourceDrawer()" aria-expanded="false">
                <span id="source-drawer-label">Source code</span>
                <span id="source-drawer-arrow">▾</span>
              </button>
              <pre class="source-drawer-code" id="insp-source-code" hidden><code></code></pre>
              <div class="source-drawer-refs" id="insp-source-refs" hidden></div>
            </div>
          </div>
          <details class="event-history" id="event-history"><summary>Event history</summary><div class="event-list" id="event-list"></div></details>
        </div>

        {source_panel}
      </aside>

      <nav class="sidebar-rail" id="sidebar-rail" aria-label="Graph tools">
        <button class="btn icon" id="btn-toggle-inspector-bottom" onclick="showSidebarPanel('timeline')" aria-label="Node details" title="Node details"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7v1"/></svg></button>
        {source_tab}
        {video_tab_btn}
      </nav>
      {video_panel}
    </main>
  </div>

  <script>
    const reactlogData = {escaped_json};
    const rawAppSource = {escaped_source_raw};
    const ICONS = {{
      play: '<svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><polygon points="6 3 20 12 6 21 6 3"/></svg>',
      pause: '<svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg>',
      video: '<svg class="inline-icon" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m16 13 5.223 3.482a.5.5 0 0 0 .777-.416V7.87a.5.5 0 0 0-.752-.432L16 10.5"/><rect x="2" y="6" width="14" height="12" rx="2"/></svg>',
      eye: '<svg class="inline-icon" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/></svg>',
      zap: '<svg class="inline-icon" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>',
      clock: '<svg class="inline-icon" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>',
      arrowRight: '<svg class="inline-icon" width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>',
      flame: '<svg class="inline-icon flame-icon" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="color:var(--danger, #ef4444);vertical-align:-1px;margin-left:4px;"><path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z"/></svg>'
    }};

    const ALL_ROLES = ['source', 'conductor', 'effect', 'output'];
    let currentStep = 0;
    let isPlaying = false;
    let playTimer = null;
    let selectedNodeId = null;
    let focusedNodeId = null;
    let selectedSearchNodeId = null;
    let searchQuery = "";
    let activeRoles = new Set(['source', 'conductor', 'observer', 'effect', 'output']);
    let hideClientData = true;
    let changedNodesOnly = false;
    let changedNodeIds = null;
    let activeBurstIndex = 0;
    let zoomLevel = 1;
    let panOffset = {{ x: 0, y: 0 }};
    let isPanning = false;
    let startPan = {{ x: 0, y: 0 }};
    let maxSessionDuration = 1.0;
    let timelineStops = [];
    let videoFrameRequest = null;
    let graphSeekTime = null;
    let videoFrameRequestKind = null;
    let isSourceDrawerOpen = false;

    let currentViewMode = 'flush';
    let eventListScope = null;
    let selectedStageFilter = null;

    let nodeIndex = new Map();
    let adjUpstream = new Map();
    let adjDownstream = new Map();
    let actionWaves = [];
    let allBursts = [];
    let executionCounts = new Map();

    function getActiveTheme() {{
      const currentAttr = document.documentElement.getAttribute('data-theme');
      if (currentAttr === 'light' || currentAttr === 'dark') return currentAttr;
      if (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) return 'light';
      return 'dark';
    }}

    function updateThemeButton() {{
      const btn = document.getElementById('btn-theme-toggle');
      if (!btn) return;
      const isLight = getActiveTheme() === 'light';
      btn.innerHTML = isLight
        ? '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/></svg>'
        : '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/></svg>';
      btn.title = isLight ? 'Switch to dark mode' : 'Switch to light mode';
      btn.setAttribute('aria-label', btn.title);
    }}

    function toggleTheme() {{
      const current = getActiveTheme();
      const next = current === 'light' ? 'dark' : 'light';
      document.documentElement.setAttribute('data-theme', next);
      try {{ localStorage.setItem('shiny_reactlog_theme', next); }} catch (e) {{}}
      updateThemeButton();
      renderGraph();
    }}

    function initTheme() {{
      let saved = null;
      try {{ saved = localStorage.getItem('shiny_reactlog_theme'); }} catch (e) {{}}
      if (saved === 'light' || saved === 'dark') {{
        document.documentElement.setAttribute('data-theme', saved);
      }}
      updateThemeButton();
    }}

    function buildGraphIndices() {{
      nodeIndex.clear();
      adjUpstream.clear();
      adjDownstream.clear();
      executionCounts.clear();

      const nodes = reactlogData.nodes || [];
      const edges = reactlogData.edges || [];
      const events = reactlogData.events || reactlogData.log || [];

      nodes.forEach(n => {{
        nodeIndex.set(n.id, n);
        adjUpstream.set(n.id, new Set());
        adjDownstream.set(n.id, new Set());
        executionCounts.set(n.id, 0);
      }});

      edges.forEach(e => {{
        if (e.isolated) return;
        if (adjDownstream.has(e.from)) adjDownstream.get(e.from).add(e.to);
        if (adjUpstream.has(e.to)) adjUpstream.get(e.to).add(e.from);
      }});

      events.forEach(ev => {{
        const nid = ev.node_id || ev.id;
        const act = ev.action || ev.event;
        if (nid && (act === 'wouldEvaluate' || act === 'outputUpdated' || act === 'valueChange' || act === 'enter' || act === 'exit')) {{
          executionCounts.set(nid, (executionCounts.get(nid) || 0) + 1);
        }}
      }});
    }}

    function getUpstreamNodes(nodeId) {{
      const ancestors = new Set();
      const queue = [nodeId];
      while (queue.length > 0) {{
        const curr = queue.shift();
        const parents = adjUpstream.get(curr) || new Set();
        for (const p of parents) {{
          if (!ancestors.has(p)) {{
            ancestors.add(p);
            queue.push(p);
          }}
        }}
      }}
      return ancestors;
    }}

    function getDownstreamNodes(nodeId) {{
      const descendants = new Set();
      const queue = [nodeId];
      while (queue.length > 0) {{
        const curr = queue.shift();
        const children = adjDownstream.get(curr) || new Set();
        for (const c of children) {{
          if (!descendants.has(c)) {{
            descendants.add(c);
            queue.push(c);
          }}
        }}
      }}
      return descendants;
    }}

    function getActiveLineageSet() {{
      if (!searchQuery) return null;
      const isIdQuery = searchQuery.startsWith('id:');
      const selectedSearchNode = selectedSearchNodeId ? nodeIndex.get(selectedSearchNodeId) : null;
      const focusedNode = focusedNodeId ? nodeIndex.get(focusedNodeId) : null;
      const matchedNode = (selectedSearchNode && searchQuery === nodeDisplayName(selectedSearchNode).toLowerCase())
        ? selectedSearchNode
        : ((focusedNode && searchQuery === nodeDisplayName(focusedNode).toLowerCase()) ? focusedNode : null);
      if (!isIdQuery && !matchedNode) return null;
      const matchingIds = matchedNode ? [matchedNode.id] : [];
      if (isIdQuery) {{
        const needle = searchQuery.slice(3).trim().toLowerCase();
        if (!needle) return null;
        (reactlogData.nodes || []).forEach(n => {{
          const nid = String(n.id || '').toLowerCase();
          const nlabel = String(n.label || '').toLowerCase();
          const nname = String(n.name || '').toLowerCase();
          if (
            nid === needle ||
            nid.endsWith(':' + needle) ||
            nid.includes(needle) ||
            nlabel === needle ||
            nname === needle
          ) {{
            matchingIds.push(n.id);
          }}
        }});
      }}
      if (matchingIds.length === 0) return null;
      const lineage = new Set(matchingIds);
      matchingIds.forEach(id => {{
        getUpstreamNodes(id).forEach(ancestorId => lineage.add(ancestorId));
        getDownstreamNodes(id).forEach(descendantId => lineage.add(descendantId));
      }});
      return lineage;
    }}

    function syncSearchClearButton() {{
      const input = document.getElementById('search-input');
      const clearBtn = document.getElementById('search-clear');
      if (!clearBtn) return;
      const hasValue = Boolean((input && input.value && input.value.trim()) || searchQuery || selectedSearchNodeId);
      clearBtn.hidden = !hasValue;
    }}

    function filterLineageForNode(nodeId) {{
      if (!nodeId) return;
      const node = nodeIndex.get(nodeId);
      const filterVal = node ? nodeDisplayName(node) : `id:${{nodeId}}`;
      selectedSearchNodeId = nodeId;
      searchQuery = filterVal.toLowerCase();
      document.getElementById('search-input').value = filterVal;
      syncSearchClearButton();
      closeSearchChoices();
      if (node && isClientDataNode(node)) setClientDataVisibility('show');
      if (node && changedNodeIds && !changedNodeIds.has(node.id)) changedNodesOnly = false;
      activeRoles = new Set(['source', 'conductor', 'observer', 'effect', 'output']);
      selectNode(nodeId);
      refreshExploration();
      fitGraph();
    }}

    function prepareEventTimings() {{
      const events = reactlogData.events || reactlogData.log || [];
      if (!events || events.length === 0) return;

      let i = 0;
      while (i < events.length) {{
        const baseTime = events[i].time_sec !== undefined ? events[i].time_sec : (events[i].time !== undefined ? events[i].time : 0);
        let j = i;
        while (j < events.length && Math.abs(((events[j].time_sec !== undefined ? events[j].time_sec : events[j].time) || 0) - baseTime) < 0.04) {{
          j++;
        }}
        const clusterLen = j - i;
        const nextTime = (j < events.length && (events[j].time_sec !== undefined || events[j].time !== undefined)) ? (events[j].time_sec ?? events[j].time) : (baseTime + 1.2);
        const windowDuration = Math.min(0.75, Math.max(0.25, (nextTime - baseTime) * 0.7));

        for (let k = 0; k < clusterLen; k++) {{
          const evIdx = i + k;
          if (events[evIdx].time_sec !== undefined || events[evIdx].time !== undefined) {{
            events[evIdx].effective_time = baseTime + (clusterLen > 1 ? (k / (clusterLen - 1)) * windowDuration : 0);
          }} else {{
            events[evIdx].effective_time = baseTime;
          }}
        }}
        i = j;
      }}
    }}

    function filterItems(arr, predicate) {{
      const out = [];
      for (const item of (arr || [])) {{
        if (predicate(item)) out.push(item);
      }}
      return out;
    }}

    function cleanName(n) {{
      if (!n) return '';
      let s = String(n);
      s = s.replace(/^Observed\\s+[^:]*:\\s*/i, '');
      s = s.replace(/^click\\s+(on\\s+)?/i, '');
      s = s.replace(/^(input|output|calc|effect)[:.]/, '');
      s = s.replace(/^(input#|#)/, '');
      s = s.replace(/^(on[,\\s]+)/i, '');
      s = s.replace(/^[.#]/, '');
      s = s.split('=')[0].trim();
      return s;
    }}

    function formatHumanValue(val) {{
      if (val === null || val === undefined) return '';
      if (typeof val === 'string' && val.length > 20) return val.slice(0, 18) + '…';
      return String(val);
    }}

    function buildActionWaves() {{
      if (reactlogData.action_waves && reactlogData.action_waves.length > 0) {{
        const rawWaves = reactlogData.action_waves;
        const coalesced = [];
        for (let i = 0; i < rawWaves.length; i++) {{
          const w = rawWaves[i];
          const nextW = rawWaves[i + 1];
          if (nextW && w.trigger && w.trigger.startsWith('Click:') && (w.inferred_executions || []).length === 0 && Math.abs((nextW.start_time || 0) - (w.start_time || 0)) <= 0.05) {{
            nextW.human_action = `${{w.trigger}} → ${{nextW.human_action || nextW.trigger}}`;
            continue;
          }}
          coalesced.push(w);
        }}
        const mapped = coalesced.map((w, idx) => {{
          const inputs = [];
          if (w.trigger_node_id) {{
            inputs.push({{
              name: nodeDisplayName(w.trigger_node_id),
              nodeId: w.trigger_node_id,
              step: w.start_step,
              isClick: !w.trigger_value,
              details: w.trigger || w.human_action,
              value: w.trigger_value
            }});
          }}
          const calcs = filterItems(w.inferred_executions || [], id => id.startsWith('calc:') || nodeIndex.get(id)?.type === 'calc')
            .map(id => ({{ name: nodeDisplayName(id), nodeId: id, step: w.start_step }}));
          const outputs = filterItems(w.inferred_executions || [], id => id.startsWith('output:') || nodeIndex.get(id)?.type === 'output')
            .map(id => ({{ name: nodeDisplayName(id), nodeId: id, step: w.start_step }}));

          let shortLabel = w.is_mark ? (w.short_label || '') : nodeDisplayName(w.short_label || '');
          if (!shortLabel) {{
            if (w.is_init) {{
              shortLabel = 'Init';
            }} else if (w.trigger_node_id) {{
              shortLabel = nodeDisplayName(w.trigger_node_id);
            }} else if (w.trigger_label) {{
              shortLabel = nodeDisplayName(w.trigger_label);
            }} else {{
              shortLabel = 'Action';
            }}
          }}

          return {{
            id: w.action_id || `burst-${{idx}}`,
            index: w.index !== undefined ? w.index : idx,
            isInit: Boolean(w.is_init),
            isMark: Boolean(w.is_mark),
            startTime: w.start_time || 0.0,
            endTime: w.end_time || 0.0,
            time: w.start_time || 0.0,
            startStep: w.start_step || 0,
            endStep: w.end_step || 0,
            triggerLabel: w.is_mark ? (w.trigger_label || w.trigger || 'Action') : nodeDisplayName(w.trigger_label || w.trigger || 'Action'),
            shortLabel: shortLabel,
            humanAction: w.is_mark ? (w.human_action || w.trigger || 'Action') : nodeDisplayName(w.human_action || w.trigger || 'Action'),
            triggerNodeId: w.trigger_node_id || '',
            triggerValue: w.trigger_value,
            inputs: inputs,
            calcs: calcs,
            outputs: outputs,
            invalidatedNodes: new Set(w.invalidated_nodes || []),
            inferredExecutions: new Set(w.inferred_executions || []),
            observedExecutions: new Set(w.observed_executions || []),
            observedOutputs: new Set(w.observed_outputs || []),
            totalEvents: (w.end_step - w.start_step + 1),
            userChanges: inputs.length,
            details: w.trigger || 'Action'
          }};
        }});
        allBursts = mapped;
        actionWaves = filterItems(mapped, w => !w.isInit);
        return;
      }}
      actionWaves = [];
      allBursts = [];
      const events = reactlogData.events || reactlogData.log || [];
      const lastKnownValues = new Map();
      (reactlogData.nodes || []).forEach(n => {{
        if (n.value !== undefined && n.value !== null) {{
          lastKnownValues.set(nodeDisplayName(n), n.value);
        }}
      }});
      let initWave = null;
      let curWave = null;

      events.forEach((ev, idx) => {{
        const evAction = ev.action || ev.event || '';
        const isInit = ev.phase === 'init' || ['define', 'analysisInit', 'createContext', 'sessionInit'].includes(evAction);
        const t = ev.time_sec !== undefined ? ev.time_sec : (ev.time !== undefined ? ev.time : 0);

        if (isInit) {{
          if (ev.value !== undefined && ev.value !== null) {{
            const raw = ev.node_id || ev.id || ev.node_label || ev.label || '';
            const name = nodeDisplayName(raw);
            if (name) lastKnownValues.set(name, ev.value);
          }}
          if (!initWave) {{
            initWave = {{
              id: 'burst-init',
              index: 0,
              isInit: true,
              startTime: t,
              endTime: t,
              time: t,
              startStep: idx,
              endStep: idx,
              triggerLabel: 'Init',
              shortLabel: 'Init',
              humanAction: 'Init',
              inputs: [],
              calcs: [],
              outputs: [],
              totalEvents: 0,
              userChanges: 0,
              details: 'Application Initialization',
            }};
          }}
          initWave.endStep = idx;
          initWave.endTime = t;
          initWave.totalEvents++;
        }} else {{
          const isUserAction = evAction === 'inputChange' || evAction === 'userClick' || evAction === 'userAction';
          const isNewTrigger = isUserAction && curWave && curWave.inputs.length > 0;
          if (!curWave || (t - curWave.startTime) > 0.25 || isNewTrigger) {{
            curWave = {{
              id: `burst-${{actionWaves.length + 1}}`,
              index: actionWaves.length + 1,
              isInit: false,
              startTime: t,
              endTime: t,
              time: t,
              startStep: idx,
              endStep: idx,
              triggerLabel: '',
              shortLabel: '',
              humanAction: '',
              triggerNodeId: '',
              triggerValue: ev.value,
              inputs: [],
              calcs: [],
              outputs: [],
              totalEvents: 0,
              userChanges: 0,
              details: ev.details || evAction,
            }};
            actionWaves.push(curWave);
          }}
          curWave.endStep = idx;
          curWave.endTime = t;
          curWave.totalEvents++;

          const nId = ev.node_id || ev.id || '';
          if (evAction === 'inputChange' || evAction === 'userClick' || evAction === 'userAction' || nId.startsWith('input:') || nodeIndex.get(nId)?.type === 'input') {{
            const raw = nId || ev.details || '';
            if (!raw.includes('clientdata') && !raw.includes('pixelratio') && !raw.includes('_hidden')) {{
              const name = nodeDisplayName(raw) || 'input';
              const prevVal = lastKnownValues.get(name);
              const newVal = ev.value !== undefined ? ev.value : null;
              if (newVal !== null) lastKnownValues.set(name, newVal);

              if (!curWave.triggerLabel) {{
                curWave.shortLabel = name;
                if (evAction === 'userClick') {{
                  curWave.humanAction = `Click: ${{name}}`;
                  curWave.triggerLabel = name;
                  curWave.shortLabel = `Click: ${{name}}`;
                }} else if (prevVal !== undefined && newVal !== null && prevVal !== newVal) {{
                  curWave.humanAction = `${{name}}: ${{formatHumanValue(prevVal)}} → ${{formatHumanValue(newVal)}}`;
                  curWave.triggerLabel = name;
                }} else if (newVal !== null) {{
                  curWave.humanAction = `${{name}}: ${{formatHumanValue(newVal)}}`;
                  curWave.triggerLabel = name;
                }} else {{
                  curWave.humanAction = `${{name}} changed`;
                  curWave.triggerLabel = name;
                }}
                curWave.triggerNodeId = nId;
                curWave.triggerValue = ev.value;
              }}
              if (!curWave.inputs.some(item => item.name === name)) {{
                curWave.inputs.push({{ name, nodeId: nId, step: idx, isClick: evAction === 'userClick' || evAction === 'userAction', details: ev.details, value: ev.value }});
                curWave.userChanges++;
              }}
            }}
          }} else if (nId && (nId.startsWith('calc:') || nId.startsWith('effect:') || (ev.type === 'calc') || ['calc', 'effect'].includes(nodeIndex.get(nId)?.type) || (ev.node_type === 'conductor'))) {{
            const name = nodeDisplayName(nId);
            if (name && !curWave.calcs.some(item => item.name === name)) {{
              curWave.calcs.push({{ name, nodeId: nId, step: idx, details: ev.details }});
            }}
          }} else if (nId && (nId.startsWith('output:') || (ev.type === 'output') || nodeIndex.get(nId)?.type === 'output' || (ev.node_type === 'observer'))) {{
            const name = nodeDisplayName(nId);
            if (name && !curWave.outputs.some(item => item.name === name)) {{
              curWave.outputs.push({{ name, nodeId: nId, step: idx, details: ev.details }});
            }}
          }}
        }}
      }});

      actionWaves.forEach(w => {{
        if (!w.triggerLabel) {{
          if (w.inputs.length > 0) {{
            w.humanAction = `${{w.inputs[0].name}} changed`;
            w.triggerLabel = w.inputs[0].name;
            w.shortLabel = w.inputs[0].name;
          }} else if (w.calcs.length > 0) {{
            w.humanAction = `Recalc: ${{w.calcs[0].name}}`;
            w.triggerLabel = w.calcs[0].name;
            w.shortLabel = w.calcs[0].name;
          }} else if (w.outputs.length > 0) {{
            w.humanAction = `Render: ${{w.outputs[0].name}}`;
            w.triggerLabel = w.outputs[0].name;
            w.shortLabel = w.outputs[0].name;
          }} else {{
            w.humanAction = 'Action';
            w.triggerLabel = 'Action';
            w.shortLabel = 'Action';
          }}
        }}
      }});

      allBursts = (initWave && initWave.totalEvents > 0 ? [initWave] : []).concat(actionWaves);
      if (allBursts.length === 0) {{
        allBursts = [{{
          id: 'burst-init',
          index: 0,
          isInit: true,
          isMark: false,
          startTime: 0,
          endTime: 0,
          time: 0,
          startStep: 0,
          endStep: Math.max(0, (reactlogData.events || []).length - 1),
          triggerLabel: 'Init',
          shortLabel: 'Init',
          humanAction: 'Init',
          triggerNodeId: '',
          triggerValue: null,
          inputs: [],
          calcs: [],
          outputs: [],
          invalidatedNodes: new Set(),
          inferredExecutions: new Set(),
          observedExecutions: new Set(),
          observedOutputs: new Set(),
          totalEvents: Math.max(1, (reactlogData.events || []).length),
          userChanges: 0,
          details: 'Initial State'
        }}];
      }}
    }}

    function getCurrentStepTime() {{
      const events = reactlogData.events || reactlogData.log || [];
      const ev = events[currentStep];
      return ev ? (ev.effective_time !== undefined ? ev.effective_time : ((ev.time_sec !== undefined ? ev.time_sec : ev.time) || 0)) : 0;
    }}

    function initTraceTimeline() {{
      const events = reactlogData.events || reactlogData.log || [];
      const video = document.getElementById('session-video');
      maxSessionDuration = events.reduce((max, ev) => Math.max(max, ev.effective_time ?? ev.time_sec ?? ev.time ?? 0), Number.isFinite(video?.duration) ? video.duration : 1);
      document.getElementById('trace-total-time').textContent = formatTime(maxSessionDuration);
      const markers = document.getElementById('trace-markers');
      markers.replaceChildren();
      timelineStops = [];
      let depth = 0;
      events.forEach((ev, step) => {{
        const action = ev.action || ev.event || '';
        if (['enter', 'execStart'].includes(action)) depth++;
        let outputComplete = action === 'outputUpdated' || ev.event === 'outputUpdated';
        if (['exit', 'execEnd'].includes(action)) {{
          depth = Math.max(0, depth - 1);
          outputComplete = depth === 0;
        }}
        const kind = isErrorEvent(ev) ? 'error' : ['mark', 'userMark'].includes(action) ? 'mark' : isIdleEvent(ev) ? 'idle' : outputComplete ? 'output' : null;
        if (!kind) return;
        timelineStops.push({{ step, kind }});
        const label = kind === 'error' ? 'Error' : kind === 'mark' ? 'User mark' : kind === 'idle' ? 'Idle' : 'Output calculation';
        const time = formatTime(ev.time_sec ?? ev.time ?? 0);
        const description = kind === 'error' ? formatEventDetails(ev) : kind === 'mark'
          ? (ev.node_label || ev.label || ev.details || '')
          : nodeDisplayName(ev.node_id || ev.id || ev.node_label || ev.label || '');
        const text = `${{label}} · Step ${{step}} · ${{time}}${{description ? ' · ' + description : ''}}`;
        const marker = document.createElement('button');
        marker.type = 'button';
        marker.tabIndex = -1;
        marker.className = `timeline-marker is-${{kind}}`;
        marker.dataset.step = step;
        marker.setAttribute('aria-label', text);
        marker.title = text;
        const width = Math.min(100, 75 / Math.max(1, events.length - 1));
        marker.style.width = `${{width}}%`;
        marker.style.left = `${{Math.max(0, 100 * step / Math.max(1, events.length - 1) - width)}}%`;
        const tooltip = document.getElementById('timeline-tooltip');
        marker.onmouseenter = marker.onfocus = () => {{ tooltip.textContent = text; tooltip.hidden = false; }};
        marker.onmouseleave = marker.onblur = () => {{ tooltip.hidden = true; }};
        marker.onclick = () => {{ seekTo(step); }};
        markers.appendChild(marker);
      }});
      const track = document.getElementById('trace-track-wrap');
      const seekPointer = event => {{
        const box = track.getBoundingClientRect();
        const ratio = Math.max(0, Math.min(1, (event.clientX - box.left) / box.width));
        seekTo(Math.round(ratio * Math.max(0, events.length - 1)));
      }};
      track.onpointerdown = event => {{
        if (event.button !== 0) return;
        event.preventDefault();
        track.setPointerCapture(event.pointerId);
        document.getElementById('scrubber-range').focus({{ preventScroll: true }});
        const marker = event.target.closest('.timeline-marker');
        if (marker) seekTo(Number(marker.dataset.step)); else seekPointer(event);
      }};
      track.onpointermove = event => {{
        if (track.hasPointerCapture(event.pointerId) && event.buttons === 1) {{
          document.getElementById('timeline-tooltip').hidden = true;
          seekPointer(event);
        }}
      }};
      track.onpointerup = event => {{
        if (track.hasPointerCapture(event.pointerId)) track.releasePointerCapture(event.pointerId);
      }};
      updateTraceTimelineScrubber(getCurrentStepTime());
    }}

    function updateTraceTimelineScrubber(curSec) {{
      document.getElementById('trace-current-time').textContent = formatTime(curSec);
      const events = reactlogData.events || reactlogData.log || [];
      const curWave = allBursts.slice().reverse().find(w => currentStep >= w.startStep) || allBursts[0];
      activeBurstIndex = curWave ? allBursts.indexOf(curWave) : 0;
      const activeLabel = document.getElementById('active-flush-label');
      activeLabel.textContent = curWave
        ? (curWave.isInit ? 'Initial render' : (curWave.humanAction || curWave.triggerLabel || 'Initial render'))
        : 'No recorded activity';
      activeLabel.title = activeLabel.textContent;
      const ev = events[currentStep];
      const status = document.getElementById('trace-status-line');
      status.textContent = ev ? (isIdleEvent(ev) ? 'Idle' : ['mark', 'userMark'].includes(ev.action || ev.event) ? `User mark${{ev.details ? ' · ' + nodeDisplayName(String(ev.details)) : ''}}` : (formatEventDetails(ev) || ev.action || ev.event || '')) : 'No events';
      status.title = status.textContent;
      const range = document.getElementById('scrubber-range');
      const percent = 100 * currentStep / Math.max(1, events.length - 1);
      range.style.setProperty('--progress', `${{percent}}%`);
      document.getElementById('timeline-playhead').style.left = `calc(${{percent}}% - ${{3 * percent / 100}}px)`;
      range.setAttribute('aria-valuetext', `Step ${{currentStep}} of ${{Math.max(0, events.length - 1)}}. ${{activeLabel.textContent}}. ${{status.textContent}}`);
    }}

    function nextAction() {{
      const events = reactlogData.events || reactlogData.log || [];
      for (let i = currentStep + 1; i < events.length; i++) {{
        const ev = events[i];
        const act = ev.action || ev.event || '';
        if (ev.phase === 'interaction' && (act === 'inputChange' || act === 'userClick' || act === 'userAction' || act === 'outputUpdated' || act === 'valueChange')) {{
          seekTo(i);
          return;
        }}
      }}
    }}

    function prevAction() {{
      const events = reactlogData.events || reactlogData.log || [];
      for (let i = currentStep - 1; i >= 0; i--) {{
        const ev = events[i];
        const act = ev.action || ev.event || '';
        if (ev.phase === 'interaction' && (act === 'inputChange' || act === 'userClick' || act === 'userAction' || act === 'outputUpdated' || act === 'valueChange')) {{
          seekTo(i);
          return;
        }}
      }}
      seekTo(0);
    }}

    function getCurrentFlushIndex() {{
      if (!allBursts || allBursts.length === 0) return 0;
      for (let i = allBursts.length - 1; i >= 0; i--) {{
        if (currentStep >= allBursts[i].startStep) return i;
      }}
      return 0;
    }}

    function getActiveFlushNodeIds(wave) {{
      if (!wave) return new Set();
      const set = new Set();
      if (wave.isInit) {{
        (reactlogData.nodes || []).forEach(n => {{
          set.add(n.id);
          set.add(cleanName(n.id));
        }});
        return set;
      }}
      if (wave.triggerNodeId) {{
        set.add(wave.triggerNodeId);
        set.add(cleanName(wave.triggerNodeId));
        (adjDownstream.get(wave.triggerNodeId) || []).forEach(dn => {{
          set.add(dn);
          set.add(cleanName(dn));
        }});
      }}
      (wave.inputs || []).forEach(i => {{
        if (i.nodeId) {{
          set.add(i.nodeId);
          set.add(cleanName(i.nodeId));
          (adjDownstream.get(i.nodeId) || []).forEach(dn => {{
            set.add(dn);
            set.add(cleanName(dn));
          }});
        }}
        if (i.name) set.add(i.name);
      }});
      (wave.calcs || []).forEach(c => {{
        if (c.nodeId) {{
          set.add(c.nodeId);
          set.add(cleanName(c.nodeId));
          (adjDownstream.get(c.nodeId) || []).forEach(dn => {{
            set.add(dn);
            set.add(cleanName(dn));
          }});
        }}
        if (c.name) set.add(c.name);
      }});
      (wave.outputs || []).forEach(o => {{
        if (o.nodeId) {{ set.add(o.nodeId); set.add(cleanName(o.nodeId)); }}
        if (o.name) set.add(o.name);
      }});
      if (wave.invalidatedNodes) {{
        wave.invalidatedNodes.forEach(id => {{
          set.add(id);
          set.add(cleanName(id));
        }});
      }}
      if (wave.inferredExecutions) {{
        wave.inferredExecutions.forEach(id => {{
          set.add(id);
          set.add(cleanName(id));
        }});
      }}
      if (wave.observedExecutions) {{
        wave.observedExecutions.forEach(id => {{
          set.add(id);
          set.add(cleanName(id));
        }});
      }}
      const directIds = new Set(set);
      (reactlogData.edges || []).forEach(e => {{
        if (directIds.has(e.from) || (e.from && directIds.has(cleanName(e.from)))) {{
          set.add(e.to);
          set.add(cleanName(e.to));
        }}
        if (directIds.has(e.to) || (e.to && directIds.has(cleanName(e.to)))) {{
          set.add(e.from);
          set.add(cleanName(e.from));
        }}
      }});
      return set;
    }}

    function selectFlush(flushIndex) {{
      if (!allBursts || allBursts.length === 0) return;
      const idx = Math.max(0, Math.min(flushIndex, allBursts.length - 1));
      activeBurstIndex = idx;
      const targetBurst = allBursts[idx];
      if (!targetBurst) return;
      const targetStep = targetBurst.inputs && targetBurst.inputs[0] ? targetBurst.inputs[0].step : targetBurst.startStep;
      seekTo(targetStep);
      if (currentViewMode === 'flush') {{
        renderGraph();
        fitGraph();
      }}
    }}

    function isIdleEvent(ev) {{
      return ev.event !== 'orderingStart' && ['idle', 'queueEmpty'].includes(ev.action || ev.event);
    }}

    function seekTimelineStop(kind, direction) {{
      const stops = direction < 0 ? timelineStops.slice().reverse() : timelineStops;
      const target = stops.find(stop => stop.kind === kind && (direction < 0 ? stop.step < currentStep : stop.step > currentStep));
      if (target) seekTo(target.step);
    }}

    function prevFlush() {{ seekTimelineStop('idle', -1); }}
    function nextFlush() {{ seekTimelineStop('idle', 1); }}

    function setViewMode(mode) {{
      currentViewMode = mode;
      const activitySelect = document.getElementById('activity-select');
      if (activitySelect) activitySelect.value = mode;
      refreshExploration();
      fitGraph();
    }}

    function filterFlushStage(stage) {{
      if (selectedStageFilter === stage) {{
        selectedStageFilter = null;
      }} else {{
        selectedStageFilter = stage;
      }}
      document.querySelectorAll('.pipeline-step-item').forEach(el => {{
        el.classList.toggle('is-selected-stage', el.id === `pipe-${{selectedStageFilter}}`);
      }});
      renderGraph();
      fitGraph();
    }}

    function toggleCollapseAllModules() {{
      toggleSettingsMenu(false);
      const allMods = new Set(filterItems((reactlogData.nodes || []).map(n => n.module), Boolean));
      if (collapsedModules.size >= allMods.size) {{
        collapsedModules.clear();
      }} else {{
        allMods.forEach(m => collapsedModules.add(m));
      }}
      renderGraph();
      fitGraph();
    }}

    function nodeRoleKey(n) {{
      if (n.role === 'source' || n.type === 'input') return 'source';
      if (n.role === 'conductor' || n.type === 'calc') return 'conductor';
      const raw = `${{n.type || ''}} ${{n.label || ''}} ${{n.id || ''}}`.toLowerCase();
      if (n.type === 'effect' || raw.includes('reactive.effect') || String(n.id || '').startsWith('effect:')) return 'effect';
      return 'output';
    }}

    function isClientDataNode(n) {{
      const raw = `${{n.id || ''}} ${{n.label || ''}} ${{n.name || ''}}`.toLowerCase();
      return raw.includes('.clientdata_') || raw.includes('clientdata') || raw.includes('pixelratio');
    }}

    function syncRoleFilterButtons() {{
      document.querySelectorAll('.legend-role-btn').forEach(btn => {{
        const role = btn.getAttribute('data-role');
        const active = activeRoles.has(role);
        btn.classList.toggle('is-active', active);
        btn.setAttribute('aria-pressed', String(active));
      }});
    }}

    function toggleRoleFilter(role) {{
      if (activeRoles.has(role)) {{
        activeRoles.delete(role);
      }} else {{
        activeRoles.add(role);
      }}
      if (activeRoles.has('effect') || activeRoles.has('output')) activeRoles.add('observer');
      else activeRoles.delete('observer');
      syncRoleFilterButtons();
      refreshExploration();
      fitGraph();
    }}

    function findChangedNodes() {{
      const events = reactlogData.events || reactlogData.log || [];
      const boundary = events.findIndex(ev => (ev.action || ev.event) === 'queueEmpty');
      if (boundary < 0) return null;
      const values = new Map(), changed = new Set();
      events.forEach((ev, index) => {{
        const action = ev.action || ev.event;
        const id = ev.node_id || ev.reactId || ev.id;
        if (!id || ev.provenance === 'inferred') return;
        if (ev.provenance === 'observed' && (action === 'enter' || ev.event === 'outputUpdated')) {{
          changed.add(id);
          return;
        }}
        if (!['valueChange', 'inputChange'].includes(action)) return;
        const value = JSON.stringify(ev.value);
        if (values.has(id) ? values.get(id) !== value : index > boundary) changed.add(id);
        values.set(id, value);
      }});
      return changed;
    }}

    function toggleChangedNodes() {{
      changedNodesOnly = !changedNodesOnly;
      refreshExploration();
      fitGraph();
    }}

    function setClientDataVisibility(mode) {{
      hideClientData = mode === 'hide';
      const clientSelect = document.getElementById('clientdata-select');
      if (clientSelect) clientSelect.value = hideClientData ? 'hide' : 'show';
      refreshExploration();
      fitGraph();
    }}

    function toggleClientData() {{
      setClientDataVisibility(hideClientData ? 'show' : 'hide');
    }}

    function updateFlushUI() {{
      if (!allBursts || allBursts.length === 0) return;
      const curIdx = getCurrentFlushIndex();
      const curWave = allBursts[curIdx] || allBursts[0];
      if (!curWave) return;

      const invCount = curWave.invalidatedNodes ? curWave.invalidatedNodes.size : 0;
      const calcCount = curWave.calcs ? curWave.calcs.length : 0;
      const outCount = curWave.outputs ? curWave.outputs.length : 0;

      const cardTitle = document.getElementById('flush-card-title');
      if (cardTitle) {{
        cardTitle.textContent = curWave.isInit ? 'Activity 1: Initial render' : `Activity ${{curIdx + 1}}: ${{curWave.shortLabel || 'Action'}}`;
      }}
      const cardTime = document.getElementById('flush-card-time');
      if (cardTime) {{
        const dur = Math.max(0, (curWave.endTime - curWave.startTime) * 1000);
        cardTime.textContent = `${{formatTime(curWave.startTime)}} (${{Math.round(dur)}}ms)`;
      }}
      const cardTrigger = document.getElementById('flush-card-trigger');
      if (cardTrigger) {{
        cardTrigger.textContent = curWave.humanAction || curWave.triggerLabel || (curWave.isInit ? 'Application Initialization' : 'Action');
      }}
      const cardInv = document.getElementById('flush-card-invalidated');
      if (cardInv) cardInv.textContent = `${{invCount}} nodes marked dirty`;
      const cardCalcs = document.getElementById('flush-card-calcs');
      if (cardCalcs) cardCalcs.textContent = `${{calcCount}} calcs re-evaluated`;
      const cardOuts = document.getElementById('flush-card-outputs');
      if (cardOuts) cardOuts.textContent = `Outputs that ran: ${{outCount}}`;

      const execOrder = document.getElementById('flush-execution-order');
      if (execOrder) {{
        execOrder.innerHTML = '';
        const sequence = [];
        if (curWave.inputs) curWave.inputs.forEach(i => sequence.push({{ role: 'source', nodeId: i.nodeId, name: i.name || i.nodeId, label: 'Trigger Input' }}));
        if (curWave.calcs) curWave.calcs.forEach(c => sequence.push({{ role: 'conductor', nodeId: c.nodeId, name: c.name || c.nodeId, label: 'Calc' }}));
        if (curWave.outputs) curWave.outputs.forEach(o => sequence.push({{ role: 'observer', nodeId: o.nodeId, name: o.name || o.nodeId, label: 'Output' }}));
        sequence.slice(0, 12).forEach((item, sIdx) => {{
          const row = document.createElement('div');
          row.className = 'flush-order-item';
          const roleColor = item.role === 'source' ? 'var(--source)' : (item.role === 'conductor' ? 'var(--calc)' : 'var(--output)');
          row.innerHTML = `<span class="flush-order-idx">${{sIdx + 1}}.</span><span class="flush-order-role" style="background:${{roleColor}}"></span><span style="font-weight:700;">${{nodeLabelHTML(nodeIndex.get(item.nodeId) || {{ label: item.name }})}}</span><span style="color:var(--text-muted);font-size:0.6rem;margin-left:auto;">${{item.label}}</span>`;
          row.onclick = () => {{
            const matching = nodeIndex.get(item.nodeId) || (reactlogData.nodes || []).find(n => nodeDisplayName(n) === item.name);
            if (matching) selectNode(matching.id);
          }};
          execOrder.appendChild(row);
        }});
        if (sequence.length > 12) {{
          const more = document.createElement('div');
          more.style.cssText = 'color:var(--text-muted);font-size:0.62rem;font-style:italic;padding-left:18px;';
          more.textContent = `+ ${{sequence.length - 12}} more steps in cascade`;
          execOrder.appendChild(more);
        }}
      }}

    }}

    function getScopedNodes() {{
      const lineage = getActiveLineageSet();
      const wave = allBursts[getCurrentFlushIndex()] || allBursts[0];
      const active = currentViewMode === 'flush' && !focusedNodeId && wave ? getActiveFlushNodeIds(wave) : null;
      return filterItems(reactlogData.nodes || [], n => {{
        const roleKey = nodeRoleKey(n);
        if (lineage ? !lineage.has(n.id) : ((!activeRoles.has(roleKey) || !activeRoles.has(n.role)) || (searchQuery && !Number.isFinite(nodeSearchScore(n, searchQuery))))) return false;
        if (hideClientData && isClientDataNode(n)) return false;
        if (changedNodesOnly && changedNodeIds && !changedNodeIds.has(n.id)) return false;
        if (active && active.size && !active.has(n.id) && !active.has(cleanName(n.id))) return false;
        if (selectedStageFilter && wave) {{
          const members = selectedStageFilter === 'invalidated' ? wave.invalidatedNodes || new Set()
            : new Set((selectedStageFilter === 'calcs' ? wave.calcs || [] : wave.outputs || []).map(x => x.nodeId || x.name));
          if (!members.has(n.id) && !members.has(cleanName(n.id))) return false;
        }}
        return true;
      }});
    }}

    function refreshExploration() {{
      renderGraph();
      renderEventList();
    }}

    function updateFilterState(nodes) {{
      document.getElementById('filter-node-count').textContent = `${{nodes.length}} of ${{(reactlogData.nodes || []).length}} nodes`;
      syncSearchClearButton();
      const clientSelect = document.getElementById('clientdata-select');
      if (clientSelect) clientSelect.value = hideClientData ? 'hide' : 'show';
      const activitySelect = document.getElementById('activity-select');
      if (activitySelect) activitySelect.value = currentViewMode;
      syncRoleFilterButtons();
      const chips = document.getElementById('active-filters');
      chips.replaceChildren();
      const add = (kind, label, clear) => {{
        const button = document.createElement('button');
        button.className = 'btn mini'; button.type = 'button';
        button.textContent = label + ' ×'; button.setAttribute('aria-label', `Remove ${{kind}} filter`);
        button.onclick = () => {{ clear(); refreshExploration(); }};
        chips.appendChild(button);
      }};
      if (selectedStageFilter) add('stage', selectedStageFilter, () => {{ selectedStageFilter = null; }});
      if (ALL_ROLES.some(r => !activeRoles.has(r))) add('role', 'Role filter', () => {{
        activeRoles = new Set(['source', 'conductor', 'observer', 'effect', 'output']);
      }});

      document.querySelectorAll('.pipeline-step-item').forEach(el => el.classList.toggle('is-selected-stage', el.id === `pipe-${{selectedStageFilter}}`));
      renderEventList();
    }}

    function init() {{
      document.addEventListener('click', (e) => {{
        if (!e.target.closest('.search-wrap')) closeSearchChoices();
        if (!e.target.closest('.settings-wrap')) toggleSettingsMenu(false);
        const nodeBtn = e.target.closest('[data-node-id]');
        if (nodeBtn && nodeBtn.dataset.nodeId) {{
          selectNode(nodeBtn.dataset.nodeId);
          return;
        }}
        const jumpBtn = e.target.closest('[data-seek-step]');
        if (jumpBtn && jumpBtn.dataset.seekStep) {{
          seekTo(parseInt(jumpBtn.dataset.seekStep, 10));
          return;
        }}
      }});
      initTheme();
      prepareEventTimings();
      buildGraphIndices();
      buildActionWaves();
      changedNodeIds = findChangedNodes();

      const events = reactlogData.events || reactlogData.log || [];
      const nodes = reactlogData.nodes || [];
      const edges = reactlogData.edges || [];

      const scrubber = document.getElementById('scrubber-range');
      scrubber.max = Math.max(0, events.length - 1);
      scrubber.value = 0;

      showSourceFile(reactlogData.entry_file || Object.keys(reactlogData.sources || {{}})[0]);
      renderEventList();
      renderGraph();
      initTraceTimeline();
      seekTo(0);
      updateFlushUI();
      setupPanZoom();
      fitGraph();
      setupVideoSync();
      toggleInspector(false);
      setViewMode('full');
    }}

    const reactiveStateColors = {{ ready: 'var(--state-ready)', calculating: 'var(--state-calculating)', invalidating: 'var(--state-invalidating)', invalidated: 'var(--state-invalidated)', frozen: 'var(--state-frozen)', error: 'var(--state-error)' }};

    function isErrorEvent(ev) {{
      return ev && (typeof ev.error === 'string' || (ev.action || ev.event) === 'outputError');
    }}

    function reactiveEventState(ev) {{
      const action = ev.action || ev.event;
      if (isErrorEvent(ev)) return 'error';
      if (['enter', 'execStart', 'wouldEvaluate', 'recalculate', 'render', 'output'].includes(action)) return 'calculating';
      if (action === 'invalidateStart') return 'invalidating';
      if (['invalidateEnd', 'invalidate', 'propagate', 'define'].includes(action)) return 'invalidated';
      if (['exit', 'execEnd', 'ordered', 'outputUpdated', 'valueChange', 'inputChange', 'assumeValue'].includes(action)) return 'ready';
      return null;
    }}

    function graphStateAtStep() {{
      const states = new Map(), frozen = new Set(), inactiveEdges = new Set();
      const events = reactlogData.events || reactlogData.log || [];
      events.forEach(ev => {{
        if ((ev.action || ev.event) === 'dependsOn') inactiveEdges.add(JSON.stringify([ev.edge_from || ev.dependsOn || ev.depOnReactId, ev.edge_to || ev.node_id || ev.reactId || ev.id]));
      }});
      for (let i = 0; i <= currentStep && i < events.length; i++) {{
        const ev = events[i], action = ev.action || ev.event;
        const id = ev.node_id || ev.reactId || ev.id;
        const state = reactiveEventState(ev);
        if (id && state) states.set(id, state);
        if (action === 'freeze') frozen.add(id);
        if (action === 'thaw') frozen.delete(id);
        const from = ev.edge_from || ev.dependsOn || ev.depOnReactId;
        const to = ev.edge_to || id;
        const key = JSON.stringify([from, to]);
        if (action === 'dependsOnRemove') inactiveEdges.add(key);
        if (action === 'dependsOn') inactiveEdges.delete(key);
      }}
      frozen.forEach(id => states.set(id, 'frozen'));
      return {{ states, inactiveEdges }};
    }}

    function nodeKind(n) {{
      if (n.type === 'module') return {{ label: 'Module', color: 'var(--effect)', lightColor: '#994a78', darkColor: '#e3a4c8', shape: 'M3.2 0.8H11.2V8.8H9.6V2.4H3.2V0.8ZM0.8 3.2H8.8V11.2H0.8V3.2ZM2.6 5V9.4H7V5H2.6Z', verb: 'run' }};
      if (n.render_type === 'plot' || n.render_type === 'image') return {{ label: 'Plot', color: 'var(--output)', lightColor: '#006e59', darkColor: '#5fc7a7', shape: 'M0.8 1H11.2V11H0.8L3.8 6ZM5.2 4.4H8.4V7.6H5.2Z', verb: 'render' }};
      if (n.role === 'source' || n.type === 'input') return {{ label: 'Input', color: 'var(--source)', lightColor: '#005a9c', darkColor: '#56b4e9', shape: 'M0.8 1H8.2L11.2 6L8.2 11H0.8Z', verb: 'change' }};
      if (n.role === 'conductor' || n.type === 'calc') return {{ label: 'Reactive Calc', color: 'var(--calc)', lightColor: '#9c4f00', darkColor: '#e9b44c', shape: 'M0.8 1H8.2L11.2 6L8.2 11H0.8L3.8 6Z', verb: 'run' }};
      if (n.type === 'effect') return {{ label: 'Effect', color: 'var(--effect)', lightColor: '#994a78', darkColor: '#e3a4c8', shape: 'M6 1.2L11.2 10.8H0.8Z', verb: 'trigger' }};
      return {{ label: 'Output', color: 'var(--output)', lightColor: '#006e59', darkColor: '#5fc7a7', shape: 'M0.8 1H11.2V11H0.8L3.8 6Z', verb: 'render' }};
    }}

    function toggleInspector(forceState) {{
      const sidebar = document.getElementById('sidebar');
      const shouldOpen = forceState !== undefined ? Boolean(forceState) : sidebar.hidden;
      sidebar.hidden = !shouldOpen;
      const mainView = document.getElementById('main-view');
      if (mainView) mainView.classList.toggle('is-inspector-open', shouldOpen);
      const inspectBtn = document.getElementById('btn-inspect-selection');
      if (inspectBtn) inspectBtn.hidden = !focusedNodeId || shouldOpen;
      for (const id of ['btn-toggle-inspector', 'btn-toggle-inspector-bottom']) {{
        const button = document.getElementById(id);
        button.classList.toggle('is-active', shouldOpen);
        button.setAttribute('aria-expanded', String(shouldOpen));
      }}
    }}

    function closeSidebarAndClearSelection() {{
      clearNodeSelection();
      toggleInspector(false);
    }}

    function toggleSettingsMenu(forceState) {{
      const menu = document.getElementById('settings-menu');
      const btn = document.getElementById('btn-settings');
      if (!menu || !btn) return;
      const shouldOpen = forceState !== undefined ? Boolean(forceState) : menu.hidden;
      menu.hidden = !shouldOpen;
      btn.setAttribute('aria-expanded', String(shouldOpen));
      btn.classList.toggle('is-active', shouldOpen);
    }}

    function showSidebarPanel(panelName) {{
      toggleInspector(true);
      for (const name of ['timeline', 'source']) {{
        document.getElementById(`${{name}}-panel`).hidden = name !== panelName;
      }}
      document.getElementById('source-tab').setAttribute('aria-selected', String(panelName === 'source'));
      document.getElementById('detail-panel-title').textContent = panelName === 'source' ? 'App code' : 'Node details';
      if (panelName === 'source') updateSourceHighlight();
    }}

    function toggleRecording(forceState) {{
      const panel = document.getElementById('video-panel');
      if (!panel) return;
      panel.hidden = forceState !== undefined ? !forceState : !panel.hidden;
      document.getElementById('video-tab').setAttribute('aria-expanded', String(!panel.hidden));
    }}

    function escapeHTML(str) {{
      if (str === null || str === undefined) return '';
      return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
    }}

    function formatTime(sec) {{
      if (sec === undefined || sec === null) return '';
      const s = Number(sec);
      const mins = Math.floor(s / 60);
      const rem = (s % 60).toFixed(1);
      return `${{mins > 0 ? mins + 'm ' : ''}}${{rem}}s`;
    }}

    function nodeDisplayName(value) {{
      if (typeof value === 'string') {{
        const map = typeof nodeIndex !== 'undefined' ? nodeIndex : null;
        const node = map ? map.get(value) : null;
        if (node) return nodeDisplayName(node);
        const action = value.match(/^(Recalc: |Render: |Click: )(.+)$/);
        if (action && map && map.has(action[2])) return action[1] + nodeDisplayName(map.get(action[2]));
        if (map && value.includes("'")) {{
          return value.replace(/'([^']+)'/g, (match, token) =>
            map.has(token) ? `'${{nodeDisplayName(map.get(token))}}'` : match
          );
        }}
        return value;
      }}
      return String(value?.label || value?.name || value?.id || '');
    }}

    function formatEventDetails(ev) {{
      if (!ev) return '';
      const act = ev.action || ev.event || '';
      if (isErrorEvent(ev)) {{
        const node = nodeDisplayName(ev.node_id || ev.reactId || ev.id || ev.node_label || ev.label || '');
        return `${{node ? node + ' failed' : 'Execution failed'}}${{ev.error ? ': ' + ev.error : ''}}`;
      }}
      if (ev.details) return nodeDisplayName(String(ev.details));
      const nid = ev.node_id || ev.reactId || ev.id || '';
      const lbl = nodeDisplayName(nid || ev.node_label || ev.label || '');
      const fromId = ev.edge_from || ev.depOnReactId || ev.dependsOn || '';
      const toId = ev.edge_to || nid || '';
      if (act === 'dependsOn' && (fromId || toId)) {{
        return `Dependency: '${{nodeDisplayName(fromId)}}' used by '${{nodeDisplayName(toId || lbl)}}'`;
      }}
      if (act === 'dependsOnRemove' && (fromId || toId)) {{
        return `Removed dependency: '${{nodeDisplayName(fromId)}}' used by '${{nodeDisplayName(toId || lbl)}}'`;
      }}
      if (act === 'define' && lbl) return `Defined reactive node '${{lbl}}'`;
      if ((act === 'invalidate' || act === 'invalidateEnd') && lbl) return `Invalidated '${{lbl}}'`;
      if (act === 'invalidateStart' && lbl) return `Invalidating '${{lbl}}'`;
      if ((act === 'valueChange' || act === 'inputChange') && lbl) {{
        return ev.value !== undefined && ev.value !== null
          ? `Value change for '${{lbl}}': ${{ev.value}}`
          : `Value change for '${{lbl}}'`;
      }}
      if ((act === 'enter' || act === 'wouldEvaluate') && lbl) return `Evaluating '${{lbl}}'`;
      if ((act === 'exit' || act === 'ordered') && lbl) return `Completed evaluation of '${{lbl}}'`;
      if (act === 'freeze' && lbl) return `Froze '${{lbl}}'`;
      if (act === 'thaw' && lbl) return `Thawed '${{lbl}}'`;
      return lbl ? `Event '${{act}}' on '${{lbl}}'` : act;
    }}

    function nodeLabelHTML(node, svg = false, maxChars = Infinity) {{
      const label = nodeDisplayName(node), moduleName = String(node.module || '');
      let parts = [{{ text: label, module: false }}];
      if (moduleName) {{
        const start = label.indexOf(moduleName);
        parts = start < 0
          ? [{{ text: moduleName, module: true }}, {{ text: ' · ' + label, module: false }}]
          : [{{ text: label.slice(0, start), module: false }}, {{ text: moduleName, module: true }}, {{ text: label.slice(start + moduleName.length), module: false }}];
      }}
      const length = parts.reduce((total, part) => total + part.text.length, 0);
      let remaining = length > maxChars ? maxChars - 1 : length;
      const tag = svg ? 'tspan' : 'span';
      const result = parts.map(part => {{
        const text = part.text.slice(0, remaining);
        remaining -= text.length;
        return part.module && text
          ? '<' + tag + ' class="module-name">' + escapeHTML(text) + '</' + tag + '>'
          : escapeHTML(text);
      }}).join('');
      return result + (length > maxChars ? '…' : '');
    }}

    function graphNodeLabel(node) {{
      if (node.type === 'module') return nodeLabelHTML(node, true, 28);
      let label = nodeDisplayName(node);
      if (node.module) {{
        const [, prefix = '', name = label] = label.match(/^(input[.]|(?:output|calc|effect|reactive)[: ])(.+)$/) || [];
        const namespace = [node.module + '-', node.module + ':'].find(value => name.startsWith(value));
        if (namespace) label = prefix + name.slice(namespace.length);
      }}
      const characters = Array.from(label);
      return escapeHTML(characters.length > 28 ? characters.slice(0, 25).join('') + '...' : label);
    }}

    function renderEventList() {{
      const list = document.getElementById('event-list');
      if (!list) return;
      const events = reactlogData.events || reactlogData.log || [];
      const scopedIds = new Set(getScopedNodes().map(n => n.id));
      const scope = JSON.stringify([searchQuery, selectedStageFilter, currentViewMode, [...scopedIds]]);
      if (eventListScope === scope) return;
      eventListScope = scope;
      list.innerHTML = '';
      let visiblePhase = null;
      const filtered = searchQuery || selectedStageFilter || currentViewMode === 'flush';
      events.forEach((ev, idx) => {{
        const eventIds = filterItems([ev.node_id || ev.id, ev.edge_from, ev.edge_to], Boolean);
        if (filtered && eventIds.length && !eventIds.some(id => scopedIds.has(id))) return;

        const eventPhase = ev.phase || 'interaction';
        if (eventPhase !== visiblePhase) {{
          const phaseLabel = document.createElement('h2');
          phaseLabel.className = 'event-phase-label';
          phaseLabel.textContent = eventPhase === 'init' ? 'Initialization' : 'Recorded actions';
          list.appendChild(phaseLabel);
          visiblePhase = eventPhase;
        }}

        const item = document.createElement('button');
        item.type = 'button';
        item.className = 'event-item' + (idx === currentStep ? ' is-current' : '');
        item.setAttribute('data-step', String(idx));
        const nodeId = ev.node_id || ev.id || '';
        const evName = nodeIndex.has(nodeId) ? nodeDisplayName(nodeIndex.get(nodeId)) : nodeDisplayName(ev.node_label || ev.label || ev.event || ev.action);
        const evDetails = formatEventDetails(ev);
        if (nodeId.startsWith('input:')) item.classList.add('kind-input');
        else if (nodeId.startsWith('calc:')) item.classList.add('kind-calc');
        else if (nodeId.startsWith('output:')) item.classList.add('kind-output');
        else if (nodeId.startsWith('effect:')) item.classList.add('kind-effect');
        item.setAttribute('aria-label', `Step ${{idx}}: ${{evName}}. ${{evDetails}}`);
        item.onclick = () => seekTo(idx);

        const header = document.createElement('div');
        header.className = 'event-header';

        const nameWrap = document.createElement('div');
        nameWrap.className = 'event-name-wrap';

        const stepSpan = document.createElement('span');
        stepSpan.className = 'event-step';
        stepSpan.textContent = `#${{idx}}`;

        const nameSpan = document.createElement('span');
        nameSpan.className = 'event-name';
        nameSpan.innerHTML = nodeIndex.has(nodeId) ? nodeLabelHTML(nodeIndex.get(nodeId)) : escapeHTML(evName);

        nameWrap.appendChild(stepSpan);
        nameWrap.appendChild(nameSpan);

        const badgesWrap = document.createElement('div');
        badgesWrap.className = 'event-badges';

        const tVal = ev.time_sec !== undefined ? ev.time_sec : ev.time;
        if (tVal !== undefined && tVal > 0) {{
          const timeSpan = document.createElement('span');
          timeSpan.className = 'event-time';
          timeSpan.textContent = formatTime(tVal);
          badgesWrap.appendChild(timeSpan);
        }}

        const provBadge = document.createElement('span');
        const prov = ev.provenance || 'inferred';
        provBadge.className = `event-badge provenance-${{prov}}`;
        provBadge.innerHTML = `${{prov === 'observed' ? ICONS.eye : ICONS.zap}} ${{prov.toUpperCase()}}`;
        badgesWrap.appendChild(provBadge);

        const badge = document.createElement('span');
        badge.className = `event-badge ${{ev.status || 'idle'}}`;
        badge.textContent = isIdleEvent(ev) ? 'Idle' : (reactiveEventState(ev) || ev.status || ev.action || ev.event);
        badgesWrap.appendChild(badge);

        header.appendChild(nameWrap);
        header.appendChild(badgesWrap);

        const details = document.createElement('div');
        details.className = 'event-details';
        details.textContent = evDetails;

        item.appendChild(header);
        item.appendChild(details);
        list.appendChild(item);
      }});
    }}

    function explainWhyNodeRan(nodeId, stepIdx) {{
      const events = reactlogData.events || reactlogData.log || [];
      if (!nodeId) return null;

      const targetNode = nodeIndex.get(nodeId);
      if (!targetNode) return null;

      const kind = nodeKind(targetNode);
      const questionVerb = kind.verb || 'run';

      let curWave = allBursts.find(w => stepIdx >= w.startStep && stepIdx <= w.endStep) || allBursts[0];
      if (!curWave && allBursts.length > 0) curWave = allBursts[0];

      const burstEvents = (curWave && events.length > 0)
        ? events.slice(curWave.startStep, curWave.endStep + 1)
        : events;

      const targetLabel = nodeDisplayName(targetNode);
      const cleanTargetName = cleanName(targetLabel);
      const cleanTargetId = cleanName(targetNode.name || targetNode.id);
      const burstEventForNode = burstEvents.find(e => {{
        const eid = e.node_id || e.id || '';
        return eid === nodeId || cleanName(eid) === cleanTargetId || cleanName(eid) === cleanTargetName || (e.node_label && (cleanName(e.node_label) === cleanTargetName || cleanName(e.node_label) === cleanTargetId));
      }});

      const ranInBurst = Boolean(curWave && (curWave.isInit || burstEventForNode));
      const directParents = Array.from(adjUpstream.get(nodeId) || []).map(p => nodeIndex.get(p) || {{ id: p, label: nodeDisplayName(p) }});

      if (ranInBurst) {{
        const question = `Why did ${{targetLabel}} ${{questionVerb}}?`;
        const execTime = (burstEventForNode && (burstEventForNode.time_sec !== undefined ? burstEventForNode.time_sec : burstEventForNode.time))
          || (curWave ? curWave.time : 0);

        const executedNamesInBurst = new Set();
        burstEvents.forEach(e => {{
          const eid = e.node_id || e.id || '';
          if (eid) {{
            executedNamesInBurst.add(eid);
            executedNamesInBurst.add(cleanName(eid));
          }}
          if (e.node_label) executedNamesInBurst.add(cleanName(e.node_label));
        }});

        const activeParents = filterItems(directParents, p =>
          executedNamesInBurst.has(p.id) ||
          executedNamesInBurst.has(cleanName(p.name || p.id)) ||
          executedNamesInBurst.has(cleanName(nodeDisplayName(p)))
        );
        const inactiveParents = filterItems(directParents, p => !activeParents.includes(p));

        let narrative = '';
        if (targetNode.role === 'source' || targetNode.type === 'input') {{
          const valChange = curWave && curWave.humanAction ? curWave.humanAction : targetLabel;
          narrative = `<p><strong>${{escapeHTML(targetLabel)}}</strong> changed (${{escapeHTML(valChange)}}) at ${{escapeHTML(formatTime(execTime))}}.</p>`;
        }} else {{
          narrative = `<p><strong>${{escapeHTML(targetLabel)}}</strong> ${{escapeHTML(questionVerb)}} at ${{escapeHTML(formatTime(execTime))}}.</p>`;
          if (activeParents.length > 0) {{
            narrative += `<div class="why-section-title">Immediate causes:</div><ul class="why-causes-list">${{activeParents.map(p => '<li><strong>' + escapeHTML(nodeDisplayName(p)) + '</strong> recalculated</li>').join('')}}</ul>`;
          }} else if (directParents.length > 0) {{
            narrative += `<div class="why-section-title">Immediate causes:</div><ul class="why-causes-list">${{directParents.map(p => '<li><strong>' + escapeHTML(nodeDisplayName(p)) + '</strong> changed</li>').join('')}}</ul>`;
          }} else if (curWave && curWave.humanAction) {{
            narrative += `<div class="why-section-title">Immediate causes:</div><ul class="why-causes-list"><li><strong>${{escapeHTML(curWave.humanAction)}}</strong></li></ul>`;
          }}
          if (inactiveParents.length > 0) {{
            narrative += `<div class="why-section-title" style="margin-top:0.4rem;opacity:0.75">Other potential dependencies:</div><div style="font:500 0.68rem var(--mono);color:var(--text-muted)">${{inactiveParents.map(p => escapeHTML(nodeDisplayName(p))).join(', ')}}</div>`;
          }}
        }}

        return {{
          nodeId,
          targetLabel,
          question,
          time: execTime,
          narrative,
          directParents: activeParents.length > 0 ? activeParents : directParents,
          targetNode,
          ranInBurst: true
        }};
      }} else {{
        const actionName = curWave ? (curWave.humanAction || curWave.triggerLabel || 'this action') : 'this action';
        const question = `${{targetLabel}} did not ${{questionVerb}}`;

        let lastExec = null;
        for (let i = (curWave ? curWave.startStep - 1 : stepIdx); i >= 0; i--) {{
          const e = events[i];
          const eid = e.node_id || e.id || '';
          if (eid === nodeId || cleanName(eid) === cleanTargetId || cleanName(eid) === cleanTargetName) {{
            lastExec = e;
            break;
          }}
        }}

        let upstreamNote = 'No upstream dependencies were invalidated in this action.';
        if (curWave && curWave.invalidatedNodes && curWave.invalidatedNodes.size > 0) {{
          const invParents = filterItems(directParents, p => curWave.invalidatedNodes.has(p.id));
          if (invParents.length > 0) {{
            upstreamNote = `Upstream dependencies invalidated: ${{invParents.map(p => escapeHTML(nodeDisplayName(p))).join(', ')}}`;
          }}
        }}
        let narrative = `<div class="did-not-run-banner" style="background:color-mix(in srgb, var(--surface-3) 80%, transparent);border:1px solid var(--border);border-radius:6px;padding:0.5rem 0.6rem;margin-bottom:0.4rem"><div style="font:700 0.72rem var(--sans);color:var(--text)">Did not ${{questionVerb}} during ${{escapeHTML(actionName)}}</div><div style="font:500 0.68rem var(--sans);color:var(--text-muted);margin-top:0.2rem">No execution of <strong>${{escapeHTML(targetLabel)}}</strong> was observed or inferred during this action.</div><div style="font:500 0.64rem var(--mono);color:var(--text-dim);margin-top:0.2rem">${{upstreamNote}}</div></div>`;
        if (lastExec) {{
          const lastTime = lastExec.time_sec !== undefined ? lastExec.time_sec : (lastExec.time || 0);
          narrative += `<div style="display:flex;align-items:center;justify-content:space-between;margin-top:0.3rem"><span style="font:500 0.66rem var(--mono);color:var(--text-muted)">Last ran at ${{escapeHTML(formatTime(lastTime))}}</span><button type="button" class="btn mini" data-seek-step="${{lastExec.step}}">Jump to run</button></div>`;
        }}
        if (directParents.length > 0) {{
          narrative += `<div class="why-section-title" style="margin-top:0.5rem">Potential dependencies:</div><div style="font:500 0.68rem var(--mono);color:var(--text-muted)">${{directParents.map(p => escapeHTML(nodeDisplayName(p))).join(', ')}}</div>`;
        }}

        return {{
          nodeId,
          targetLabel,
          question,
          time: null,
          narrative,
          directParents: [],
          targetNode,
          ranInBurst: false
        }};
      }}
    }}

    function renderInspector() {{
      const events = reactlogData.events || reactlogData.log || [];
      const ev = events[currentStep] || {{}};
      const currentEventNodeId = ev.node_id || ev.id;
      const targetNodeId = selectedNodeId || currentEventNodeId;
      const node = targetNodeId ? nodeIndex.get(targetNodeId) : null;
      renderPlotPreview(node);

      const whyTitle = document.getElementById('why-title');
      const whyStory = document.getElementById('why-story');
      const whyFlow = document.getElementById('why-cascade-flow');

      if (node) {{
        const explanation = explainWhyNodeRan(node.id, currentStep);
        if (explanation) {{
          whyTitle.textContent = explanation.question;
          whyStory.innerHTML = explanation.narrative;

          whyFlow.innerHTML = '';
          if (explanation.directParents.length > 1) {{
            const parentsCol = document.createElement('div');
            parentsCol.className = 'dag-parents-col';
            explanation.directParents.forEach(p => {{
              const pill = document.createElement('button');
              pill.type = 'button';
              pill.className = 'flow-node-pill is-trigger';
              pill.innerHTML = nodeLabelHTML(p);
              pill.onclick = () => selectNode(p.id);
              parentsCol.appendChild(pill);
            }});
            whyFlow.appendChild(parentsCol);

            const bracket = document.createElement('div');
            bracket.className = 'dag-bracket';
            bracket.textContent = '➔';
            whyFlow.appendChild(bracket);

            const targetCol = document.createElement('div');
            targetCol.className = 'dag-target-col';
            const targetPill = document.createElement('button');
            targetPill.type = 'button';
            targetPill.className = 'flow-node-pill is-target';
            targetPill.innerHTML = nodeLabelHTML(node);
            targetCol.appendChild(targetPill);
            whyFlow.appendChild(targetCol);
          }} else if (explanation.directParents.length === 1) {{
            const p = explanation.directParents[0];
            const pPill = document.createElement('button');
            pPill.type = 'button';
            pPill.className = 'flow-node-pill is-trigger';
            pPill.innerHTML = nodeLabelHTML(p);
            pPill.onclick = () => selectNode(p.id);
            whyFlow.appendChild(pPill);

            const arrow = document.createElement('span');
            arrow.className = 'dag-bracket';
            arrow.textContent = '➔';
            whyFlow.appendChild(arrow);

            const targetPill = document.createElement('button');
            targetPill.type = 'button';
            targetPill.className = 'flow-node-pill is-target';
            targetPill.innerHTML = nodeLabelHTML(node);
            whyFlow.appendChild(targetPill);
          }} else {{
            const targetPill = document.createElement('button');
            targetPill.type = 'button';
            targetPill.className = 'flow-node-pill is-trigger is-target';
            targetPill.innerHTML = nodeLabelHTML(node);
            whyFlow.appendChild(targetPill);
          }}
        }}

        const kind = nodeKind(node);
        document.getElementById('insp-title').innerHTML = nodeLabelHTML(node) + ' (' + escapeHTML(kind.label) + ')';
        const execCounts = getNodeExecutionCounts();
        const execCount = execCounts.get(node.id) || 0;
        document.getElementById('insp-meta-line').textContent = filterItems([node.source_file, node.line ? `Line ${{node.line}}` : 'Unknown'], Boolean).join(' · ');
        const runsEl = document.getElementById('insp-runs-badge');
        if (runsEl) {{
          runsEl.innerHTML = execCount > 0 ? `· Runs: <b>${{execCount}}×</b>` : '';
        }}

        const downstreamSec = document.getElementById('insp-downstream-section');
        const downstreamWrap = document.getElementById('insp-downstream-list');
        downstreamWrap.innerHTML = '';
        const children = Array.from(adjDownstream.get(node.id) || []);
        if (children.length === 0) {{
          downstreamSec.hidden = true;
        }} else {{
          downstreamSec.hidden = false;
          children.forEach(c => {{
            const cNode = nodeIndex.get(c);
            const pill = document.createElement('button');
            pill.type = 'button';
            pill.className = 'conn-pill';
            pill.innerHTML = cNode ? nodeLabelHTML(cNode) : escapeHTML(c);
            pill.onclick = () => selectNode(c);
            downstreamWrap.appendChild(pill);
          }});
        }}

        const upstreamSec = document.getElementById('insp-upstream-section');
        const upstreamWrap = document.getElementById('insp-upstream-list');
        upstreamWrap.innerHTML = '';
        const parents = Array.from(adjUpstream.get(node.id) || []);
        if (parents.length === 0) {{
          upstreamSec.hidden = true;
        }} else {{
          upstreamSec.hidden = false;
          parents.forEach(p => {{
            const pNode = nodeIndex.get(p);
            const pill = document.createElement('button');
            pill.type = 'button';
            pill.className = 'conn-pill';
            pill.innerHTML = pNode ? nodeLabelHTML(pNode) : escapeHTML(p);
            pill.onclick = () => selectNode(p);
            upstreamWrap.appendChild(pill);
          }});
        }}

        const inspType = document.getElementById('insp-type');
        if (inspType) inspType.textContent = kind.label;
        const inspStatus = document.getElementById('insp-status');
        if (inspStatus) inspStatus.textContent = ev.status || 'active';

        const filterBtn = document.getElementById('btn-filter-lineage');
        if (filterBtn) filterBtn.style.display = 'inline-flex';

        renderInlineSource(node);
      }} else if (ev) {{
        const filterBtn = document.getElementById('btn-filter-lineage');
        if (filterBtn) filterBtn.style.display = 'none';

        const evTitle = nodeDisplayName(ev.node_id || ev.id || ev.node_label || ev.label || ev.action || ev.event);
        whyTitle.textContent = evTitle;
        whyStory.innerHTML = `<p>${{escapeHTML(formatEventDetails(ev) || 'Step #' + currentStep)}}</p>`;
        whyFlow.innerHTML = '';

        document.getElementById('insp-title').textContent = evTitle;
        document.getElementById('insp-meta-line').textContent = '—';
        const runsEl = document.getElementById('insp-runs-badge');
        if (runsEl) runsEl.textContent = '';
        const inspType = document.getElementById('insp-type');
        if (inspType) inspType.textContent = ev.phase === 'init' ? 'Initialization event' : (ev.action || 'Event');
        const inspStatus = document.getElementById('insp-status');
        if (inspStatus) inspStatus.textContent = ev.status || 'active';
        document.getElementById('insp-upstream-section').hidden = true;
        document.getElementById('insp-downstream-section').hidden = true;
      }}
    }}

    const pythonKeywords = new Set(["False", "None", "True", "and", "as", "assert", "async", "await", "break", "class", "continue", "def", "del", "elif", "else", "except", "finally", "for", "from", "global", "if", "import", "in", "is", "lambda", "nonlocal", "not", "or", "pass", "raise", "return", "try", "while", "with", "yield"]);
    const highlightedSourceCache = new Map();

    function highlightedSourceLines(source) {{
      if (highlightedSourceCache.has(source)) return highlightedSourceCache.get(source);
      // Tokenize the whole file so triple-quoted strings keep their color across lines.
      // Escape every token before adding our own spans; imported JSON contains raw code.
      const tokens = /#[^\\r\\n]*|[rRuUbBfF]{{0,2}}(?:\"\"\"[\\s\\S]*?(?:\"\"\"|$)|'''[\\s\\S]*?(?:'''|$)|"(?:\\\\.|[^"\\\\\\r\\n])*"|'(?:\\\\.|[^'\\\\\\r\\n])*')|\\b(?:0[xX][\\da-fA-F_]+|0[bB][01_]+|0[oO][0-7_]+|\\d[\\d_]*(?:\\.[\\d_]*)?(?:[eE][+-]?[\\d_]+)?[jJ]?)|\\b[A-Za-z_]\\w*\\b|[-+*/%=<>!&|^~:@.,;()[\\]{{}}]/g;
      let markup = '', cursor = 0;
      for (const match of source.matchAll(tokens)) {{
        const token = match[0];
        markup += escapeHTML(source.slice(cursor, match.index));
        let kind = '';
        if (token.startsWith('#')) kind = 'comment';
        else if (/^[rRuUbBfF]{{0,2}}["']/.test(token)) kind = 'string';
        else if (/^\\d/.test(token)) kind = 'number';
        else if (pythonKeywords.has(token)) kind = 'keyword';
        else if (!/^\\w/.test(token)) kind = 'operator';
        // Close spans on each line so snippets can be sliced without broken markup.
        markup += token.split('\\n').map(part => kind && part
          ? `<span class="syntax-${{kind}}">${{escapeHTML(part)}}</span>` : escapeHTML(part)).join('\\n');
        cursor = match.index + token.length;
      }}
      markup += escapeHTML(source.slice(cursor));
      const lines = markup.split('\\n');
      if (lines.at(-1) === '') lines.pop();
      highlightedSourceCache.set(source, lines);
      return lines;
    }}

    function sourceLineHTML(content, lineNum, active = false) {{
      return `<div class="source-line${{active ? ' is-active' : ''}}" data-line="${{lineNum}}"><span class="source-line-num" aria-hidden="true">${{lineNum}}</span><span class="source-line-content">${{content}}</span></div>`;
    }}

    let displayedSourceFile = '';

    function nodeSource(node) {{
      return (reactlogData.sources || {{}})[node?.source_file] || rawAppSource;
    }}

    function showSourceFile(filename) {{
      const sources = reactlogData.sources || {{}};
      if (!Object.prototype.hasOwnProperty.call(sources, filename)) return;
      const selector = document.getElementById('source-file-select');
      selector.replaceChildren();
      Object.keys(sources).forEach(name => {{
        const option = document.createElement('option');
        option.value = name; option.textContent = name;
        selector.appendChild(option);
      }});
      selector.hidden = false;
      selector.value = filename;
      displayedSourceFile = filename;
      const code = document.querySelector('#source-panel code');
      code.innerHTML = highlightedSourceLines(sources[filename]).map((line, i) => sourceLineHTML(line, i + 1)).join('');
    }}

    function renderInlineSource(node) {{
      const drawer = document.getElementById('insp-source-drawer');
      const codeBlock = document.getElementById('insp-source-code');
      const refsBlock = document.getElementById('insp-source-refs');
      const source = nodeSource(node);
      if (!drawer || !codeBlock || !source) return;

      if (!node.line) {{
        drawer.hidden = true;
        return;
      }}

      drawer.hidden = false;
      const lines = highlightedSourceLines(source);
      const startLine = Math.max(0, node.line - 1);
      let endLine = Math.min(lines.length, startLine + 4);

      let snippetHtml = '';
      for (let i = startLine; i < endLine; i++) {{
        const lineNum = i + 1;
        snippetHtml += sourceLineHTML(lines[i], lineNum, lineNum === node.line);
      }}
      codeBlock.querySelector('code').innerHTML = snippetHtml;

      if (refsBlock) {{
        const children = Array.from(adjDownstream.get(node.id) || []);
        if (children.length > 0) {{
          refsBlock.hidden = false;
          const refButtons = children.map(c => {{
            const cNode = nodeIndex.get(c);
            const lbl = cNode ? nodeDisplayName(cNode) : nodeDisplayName(c);
            const lineStr = cNode && cNode.line ? ` · line ${{cNode.line}}` : '';
            return `<button type="button" class="conn-pill" data-node-id="${{escapeHTML(c)}}">${{escapeHTML(lbl)}}${{lineStr}}</button>`;
          }}).join(' ');
          refsBlock.innerHTML = `<span>Referenced by:</span> ${{refButtons}}`;
        }} else {{
          refsBlock.hidden = true;
        }}
      }}
    }}

    function toggleSourceDrawer() {{
      const codeBlock = document.getElementById('insp-source-code');
      const arrow = document.getElementById('source-drawer-arrow');
      const btn = document.getElementById('btn-toggle-source-drawer');
      if (!codeBlock || !arrow || !btn) return;
      isSourceDrawerOpen = !isSourceDrawerOpen;
      codeBlock.hidden = !isSourceDrawerOpen;
      arrow.textContent = isSourceDrawerOpen ? '▴' : '▾';
      btn.setAttribute('aria-expanded', String(isSourceDrawerOpen));
    }}

    function selectNode(nodeId) {{
      selectedNodeId = nodeId;
      focusedNodeId = nodeId;
      showSidebarPanel('timeline');
      renderInspector();
      renderGraph();
      updateSourceHighlight();
      updateTraceTimelineScrubber(getCurrentStepTime());
    }}

    function clearNodeSelection() {{
      focusedNodeId = null;
      selectedNodeId = null;
      if (selectedSearchNodeId) {{
        selectedSearchNodeId = null;
        searchQuery = '';
        document.getElementById('search-input').value = '';
      }}
      renderInspector();
      renderGraph();
      updateSourceHighlight();
      updateTraceTimelineScrubber(getCurrentStepTime());
    }}

    const collapsedModules = new Set();

    // Rank the condensed graph: cycles share a rank, every other edge goes right.
    function dependencyRanks(nodes, edges) {{
      const children = new Map(nodes.map(n => [n.id, []]));
      edges.forEach(e => children.get(e.from)?.push(e.to));
      let serial = 0;
      const indices = new Map(), low = new Map(), stack = [], onStack = new Set();
      const component = new Map(), components = [];
      function visit(id) {{
        indices.set(id, serial); low.set(id, serial++); stack.push(id); onStack.add(id);
        for (const next of children.get(id) || []) {{
          if (!indices.has(next)) {{ visit(next); low.set(id, Math.min(low.get(id), low.get(next))); }}
          else if (onStack.has(next)) low.set(id, Math.min(low.get(id), indices.get(next)));
        }}
        if (low.get(id) === indices.get(id)) {{
          const members = []; let next;
          do {{ next = stack.pop(); onStack.delete(next); component.set(next, components.length); members.push(next); }} while (next !== id);
          components.push(members);
        }}
      }}
      nodes.forEach(n => {{ if (!indices.has(n.id)) visit(n.id); }});
      const ranks = components.map(() => 0), incoming = components.map(() => 0), outgoing = components.map(() => new Set());
      edges.forEach(e => {{
        const from = component.get(e.from), to = component.get(e.to);
        if (from !== to && !outgoing[from].has(to)) {{ outgoing[from].add(to); incoming[to]++; }}
      }});
      const queue = filterItems(incoming.map((count, i) => count === 0 ? i : -1), i => i >= 0);
      for (let i = 0; i < queue.length; i++) {{
        const from = queue[i];
        outgoing[from].forEach(to => {{ ranks[to] = Math.max(ranks[to], ranks[from] + 1); if (--incoming[to] === 0) queue.push(to); }});
      }}
      return new Map(nodes.map(n => [n.id, ranks[component.get(n.id)]]));
    }}

    function arrangeGraphBand(members, edges, ranks, top, colWidth, rowHeight) {{
      const columns = new Map();
      members.forEach(n => {{
        const rank = ranks.get(n.id);
        if (!columns.has(rank)) columns.set(rank, []);
        columns.get(rank).push(n);
      }});
      const ordered = [...columns.keys()].sort((a, b) => a - b);
      const order = new Map();
      columns.forEach(col => col.forEach((n, i) => order.set(n.id, i)));
      // Alternate sweeps group nodes by their neighbours without moving them across modules.
      for (let pass = 0; pass < 4; pass++) {{
        const reverse = pass % 2 === 1;
        for (const rank of reverse ? ordered.slice().reverse() : ordered) {{
          const col = columns.get(rank), scores = new Map();
          col.forEach(n => {{
            const peers = filterItems(filterItems(edges, e => reverse ? e.from === n.id : e.to === n.id)
              .map(e => reverse ? e.to : e.from), id => order.has(id));
            scores.set(n.id, peers.length
              ? peers.reduce((sum, id) => sum + order.get(id) + ranks.get(id) / 1000, 0) / peers.length
              : order.get(n.id));
          }});
          col.sort((a, b) => scores.get(a.id) - scores.get(b.id) || order.get(a.id) - order.get(b.id));
          col.forEach((n, i) => order.set(n.id, i));
        }}
      }}
      const rows = Math.max(1, ...[...columns.values()].map(col => col.length));
      const positions = {{}};
      for (const rank of ordered) {{
        const col = columns.get(rank);
        let previous = -1;
        col.forEach((n, i) => {{
          const parents = filterItems(edges, e => e.to === n.id && positions[e.from]).map(e => positions[e.from].y);
          const preferred = parents.length
            ? Math.round((parents.reduce((sum, y) => sum + y, 0) / parents.length - top - 40) / rowHeight)
            : i;
          const row = Math.max(previous + 1, Math.min(rows - col.length + i, preferred));
          positions[n.id] = {{ x: 150 + rank * colWidth, y: top + 40 + row * rowHeight }};
          previous = row;
        }});
      }}
      return {{ positions, rows }};
    }}

    function routeGraphEdge(edge, positions, nodeWidth, nodeHeight, edges = []) {{
      const from = positions[edge.from], to = positions[edge.to];
      if (!from || !to) return [];
      const offset = (outgoing, id) => {{
        const peers = filterItems(edges, e => outgoing ? e.from === id : e.to === id)
          .sort((a, b) => {{
            const first = outgoing ? a.to : a.from, second = outgoing ? b.to : b.from;
            return positions[first].y - positions[second].y || first.localeCompare(second);
          }});
        const index = peers.indexOf(edge);
        return peers.length > 1 && index >= 0
          ? (index / (peers.length - 1) - 0.5) * Math.min(nodeHeight - 24, (peers.length - 1) * 12) : 0;
      }};
      const x1 = from.x + nodeWidth / 2, y1 = from.y + offset(true, edge.from);
      const forward = to.x > from.x;
      const x2 = to.x + (forward ? -1 : 1) * nodeWidth / 2, y2 = to.y + offset(false, edge.to);
      const lane = Math.max(0, edges.indexOf(edge));
      let points;
      if (forward && x2 - x1 < nodeWidth) {{
        const gutter = x1 + (x2 - x1) * (0.35 + (lane % 5) * 0.075);
        points = [[x1, y1], [gutter, y1], [gutter, y2], [x2, y2]];
      }} else {{
        const clearance = 12, inset = 18 + (lane % 4) * 4;
        const exit = x1 + inset, entry = x2 + (forward ? -inset : inset);
        const left = Math.min(exit, entry), right = Math.max(exit, entry);
        const obstacles = filterItems(Object.values(positions), p =>
          p.x + nodeWidth / 2 + clearance > left && p.x - nodeWidth / 2 - clearance < right);
        const candidates = [y1, y2, (y1 + y2) / 2, ...obstacles.flatMap(p =>
          [p.y - nodeHeight / 2 - clearance, p.y + nodeHeight / 2 + clearance])];
        const cost = y => Math.abs(y1 - y) + Math.abs(y2 - y) + Math.abs(y - (y1 + y2) / 2) * 0.01;
        // Connections that skip a column travel through an empty horizontal lane.
        const y = filterItems(candidates, candidate => obstacles.every(p =>
          candidate <= p.y - nodeHeight / 2 - clearance || candidate >= p.y + nodeHeight / 2 + clearance))
          .sort((a, b) => cost(a) - cost(b))[0];
        points = [[x1, y1], [exit, y1], [exit, y], [entry, y], [entry, y2], [x2, y2]];
      }}
      const route = [];
      for (const point of points) {{
        const last = route[route.length - 1];
        if (last && last[0] === point[0] && last[1] === point[1]) continue;
        while (route.length > 1) {{
          const a = route[route.length - 2], b = route[route.length - 1];
          if ((a[0] === b[0] && b[0] === point[0]) || (a[1] === b[1] && b[1] === point[1])) route.pop();
          else break;
        }}
        route.push(point);
      }}
      return route;
    }}

    function graphEdgePath(edge, positions, nodeWidth, nodeHeight, edges = []) {{
      const route = routeGraphEdge(edge, positions, nodeWidth, nodeHeight, edges);
      if (route.length < 2) return '';
      const [x1, y1] = route[0], [x2, y2] = route[route.length - 1];
      const clearance = 12;
      const canCurveDirectly = x2 > x1 && Object.entries(positions).every(([id, p]) => {{
        if (id === edge.from || id === edge.to) return true;
        if (p.x + nodeWidth / 2 + clearance <= x1 || p.x - nodeWidth / 2 - clearance >= x2) return true;
        const u = Math.max(0, Math.min(1, (p.x - x1) / (x2 - x1)));
        const curveY = y1 + (y2 - y1) * (3 * u * u - 2 * u * u * u);
        return Math.abs(curveY - p.y) >= nodeHeight / 2 + clearance;
      }});
      if (canCurveDirectly) {{
        const dx = Math.max(28, (x2 - x1) * 0.42);
        return `M ${{x1}} ${{y1}} C ${{x1 + dx}} ${{y1}}, ${{x2 - dx}} ${{y2}}, ${{x2}} ${{y2}}`;
      }}
      const laneY = route.length >= 4 ? route[2][1] : (y1 + y2) / 2;
      if (x2 > x1) {{
        const exitX = Math.min((x1 + x2) / 2, x1 + 56);
        const entryX = Math.max(exitX, x2 - 56);
        return `M ${{x1}} ${{y1}} C ${{(x1 + exitX) / 2}} ${{y1}}, ${{(x1 + exitX) / 2}} ${{laneY}}, ${{exitX}} ${{laneY}} C ${{(2 * exitX + entryX) / 3}} ${{laneY}}, ${{(exitX + 2 * entryX) / 3}} ${{laneY}}, ${{entryX}} ${{laneY}} C ${{(entryX + x2) / 2}} ${{laneY}}, ${{(entryX + x2) / 2}} ${{y2}}, ${{x2}} ${{y2}}`;
      }}
      const exitX = route[1][0], entryX = route[route.length - 2][0];
      const midStart = (x1 + exitX) / 2, midEnd = (x2 + entryX) / 2;
      return `M ${{x1}} ${{y1}} C ${{exitX}} ${{y1}}, ${{exitX}} ${{laneY}}, ${{midStart}} ${{laneY}} C ${{(2 * midStart + midEnd) / 3}} ${{laneY}}, ${{(midStart + 2 * midEnd) / 3}} ${{laneY}}, ${{midEnd}} ${{laneY}} C ${{entryX}} ${{laneY}}, ${{entryX}} ${{y2}}, ${{x2}} ${{y2}}`;
    }}

    function toggleModule(name) {{
      if (collapsedModules.has(name)) collapsedModules.delete(name);
      else collapsedModules.add(name);
      renderGraph(); fitGraph();
    }}

    function renderPlotPreview(node) {{
      const panel = document.getElementById('insp-plot');
      const img = document.getElementById('insp-plot-image');
      const caption = document.getElementById('insp-plot-caption');
      const events = reactlogData.events || reactlogData.log || [];
      const preview = node && events.slice(0, currentStep + 1).reverse().find(e => e.node_id === node.id && e.plot);
      panel.hidden = !node || (node.render_type !== 'plot' && node.render_type !== 'image' && !preview);
      img.hidden = !preview;
      img.removeAttribute('src');
      if (preview && /^data:image\\/(png|jpeg|gif|webp);base64,/.test(preview.plot.src)) {{
        img.src = preview.plot.src;
        img.alt = preview.plot.alt || node.label;
        caption.textContent = `Recorded plot · ${{Number(preview.time_sec || 0).toFixed(2)}}s`;
      }} else {{
        img.hidden = true;
        caption.textContent = 'No plot captured at this step. Record the app to preview rendered plots here.';
      }}
    }}

    function getNodeExecutionCounts() {{
      const counts = new Map();
      const events = reactlogData.events || reactlogData.log || [];
      events.forEach(ev => {{
        const nid = ev.node_id || ev.id;
        if (!nid) return;
        if (ev.event === 'ordered' || ev.event === 'outputUpdated' || ev.event === 'inputChange' || ev.event === 'assumeValue') {{
          counts.set(nid, (counts.get(nid) || 0) + 1);
        }}
      }});
      return counts;
    }}

    function toggleShortcutsModal() {{
      const modal = document.getElementById('shortcuts-modal');
      if (!modal) return;
      const isHidden = modal.hidden;
      modal.hidden = !isHidden;
      if (isHidden) {{
        modal.querySelector('.modal-close-btn')?.focus();
      }}
    }}

    function getNodeShapePath(n, p, width, height) {{
      const role = n.role || n.type;
      const x0 = p.x - width / 2;
      const x1 = p.x + width / 2;
      const y0 = p.y - height / 2;
      const y1 = p.y + height / 2;
      const ym = p.y;
      const wc = 20;

      if (n.type === 'module') {{
        return `M ${{x0}} ${{y0}} H ${{x1}} V ${{y1}} H ${{x0}} Z`;
      }}
      if (role === 'source' || n.type === 'input') {{
        return `M ${{x0}} ${{y0}} H ${{x1 - wc}} L ${{x1}} ${{ym}} L ${{x1 - wc}} ${{y1}} H ${{x0}} Z`;
      }}
      if (role === 'conductor' || n.type === 'calc') {{
        return `M ${{x0}} ${{y0}} H ${{x1 - wc}} L ${{x1}} ${{ym}} L ${{x1 - wc}} ${{y1}} H ${{x0}} L ${{x0 + wc}} ${{ym}} Z`;
      }}
      return `M ${{x0}} ${{y0}} H ${{x1}} V ${{y1}} H ${{x0}} L ${{x0 + wc}} ${{ym}} Z`;
    }}

    function renderGraph(previousStep = currentStep) {{
      const svg = document.getElementById('graph-content');
      if (!svg) return;
      svg.innerHTML = '';
      const isLight = getActiveTheme() === 'light';
      const visibleNodes = [];
      const representatives = new Map();
      const moduleNodes = new Map();
      const focusedNodes = focusedNodeId ? new Set([
        focusedNodeId, ...getUpstreamNodes(focusedNodeId), ...getDownstreamNodes(focusedNodeId)
      ]) : null;
      const clearBtn = document.getElementById('btn-clear-selection');
      if (clearBtn) clearBtn.hidden = !focusedNodeId;
      const inspectBtn = document.getElementById('btn-inspect-selection');
      if (inspectBtn) inspectBtn.hidden = !focusedNodeId || !document.getElementById('sidebar').hidden;
      const railInspectorBtn = document.getElementById('btn-toggle-inspector-bottom');
      if (railInspectorBtn) railInspectorBtn.classList.toggle('has-selection', Boolean(focusedNodeId));

      const scopedNodes = getScopedNodes();
      document.getElementById('empty-graph-message').hidden = !(changedNodesOnly && changedNodeIds && !scopedNodes.length && !searchQuery);
      updateFilterState(scopedNodes);
      scopedNodes.forEach(n => {{
        if (n.module && collapsedModules.has(n.module)) {{
          const id = `module:${{n.module}}`;
          representatives.set(n.id, id);
          if (!moduleNodes.has(id)) {{
            const group = {{ id, label: n.module, type: 'module', role: 'conductor', module: n.module, members: [] }};
            moduleNodes.set(id, group); visibleNodes.push(group);
          }}
          moduleNodes.get(id).members.push(n.id);
        }} else {{ representatives.set(n.id, n.id); visibleNodes.push(n); }}
      }});
      const nodes = visibleNodes;
      const replay = graphStateAtStep();
      const edges = [], edgeKeys = new Map();
      (reactlogData.edges || []).forEach(e => {{
        const from = representatives.get(e.from), to = representatives.get(e.to);
        if (!from || !to || from === to) return;
        const key = JSON.stringify([from, to]);
        const related = !focusedNodes || (focusedNodes.has(e.from) && focusedNodes.has(e.to));
        if (!edgeKeys.has(key)) {{
          const edge = {{ from, to, isolated: Boolean(e.isolated), inactive: replay.inactiveEdges.has(JSON.stringify([e.from, e.to])), related }};
          edges.push(edge); edgeKeys.set(key, edge);
        }} else if (related) edgeKeys.get(key).related = true;
      }});

      const ranks = dependencyRanks(nodes, edges);
      const colWidth = 350, rowHeight = 92, nodeWidth = 280, nodeHeight = 64;
      const pos = {{}};
      // Module bands keep boxes disjoint while dependency rank sets horizontal position.
      const bands = new Map();
      nodes.forEach(n => {{ const key = n.module || ''; if (!bands.has(key)) bands.set(key, []); bands.get(key).push(n); }});
      let top = 70;
      for (const [name, members] of bands) {{
        const layout = arrangeGraphBand(members, edges, ranks, top, colWidth, rowHeight);
        const rows = layout.rows;
        Object.assign(pos, layout.positions);
        if (!name || !collapsedModules.has(name)) {{
          const left = Math.min(...members.map(n => pos[n.id].x)) - nodeWidth / 2 - 20;
          const right = Math.max(...members.map(n => pos[n.id].x)) + nodeWidth / 2 + 20;
          const box = document.createElementNS('http://www.w3.org/2000/svg', 'g');
          const dimmed = focusedNodes && !members.some(n => focusedNodes.has(n.id));
          box.setAttribute('class', (name ? 'module-box' : 'app-box') + (dimmed ? ' is-dimmed' : ''));
          if (name) {{
            box.setAttribute('data-module', name);
            box.setAttribute('tabindex', '0');
            box.setAttribute('role', 'region');
            box.setAttribute('aria-label', `Module ${{name}}`);
            box.onkeydown = e => {{ if (e.key === 'Enter' || e.key === ' ') {{ e.preventDefault(); e.stopPropagation(); toggleModule(name); }} }};
          }}
          const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
          rect.setAttribute('x', left);
          rect.setAttribute('y', top - 28);
          rect.setAttribute('width', Math.max(320, right - left));
          rect.setAttribute('height', rows * rowHeight + 20);
          rect.setAttribute('rx', '12');
          rect.setAttribute('fill', isLight ? '#e0f2fe66' : '#17314b55');
          rect.setAttribute('stroke', isLight ? '#3b6b91' : '#5b82a6');
          rect.setAttribute('stroke-dasharray', '5 4');
          rect.onclick = e => e.stopPropagation();
          box.appendChild(rect);

          if (name) {{
            const headerBtn = document.createElementNS('http://www.w3.org/2000/svg', 'g');
            headerBtn.setAttribute('class', 'module-collapse-btn');
            headerBtn.setAttribute('tabindex', '0');
            headerBtn.setAttribute('role', 'button');
            headerBtn.setAttribute('aria-expanded', 'true');
            headerBtn.setAttribute('aria-label', `Collapse module ${{name}}`);
            headerBtn.onclick = e => {{ e.stopPropagation(); toggleModule(name); }};
            headerBtn.ondblclick = e => {{ e.stopPropagation(); toggleModule(name); }};
            headerBtn.onkeydown = e => {{ if (e.key === 'Enter' || e.key === ' ') {{ e.preventDefault(); e.stopPropagation(); toggleModule(name); }} }};

            const label = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            label.setAttribute('x', left + 14);
            label.setAttribute('y', top - 8);
            label.setAttribute('fill', isLight ? '#315575' : '#a4c7e7');
            label.setAttribute('font-size', '12');
            label.innerHTML = nodeLabelHTML({{ label: name, module: name }}, true) + escapeHTML(` · ${{members.length}} nodes · click to collapse`);
            headerBtn.appendChild(label);

            const textWidth = (label.getComputedTextLength && label.getComputedTextLength()) || (name.length * 8 + 190);
            const iconX = left + 14 + textWidth + 8;
            const iconY = top - 19;

            const iconG = document.createElementNS('http://www.w3.org/2000/svg', 'g');
            iconG.setAttribute('class', 'module-collapse-icon');
            iconG.setAttribute('transform', `translate(${{iconX}}, ${{iconY}})`);
            iconG.setAttribute('aria-hidden', 'true');

            const iconBg = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
            iconBg.setAttribute('width', '16');
            iconBg.setAttribute('height', '16');
            iconBg.setAttribute('rx', '3');
            iconBg.setAttribute('fill', isLight ? '#e2e8f0' : '#1e293b');
            iconBg.setAttribute('stroke', isLight ? '#94a3b8' : '#475569');
            iconBg.setAttribute('stroke-width', '1');
            iconG.appendChild(iconBg);

            const iconPath = document.createElementNS('http://www.w3.org/2000/svg', 'path');
            iconPath.setAttribute('d', 'M3.5 6.5h3v-3M3.5 3.5l3 3M12.5 9.5h-3v3M12.5 12.5l-3-3');
            iconPath.setAttribute('fill', 'none');
            iconPath.setAttribute('stroke', isLight ? '#0284c7' : '#38bdf8');
            iconPath.setAttribute('stroke-width', '1.5');
            iconPath.setAttribute('stroke-linecap', 'round');
            iconPath.setAttribute('stroke-linejoin', 'round');
            iconG.appendChild(iconPath);

            headerBtn.appendChild(iconG);

            const hitRect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
            hitRect.setAttribute('x', left + 8);
            hitRect.setAttribute('y', top - 24);
            hitRect.setAttribute('width', textWidth + 30);
            hitRect.setAttribute('height', 22);
            hitRect.setAttribute('fill', 'transparent');
            hitRect.setAttribute('class', 'module-header-hit');
            headerBtn.insertBefore(hitRect, label);

            box.appendChild(headerBtn);
          }} else {{
            const label = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            label.setAttribute('x', left + 14);
            label.setAttribute('y', top - 8);
            label.setAttribute('fill', isLight ? '#315575' : '#a4c7e7');
            label.setAttribute('font-size', '12');
            label.textContent = escapeHTML(`App · ${{members.length}} nodes`);
            box.appendChild(label);
          }}
          svg.appendChild(box);
        }}
        top += rows * rowHeight + 75;
      }}

      const events = reactlogData.events || reactlogData.log || [];
      const activeEvent = events[currentStep] || {{}};
      const activeNodeId = activeEvent.node_id || activeEvent.id;

      curWave = allBursts.slice().reverse().find(w => currentStep >= w.startStep) || allBursts[0];
      const executedInBurst = new Set();
      if (curWave) {{
        curWave.inputs.forEach(i => executedInBurst.add(i.nodeId));
        curWave.calcs.forEach(c => executedInBurst.add(c.nodeId));
        curWave.outputs.forEach(o => executedInBurst.add(o.nodeId));
      }}

      const motionPaths = new Map();
      edges.forEach(e => {{
        const p1 = pos[e.from];
        const p2 = pos[e.to];
        if (p1 && p2) {{
          const fromMatch = representatives.get(activeEvent.edge_from || activeEvent.dependsOn);
          const toMatch = representatives.get(activeEvent.edge_to || activeEvent.node_id || activeEvent.id);
          const isEdgeActive = !e.inactive && ((fromMatch && toMatch)
            ? (fromMatch === e.from && toMatch === e.to)
            : (activeEvent.node_id === e.to && (activeEvent.event === 'dependsOn' || activeEvent.event === 'propagate' || activeEvent.action === 'dependsOn' || activeEvent.action === 'invalidate')));

          const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
          const d = graphEdgePath(e, pos, nodeWidth, nodeHeight, edges);
          path.setAttribute('d', d);
          if (e.related && !e.isolated) motionPaths.set(JSON.stringify([e.from, e.to]), d);
          path.setAttribute('fill', 'none');
          path.setAttribute('stroke-linecap', 'round');
          path.setAttribute('stroke-linejoin', 'round');
          path.setAttribute('data-from', e.from);
          path.setAttribute('data-to', e.to);
          path.setAttribute('data-active', isEdgeActive ? 'true' : 'false');
          path.setAttribute('class', 'graph-edge' + (e.isolated ? ' is-isolated' : '') + (e.inactive ? ' is-inactive' : '') + (!e.related ? ' is-dimmed' : ''));
          const edgeTitle = document.createElementNS('http://www.w3.org/2000/svg', 'title');
          const fromLabel = nodeDisplayName(e.from);
          const toLabel = nodeDisplayName(e.to);
          if (e.isolated) {{
            path.setAttribute('stroke-dasharray', '5 4');
            path.setAttribute('data-isolated', 'true');
            edgeTitle.textContent = `Isolated read (reactive.isolate) from ${{fromLabel}} to ${{toLabel}}`;
          }} else {{
            edgeTitle.textContent = `${{fromLabel}} → ${{toLabel}}`;
          }}
          path.appendChild(edgeTitle);
          path.setAttribute('marker-end', isEdgeActive ? 'url(#arrow-active)' : (e.isolated ? 'url(#arrow-isolated)' : 'url(#arrow)'));

          svg.appendChild(path);
        }}
      }});
      updateEdgePulses(motionPaths, representatives, events, previousStep);

      const execCounts = getNodeExecutionCounts();
      nodes.forEach(n => {{
        const p = pos[n.id] || {{ x: 200, y: 200 }};
        const isActive = activeNodeId === n.id || (n.members || []).includes(activeNodeId);
        const isSelected = selectedNodeId === n.id || (n.members || []).includes(selectedNodeId);
        const isExecuted = (n.members || []).some(id => executedInBurst.has(id)) || executedInBurst.has(n.id) || (n.id.startsWith('input:') && executedInBurst.has(n.id.replace('input:', '')));
        const kind = nodeKind(n);
        const isDimmed = focusedNodes && !(n.members || [n.id]).some(id => focusedNodes.has(id));
        const isClientData = isClientDataNode(n);

        const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        g.setAttribute('class', 'graph-node' + (isSelected ? ' is-selected' : '') + (isActive ? ' is-active' : '') + (isExecuted ? ' is-executed' : '') + (isDimmed ? ' is-dimmed' : '') + (isClientData ? ' is-clientdata' : ''));
        g.setAttribute('data-id', n.id);
        g.setAttribute('data-role', n.role);
        const state = replay.states.get(n.id) || 'ready';
        g.setAttribute('data-state', state);
        g.setAttribute('aria-pressed', String(isSelected));
        g.style.setProperty('--node-selection-stroke', isLight ? '#0f172a' : '#ffffff');
        g.setAttribute('data-active', isActive ? 'true' : 'false');
        g.setAttribute('tabindex', '0');
        g.setAttribute('role', 'button');
        g.setAttribute('aria-label', `${{kind.label}} ${{nodeDisplayName(n)}}, ${{state}}, line ${{n.line || 'unknown'}}`);

        g.onclick = (e) => {{
          e.stopPropagation();
          if (n.type === 'module') {{
            toggleModule(n.module);
            return;
          }}
          if (e.detail >= 2) {{
            filterLineageForNode(n.id);
            return;
          }}
          selectNode(n.id);
        }};
        g.ondblclick = (e) => {{
          e.stopPropagation();
          if (n.type === 'module') {{
            toggleModule(n.module);
            return;
          }}
          filterLineageForNode(n.id);
        }};
        g.onkeydown = e => {{
          if (e.key === 'Enter' || e.key === ' ') {{
            e.preventDefault(); e.stopPropagation(); selectNode(n.id);
            document.querySelectorAll('.graph-node').forEach(el => {{ if (el.dataset.id === n.id) el.focus(); }});
          }}
        }};
        if (n.type === 'module') {{
          g.setAttribute('aria-expanded', 'false');
          g.setAttribute('aria-label', `Expand module ${{n.module}}`);
          g.onkeydown = e => {{ if (e.key === 'Enter' || e.key === ' ') {{ e.preventDefault(); e.stopPropagation(); toggleModule(n.module); }} }};
        }};
        g.onmouseenter = () => highlightDependencies(n.id);
        g.onmouseleave = () => resetHighlight();

        const role = n.role || n.type;
        const cardPath = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        cardPath.setAttribute('d', getNodeShapePath(n, p, nodeWidth, nodeHeight));

        const fillCol = reactiveStateColors[state];
        const defaultStroke = state === 'frozen'
          ? (isLight ? '#073859' : '#7dd3fc')
          : (isLight ? '#475569' : '#1e293b');
        const strokeCol = isSelected ? (isLight ? '#0f172a' : '#ffffff') : defaultStroke;
        const strokeW = isSelected ? '3' : '1.5';
        const filterVal = isSelected ? (isLight ? 'drop-shadow(0 0 8px rgba(2,132,199,0.35))' : 'drop-shadow(0 0 10px rgba(99,179,255,0.4))') : 'url(#card-shadow)';

        cardPath.setAttribute('fill', fillCol);
        cardPath.setAttribute('stroke', strokeCol);
        cardPath.setAttribute('stroke-width', strokeW);
        cardPath.setAttribute('stroke-linejoin', 'round');
        cardPath.setAttribute('stroke-linecap', 'round');
        cardPath.setAttribute('filter', filterVal);
        cardPath.setAttribute('class', 'node-card');
        g.appendChild(cardPath);

        const focusRing = cardPath.cloneNode(false);
        focusRing.setAttribute('class', 'node-focus-ring');
        focusRing.setAttribute('fill', 'none');
        focusRing.removeAttribute('filter');
        focusRing.setAttribute('aria-hidden', 'true');
        g.appendChild(focusRing);

        const textX = p.x - (nodeWidth / 2) + ((role === 'source' || n.type === 'input' || n.type === 'module') ? 22 : 36);

        const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        text.setAttribute('x', textX);
        text.setAttribute('y', p.y - 4);
        text.setAttribute('fill', state === 'frozen' ? '#ffffff' : '#0f172a');
        text.setAttribute('font-family', 'var(--mono)');
        text.setAttribute('font-size', '14px');
        text.setAttribute('font-weight', '700');
        text.innerHTML = graphNodeLabel(n);
        const title = document.createElementNS('http://www.w3.org/2000/svg', 'title');
        title.textContent = `${{nodeDisplayName(n)}} · ${{state}}${{n.line ? ' · line ' + n.line : ''}}`;
        g.appendChild(title);
        g.appendChild(text);

        const subText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        subText.setAttribute('x', textX);
        subText.setAttribute('y', p.y + 14);
        subText.setAttribute('fill', state === 'frozen' ? '#e2e8f0' : '#1e293b');
        subText.setAttribute('font-size', '12px');
        subText.textContent = n.type === 'module' ? `${{n.members.length}} nodes · click to expand` : `${{kind.label}} · ${{state}}`;
        g.appendChild(subText);

        const execCount = execCounts.get(n.id) || 0;
        if (execCount > 1) {{
          const badgeG = document.createElementNS('http://www.w3.org/2000/svg', 'g');
          badgeG.setAttribute('class', 'node-exec-badge');
          const badgeWidth = 34;
          const badgeHeight = 18;
          const hasRightChevron = (role === 'source' || n.type === 'input' || role === 'conductor' || n.type === 'calc');
          const badgeX = p.x + (nodeWidth / 2) - badgeWidth - (hasRightChevron ? 28 : 10);
          const badgeY = p.y - (nodeHeight / 2) - 9;

          const badgeRect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
          badgeRect.setAttribute('x', badgeX);
          badgeRect.setAttribute('y', badgeY);
          badgeRect.setAttribute('width', badgeWidth);
          badgeRect.setAttribute('height', badgeHeight);
          badgeRect.setAttribute('rx', '9');
          badgeRect.setAttribute('fill', isLight ? '#f1f5f9' : '#1e293b');
          badgeRect.setAttribute('stroke', isLight ? '#cbd5e1' : '#475569');
          badgeRect.setAttribute('stroke-width', '1.2');
          badgeRect.setAttribute('filter', 'drop-shadow(0 2px 4px rgba(0,0,0,0.18))');
          badgeG.appendChild(badgeRect);

          const badgeText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
          badgeText.setAttribute('x', badgeX + (badgeWidth / 2));
          badgeText.setAttribute('y', badgeY + 12);
          badgeText.setAttribute('text-anchor', 'middle');
          badgeText.setAttribute('fill', isLight ? '#475569' : '#94a3b8');
          badgeText.setAttribute('font-size', '10px');
          badgeText.setAttribute('font-weight', '700');
          badgeText.textContent = `${{execCount}}×`;
          badgeG.appendChild(badgeText);

          const badgeTitle = document.createElementNS('http://www.w3.org/2000/svg', 'title');
          badgeTitle.textContent = `Executed ${{execCount}} times during session`;
          badgeG.appendChild(badgeTitle);

          g.appendChild(badgeG);
        }}

        svg.appendChild(g);
      }});
    }}

    function updateEdgePulses(paths, representatives, events, previousStep) {{
      const layer = document.getElementById('graph-edge-pulses');
      if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {{
        layer.replaceChildren();
        return;
      }}
      const moving = new Set();
      for (const dot of Array.from(layer.children)) {{
        const key = dot.dataset.edge;
        if (paths.get(key) === dot.firstElementChild.getAttribute('path')) moving.add(key);
        else dot.remove();
      }}

      // A scrub can skip dependency events. Use the closest visible one to where it landed.
      const forward = currentStep > previousStep;
      const direction = forward ? -1 : 1;
      for (let step = currentStep; forward ? step > previousStep : step < previousStep; step += direction) {{
        const ev = events[step];
        if (!ev || ev.isolate || !['dependsOn', 'invalidate', 'invalidateStart', 'propagate'].includes(ev.action || ev.event)) continue;
        const from = representatives.get(ev.edge_from || ev.depOnReactId || ev.dependsOn);
        const to = representatives.get(ev.edge_to || ev.node_id || ev.reactId || ev.id);
        const key = JSON.stringify([from, to]);
        const path = paths.get(key);
        if (!path) continue;
        if (moving.has(key)) return;

        const dot = document.createElementNS(layer.namespaceURI, 'circle');
        dot.setAttribute('class', 'graph-edge-pulse');
        dot.setAttribute('r', '6');
        dot.dataset.edge = key;
        const motion = document.createElementNS(layer.namespaceURI, 'animateMotion');
        motion.setAttribute('path', path);
        motion.setAttribute('dur', '1.1s');
        motion.setAttribute('begin', 'indefinite');
        motion.addEventListener('endEvent', () => dot.remove(), {{ once: true }});
        dot.appendChild(motion);
        layer.appendChild(dot);
        motion.beginElement();
        return;
      }}
    }}

    function highlightDependencies(nodeId) {{
      if (focusedNodeId) return;
      document.querySelectorAll('.graph-edge').forEach(edge => {{
        const from = edge.getAttribute('data-from');
        const to = edge.getAttribute('data-to');
        if (from === nodeId || to === nodeId) {{
          edge.style.opacity = '1';
          edge.style.stroke = 'var(--accent)';
          edge.style.strokeWidth = '2.5px';
        }} else {{
          edge.style.opacity = '0.15';
        }}
      }});
    }}

    function resetHighlight() {{
      if (focusedNodeId) return;
      document.querySelectorAll('.graph-edge').forEach(edge => {{
        edge.style.removeProperty('opacity');
        edge.style.removeProperty('stroke');
        edge.style.removeProperty('stroke-width');
      }});
    }}

    function seekTo(step, fromVideo = false, mediaTime = null) {{
      const events = reactlogData.events || reactlogData.log || [];
      const previousStep = currentStep;
      currentStep = Math.max(0, Math.min(step, events.length - 1));
      document.getElementById('scrubber-range').value = currentStep;
      document.getElementById('step-display').textContent = `Step ${{currentStep}} / ${{Math.max(0, events.length - 1)}}`;

      document.querySelectorAll('.event-item').forEach(item => {{
        const stepNum = Number(item.getAttribute('data-step'));
        const isCur = stepNum === currentStep;
        item.classList.toggle('is-current', isCur);
        if (isCur) {{
          const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
          item.scrollIntoView({{ block: 'nearest', behavior: reduceMotion ? 'auto' : 'smooth' }});
        }}
      }});

      const ev = events[currentStep];
      if (!focusedNodeId && ev && (ev.node_id || ev.id)) {{
        const evNodeId = ev.node_id || ev.id;
        const lineageSet = getActiveLineageSet();
        if (!lineageSet || lineageSet.has(evNodeId)) {{
          selectedNodeId = evNodeId;
        }}
      }}
      renderInspector();
      renderGraph(previousStep);
      updateSourceHighlight();
      updateActionToast();
      updateFlushUI();

      const evTime = ev && (ev.time_sec !== undefined ? ev.time_sec : ev.time);
      const curSec = fromVideo && mediaTime !== null
        ? mediaTime
        : (evTime !== undefined ? evTime : 0);
      updateTraceTimelineScrubber(curSec);

      if (!fromVideo) {{
        const video = document.getElementById('session-video');
        if (video && evTime !== undefined && !isNaN(evTime)) {{
          try {{
            graphSeekTime = Math.max(0, evTime);
            video.currentTime = graphSeekTime;
          }} catch (e) {{}}
        }}
      }}
    }}

    function updateActionToast() {{
      const events = reactlogData.events || reactlogData.log || [];
      const ev = events[currentStep];
      const toast = document.getElementById('live-action-toast');
      if (!toast) return;

      const act = ev ? (ev.action || ev.event || '') : '';
      if (ev && (ev.phase === 'interaction' || !['define', 'analysisInit', 'createContext', 'sessionInit'].includes(act)) && (act === 'inputChange' || act === 'userClick' || act === 'userAction' || act === 'outputUpdated' || act === 'valueChange')) {{
        const evTime = ev.time_sec !== undefined ? ev.time_sec : ev.time;
        const timeStr = evTime !== undefined ? `[${{formatTime(evTime)}}] ` : '';
        toast.innerHTML = `${{ICONS.video}} ${{escapeHTML(timeStr)}}${{escapeHTML(formatEventDetails(ev) || act)}}`;
        toast.hidden = false;
      }} else {{
        toast.hidden = true;
      }}
    }}

    function setupVideoSync() {{
      const video = document.getElementById('session-video');
      if (!video) return;

      const btn = document.getElementById('btn-play');
      const syncStatus = document.getElementById('video-sync-status');

      const updatePlayButton = (playing) => {{
        if (!btn) return;
        btn.textContent = playing ? '❚❚ Pause' : '▶ Play';
        btn.setAttribute('aria-label', playing ? 'Pause recording' : 'Play recording');
        btn.title = playing ? 'Pause recording' : 'Play recording';
      }};

      const updateSyncStatus = (message) => {{
        if (syncStatus) syncStatus.textContent = `● ${{message}}`;
      }};

      const syncGraphToTime = (curSec) => {{
        // Paused graph stepping must keep the exact event when timestamps coincide.
        if (video.paused && graphSeekTime !== null && Math.abs(curSec - graphSeekTime) < 0.05) return;
        graphSeekTime = null;
        updateTraceTimelineScrubber(curSec);
        let matchIdx = 0;
        const events = reactlogData.events || reactlogData.log || [];
        for (let i = 0; i < events.length; i++) {{
          const ev = events[i];
          const t = ev.effective_time !== undefined ? ev.effective_time : ((ev.time_sec !== undefined ? ev.time_sec : ev.time) || 0);
          if (t <= curSec) matchIdx = i;
        }}
        if (matchIdx !== currentStep) {{
          seekTo(matchIdx, true, curSec);
        }}
      }};

      const stopFrameSync = () => {{
        if (videoFrameRequest === null) return;
        if (videoFrameRequestKind === 'video' && typeof video.cancelVideoFrameCallback === 'function') {{
          video.cancelVideoFrameCallback(videoFrameRequest);
        }} else if (videoFrameRequestKind === 'animation') {{
          cancelAnimationFrame(videoFrameRequest);
        }}
        videoFrameRequest = null;
        videoFrameRequestKind = null;
      }};

      const syncVideoFrame = (_now, metadata) => {{
        videoFrameRequest = null;
        videoFrameRequestKind = null;
        if (video.paused || video.ended) return;
        const mediaTime = metadata && Number.isFinite(metadata.mediaTime)
          ? metadata.mediaTime
          : video.currentTime;
        syncGraphToTime(mediaTime);
        requestNextFrame();
      }};

      const requestNextFrame = () => {{
        if (videoFrameRequest !== null || video.paused || video.ended) return;
        if (typeof video.requestVideoFrameCallback === 'function') {{
          videoFrameRequestKind = 'video';
          videoFrameRequest = video.requestVideoFrameCallback(syncVideoFrame);
        }} else {{
          videoFrameRequestKind = 'animation';
          videoFrameRequest = requestAnimationFrame((now) => syncVideoFrame(now, null));
        }}
      }};

      video.addEventListener('loadedmetadata', () => {{
        updateSyncStatus(`Paused at ${{formatTime(video.currentTime)}}`);
        if (video.duration && !isNaN(video.duration)) {{
          maxSessionDuration = Math.max(maxSessionDuration, video.duration);
          const totalDisplay = document.getElementById('trace-total-time');
          if (totalDisplay) totalDisplay.textContent = formatTime(maxSessionDuration);
          initTraceTimeline();
        }}
      }});

      video.addEventListener('play', () => {{
        graphSeekTime = null;
        isPlaying = true;
        updatePlayButton(true);
        updateSyncStatus('Following recording');
        requestNextFrame();
      }});

      video.addEventListener('pause', () => {{
        isPlaying = false;
        stopFrameSync();
        updatePlayButton(false);
        updateSyncStatus(`Paused at ${{formatTime(video.currentTime)}}`);
      }});

      video.addEventListener('ended', () => {{
        isPlaying = false;
        stopFrameSync();
        updatePlayButton(false);
        updateSyncStatus('Recording complete');
      }});

      video.addEventListener('timeupdate', () => syncGraphToTime(video.currentTime));
      video.addEventListener('seeked', () => syncGraphToTime(video.currentTime));
    }}

    function updateSourceHighlight() {{
      const events = reactlogData.events || reactlogData.log || [];
      const ev = events[currentStep];
      const isMark = ['mark', 'userMark'].includes(ev?.action || ev?.event);
      const isError = isErrorEvent(ev);
      const eventNode = nodeIndex.get(ev?.node_id || ev?.reactId || ev?.id);
      const selected = nodeIndex.get(selectedNodeId);
      const target = ev?.line ? ev : (isError ? eventNode : (selected?.line ? selected : eventNode));
      const panel = document.getElementById('source-panel');
      panel.querySelector('.source-line.is-active')?.classList.remove('is-active', 'is-mark', 'is-error');
      if (!Number.isInteger(target?.line)) return;
      if (target.source_file && target.source_file !== displayedSourceFile) {{
        showSourceFile(target.source_file);
        if (target.source_file !== displayedSourceFile) return;
      }}
      const line = panel.querySelector(`.source-line[data-line="${{target.line}}"]`);
      if (!line) return;
      line.classList.add('is-active');
      if (isMark && target === ev) line.classList.add('is-mark');
      if (isError) line.classList.add('is-error');
      if (!panel.hidden) {{
        const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        line.scrollIntoView({{ block: 'center', behavior: reduceMotion ? 'auto' : 'smooth' }});
      }}
    }}

    function togglePlay() {{
      const video = document.getElementById('session-video');
      if (video) {{
        if (video.paused) {{
          const atVideoEnd = video.ended || (
            Number.isFinite(video.duration)
            && video.duration > 0
            && video.currentTime >= video.duration - 0.05
          );
          if (atVideoEnd) {{
            video.currentTime = 0;
            seekTo(0, true);
          }}
          video.play().catch(() => {{}});
        }} else {{
          video.pause();
        }}
        return;
      }}

      const events = reactlogData.events || reactlogData.log || [];
      isPlaying = !isPlaying;
      const btn = document.getElementById('btn-play');
      if (btn) {{
        btn.textContent = isPlaying ? '❚❚ Pause' : '▶ Play';
        btn.setAttribute('aria-label', isPlaying ? 'Pause timeline' : 'Play timeline');
      }}

      if (isPlaying) {{
        if (currentStep >= events.length - 1) currentStep = 0;
        playTimer = setInterval(() => {{
          if (currentStep < events.length - 1) {{
            seekTo(currentStep + 1);
          }} else {{
            togglePlay();
          }}
        }}, 600);
      }} else {{
        clearInterval(playTimer);
      }}
    }}

    function stepForward() {{ seekTo(currentStep + 1); }}
    function stepBack() {{ seekTo(currentStep - 1); }}
    function resetTimeline() {{ seekTo(0); }}

    function nodeSearchScore(node, query) {{
      const moduleOnly = query.startsWith('module:');
      if (moduleOnly) {{
        const needle = query.slice(7).trim().toLowerCase();
        const module = String(node.module || '__root__').toLowerCase();
        return !needle || module.includes(needle) ? 0 : Infinity;
      }}
      const idOnly = query.startsWith('id:');
      const needle = (idOnly ? query.slice(3) : query).trim().toLowerCase();
      if (!needle) return 0;
      if (idOnly) {{
        const nid = String(node.id || '').toLowerCase();
        const nlabel = String(node.label || '').toLowerCase();
        const nname = String(node.name || '').toLowerCase();
        if (nid === needle || nid.endsWith(':' + needle) || nlabel === needle || nname === needle) return 0;
        if (nid.includes(needle) || nlabel.includes(needle) || nname.includes(needle)) return 1;
        return Infinity;
      }}
      const fields = [node.id, node.label, node.name, node.type, node.role, node.module];
      let best = Infinity;
      fields.forEach(field => {{
        const value = String(field || '').toLowerCase();
        if (value === needle) best = Math.min(best, 0);
        else if (value.includes(needle)) best = Math.min(best, 1 + value.indexOf(needle) / Math.max(1, value.length));
        else {{
          let pos = 0;
          for (const char of value) if (char === needle[pos]) pos++;
          if (pos === needle.length) best = Math.min(best, 3 + value.length / 1000);
        }}
      }});
      return best;
    }}

    function closeSearchChoices() {{
      document.getElementById('search-results').hidden = true;
      document.getElementById('search-input').setAttribute('aria-expanded', 'false');
      document.querySelector('.search-toggle').setAttribute('aria-expanded', 'false');
    }}

    function toggleSearchChoices() {{
      if (!document.getElementById('search-results').hidden) closeSearchChoices();
      else {{ handleSearch(document.getElementById('search-input').value, false); document.getElementById('search-input').focus(); }}
    }}

    function clearSearchFilter() {{
      selectedSearchNodeId = null;
      focusedNodeId = null;
      selectedNodeId = null;
      searchQuery = '';
      document.getElementById('search-input').value = '';
      syncSearchClearButton();
      closeSearchChoices();
      refreshExploration();
      renderInspector();
      updateSourceHighlight();
      updateTraceTimelineScrubber(getCurrentStepTime());
      fitGraph();
    }}

    function handleSearch(q, isTyping = true) {{
      const rawQuery = (q || '').trim().toLowerCase();
      if (isTyping) {{
        searchQuery = rawQuery;
        if (!rawQuery) {{
          selectedSearchNodeId = null;
          focusedNodeId = null;
          selectedNodeId = null;
        }} else if (selectedSearchNodeId) {{
          const selNode = nodeIndex.get(selectedSearchNodeId);
          if (!selNode || rawQuery !== nodeDisplayName(selNode).toLowerCase()) {{
            selectedSearchNodeId = null;
            focusedNodeId = null;
            selectedNodeId = null;
          }}
        }}
      }} else {{
        searchQuery = rawQuery;
      }}
      syncSearchClearButton();
      const dropdownQuery = (!isTyping && selectedSearchNodeId) ? '' : searchQuery;
      const results = document.getElementById('search-results');
      results.replaceChildren();
      results.hidden = false;
      document.getElementById('search-input').setAttribute('aria-expanded', 'true');
      document.querySelector('.search-toggle').setAttribute('aria-expanded', 'true');
      {{
        const matches = filterItems(
          filterItems(reactlogData.nodes || [], n => dropdownQuery || n.id === selectedSearchNodeId || ((!hideClientData || !isClientDataNode(n)) && (!changedNodesOnly || !changedNodeIds || changedNodeIds.has(n.id)))).map(n => ({{ node: n, score: dropdownQuery ? nodeSearchScore(n, dropdownQuery) : (n.id === selectedSearchNodeId ? -1 : 0) }})),
          m => Number.isFinite(m.score)
        ).sort((a, b) => a.score - b.score);
        const summary = document.createElement('div');
        summary.className = 'search-summary';
        summary.setAttribute('role', 'status');
        summary.textContent = matches.length
          ? `${{matches.length}} matches${{matches.length > 50 ? ' · showing first 50' : ''}}${{selectedSearchNodeId ? ' · click checked item to clear' : ' · ↓ to select'}}`
          : '0 matches. Try a node name or module:name. Press Escape to clear.';
        results.appendChild(summary);
        matches.slice(0, 50).forEach(({{node}}) => {{
          const isSelected = selectedSearchNodeId === node.id;
          const button = document.createElement('button');
          button.type = 'button';
          button.className = 'search-option' + (isSelected ? ' is-selected' : '');
          button.setAttribute('role', 'option');
          button.setAttribute('aria-selected', String(isSelected));
          const kind = nodeKind(node);
          const checkSvg = '<span class="search-check" aria-hidden="true"><svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.75" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg></span>';
          button.innerHTML = '<span class="search-item-main">' + checkSvg + '<span><b>' + nodeLabelHTML(node) + '</b></span></span><span style="color:var(--text-muted);font-size:0.68rem;flex-shrink:0;">' + escapeHTML(kind.label) + '</span>';
          button.onclick = () => {{
            if (isSelected) {{
              clearSearchFilter();
              return;
            }}
            filterLineageForNode(node.id);
          }};
          results.appendChild(button);
        }});
      }}
      refreshExploration();
      fitGraph();
    }}

    function resetGraphView() {{
      toggleSettingsMenu(false);
      selectedNodeId = null;
      focusedNodeId = null;
      selectedSearchNodeId = null;
      searchQuery = '';
      selectedStageFilter = null;
      hideClientData = false;
      changedNodesOnly = false;
      document.getElementById('search-input').value = '';
      closeSearchChoices();
      activeRoles = new Set(['source', 'conductor', 'observer', 'effect', 'output']);
      if (currentViewMode === 'flush') setViewMode('full');
      refreshExploration();
      renderInspector();
      updateTraceTimelineScrubber(getCurrentStepTime());
      fitGraph();
    }}

    function handleSearchKey(event) {{
      const input = document.getElementById('search-input');
      const results = document.getElementById('search-results');
      const buttons = Array.from(results.querySelectorAll('button'));
      if (event.key === 'Escape') {{
        event.preventDefault();
        input.value = '';
        handleSearch('');
        input.focus();
        closeSearchChoices();
      }} else if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {{
        if (results.hidden || !buttons.length) return;
        event.preventDefault();
        const index = buttons.indexOf(document.activeElement);
        const next = event.key === 'ArrowDown' ? (index + 1) % buttons.length : (index <= 0 ? buttons.length - 1 : index - 1);
        buttons[next].focus();
      }} else if (event.key === 'Enter' && event.target === input && !results.hidden && buttons.length) {{
        event.preventDefault();
        buttons[0].click();
      }}
    }}

    function setupPanZoom() {{
      const svg = document.getElementById('reactlog-svg');
      if (!svg) return;
      if (svg.dataset.panZoomBound) return;
      svg.dataset.panZoomBound = 'true';
      svg.addEventListener('mousedown', e => {{
        if (e.target.closest('.graph-node, .module-box')) return;
        isPanning = true;
        startPan = {{ x: e.clientX - panOffset.x, y: e.clientY - panOffset.y }};
      }});
      window.addEventListener('mousemove', e => {{
        if (!isPanning) return;
        panOffset = {{ x: e.clientX - startPan.x, y: e.clientY - startPan.y }};
        applyZoom();
      }});
      window.addEventListener('mouseup', () => isPanning = false);
      svg.addEventListener('wheel', e => {{
        e.preventDefault();
        const delta = e.deltaY > 0 ? 0.9 : 1.1;
        const rect = svg.getBoundingClientRect();
        zoomAt(delta, e.clientX - rect.left, e.clientY - rect.top);
      }});
    }}

    function applyZoom() {{
      const g = document.getElementById('viewport-g');
      if (g) g.setAttribute('transform', `translate(${{panOffset.x}}, ${{panOffset.y}}) scale(${{zoomLevel}})`);
    }}

    function zoomAt(factor, x, y) {{
      const svg = document.getElementById('reactlog-svg');
      x = x ?? svg.clientWidth / 2;
      y = y ?? svg.clientHeight / 2;
      const next = Math.max(Math.min(0.001, zoomLevel), Math.min(2.5, zoomLevel * factor));
      const ratio = next / zoomLevel;
      panOffset = {{ x: x - (x - panOffset.x) * ratio, y: y - (y - panOffset.y) * ratio }};
      zoomLevel = next;
      applyZoom();
    }}
    function zoomIn() {{ zoomAt(1.2); }}
    function zoomOut() {{ zoomAt(0.8); }}
    function resetZoom() {{ zoomLevel = 1; panOffset = {{ x: 0, y: 0 }}; applyZoom(); }}
    function fitGraph() {{
      const svg = document.getElementById('reactlog-svg');
      const g = document.getElementById('graph-content');
      if (!svg || !g || !g.childElementCount) return;
      const box = g.getBBox();
      const width = svg.clientWidth, height = svg.clientHeight;
      if (!width || !height || !box.width || !box.height) return;
      zoomLevel = Math.min(1, Math.max(1, width - 48) / box.width, Math.max(1, height - 96) / box.height);
      panOffset = {{ x: (width - box.width * zoomLevel) / 2 - box.x * zoomLevel,
                     y: (height - box.height * zoomLevel) / 2 - box.y * zoomLevel }};
      applyZoom();
    }}
    function isFullscreen() {{
      return !!(document.fullscreenElement || document.webkitFullscreenElement || document.mozFullScreenElement || document.msFullscreenElement);
    }}
    function updateFullscreenButton() {{
      const btn = document.getElementById('btn-fullscreen');
      if (!btn) return;
      const fs = isFullscreen();
      btn.setAttribute('aria-label', fs ? 'Exit full screen' : 'Full screen');
      btn.title = fs ? 'Exit full screen' : 'Full screen';
      btn.innerHTML = fs
        ? '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 3v3a2 2 0 0 1-2 2H3"/><path d="M21 8h-3a2 2 0 0 1-2-2V3"/><path d="M3 16h3a2 2 0 0 1 2 2v3"/><path d="M16 21v-3a2 2 0 0 1 2-2h3"/></svg>'
        : '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 3H5a2 2 0 0 0-2 2v3"/><path d="M21 8V5a2 2 0 0 0-2-2h-3"/><path d="M3 16v3a2 2 0 0 0 2 2h3"/><path d="M16 21h3a2 2 0 0 0 2-2v-3"/></svg>';
    }}
    function toggleFullscreen() {{
      if (!isFullscreen()) {{
        const root = document.documentElement;
        if (root.requestFullscreen) {{
          root.requestFullscreen().catch(() => {{}});
        }} else if (root.webkitRequestFullscreen) {{
          root.webkitRequestFullscreen();
        }} else if (root.msRequestFullscreen) {{
          root.msRequestFullscreen();
        }}
      }} else {{
        if (document.exitFullscreen) {{
          document.exitFullscreen().catch(() => {{}});
        }} else if (document.webkitExitFullscreen) {{
          document.webkitExitFullscreen();
        }} else if (document.msExitFullscreen) {{
          document.msExitFullscreen();
        }}
      }}
    }}
    document.addEventListener('fullscreenchange', () => {{
      updateFullscreenButton();
      setTimeout(fitGraph, 100);
    }});
    document.addEventListener('webkitfullscreenchange', () => {{
      updateFullscreenButton();
      setTimeout(fitGraph, 100);
    }});

    function loadReactlogObject(loadedData) {{
      let normalized = loadedData;
      if (Array.isArray(loadedData) || (loadedData && (!loadedData.nodes || !loadedData.events))) {{
        const rawEvents = Array.isArray(loadedData) ? loadedData : (loadedData.log || loadedData.events || loadedData.entries || []);
        const nodesMap = Object.create(null);
        const edgesSet = new Set();
        const normEvents = [];
        let sIdx = 0;

        let minEpochTime = Infinity;
        let isEpoch = false;
        rawEvents.forEach(item => {{
          const t = Number(item.time || item.time_sec || (Number(item.timestamp || 0) / 1000.0) || 0);
          if (t > 100000) isEpoch = true;
          if (t > 0 && t < minEpochTime) minEpochTime = t;
        }});
        const baseEpoch = isEpoch && isFinite(minEpochTime) ? minEpochTime : 0;

        rawEvents.forEach(item => {{
          const act = item.action || item.event || '';
          const nid = item.reactId || item.node_id || item.id;
          if (!nid) return;
          const rawLbl = item.label || item.node_label;
          const existing = nodesMap[nid];
          if (!existing || act === 'define' || (rawLbl && rawLbl !== nid && (!existing.label || existing.label === nid))) {{
            const ntype = item.type || item.node_type || existing?.type || 'calc';
            let role = 'conductor';
            let ctype = String(ntype).toLowerCase();
            if (['observable', 'reactive'].includes(ctype)) ctype = 'calc';
            if (['input', 'reactiveval', 'reactivevalueskey', 'reactivevaluesnames', 'reactivevaluesaslist'].includes(ctype) || String(nid).startsWith('input:') || String(nid).startsWith('input$')) {{
              role = 'source'; ctype = 'input';
            }} else if (['observer', 'output', 'effect'].includes(ctype) || String(nid).startsWith('output:') || String(nid).startsWith('output$') || String(nid).startsWith('effect:')) {{
              role = 'observer'; ctype = 'output';
            }}
            const resolvedLbl = (rawLbl && rawLbl !== nid) ? String(rawLbl) : String(existing?.label || rawLbl || nid);
            const fallbackName = String(nid).includes(':') ? String(nid).split(':')[1] : (String(nid).includes('$') ? String(nid).split('$')[1] : (resolvedLbl !== String(nid) ? resolvedLbl : String(nid)));
            nodesMap[nid] = {{
              id: nid,
              name: fallbackName,
              type: ctype,
              role: role,
              label: resolvedLbl,
              line: item.line ?? existing?.line,
              module: item.module ?? existing?.module,
              render_type: item.render_type ?? existing?.render_type,
              source_file: item.source_file ?? existing?.source_file
            }};
          }}
        }});

        const resolveNodeLabel = (id, fallback) => {{
          const sid = String(id || '');
          const mapped = String(nodesMap[sid]?.label || '');
          const fb = String(fallback || '');
          if (mapped && mapped !== sid) return mapped;
          if (fb && fb !== sid) return fb;
          return mapped || fb || sid;
        }};

        rawEvents.forEach(item => {{
          const act = item.action || item.event || '';
          const nid = item.reactId || item.node_id || item.id;
          const lbl = resolveNodeLabel(nid, item.label || item.node_label);
          const ntype = item.type || item.node_type || 'calc';
          const depFrom = item.depOnReactId || item.dependsOn || item.edge_from;
          const depTo = nid || item.reactId || item.edge_to;
          const depFromLbl = depFrom ? resolveNodeLabel(depFrom) : '';
          const depToLbl = depTo ? resolveNodeLabel(depTo, lbl) : lbl;
          const rawT = Number(item.time || item.time_sec || (Number(item.timestamp || 0) / 1000.0) || 0);
          const tSec = Math.max(0, baseEpoch > 0 ? (rawT - baseEpoch) : rawT);
          const tMs = Number(item.timestamp || (tSec * 1000));
          const prov = item.provenance || (['valueChange', 'inputChange', 'userClick', 'userAction'].includes(act) ? 'observed' : 'inferred');
          const phase = item.phase || (['define', 'analysisInit', 'createContext', 'sessionInit'].includes(act) ? 'init' : 'interaction');

          if (act === 'dependsOn' && depFrom && depTo) {{
            edgesSet.add(`${{depFrom}}==>${{depTo}}`);
          }}

          let details = item.details;
          if (!details) {{
            if (act === 'define') details = `Defined reactive node '${{lbl}}'`;
            else if (act === 'dependsOn') details = `Dependency: '${{depFromLbl}}' used by '${{depToLbl}}'`;
            else if (act === 'dependsOnRemove') details = `Removed dependency: '${{depFromLbl}}' used by '${{depToLbl}}'`;
            else if (act === 'invalidate' || act === 'invalidateEnd') details = `Invalidated '${{lbl}}'`;
            else if (act === 'invalidateStart') details = `Invalidating '${{lbl}}'`;
            else if (act === 'valueChange' || act === 'inputChange') details = `Value change for '${{lbl}}': ${{item.value !== undefined ? String(item.value) : ''}}`;
            else if (act === 'enter' || act === 'wouldEvaluate') details = `Evaluating '${{lbl}}'`;
            else if (act === 'exit' || act === 'ordered') details = `Completed evaluation of '${{lbl}}'`;
            else if (act === 'idle' || act === 'queueEmpty') details = 'Idle';
            else details = lbl ? `Event '${{act}}' on '${{lbl}}'` : `Event '${{act}}'`;
          }}

          normEvents.push({{
            step: sIdx,
            action: act,
            event: act,
            id: nid,
            reactId: nid,
            node_id: nid,
            label: lbl,
            node_label: lbl,
            type: ntype,
            node_type: ntype,
            status: item.status || (act === 'define' ? 'discovered' : (act === 'invalidate' ? 'affected' : 'scheduled')),
            phase: phase,
            provenance: prov,
            time: tSec,
            time_sec: tSec,
            timestamp: tMs,
            value: item.value !== undefined ? String(item.value) : null,
            depOnReactId: depFrom,
            edge_from: depFrom,
            edge_to: depTo,
            isolate: Boolean(item.isolate),
            details: details
          }});
          sIdx++;
        }});

        const finalNodes = Object.values(nodesMap);
        const finalEdges = Array.from(edgesSet).map(e => {{
          const parts = e.split('==>');
          return {{ from: parts[0], to: parts[1] }};
        }});

        normalized = {{
          success: true,
          version: loadedData.version || "1.0",
          session: loadedData.session || "default",
          nodes: finalNodes,
          edges: finalEdges,
          events: normEvents,
          log: normEvents,
          summary: `Loaded Reactlog: ${{finalNodes.length}} nodes, ${{finalEdges.length}} edges, ${{normEvents.length}} log events`
        }};
      }}

      Object.assign(reactlogData, normalized);
      document.getElementById('graph-edge-pulses').replaceChildren();
      selectedNodeId = null;
      focusedNodeId = null;
      collapsedModules.clear();
      graphSeekTime = null;
      currentStep = 0;
      searchQuery = '';
      selectedStageFilter = null;
      document.getElementById('search-input').value = '';
      closeSearchChoices();
      activeRoles = new Set(['source', 'conductor', 'observer', 'effect', 'output']);
      hideClientData = true;
      changedNodesOnly = true;
      eventListScope = null;
      init();
      renderGraph();
    }}

    function handleReactlogFileUpload(e) {{
      const file = e.target.files && e.target.files[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = (evt) => {{
        try {{
          const parsed = JSON.parse(evt.target.result);
          loadReactlogObject(parsed);
        }} catch (err) {{
          alert('Error parsing JSON file: ' + err.message);
        }}
      }};
      reader.readAsText(file);
    }}

    document.addEventListener('keydown', (e) => {{
      const tag = (e.target && e.target.tagName) ? e.target.tagName.toLowerCase() : '';
      const isInput = tag === 'input' || tag === 'textarea' || tag === 'select' || (e.target && e.target.isContentEditable);

      if (isInput) {{
        if (e.key === 'Escape') {{
          const modal = document.getElementById('shortcuts-modal');
          if (modal && !modal.hidden) {{
            toggleShortcutsModal();
            e.preventDefault();
            return;
          }}
          const settingsMenu = document.getElementById('settings-menu');
          if (settingsMenu && !settingsMenu.hidden) {{
            toggleSettingsMenu(false);
            e.preventDefault();
            return;
          }}
        }}
        return;
      }}

      if (e.key === 'Escape') {{
        const modal = document.getElementById('shortcuts-modal');
        if (modal && !modal.hidden) {{
          toggleShortcutsModal();
          e.preventDefault();
          return;
        }}
        const settingsMenu = document.getElementById('settings-menu');
        if (settingsMenu && !settingsMenu.hidden) {{
          toggleSettingsMenu(false);
          e.preventDefault();
          return;
        }}
        if (selectedNodeId) {{
          clearNodeSelection();
          e.preventDefault();
          return;
        }}
      }}

      if ((e.shiftKey && e.key === 'ArrowLeft') || e.key === '[') {{
        e.preventDefault();
        prevFlush();
      }} else if ((e.shiftKey && e.key === 'ArrowRight') || e.key === ']') {{
        e.preventDefault();
        nextFlush();
      }} else if (e.altKey && (e.key === 'ArrowLeft' || e.key === 'ArrowRight')) {{
        e.preventDefault();
        seekTimelineStop('output', e.key === 'ArrowLeft' ? -1 : 1);
      }} else if (e.altKey && (e.key === 'ArrowUp' || e.key === 'ArrowDown')) {{
        e.preventDefault();
        seekTimelineStop('mark', e.key === 'ArrowUp' ? -1 : 1);
      }} else if (e.key === 'f' || e.key === 'F') {{
        e.preventDefault();
        setViewMode(currentViewMode === 'flush' ? 'full' : 'flush');
      }} else if (e.key === 'ArrowLeft' || e.key === 'h') {{
        e.preventDefault();
        stepBack();
      }} else if (e.key === 'ArrowRight' || e.key === 'l') {{
        e.preventDefault();
        stepForward();
      }} else if (e.key === 'ArrowUp' || e.key === 'k') {{
        e.preventDefault();
        prevAction();
      }} else if (e.key === 'ArrowDown' || e.key === 'j') {{
        e.preventDefault();
        nextAction();
      }} else if (e.key === ' ' || e.code === 'Space') {{
        e.preventDefault();
        togglePlay();
      }} else if (e.key === 'Home') {{
        e.preventDefault();
        seekTo(0);
      }} else if (e.key === 'End') {{
        e.preventDefault();
        const evs = reactlogData.events || reactlogData.log || [];
        seekTo(Math.max(0, evs.length - 1));
      }} else if (e.key === '?') {{
        e.preventDefault();
        toggleShortcutsModal();
      }}
    }});

    window.addEventListener('DOMContentLoaded', () => {{
      init();
      new ResizeObserver(() => fitGraph()).observe(document.getElementById('graph-container'));
    }});
  </script>
  <div id="shortcuts-modal" class="modal-backdrop" hidden onclick="if(event.target===this)toggleShortcutsModal()">
    <div class="modal-dialog" role="dialog" aria-labelledby="shortcuts-modal-title" aria-modal="true">
      <div class="modal-header">
        <h2 class="modal-title" id="shortcuts-modal-title">Keyboard Navigation Shortcuts</h2>
        <button class="modal-close-btn" onclick="toggleShortcutsModal()" aria-label="Close shortcuts dialog">✕</button>
      </div>
      <table class="shortcuts-table">
        <tbody>
          <tr><td><span class="shortcut-key">Shift+←</span> / <span class="shortcut-key">Shift+→</span></td><td>Jump to previous / next idle</td></tr>
          <tr><td><span class="shortcut-key">Alt+←</span> / <span class="shortcut-key">Alt+→</span></td><td>Previous / next output calculation</td></tr>
          <tr><td><span class="shortcut-key">Alt+↑</span> / <span class="shortcut-key">Alt+↓</span></td><td>Previous / next user mark</td></tr>
          <tr><td><span class="shortcut-key">F</span></td><td>Toggle current activity view</td></tr>
          <tr><td><span class="shortcut-key">←</span> or <span class="shortcut-key">h</span></td><td>Step backward one event</td></tr>
          <tr><td><span class="shortcut-key">→</span> or <span class="shortcut-key">l</span></td><td>Step forward one event</td></tr>
          <tr><td><span class="shortcut-key">↑</span> or <span class="shortcut-key">k</span></td><td>Jump to previous action burst</td></tr>
          <tr><td><span class="shortcut-key">↓</span> or <span class="shortcut-key">j</span></td><td>Jump to next action burst</td></tr>
          <tr><td><span class="shortcut-key">Space</span></td><td>Play / Pause timeline playback</td></tr>
          <tr><td><span class="shortcut-key">Home</span> / <span class="shortcut-key">End</span></td><td>Jump to start / end of timeline</td></tr>
          <tr><td><span class="shortcut-key">Esc</span></td><td>Close dialog / clear node selection</td></tr>
          <tr><td><span class="shortcut-key">?</span></td><td>Toggle this shortcuts dialog</td></tr>
        </tbody>
      </table>
    </div>
  </div>
</body>
</html>
"""
