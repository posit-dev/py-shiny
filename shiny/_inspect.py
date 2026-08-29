from __future__ import annotations

import ast
import asyncio
import concurrent.futures
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


class GraphVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.inputs: Dict[str, int] = {}
        self.calcs: Dict[str, Dict[str, Any]] = {}
        self.outputs: Dict[str, Dict[str, Any]] = {}
        self.effects: Dict[str, Dict[str, Any]] = {}
        self.current_calc: Optional[str] = None
        self.current_output: Optional[str] = None
        self.current_effect: Optional[str] = None
        self.isolated_depth: int = 0

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
        func_name = ""
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                func_name = f"{node.func.value.id}.{node.func.attr}"

        if (
            func_name.startswith("ui.input_")
            and node.args
            and isinstance(node.args[0], ast.Constant)
            and isinstance(node.args[0].value, str)
        ):
            input_id = node.args[0].value
            if input_id not in self.inputs:
                self.inputs[input_id] = node.lineno

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

        if self.isolated_depth == 0:
            if (
                isinstance(node.func, ast.Attribute)
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "input"
            ):
                target_input = node.func.attr
                if self.current_output and self.current_output in self.outputs:
                    self.outputs[self.current_output]["deps"].add(target_input)
                elif self.current_effect and self.current_effect in self.effects:
                    self.effects[self.current_effect]["deps"].add(target_input)
                elif self.current_calc and self.current_calc in self.calcs:
                    self.calcs[self.current_calc]["deps"].add(target_input)

            if isinstance(node.func, ast.Name):
                called_name = node.func.id
                if self.current_output and self.current_output in self.outputs:
                    self.outputs[self.current_output]["calc_deps"].add(called_name)
                elif self.current_effect and self.current_effect in self.effects:
                    self.effects[self.current_effect]["calc_deps"].add(called_name)
                elif self.current_calc and self.current_calc in self.calcs:
                    self.calcs[self.current_calc]["calc_deps"].add(called_name)

        self.generic_visit(node)

    def _get_decorator_name(self, d: ast.AST) -> str:
        if isinstance(d, ast.Call):
            d = d.func
        if isinstance(d, ast.Name):
            return d.id
        elif isinstance(d, ast.Attribute) and isinstance(d.value, ast.Name):
            return f"{d.value.id}.{d.attr}"
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
            if "event" in d_name:
                has_event_decorator = True
                inp_d, c_d = self._extract_event_triggers(d)
                event_input_deps.update(inp_d)
                event_calc_deps.update(c_d)

        is_effect = any("effect" in d or "Effect" in d for d in decorators)
        is_render = any(
            d.startswith("render.") or d.startswith("render_") for d in decorators
        )
        is_calc = (
            any(("calc" in d or "Calc" in d or "event" in d) for d in decorators)
            and not is_effect
            and not is_render
        )

        prev_out = self.current_output
        prev_effect = self.current_effect
        prev_calc = self.current_calc

        if is_render:
            self.current_output = node.name
            self.outputs[node.name] = {
                "line": node.lineno,
                "deps": set(event_input_deps),
                "calc_deps": set(event_calc_deps),
                "is_async": isinstance(node, ast.AsyncFunctionDef),
            }
        elif is_effect:
            self.current_effect = node.name
            self.effects[node.name] = {
                "line": node.lineno,
                "deps": set(event_input_deps),
                "calc_deps": set(event_calc_deps),
                "is_async": isinstance(node, ast.AsyncFunctionDef),
            }
        elif is_calc:
            self.current_calc = node.name
            self.calcs[node.name] = {
                "line": node.lineno,
                "deps": set(event_input_deps),
                "calc_deps": set(event_calc_deps),
                "is_async": isinstance(node, ast.AsyncFunctionDef),
            }

        if has_event_decorator:
            self.isolated_depth += 1

        for stmt in node.body:
            self.visit(stmt)

        if has_event_decorator:
            self.isolated_depth -= 1

        self.current_output = prev_out
        self.current_effect = prev_effect
        self.current_calc = prev_calc

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._handle_func_def(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._handle_func_def(node)


def inspect_reactive_graph(code: str) -> Dict[str, Any]:
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return {
            "success": False,
            "error": f"SyntaxError: {e.msg}",
            "nodes": [],
            "edges": [],
            "summary": "Syntax error in source code",
        }

    visitor = GraphVisitor()
    visitor.visit(tree)

    known_calcs = set(visitor.calcs.keys())

    referenced_inputs: Set[str] = set()
    for meta in visitor.outputs.values():
        referenced_inputs.update(meta["deps"])
    for meta in visitor.effects.values():
        referenced_inputs.update(meta["deps"])
    for meta in visitor.calcs.values():
        referenced_inputs.update(meta["deps"])

    all_inputs = set(visitor.inputs.keys()) | referenced_inputs

    nodes: List[Dict[str, Any]] = []
    for inp in sorted(all_inputs):
        is_declared = inp in visitor.inputs
        line = visitor.inputs.get(inp)
        nodes.append(
            {
                "id": f"input:{inp}",
                "name": inp,
                "type": "input",
                "role": "source",
                "label": f"input.{inp}",
                "line": line,
                "declaration": "declared" if is_declared else "unresolved",
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
                "line": meta["line"],
            }
        )

    edges: List[Dict[str, str]] = []
    for out_name, meta in visitor.outputs.items():
        for dep in sorted(meta["deps"]):
            edges.append({"from": f"input:{dep}", "to": f"output:{out_name}"})
        for cdep in sorted(meta["calc_deps"]):
            if cdep in known_calcs:
                edges.append({"from": f"calc:{cdep}", "to": f"output:{out_name}"})

    for eff_name, meta in visitor.effects.items():
        for dep in sorted(meta["deps"]):
            edges.append({"from": f"input:{dep}", "to": f"effect:{eff_name}"})
        for cdep in sorted(meta["calc_deps"]):
            if cdep in known_calcs:
                edges.append({"from": f"calc:{cdep}", "to": f"effect:{eff_name}"})

    for calc_name, meta in visitor.calcs.items():
        for dep in sorted(meta["deps"]):
            edges.append({"from": f"input:{dep}", "to": f"calc:{calc_name}"})
        for cdep in sorted(meta["calc_deps"]):
            if cdep in known_calcs and cdep != calc_name:
                edges.append({"from": f"calc:{cdep}", "to": f"calc:{calc_name}"})

    total_observers = len(visitor.outputs) + len(visitor.effects)
    return {
        "success": True,
        "nodes": nodes,
        "edges": edges,
        "summary": f"{len(all_inputs)} inputs (sources), {len(visitor.calcs)} reactives (conductors), {total_observers} outputs & effects (observers)",
    }


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

    item: Dict[str, Any] = {
        "step": step,
        "action": act,
        "event": event,
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
) -> Dict[str, Any]:
    graph = inspect_reactive_graph(code)
    if not graph.get("success"):
        return graph

    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])
    events: List[Dict[str, Any]] = []
    step = 0

    adj_downstream: Dict[str, List[str]] = {}
    adj_upstream: Dict[str, List[str]] = {}
    for edge in edges:
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

        last_ts = 0
        for action in deduped_actions:
            action_type = action.get("type", "action")
            raw_name = str(action.get("name") or action.get("target") or "unknown")
            action_val = action.get("value")
            ts = action.get("timestamp")
            if ts is not None:
                last_ts = int(ts)
            ts_ms = last_ts
            ts_sec = round(ts_ms / 1000.0, 2)

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

            elif action_type == "output":
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
                        event="outputUpdated",
                        phase="interaction",
                        provenance="observed",
                        node_id=out_id,
                        node_label=node_lbl,
                        node_type="observer",
                        status="scheduled",
                        timestamp=ts_ms,
                        time_sec=ts_sec,
                        details=f"Observed browser output render: {node_lbl}",
                        session=session,
                    )
                )
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
            "edges": edges,
            "events": events,
            "log": events,
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
            details=f"Static ordering contains {len(eval_order)} nodes; no reactive flush occurred",
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
        "nodes": nodes,
        "edges": edges,
        "events": events,
        "log": events,
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

    normalized_events: List[Dict[str, Any]] = []
    step_idx = 0

    for item in raw_events:
        action = str(item.get("action") or item.get("event") or "")
        nid = item.get("reactId") or item.get("node_id") or item.get("id")
        lbl = item.get("label") or item.get("node_label") or nid or ""
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
            elif action == "invalidate":
                details = f"Invalidated '{lbl}'"
            elif action in ("valueChange", "inputChange"):
                details = f"Value change for '{lbl}': {val_str}"
            elif action in ("enter", "wouldEvaluate"):
                details = f"Evaluating '{lbl}'"
            elif action in ("exit", "ordered"):
                details = f"Completed evaluation of '{lbl}'"
            else:
                details = f"Event '{action}' on '{lbl}'"

        if action == "dependsOn" and dep_from and dep_to:
            edges_set.add((str(dep_from), str(dep_to)))

        if nid and str(nid) not in nodes_map:
            role = "conductor"
            clean_type = str(ntype).lower()
            if clean_type in ("observable", "input") or str(nid).startswith("input:"):
                role = "source"
                clean_type = "input"
            elif (
                clean_type in ("observer", "output", "effect")
                or str(nid).startswith("output:")
                or str(nid).startswith("effect:")
            ):
                role = "observer"
                clean_type = "output"
            elif clean_type in ("calc", "reactive"):
                role = "conductor"
                clean_type = "calc"

            name_val = str(nid).split(":", 1)[1] if ":" in str(nid) else str(nid)
            nodes_map[str(nid)] = {
                "id": str(nid),
                "name": name_val,
                "type": clean_type,
                "role": role,
                "label": str(lbl),
                "line": item.get("line"),
            }

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

    return {
        "success": True,
        "version": version,
        "session": session_name,
        "trace_kind": "loaded_reactlog_json",
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
            env={"SHINY_TESTMODE": "1", "PYTHONUNBUFFERED": "1"},
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
            context = browser.new_context(
                record_video_dir=temp_dir,
                record_video_size={"width": 1280, "height": 720},
                viewport={"width": 1280, "height": 720},
            )
            page = context.new_page()

            recorder_init_script = """
            window.__recordedActions = [];
            window.__recordStartTime = Date.now();
            const recentInputs = new Map();
            let lastClickTime = 0;
            let lastClickTarget = '';

            function trackAction(item) {
                item.timestamp = Date.now() - window.__recordStartTime;
                window.__recordedActions.push(item);
            }

            function attachShinyListeners() {
                if (window.$ && window.Shiny) {
                    $(document).off('.shinyRecorder');
                    $(document).on('shiny:inputchanged.shinyRecorder', (e) => {
                        const valKey = typeof e.value === 'object' ? JSON.stringify(e.value) : String(e.value);
                        recentInputs.set(e.name, { val: valKey, t: Date.now() });
                        trackAction({
                            type: 'input',
                            name: e.name,
                            value: e.value,
                            inputType: e.inputType || 'shiny'
                        });
                    });
                    $(document).on('shiny:value.shinyRecorder', (e) => {
                        trackAction({
                            type: 'output',
                            name: e.name
                        });
                    });
                }
            }

            document.addEventListener('DOMContentLoaded', attachShinyListeners);
            window.addEventListener('load', attachShinyListeners);
            document.addEventListener('shiny:connected', attachShinyListeners);

            document.addEventListener('change', (e) => {
                const target = e.target;
                if (!target || !target.id || target.id.startsWith('.')) return;
                const id = target.id;
                const val = target.value !== undefined ? target.value : target.checked;
                const valKey = String(val);
                const rec = recentInputs.get(id);
                if (rec && (Date.now() - rec.t < 350) && rec.val === valKey) {
                    return;
                }
                if (window.Shiny && window.Shiny.setInputValue && target.closest('.shiny-input-container')) {
                    return;
                }
                recentInputs.set(id, { val: valKey, t: Date.now() });
                trackAction({
                    type: 'input',
                    name: id,
                    value: val,
                    inputType: target.type || target.tagName.toLowerCase()
                });
            }, true);

            document.addEventListener('click', (e) => {
                const target = e.target.closest('button, input, select, textarea, a, .btn');
                if (!target) return;
                const tgtName = target.id || target.name || target.tagName.toLowerCase();
                const now = Date.now();
                if (tgtName === lastClickTarget && (now - lastClickTime < 200)) {
                    return;
                }
                lastClickTime = now;
                lastClickTarget = tgtName;
                trackAction({
                    type: 'click',
                    target: tgtName,
                    text: (target.innerText || target.value || '').trim().slice(0, 50)
                });
            }, true);
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
            else:
                time.sleep(1.0)

            try:
                if not page.is_closed():
                    raw_actions = page.evaluate("() => window.__recordedActions || []")
                    if isinstance(raw_actions, list):
                        recorded_actions = cast(List[Dict[str, Any]], raw_actions)
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

        return {
            "success": True,
            "actions": recorded_actions,
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
            )
            return future.result()
    return _record_session_sync(
        app_path, video_path, headless, record_script, timeout_secs
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
            lines.append(f'    {syn_id}["📥 {label}"]:::inputClass')
        elif ntype == "calc":
            lines.append(f'    {syn_id}["⚡ {label}"]:::calcClass')
        elif ntype == "effect":
            lines.append(f'    {syn_id}["🔔 {label}"]:::effectClass')
        else:
            lines.append(f'    {syn_id}["📊 {label}"]:::outputClass')

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
    except (IndentationError, tokenize.TokenError):
        return html_lib.escape(source)

    fragments.append(html_lib.escape(source[cursor:]))
    return "".join(fragments)


def format_reactlog_html(
    reactlog: Dict[str, Any],
    source_code: str,
    title: str = "Shiny Reactive Dependency Simulation",
    video_path: Optional[str] = None,
    html_path: Optional[str] = None,
    theme: str = "dark",
) -> str:
    escaped_title = html_lib.escape(title)
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
            '<button class="sidebar-tab" id="video-tab" role="tab" '
            'aria-selected="false" aria-controls="video-panel" '
            "onclick=\"showSidebarPanel('video')\">Recording</button>"
        )
        video_panel = f"""
        <div class="video-panel sidebar-panel" id="video-panel" role="tabpanel" aria-labelledby="video-tab" hidden>
          <div class="video-container">
            <video id="session-video" controls preload="metadata" playsinline>
              <source src="{rel_video}" type="video/webm">
              Your browser does not support the video tag.
            </video>
          </div>
          <div class="video-meta">
            <span class="video-badge">Playwright Video Recording</span>
            <span class="video-filename">{rel_video}</span>
          </div>
          <p class="video-help">Play, pause, or seek here—the graph, event list, and recording timeline follow the video.</p>
        </div>
        """

    trace_label = "Recording timeline" if actual_video else "Event timeline"
    video_sync_indicator = (
        '<span class="video-sync-status" id="video-sync-status" role="status" '
        'aria-live="polite">● Graph follows recording</span>'
        if actual_video
        else ""
    )

    source_tab = (
        '<button class="sidebar-tab" id="source-tab" role="tab" '
        'aria-selected="false" aria-controls="source-panel" '
        "onclick=\"showSidebarPanel('source')\">App code</button>"
    )
    source_panel = (
        '<pre class="source-panel sidebar-panel" id="source-panel" role="tabpanel" '
        'aria-labelledby="source-tab" hidden><mark class="source-line-highlight" '
        'id="source-line-highlight" aria-hidden="true" hidden></mark><code>'
        f"{formatted_source}</code></pre>"
    )
    escaped_json = (
        json.dumps(reactlog, indent=2)
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
    :root, [data-theme="dark"] {{
      color-scheme: dark;
      --bg: #090d12;
      --surface: #111821;
      --surface-2: #17212d;
      --surface-3: #1d2a38;
      --border: #293747;
      --border-strong: #3a4b5f;
      --text: #edf4fb;
      --text-muted: #91a1b3;
      --accent: #63b3ff;
      --source: #38bdf8;
      --calc: #fbbf24;
      --effect: #c084fc;
      --output: #4ade80;
      --warning: #fb923c;
      --grid-line: rgba(105, 128, 151, 0.055);
      --header-bg: rgba(17, 24, 33, 0.96);
      --node-fill: #121b25;
      --node-stroke: #35475a;
      --node-text: #edf4fb;
      --node-subtext: #91a1b3;
      --source-panel-bg: #0c1219;
      --source-panel-text: #d9e7f5;
      --trace-bg: #080d14;
      --trace-lane-bg: #0a111a;
      --toast-bg: rgba(23, 33, 45, 0.95);
      --legend-bg: rgba(17, 24, 33, 0.9);
      --mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      --sans: Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    [data-theme="light"] {{
      color-scheme: light;
      --bg: #f8fafc;
      --surface: #ffffff;
      --surface-2: #f1f5f9;
      --surface-3: #e2e8f0;
      --border: #cbd5e1;
      --border-strong: #94a3b8;
      --text: #0f172a;
      --text-muted: #64748b;
      --accent: #0284c7;
      --source: #0284c7;
      --calc: #d97706;
      --effect: #9333ea;
      --output: #16a34a;
      --warning: #ea580c;
      --grid-line: rgba(15, 23, 42, 0.06);
      --header-bg: rgba(255, 255, 255, 0.96);
      --node-fill: #ffffff;
      --node-stroke: #cbd5e1;
      --node-text: #0f172a;
      --node-subtext: #64748b;
      --source-panel-bg: #f8fafc;
      --source-panel-text: #1e293b;
      --trace-bg: #f1f5f9;
      --trace-lane-bg: #ffffff;
      --toast-bg: rgba(255, 255, 255, 0.95);
      --legend-bg: rgba(255, 255, 255, 0.92);
    }}
    @media (prefers-color-scheme: light) {{
      [data-theme="auto"] {{
        color-scheme: light;
        --bg: #f8fafc;
        --surface: #ffffff;
        --surface-2: #f1f5f9;
        --surface-3: #e2e8f0;
        --border: #cbd5e1;
        --border-strong: #94a3b8;
        --text: #0f172a;
        --text-muted: #64748b;
        --accent: #0284c7;
        --source: #0284c7;
        --calc: #d97706;
        --effect: #9333ea;
        --output: #16a34a;
        --warning: #ea580c;
        --grid-line: rgba(15, 23, 42, 0.06);
        --header-bg: rgba(255, 255, 255, 0.96);
        --node-fill: #ffffff;
        --node-stroke: #cbd5e1;
        --node-text: #0f172a;
        --node-subtext: #64748b;
        --source-panel-bg: #f8fafc;
        --source-panel-text: #1e293b;
        --trace-bg: #f1f5f9;
        --trace-lane-bg: #ffffff;
        --toast-bg: rgba(255, 255, 255, 0.95);
        --legend-bg: rgba(255, 255, 255, 0.92);
      }}
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    button, input {{ font: inherit; }}
    button:focus-visible, input:focus-visible {{ outline: 2px solid var(--accent); outline-offset: 2px; }}
    body {{ background: var(--bg); color: var(--text); font-family: var(--sans); height: 100vh; display: flex; flex-direction: column; overflow: hidden; }}
    .app-header {{ min-height: 64px; background: var(--header-bg); border-bottom: 1px solid var(--border); padding: 0.75rem 1.25rem; display: flex; justify-content: space-between; gap: 1rem; align-items: center; }}
    .brand {{ display: flex; align-items: center; gap: 0.75rem; min-width: 0; }}
    .brand-mark {{ width: 34px; height: 34px; border-radius: 9px; display: grid; place-items: center; color: #07111c; background: linear-gradient(145deg, #82c9ff, #3b9ced); font-family: var(--mono); font-weight: 900; box-shadow: 0 7px 20px rgba(58, 158, 239, 0.22); }}
    .brand-copy {{ min-width: 0; }}
    .brand-title {{ font-weight: 760; font-size: 0.98rem; letter-spacing: -0.01em; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
    .brand-subtitle {{ color: var(--text-muted); font-size: 0.74rem; margin-top: 0.15rem; }}
    .stats {{ display: flex; align-items: center; gap: 0.45rem; flex-wrap: wrap; justify-content: flex-end; }}
    .stat {{ border: 1px solid var(--border); background: var(--surface-2); border-radius: 999px; color: var(--text-muted); padding: 0.28rem 0.58rem; font: 600 0.7rem var(--mono); }}
    .toolbar {{ min-height: 58px; background: var(--surface); border-bottom: 1px solid var(--border); padding: 0.65rem 1rem; display: flex; align-items: center; gap: 0.65rem; flex-wrap: wrap; }}
    .toolbar-group {{ display: flex; align-items: center; gap: 0.35rem; }}
    .toolbar-divider {{ width: 1px; height: 28px; background: var(--border); margin: 0 0.2rem; }}
    .btn {{ min-height: 34px; background: var(--surface-2); border: 1px solid var(--border); color: var(--text); padding: 0.42rem 0.66rem; border-radius: 7px; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; gap: 0.38rem; transition: background 120ms ease, border-color 120ms ease, transform 120ms ease; font-size: 0.76rem; font-weight: 700; }}
    .btn:hover {{ background: var(--surface-3); border-color: var(--border-strong); }}
    .btn:active {{ transform: translateY(1px); }}
    .btn.icon {{ width: 34px; padding: 0; font-family: var(--mono); }}
    .btn.primary {{ background: #1f69a3; border-color: #2d86c8; color: #fff; }}
    .btn.primary:hover {{ background: #267ec4; }}
    .btn.accent-skip {{ background: color-mix(in srgb, var(--effect) 14%, var(--surface-2)); border-color: color-mix(in srgb, var(--effect) 40%, var(--border)); color: var(--effect); }}
    .btn.accent-skip:hover {{ background: color-mix(in srgb, var(--effect) 22%, var(--surface-2)); }}
    .inline-icon {{ display: inline-block; vertical-align: -0.15em; margin-right: 0.35rem; flex-shrink: 0; }}
    .btn.icon svg {{ display: block; margin: auto; }}
    .phase-selector {{ display: flex; background: var(--bg); border: 1px solid var(--border); border-radius: 8px; padding: 2px; gap: 2px; }}
    .phase-btn {{ display: inline-flex; align-items: center; background: transparent; border: none; color: var(--text-muted); padding: 0.3rem 0.65rem; border-radius: 6px; font: 700 0.7rem var(--mono); cursor: pointer; transition: color 120ms ease, background 120ms ease, box-shadow 120ms ease; }}
    .phase-btn:hover {{ color: var(--text); background: var(--surface-2); }}
    .phase-btn.is-active {{ background: var(--surface-3); color: var(--accent); box-shadow: 0 2px 8px rgba(0,0,0,0.12); }}
    .search-wrap {{ position: relative; flex: 0 1 200px; min-width: 130px; }}
    .search-icon {{ position: absolute; left: 0.7rem; top: 50%; transform: translateY(-50%); color: var(--text-muted); pointer-events: none; }}
    .search-input {{ width: 100%; height: 34px; color: var(--text); background: var(--bg); border: 1px solid var(--border); border-radius: 7px; padding: 0 0.7rem 0 2rem; font-size: 0.76rem; }}
    .search-input::placeholder {{ color: var(--text-muted); }}
    .filter-btn[aria-pressed="true"] {{ color: var(--text); background: var(--surface-3); }}
    .filter-btn[data-role="source"][aria-pressed="true"] {{ border-color: var(--source); }}
    .filter-btn[data-role="conductor"][aria-pressed="true"] {{ border-color: var(--calc); }}
    .filter-btn[data-role="observer"][aria-pressed="true"] {{ border-color: var(--output); }}
    .scrubber {{ flex: 1; min-width: 130px; display: flex; align-items: center; gap: 0.6rem; }}
    .scrubber input[type="range"] {{ width: 100%; accent-color: var(--accent); cursor: pointer; }}
    .step-display {{ font: 700 0.72rem var(--mono); color: var(--accent); min-width: 80px; text-align: right; }}
    .main-view {{ display: grid; grid-template-columns: minmax(0, 1fr) 8px var(--sidebar-width, 440px); flex: 1; min-height: 0; overflow: hidden; position: relative; }}
    .main-view.sidebar-hidden {{ grid-template-columns: minmax(0, 1fr) 0 0; }}
    .split-resizer {{ width: 8px; background: var(--surface); border-left: 1px solid var(--border); border-right: 1px solid var(--border); cursor: col-resize; display: flex; align-items: center; justify-content: center; user-select: none; transition: background 120ms ease; z-index: 10; }}
    .split-resizer:hover, .split-resizer:focus-visible, .split-resizer.is-dragging {{ background: var(--surface-3); border-color: var(--accent); outline: none; }}
    .resizer-handle {{ width: 2px; height: 32px; border-radius: 1px; background: var(--border-strong); }}
    .split-resizer:hover .resizer-handle, .split-resizer.is-dragging .resizer-handle {{ background: var(--accent); }}
    .graph-container {{ min-width: 0; min-height: 0; overflow: hidden; position: relative; background-color: var(--bg); background-image: linear-gradient(var(--grid-line) 1px, transparent 1px), linear-gradient(90deg, var(--grid-line) 1px, transparent 1px); background-size: 24px 24px; }}
    .graph-topbar {{ position: absolute; z-index: 3; top: 0.8rem; left: 0.8rem; right: 0.8rem; display: flex; align-items: flex-start; justify-content: space-between; gap: 0.75rem; pointer-events: none; }}
    .legend {{ display: flex; gap: 0.4rem; flex-wrap: wrap; padding: 0.4rem; border: 1px solid var(--border); border-radius: 9px; background: var(--legend-bg); backdrop-filter: blur(8px); box-shadow: 0 8px 30px rgba(0,0,0,0.12); pointer-events: auto; }}
    .legend-item {{ display: inline-flex; align-items: center; gap: 0.35rem; color: var(--text-muted); font: 650 0.66rem var(--mono); padding: 0.18rem 0.32rem; }}
    .legend-dot {{ width: 7px; height: 7px; border-radius: 50%; background: var(--role-color); box-shadow: 0 0 0 3px color-mix(in srgb, var(--role-color) 18%, transparent); }}
    .zoom-controls {{ display: flex; gap: 0.3rem; pointer-events: auto; }}
    .action-toast {{ position: absolute; z-index: 4; bottom: 1rem; left: 50%; transform: translateX(-50%); background: var(--toast-bg); border: 1px solid var(--accent); border-radius: 999px; padding: 0.45rem 1.1rem; color: var(--text); font: 650 0.76rem var(--mono); box-shadow: 0 10px 30px rgba(0,0,0,0.25); display: flex; align-items: center; gap: 0.6rem; pointer-events: none; animation: toast-pop 200ms ease; }}
    @keyframes toast-pop {{ from {{ opacity: 0; transform: translate(-50%, 8px); }} to {{ opacity: 1; transform: translate(-50%, 0); }} }}
    #reactlog-svg {{ width: 100%; height: 100%; min-height: 430px; display: block; }}
    .graph-node, .graph-edge {{ transition: opacity 160ms ease, filter 160ms ease, stroke 160ms ease, stroke-width 160ms ease; }}
    .graph-edge {{ opacity: 0.75; stroke: #527494; stroke-width: 1.8px; }}
    .graph-edge[data-active="true"] {{ opacity: 1 !important; stroke: var(--accent) !important; stroke-width: 2.8px !important; stroke-dasharray: 7 8; animation: edge-flow 900ms linear infinite; }}
    @keyframes edge-flow {{ to {{ stroke-dashoffset: -30; }} }}
    @media (prefers-reduced-motion: reduce) {{
      .graph-node, .graph-edge, .source-line-highlight, .trace-chip, .trace-playhead {{ transition: none; }}
      .graph-edge[data-active="true"] {{ animation: none; }}
      .action-toast {{ animation: none; }}
    }}
    .graph-node {{ cursor: pointer; }}
    .graph-node:hover .node-card {{ filter: brightness(1.08); }}
    .graph-node.is-selected .node-card {{ filter: drop-shadow(0 0 9px color-mix(in srgb, var(--accent) 50%, transparent)); }}
    .stage-label {{ font: 700 10px var(--mono); fill: var(--text-muted); letter-spacing: 0.08em; }}
    .sidebar {{ min-width: 0; background: var(--surface); border-left: 1px solid var(--border); display: flex; flex-direction: column; overflow: hidden; }}
    .sidebar-header {{ min-height: 46px; padding: 0.7rem 0.8rem 0.65rem 1rem; border-bottom: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between; gap: 0.75rem; }}
    .sidebar-tabs {{ display: flex; align-items: center; gap: 0.25rem; }}
    .sidebar-tab {{ color: var(--text-muted); background: transparent; border: 1px solid transparent; border-radius: 6px; padding: 0.36rem 0.55rem; font-size: 0.7rem; font-weight: 800; letter-spacing: 0.06em; text-transform: uppercase; cursor: pointer; }}
    .sidebar-tab:hover {{ color: var(--text); background: var(--surface-2); }}
    .sidebar-tab[aria-selected="true"] {{ color: var(--text); background: var(--surface-3); border-color: var(--border); }}
    .sidebar-panel {{ min-height: 0; flex: 1; }}
    .sidebar-panel[hidden] {{ display: none; }}
    .timeline-panel {{ display: flex; flex-direction: column; }}
    .source-panel {{ position: relative; overflow: auto; padding: 1rem; background: var(--source-panel-bg); color: var(--source-panel-text); font: 500 0.76rem/1.62 var(--mono); white-space: pre; tab-size: 4; }}
    .source-panel code {{ position: relative; z-index: 1; font: inherit; }}
    .source-line-highlight {{ position: absolute; z-index: 0; left: 0; right: 0; margin: 0; padding: 0; border: 0; border-left: 3px solid var(--source-highlight-color, var(--accent)); border-radius: 0; background: color-mix(in srgb, var(--source-highlight-color, var(--accent)) 16%, transparent); box-shadow: inset 0 1px color-mix(in srgb, var(--source-highlight-color, var(--accent)) 12%, transparent), inset 0 -1px color-mix(in srgb, var(--source-highlight-color, var(--accent)) 12%, transparent); pointer-events: none; transition: top 150ms ease, background 150ms ease; }}
    .source-line-highlight[hidden] {{ display: none; }}
    .video-panel {{ display: flex; flex-direction: column; padding: 1rem; gap: 0.8rem; background: var(--surface); overflow: auto; }}
    .video-container {{ width: 100%; border-radius: 8px; overflow: hidden; border: 1px solid var(--border); background: #000; }}
    .video-container video {{ width: 100%; display: block; }}
    .video-meta {{ display: flex; align-items: center; justify-content: space-between; gap: 0.5rem; flex-wrap: wrap; }}
    .video-badge {{ background: color-mix(in srgb, var(--accent) 18%, var(--surface-2)); border: 1px solid var(--accent); color: var(--accent); border-radius: 999px; padding: 0.2rem 0.55rem; font: 700 0.68rem var(--mono); }}
    .video-sync-status {{ color: var(--output); font: 700 0.68rem var(--mono); display: inline-flex; align-items: center; gap: 0.3rem; }}
    .video-filename {{ color: var(--text-muted); font: 500 0.7rem var(--mono); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
    .video-help {{ color: var(--text-muted); font-size: 0.72rem; line-height: 1.5; text-wrap: pretty; }}
    .syntax-keyword {{ color: #c084fc; font-weight: 700; }}
    [data-theme="light"] .syntax-keyword {{ color: #7e22ce; font-weight: 700; }}
    .syntax-string {{ color: #4ade80; }}
    [data-theme="light"] .syntax-string {{ color: #15803d; }}
    .syntax-number {{ color: #fbbf24; }}
    [data-theme="light"] .syntax-number {{ color: #b45309; }}
    .syntax-comment {{ color: var(--text-muted); font-style: italic; }}
    .event-list {{ flex: 1; overflow-y: auto; padding: 0 0.6rem 0.6rem; display: flex; flex-direction: column; gap: 0.35rem; overscroll-behavior: contain; }}
    .event-phase-label {{ position: sticky; top: 0; z-index: 2; margin: 0 -0.6rem; padding: 0.65rem 0.75rem 0.4rem; color: var(--text-muted); background: linear-gradient(var(--surface) 78%, transparent); font: 800 0.64rem var(--mono); letter-spacing: 0.08em; text-transform: uppercase; }}
    .event-item {{ width: 100%; padding: 0.55rem 0.7rem; border-radius: 7px; border: 1px solid var(--border); border-left: 3px solid var(--border-strong); background: var(--surface-2); color: var(--text); text-align: left; cursor: pointer; display: flex; flex-direction: column; gap: 0.25rem; }}
    .event-item:hover {{ background: var(--surface-3); border-color: var(--border-strong); }}
    .event-item.is-current {{ border-color: var(--accent); background: color-mix(in srgb, var(--accent) 12%, var(--surface-2)); }}
    .event-item.kind-input {{ border-left-color: var(--source); }}
    .event-item.kind-calc {{ border-left-color: var(--calc); }}
    .event-item.kind-output {{ border-left-color: var(--output); }}
    .event-item.kind-effect {{ border-left-color: var(--effect); }}
    .event-header {{ display: flex; align-items: center; justify-content: space-between; gap: 0.5rem; }}
    .event-name-wrap {{ min-width: 0; display: flex; align-items: baseline; gap: 0.45rem; }}
    .event-step {{ color: var(--text-muted); font: 650 0.62rem var(--mono); font-variant-numeric: tabular-nums; }}
    .event-name {{ font: 700 0.76rem var(--mono); color: var(--text); }}
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
    .event-details {{ font-size: 0.72rem; color: var(--text-muted); line-height: 1.35; }}
    .inspector-panel {{ border-top: 1px solid var(--border); padding: 0.8rem; background: var(--surface); }}
    .inspector-title {{ font: 700 0.8rem var(--mono); color: var(--text); margin-bottom: 0.4rem; }}
    .inspector-row {{ display: flex; justify-content: space-between; font-size: 0.74rem; padding: 0.2rem 0; }}
    .inspector-label {{ color: var(--text-muted); }}
    .inspector-val {{ font-family: var(--mono); color: var(--text); font-weight: 600; }}
    .trace-timeline-bar {{ display: flex; flex-direction: column; gap: 0.35rem; padding: 0.45rem 1rem 0.55rem 1rem; background: var(--trace-bg); border-bottom: 1px solid var(--border); user-select: none; }}
    .trace-header {{ display: flex; align-items: center; justify-content: space-between; gap: 1rem; }}
    .trace-controls {{ display: flex; align-items: center; gap: 0.45rem; font: 700 0.74rem var(--mono); color: var(--text); }}
    .trace-badge {{ background: color-mix(in srgb, var(--accent) 18%, var(--surface-2)); border: 1px solid var(--accent); color: var(--accent); border-radius: 4px; padding: 0.1rem 0.35rem; font-size: 0.62rem; text-transform: uppercase; font-weight: 800; letter-spacing: 0.05em; }}
    .trace-clock {{ color: var(--accent); font-weight: 800; font-variant-numeric: tabular-nums; }}
    .trace-sep {{ color: var(--text-muted); opacity: 0.5; }}
    .trace-total {{ color: var(--text-muted); }}
    .trace-nav-actions {{ display: flex; gap: 0.2rem; margin-left: 0.2rem; }}
    .btn.mini {{ padding: 0.18rem 0.35rem; font-size: 0.65rem; }}
    .trace-legend-mini {{ display: flex; align-items: center; gap: 0.8rem; font: 600 0.64rem var(--mono); color: var(--text-muted); }}
    .legend-chip {{ display: inline-flex; align-items: center; gap: 0.3rem; }}
    .chip-dot {{ width: 6px; height: 6px; border-radius: 50%; display: inline-block; }}
    .lane-input .chip-dot {{ background: var(--source); box-shadow: 0 0 4px var(--source); }}
    .lane-calc .chip-dot {{ background: var(--calc); box-shadow: 0 0 4px var(--calc); }}
    .lane-output .chip-dot {{ background: var(--output); box-shadow: 0 0 4px var(--output); }}
    .trace-main-wrap {{ display: flex; align-items: stretch; gap: 0.6rem; position: relative; }}
    .trace-lanes-labels {{ display: flex; flex-direction: column; justify-content: space-between; width: 52px; padding-top: 14px; }}
    .lane-label {{ font: 700 0.6rem var(--mono); color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; height: 20px; display: flex; align-items: center; }}
    .trace-track-wrap {{ flex: 1; position: relative; display: flex; flex-direction: column; justify-content: flex-end; cursor: pointer; outline: none; border-radius: 6px; }}
    .trace-track-wrap:focus-visible {{ outline: 2px solid var(--accent); outline-offset: 3px; }}
    .trace-ruler {{ position: relative; height: 14px; width: 100%; pointer-events: none; }}
    .trace-ruler-tick {{ position: absolute; bottom: 0; width: 1px; height: 5px; background: var(--border-strong); }}
    .trace-ruler-tick.major {{ height: 9px; background: var(--text-muted); }}
    .trace-ruler-label {{ position: absolute; bottom: 4px; transform: translateX(-50%); font: 600 0.58rem var(--mono); color: var(--text-muted); pointer-events: none; }}
    .trace-lanes {{ position: relative; height: 66px; background: var(--trace-lane-bg); border: 1px solid var(--border); border-radius: 6px; display: flex; flex-direction: column; overflow: visible; }}
    .trace-lane {{ position: relative; height: 22px; width: 100%; border-bottom: 1px dashed var(--border); }}
    .trace-lane:last-of-type {{ border-bottom: none; }}
    .trace-fill {{ position: absolute; top: 0; left: 0; bottom: 0; width: 0%; background: color-mix(in srgb, var(--accent) 12%, transparent); border-radius: 5px 0 0 5px; pointer-events: none; }}
    .trace-chip {{ position: absolute; top: 50%; transform: translate(-50%, -50%); pointer-events: auto; height: 18px; max-width: 120px; padding: 0 6px; border-radius: 4px; font: 700 0.58rem var(--mono); display: inline-flex; align-items: center; gap: 3px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; cursor: pointer; box-shadow: 0 1px 4px rgba(0,0,0,0.25); transition: transform 120ms ease, box-shadow 120ms ease, border-color 120ms ease; z-index: 2; }}
    .trace-chip:hover, .trace-chip.is-active {{ transform: translate(-50%, -50%) scale(1.12); z-index: 10; box-shadow: 0 0 10px var(--accent); }}
    .trace-chip.kind-input {{ background: color-mix(in srgb, var(--source) 18%, var(--surface)); color: var(--source); border: 1px solid var(--source); }}
    .trace-chip.kind-click {{ background: color-mix(in srgb, var(--effect) 18%, var(--surface)); color: var(--effect); border: 1px solid var(--effect); }}
    .trace-chip.kind-calc {{ background: color-mix(in srgb, var(--calc) 18%, var(--surface)); color: var(--calc); border: 1px solid var(--calc); }}
    .trace-chip.kind-output {{ background: color-mix(in srgb, var(--output) 18%, var(--surface)); color: var(--output); border: 1px solid var(--output); }}
    .trace-playhead {{ position: absolute; top: -5px; bottom: -3px; left: 0%; width: 2px; background: var(--accent); box-shadow: 0 0 10px var(--accent); pointer-events: none; z-index: 15; transition: left 40ms linear; }}
    .playhead-handle {{ position: absolute; top: 0; left: 50%; transform: translate(-50%, -50%) rotate(45deg); width: 8px; height: 8px; background: var(--accent); border-radius: 2px; box-shadow: 0 0 6px var(--accent); }}
    .playhead-line {{ width: 100%; height: 100%; }}
    .trace-tooltip {{ position: absolute; bottom: calc(100% + 8px); transform: translateX(-50%); background: var(--surface); border: 1px solid var(--accent); border-radius: 6px; padding: 0.4rem 0.65rem; font: 600 0.68rem var(--mono); color: var(--text); white-space: nowrap; pointer-events: none; box-shadow: 0 8px 24px rgba(0,0,0,0.3); z-index: 25; display: flex; flex-direction: column; gap: 0.15rem; }}
    .tooltip-time {{ color: var(--accent); font-weight: 800; font-size: 0.72rem; }}
    .tooltip-title {{ color: var(--text); font-weight: 700; }}
    .tooltip-desc {{ color: var(--text-muted); font-size: 0.62rem; }}
  </style>
</head>
<body>
  <header class="app-header">
    <div class="brand">
      <div class="brand-mark" aria-hidden="true">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
      </div>
      <div class="brand-copy">
        <h1 class="brand-title">{escaped_title}</h1>
        <div class="brand-subtitle">Interactive Shiny Reactive Log & Graph Explorer</div>
      </div>
    </div>
    <div class="stats">
      <span class="stat" id="stat-nodes">Nodes: 0</span>
      <span class="stat" id="stat-edges">Edges: 0</span>
      <span class="stat" id="stat-observed"><svg class="inline-icon" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/></svg>Observed: 0</span>
      <span class="stat" id="stat-inferred"><svg class="inline-icon" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>Inferred: 0</span>
      <button class="btn icon" id="btn-theme-toggle" onclick="toggleTheme()" aria-label="Toggle light/dark theme" title="Toggle theme"></button>
    </div>
  </header>

  <main class="toolbar" role="toolbar" aria-label="Reactlog controls">
    <div class="toolbar-group">
      <button class="btn icon" id="btn-play" onclick="togglePlay()" aria-label="Play timeline" title="Play"><svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><polygon points="6 3 20 12 6 21 6 3"/></svg></button>
      <button class="btn icon" onclick="stepBack()" aria-label="Step back" title="Step back"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="19 20 9 12 19 4 19 20"/><line x1="5" x2="5" y1="19" y2="5"/></svg></button>
      <button class="btn icon" onclick="stepForward()" aria-label="Step forward" title="Step forward"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="5 4 15 12 5 20 5 4"/><line x1="19" x2="19" y1="5" y2="19"/></svg></button>
      <button class="btn icon" onclick="resetTimeline()" aria-label="Reset timeline" title="Reset"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/></svg></button>
    </div>

    <div class="toolbar-divider" aria-hidden="true"></div>

    <div class="phase-selector" role="group" aria-label="Timeline phase filter">
      <button class="phase-btn is-active" id="phase-btn-all" aria-pressed="true" onclick="setPhaseFilter('all')"><svg class="inline-icon" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="7" height="7" x="3" y="3" rx="1"/><rect width="7" height="7" x="14" y="3" rx="1"/><rect width="7" height="7" x="14" y="14" rx="1"/><rect width="7" height="7" x="3" y="14" rx="1"/></svg>All (<span id="count-all">0</span>)</button>
      <button class="phase-btn" id="phase-btn-init" aria-pressed="false" onclick="setPhaseFilter('init')"><svg class="inline-icon" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/></svg>Init (<span id="count-init">0</span>)</button>
      <button class="phase-btn" id="phase-btn-interaction" aria-pressed="false" onclick="setPhaseFilter('interaction')"><svg class="inline-icon" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m16 13 5.223 3.482a.5.5 0 0 0 .777-.416V7.87a.5.5 0 0 0-.752-.432L16 10.5"/><rect x="2" y="6" width="14" height="12" rx="2"/></svg>Actions (<span id="count-interaction">0</span>)</button>
    </div>

    <button class="btn accent-skip" id="btn-skip-init" onclick="skipToInteractions()" title="Skip initialization steps and start at first app action"><svg class="inline-icon" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 19 22 12 13 5 13 19"/><polygon points="2 19 11 12 2 5 2 19"/></svg>Skip to Actions</button>

    <div class="toolbar-divider" aria-hidden="true"></div>

    <div class="scrubber">
      <input type="range" id="scrubber-range" min="0" max="0" value="0" oninput="seekTo(Number(this.value))" aria-label="Timeline step scrubber" />
      <span class="step-display" id="step-display">Step 0 / 0</span>
    </div>

    <div class="toolbar-divider" aria-hidden="true"></div>

    <div class="search-wrap">
      <svg class="search-icon" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
      <input type="search" class="search-input" id="search-input" name="reactive-node-filter" autocomplete="off" placeholder="Filter graph nodes…" oninput="handleSearch(this.value)" aria-label="Filter reactive nodes by name or type" />
    </div>

    <div class="toolbar-group">
      <button class="btn filter-btn" data-role="source" aria-pressed="true" onclick="toggleRoleFilter('source', this)">Inputs</button>
      <button class="btn filter-btn" data-role="conductor" aria-pressed="true" onclick="toggleRoleFilter('conductor', this)">Calcs</button>
      <button class="btn filter-btn" data-role="observer" aria-pressed="true" onclick="toggleRoleFilter('observer', this)">Outputs</button>
    </div>

    <div class="toolbar-divider" aria-hidden="true"></div>

    <div class="toolbar-group">
      <input type="file" id="reactlog-file-input" accept=".json" style="display:none" onchange="handleReactlogFileUpload(event)" />
      <button class="btn" id="btn-open-json" onclick="document.getElementById('reactlog-file-input').click()" title="Open existing Reactlog JSON file"><svg class="inline-icon" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="12" y1="18" x2="12" y2="12"/><line x1="9" y1="15" x2="15" y2="15"/></svg>Open JSON</button>
    </div>
  </main>

  <div class="trace-timeline-bar" id="trace-timeline-bar" aria-label="Session Recording Trace Scrubber">
    <div class="trace-header">
      <div class="trace-controls">
        <span class="trace-badge">{trace_label}</span>
        <span class="trace-clock" id="trace-current-time">0.0s</span>
        <span class="trace-sep">/</span>
        <span class="trace-total" id="trace-total-time">0.0s</span>
        <div class="trace-nav-actions">
          <button class="btn icon mini" onclick="prevAction()" aria-label="Previous action" title="Previous action"><svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="19 20 9 12 19 4 19 20"/><line x1="5" x2="5" y1="19" y2="5"/></svg></button>
          <button class="btn icon mini" onclick="nextAction()" aria-label="Next action" title="Next action"><svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="5 4 15 12 5 20 5 4"/><line x1="19" x2="19" y1="5" y2="19"/></svg></button>
        </div>
      </div>
      <div class="trace-legend-mini">
        {video_sync_indicator}
        <span class="legend-chip lane-input"><span class="chip-dot"></span>Inputs & Clicks</span>
        <span class="legend-chip lane-calc"><span class="chip-dot"></span>Reactive Calcs</span>
        <span class="legend-chip lane-output"><span class="chip-dot"></span>Outputs</span>
      </div>
    </div>

    <div class="trace-main-wrap">
      <div class="trace-lanes-labels">
        <div class="lane-label">Inputs</div>
        <div class="lane-label">Calcs</div>
        <div class="lane-label">Outputs</div>
      </div>
      <div class="trace-track-wrap" id="trace-track-wrap" tabindex="0" role="slider" aria-label="Scrub trace recording" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0">
        <div class="trace-ruler" id="trace-ruler"></div>
        <div class="trace-lanes" id="trace-lanes">
          <div class="trace-fill" id="trace-fill"></div>
          <div class="trace-lane" id="lane-inputs"></div>
          <div class="trace-lane" id="lane-calcs"></div>
          <div class="trace-lane" id="lane-outputs"></div>
          <div class="trace-playhead" id="trace-playhead">
            <div class="playhead-handle"></div>
            <div class="playhead-line"></div>
          </div>
        </div>
        <div class="trace-tooltip" id="trace-tooltip" hidden></div>
      </div>
    </div>
  </div>

  <div class="main-view" id="main-view">
    <div class="graph-container" id="graph-container">
      <div class="graph-topbar">
        <div class="legend" aria-label="Node types legend">
          <div class="legend-item"><span class="legend-dot" style="--role-color: var(--source)"></span> Inputs</div>
          <div class="legend-item"><span class="legend-dot" style="--role-color: var(--calc)"></span> Calcs</div>
          <div class="legend-item"><span class="legend-dot" style="--role-color: var(--output)"></span> Outputs</div>
          <div class="legend-item"><span class="legend-dot" style="--role-color: var(--effect)"></span> Effects</div>
        </div>
        <div class="zoom-controls">
          <button class="btn icon" onclick="zoomIn()" aria-label="Zoom in" title="Zoom in"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" x2="16.65" y1="21" y2="16.65"/><line x1="11" x2="11" y1="8" y2="14"/><line x1="8" x2="14" y1="11" y2="11"/></svg></button>
          <button class="btn icon" onclick="zoomOut()" aria-label="Zoom out" title="Zoom out"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" x2="16.65" y1="21" y2="16.65"/><line x1="8" x2="14" y1="11" y2="11"/></svg></button>
          <button class="btn icon" onclick="fitGraph()" aria-label="Fit graph to view" title="Fit to view"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 3H5a2 2 0 0 0-2 2v3"/><path d="M21 8V5a2 2 0 0 0-2-2h-3"/><path d="M3 16v3a2 2 0 0 0 2 2h3"/><path d="M16 21h3a2 2 0 0 0 2-2v-3"/></svg></button>
          <button class="btn icon" onclick="resetZoom()" aria-label="Reset zoom" title="Reset zoom" style="font: 700 0.7rem var(--mono)">1:1</button>
        </div>
      </div>
      <div id="live-action-toast" class="action-toast" role="status" aria-live="polite" hidden></div>
      <svg id="reactlog-svg" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto">
            <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#6685a3" />
          </marker>
          <marker id="arrow-active" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto">
            <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="var(--accent)" />
          </marker>
          <marker id="arrow-invalidate" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto">
            <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="var(--warning)" />
          </marker>
          <filter id="card-shadow" x="-10%" y="-10%" width="120%" height="130%">
            <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#000" flood-opacity="0.22" />
          </filter>
        </defs>
        <g id="viewport-g"></g>
      </svg>
    </div>

    <div class="split-resizer" id="split-resizer" role="separator" aria-orientation="vertical" tabindex="0" aria-label="Resize sidebar panel" aria-valuenow="440" aria-valuemin="320" aria-valuemax="1200" title="Drag to resize sidebar, double-click to reset (or use Left/Right arrows)">
      <div class="resizer-handle"></div>
    </div>

    <aside class="sidebar" id="sidebar" aria-label="Details and events">
      <div class="sidebar-header">
        <div class="sidebar-tabs" role="tablist" aria-label="Sidebar views">
          <button class="sidebar-tab" id="timeline-tab" role="tab" aria-selected="true" aria-controls="timeline-panel" onclick="showSidebarPanel('timeline')">Events</button>
          {source_tab}
          {video_tab_btn}
        </div>
      </div>

      <div class="timeline-panel sidebar-panel" id="timeline-panel" role="tabpanel" aria-labelledby="timeline-tab">
        <div class="event-list" id="event-list"></div>
        <div class="inspector-panel" id="inspector-panel">
          <div class="inspector-title" id="insp-title">Node Details</div>
          <div class="inspector-row"><span class="inspector-label">Type:</span><span class="inspector-val" id="insp-type">-</span></div>
          <div class="inspector-row"><span class="inspector-label">Line:</span><span class="inspector-val" id="insp-line">-</span></div>
          <div class="inspector-row"><span class="inspector-label">Status:</span><span class="inspector-val" id="insp-status">-</span></div>
        </div>
      </div>

      {source_panel}
      {video_panel}
    </aside>
  </div>

  <script>
    const reactlogData = {escaped_json};
    const ICONS = {{
      play: '<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><polygon points="6 3 20 12 6 21 6 3"/></svg>',
      pause: '<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg>',
      video: '<svg class="inline-icon" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m16 13 5.223 3.482a.5.5 0 0 0 .777-.416V7.87a.5.5 0 0 0-.752-.432L16 10.5"/><rect x="2" y="6" width="14" height="12" rx="2"/></svg>',
      eye: '<svg class="inline-icon" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/></svg>',
      zap: '<svg class="inline-icon" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>'
    }};
    let currentStep = 0;
    let isPlaying = false;
    let playTimer = null;
    let selectedNodeId = null;
    let searchQuery = "";
    let activeRoles = new Set(['source', 'conductor', 'observer']);
    let currentPhaseFilter = 'all';
    let zoomLevel = 1;
    let panOffset = {{ x: 0, y: 0 }};
    let isPanning = false;
    let startPan = {{ x: 0, y: 0 }};
    let hasUserCustomWidth = false;
    let maxSessionDuration = 1.0;
    let isDraggingTrace = false;
    let videoFrameRequest = null;
    let videoFrameRequestKind = null;

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

    function setSidebarWidth(widthPx) {{
      const minW = 320;
      const maxW = Math.max(minW, Math.min(window.innerWidth * 0.65, 1200));
      const clamped = Math.max(minW, Math.min(widthPx, maxW));
      document.documentElement.style.setProperty('--sidebar-width', `${{clamped}}px`);
      const resizer = document.getElementById('split-resizer');
      if (resizer) resizer.setAttribute('aria-valuenow', String(Math.round(clamped)));
    }}

    function initSplitResizer() {{
      const resizer = document.getElementById('split-resizer');
      const mainView = document.getElementById('main-view');
      if (!resizer || !mainView) return;

      let isDragging = false;

      const onMouseDown = (e) => {{
        isDragging = true;
        hasUserCustomWidth = true;
        resizer.classList.add('is-dragging');
        document.body.style.cursor = 'col-resize';
        document.body.style.userSelect = 'none';
        e.preventDefault();
      }};

      const onMouseMove = (e) => {{
        if (!isDragging) return;
        const newW = window.innerWidth - e.clientX;
        setSidebarWidth(newW);
      }};

      const onMouseUp = () => {{
        if (!isDragging) return;
        isDragging = false;
        resizer.classList.remove('is-dragging');
        document.body.style.cursor = '';
        document.body.style.userSelect = '';
      }};

      resizer.addEventListener('mousedown', onMouseDown);
      window.addEventListener('mousemove', onMouseMove);
      window.addEventListener('mouseup', onMouseUp);

      resizer.addEventListener('touchstart', (e) => {{
        if (e.touches.length === 1) {{
          isDragging = true;
          hasUserCustomWidth = true;
          resizer.classList.add('is-dragging');
        }}
      }}, {{ passive: true }});
      window.addEventListener('touchmove', (e) => {{
        if (isDragging && e.touches.length === 1) {{
          const newW = window.innerWidth - e.touches[0].clientX;
          setSidebarWidth(newW);
        }}
      }}, {{ passive: true }});
      window.addEventListener('touchend', () => {{
        if (isDragging) {{
          isDragging = false;
          resizer.classList.remove('is-dragging');
        }}
      }});

      resizer.addEventListener('dblclick', () => {{
        hasUserCustomWidth = false;
        setSidebarWidth(440);
      }});

      resizer.addEventListener('keydown', (e) => {{
        const curW = parseInt(getComputedStyle(document.documentElement).getPropertyValue('--sidebar-width')) || 440;
        if (e.key === 'ArrowLeft') {{
          hasUserCustomWidth = true;
          setSidebarWidth(curW + 24);
          e.preventDefault();
        }} else if (e.key === 'ArrowRight') {{
          hasUserCustomWidth = true;
          setSidebarWidth(curW - 24);
          e.preventDefault();
        }} else if (e.key === 'Home') {{
          hasUserCustomWidth = false;
          setSidebarWidth(440);
          e.preventDefault();
        }}
      }});
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

    function initTraceTimeline() {{
      const bar = document.getElementById('trace-timeline-bar');
      const trackWrap = document.getElementById('trace-track-wrap');
      const ruler = document.getElementById('trace-ruler');
      const laneInputs = document.getElementById('lane-inputs');
      const laneCalcs = document.getElementById('lane-calcs');
      const laneOutputs = document.getElementById('lane-outputs');
      if (!bar || !trackWrap || !ruler || !laneInputs || !laneCalcs || !laneOutputs) return;

      const events = reactlogData.events || reactlogData.log || [];
      let maxTime = 0;
      for (const ev of events) {{
        const tVal = ev.time_sec !== undefined ? ev.time_sec : ev.time;
        if (tVal !== undefined && tVal > maxTime) maxTime = tVal;
        if (ev.effective_time !== undefined && ev.effective_time > maxTime) maxTime = ev.effective_time;
      }}
      const video = document.getElementById('session-video');
      if (video && video.duration && !isNaN(video.duration)) {{
        maxTime = Math.max(maxTime, video.duration);
      }}
      maxSessionDuration = Math.max(1.0, maxTime);

      const totalDisplay = document.getElementById('trace-total-time');
      if (totalDisplay) totalDisplay.textContent = formatTime(maxSessionDuration);
      const curDisplay = document.getElementById('trace-current-time');
      if (curDisplay) curDisplay.textContent = formatTime(0);

      ruler.innerHTML = '';
      const safeDuration = Math.min(7200, Math.max(1.0, maxSessionDuration));
      const stepSec = safeDuration <= 5 ? 0.5 : (safeDuration <= 20 ? 1.0 : (safeDuration <= 120 ? 5.0 : Math.max(10.0, safeDuration / 20)));
      for (let sec = 0; sec <= safeDuration + 0.001; sec += stepSec) {{
        const pct = (sec / maxSessionDuration) * 100;
        if (pct > 100) break;
        const isMajor = Math.abs(sec - Math.round(sec)) < 0.01;
        const tick = document.createElement('div');
        tick.className = `trace-ruler-tick ${{isMajor ? 'major' : ''}}`;
        tick.style.left = `${{pct}}%`;
        ruler.appendChild(tick);

        if (isMajor || sec === 0) {{
          const lbl = document.createElement('span');
          lbl.className = 'trace-ruler-label';
          lbl.style.left = `${{pct}}%`;
          lbl.textContent = `${{Math.round(sec)}}s`;
          ruler.appendChild(lbl);
        }}
      }}

      laneInputs.innerHTML = '';
      laneCalcs.innerHTML = '';
      laneOutputs.innerHTML = '';

      const waves = [];
      let curWave = null;

      const cleanName = (n) => {{
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
      }};

      events.forEach((ev, idx) => {{
        const evAction = ev.action || ev.event || '';
        const isInteract = ev.phase === 'interaction' || !['define', 'analysisInit', 'createContext', 'sessionInit'].includes(evAction);
        if (isInteract) {{
          const t = ev.time_sec !== undefined ? ev.time_sec : (ev.time !== undefined ? ev.time : 0);
          if (!curWave || (t - curWave.startTime) > 0.35) {{
            curWave = {{
              startTime: t,
              time: t,
              startStep: idx,
              inputs: [],
              calcs: [],
              outputs: [],
              details: ev.details || evAction,
            }};
            waves.push(curWave);
          }}

          const nId = ev.node_id || ev.id || '';
          if (evAction === 'inputChange' || evAction === 'userClick' || evAction === 'userAction' || nId.startsWith('input:')) {{
            const raw = nId || ev.details || '';
            if (!raw.includes('clientdata') && !raw.includes('pixelratio') && !raw.includes('_hidden')) {{
              const name = cleanName(raw) || 'input';
              if (!curWave.inputs.some(item => item.name === name)) {{
                curWave.inputs.push({{ name, step: idx, isClick: evAction === 'userClick' || evAction === 'userAction', details: ev.details }});
              }}
            }}
          }} else if (nId && (nId.startsWith('calc:') || nId.startsWith('effect:') || (ev.type === 'calc') || (ev.node_type === 'conductor'))) {{
            const name = cleanName(nId);
            if (name && !curWave.calcs.some(item => item.name === name)) {{
              curWave.calcs.push({{ name, step: idx, details: ev.details }});
            }}
          }} else if (nId && (nId.startsWith('output:') || (ev.type === 'output') || (ev.node_type === 'observer'))) {{
            const name = cleanName(nId);
            if (name && !curWave.outputs.some(item => item.name === name)) {{
              curWave.outputs.push({{ name, step: idx, details: ev.details }});
            }}
          }}
        }}
      }});

      const genericTokens = new Set(['on', 'off', 'true', 'false', 'null', 'undefined', 'click', 'button', 'input']);

      waves.forEach(wave => {{
        const pct = Math.min(96, Math.max(4, (wave.time / maxSessionDuration) * 100));

        if (wave.inputs.length > 0) {{
          const cleanInpNames = [...new Set(wave.inputs.flatMap(i => i.name ? [i.name] : []))];
          let meaningfulInps = [];
          for (const name of cleanInpNames) {{
            if (!genericTokens.has(name.toLowerCase())) meaningfulInps.push(name);
          }}
          if (meaningfulInps.length === 0) meaningfulInps = cleanInpNames;

          if (meaningfulInps.length > 0) {{
            const chip = document.createElement('button');
            chip.type = 'button';
            const isClick = wave.inputs.some(i => i.isClick);
            chip.className = `trace-chip ${{isClick ? 'kind-click' : 'kind-input'}}`;
            chip.style.left = `${{pct}}%`;
            chip.setAttribute('data-step', String(wave.inputs[0].step));
            chip.setAttribute('data-time', String(wave.time));
            const label = meaningfulInps.length === 1 ? meaningfulInps[0] : (meaningfulInps.length === 2 ? `${{meaningfulInps[0]}}, ${{meaningfulInps[1]}}` : `${{meaningfulInps.length}} inputs`);
            chip.title = `[${{formatTime(wave.time)}}] ${{wave.inputs.map(i => i.details || i.name).join(' | ')}}`;
            chip.textContent = label;
            chip.onclick = (e) => {{
              e.stopPropagation();
              seekTo(wave.inputs[0].step);
            }};
            laneInputs.appendChild(chip);
          }}
        }}

        const cleanCalcNames = [...new Set(wave.calcs.flatMap(c => c.name ? [c.name] : []))];
        if (cleanCalcNames.length > 0) {{
          const chip = document.createElement('button');
          chip.type = 'button';
          chip.className = 'trace-chip kind-calc';
          chip.style.left = `${{pct}}%`;
          chip.setAttribute('data-step', String(wave.calcs[0].step));
          chip.setAttribute('data-time', String(wave.time));
          const label = cleanCalcNames.length === 1 ? cleanCalcNames[0] : (cleanCalcNames.length === 2 ? `${{cleanCalcNames[0]}}, ${{cleanCalcNames[1]}}` : `${{cleanCalcNames.length}} calcs`);
          chip.title = `[${{formatTime(wave.time)}}] Recalculates: ${{cleanCalcNames.join(', ')}}`;
          chip.textContent = label;
          chip.onclick = (e) => {{
            e.stopPropagation();
            seekTo(wave.calcs[0].step);
          }};
          laneCalcs.appendChild(chip);
        }}

        const cleanOutputNames = [...new Set(wave.outputs.flatMap(o => o.name ? [o.name] : []))];
        if (cleanOutputNames.length > 0) {{
          const chip = document.createElement('button');
          chip.type = 'button';
          chip.className = 'trace-chip kind-output';
          chip.style.left = `${{pct}}%`;
          chip.setAttribute('data-step', String(wave.outputs[0].step));
          chip.setAttribute('data-time', String(wave.time));
          const label = cleanOutputNames.length === 1 ? cleanOutputNames[0] : (cleanOutputNames.length === 2 ? `${{cleanOutputNames[0]}}, ${{cleanOutputNames[1]}}` : `${{cleanOutputNames.length}} outputs`);
          chip.title = `[${{formatTime(wave.time)}}] Updates: ${{cleanOutputNames.join(', ')}}`;
          chip.textContent = label;
          chip.onclick = (e) => {{
            e.stopPropagation();
            seekTo(wave.outputs[0].step);
          }};
          laneOutputs.appendChild(chip);
        }}
      }});

      const tooltip = document.getElementById('trace-tooltip');
      const seekFromPointer = (e) => {{
        const rect = trackWrap.getBoundingClientRect();
        const clientX = e.touches ? e.touches[0].clientX : e.clientX;
        const ratio = Math.max(0, Math.min(1, (clientX - rect.left) / rect.width));
        const targetSec = ratio * maxSessionDuration;

        let matchIdx = 0;
        for (let i = 0; i < events.length; i++) {{
          const ev = events[i];
          const t = ev.effective_time !== undefined ? ev.effective_time : ((ev.time_sec !== undefined ? ev.time_sec : ev.time) || 0);
          if (t <= targetSec) matchIdx = i;
        }}
        seekTo(matchIdx);

        if (video) {{
          try {{ video.currentTime = targetSec; }} catch (err) {{}}
        }}
      }};

      trackWrap.addEventListener('pointerdown', (e) => {{
        isDraggingTrace = true;
        try {{ trackWrap.setPointerCapture(e.pointerId); }} catch (err) {{}}
        seekFromPointer(e);
      }});

      trackWrap.addEventListener('pointermove', (e) => {{
        const rect = trackWrap.getBoundingClientRect();
        const ratio = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
        const targetSec = ratio * maxSessionDuration;

        if (isDraggingTrace) {{
          seekFromPointer(e);
        }}

        if (tooltip) {{
          tooltip.hidden = false;
          const leftPx = Math.max(80, Math.min(rect.width - 80, ratio * rect.width));
          tooltip.style.left = `${{leftPx}}px`;

          let nearestWave = null;
          let minDiff = Infinity;
          for (const w of waves) {{
            const diff = Math.abs(w.time - targetSec);
            if (diff < minDiff) {{
              minDiff = diff;
              nearestWave = w;
            }}
          }}

          let tooltipHtml = `<span class="tooltip-time">⏱ ${{escapeHTML(formatTime(targetSec))}}</span>`;
          if (nearestWave && minDiff < 0.8) {{
            const inList = nearestWave.inputs.map(i => (i.isClick ? `👆 click on ${{escapeHTML(i.name)}}` : `📥 ${{escapeHTML(i.name)}}`)).join(', ');
            const outList = nearestWave.outputs.map(o => escapeHTML(o.name)).join(', ');
            const calcList = nearestWave.calcs.map(c => escapeHTML(c.name)).join(', ');

            if (inList) tooltipHtml += `<span class="tooltip-title">${{inList}}</span>`;
            if (calcList || outList) {{
              const dependencyParts = [];
              if (calcList) dependencyParts.push(calcList);
              if (outList) dependencyParts.push(outList);
              tooltipHtml += `<span class="tooltip-desc">↳ ${{dependencyParts.join(' → ')}}</span>`;
            }}
          }}
          tooltip.innerHTML = tooltipHtml;
        }}
      }});

      trackWrap.addEventListener('pointerleave', () => {{
        if (!isDraggingTrace && tooltip) tooltip.hidden = true;
      }});

      trackWrap.addEventListener('pointerup', (e) => {{
        isDraggingTrace = false;
        try {{ trackWrap.releasePointerCapture(e.pointerId); }} catch (err) {{}}
        if (tooltip) tooltip.hidden = true;
      }});
    }}

    function updateTraceTimelineScrubber(curSec) {{
      if (!maxSessionDuration || isNaN(maxSessionDuration)) return;
      const playhead = document.getElementById('trace-playhead');
      const fill = document.getElementById('trace-fill');
      const curDisplay = document.getElementById('trace-current-time');
      const pct = Math.min(100, Math.max(0, (curSec / maxSessionDuration) * 100));

      if (playhead) playhead.style.left = `${{pct}}%`;
      if (fill) fill.style.width = `${{pct}}%`;
      if (curDisplay) curDisplay.textContent = formatTime(curSec);

      document.querySelectorAll('.trace-chip').forEach(chip => {{
        const chipTime = parseFloat(chip.getAttribute('data-time') || '0');
        const isActive = Math.abs(chipTime - curSec) < 0.35;
        chip.classList.toggle('is-active', isActive);
      }});
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

    function init() {{
      initTheme();
      prepareEventTimings();
      const events = reactlogData.events || reactlogData.log || [];
      const nodes = reactlogData.nodes || [];
      const edges = reactlogData.edges || [];

      document.getElementById('stat-nodes').textContent = `Nodes: ${{nodes.length}}`;
      document.getElementById('stat-edges').textContent = `Edges: ${{edges.length}}`;
      const obsCount = reactlogData.observed_events_count !== undefined ? reactlogData.observed_events_count : events.reduce((acc, e) => acc + (e.provenance === 'observed' ? 1 : 0), 0);
      const infCount = reactlogData.inferred_events_count !== undefined ? reactlogData.inferred_events_count : events.reduce((acc, e) => acc + (e.provenance === 'inferred' ? 1 : 0), 0);
      document.getElementById('stat-observed').innerHTML = `${{ICONS.eye}} Observed: ${{obsCount}}`;
      document.getElementById('stat-inferred').innerHTML = `${{ICONS.zap}} Inferred: ${{infCount}}`;

      const initCount = reactlogData.init_steps_count !== undefined ? reactlogData.init_steps_count : events.reduce((acc, e) => acc + (e.phase === 'init' ? 1 : 0), 0);
      const interactCount = reactlogData.interaction_steps_count !== undefined ? reactlogData.interaction_steps_count : (events.length - initCount);
      document.getElementById('count-all').textContent = String(events.length);
      document.getElementById('count-init').textContent = String(initCount);
      document.getElementById('count-interaction').textContent = String(interactCount);

      const scrubber = document.getElementById('scrubber-range');
      scrubber.max = Math.max(0, events.length - 1);
      scrubber.value = 0;

      renderEventList();
      renderGraph();
      initTraceTimeline();
      seekTo(0);
      setupPanZoom();
      setupVideoSync();
      initSplitResizer();
    }}

    function nodeKind(n) {{
      if (n.role === 'source' || n.type === 'input') return {{ label: 'Input', color: '#0284c7' }};
      if (n.role === 'conductor' || n.type === 'calc') return {{ label: 'Reactive Calc', color: '#d97706' }};
      if (n.type === 'effect') return {{ label: 'Effect', color: '#9333ea' }};
      return {{ label: 'Output', color: '#16a34a' }};
    }}

    function showSidebarPanel(panelName) {{
      const tabs = ['timeline', 'source', 'video'];
      tabs.forEach(t => {{
        const btn = document.getElementById(`${{t}}-tab`);
        const panel = document.getElementById(`${{t}}-panel`);
        if (btn && panel) {{
          const isTarget = t === panelName;
          btn.setAttribute('aria-selected', isTarget ? 'true' : 'false');
          panel.hidden = !isTarget;
        }}
      }});

      if (!hasUserCustomWidth) {{
        if (panelName === 'video') {{
          setSidebarWidth(Math.max(480, Math.round(window.innerWidth * 0.45)));
        }} else if (panelName === 'source') {{
          setSidebarWidth(Math.max(480, Math.min(window.innerWidth * 0.52, 680)));
        }} else {{
          setSidebarWidth(440);
        }}
      }}
    }}

    function setPhaseFilter(phase) {{
      currentPhaseFilter = phase;
      ['all', 'init', 'interaction'].forEach(p => {{
        const btn = document.getElementById(`phase-btn-${{p}}`);
        if (btn) {{
          const isActive = p === phase;
          btn.classList.toggle('is-active', isActive);
          btn.setAttribute('aria-pressed', isActive ? 'true' : 'false');
        }}
      }});
      renderEventList();
    }}

    function skipToInteractions() {{
      const firstActionIdx = reactlogData.first_interaction_step || 0;
      setPhaseFilter('interaction');
      seekTo(firstActionIdx);
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

    function renderEventList() {{
      const list = document.getElementById('event-list');
      list.innerHTML = '';
      let visiblePhase = null;
      const events = reactlogData.events || reactlogData.log || [];

      events.forEach((ev, idx) => {{
        if (currentPhaseFilter !== 'all' && ev.phase && ev.phase !== currentPhaseFilter) {{
          return;
        }}

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
        if (nodeId.startsWith('input:')) item.classList.add('kind-input');
        else if (nodeId.startsWith('calc:')) item.classList.add('kind-calc');
        else if (nodeId.startsWith('output:')) item.classList.add('kind-output');
        else if (nodeId.startsWith('effect:')) item.classList.add('kind-effect');
        item.setAttribute('aria-label', `Step ${{idx}}: ${{ev.node_label || ev.label || ev.event || ev.action}}. ${{ev.details || ''}}`);
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
        nameSpan.textContent = ev.node_label || ev.label || ev.event || ev.action;

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
        provBadge.textContent = prov === 'observed' ? '👁️ OBSERVED' : '⚡ INFERRED';
        badgesWrap.appendChild(provBadge);

        const badge = document.createElement('span');
        badge.className = `event-badge ${{ev.status || 'idle'}}`;
        badge.textContent = ev.status || ev.action || ev.event;
        badgesWrap.appendChild(badge);

        header.appendChild(nameWrap);
        header.appendChild(badgesWrap);

        const details = document.createElement('div');
        details.className = 'event-details';
        details.textContent = ev.details || '';

        item.appendChild(header);
        item.appendChild(details);
        list.appendChild(item);
      }});
    }}

    function renderGraph() {{
      const svg = document.getElementById('viewport-g');
      svg.innerHTML = '';
      const isLight = getActiveTheme() === 'light';

      const rawNodes = reactlogData.nodes || [];
      const nodes = [];
      rawNodes.forEach(n => {{
        if (!activeRoles.has(n.role)) return;
        if (searchQuery && !n.id.toLowerCase().includes(searchQuery) && !(n.label || '').toLowerCase().includes(searchQuery)) return;
        nodes.push(n);
      }});

      const nodeSet = new Set(nodes.map(n => n.id));
      const edges = [];
      (reactlogData.edges || []).forEach(e => {{
        if (nodeSet.has(e.from) && nodeSet.has(e.to)) {{
          edges.push(e);
        }}
      }});

      const inDegree = {{}};
      nodes.forEach(n => inDegree[n.id] = 0);
      edges.forEach(e => inDegree[e.to] = (inDegree[e.to] || 0) + 1);

      const ranks = {{}};
      nodes.forEach(n => ranks[n.id] = n.role === 'source' ? 0 : 1);
      edges.forEach(e => {{
        ranks[e.to] = Math.max(ranks[e.to] || 1, (ranks[e.from] || 0) + 1);
      }});

      const maxRank = Math.max(1, ...Object.values(ranks));
      const columns = Array.from({{ length: maxRank + 1 }}, () => []);
      nodes.forEach(n => {{
        const r = ranks[n.id] || 0;
        columns[r].push(n);
      }});

      const colWidth = 280;
      const rowHeight = 88;
      const nodeWidth = 210;
      const nodeHeight = 58;
      const maxInCol = Math.max(1, ...columns.map(c => c.length));
      const svgHeight = Math.max(520, maxInCol * rowHeight + 140);

      const pos = {{}};
      columns.forEach((colNodes, colIdx) => {{
        const colX = 140 + colIdx * colWidth;
        const totalH = (colNodes.length - 1) * rowHeight;
        const startY = 100 + (svgHeight - 140 - totalH) / 2;

        const stageHeader = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        stageHeader.setAttribute('x', colX);
        stageHeader.setAttribute('y', 50);
        stageHeader.setAttribute('class', 'stage-label');
        stageHeader.setAttribute('text-anchor', 'middle');
        stageHeader.textContent = colIdx === 0 ? 'INPUTS' : (colIdx === maxRank ? 'OUTPUTS / EFFECTS' : `STAGE ${{colIdx}}`);
        svg.appendChild(stageHeader);

        colNodes.forEach((n, rowIdx) => {{
          pos[n.id] = {{ x: colX, y: startY + rowIdx * rowHeight }};
        }});
      }});

      const events = reactlogData.events || reactlogData.log || [];
      const activeEvent = events[currentStep] || {{}};

      edges.forEach(e => {{
        const p1 = pos[e.from];
        const p2 = pos[e.to];
        if (p1 && p2) {{
          const x1 = p1.x + (nodeWidth / 2);
          const y1 = p1.y;
          const x2 = p2.x - (nodeWidth / 2);
          const y2 = p2.y;
          const midX = x1 + Math.max(35, (x2 - x1) * 0.5);

          const fromMatch = activeEvent.edge_from || activeEvent.dependsOn;
          const toMatch = activeEvent.edge_to || activeEvent.node_id || activeEvent.id;
          const isEdgeActive = (fromMatch && toMatch)
            ? (fromMatch === e.from && toMatch === e.to)
            : (activeEvent.node_id === e.to && (activeEvent.event === 'dependsOn' || activeEvent.event === 'propagate' || activeEvent.action === 'dependsOn' || activeEvent.action === 'invalidate'));
          const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
          path.setAttribute('d', `M ${{x1}} ${{y1}} C ${{midX}} ${{y1}}, ${{midX}} ${{y2}}, ${{x2}} ${{y2}}`);
          path.setAttribute('fill', 'none');
          path.setAttribute('stroke-linecap', 'round');
          path.setAttribute('data-from', e.from);
          path.setAttribute('data-to', e.to);
          path.setAttribute('data-active', isEdgeActive ? 'true' : 'false');
          path.setAttribute('class', 'graph-edge');
          path.setAttribute('marker-end', isEdgeActive ? 'url(#arrow-active)' : 'url(#arrow)');

          svg.appendChild(path);
        }}
      }});

      nodes.forEach(n => {{
        const p = pos[n.id] || {{ x: 200, y: 200 }};
        const activeNodeId = activeEvent.node_id || activeEvent.id;
        const isActive = activeNodeId === n.id;
        const isSelected = selectedNodeId === n.id;
        const fromMatch = activeEvent.edge_from || activeEvent.dependsOn;
        const isEdgeSource = fromMatch === n.id;
        const kind = nodeKind(n);

        const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        g.setAttribute('class', 'graph-node' + (isSelected ? ' is-selected' : '') + (isActive ? ' is-active' : ''));
        g.setAttribute('data-id', n.id);
        g.setAttribute('data-role', n.role);
        g.setAttribute('data-active', isActive ? 'true' : 'false');
        g.setAttribute('tabindex', '0');
        g.setAttribute('role', 'button');
        g.setAttribute('aria-label', `${{kind.label}} ${{n.id}}, line ${{n.line || 'unknown'}}`);

        g.onclick = () => {{
          selectedNodeId = n.id;
          renderInspector();
          renderGraph();
        }};
        g.onmouseenter = () => highlightDependencies(n.id);
        g.onmouseleave = () => resetHighlight();

        const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        rect.setAttribute('x', p.x - (nodeWidth / 2));
        rect.setAttribute('y', p.y - (nodeHeight / 2));
        rect.setAttribute('width', nodeWidth);
        rect.setAttribute('height', nodeHeight);
        rect.setAttribute('rx', '9');

        let fillCol = isLight ? '#ffffff' : '#121b25';
        let strokeCol = isSelected ? (isLight ? '#0284c7' : '#63b3ff') : (isLight ? '#cbd5e1' : '#35475a');
        let strokeW = isSelected ? '2' : '1';
        let filterVal = isSelected ? (isLight ? 'drop-shadow(0 0 8px rgba(2,132,199,0.35))' : 'drop-shadow(0 0 9px rgba(99,179,255,0.36))') : 'url(#card-shadow)';

        if (isActive) {{
          fillCol = isLight ? `color-mix(in srgb, ${{kind.color}} 14%, #ffffff)` : `color-mix(in srgb, ${{kind.color}} 26%, #0f1722)`;
          strokeCol = kind.color;
          strokeW = '2.5';
          filterVal = isLight ? `drop-shadow(0 0 12px ${{kind.color}})` : `drop-shadow(0 0 16px ${{kind.color}})`;
        }} else if (isEdgeSource) {{
          fillCol = isLight ? 'color-mix(in srgb, #0284c7 12%, #ffffff)' : 'color-mix(in srgb, #38bdf8 18%, #0f1722)';
          strokeCol = isLight ? '#0284c7' : '#38bdf8';
          strokeW = '2';
          filterVal = isLight ? 'drop-shadow(0 0 8px rgba(2,132,199,0.3))' : 'drop-shadow(0 0 10px rgba(56,189,248,0.45))';
        }}

        rect.setAttribute('fill', fillCol);
        rect.setAttribute('stroke', strokeCol);
        rect.setAttribute('stroke-width', strokeW);
        rect.setAttribute('filter', filterVal);
        rect.setAttribute('class', 'node-card');
        g.appendChild(rect);

        const accent = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        accent.setAttribute('x', p.x - (nodeWidth / 2));
        accent.setAttribute('y', p.y - (nodeHeight / 2) + 6);
        accent.setAttribute('width', '4');
        accent.setAttribute('height', nodeHeight - 12);
        accent.setAttribute('rx', '2');
        accent.setAttribute('fill', kind.color);
        g.appendChild(accent);

        const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        text.setAttribute('x', p.x - (nodeWidth / 2) + 14);
        text.setAttribute('y', p.y - 4);
        text.setAttribute('fill', isLight ? '#0f172a' : '#edf4fb');
        text.setAttribute('font-family', 'var(--mono)');
        text.setAttribute('font-size', '12px');
        text.setAttribute('font-weight', '700');
        text.textContent = n.label || n.id;
        g.appendChild(text);

        const subText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        subText.setAttribute('x', p.x - (nodeWidth / 2) + 14);
        subText.setAttribute('y', p.y + 14);
        subText.setAttribute('fill', isLight ? '#64748b' : '#91a1b3');
        subText.setAttribute('font-size', '10px');
        subText.textContent = `${{kind.label}}${{n.line ? ' · line ' + n.line : ''}}`;
        g.appendChild(subText);

        svg.appendChild(g);
      }});
    }}

    function highlightDependencies(nodeId) {{
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
      document.querySelectorAll('.graph-edge').forEach(edge => {{
        edge.style.opacity = '0.75';
        edge.style.stroke = '#527494';
        edge.style.strokeWidth = '1.8px';
      }});
    }}

    function seekTo(step, fromVideo = false, mediaTime = null) {{
      const events = reactlogData.events || reactlogData.log || [];
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
      if (ev && (ev.node_id || ev.id)) {{
        selectedNodeId = ev.node_id || ev.id;
      }}
      renderInspector();
      renderGraph();
      updateSourceHighlight();
      updateActionToast();

      const evTime = ev && (ev.time_sec !== undefined ? ev.time_sec : ev.time);
      const curSec = fromVideo && mediaTime !== null
        ? mediaTime
        : (evTime !== undefined ? evTime : 0);
      updateTraceTimelineScrubber(curSec);

      if (!fromVideo) {{
        const video = document.getElementById('session-video');
        if (video && evTime !== undefined && !isNaN(evTime)) {{
          try {{
            video.currentTime = Math.max(0, evTime);
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
        toast.innerHTML = `${{ICONS.video}} ${{escapeHTML(timeStr)}}${{escapeHTML(ev.details || act)}}`;
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
        btn.innerHTML = playing ? ICONS.pause : ICONS.play;
        btn.setAttribute('aria-label', playing ? 'Pause recording' : 'Play recording');
        btn.title = playing ? 'Pause recording' : 'Play recording';
      }};

      const updateSyncStatus = (message) => {{
        if (syncStatus) syncStatus.textContent = `● ${{message}}`;
      }};

      const syncGraphToTime = (curSec) => {{
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
        if (video.duration && !isNaN(video.duration)) {{
          maxSessionDuration = Math.max(maxSessionDuration, video.duration);
          const totalDisplay = document.getElementById('trace-total-time');
          if (totalDisplay) totalDisplay.textContent = formatTime(maxSessionDuration);
          initTraceTimeline();
        }}
      }});

      video.addEventListener('play', () => {{
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
      const highlight = document.getElementById('source-line-highlight');
      if (!highlight) return;

      let targetLine = null;
      if (ev && (ev.node_id || ev.id)) {{
        const nid = ev.node_id || ev.id;
        const node = (reactlogData.nodes || []).find(n => n.id === nid);
        if (node && node.line) targetLine = node.line;
      }}

      if (targetLine !== null) {{
        highlight.hidden = false;
        highlight.setAttribute('data-line', String(targetLine));
        highlight.style.top = `${{(targetLine - 1) * 1.62}}em`;
        highlight.style.height = '1.62em';
      }} else {{
        highlight.hidden = true;
      }}
    }}

    function renderInspector() {{
      const events = reactlogData.events || reactlogData.log || [];
      const ev = events[currentStep];
      const node = (reactlogData.nodes || []).find(n => n.id === selectedNodeId);
      if (node) {{
        document.getElementById('insp-title').textContent = node.label || node.id;
        document.getElementById('insp-type').textContent = nodeKind(node).label;
        document.getElementById('insp-line').textContent = node.line || 'Unknown';
        const activeNodeId = ev ? (ev.node_id || ev.id) : null;
        document.getElementById('insp-status').textContent = ev && activeNodeId === node.id ? (ev.status || 'active') : 'idle';
      }} else if (ev) {{
        document.getElementById('insp-title').textContent = ev.node_label || ev.label || ev.action || ev.event;
        document.getElementById('insp-type').textContent = ev.phase === 'init' ? 'Initialization event' : 'Recorded event';
        document.getElementById('insp-line').textContent = '—';
        document.getElementById('insp-status').textContent = ev.status || 'idle';
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
      if (btn) btn.innerHTML = isPlaying ? ICONS.pause : ICONS.play;

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

    function handleSearch(q) {{
      searchQuery = (q || '').trim().toLowerCase();
      renderGraph();
    }}

    function toggleRoleFilter(role, btn) {{
      if (activeRoles.has(role)) {{
        activeRoles.delete(role);
        btn.setAttribute('aria-pressed', 'false');
      }} else {{
        activeRoles.add(role);
        btn.setAttribute('aria-pressed', 'true');
      }}
      renderGraph();
    }}

    function setupPanZoom() {{
      const svg = document.getElementById('reactlog-svg');
      svg.addEventListener('mousedown', e => {{
        if (e.target.closest('.graph-node')) return;
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
        zoomLevel = Math.max(0.4, Math.min(2.5, zoomLevel * delta));
        applyZoom();
      }});
    }}

    function applyZoom() {{
      const g = document.getElementById('viewport-g');
      if (g) g.setAttribute('transform', `translate(${{panOffset.x}}, ${{panOffset.y}}) scale(${{zoomLevel}})`);
    }}

    function zoomIn() {{ zoomLevel = Math.min(2.5, zoomLevel * 1.2); applyZoom(); }}
    function zoomOut() {{ zoomLevel = Math.max(0.4, zoomLevel * 0.8); applyZoom(); }}
    function resetZoom() {{ zoomLevel = 1; panOffset = {{ x: 0, y: 0 }}; applyZoom(); }}
    function fitGraph() {{ resetZoom(); }}

    function loadReactlogObject(loadedData) {{
      let normalized = loadedData;
      if (Array.isArray(loadedData) || (loadedData && (!loadedData.nodes || !loadedData.events))) {{
        const rawEvents = Array.isArray(loadedData) ? loadedData : (loadedData.log || loadedData.events || loadedData.entries || []);
        const nodesMap = {{}};
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
          const lbl = item.label || item.node_label || nid || '';
          const ntype = item.type || item.node_type || 'calc';
          const depFrom = item.depOnReactId || item.dependsOn || item.edge_from;
          const depTo = nid || item.reactId || item.edge_to;
          const rawT = Number(item.time || item.time_sec || (Number(item.timestamp || 0) / 1000.0) || 0);
          const tSec = Math.max(0, baseEpoch > 0 ? (rawT - baseEpoch) : rawT);
          const tMs = Number(item.timestamp || (tSec * 1000));
          const prov = item.provenance || (['valueChange', 'inputChange', 'userClick', 'userAction'].includes(act) ? 'observed' : 'inferred');
          const phase = item.phase || (['define', 'analysisInit', 'createContext', 'sessionInit'].includes(act) ? 'init' : 'interaction');

          if (act === 'dependsOn' && depFrom && depTo) {{
            edgesSet.add(`${{depFrom}}==>${{depTo}}`);
          }}

          if (nid && !nodesMap[nid]) {{
            let role = 'conductor';
            let ctype = String(ntype).toLowerCase();
            if (['observable', 'input'].includes(ctype) || String(nid).startsWith('input:') || String(nid).startsWith('input$')) {{
              role = 'source'; ctype = 'input';
            }} else if (['observer', 'output', 'effect'].includes(ctype) || String(nid).startsWith('output:') || String(nid).startsWith('output$') || String(nid).startsWith('effect:')) {{
              role = 'observer'; ctype = 'output';
            }}
            nodesMap[nid] = {{
              id: nid,
              name: String(nid).includes(':') ? String(nid).split(':')[1] : (String(nid).includes('$') ? String(nid).split('$')[1] : nid),
              type: ctype,
              role: role,
              label: lbl,
              line: item.line
            }};
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
            details: item.details || `Event ${{act}} on ${{lbl}}`
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
      selectedNodeId = null;
      currentStep = 0;
      init();
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

    window.addEventListener('DOMContentLoaded', init);
  </script>
</body>
</html>
"""
