---
title: "Reactlog trace format and replay"
description: "The versioned JSON trace contract and standalone TypeScript graph replay used by the Reactlog viewer."
---

# Reactlog trace format

A portable trace is a JSON object with `trace_version: 1` and an ordered
`log` array. Each element has a string `action`. A node event uses `reactId`
for its node ID. Dependency events use `reactId` for the dependent and
`depOnReactId` for the dependency. Both `dependsOn` and `dependsOnRemove`
carry these IDs.

```json
{
  "trace_version": 1,
  "log": [
    {"action": "dependsOn", "reactId": "result", "depOnReactId": "a"},
    {"action": "dependsOnRemove", "reactId": "result", "depOnReactId": "a"},
    {"action": "dependsOn", "reactId": "result", "depOnReactId": "b"}
  ]
}
```

The order in `log` determines replay. Optional `time` values are timestamps
in seconds on a common clock. They help the viewer position events on the
timeline. Node IDs must be stable and unique within the trace. Optional
`provenance` values are `observed` for recorded events and `inferred` for
predicted events. An event can carry an error message in `error`, or list
multiple nodes affected by an invalidation in `invalidated_node_ids`.

Producers can include extra metadata such as source files, or enrich the
report with a display event list and precomputed node and edge lists. The
`log` is sufficient to replay event-driven graph changes. The existing
`version` field belongs to the producer. `trace_version` identifies this format.
Readers accept older unversioned R and Python exports and reject unknown
explicit trace versions.

## Replay

`js/reactlog/replay.ts` exports `replayGraph(trace, step)`. It returns
a node-state map and the dependency pairs that are inactive at that step.
A step is the zero-based index of the last event applied. Step `-1` applies
no events. A dependency with an add event begins inactive, becomes active at
its add event, and goes inactive at its removal. Static edges with no add
event are available from the start. The viewer can show inactive edges for
context.

Use `traceForReplay()` at the viewer boundary to translate legacy field
aliases into the portable format. Keep rendering, timeline layout, and
capture in their respective callers. Test the replay module independently
with `npm test` in `js/` and use report tests to check the same semantics
through the browser.
