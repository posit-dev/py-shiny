from __future__ import annotations

import ast
import html as html_lib
import json
from collections import deque
from typing import Any, Dict, List, Optional, Set


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

    nodes: List[Dict[str, Any]] = []
    for inp, line in sorted(visitor.inputs.items()):
        nodes.append(
            {
                "id": inp,
                "type": "input",
                "role": "source",
                "label": f"input.{inp}",
                "line": line,
            }
        )
    for c, meta in sorted(visitor.calcs.items()):
        nodes.append(
            {
                "id": c,
                "type": "calc",
                "role": "conductor",
                "label": f"calc:{c}",
                "line": meta["line"],
            }
        )
    for eff, meta in sorted(visitor.effects.items()):
        nodes.append(
            {
                "id": eff,
                "type": "effect",
                "role": "observer",
                "label": f"effect:{eff}",
                "line": meta["line"],
            }
        )
    for out, meta in sorted(visitor.outputs.items()):
        nodes.append(
            {
                "id": out,
                "type": "output",
                "role": "observer",
                "label": f"output:{out}",
                "line": meta["line"],
            }
        )

    edges: List[Dict[str, str]] = []
    for out_name, meta in visitor.outputs.items():
        for dep in sorted(meta["deps"]):
            edges.append({"from": dep, "to": out_name})
        for cdep in sorted(meta["calc_deps"]):
            if cdep in known_calcs:
                edges.append({"from": cdep, "to": out_name})

    for eff_name, meta in visitor.effects.items():
        for dep in sorted(meta["deps"]):
            edges.append({"from": dep, "to": eff_name})
        for cdep in sorted(meta["calc_deps"]):
            if cdep in known_calcs:
                edges.append({"from": cdep, "to": eff_name})

    for calc_name, meta in visitor.calcs.items():
        for dep in sorted(meta["deps"]):
            edges.append({"from": dep, "to": calc_name})
        for cdep in sorted(meta["calc_deps"]):
            if cdep in known_calcs and cdep != calc_name:
                edges.append({"from": cdep, "to": calc_name})

    total_observers = len(visitor.outputs) + len(visitor.effects)
    return {
        "success": True,
        "nodes": nodes,
        "edges": edges,
        "summary": f"{len(visitor.inputs)} inputs (sources), {len(visitor.calcs)} reactives (conductors), {total_observers} outputs & effects (observers)",
    }


def generate_reactlog(
    code: str, inputs: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    graph = inspect_reactive_graph(code)
    if not graph.get("success"):
        return graph

    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])
    events: List[Dict[str, Any]] = []
    step = 0

    events.append(
        {
            "step": step,
            "event": "analysisInit",
            "node_id": None,
            "node_label": "session",
            "node_type": "session",
            "status": "active",
            "details": "Started static AST dependency analysis; app code was not executed",
        }
    )
    step += 1

    for node in nodes:
        events.append(
            {
                "step": step,
                "event": "define",
                "node_id": node["id"],
                "node_label": node["label"],
                "node_type": node["role"],
                "status": "discovered",
                "details": f"Found {node['role']} node at line {node.get('line', '?')}",
            }
        )
        step += 1

    adj_downstream: Dict[str, List[str]] = {}
    adj_upstream: Dict[str, List[str]] = {}
    for edge in edges:
        f, t = edge["from"], edge["to"]
        adj_downstream.setdefault(f, []).append(t)
        adj_upstream.setdefault(t, []).append(f)

    sim_inputs = dict(inputs or {})
    if not sim_inputs:
        input_nodes = [n for n in nodes if n["role"] == "source"]
        for n in input_nodes:
            sim_inputs[n["id"]] = 10

    invalidated_nodes: Set[str] = set()

    def cascade_invalidate(nid: str, cur_step: int) -> int:
        for down in adj_downstream.get(nid, []):
            if down not in invalidated_nodes:
                invalidated_nodes.add(down)
                events.append(
                    {
                        "step": cur_step,
                        "event": "propagate",
                        "node_id": down,
                        "node_label": next(
                            (n["label"] for n in nodes if n["id"] == down), down
                        ),
                        "node_type": next(
                            (n["role"] for n in nodes if n["id"] == down), "conductor"
                        ),
                        "status": "affected",
                        "details": f"Static dependency path propagates from '{nid}'",
                    }
                )
                cur_step += 1
                cur_step = cascade_invalidate(down, cur_step)
        return cur_step

    for input_id, val in sim_inputs.items():
        events.append(
            {
                "step": step,
                "event": "assumeValue",
                "node_id": input_id,
                "node_label": f"input.{input_id}",
                "node_type": "source",
                "status": "assumed",
                "value": str(val),
                "details": f"Assumed input value {val!r} for dependency analysis",
            }
        )
        step += 1
        step = cascade_invalidate(input_id, step)

    events.append(
        {
            "step": step,
            "event": "orderingStart",
            "node_id": None,
            "node_label": "reactiveEnvironment",
            "node_type": "engine",
            "status": "ordering",
            "details": f"Computing a possible topological order for {len(invalidated_nodes)} affected nodes",
        }
    )
    step += 1

    conductor_ids = {
        n["id"]
        for n in nodes
        if n["role"] == "conductor" and n["id"] in invalidated_nodes
    }
    conductor_in_degree: Dict[str, int] = {cid: 0 for cid in conductor_ids}
    for cid in conductor_ids:
        for up in adj_upstream.get(cid, []):
            if up in conductor_ids:
                conductor_in_degree[cid] += 1

    queue = deque([cid for cid, deg in sorted(conductor_in_degree.items()) if deg == 0])
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
        n for n in nodes if n["role"] == "observer" and n["id"] in invalidated_nodes
    ]

    nodes_by_id = {n["id"]: n for n in nodes}
    eval_order: List[Dict[str, Any]] = [
        nodes_by_id[cid] for cid in sorted_conductors if cid in nodes_by_id
    ] + observer_nodes

    for target in eval_order:
        tid = target["id"]
        tlabel = target["label"]
        trole = target["role"]

        events.append(
            {
                "step": step,
                "event": "wouldEvaluate",
                "node_id": tid,
                "node_label": tlabel,
                "node_type": trole,
                "status": "scheduled",
                "details": f"Static ordering places '{tid}' at this position; it was not executed",
            }
        )
        step += 1

        for dep in adj_upstream.get(tid, []):
            events.append(
                {
                    "step": step,
                    "event": "dependsOn",
                    "node_id": tid,
                    "node_label": tlabel,
                    "node_type": trole,
                    "status": "scheduled",
                    "details": f"AST inspection found dependency edge from '{dep}'",
                }
            )
            step += 1

        events.append(
            {
                "step": step,
                "event": "ordered",
                "node_id": tid,
                "node_label": tlabel,
                "node_type": trole,
                "status": "scheduled",
                "details": "Node placed in the simulated static order; no runtime result is known",
            }
        )
        step += 1

    events.append(
        {
            "step": step,
            "event": "orderingComplete",
            "node_id": None,
            "node_label": "reactiveEnvironment",
            "node_type": "engine",
            "status": "idle",
            "details": f"Static ordering contains {len(eval_order)} nodes; no reactive flush occurred",
        }
    )

    return {
        "success": True,
        "trace_kind": "static_dependency_simulation",
        "nodes": nodes,
        "edges": edges,
        "events": events,
        "steps_total": len(events),
        "summary": f"Static dependency simulation: {len(events)} steps across {len(nodes)} nodes ({len(invalidated_nodes)} affected); app code was not executed",
    }


