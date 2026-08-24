from __future__ import annotations

import ast
import asyncio
import concurrent.futures
import html as html_lib
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

    def _handle_func_def(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        decorators: List[str] = [
            name for d in node.decorator_list if (name := self._get_decorator_name(d))
        ]

        is_effect = any("effect" in d or "Effect" in d for d in decorators)
        is_render = any(
            d.startswith("render.") or d.startswith("render_") for d in decorators
        )
        is_calc = any(
            ("calc" in d or "Calc" in d or "event" in d) and not is_effect
            for d in decorators
        )

        prev_out = self.current_output
        prev_effect = self.current_effect
        prev_calc = self.current_calc

        if is_render:
            self.current_output = node.name
            self.outputs[node.name] = {
                "line": node.lineno,
                "deps": set(),
                "calc_deps": set(),
                "is_async": isinstance(node, ast.AsyncFunctionDef),
            }
        elif is_effect:
            self.current_effect = node.name
            self.effects[node.name] = {
                "line": node.lineno,
                "deps": set(),
                "calc_deps": set(),
                "is_async": isinstance(node, ast.AsyncFunctionDef),
            }
        elif is_calc:
            self.current_calc = node.name
            self.calcs[node.name] = {
                "line": node.lineno,
                "deps": set(),
                "calc_deps": set(),
                "is_async": isinstance(node, ast.AsyncFunctionDef),
            }

        self.generic_visit(node)

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


def generate_reactlog(
    code: str,
    inputs: Optional[Dict[str, Any]] = None,
    recorded_actions: Optional[List[Dict[str, Any]]] = None,
    video_path: Optional[str] = None,
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
        {
            "step": step,
            "event": "analysisInit",
            "phase": "init",
            "provenance": "inferred",
            "timestamp": 0,
            "time_sec": 0.0,
            "node_id": None,
            "node_label": "session",
            "node_type": "session",
            "status": "active",
            "details": (
                "Initialized reactive session with recorded Playwright interactions"
                if recorded_actions
                else "Started static AST dependency analysis; app code was not executed"
            ),
        }
    )
    step += 1

    for node in nodes:
        events.append(
            {
                "step": step,
                "event": "define",
                "phase": "init",
                "provenance": "inferred",
                "timestamp": 0,
                "time_sec": 0.0,
                "node_id": node["id"],
                "node_label": node["label"],
                "node_type": node["role"],
                "status": "discovered",
                "details": f"Discovered {node['role']} node '{node['label']}' at line {node.get('line', '?')}",
            }
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
                    {
                        "step": cur_step,
                        "event": "propagate",
                        "phase": "interaction",
                        "provenance": "inferred",
                        "timestamp": ts_ms,
                        "time_sec": ts_s,
                        "node_id": down,
                        "node_label": down_lbl,
                        "node_type": node_obj.get("role", "conductor"),
                        "status": "affected",
                        "details": f"Inferred invalidation of '{down_lbl}' by '{nid_lbl}'",
                    }
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
                        {
                            "step": step,
                            "event": "inputChange",
                            "phase": "interaction",
                            "provenance": "observed",
                            "node_id": node_id,
                            "node_label": node_obj["label"],
                            "node_type": "source",
                            "status": "assumed",
                            "value": str(action_val),
                            "timestamp": ts_ms,
                            "time_sec": ts_sec,
                            "details": f"Observed browser input change: {node_obj['label']} = {action_val!r}",
                        }
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
                            {
                                "step": step,
                                "event": "wouldEvaluate",
                                "phase": "interaction",
                                "provenance": "inferred",
                                "node_id": tid,
                                "node_label": tlabel,
                                "node_type": trole,
                                "status": "scheduled",
                                "timestamp": ts_ms,
                                "time_sec": ts_sec,
                                "details": f"Inferred evaluation: '{tlabel}' (static topological order)",
                            }
                        )
                        step += 1

                        for dep in adj_upstream.get(tid, []):
                            dep_lbl = nodes_by_id.get(dep, {}).get("label", dep)
                            events.append(
                                {
                                    "step": step,
                                    "event": "dependsOn",
                                    "phase": "interaction",
                                    "provenance": "inferred",
                                    "node_id": tid,
                                    "node_label": tlabel,
                                    "node_type": trole,
                                    "status": "scheduled",
                                    "timestamp": ts_ms,
                                    "time_sec": ts_sec,
                                    "details": f"Inferred dependency: '{dep_lbl}' used by '{tlabel}'",
                                }
                            )
                            step += 1

                        events.append(
                            {
                                "step": step,
                                "event": "ordered",
                                "phase": "interaction",
                                "provenance": "inferred",
                                "node_id": tid,
                                "node_label": tlabel,
                                "node_type": trole,
                                "status": "scheduled",
                                "timestamp": ts_ms,
                                "time_sec": ts_sec,
                                "details": f"Inferred completed state for '{tlabel}'",
                            }
                        )
                        step += 1
                else:
                    unmatched_inputs.append(raw_name)
                    events.append(
                        {
                            "step": step,
                            "event": "inputChange",
                            "phase": "interaction",
                            "provenance": "observed",
                            "node_id": None,
                            "node_label": f"input.{raw_name}",
                            "node_type": "source",
                            "status": "assumed",
                            "value": str(action_val),
                            "timestamp": ts_ms,
                            "time_sec": ts_sec,
                            "details": f"Observed browser input change (unmatched node): input.{raw_name} = {action_val!r}",
                        }
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
                    {
                        "step": step,
                        "event": "outputUpdated",
                        "phase": "interaction",
                        "provenance": "observed",
                        "node_id": out_id,
                        "node_label": node_lbl,
                        "node_type": "observer",
                        "status": "scheduled",
                        "timestamp": ts_ms,
                        "time_sec": ts_sec,
                        "details": f"Observed browser output render: {node_lbl}",
                    }
                )
                step += 1

            elif action_type == "click":
                events.append(
                    {
                        "step": step,
                        "event": "userClick",
                        "phase": "interaction",
                        "provenance": "observed",
                        "node_id": None,
                        "node_label": raw_name,
                        "node_type": "user",
                        "status": "active",
                        "timestamp": ts_ms,
                        "time_sec": ts_sec,
                        "details": f"Observed user click: {action.get('text', raw_name)}",
                    }
                )
                step += 1

        events.append(
            {
                "step": step,
                "event": "recordingComplete",
                "phase": "interaction",
                "provenance": "inferred",
                "node_id": None,
                "node_label": "session",
                "node_type": "engine",
                "status": "idle",
                "timestamp": last_ts,
                "time_sec": round(last_ts / 1000.0, 2),
                "details": "Playwright recording complete",
            }
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
            "trace_kind": "inferred_simulation_with_recorded_browser_events",
            "nodes": nodes,
            "edges": edges,
            "events": events,
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
                    {
                        "step": cur_step,
                        "event": "propagate",
                        "phase": "interaction",
                        "provenance": "inferred",
                        "timestamp": 0,
                        "time_sec": 0.0,
                        "node_id": down,
                        "node_label": down_lbl,
                        "node_type": node_obj.get("role", "conductor"),
                        "status": "affected",
                        "details": f"Inferred invalidation of '{down_lbl}' from '{nid_lbl}'",
                    }
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
            {
                "step": step,
                "event": "assumeValue",
                "phase": "interaction",
                "provenance": "inferred",
                "timestamp": 0,
                "time_sec": 0.0,
                "node_id": node_id,
                "node_label": node_lbl,
                "node_type": "source",
                "status": "assumed",
                "value": str(input_val),
                "details": f"Simulation assumes {node_lbl} is set to {input_val!r}",
            }
        )
        step += 1
        step = cascade_invalidate(node_id, step)

    events.append(
        {
            "step": step,
            "event": "orderingStart",
            "phase": "interaction",
            "provenance": "inferred",
            "timestamp": 0,
            "time_sec": 0.0,
            "node_id": None,
            "node_label": "reactiveEnvironment",
            "node_type": "engine",
            "status": "active",
            "details": f"Simulating static ordering for {len(invalidated_nodes_static)} affected node(s)",
        }
    )
    step += 1

    eval_order = compute_evaluation_order(invalidated_nodes_static)
    for target in eval_order:
        tid = target["id"]
        tlabel = target["label"]
        trole = target["role"]

        events.append(
            {
                "step": step,
                "event": "wouldEvaluate",
                "phase": "interaction",
                "provenance": "inferred",
                "timestamp": 0,
                "time_sec": 0.0,
                "node_id": tid,
                "node_label": tlabel,
                "node_type": trole,
                "status": "scheduled",
                "details": f"Inferred evaluation: '{tlabel}' (static topological order; not executed)",
            }
        )
        step += 1

        for dep in adj_upstream.get(tid, []):
            dep_lbl = nodes_by_id.get(dep, {}).get("label", dep)
            events.append(
                {
                    "step": step,
                    "event": "dependsOn",
                    "phase": "interaction",
                    "provenance": "inferred",
                    "timestamp": 0,
                    "time_sec": 0.0,
                    "node_id": tid,
                    "node_label": tlabel,
                    "node_type": trole,
                    "status": "scheduled",
                    "details": f"Inferred dependency edge: '{dep_lbl}' used by '{tlabel}'",
                }
            )
            step += 1

        events.append(
            {
                "step": step,
                "event": "ordered",
                "phase": "interaction",
                "provenance": "inferred",
                "timestamp": 0,
                "time_sec": 0.0,
                "node_id": tid,
                "node_label": tlabel,
                "node_type": trole,
                "status": "scheduled",
                "details": f"Inferred completed state for '{tlabel}'",
            }
        )
        step += 1

    events.append(
        {
            "step": step,
            "event": "orderingComplete",
            "phase": "interaction",
            "provenance": "inferred",
            "timestamp": 0,
            "time_sec": 0.0,
            "node_id": None,
            "node_label": "reactiveEnvironment",
            "node_type": "engine",
            "status": "idle",
            "details": f"Static ordering contains {len(eval_order)} nodes; no reactive flush occurred",
        }
    )

    init_count = len([e for e in events if e.get("phase") == "init"])
    interact_count = len([e for e in events if e.get("phase") == "interaction"])
    first_interact = next(
        (i for i, e in enumerate(events) if e.get("phase") == "interaction"), 0
    )

    return {
        "success": True,
        "trace_kind": "static_inferred_simulation",
        "nodes": nodes,
        "edges": edges,
        "events": events,
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
                browser = p.chromium.connect(ws_endpoint)
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

            page.close()
            context.close()
            browser.close()

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
            <video id="session-video" controls preload="metadata">
              <source src="{rel_video}" type="video/webm">
              Your browser does not support the video tag.
            </video>
          </div>
          <div class="video-meta">
            <span class="video-badge">Playwright Video Recording</span>
            <span class="video-filename">{rel_video}</span>
          </div>
        </div>
        """

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

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{escaped_title}</title>
  <style>
    :root {{
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
      --mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      --sans: Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    button, input {{ font: inherit; }}
    button:focus-visible, input:focus-visible {{ outline: 2px solid var(--accent); outline-offset: 2px; }}
    body {{ background: var(--bg); color: var(--text); font-family: var(--sans); height: 100vh; display: flex; flex-direction: column; overflow: hidden; }}
    .app-header {{ min-height: 64px; background: rgba(17, 24, 33, 0.96); border-bottom: 1px solid var(--border); padding: 0.75rem 1.25rem; display: flex; justify-content: space-between; gap: 1rem; align-items: center; }}
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
    .btn.accent-skip {{ background: #2b2146; border-color: #63439b; color: #d8b4fe; }}
    .btn.accent-skip:hover {{ background: #3b2b63; border-color: #8b5cf6; }}
    .phase-selector {{ display: flex; background: var(--bg); border: 1px solid var(--border); border-radius: 8px; padding: 2px; gap: 2px; }}
    .phase-btn {{ background: transparent; border: none; color: var(--text-muted); padding: 0.3rem 0.65rem; border-radius: 6px; font: 700 0.7rem var(--mono); cursor: pointer; transition: all 120ms ease; }}
    .phase-btn:hover {{ color: var(--text); background: var(--surface-2); }}
    .phase-btn.is-active {{ background: var(--surface-3); color: var(--accent); box-shadow: 0 2px 8px rgba(0,0,0,0.2); }}
    .search-wrap {{ position: relative; flex: 0 1 200px; min-width: 130px; }}
    .search-wrap::before {{ content: "⌕"; position: absolute; left: 0.7rem; top: 50%; transform: translateY(-53%); color: var(--text-muted); font: 700 1rem var(--mono); pointer-events: none; }}
    .search-input {{ width: 100%; height: 34px; color: var(--text); background: var(--bg); border: 1px solid var(--border); border-radius: 7px; padding: 0 0.7rem 0 2rem; font-size: 0.76rem; }}
    .search-input::placeholder {{ color: #6f8194; }}
    .filter-btn[aria-pressed="true"] {{ color: var(--text); background: var(--surface-3); }}
    .filter-btn[data-role="source"][aria-pressed="true"] {{ border-color: var(--source); }}
    .filter-btn[data-role="conductor"][aria-pressed="true"] {{ border-color: var(--calc); }}
    .filter-btn[data-role="observer"][aria-pressed="true"] {{ border-color: var(--output); }}
    .scrubber {{ flex: 1; min-width: 130px; display: flex; align-items: center; gap: 0.6rem; }}
    .scrubber input[type="range"] {{ width: 100%; accent-color: var(--accent); cursor: pointer; }}
    .step-display {{ font: 700 0.72rem var(--mono); color: var(--accent); min-width: 80px; text-align: right; }}
    .main-view {{ display: grid; grid-template-columns: minmax(0, 1fr) 380px; flex: 1; min-height: 0; overflow: hidden; transition: grid-template-columns 180ms ease; }}
    .main-view.source-visible {{ grid-template-columns: minmax(0, 1fr) min(54vw, 680px); }}
    .main-view.sidebar-hidden {{ grid-template-columns: minmax(0, 1fr) 0; }}
    .graph-container {{ min-width: 0; min-height: 0; overflow: hidden; position: relative; background-color: var(--bg); background-image: linear-gradient(rgba(105, 128, 151, 0.055) 1px, transparent 1px), linear-gradient(90deg, rgba(105, 128, 151, 0.055) 1px, transparent 1px); background-size: 24px 24px; }}
    .graph-topbar {{ position: absolute; z-index: 3; top: 0.8rem; left: 0.8rem; right: 0.8rem; display: flex; align-items: flex-start; justify-content: space-between; gap: 0.75rem; pointer-events: none; }}
    .legend {{ display: flex; gap: 0.4rem; flex-wrap: wrap; padding: 0.4rem; border: 1px solid var(--border); border-radius: 9px; background: rgba(17, 24, 33, 0.9); backdrop-filter: blur(8px); box-shadow: 0 8px 30px rgba(0,0,0,0.18); pointer-events: auto; }}
    .legend-item {{ display: inline-flex; align-items: center; gap: 0.35rem; color: var(--text-muted); font: 650 0.66rem var(--mono); padding: 0.18rem 0.32rem; }}
    .legend-dot {{ width: 7px; height: 7px; border-radius: 50%; background: var(--role-color); box-shadow: 0 0 0 3px color-mix(in srgb, var(--role-color) 18%, transparent); }}
    .zoom-controls {{ display: flex; gap: 0.3rem; pointer-events: auto; }}
    .action-toast {{ position: absolute; z-index: 4; bottom: 1rem; left: 50%; transform: translateX(-50%); background: rgba(23, 33, 45, 0.95); border: 1px solid var(--accent); border-radius: 999px; padding: 0.45rem 1.1rem; color: var(--text); font: 650 0.76rem var(--mono); box-shadow: 0 10px 30px rgba(0,0,0,0.4); display: flex; align-items: center; gap: 0.6rem; pointer-events: none; animation: toast-pop 200ms ease; }}
    @keyframes toast-pop {{ from {{ opacity: 0; transform: translate(-50%, 8px); }} to {{ opacity: 1; transform: translate(-50%, 0); }} }}
    #reactlog-svg {{ width: 100%; height: 100%; min-height: 430px; display: block; }}
    .graph-node, .graph-edge {{ transition: opacity 160ms ease, filter 160ms ease, stroke 160ms ease, stroke-width 160ms ease; }}
    .graph-edge {{ opacity: 0.75; stroke: #527494; stroke-width: 1.8px; }}
    .graph-edge[data-active="true"] {{ opacity: 1 !important; stroke: #63b3ff !important; stroke-width: 2.8px !important; stroke-dasharray: 7 8; animation: edge-flow 900ms linear infinite; }}
    @keyframes edge-flow {{ to {{ stroke-dashoffset: -30; }} }}
    @media (prefers-reduced-motion: reduce) {{
      .graph-node, .graph-edge {{ transition: none; }}
      .graph-edge[data-active="true"] {{ animation: none; }}
    }}
    .graph-node {{ cursor: pointer; }}
    .graph-node:hover .node-card {{ filter: brightness(1.14); }}
    .graph-node.is-selected .node-card {{ filter: drop-shadow(0 0 9px rgba(99,179,255,0.36)); }}
    .stage-label {{ font: 700 10px var(--mono); fill: #718297; letter-spacing: 0.08em; }}
    .sidebar {{ min-width: 0; background: var(--surface); border-left: 1px solid var(--border); display: flex; flex-direction: column; overflow: hidden; }}
    .sidebar-header {{ min-height: 46px; padding: 0.7rem 0.8rem 0.65rem 1rem; border-bottom: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between; gap: 0.75rem; }}
    .sidebar-tabs {{ display: flex; align-items: center; gap: 0.25rem; }}
    .sidebar-tab {{ color: var(--text-muted); background: transparent; border: 1px solid transparent; border-radius: 6px; padding: 0.36rem 0.55rem; font-size: 0.7rem; font-weight: 800; letter-spacing: 0.06em; text-transform: uppercase; cursor: pointer; }}
    .sidebar-tab:hover {{ color: var(--text); background: var(--surface-2); }}
    .sidebar-tab[aria-selected="true"] {{ color: var(--text); background: var(--surface-3); border-color: var(--border); }}
    .sidebar-panel {{ min-height: 0; flex: 1; }}
    .sidebar-panel[hidden] {{ display: none; }}
    .timeline-panel {{ display: flex; flex-direction: column; }}
    .source-panel {{ position: relative; overflow: auto; padding: 1rem; background: #0c1219; color: #d9e7f5; font: 500 0.76rem/1.62 var(--mono); white-space: pre; tab-size: 4; }}
    .source-panel code {{ position: relative; z-index: 1; font: inherit; }}
    .source-line-highlight {{ position: absolute; z-index: 0; left: 0; right: 0; margin: 0; padding: 0; border: 0; border-left: 3px solid var(--source-highlight-color, var(--accent)); border-radius: 0; background: color-mix(in srgb, var(--source-highlight-color, var(--accent)) 16%, transparent); box-shadow: inset 0 1px color-mix(in srgb, var(--source-highlight-color, var(--accent)) 12%, transparent), inset 0 -1px color-mix(in srgb, var(--source-highlight-color, var(--accent)) 12%, transparent); pointer-events: none; transition: top 150ms ease, background 150ms ease; }}
    .source-line-highlight[hidden] {{ display: none; }}
    .video-panel {{ display: flex; flex-direction: column; padding: 1rem; gap: 0.8rem; background: #0c1219; overflow: auto; }}
    .video-container {{ width: 100%; border-radius: 8px; overflow: hidden; border: 1px solid var(--border); background: #000; }}
    .video-container video {{ width: 100%; display: block; }}
    .video-meta {{ display: flex; align-items: center; justify-content: space-between; gap: 0.5rem; flex-wrap: wrap; }}
    .video-badge {{ background: #193147; border: 1px solid #2d618d; color: #79c0ff; border-radius: 999px; padding: 0.2rem 0.55rem; font: 700 0.68rem var(--mono); }}
    .video-sync-status {{ color: #7ee787; font: 700 0.68rem var(--mono); display: inline-flex; align-items: center; gap: 0.3rem; }}
    .video-filename {{ color: var(--text-muted); font: 500 0.7rem var(--mono); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
    .syntax-keyword {{ color: #c792ea; font-weight: 700; }}
    .syntax-string {{ color: #a8d279; }}
    .syntax-number {{ color: #f6c177; }}
    .syntax-comment {{ color: #718096; font-style: italic; }}
    .event-list {{ flex: 1; overflow-y: auto; padding: 0.6rem; display: flex; flex-direction: column; gap: 0.35rem; }}
    .event-item {{ padding: 0.55rem 0.7rem; border-radius: 7px; border: 1px solid var(--border); background: var(--surface-2); cursor: pointer; display: flex; flex-direction: column; gap: 0.2rem; }}
    .event-item:hover {{ background: var(--surface-3); border-color: var(--border-strong); }}
    .event-item.is-current {{ border-color: var(--accent); background: color-mix(in srgb, var(--accent) 12%, var(--surface-2)); }}
    .event-header {{ display: flex; align-items: center; justify-content: space-between; gap: 0.5rem; }}
    .event-name {{ font: 700 0.76rem var(--mono); color: var(--text); }}
    .event-badges {{ display: flex; align-items: center; gap: 0.3rem; }}
    .event-time {{ font: 600 0.64rem var(--mono); color: #93c5fd; background: #13273b; border-radius: 4px; padding: 0.1rem 0.3rem; }}
    .event-badge {{ font: 700 0.62rem var(--mono); border-radius: 4px; padding: 0.1rem 0.35rem; text-transform: uppercase; }}
    .event-badge.provenance-observed {{ background: #0c2d48; color: #38bdf8; border: 1px solid #0284c7; }}
    .event-badge.provenance-inferred {{ background: #2d1847; color: #c084fc; border: 1px solid #7e22ce; }}
    .event-badge.assumed {{ background: #1b4728; color: #7ee787; }}
    .event-badge.affected {{ background: #4e3510; color: #f0883e; }}
    .event-badge.scheduled {{ background: #193147; color: #79c0ff; }}
    .event-badge.discovered {{ background: #262933; color: #a5d6ff; }}
    .event-badge.idle {{ background: #21262d; color: #8b949e; }}
    .event-badge.active {{ background: #3d2459; color: #d2a8ff; }}
    .event-details {{ font-size: 0.72rem; color: var(--text-muted); line-height: 1.35; }}
    .inspector-panel {{ border-top: 1px solid var(--border); padding: 0.8rem; background: var(--surface); }}
    .inspector-title {{ font: 700 0.8rem var(--mono); color: var(--text); margin-bottom: 0.4rem; }}
    .inspector-row {{ display: flex; justify-content: space-between; font-size: 0.74rem; padding: 0.2rem 0; }}
    .inspector-label {{ color: var(--text-muted); }}
    .inspector-val {{ font-family: var(--mono); color: var(--text); font-weight: 600; }}
  </style>
</head>
<body>
  <header class="app-header">
    <div class="brand">
      <div class="brand-mark" aria-hidden="true">⚡</div>
      <div class="brand-copy">
        <div class="brand-title">{escaped_title}</div>
        <div class="brand-subtitle">Interactive Shiny Reactive Log & Graph Explorer (Statically Inferred Dependency Execution)</div>
      </div>
    </div>
    <div class="stats">
      <span class="stat" id="stat-nodes">Nodes: 0</span>
      <span class="stat" id="stat-edges">Edges: 0</span>
      <span class="stat" id="stat-observed">👁️ Observed: 0</span>
      <span class="stat" id="stat-inferred">⚡ Inferred: 0</span>
    </div>
  </header>

  <main class="toolbar" role="toolbar" aria-label="Reactlog controls">
    <div class="toolbar-group">
      <button class="btn icon" id="btn-play" onclick="togglePlay()" aria-label="Play timeline" title="Play">▶</button>
      <button class="btn icon" onclick="stepBack()" aria-label="Step back" title="Step back">⏮</button>
      <button class="btn icon" onclick="stepForward()" aria-label="Step forward" title="Step forward">⏭</button>
      <button class="btn icon" onclick="resetTimeline()" aria-label="Reset timeline" title="Reset">↺</button>
    </div>

    <div class="toolbar-divider" aria-hidden="true"></div>

    <div class="phase-selector" role="group" aria-label="Timeline phase filter">
      <button class="phase-btn is-active" id="phase-btn-all" onclick="setPhaseFilter('all')">All (<span id="count-all">0</span>)</button>
      <button class="phase-btn" id="phase-btn-init" onclick="setPhaseFilter('init')">⚙️ Init (<span id="count-init">0</span>)</button>
      <button class="phase-btn" id="phase-btn-interaction" onclick="setPhaseFilter('interaction')">🎬 Actions (<span id="count-interaction">0</span>)</button>
    </div>

    <button class="btn accent-skip" id="btn-skip-init" onclick="skipToInteractions()" title="Skip initialization steps and start at first app action">⏭ Skip to Actions</button>

    <div class="toolbar-divider" aria-hidden="true"></div>

    <div class="scrubber">
      <input type="range" id="scrubber-range" min="0" max="0" value="0" oninput="seekTo(Number(this.value))" aria-label="Timeline step scrubber" />
      <span class="step-display" id="step-display">Step 0 / 0</span>
    </div>

    <div class="toolbar-divider" aria-hidden="true"></div>

    <div class="search-wrap">
      <input type="search" class="search-input" id="search-input" placeholder="Filter graph nodes..." oninput="handleSearch(this.value)" aria-label="Filter reactive nodes by name or type" />
    </div>

    <div class="toolbar-group">
      <button class="btn filter-btn" data-role="source" aria-pressed="true" onclick="toggleRoleFilter('source', this)">Inputs</button>
      <button class="btn filter-btn" data-role="conductor" aria-pressed="true" onclick="toggleRoleFilter('conductor', this)">Calcs</button>
      <button class="btn filter-btn" data-role="observer" aria-pressed="true" onclick="toggleRoleFilter('observer', this)">Outputs</button>
    </div>
  </main>

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
          <button class="btn icon" onclick="zoomIn()" aria-label="Zoom in" title="Zoom in">+</button>
          <button class="btn icon" onclick="zoomOut()" aria-label="Zoom out" title="Zoom out">−</button>
          <button class="btn icon" onclick="fitGraph()" aria-label="Fit graph to view" title="Fit to view">⊡</button>
          <button class="btn icon" onclick="resetZoom()" aria-label="Reset zoom" title="Reset zoom">1:1</button>
        </div>
      </div>
      <div id="live-action-toast" class="action-toast" hidden></div>
      <svg id="reactlog-svg" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto">
            <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#6685a3" />
          </marker>
          <marker id="arrow-active" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto">
            <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#63b3ff" />
          </marker>
          <marker id="arrow-invalidate" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto">
            <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#fb923c" />
          </marker>
          <filter id="card-shadow" x="-10%" y="-10%" width="120%" height="130%">
            <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#000" flood-opacity="0.32" />
          </filter>
        </defs>
        <g id="viewport-g"></g>
      </svg>
    </div>

    <aside class="sidebar" aria-label="Details and Timeline">
      <div class="sidebar-header">
        <div class="sidebar-tabs" role="tablist" aria-label="Sidebar views">
          <button class="sidebar-tab" id="timeline-tab" role="tab" aria-selected="true" aria-controls="timeline-panel" onclick="showSidebarPanel('timeline')">Timeline</button>
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

    function init() {{
      document.getElementById('stat-nodes').textContent = `Nodes: ${{reactlogData.nodes.length}}`;
      document.getElementById('stat-edges').textContent = `Edges: ${{reactlogData.edges.length}}`;
      const obsCount = reactlogData.observed_events_count !== undefined ? reactlogData.observed_events_count : reactlogData.events.reduce((acc, e) => acc + (e.provenance === 'observed' ? 1 : 0), 0);
      const infCount = reactlogData.inferred_events_count !== undefined ? reactlogData.inferred_events_count : reactlogData.events.reduce((acc, e) => acc + (e.provenance === 'inferred' ? 1 : 0), 0);
      document.getElementById('stat-observed').textContent = `👁️ Observed: ${{obsCount}}`;
      document.getElementById('stat-inferred').textContent = `⚡ Inferred: ${{infCount}}`;

      const initCount = reactlogData.init_steps_count !== undefined ? reactlogData.init_steps_count : reactlogData.events.reduce((acc, e) => acc + (e.phase === 'init' ? 1 : 0), 0);
      const interactCount = reactlogData.interaction_steps_count !== undefined ? reactlogData.interaction_steps_count : (reactlogData.events.length - initCount);
      document.getElementById('count-all').textContent = String(reactlogData.events.length);
      document.getElementById('count-init').textContent = String(initCount);
      document.getElementById('count-interaction').textContent = String(interactCount);

      const scrubber = document.getElementById('scrubber-range');
      scrubber.max = Math.max(0, reactlogData.events.length - 1);
      scrubber.value = 0;

      renderEventList();
      renderGraph();
      seekTo(0);
      setupPanZoom();
      setupVideoSync();
    }}

    function nodeKind(n) {{
      if (n.role === 'source') return {{ label: 'Input', color: '#38bdf8' }};
      if (n.role === 'conductor') return {{ label: 'Reactive Calc', color: '#fbbf24' }};
      if (n.type === 'effect') return {{ label: 'Effect', color: '#c084fc' }};
      return {{ label: 'Output', color: '#4ade80' }};
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
      const mainView = document.getElementById('main-view');
      if (panelName === 'source') {{
        mainView.classList.add('source-visible');
      }} else {{
        mainView.classList.remove('source-visible');
      }}
    }}

    function setPhaseFilter(phase) {{
      currentPhaseFilter = phase;
      ['all', 'init', 'interaction'].forEach(p => {{
        const btn = document.getElementById(`phase-btn-${{p}}`);
        if (btn) btn.classList.toggle('is-active', p === phase);
      }});
      renderEventList();
    }}

    function skipToInteractions() {{
      const firstActionIdx = reactlogData.first_interaction_step || 0;
      setPhaseFilter('interaction');
      seekTo(firstActionIdx);
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
      reactlogData.events.forEach((ev, idx) => {{
        if (currentPhaseFilter !== 'all' && ev.phase && ev.phase !== currentPhaseFilter) {{
          return;
        }}

        const item = document.createElement('div');
        item.className = 'event-item' + (idx === currentStep ? ' is-current' : '');
        item.setAttribute('data-step', String(idx));
        item.onclick = () => seekTo(idx);

        const header = document.createElement('div');
        header.className = 'event-header';

        const nameSpan = document.createElement('span');
        nameSpan.className = 'event-name';
        nameSpan.textContent = ev.node_label || ev.event;

        const badgesWrap = document.createElement('div');
        badgesWrap.className = 'event-badges';

        if (ev.time_sec !== undefined && ev.time_sec > 0) {{
          const timeSpan = document.createElement('span');
          timeSpan.className = 'event-time';
          timeSpan.textContent = formatTime(ev.time_sec);
          badgesWrap.appendChild(timeSpan);
        }}

        const provBadge = document.createElement('span');
        const prov = ev.provenance || 'inferred';
        provBadge.className = `event-badge provenance-${{prov}}`;
        provBadge.textContent = prov === 'observed' ? '👁️ OBSERVED' : '⚡ INFERRED';
        badgesWrap.appendChild(provBadge);

        const badge = document.createElement('span');
        badge.className = `event-badge ${{ev.status || 'idle'}}`;
        badge.textContent = ev.status || ev.event;
        badgesWrap.appendChild(badge);

        header.appendChild(nameSpan);
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

      const nodes = [];
      reactlogData.nodes.forEach(n => {{
        if (!activeRoles.has(n.role)) return;
        if (searchQuery && !n.id.toLowerCase().includes(searchQuery) && !(n.label || '').toLowerCase().includes(searchQuery)) return;
        nodes.push(n);
      }});

      const nodeSet = new Set(nodes.map(n => n.id));
      const edges = [];
      reactlogData.edges.forEach(e => {{
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

      const activeEvent = reactlogData.events[currentStep] || {{}};

      edges.forEach(e => {{
        const p1 = pos[e.from];
        const p2 = pos[e.to];
        if (p1 && p2) {{
          const x1 = p1.x + (nodeWidth / 2);
          const y1 = p1.y;
          const x2 = p2.x - (nodeWidth / 2);
          const y2 = p2.y;
          const midX = x1 + Math.max(35, (x2 - x1) * 0.5);

          const isEdgeActive = activeEvent.node_id === e.to && (activeEvent.event === 'dependsOn' || activeEvent.event === 'propagate');
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
        const isActive = activeEvent.node_id === n.id;
        const isSelected = selectedNodeId === n.id;
        const kind = nodeKind(n);

        const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        g.setAttribute('class', 'graph-node' + (isSelected ? ' is-selected' : ''));
        g.setAttribute('data-id', n.id);
        g.setAttribute('data-role', n.role);
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
        rect.setAttribute('fill', isActive ? '#192838' : '#121b25');
        rect.setAttribute('stroke', isActive ? '#63b3ff' : (isSelected ? '#63b3ff' : '#35475a'));
        rect.setAttribute('stroke-width', isActive || isSelected ? '2' : '1');
        rect.setAttribute('filter', 'url(#card-shadow)');
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
        text.setAttribute('fill', '#edf4fb');
        text.setAttribute('font-family', 'var(--mono)');
        text.setAttribute('font-size', '12px');
        text.setAttribute('font-weight', '700');
        text.textContent = n.label || n.id;
        g.appendChild(text);

        const subText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        subText.setAttribute('x', p.x - (nodeWidth / 2) + 14);
        subText.setAttribute('y', p.y + 14);
        subText.setAttribute('fill', '#91a1b3');
        subText.setAttribute('font-size', '10px');
        subText.textContent = `${{kind.label}} · line ${{n.line || '?'}}`;
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
          edge.style.stroke = '#63b3ff';
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

    function seekTo(step, fromVideo = false) {{
      currentStep = Math.max(0, Math.min(step, reactlogData.events.length - 1));
      document.getElementById('scrubber-range').value = currentStep;
      document.getElementById('step-display').textContent = `Step ${{currentStep}} / ${{Math.max(0, reactlogData.events.length - 1)}}`;

      document.querySelectorAll('.event-item').forEach(item => {{
        const stepNum = Number(item.getAttribute('data-step'));
        const isCur = stepNum === currentStep;
        item.classList.toggle('is-current', isCur);
        if (isCur) {{
          item.scrollIntoView({{ block: 'nearest', behavior: 'smooth' }});
        }}
      }});

      const ev = reactlogData.events[currentStep];
      if (ev && ev.node_id) {{
        selectedNodeId = ev.node_id;
      }}
      renderInspector();
      renderGraph();
      updateSourceHighlight();
      updateActionToast();

      if (!fromVideo) {{
        const video = document.getElementById('session-video');
        if (video && ev && ev.time_sec !== undefined && !isNaN(ev.time_sec)) {{
          try {{
            video.currentTime = Math.max(0, ev.time_sec);
          }} catch (e) {{}}
        }}
      }}
    }}

    function updateActionToast() {{
      const ev = reactlogData.events[currentStep];
      const toast = document.getElementById('live-action-toast');
      if (!toast) return;

      if (ev && ev.phase === 'interaction' && (ev.event === 'inputChange' || ev.event === 'userClick' || ev.event === 'outputUpdated')) {{
        const timeStr = ev.time_sec !== undefined ? `[${{formatTime(ev.time_sec)}}] ` : '';
        toast.textContent = `🎬 ${{timeStr}}${{ev.details || ev.event}}`;
        toast.hidden = false;
      }} else {{
        toast.hidden = true;
      }}
    }}

    function setupVideoSync() {{
      const video = document.getElementById('session-video');
      if (!video) return;

      video.addEventListener('timeupdate', () => {{
        if (isPlaying) return;
        const curSec = video.currentTime;
        let matchIdx = 0;
        for (let i = 0; i < reactlogData.events.length; i++) {{
          const ev = reactlogData.events[i];
          if (ev.time_sec !== undefined && ev.time_sec <= curSec) {{
            matchIdx = i;
          }}
        }}
        if (matchIdx !== currentStep) {{
          seekTo(matchIdx, true);
        }}
      }});
    }}

    function updateSourceHighlight() {{
      const ev = reactlogData.events[currentStep];
      const highlight = document.getElementById('source-line-highlight');
      if (!highlight) return;

      let targetLine = null;
      if (ev && ev.node_id) {{
        const node = reactlogData.nodes.find(n => n.id === ev.node_id);
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
      const node = reactlogData.nodes.find(n => n.id === selectedNodeId);
      if (node) {{
        document.getElementById('insp-title').textContent = node.label || node.id;
        document.getElementById('insp-type').textContent = nodeKind(node).label;
        document.getElementById('insp-line').textContent = node.line || 'Unknown';
        const ev = reactlogData.events[currentStep];
        document.getElementById('insp-status').textContent = ev && ev.node_id === node.id ? ev.status : 'idle';
      }}
    }}

    function togglePlay() {{
      isPlaying = !isPlaying;
      const btn = document.getElementById('btn-play');
      btn.textContent = isPlaying ? '⏸' : '▶';
      const video = document.getElementById('session-video');

      if (isPlaying) {{
        if (currentStep >= reactlogData.events.length - 1) currentStep = 0;
        if (video) {{
          video.play().catch(() => {{}});
        }}
        playTimer = setInterval(() => {{
          if (currentStep < reactlogData.events.length - 1) {{
            seekTo(currentStep + 1);
          }} else {{
            togglePlay();
          }}
        }}, 600);
      }} else {{
        if (video) {{
          video.pause();
        }}
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

    window.addEventListener('DOMContentLoaded', init);
  </script>
</body>
</html>
"""
