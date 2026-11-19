import type { ReactlogData } from "./types";

export const TRACE_VERSION = 1;

export interface TraceEvent {
  readonly action: string;
  readonly reactId?: string | null;
  readonly depOnReactId?: string | null;
  readonly error?: string;
  readonly invalidated_node_ids?: readonly string[];
}

export interface ReactlogTrace {
  readonly trace_version: typeof TRACE_VERSION;
  readonly log: readonly TraceEvent[];
}

export function checkTraceVersion(version: unknown) {
  if (version !== undefined && version !== TRACE_VERSION) {
    throw new Error(`Unsupported Reactlog trace version: ${String(version)}`);
  }
}

// Reports may contain an enriched event list for display. Translate legacy
// aliases at this boundary so replay only reads the portable trace fields.
export function traceForReplay(report: ReactlogData): ReactlogTrace {
  checkTraceVersion(report.trace_version);
  const events = report.events ?? report.log ?? report.entries ?? [];
  return {
    trace_version: TRACE_VERSION,
    log: events.map(event => ({
      ...event,
      action: event.action || event.event || "unknown",
      reactId: event.edge_to || event.node_id || event.reactId || event.id,
      depOnReactId: event.edge_from || event.dependsOn || event.depOnReactId,
    })),
  };
}

type NodeState = "calculating" | "invalidating" | "invalidated" | "ready" | "frozen" | "error";

export function reactiveEventState(action?: string, error?: unknown): NodeState | null {
  if (typeof error === "string" || action === "outputError") return "error";
  switch (action) {
    case "enter":
    case "execStart":
    case "wouldEvaluate":
    case "recalculate":
    case "render":
    case "output":
      return "calculating";
    case "invalidateStart":
      return "invalidating";
    case "invalidateEnd":
    case "invalidate":
    case "propagate":
    case "define":
      return "invalidated";
    case "exit":
    case "execEnd":
    case "ordered":
    case "outputUpdated":
    case "valueChange":
    case "inputChange":
    case "assumeValue":
      return "ready";
    default:
      return null;
  }
}

function dependencyKey(event: TraceEvent): string | undefined {
  if (event.depOnReactId && event.reactId) {
    return JSON.stringify([event.depOnReactId, event.reactId]);
  }
}

// Step is the inclusive, zero-based index of the last event to apply.
export function replayGraph(trace: ReactlogTrace, step: number) {
  checkTraceVersion(trace.trace_version);
  const states = new Map<string, NodeState>();
  const frozen = new Set<string>();
  const inactiveEdges = new Set<string>();

  for (const event of trace.log) {
    if (event.action === "dependsOn") {
      const edge = dependencyKey(event);
      if (edge) inactiveEdges.add(edge);
    }
  }

  for (let i = 0; i <= step && i < trace.log.length; i++) {
    const event = trace.log[i]!;
    const { action, reactId } = event;
    const state = reactiveEventState(action, event.error);
    if (state) {
      for (const target of event.invalidated_node_ids ?? [reactId]) {
        if (!target) continue;
        // Output observers can exit normally after handling a renderer error.
        if (action === "exit" && state === "ready" && states.get(target) === "error") continue;
        states.set(target, state);
      }
    }
    if (reactId && action === "freeze") frozen.add(reactId);
    if (reactId && action === "thaw") frozen.delete(reactId);
    if (action === "dependsOnRemove" || action === "dependsOn") {
      const edge = dependencyKey(event);
      if (!edge) continue;
      if (action === "dependsOnRemove") inactiveEdges.add(edge);
      else inactiveEdges.delete(edge);
    }
  }

  for (const id of frozen) states.set(id, "frozen");
  return { states, inactiveEdges };
}