def format_graph_mermaid(graph: Dict[str, Any]) -> str:
    lines = ["graph TD"]
    for node in graph.get("nodes", []):
        nid = node["id"].replace("-", "_").replace(".", "_")
        ntype = node.get("type", "")
        label = node.get("label", node["id"])
        if ntype == "input":
            lines.append(f'    {nid}["📥 {label}"]:::inputClass')
        elif ntype == "calc":
            lines.append(f'    {nid}["⚡ {label}"]:::calcClass')
        elif ntype == "effect":
            lines.append(f'    {nid}["🔔 {label}"]:::effectClass')
        else:
            lines.append(f'    {nid}["📊 {label}"]:::outputClass')

    for edge in graph.get("edges", []):
        f = edge["from"].replace("-", "_").replace(".", "_")
        t = edge["to"].replace("-", "_").replace(".", "_")
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
    for node in graph.get("nodes", []):
        nid = node["id"].replace("-", "_").replace(".", "_")
        label = node.get("label", node["id"])
        ntype = node.get("type", "")
        if ntype == "input":
            color = "#0284c7"
        elif ntype == "calc":
            color = "#d97706"
        elif ntype == "effect":
            color = "#9333ea"
        else:
            color = "#16a34a"
        lines.append(f'    "{nid}" [label="{label}", color="{color}"];')

    for edge in graph.get("edges", []):
        f = edge["from"].replace("-", "_").replace(".", "_")
        t = edge["to"].replace("-", "_").replace(".", "_")
        lines.append(f'    "{f}" -> "{t}";')

    lines.append("}")
    return "\n".join(lines)


