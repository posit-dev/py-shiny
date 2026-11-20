from __future__ import annotations

import ast
import asyncio
import concurrent.futures
import copy
import inspect
import json
import os
import shutil
import sys
import tempfile
import time
from collections import deque
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, cast

from ._reactlog_format import TRACE_VERSION


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
    elif event in ("propagate", "invalidate", "invalidateStart"):
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


def _mark_event(
    *, step: int, label: str, timestamp: int, time_sec: float, session: str
) -> Dict[str, Any]:
    """A timeline bookmark event, shared by generated and loaded reactlogs."""
    return _make_event(
        step=step,
        event="userMark",
        action="userMark",
        phase="interaction",
        provenance="observed",
        node_id=None,
        node_label=f"🔖 {label}",
        node_type="mark",
        status="active",
        timestamp=timestamp,
        time_sec=time_sec,
        details=f"User mark: {label}",
        session=session,
    )


def _mark_wave(*, label: str, time_sec: float, step: int, index: int) -> Dict[str, Any]:
    """A timeline bookmark wave, shared by generated and loaded reactlogs."""
    return {
        "action_id": f"mark-{index}",
        "index": index,
        "is_init": False,
        "is_mark": True,
        "start_time": time_sec,
        "end_time": time_sec,
        "start_step": step,
        "end_step": step,
        "trigger": f"Bookmark: {label}",
        "trigger_label": f"🔖 {label}",
        "short_label": f"🔖 {label[:20]}",
        "human_action": f"Mark: {label}",
        "trigger_node_id": "",
        "trigger_value": None,
        "invalidated_nodes": [],
        "inferred_executions": [],
        "observed_executions": [],
        "observed_outputs": [],
    }


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
            _mark_event(
                step=cur_step,
                label=mark_label,
                timestamp=mark_ms,
                time_sec=mark_time,
                session=session,
            )
        )
        filename = m.get("source_file")
        if isinstance(filename, str):
            source_file = source_files.get(Path(filename).resolve())
            if source_file:
                events[-1].update(source_file=source_file, line=m.get("line"))
        action_waves.append(
            _mark_wave(
                label=mark_label,
                time_sec=mark_time,
                step=cur_step,
                index=len(action_waves),
            )
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
            "trace_version": TRACE_VERSION,
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
        "trace_version": TRACE_VERSION,
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
