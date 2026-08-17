from __future__ import annotations

import ast
import json
from typing import Any, Dict, List, Optional, Set


class GraphVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.inputs: Dict[str, int] = {}
        self.calcs: Dict[str, Dict[str, Any]] = {}
        self.outputs: Dict[str, Dict[str, Any]] = {}
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
            elif self.current_calc and self.current_calc in self.calcs:
                self.calcs[self.current_calc]["deps"].add(target_input)

        if isinstance(node.func, ast.Name):
            called_name = node.func.id
            if self.current_output and self.current_output in self.outputs:
                self.outputs[self.current_output]["calc_deps"].add(called_name)
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
            self.outputs[node.name] = {
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
        nodes.append({
            "id": inp,
            "type": "input",
            "role": "source",
            "label": f"input.{inp}",
            "line": line,
        })
    for c, meta in sorted(visitor.calcs.items()):
        nodes.append({
            "id": c,
            "type": "calc",
            "role": "conductor",
            "label": f"calc:{c}",
            "line": meta["line"],
        })
    for out, meta in sorted(visitor.outputs.items()):
        nodes.append({
            "id": out,
            "type": "output",
            "role": "observer",
            "label": f"output:{out}",
            "line": meta["line"],
        })

    edges: List[Dict[str, str]] = []
    for out_name, meta in visitor.outputs.items():
        for dep in sorted(meta["deps"]):
            edges.append({"from": dep, "to": out_name})
        for cdep in sorted(meta["calc_deps"]):
            if cdep in known_calcs:
                edges.append({"from": cdep, "to": out_name})

    for calc_name, meta in visitor.calcs.items():
        for dep in sorted(meta["deps"]):
            edges.append({"from": dep, "to": calc_name})
        for cdep in sorted(meta["calc_deps"]):
            if cdep in known_calcs and cdep != calc_name:
                edges.append({"from": cdep, "to": calc_name})

    return {
        "success": True,
        "nodes": nodes,
        "edges": edges,
        "summary": f"{len(visitor.inputs)} inputs (sources), {len(visitor.calcs)} reactives (conductors), {len(visitor.outputs)} outputs (observers)",
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
    time_offset = 0.0

    events.append({
        "step": step,
        "time_ms": round(time_offset, 1),
        "event": "sessionInit",
        "node_id": None,
        "node_label": "session",
        "node_type": "session",
        "status": "active",
        "details": "Initialized reactive session context",
    })
    step += 1
    time_offset += 1.2

    for node in nodes:
        events.append({
            "step": step,
            "time_ms": round(time_offset, 1),
            "event": "define",
            "node_id": node["id"],
            "node_label": node["label"],
            "node_type": node["role"],
            "status": "ready" if node["role"] == "source" else "idle",
            "details": f"Registered {node['role']} node at line {node.get('line', '?')}",
        })
        step += 1
        time_offset += 0.8

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
    for input_id, val in sim_inputs.items():
        events.append({
            "step": step,
            "time_ms": round(time_offset, 1),
            "event": "valueChange",
            "node_id": input_id,
            "node_label": f"input.{input_id}",
            "node_type": "source",
            "status": "ready",
            "value": str(val),
            "details": f"Input value set to {val!r}",
        })
        step += 1
        time_offset += 1.5

        def cascade_invalidate(nid: str) -> None:
            for down in adj_downstream.get(nid, []):
                if down not in invalidated_nodes:
                    invalidated_nodes.add(down)
                    events.append({
                        "step": step,
                        "time_ms": round(time_offset, 1),
                        "event": "invalidate",
                        "node_id": down,
                        "node_label": next((n["label"] for n in nodes if n["id"] == down), down),
                        "node_type": next((n["role"] for n in nodes if n["id"] == down), "conductor"),
                        "status": "dirty",
                        "details": f"Invalidated by upstream dependency '{nid}'",
                    })
                    cascade_invalidate(down)

        cascade_invalidate(input_id)
        step = len(events)
        time_offset += 2.0

    events.append({
        "step": step,
        "time_ms": round(time_offset, 1),
        "event": "flushStart",
        "node_id": None,
        "node_label": "reactiveEnvironment",
        "node_type": "engine",
        "status": "flushing",
        "details": f"Starting reactive flush ({len(invalidated_nodes)} dirty nodes)",
    })
    step += 1
    time_offset += 1.0

    eval_order: List[Dict[str, Any]] = []
    conductor_nodes = [n for n in nodes if n["role"] == "conductor" and n["id"] in invalidated_nodes]
    observer_nodes = [n for n in nodes if n["role"] == "observer" and n["id"] in invalidated_nodes]
    eval_order.extend(conductor_nodes)
    eval_order.extend(observer_nodes)

    for target in eval_order:
        tid = target["id"]
        tlabel = target["label"]
        trole = target["role"]

        events.append({
            "step": step,
            "time_ms": round(time_offset, 1),
            "event": "calculate",
            "node_id": tid,
            "node_label": tlabel,
            "node_type": trole,
            "status": "calculating",
            "details": f"Executing reactive computation for '{tid}'",
        })
        step += 1
        time_offset += 3.5

        for dep in adj_upstream.get(tid, []):
            events.append({
                "step": step,
                "time_ms": round(time_offset, 1),
                "event": "dependsOn",
                "node_id": tid,
                "node_label": tlabel,
                "node_type": trole,
                "status": "calculating",
                "details": f"Read value from dependency '{dep}'",
            })
            step += 1
            time_offset += 0.5

        events.append({
            "step": step,
            "time_ms": round(time_offset, 1),
            "event": "ready",
            "node_id": tid,
            "node_label": tlabel,
            "node_type": trole,
            "status": "ready",
            "details": "Computation completed; cached updated value",
        })
        step += 1
        time_offset += 2.0

    events.append({
        "step": step,
        "time_ms": round(time_offset, 1),
        "event": "flushComplete",
        "node_id": None,
        "node_label": "reactiveEnvironment",
        "node_type": "engine",
        "status": "idle",
        "details": f"Reactive flush finished in {round(time_offset, 1)}ms",
    })

    return {
        "success": True,
        "nodes": nodes,
        "edges": edges,
        "events": events,
        "steps_total": len(events),
        "total_time_ms": round(time_offset, 1),
        "summary": f"Reactlog recorded {len(events)} steps across {len(nodes)} nodes in {round(time_offset, 1)}ms",
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


def format_reactlog_html(reactlog: Dict[str, Any], title: str = "Shiny Reactlog") -> str:
    data_json = json.dumps(reactlog, indent=2)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css" />
  <style>
    :root {{
      --bg: #0d1117;
      --surface: #161b22;
      --surface-elevated: #21262d;
      --border: #30363d;
      --text: #f0f6fc;
      --text-muted: #8b949e;
      --accent: #58a6ff;
      --success: #3fb950;
      --warning: #d29922;
      --danger: #f85149;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ background: var(--bg); color: var(--text); font-family: 'Plus Jakarta Sans', sans-serif; height: 100vh; display: flex; flex-direction: column; overflow: hidden; }}
    header {{ background: var(--surface); border-bottom: 1px solid var(--border); padding: 0.75rem 1.5rem; display: flex; justify-content: space-between; align-items: center; }}
    .brand {{ display: flex; align-items: center; gap: 0.6rem; font-weight: 800; font-size: 1.1rem; color: #ffffff; }}
    .brand i {{ color: #58a6ff; }}
    .playback-bar {{ background: var(--surface-elevated); border-bottom: 1px solid var(--border); padding: 0.75rem 1.5rem; display: flex; align-items: center; gap: 1rem; flex-wrap: wrap; }}
    .btn {{ background: var(--surface); border: 1px solid var(--border); color: var(--text); font-family: inherit; font-size: 0.85rem; font-weight: 600; padding: 0.4rem 0.85rem; border-radius: 6px; cursor: pointer; display: inline-flex; align-items: center; gap: 0.4rem; transition: all 0.15s ease; }}
    .btn:hover {{ background: var(--accent); border-color: var(--accent); color: #ffffff; }}
    .scrubber {{ flex-grow: 1; min-width: 200px; }}
    .scrubber input[type="range"] {{ width: 100%; accent-color: var(--accent); }}
    .step-display {{ font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; font-weight: 700; color: #58a6ff; min-width: 140px; text-align: right; }}
    .main-view {{ display: grid; grid-template-columns: 1fr 380px; flex-grow: 1; overflow: hidden; }}
    .graph-container {{ padding: 1.5rem; display: flex; flex-direction: column; align-items: center; justify-content: center; background: radial-gradient(circle at center, #161b22 0%, #0d1117 100%); overflow: auto; position: relative; }}
    .sidebar {{ background: var(--surface); border-left: 1px solid var(--border); display: flex; flex-direction: column; overflow: hidden; }}
    .sidebar-header {{ padding: 0.75rem 1rem; border-bottom: 1px solid var(--border); font-size: 0.85rem; font-weight: 700; text-transform: uppercase; color: var(--text-muted); }}
    .event-list {{ flex-grow: 1; overflow-y: auto; padding: 0.5rem; list-style: none; }}
    .event-item {{ padding: 0.6rem 0.75rem; border-radius: 6px; font-size: 0.8rem; margin-bottom: 0.35rem; border: 1px solid transparent; cursor: pointer; transition: all 0.15s ease; }}
    .event-item:hover {{ background: var(--surface-elevated); }}
    .event-item.active {{ background: rgba(88, 166, 255, 0.15); border-color: var(--accent); color: #ffffff; }}
    .event-item .badge {{ font-size: 0.7rem; font-weight: 700; padding: 0.15rem 0.4rem; border-radius: 4px; font-family: 'JetBrains Mono', monospace; text-transform: uppercase; }}
    .badge.define {{ background: #21262d; color: var(--text-muted); }}
    .badge.valueChange {{ background: rgba(88, 166, 255, 0.2); color: #58a6ff; }}
    .badge.invalidate {{ background: rgba(210, 153, 34, 0.2); color: #d29922; }}
    .badge.calculate {{ background: rgba(88, 166, 255, 0.25); color: #79c0ff; }}
    .badge.ready {{ background: rgba(63, 185, 80, 0.2); color: #3fb950; }}
    .graph-node {{ transition: all 0.25s ease; }}
  </style>
</head>
<body>
  <header>
    <div class="brand"><i class="fa-solid fa-clock-rotate-left"></i> <span>Shiny Reactlog Visualizer</span></div>
    <div style="font-size: 0.8rem; color: var(--text-muted);" id="summary-text"></div>
  </header>
  <div class="playback-bar">
    <button class="btn" onclick="firstStep()"><i class="fa-solid fa-backward-step"></i> First</button>
    <button class="btn" onclick="prevStep()"><i class="fa-solid fa-backward"></i> Prev</button>
    <button class="btn" id="play-btn" onclick="togglePlay()"><i class="fa-solid fa-play"></i> Play</button>
    <button class="btn" onclick="nextStep()">Next <i class="fa-solid fa-forward"></i></button>
    <button class="btn" onclick="lastStep()">Last <i class="fa-solid fa-forward-step"></i></button>
    <div class="scrubber">
      <input type="range" id="scrubber-range" min="0" value="0" oninput="setStep(parseInt(this.value))" />
    </div>
    <div class="step-display" id="step-counter">Step 0 / 0</div>
  </div>
  <div class="main-view">
    <div class="graph-container" id="graph-viewport">
      <svg id="reactlog-svg" width="600" height="380" viewBox="0 0 600 380"></svg>
    </div>
    <div class="sidebar">
      <div class="sidebar-header"><i class="fa-solid fa-list-timeline"></i> Event Stream</div>
      <ul class="event-list" id="event-list"></ul>
    </div>
  </div>
  <script>
    const LOG_DATA = {data_json};
    let currentStep = 0;
    let isPlaying = false;
    let playTimer = null;

    const totalSteps = (LOG_DATA.events || []).length;
    document.getElementById('scrubber-range').max = Math.max(0, totalSteps - 1);
    document.getElementById('summary-text').textContent = LOG_DATA.summary || '';

    function renderEventsList() {{
      const list = document.getElementById('event-list');
      list.innerHTML = '';
      (LOG_DATA.events || []).forEach((ev, idx) => {{
        const li = document.createElement('li');
        li.className = 'event-item' + (idx === currentStep ? ' active' : '');
        li.onclick = () => setStep(idx);
        li.innerHTML = `
          <div style="display: flex; justify-content: space-between; margin-bottom: 0.2rem;">
            <span class="badge ${{ev.event}}">${{ev.event}}</span>
            <span style="color: var(--text-muted); font-family: 'JetBrains Mono', monospace; font-size: 0.75rem;">+${{ev.time_ms}}ms</span>
          </div>
          <div style="font-weight: 600; color: #ffffff;">${{ev.node_label}}</div>
          <div style="font-size: 0.75rem; color: var(--text-muted);">${{ev.details}}</div>
        `;
        list.appendChild(li);
      }});
    }}

    function renderGraph() {{
      const svg = document.getElementById('reactlog-svg');
      svg.innerHTML = '<defs><marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#30363d"/></marker></defs>';

      const nodes = LOG_DATA.nodes || [];
      const edges = LOG_DATA.edges || [];
      const activeEvent = LOG_DATA.events[currentStep] || {{}};

      const sources = nodes.filter(n => n.role === 'source');
      const conductors = nodes.filter(n => n.role === 'conductor');
      const observers = nodes.filter(n => n.role === 'observer');

      const pos = {{}};
      sources.forEach((n, i) => {{ pos[n.id] = {{ x: 80, y: 70 + (i * 70) }}; }});
      conductors.forEach((n, i) => {{ pos[n.id] = {{ x: 280, y: 90 + (i * 80) }}; }});
      observers.forEach((n, i) => {{ pos[n.id] = {{ x: 480, y: 70 + (i * 70) }}; }});

      edges.forEach(e => {{
        const p1 = pos[e.from];
        const p2 = pos[e.to];
        if (p1 && p2) {{
          const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
          path.setAttribute('d', `M ${{p1.x + 50}} ${{p1.y + 15}} L ${{p2.x - 50}} ${{p2.y + 15}}`);
          path.setAttribute('stroke', '#30363d');
          path.setAttribute('stroke-width', '2');
          path.setAttribute('marker-end', 'url(#arrow)');
          svg.appendChild(path);
        }}
      }});

      nodes.forEach(n => {{
        const p = pos[n.id] || {{ x: 200, y: 200 }};
        const isActive = activeEvent.node_id === n.id;
        let strokeColor = '#30363d';
        let fillColor = '#161b22';
        let textColor = '#8b949e';

        if (n.role === 'source') strokeColor = '#1f6feb';
        else if (n.role === 'conductor') strokeColor = '#d29922';
        else strokeColor = '#238636';

        if (isActive) {{
          fillColor = '#21262d';
          textColor = '#ffffff';
          if (activeEvent.status === 'dirty') strokeColor = '#d29922';
          else if (activeEvent.status === 'calculating') strokeColor = '#58a6ff';
          else if (activeEvent.status === 'ready') strokeColor = '#3fb950';
        }}

        const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        g.className = 'graph-node';

        const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        rect.setAttribute('x', p.x - 55);
        rect.setAttribute('y', p.y);
        rect.setAttribute('width', 110);
        rect.setAttribute('height', 32);
        rect.setAttribute('rx', '6');
        rect.setAttribute('fill', fillColor);
        rect.setAttribute('stroke', strokeColor);
        rect.setAttribute('stroke-width', isActive ? '3' : '1.5');
        g.appendChild(rect);

        const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        text.setAttribute('x', p.x);
        text.setAttribute('y', p.y + 20);
        text.setAttribute('fill', textColor);
        text.setAttribute('font-size', '11');
        text.setAttribute('font-family', 'JetBrains Mono, monospace');
        text.setAttribute('text-anchor', 'middle');
        text.textContent = n.label;
        g.appendChild(text);

        svg.appendChild(g);
      }});
    }}

    function setStep(idx) {{
      currentStep = Math.max(0, Math.min(idx, totalSteps - 1));
      document.getElementById('scrubber-range').value = currentStep;
      document.getElementById('step-counter').textContent = `Step ${{currentStep + 1}} / ${{totalSteps}}`;
      renderEventsList();
      renderGraph();
      const activeEl = document.querySelectorAll('.event-item')[currentStep];
      if (activeEl) activeEl.scrollIntoView({{ block: 'nearest', behavior: 'smooth' }});
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
        btn.innerHTML = '<i class="fa-solid fa-pause"></i> Pause';
        playTimer = setInterval(nextStep, 700);
      }} else {{
        btn.innerHTML = '<i class="fa-solid fa-play"></i> Play';
        clearInterval(playTimer);
      }}
    }}

    setStep(0);
  </script>
</body>
</html>
"""