def format_reactlog_html(
    reactlog: Dict[str, Any], title: str = "Static Shiny Dependency Simulation"
) -> str:
    escaped_title = html_lib.escape(title)
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
    .toolbar {{ min-height: 58px; background: var(--surface); border-bottom: 1px solid var(--border); padding: 0.65rem 1rem; display: flex; align-items: center; gap: 0.65rem; }}
    .toolbar-group {{ display: flex; align-items: center; gap: 0.35rem; }}
    .toolbar-divider {{ width: 1px; height: 28px; background: var(--border); margin: 0 0.2rem; }}
    .btn {{ min-height: 34px; background: var(--surface-2); border: 1px solid var(--border); color: var(--text); padding: 0.42rem 0.66rem; border-radius: 7px; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; gap: 0.38rem; transition: background 120ms ease, border-color 120ms ease, transform 120ms ease; font-size: 0.76rem; font-weight: 700; }}
    .btn:hover {{ background: var(--surface-3); border-color: var(--border-strong); }}
    .btn:active {{ transform: translateY(1px); }}
    .btn.icon {{ width: 34px; padding: 0; font-family: var(--mono); }}
    .btn.primary {{ background: #1f69a3; border-color: #2d86c8; }}
    .search-wrap {{ position: relative; flex: 0 1 240px; min-width: 150px; }}
    .search-wrap::before {{ content: "⌕"; position: absolute; left: 0.7rem; top: 50%; transform: translateY(-53%); color: var(--text-muted); font: 700 1rem var(--mono); pointer-events: none; }}
    .search-input {{ width: 100%; height: 34px; color: var(--text); background: var(--bg); border: 1px solid var(--border); border-radius: 7px; padding: 0 0.7rem 0 2rem; font-size: 0.76rem; }}
    .search-input::placeholder {{ color: #6f8194; }}
    .filter-btn[aria-pressed="true"] {{ color: var(--text); background: var(--surface-3); }}
    .filter-btn[data-role="source"][aria-pressed="true"] {{ border-color: var(--source); }}
    .filter-btn[data-role="conductor"][aria-pressed="true"] {{ border-color: var(--calc); }}
    .filter-btn[data-role="observer"][aria-pressed="true"] {{ border-color: var(--output); }}
    .scrubber {{ flex: 1; min-width: 130px; display: flex; align-items: center; gap: 0.6rem; }}
    .scrubber input[type="range"] {{ width: 100%; accent-color: var(--accent); cursor: pointer; }}
    .step-display {{ font: 700 0.72rem var(--mono); color: var(--accent); min-width: 72px; text-align: right; }}
    .main-view {{ display: grid; grid-template-columns: minmax(0, 1fr) 360px; flex: 1; min-height: 0; overflow: hidden; transition: grid-template-columns 180ms ease; }}
    .main-view.sidebar-hidden {{ grid-template-columns: minmax(0, 1fr) 0; }}
    .graph-container {{ min-width: 0; min-height: 0; overflow: hidden; position: relative; background-color: var(--bg); background-image: linear-gradient(rgba(105, 128, 151, 0.055) 1px, transparent 1px), linear-gradient(90deg, rgba(105, 128, 151, 0.055) 1px, transparent 1px); background-size: 24px 24px; }}
    .graph-topbar {{ position: absolute; z-index: 3; top: 0.8rem; left: 0.8rem; right: 0.8rem; display: flex; align-items: flex-start; justify-content: space-between; gap: 0.75rem; pointer-events: none; }}
    .legend {{ display: flex; gap: 0.4rem; flex-wrap: wrap; padding: 0.4rem; border: 1px solid var(--border); border-radius: 9px; background: rgba(17, 24, 33, 0.9); backdrop-filter: blur(8px); box-shadow: 0 8px 30px rgba(0,0,0,0.18); pointer-events: auto; }}
    .legend-item {{ display: inline-flex; align-items: center; gap: 0.35rem; color: var(--text-muted); font: 650 0.66rem var(--mono); padding: 0.18rem 0.32rem; }}
    .legend-dot {{ width: 7px; height: 7px; border-radius: 50%; background: var(--role-color); box-shadow: 0 0 0 3px color-mix(in srgb, var(--role-color) 18%, transparent); }}
    .zoom-controls {{ display: flex; gap: 0.3rem; pointer-events: auto; }}
    #reactlog-svg {{ width: 100%; height: 100%; min-height: 430px; display: block; }}
    .graph-node, .graph-edge {{ transition: opacity 160ms ease, filter 160ms ease, stroke 160ms ease, stroke-width 160ms ease; }}
    .graph-edge {{ opacity: 0; pointer-events: none; }}
    .graph-edge[data-active="true"] {{ stroke-dasharray: 7 8; animation: edge-flow 900ms linear infinite; }}
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
    .sidebar-title {{ font-size: 0.72rem; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; color: var(--text-muted); }}
    .inspector {{ margin: 0.75rem; padding: 0.85rem; background: var(--surface-2); border: 1px solid var(--border); border-radius: 9px; }}
    .inspector-eyebrow {{ display: flex; align-items: center; justify-content: space-between; gap: 0.5rem; margin-bottom: 0.55rem; }}
    .inspector-node {{ font: 700 0.88rem var(--mono); color: var(--text); overflow-wrap: anywhere; }}
    .inspector-detail {{ color: var(--text-muted); font-size: 0.75rem; line-height: 1.45; margin-top: 0.35rem; }}
    .event-list {{ flex: 1; overflow-y: auto; padding: 0 0.5rem 0.75rem; list-style: none; }}
    .event-item {{ padding: 0.58rem 0.65rem; border-radius: 7px; font-size: 0.76rem; margin-bottom: 0.22rem; border: 1px solid transparent; cursor: pointer; transition: background 120ms ease, border-color 120ms ease; }}
    .event-item:hover {{ background: var(--surface-2); }}
    .event-item.active {{ background: rgba(99, 179, 255, 0.1); border-color: rgba(99, 179, 255, 0.62); }}
    .event-row {{ display: flex; align-items: center; justify-content: space-between; gap: 0.5rem; }}
    .event-node {{ color: var(--text); font: 650 0.73rem var(--mono); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
    .event-step {{ color: #708195; font: 600 0.65rem var(--mono); }}
    .badge {{ display: inline-flex; align-items: center; max-width: 100%; font: 750 0.6rem var(--mono); padding: 0.16rem 0.35rem; border-radius: 4px; text-transform: uppercase; letter-spacing: 0.025em; background: var(--surface-3); color: var(--text-muted); }}
    .badge.assumeValue {{ background: rgba(56,189,248,0.13); color: #7dd3fc; }}
    .badge.propagate {{ background: rgba(251,146,60,0.13); color: #fdba74; }}
    .badge.wouldEvaluate, .badge.dependsOn {{ background: rgba(99,179,255,0.13); color: #93c5fd; }}
    .badge.ordered {{ background: rgba(74,222,128,0.13); color: #86efac; }}
    .sidebar-hidden .sidebar {{ visibility: hidden; }}
    @media (max-width: 980px) {{
      .app-header {{ align-items: flex-start; }}
      .stats .stat.summary {{ display: none; }}
      .toolbar {{ flex-wrap: wrap; }}
      .toolbar .scrubber {{ order: 3; flex-basis: 100%; }}
      .main-view {{ grid-template-columns: minmax(0, 1fr) 310px; }}
    }}
    @media (max-width: 720px) {{
      body {{ overflow: auto; min-height: 100vh; }}
      .app-header {{ position: static; }}
      .brand-subtitle, .stats {{ display: none; }}
      .toolbar-divider, .filter-btn {{ display: none; }}
      .search-wrap {{ flex: 1; }}
      .main-view, .main-view.sidebar-hidden {{ display: grid; grid-template-columns: 1fr; grid-template-rows: minmax(460px, 60vh) 320px; overflow: visible; }}
      .graph-container {{ overflow: auto; }}
      #reactlog-svg {{ width: 1400px; max-width: none; }}
      .sidebar {{ border-left: 0; border-top: 1px solid var(--border); visibility: visible !important; }}
      .sidebar-toggle {{ display: none; }}
    }}
  </style>
</head>
<body>
  <header class="app-header">
    <div class="brand">
      <div class="brand-mark" aria-hidden="true">S</div>
      <div class="brand-copy">
        <div class="brand-title">Reactive dependency explorer</div>
        <div class="brand-subtitle">Static simulation · app code is not executed</div>
      </div>
    </div>
    <div class="stats" id="graph-stats" aria-label="Graph summary"></div>
  </header>
  <nav class="toolbar" aria-label="Graph controls">
    <div class="toolbar-group" aria-label="Timeline playback">
      <button class="btn icon" onclick="firstStep()" aria-label="First event" title="First event">|‹</button>
      <button class="btn icon" onclick="prevStep()" aria-label="Previous event" title="Previous event">‹</button>
      <button class="btn primary" id="play-btn" onclick="togglePlay()" aria-label="Play timeline"><span aria-hidden="true">▶</span> Play</button>
      <button class="btn icon" onclick="nextStep()" aria-label="Next event" title="Next event">›</button>
      <button class="btn icon" onclick="lastStep()" aria-label="Last event" title="Last event">›|</button>
    </div>
    <div class="toolbar-divider" aria-hidden="true"></div>
    <label class="search-wrap">
      <span style="position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0,0,0,0)">Search graph nodes</span>
      <input id="node-search" class="search-input" type="search" aria-label="Search graph nodes" placeholder="Find a reactive…" oninput="applyGraphFilters()" />
    </label>
    <div class="toolbar-group" aria-label="Node type filters">
      <button class="btn filter-btn" data-role="source" aria-pressed="true" onclick="toggleRole(this)">Inputs</button>
      <button class="btn filter-btn" data-role="conductor" aria-pressed="true" onclick="toggleRole(this)">Calcs</button>
      <button class="btn filter-btn" data-role="observer" aria-pressed="true" onclick="toggleRole(this)">Observers</button>
    </div>
    <div class="toolbar-divider" aria-hidden="true"></div>
    <div class="scrubber">
      <input type="range" id="scrubber-range" min="0" value="0" aria-label="Timeline event" oninput="setStep(parseInt(this.value))" />
      <div class="step-display" id="step-counter" role="status" aria-live="polite">0 / 0</div>
    </div>
  </nav>
  <main class="main-view" id="main-view">
    <section class="graph-container" id="graph-viewport" aria-label="Reactive dependency graph">
      <div class="graph-topbar">
        <div class="legend" aria-label="Node type legend">
          <span class="legend-item" style="--role-color:var(--source)"><span class="legend-dot"></span>Input</span>
          <span class="legend-item" style="--role-color:var(--calc)"><span class="legend-dot"></span>Calculation</span>
          <span class="legend-item" style="--role-color:var(--effect)"><span class="legend-dot"></span>Effect</span>
          <span class="legend-item" style="--role-color:var(--output)"><span class="legend-dot"></span>Output</span>
          <span class="legend-item" title="Hover or keyboard-focus a node to reveal its dependency path">⇢ Hover to trace</span>
        </div>
        <div class="zoom-controls" aria-label="Graph zoom">
          <button class="btn icon" onclick="zoomGraph(1.2)" aria-label="Zoom in" title="Zoom in">+</button>
          <button class="btn icon" onclick="zoomGraph(0.8)" aria-label="Zoom out" title="Zoom out">−</button>
          <button class="btn" onclick="fitGraph()" aria-label="Fit graph to view" title="Fit graph to view">Fit</button>
          <button class="btn sidebar-toggle" id="sidebar-toggle" onclick="toggleSidebar()" aria-label="Hide timeline" title="Show or hide timeline">Timeline ›</button>
        </div>
      </div>
      <svg id="reactlog-svg" role="img" aria-label="Layered reactive dependency graph"></svg>
    </section>
    <aside class="sidebar" aria-label="Dependency details and event timeline">
      <div class="sidebar-header">
        <span class="sidebar-title">Timeline</span>
      </div>
      <div class="inspector" id="active-inspector" aria-live="polite"></div>
      <ul class="event-list" id="event-list"></ul>
    </aside>
  </main>
  <script>
    const LOG_DATA = {escaped_json};
    let currentStep = 0;
    let isPlaying = false;
    let playTimer = null;
    let zoomLevel = 1;
    let graphBounds = {{ width: 900, height: 560 }};
    let selectedNodeId = null;

    const totalSteps = (LOG_DATA.events || []).length;
    document.getElementById('scrubber-range').max = Math.max(0, totalSteps - 1);
    const nodeCounts = (LOG_DATA.nodes || []).reduce((counts, node) => {{
      counts[node.type] = (counts[node.type] || 0) + 1;
      return counts;
    }}, {{}});
    document.getElementById('graph-stats').innerHTML = [
      `<span class="stat">${{(LOG_DATA.nodes || []).length}} nodes</span>`,
      `<span class="stat">${{(LOG_DATA.edges || []).length}} dependencies</span>`,
      `<span class="stat summary">static trace</span>`
    ].join('');

    function eventName(name) {{
      return String(name || 'event').replace(/([a-z])([A-Z])/g, '$1 $2');
    }}

    function nodeKind(node) {{
      if (node.type === 'input') return {{ label: 'INPUT', color: '#38bdf8', glyph: 'I' }};
      if (node.type === 'effect') return {{ label: 'EFFECT', color: '#c084fc', glyph: 'E' }};
      if (node.type === 'output') return {{ label: 'OUTPUT', color: '#4ade80', glyph: 'O' }};
      return {{ label: 'CALC', color: '#fbbf24', glyph: 'C' }};
    }}

    function truncate(value, maxLength) {{
      const text = String(value || '');
      return text.length > maxLength ? text.slice(0, maxLength - 1) + '…' : text;
    }}

    function renderInspector() {{
      const inspector = document.getElementById('active-inspector');
      const event = (LOG_DATA.events || [])[currentStep];
      const selectedNode = (LOG_DATA.nodes || []).find(node => node.id === selectedNodeId);
      if (selectedNode) {{
        const kind = nodeKind(selectedNode);
        const incoming = (LOG_DATA.edges || []).filter(edge => edge.to === selectedNode.id).length;
        const outgoing = (LOG_DATA.edges || []).filter(edge => edge.from === selectedNode.id).length;
        inspector.innerHTML = '<div class="inspector-eyebrow"><span class="badge"></span><span class="event-step"></span></div><div class="inspector-node"></div><div class="inspector-detail"></div>';
        inspector.querySelector('.badge').textContent = kind.label;
        inspector.querySelector('.event-step').textContent = `line ${{selectedNode.line || '—'}}`;
        inspector.querySelector('.inspector-node').textContent = selectedNode.id;
        inspector.querySelector('.inspector-detail').textContent = `${{incoming}} upstream · ${{outgoing}} downstream. Select an event below to return to timeline details.`;
        return;
      }}
      if (!event) {{
        inspector.innerHTML = '<div class="inspector-node">No simulated events</div><div class="inspector-detail">The dependency graph is still available to explore.</div>';
        return;
      }}
      inspector.innerHTML = '<div class="inspector-eyebrow"><span class="badge"></span><span class="event-step"></span></div><div class="inspector-node"></div><div class="inspector-detail"></div>';
      const badge = inspector.querySelector('.badge');
      badge.textContent = eventName(event.event);
      if (/^[A-Za-z][A-Za-z0-9_-]*$/.test(event.event || '')) badge.classList.add(event.event);
      inspector.querySelector('.event-step').textContent = `#${{event.step ?? currentStep}}`;
      inspector.querySelector('.inspector-node').textContent = event.node_label || 'Reactive environment';
      inspector.querySelector('.inspector-detail').textContent = event.details || '';
    }}

    function renderEventsList() {{
      const list = document.getElementById('event-list');
      list.innerHTML = '';
      (LOG_DATA.events || []).forEach((ev, idx) => {{
        const li = document.createElement('li');
        li.className = 'event-item' + (idx === currentStep ? ' active' : '');
        li.onclick = () => {{ selectedNodeId = null; setStep(idx); }};

        const headerDiv = document.createElement('div');
        headerDiv.className = 'event-row';

        const badge = document.createElement('span');
        badge.className = 'badge ' + (ev.event || '');
        badge.textContent = eventName(ev.event);

        const stepNum = document.createElement('span');
        stepNum.className = 'event-step';
        stepNum.textContent = '#' + (ev.step != null ? ev.step : idx);

        headerDiv.appendChild(badge);
        headerDiv.appendChild(stepNum);

        const titleDiv = document.createElement('div');
        titleDiv.className = 'event-node';
        titleDiv.textContent = ev.node_label || 'Reactive environment';

        li.appendChild(headerDiv);
        li.appendChild(titleDiv);
        list.appendChild(li);
      }});
    }}

    function renderGraph() {{
      const svg = document.getElementById('reactlog-svg');
      svg.innerHTML = '<defs>' +
        '<filter id="card-shadow" x="-20%" y="-30%" width="140%" height="170%"><feDropShadow dx="0" dy="5" stdDeviation="7" flood-color="#000000" flood-opacity="0.28"/></filter>' +
        '<filter id="edge-glow" x="-30%" y="-50%" width="160%" height="200%"><feGaussianBlur stdDeviation="2.2" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>' +
        '<marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M 1 1.5 L 8 5 L 1 8.5" fill="none" stroke="#6685a3" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></marker>' +
        '<marker id="arrow-hover" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M 1 1.5 L 8 5 L 1 8.5" fill="none" stroke="#9bd3ff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></marker>' +
        '<marker id="arrow-active" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M 1 1.5 L 8 5 L 1 8.5" fill="none" stroke="#63b3ff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></marker>' +
        '<marker id="arrow-invalidate" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M 1 1.5 L 8 5 L 1 8.5" fill="none" stroke="#fb923c" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></marker>' +
        '</defs>';

      const nodes = LOG_DATA.nodes || [];
      const edges = LOG_DATA.edges || [];
      const activeEvent = LOG_DATA.events[currentStep] || {{}};

      const inEdges = {{}};
      const outEdges = {{}};
      nodes.forEach(n => {{ inEdges[n.id] = []; outEdges[n.id] = []; }});
      edges.forEach(e => {{
        if (outEdges[e.from]) outEdges[e.from].push(e.to);
        if (inEdges[e.to]) inEdges[e.to].push(e.from);
      }});

      const ranks = {{}};
      nodes.forEach(n => {{
        if (n.role === 'source' || inEdges[n.id].length === 0) {{
          ranks[n.id] = 0;
        }}
      }});

      let changed = true;
      let iterations = 0;
      while (changed && iterations < 30) {{
        changed = false;
        iterations++;
        edges.forEach(e => {{
          const rFrom = ranks[e.from] ?? 0;
          const curTo = ranks[e.to] ?? 0;
          if (rFrom + 1 > curTo) {{
            ranks[e.to] = rFrom + 1;
            changed = true;
          }}
        }});
      }}

      const maxRank = Math.max(0, ...Object.values(ranks));
      const columns = Array.from({{ length: maxRank + 1 }}, () => []);
      nodes.forEach(n => {{
        const r = ranks[n.id] || 0;
        columns[r].push(n);
      }});

      columns.forEach(column => column.sort((a, b) => String(a.id).localeCompare(String(b.id))));
      for (let colIdx = 1; colIdx < columns.length; colIdx++) {{
        const previousOrder = new Map();
        columns.slice(0, colIdx).flat().forEach((node, idx) => previousOrder.set(node.id, idx));
        columns[colIdx].sort((a, b) => {{
          const barycenter = node => {{
            const parents = edges.filter(edge => edge.to === node.id).map(edge => previousOrder.get(edge.from)).filter(value => value != null);
            return parents.length ? parents.reduce((sum, value) => sum + value, 0) / parents.length : Number.MAX_SAFE_INTEGER;
          }};
          return barycenter(a) - barycenter(b) || String(a.id).localeCompare(String(b.id));
        }});
      }}

      const colWidth = 292;
      const rowHeight = 92;
      const nodeWidth = 224;
      const nodeHeight = 62;
      const maxInCol = Math.max(1, ...columns.map(c => c.length));
      const svgHeight = Math.max(560, maxInCol * rowHeight + 150);
      const svgWidth = Math.max(920, (maxRank + 1) * colWidth + 100);
      graphBounds = {{ width: svgWidth, height: svgHeight }};

      svg.setAttribute('width', '100%');
      svg.setAttribute('height', '100%');
      applyZoom();

      const pos = {{}};
      columns.forEach((colNodes, colIdx) => {{
        const colX = 162 + colIdx * colWidth;
        const totalH = (colNodes.length - 1) * rowHeight;
        const startY = 116 + (svgHeight - 150 - totalH) / 2;

        const stageBand = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        stageBand.setAttribute('x', colX - (colWidth / 2) + 14);
        stageBand.setAttribute('y', '72');
        stageBand.setAttribute('width', colWidth - 28);
        stageBand.setAttribute('height', svgHeight - 100);
        stageBand.setAttribute('rx', '14');
        stageBand.setAttribute('fill', colIdx % 2 === 0 ? '#0d141c' : '#0b1118');
        stageBand.setAttribute('stroke', '#1c2936');
        stageBand.setAttribute('stroke-width', '1');
        stageBand.setAttribute('pointer-events', 'none');
        svg.appendChild(stageBand);

        const stageHeader = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        stageHeader.setAttribute('x', colX);
        stageHeader.setAttribute('y', 54);
        stageHeader.setAttribute('class', 'stage-label');
        stageHeader.setAttribute('text-anchor', 'middle');
        stageHeader.textContent = colIdx === 0 ? 'INPUTS' : (colIdx === maxRank ? 'FINAL OBSERVERS' : `REACTIVE STAGE ${{colIdx}}`);
        svg.appendChild(stageHeader);

        colNodes.forEach((n, rowIdx) => {{
          pos[n.id] = {{
            x: colX,
            y: startY + rowIdx * rowHeight,
            rank: colIdx
          }};
        }});
      }});

      edges.forEach(e => {{
        const p1 = pos[e.from];
        const p2 = pos[e.to];
        if (p1 && p2) {{
          const x1 = p1.x + (nodeWidth / 2);
          const y1 = p1.y;
          const x2 = p2.x - (nodeWidth / 2);
          const y2 = p2.y;
          const midX = x1 + Math.max(42, (x2 - x1) * 0.5);

          const isEdgeActive = activeEvent.node_id === e.to &&
            activeEvent.event === 'dependsOn' &&
            activeEvent.details &&
            activeEvent.details.includes(`'${{e.from}}'`);

          const isInvalidateEdge = activeEvent.event === 'propagate' &&
            activeEvent.node_id === e.to &&
            activeEvent.details &&
            activeEvent.details.includes(`'${{e.from}}'`);

          const isStepContext = Boolean(activeEvent.node_id) &&
            (activeEvent.node_id === e.from || activeEvent.node_id === e.to);

          const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
          path.setAttribute('d', `M ${{x1}} ${{y1}} C ${{midX}} ${{y1}}, ${{midX}} ${{y2}}, ${{x2}} ${{y2}}`);
          path.setAttribute('fill', 'none');
          path.setAttribute('stroke-linecap', 'round');
          path.setAttribute('data-from', e.from);
          path.setAttribute('data-to', e.to);
          path.setAttribute('data-active', isEdgeActive || isInvalidateEdge ? 'true' : 'false');
          path.setAttribute('data-context', isStepContext ? 'true' : 'false');
          path.setAttribute('data-tone', isInvalidateEdge ? 'warning' : 'accent');
          path.setAttribute('class', 'graph-edge');

          if (isEdgeActive) {{
            path.setAttribute('stroke', '#63b3ff');
            path.setAttribute('stroke-width', '3');
            path.setAttribute('marker-end', 'url(#arrow-active)');
          }} else if (isInvalidateEdge) {{
            path.setAttribute('stroke', '#fb923c');
            path.setAttribute('stroke-width', '3');
            path.setAttribute('marker-end', 'url(#arrow-invalidate)');
          }} else {{
            path.setAttribute('stroke', '#6685a3');
            path.setAttribute('stroke-width', '1.7');
            path.setAttribute('marker-end', 'url(#arrow)');
          }}

          svg.appendChild(path);
        }}
      }});

      nodes.forEach(n => {{
        const p = pos[n.id] || {{ x: 200, y: 200 }};
        const isActive = activeEvent.node_id === n.id;
        const isSelected = selectedNodeId === n.id;
        const kind = nodeKind(n);
        let strokeColor = isSelected ? '#63b3ff' : '#35475a';
        let fillColor = '#121b25';

        if (isActive) {{
          fillColor = '#192737';
          if (activeEvent.status === 'affected') strokeColor = '#d29922';
          else if (activeEvent.status === 'scheduled') strokeColor = '#58a6ff';
          else if (activeEvent.status === 'assumed') strokeColor = '#3fb950';
        }}

        const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        g.setAttribute('class', 'graph-node' + (isSelected ? ' is-selected' : ''));
        g.setAttribute('data-id', n.id);
        g.setAttribute('data-role', n.role);
        g.setAttribute('tabindex', '0');
        g.setAttribute('role', 'button');
        g.setAttribute('aria-label', `${{kind.label.toLowerCase()}} ${{n.id}}, line ${{n.line || 'unknown'}}`);

        g.onclick = () => {{
          selectedNodeId = n.id;
          renderInspector();
          renderGraph();
        }};
        g.onkeydown = event => {{
          if (event.key === 'Enter' || event.key === ' ') {{
            event.preventDefault();
            g.onclick();
          }}
        }};

        g.onmouseenter = () => highlightDependencies(n.id);
        g.onmouseleave = () => resetHighlight();
        g.onfocus = () => highlightDependencies(n.id);
        g.onblur = () => resetHighlight();

        const title = document.createElementNS('http://www.w3.org/2000/svg', 'title');
        title.textContent = `${{n.label || n.id}} · ${{kind.label.toLowerCase()}} · line ${{n.line || 'unknown'}}`;
        g.appendChild(title);

        const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        rect.setAttribute('x', p.x - (nodeWidth / 2));
        rect.setAttribute('y', p.y - (nodeHeight / 2));
        rect.setAttribute('width', nodeWidth);
        rect.setAttribute('height', nodeHeight);
        rect.setAttribute('rx', '10');
        rect.setAttribute('fill', fillColor);
        rect.setAttribute('stroke', strokeColor);
        rect.setAttribute('stroke-width', isActive || isSelected ? '2' : '1');
        rect.setAttribute('filter', 'url(#card-shadow)');
        rect.setAttribute('class', 'node-card');
        g.appendChild(rect);

        const accent = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        accent.setAttribute('x', p.x - (nodeWidth / 2));
        accent.setAttribute('y', p.y - (nodeHeight / 2) + 8);
        accent.setAttribute('width', '4');
        accent.setAttribute('height', nodeHeight - 16);
        accent.setAttribute('rx', '2');
        accent.setAttribute('fill', kind.color);
        g.appendChild(accent);

        const glyphBg = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        glyphBg.setAttribute('cx', p.x - 82);
        glyphBg.setAttribute('cy', p.y);
        glyphBg.setAttribute('r', '15');
        glyphBg.setAttribute('fill', kind.color);
        glyphBg.setAttribute('fill-opacity', '0.14');
        glyphBg.setAttribute('stroke', kind.color);
        glyphBg.setAttribute('stroke-opacity', '0.42');
        g.appendChild(glyphBg);

        const glyph = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        glyph.setAttribute('x', p.x - 82);
        glyph.setAttribute('y', p.y + 4);
        glyph.setAttribute('fill', kind.color);
        glyph.setAttribute('font-size', '11');
        glyph.setAttribute('font-weight', '800');
        glyph.setAttribute('font-family', 'ui-monospace, monospace');
        glyph.setAttribute('text-anchor', 'middle');
        glyph.textContent = kind.glyph;
        g.appendChild(glyph);

        const label = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        label.setAttribute('x', p.x - 58);
        label.setAttribute('y', p.y - 5);
        label.setAttribute('fill', '#edf4fb');
        label.setAttribute('font-size', '12');
        label.setAttribute('font-weight', '700');
        label.setAttribute('font-family', 'ui-monospace, monospace');
        label.textContent = truncate(n.id, 22);
        g.appendChild(label);

        const incoming = inEdges[n.id].length;
        const outgoing = outEdges[n.id].length;
        const meta = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        meta.setAttribute('x', p.x - 58);
        meta.setAttribute('y', p.y + 14);
        meta.setAttribute('fill', '#8293a7');
        meta.setAttribute('font-size', '9.5');
        meta.setAttribute('font-weight', '600');
        meta.setAttribute('font-family', 'ui-monospace, monospace');
        meta.textContent = `${{kind.label}} · line ${{n.line || '—'}} · ${{incoming}}↑ ${{outgoing}}↓`;
        g.appendChild(meta);

        svg.appendChild(g);
      }});
      applyGraphFilters();
    }}

    function highlightDependencies(nodeId) {{
      const upstream = new Set();
      const downstream = new Set();

      const findUp = (id) => {{
        (LOG_DATA.edges || []).forEach(e => {{
          if (e.to === id && !upstream.has(e.from)) {{
            upstream.add(e.from);
            findUp(e.from);
          }}
        }});
      }};
      const findDown = (id) => {{
        (LOG_DATA.edges || []).forEach(e => {{
          if (e.from === id && !downstream.has(e.to)) {{
            downstream.add(e.to);
            findDown(e.to);
          }}
        }});
      }};

      findUp(nodeId);
      findDown(nodeId);
      const related = new Set([nodeId, ...upstream, ...downstream]);

      document.querySelectorAll('.graph-node').forEach(el => {{
        const id = el.getAttribute('data-id');
        if (related.has(id)) {{
          el.style.opacity = '1';
        }} else {{
          el.style.opacity = '0.14';
        }}
      }});

      document.querySelectorAll('.graph-edge').forEach(el => {{
        const f = el.getAttribute('data-from');
        const t = el.getAttribute('data-to');
        if (related.has(f) && related.has(t)) {{
          el.style.opacity = '1';
          el.setAttribute('stroke', '#9bd3ff');
          el.setAttribute('stroke-width', '2.2');
          el.setAttribute('marker-end', 'url(#arrow-hover)');
          el.style.filter = 'none';
        }} else {{
          el.style.opacity = '0';
        }}
      }});
    }}

    function resetHighlight() {{
      applyGraphFilters();
    }}

    function toggleRole(button) {{
      button.setAttribute('aria-pressed', button.getAttribute('aria-pressed') === 'true' ? 'false' : 'true');
      applyGraphFilters();
    }}

    function applyGraphFilters() {{
      const query = (document.getElementById('node-search')?.value || '').trim().toLowerCase();
      const enabledRoles = new Set(
        Array.from(document.querySelectorAll('.filter-btn[aria-pressed="true"]')).map(button => button.dataset.role)
      );
      const visibleNodes = new Set();
      document.querySelectorAll('.graph-node').forEach(element => {{
        const id = element.getAttribute('data-id') || '';
        const role = element.getAttribute('data-role');
        const visible = enabledRoles.has(role) && (!query || id.toLowerCase().includes(query));
        element.style.opacity = visible ? '1' : '0.1';
        element.style.pointerEvents = visible ? 'auto' : 'none';
        if (visible) visibleNodes.add(id);
      }});
      document.querySelectorAll('.graph-edge').forEach(element => {{
        const visible = visibleNodes.has(element.getAttribute('data-from')) && visibleNodes.has(element.getAttribute('data-to'));
        const active = element.getAttribute('data-active') === 'true';
        const contextual = element.getAttribute('data-context') === 'true';
        const warning = element.getAttribute('data-tone') === 'warning';
        element.style.opacity = visible && (active || contextual) ? (active ? '1' : '0.62') : '0';
        element.style.filter = active ? 'url(#edge-glow)' : 'none';
        element.setAttribute('stroke', warning ? '#fb923c' : (active ? '#63b3ff' : '#6685a3'));
        element.setAttribute('stroke-width', active ? '3' : '1.7');
        element.setAttribute('marker-end', warning ? 'url(#arrow-invalidate)' : (active ? 'url(#arrow-active)' : 'url(#arrow)'));
      }});
    }}

    function applyZoom() {{
      const svg = document.getElementById('reactlog-svg');
      const width = graphBounds.width / zoomLevel;
      const height = graphBounds.height / zoomLevel;
      const x = (graphBounds.width - width) / 2;
      const y = (graphBounds.height - height) / 2;
      svg.setAttribute('viewBox', `${{x}} ${{y}} ${{width}} ${{height}}`);
    }}

    function zoomGraph(factor) {{
      zoomLevel = Math.max(0.65, Math.min(2.4, zoomLevel * factor));
      applyZoom();
    }}

    function fitGraph() {{
      zoomLevel = 1;
      applyZoom();
    }}

    function toggleSidebar() {{
      const main = document.getElementById('main-view');
      const hidden = main.classList.toggle('sidebar-hidden');
      const button = document.getElementById('sidebar-toggle');
      button.textContent = hidden ? 'Timeline ‹' : 'Timeline ›';
      button.setAttribute('aria-label', hidden ? 'Show timeline' : 'Hide timeline');
    }}

    function setStep(idx) {{
      selectedNodeId = null;
      currentStep = totalSteps ? Math.max(0, Math.min(idx, totalSteps - 1)) : 0;
      document.getElementById('scrubber-range').value = currentStep;
      document.getElementById('step-counter').textContent = totalSteps ? `${{currentStep + 1}} / ${{totalSteps}}` : '0 / 0';
      renderInspector();
      renderEventsList();
      renderGraph();
      const activeEl = document.querySelectorAll('.event-item')[currentStep];
      if (activeEl) {{
        const eventList = document.getElementById('event-list');
        const itemTop = activeEl.offsetTop - eventList.offsetTop;
        const itemBottom = itemTop + activeEl.offsetHeight;
        if (itemTop < eventList.scrollTop) eventList.scrollTop = itemTop;
        if (itemBottom > eventList.scrollTop + eventList.clientHeight) {{
          eventList.scrollTop = itemBottom - eventList.clientHeight;
        }}
      }}
    }}

    function firstStep() {{ setStep(0); }}
    function prevStep() {{ setStep(currentStep - 1); }}
    function nextStep() {{
      if (currentStep < totalSteps - 1) {{
        setStep(currentStep + 1);
      }} else if (isPlaying) {{
        togglePlay();
      }}
    }}
    function lastStep() {{ setStep(totalSteps - 1); }}

    function togglePlay() {{
      isPlaying = !isPlaying;
      const btn = document.getElementById('play-btn');
      if (isPlaying) {{
        btn.innerHTML = '<span aria-hidden="true">Ⅱ</span> Pause';
        btn.setAttribute('aria-label', 'Pause timeline');
        playTimer = setInterval(nextStep, 700);
      }} else {{
        btn.innerHTML = '<span aria-hidden="true">▶</span> Play';
        btn.setAttribute('aria-label', 'Play timeline');
        clearInterval(playTimer);
      }}
    }}

    document.addEventListener('keydown', event => {{
      if (event.target instanceof HTMLInputElement) return;
      if (event.key === 'ArrowLeft') prevStep();
      if (event.key === 'ArrowRight') nextStep();
      if (event.key === 'Escape') {{ selectedNodeId = null; renderInspector(); renderGraph(); }}
    }});

    setStep(0);
  </script>
</body>
</html>
"""
