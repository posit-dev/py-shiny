import assert from "node:assert/strict";
import { test } from "node:test";

import { replayGraph, traceForReplay } from "./replay";

test("replays a dependency switch and can seek backward without changing the trace", () => {
  const trace = {
    trace_version: 1,
    log: [
      { action: "dependsOn", reactId: "calc", depOnReactId: "a" },
      { action: "dependsOnRemove", reactId: "calc", depOnReactId: "a" },
      { action: "dependsOn", reactId: "calc", depOnReactId: "b" },
    ],
  } as const;
  const edgeA = JSON.stringify(["a", "calc"]);
  const edgeB = JSON.stringify(["b", "calc"]);

  assert.deepEqual(replayGraph(trace, -1).inactiveEdges, new Set([edgeA, edgeB]));
  assert.deepEqual(replayGraph(trace, 0).inactiveEdges, new Set([edgeB]));
  assert.deepEqual(replayGraph(trace, 1).inactiveEdges, new Set([edgeA, edgeB]));
  assert.deepEqual(replayGraph(trace, 2).inactiveEdges, new Set([edgeA]));
  assert.deepEqual(replayGraph(trace, 0).inactiveEdges, new Set([edgeB]));
});

test("adapts legacy event aliases before replay", () => {
  const trace = traceForReplay({
    events: [
      { event: "dependsOn", edge_from: "input", edge_to: "result" },
      { event: "dependsOnRemove", edge_from: "input", edge_to: "result" },
      { event: "freeze", node_id: "input" },
    ],
  });
  const replay = replayGraph(trace, 2);
  assert.deepEqual(replay.inactiveEdges, new Set([JSON.stringify(["input", "result"])]));
  assert.equal(replay.states.get("input"), "frozen");
});

test("rejects unknown versions at the replay boundary", () => {
  assert.throws(
    () => traceForReplay({ trace_version: 2, log: [] }),
    /Unsupported Reactlog trace version/
  );
});
