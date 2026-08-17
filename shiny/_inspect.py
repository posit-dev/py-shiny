from __future__ import annotations

import ast
from typing import Any, Dict, List, Optional, Set


class GraphVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.inputs: Set[str] = set()
        self.calcs: Dict[str, Set[str]] = {}
        self.outputs: Dict[str, Set[str]] = {}
        self.current_calc: Optional[str] = None
        self.current_output: Optional[str] = None

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
        ):
            self.inputs.add(str(node.args[0].value))

        if (
            isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "input"
        ):
            target_input = node.func.attr
            if self.current_output:
                self.outputs.setdefault(self.current_output, set()).add(target_input)
            elif self.current_calc:
                self.calcs.setdefault(self.current_calc, set()).add(target_input)

        self.generic_visit(node)

    def _get_decorator_name(self, d: ast.AST) -> str:
        if isinstance(d, ast.Call):
            d = d.func
        if isinstance(d, ast.Name):
            return d.id
        elif isinstance(d, ast.Attribute) and isinstance(d.value, ast.Name):
            return f"{d.value.id}.{d.attr}"
        return ""

    def _handle_func_def(
        self, node: ast.FunctionDef | ast.AsyncFunctionDef
    ) -> None:
        decorators: List[str] = [
            name
            for d in node.decorator_list
            if (name := self._get_decorator_name(d))
        ]

        is_render = any(
            d.startswith("render.") or d.startswith("render_") for d in decorators
        )
        is_calc = any(
            "calc" in d or "event" in d or "effect" in d for d in decorators
        )

        prev_out = self.current_output
        prev_calc = self.current_calc

        if is_render:
            self.current_output = node.name
            self.outputs.setdefault(node.name, set())
        elif is_calc:
            self.current_calc = node.name
            self.calcs.setdefault(node.name, set())

        self.generic_visit(node)

        self.current_output = prev_out
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

    nodes: List[Dict[str, Any]] = []
    for inp in sorted(visitor.inputs):
        nodes.append({"id": inp, "type": "input", "label": f"input.{inp}"})
    for c in sorted(visitor.calcs.keys()):
        nodes.append({"id": c, "type": "calc", "label": f"calc:{c}"})
    for out in sorted(visitor.outputs.keys()):
        nodes.append({"id": out, "type": "output", "label": f"output:{out}"})

    edges: List[Dict[str, str]] = []
    for out_name, deps in visitor.outputs.items():
        for dep in sorted(deps):
            edges.append({"from": dep, "to": out_name})
    for calc_name, deps in visitor.calcs.items():
        for dep in sorted(deps):
            edges.append({"from": dep, "to": calc_name})

    return {
        "success": True,
        "nodes": nodes,
        "edges": edges,
        "summary": f"{len(visitor.inputs)} inputs, {len(visitor.calcs)} reactives/calcs, {len(visitor.outputs)} outputs",
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
        else:
            lines.append(f'    {nid}["📊 {label}"]:::outputClass')

    for edge in graph.get("edges", []):
        f = edge["from"].replace("-", "_").replace(".", "_")
        t = edge["to"].replace("-", "_").replace(".", "_")
        lines.append(f"    {f} --> {t}")

    lines.append("    classDef inputClass fill:#e0f2fe,stroke:#0284c7,stroke-width:2px;")
    lines.append("    classDef calcClass fill:#fef3c7,stroke:#d97706,stroke-width:2px;")
    lines.append("    classDef outputClass fill:#dcfce7,stroke:#16a34a,stroke-width:2px;")
    return "\n".join(lines)


def format_graph_dot(graph: Dict[str, Any]) -> str:
    lines = ["digraph ReactiveGraph {", "    rankdir=LR;", "    node [shape=box, style=rounded];"]
    for node in graph.get("nodes", []):
        nid = node["id"].replace("-", "_").replace(".", "_")
        label = node.get("label", node["id"])
        ntype = node.get("type", "")
        color = "#0284c7" if ntype == "input" else ("#d97706" if ntype == "calc" else "#16a34a")
        lines.append(f'    "{nid}" [label="{label}", color="{color}"];')

    for edge in graph.get("edges", []):
        f = edge["from"].replace("-", "_").replace(".", "_")
        t = edge["to"].replace("-", "_").replace(".", "_")
        lines.append(f'    "{f}" -> "{t}";')

    lines.append("}")
    return "\n".join(lines)
