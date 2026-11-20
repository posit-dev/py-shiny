---
title: "Reactlog trace format and replay"
description: "The versioned JSON trace contract and the shared Reactlog report dependency."
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

## Report rendering

The [Reactlog repository](https://github.com/rstudio/reactlog) owns the report
template, stylesheet, browser code, JSON normalization, and replay tests.
Shiny generates traces and delegates HTML and Mermaid reports to the optional
`reactlog` package. CLI, recording, and application integration tests remain
here.

For development, run `uv sync --extra dev --extra test --group reactlog-dev`.
The development group pins the shared viewer while the package is prepared
for release. Run Reactlog tests with `uv run --extra dev --extra test
--group reactlog-dev python -m pytest tests/pytest/test_reactlog.py`.
