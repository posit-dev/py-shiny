from __future__ import annotations

import functools
import html as html_lib
import io
import json
import keyword
import os
import tokenize
from pathlib import Path
from typing import Any, Dict, List, Optional, cast

_R_SENTINEL_REACT_IDS = frozenset({"rNoCtxReactId", "rNoCtx", "rDummyReactId"})


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


def load_reactlog_json(
    json_data: str | Dict[str, Any] | List[Any] | Any,
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
    # An edge is isolated only if every recorded read along it was isolated.
    edges_isolated: Dict[tuple[str, str], bool] = {}

    if existing_nodes:
        for n in existing_nodes:
            nid = str(n.get("reactId") or n.get("id") or n.get("node_id") or "")
            if nid and nid not in _R_SENTINEL_REACT_IDS:
                nodes_map[nid] = dict(n)

    if existing_edges:
        for e in existing_edges:
            f = str(e.get("depOnReactId") or e.get("from") or e.get("dependsOn") or "")
            t = str(e.get("reactId") or e.get("to") or "")
            if (
                f
                and t
                and f not in _R_SENTINEL_REACT_IDS
                and t not in _R_SENTINEL_REACT_IDS
            ):
                edges_isolated[(f, t)] = bool(e.get("isolated"))

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
        if not nid or str(nid) in _R_SENTINEL_REACT_IDS:
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
                "reactivevaluesaslistall",
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
    init_end = -1
    for i, item in enumerate(raw_events):
        act = item.get("action") or item.get("event")
        if act in ("userClick", "userAction", "userMark"):
            break
        if init_end != -1 and act == "valueChange":
            ntype = item.get("type") or item.get("node_type")
            nid = str(
                item.get("reactId") or item.get("node_id") or item.get("id") or ""
            )
            lbl = str(item.get("label") or item.get("node_label") or "")
            if ntype == "input" or lbl.startswith("input.") or nid.startswith("input:"):
                break
        if act == "queueEmpty":
            init_end = i

    for item_idx, item in enumerate(raw_events):
        action = str(item.get("action") or item.get("event") or "")
        nid = item.get("reactId") or item.get("node_id") or item.get("id")
        lbl = _resolve_node_label(nid, item.get("label") or item.get("node_label"))
        ntype = item.get("type") or item.get("node_type")
        if not ntype and nid and str(nid) in nodes_map:
            ntype = nodes_map[str(nid)].get("type") or nodes_map[str(nid)].get(
                "node_type"
            )
        if not ntype:
            ntype = "calc"
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

        prov = item.get("provenance") or "observed"
        phase = item.get("phase") or (
            "init"
            if item_idx <= init_end
            or action in ("define", "analysisInit", "createContext", "sessionInit")
            else "interaction"
        )
        status = item.get("status")
        if not status:
            if action in ("define",):
                status = "discovered"
            elif action in ("invalidate", "invalidateStart", "propagate"):
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

        if (
            action == "dependsOn"
            and dep_from
            and dep_to
            and str(dep_from) not in _R_SENTINEL_REACT_IDS
            and str(dep_to) not in _R_SENTINEL_REACT_IDS
        ):
            key = (str(dep_from), str(dep_to))
            edges_isolated[key] = edges_isolated.get(key, True) and bool(
                item.get("isolate")
            )

        if (
            nid
            and str(nid) not in _R_SENTINEL_REACT_IDS
            and (str(nid) not in nodes_map or action == "define")
        ):
            role = "conductor"
            clean_type = str(ntype).lower()
            if clean_type in (
                "input",
                "reactiveval",
                "reactivevalueskey",
                "reactivevaluesnames",
                "reactivevaluesaslist",
                "reactivevaluesaslistall",
            ) or str(nid).startswith("input:"):
                role = "source"
                clean_type = "input"
            elif (
                clean_type in ("observer", "output", "effect")
                or str(nid).startswith("output:")
                or str(nid).startswith("effect:")
            ):
                role = "observer"
                clean_type = "output"
            elif clean_type in ("calc", "reactive", "observable"):
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
                **{
                    key: value
                    for key in ("module", "render_type", "line", "source_file")
                    if (value := item.get(key, nodes_map.get(str(nid), {}).get(key)))
                    is not None
                },
            }

        event_session = str(item.get("session") or session_name)
        if action == "userMark":
            mark_label = str(item.get("label") or "Bookmark")
            ev_dict = _mark_event(
                step=step_idx,
                label=mark_label,
                timestamp=t_ms,
                time_sec=round(t_sec, 3),
                session=event_session,
            )
            # Loaded logs have no `action_waves`; the viewer builds waves itself
            # and turns this into the same bookmark wave generated logs get.
            ev_dict["mark_wave"] = _mark_wave(
                label=mark_label, time_sec=round(t_sec, 3), step=step_idx, index=0
            )
        else:
            is_inval = action in ("invalidate", "invalidateStart", "propagate")
            if (
                is_inval
                and normalized_events
                and normalized_events[-1].get("action")
                in ("invalidate", "invalidateStart", "propagate")
                and normalized_events[-1].get("phase") == phase
            ):
                prev = normalized_events[-1]
                if nid:
                    nid_str = str(nid)
                    if nid_str not in prev.setdefault("invalidated_node_ids", []):
                        prev["invalidated_node_ids"].append(nid_str)
                if lbl:
                    lbl_str = str(lbl)
                    if lbl_str not in prev.setdefault("invalidated_node_labels", []):
                        prev["invalidated_node_labels"].append(lbl_str)
                count = len(prev.get("invalidated_node_ids", []))
                prev["details"] = (
                    f"Invalidated {count} reactive node{'s' if count != 1 else ''}"
                )
                continue

            # A removed dependency is not an active edge; only `details` names it.
            is_removal = action == "dependsOnRemove"
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
                edge_from=(
                    str(dep_from)
                    if not is_removal and (action == "dependsOn" or dep_from)
                    else None
                ),
                edge_to=(
                    str(dep_to)
                    if not is_removal and (action == "dependsOn" or dep_to)
                    else None
                ),
                details=details,
                session=event_session,
                action=action,
            )
            if is_inval:
                raw_inv_ids = item.get("invalidated_node_ids")
                if isinstance(raw_inv_ids, list):
                    ev_dict["invalidated_node_ids"] = [
                        str(x) for x in cast(list[Any], raw_inv_ids) if x
                    ]
                else:
                    ev_dict["invalidated_node_ids"] = [str(nid)] if nid else list[str]()
                raw_inv_lbls = item.get("invalidated_node_labels")
                if isinstance(raw_inv_lbls, list):
                    ev_dict["invalidated_node_labels"] = [
                        str(x) for x in cast(list[Any], raw_inv_lbls) if x
                    ]
                else:
                    ev_dict["invalidated_node_labels"] = (
                        [str(lbl)] if lbl else list[str]()
                    )
                if not item.get("details"):
                    ev_dict["details"] = (
                        f"Invalidated '{lbl}'" if lbl else "Invalidation phase"
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
    final_edges = [
        {"from": f, "to": t, **({"isolated": True} if isolated else {})}
        for (f, t), isolated in sorted(edges_isolated.items())
    ]

    if not normalized_events and final_nodes:
        for i, n in enumerate(final_nodes):
            normalized_events.append(
                _make_event(
                    step=i,
                    event="define",
                    phase="init",
                    provenance="observed",
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
        "unmatched_inputs": [],
        "unmatched_inputs_count": 0,
        "disclaimer": "Imported reactive log data from JSON format.",
        "summary": f"Imported Reactlog graph: {len(final_nodes)} nodes, {len(final_edges)} edges, {len(normalized_events)} log events",
    }


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
        elif ntype in ("effect", "observer"):
            lines.append(f'    {syn_id}["{label}"]:::effectClass')
        else:
            lines.append(f'    {syn_id}["{label}"]:::outputClass')

    for edge in graph.get("edges", []):
        f = node_id_map.get(str(edge["from"]))
        t = node_id_map.get(str(edge["to"]))
        if f and t:
            arrow = "-.->" if edge.get("isolated") else "-->"
            lines.append(f"    {f} {arrow} {t}")

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


@functools.lru_cache(maxsize=1)
def _load_reactlog_viewer_assets() -> tuple[str, str, str]:
    asset_dir = Path(__file__).resolve().parents[2] / "www" / "py-shiny" / "reactlog"
    css = (asset_dir / "reactlog.css").read_text(encoding="utf-8")
    html = (asset_dir / "reactlog.html").read_text(encoding="utf-8")
    js = (asset_dir / "reactlog.js").read_text(encoding="utf-8")
    return css, html, js


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
    if actual_video and "video_path" not in reactlog:
        reactlog["video_path"] = actual_video

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

    css, html_template, js = _load_reactlog_viewer_assets()
    indented_js = "\n".join(("  " + line if line else "") for line in js.splitlines())

    return (
        html_template.replace("__REACTLOG_THEME__", safe_theme)
        .replace("__REACTLOG_TITLE__", escaped_title)
        .replace("__REACTLOG_CSS__", css)
        .replace("__REACTLOG_SOURCE_PANEL__", source_panel)
        .replace("__REACTLOG_SOURCE_TAB__", source_tab)
        .replace("__REACTLOG_VIDEO_TAB_BTN__", video_tab_btn)
        .replace("__REACTLOG_VIDEO_PANEL__", video_panel)
        .replace("__REACTLOG_DATA__", escaped_json)
        .replace("__REACTLOG_RAW_SOURCE__", escaped_source_raw)
        .replace("__REACTLOG_SCRIPT__", indented_js)
    )
