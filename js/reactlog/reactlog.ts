/* eslint-disable @typescript-eslint/no-explicit-any */
import type { ReactlogData } from "./types";

declare const reactlogData: ReactlogData;
declare const rawAppSource: string | null | undefined;

const ICONS = {
  play: '<svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><polygon points="6 3 20 12 6 21 6 3"/></svg>',
  pause: '<svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg>',
  video: '<svg class="inline-icon" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m16 13 5.223 3.482a.5.5 0 0 0 .777-.416V7.87a.5.5 0 0 0-.752-.432L16 10.5"/><rect x="2" y="6" width="14" height="12" rx="2"/></svg>',
  eye: '<svg class="inline-icon" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/></svg>',
  zap: '<svg class="inline-icon" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>',
  clock: '<svg class="inline-icon" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>',
  arrowRight: '<svg class="inline-icon" width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>',
  flame: '<svg class="inline-icon flame-icon" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="color:var(--danger, #ef4444);vertical-align:-1px;margin-left:4px;"><path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z"/></svg>'
}
const ALL_ROLES = ['source', 'conductor', 'effect', 'output'];
let currentStep = 0;
let isPlaying = false;
let playTimer: any = null;
let selectedNodeId: any = null;
let focusedNodeId: any = null;
let selectedSearchNodeId: any = null;
let searchQuery = "";
let activeRoles = new Set(['source', 'conductor', 'observer', 'effect', 'output']);
let hideClientData = true;
let changedNodesOnly = false;
let changedNodeIds: any = null;
let activeBurstIndex = 0;
let zoomLevel = 1;
let panOffset = { x: 0, y: 0 };
let isPanning = false;
let startPan = { x: 0, y: 0 };
let maxSessionDuration = 1.0;
let timelineStops: any[] = [];
let videoFrameRequest: any = null;
let graphSeekTime: any = null;
let videoFrameRequestKind: any = null;
let isSourceDrawerOpen = false;

let currentViewMode = 'flush';
let eventListScope: any = null;
let selectedStageFilter: any = null;
let playbackSpeed = 'step';
let currentTimelineTime = 0;
let realtimePlayLastTick: any = null;

const nodeIndex: Map<any, any> = new Map();
const adjUpstream: Map<any, any> = new Map();
const adjDownstream: Map<any, any> = new Map();
let actionWaves: any[] = [];
let allBursts: any[] = [];
const executionCounts: Map<any, any> = new Map();

function getActiveTheme() {
  const currentAttr = document.documentElement.getAttribute('data-theme');
  if (currentAttr === 'light' || currentAttr === 'dark') return currentAttr;
  if (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) return 'light';
  return 'dark';
}

function updateThemeButton() {
  const btn = (document.getElementById('btn-theme-toggle') as any);
  if (!btn) return;
  const isLight = getActiveTheme() === 'light';
  btn.innerHTML = isLight
    ? '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/></svg>'
    : '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/></svg>';
  btn.title = isLight ? 'Switch to dark mode' : 'Switch to light mode';
  btn.setAttribute('aria-label', String(btn.title));
}

function toggleTheme() {
  const current = getActiveTheme();
  const next = current === 'light' ? 'dark' : 'light';
  document.documentElement.setAttribute('data-theme', String(next));
  try { localStorage.setItem('shiny_reactlog_theme', next); } catch { /* ignore storage errors */ }
  updateThemeButton();
  renderGraph();
}

function initTheme() {
  let saved: any = null;
  try { saved = localStorage.getItem('shiny_reactlog_theme'); } catch { /* ignore storage errors */ }
  if (saved === 'light' || saved === 'dark') {
    document.documentElement.setAttribute('data-theme', String(saved));
  }
  updateThemeButton();
}

function buildGraphIndices() {
  nodeIndex.clear();
  adjUpstream.clear();
  adjDownstream.clear();
  executionCounts.clear();

  const nodes = reactlogData.nodes || [];
  const edges = reactlogData.edges || [];
  const events = reactlogData.events || reactlogData.log || [];

  nodes.forEach((n: any) => {
    nodeIndex.set(n.id, n);
    adjUpstream.set(n.id, new Set());
    adjDownstream.set(n.id, new Set());
    executionCounts.set(n.id, 0);
  });

  edges.forEach((e: any) => {
    if (e.isolated) return;
    if (adjDownstream.has(e.from)) adjDownstream.get(e.from).add(e.to);
    if (adjUpstream.has(e.to)) adjUpstream.get(e.to).add(e.from);
  });

  events.forEach((ev: any) => {
    const nid = ev.node_id || ev.id;
    const act = ev.action || ev.event;
    if (nid && (act === 'wouldEvaluate' || act === 'outputUpdated' || act === 'valueChange' || act === 'enter' || act === 'exit')) {
      executionCounts.set(nid, (executionCounts.get(nid) || 0) + 1);
    }
  });
}

function getUpstreamNodes(nodeId: any) {
  const ancestors: Set<any> = new Set();
  const queue = [nodeId];
  while (queue.length > 0) {
    const curr = queue.shift();
    const parents = adjUpstream.get(curr) || new Set();
    for (const p of parents) {
      if (!ancestors.has(p)) {
        ancestors.add(p);
        queue.push(p);
      }
    }
  }
  return ancestors;
}

function getDownstreamNodes(nodeId: any) {
  const descendants: Set<any> = new Set();
  const queue = [nodeId];
  while (queue.length > 0) {
    const curr = queue.shift();
    const children = adjDownstream.get(curr) || new Set();
    for (const c of children) {
      if (!descendants.has(c)) {
        descendants.add(c);
        queue.push(c);
      }
    }
  }
  return descendants;
}

function getActiveLineageSet() {
  if (!searchQuery) return null;
  const isIdQuery = searchQuery.startsWith('id:');
  const selectedSearchNode = selectedSearchNodeId ? nodeIndex.get(selectedSearchNodeId) : null;
  const focusedNode = focusedNodeId ? nodeIndex.get(focusedNodeId) : null;
  const matchedNode = (selectedSearchNode && searchQuery === nodeDisplayName(selectedSearchNode).toLowerCase())
    ? selectedSearchNode
    : ((focusedNode && searchQuery === nodeDisplayName(focusedNode).toLowerCase()) ? focusedNode : null);
  if (!isIdQuery && !matchedNode) return null;
  const matchingIds = matchedNode ? [matchedNode.id] : [];
  if (isIdQuery) {
    const needle = searchQuery.slice(3).trim().toLowerCase();
    if (!needle) return null;
    (reactlogData.nodes || []).forEach((n: any) => {
      const nid = String(n.id || '').toLowerCase();
      const nlabel = String(n.label || '').toLowerCase();
      const nname = String(n.name || '').toLowerCase();
      if (
        nid === needle ||
        nid.endsWith(':' + needle) ||
        nid.includes(needle) ||
        nlabel === needle ||
        nname === needle
      ) {
        matchingIds.push(n.id);
      }
    });
  }
  if (matchingIds.length === 0) return null;
  const lineage = new Set(matchingIds);
  matchingIds.forEach((id: any) => {
    getUpstreamNodes(id).forEach((ancestorId: any) => lineage.add(ancestorId));
    getDownstreamNodes(id).forEach((descendantId: any) => lineage.add(descendantId));
  });
  return lineage;
}

function syncSearchClearButton() {
  const input = (document.getElementById('search-input') as any);
  const clearBtn = (document.getElementById('search-clear') as any);
  if (!clearBtn) return;
  const hasValue = Boolean((input && input.value && input.value.trim()) || searchQuery || selectedSearchNodeId);
  clearBtn.hidden = !hasValue;
}

function filterLineageForNode(nodeId: any) {
  if (!nodeId) return;
  const node = nodeIndex.get(nodeId);
  const filterVal = node ? nodeDisplayName(node) : `id:${nodeId}`;
  selectedSearchNodeId = nodeId;
  searchQuery = filterVal.toLowerCase();
  (document.getElementById('search-input') as any).value = filterVal;
  syncSearchClearButton();
  closeSearchChoices();
  if (node && isClientDataNode(node)) setClientDataVisibility('show');
  if (node && changedNodeIds && !changedNodeIds.has(node.id)) changedNodesOnly = false;
  activeRoles = new Set(['source', 'conductor', 'observer', 'effect', 'output']);
  selectNode(nodeId);
  refreshExploration();
  fitGraph();
}

function prepareEventTimings() {
  const events = reactlogData.events || reactlogData.log || [];
  if (!events || events.length === 0) return;

  let i = 0;
  while (i < events.length) {
    const baseTime = Number(events[i]!.time_sec !== undefined ? events[i]!.time_sec : (events[i]!.time !== undefined ? events[i]!.time : 0));
    let j = i;
    while (j < events.length && Math.abs(((events[j]!.time_sec !== undefined ? events[j]!.time_sec : events[j]!.time) || 0) - baseTime) < 0.04) {
      j++;
    }
    const clusterLen = j - i;
    const nextTime = Number((j < events.length && (events[j]!.time_sec !== undefined || events[j]!.time !== undefined)) ? (events[j]!.time_sec ?? events[j]!.time) : (baseTime + 1.2));
    const windowDuration = Math.min(0.75, Math.max(0.25, (nextTime - baseTime) * 0.7));

    for (let k = 0; k < clusterLen; k++) {
      const evIdx = i + k;
      if (events[evIdx]!.time_sec !== undefined || events[evIdx]!.time !== undefined) {
        events[evIdx]!.effective_time = baseTime + (clusterLen > 1 ? (k / (clusterLen - 1)) * windowDuration : 0);
      } else {
        events[evIdx]!.effective_time = baseTime;
      }
    }
    i = j;
  }
}

function filterItems(arr: any, predicate: any) {
  const out: any[] = [];
  for (const item of (arr || [])) {
    if (predicate(item)) out.push(item);
  }
  return out;
}

function cleanName(n: any): string {
  if (!n) return '';
  let s = String(n);
  s = s.replace(/^Observed\s+[^:]*:\s*/i, '');
  s = s.replace(/^click\s+(on\s+)?/i, '');
  s = s.replace(/^(input|output|calc|effect)[:.]/, '');
  s = s.replace(/^(input#|#)/, '');
  s = s.replace(/^(on[,\s]+)/i, '');
  s = s.replace(/^[.#]/, '');
  s = (s.split('=')[0] || '').trim();
  return s;
}

function formatHumanValue(val: any) {
  if (val === null || val === undefined) return '';
  if (typeof val === 'string' && val.length > 20) return val.slice(0, 18) + '…';
  return String(val);
}

function buildActionWaves() {
  if (reactlogData.action_waves && reactlogData.action_waves.length > 0) {
    const rawWaves = reactlogData.action_waves;
    const coalesced: any[] = [];
    for (let i = 0; i < rawWaves.length; i++) {
      const w = rawWaves[i];
      const nextW = rawWaves[i + 1];
      if (nextW && w.trigger && w.trigger.startsWith('Click:') && (w.inferred_executions || []).length === 0 && Math.abs((nextW.start_time || 0) - (w.start_time || 0)) <= 0.05) {
        nextW.human_action = `${w.trigger} → ${nextW.human_action || nextW.trigger}`;
        continue;
      }
      coalesced.push(w);
    }
    const mapped = coalesced.map((w: any, idx: any) => {
      const inputs: any[] = [];
      if (w.trigger_node_id) {
        inputs.push({
          name: nodeDisplayName(w.trigger_node_id),
          nodeId: w.trigger_node_id,
          step: w.start_step,
          isClick: !w.trigger_value,
          details: w.trigger || w.human_action,
          value: w.trigger_value
        });
      }
      const calcs = filterItems(w.inferred_executions || [], (id: any) => id.startsWith('calc:') || nodeIndex.get(id)?.type === 'calc')
        .map((id: any) => ({ name: nodeDisplayName(id), nodeId: id, step: w.start_step }));
      const outputs = filterItems(w.inferred_executions || [], (id: any) => id.startsWith('output:') || nodeIndex.get(id)?.type === 'output')
        .map((id: any) => ({ name: nodeDisplayName(id), nodeId: id, step: w.start_step }));

      let shortLabel = w.is_mark ? (w.short_label || '') : nodeDisplayName(w.short_label || '');
      if (!shortLabel) {
        if (w.is_init) {
          shortLabel = 'Init';
        } else if (w.trigger_node_id) {
          shortLabel = nodeDisplayName(w.trigger_node_id);
        } else if (w.trigger_label) {
          shortLabel = nodeDisplayName(w.trigger_label);
        } else {
          shortLabel = 'Action';
        }
      }

      return {
        id: w.action_id || `burst-${idx}`,
        index: w.index !== undefined ? w.index : idx,
        isInit: Boolean(w.is_init),
        isMark: Boolean(w.is_mark),
        startTime: w.start_time || 0.0,
        endTime: w.end_time || 0.0,
        time: w.start_time || 0.0,
        startStep: w.start_step || 0,
        endStep: w.end_step || 0,
        triggerLabel: w.is_mark ? (w.trigger_label || w.trigger || 'Action') : nodeDisplayName(w.trigger_label || w.trigger || 'Action'),
        shortLabel: shortLabel,
        humanAction: w.is_mark ? (w.human_action || w.trigger || 'Action') : nodeDisplayName(w.human_action || w.trigger || 'Action'),
        triggerNodeId: w.trigger_node_id || '',
        triggerValue: w.trigger_value,
        inputs: inputs,
        calcs: calcs,
        outputs: outputs,
        invalidatedNodes: new Set(w.invalidated_nodes || []),
        inferredExecutions: new Set(w.inferred_executions || []),
        observedExecutions: new Set(w.observed_executions || []),
        observedOutputs: new Set(w.observed_outputs || []),
        totalEvents: (w.end_step - w.start_step + 1),
        userChanges: inputs.length,
        details: w.trigger || 'Action'
      };
    });
    allBursts = mapped;
    actionWaves = filterItems(mapped, (w: any) => !w.isInit);
    return;
  }
  actionWaves = [];
  allBursts = [];
  const events = reactlogData.events || reactlogData.log || [];
  const lastKnownValues: Map<any, any> = new Map();
  (reactlogData.nodes || []).forEach((n: any) => {
    if (n.value !== undefined && n.value !== null) {
      lastKnownValues.set(nodeDisplayName(n), n.value);
    }
  });
  let initWave: any = null;
  let curWave: any = null;

  events.forEach((ev: any, idx: any) => {
    const evAction = ev.action || ev.event || '';
    const isInit = ev.phase === 'init' || ['define', 'analysisInit', 'createContext', 'sessionInit'].includes(evAction);
    const t = ev.time_sec !== undefined ? ev.time_sec : (ev.time !== undefined ? ev.time : 0);

    if (isInit) {
      if (ev.value !== undefined && ev.value !== null) {
        const raw = ev.node_id || ev.id || ev.node_label || ev.label || '';
        const name = nodeDisplayName(raw);
        if (name) lastKnownValues.set(name, ev.value);
      }
      if (!initWave) {
        initWave = {
          id: 'burst-init',
          index: 0,
          isInit: true,
          startTime: t,
          endTime: t,
          time: t,
          startStep: idx,
          endStep: idx,
          triggerLabel: 'Init',
          shortLabel: 'Init',
          humanAction: 'Init',
          inputs: [],
          calcs: [],
          outputs: [],
          totalEvents: 0,
          userChanges: 0,
          details: 'Application Initialization',
        };
      }
      initWave.endStep = idx;
      initWave.endTime = t;
      initWave.totalEvents++;
    } else {
      const isUserAction = evAction === 'inputChange' || evAction === 'userClick' || evAction === 'userAction';
      const isNewTrigger = isUserAction && curWave && curWave.inputs.length > 0;
      if (!curWave || (t - curWave.startTime) > 0.25 || isNewTrigger) {
        curWave = {
          id: `burst-${actionWaves.length + 1}`,
          index: actionWaves.length + 1,
          isInit: false,
          startTime: t,
          endTime: t,
          time: t,
          startStep: idx,
          endStep: idx,
          triggerLabel: '',
          shortLabel: '',
          humanAction: '',
          triggerNodeId: '',
          triggerValue: ev.value,
          inputs: [],
          calcs: [],
          outputs: [],
          totalEvents: 0,
          userChanges: 0,
          details: ev.details || evAction,
        };
        actionWaves.push(curWave);
      }
      curWave.endStep = idx;
      curWave.endTime = t;
      curWave.totalEvents++;

      const nId = ev.node_id || ev.id || '';
      if (evAction === 'inputChange' || evAction === 'userClick' || evAction === 'userAction' || nId.startsWith('input:') || nodeIndex.get(nId)?.type === 'input') {
        const raw = nId || ev.details || '';
        if (!raw.includes('clientdata') && !raw.includes('pixelratio') && !raw.includes('_hidden')) {
          const name = nodeDisplayName(raw) || 'input';
          const prevVal = lastKnownValues.get(name);
          const newVal = ev.value !== undefined ? ev.value : null;
          if (newVal !== null) lastKnownValues.set(name, newVal);

          if (!curWave.triggerLabel) {
            curWave.shortLabel = name;
            if (evAction === 'userClick') {
              curWave.humanAction = `Click: ${name}`;
              curWave.triggerLabel = name;
              curWave.shortLabel = `Click: ${name}`;
            } else if (prevVal !== undefined && newVal !== null && prevVal !== newVal) {
              curWave.humanAction = `${name}: ${formatHumanValue(prevVal)} → ${formatHumanValue(newVal)}`;
              curWave.triggerLabel = name;
            } else if (newVal !== null) {
              curWave.humanAction = `${name}: ${formatHumanValue(newVal)}`;
              curWave.triggerLabel = name;
            } else {
              curWave.humanAction = `${name} changed`;
              curWave.triggerLabel = name;
            }
            curWave.triggerNodeId = nId;
            curWave.triggerValue = ev.value;
          }
          if (!curWave.inputs.some((item: any) => item.name === name)) {
            curWave.inputs.push({ name, nodeId: nId, step: idx, isClick: evAction === 'userClick' || evAction === 'userAction', details: ev.details, value: ev.value });
            curWave.userChanges++;
          }
        }
      } else if (nId && (nId.startsWith('calc:') || nId.startsWith('effect:') || (ev.type === 'calc') || ['calc', 'effect'].includes(nodeIndex.get(nId)?.type) || (ev.node_type === 'conductor'))) {
        const name = nodeDisplayName(nId);
        if (name && !curWave.calcs.some((item: any) => item.name === name)) {
          curWave.calcs.push({ name, nodeId: nId, step: idx, details: ev.details });
        }
      } else if (nId && (nId.startsWith('output:') || (ev.type === 'output') || nodeIndex.get(nId)?.type === 'output' || (ev.node_type === 'observer'))) {
        const name = nodeDisplayName(nId);
        if (name && !curWave.outputs.some((item: any) => item.name === name)) {
          curWave.outputs.push({ name, nodeId: nId, step: idx, details: ev.details });
        }
      }
    }
  });

  actionWaves.forEach((w: any) => {
    if (!w.triggerLabel) {
      if (w.inputs.length > 0) {
        w.humanAction = `${w.inputs[0].name} changed`;
        w.triggerLabel = w.inputs[0].name;
        w.shortLabel = w.inputs[0].name;
      } else if (w.calcs.length > 0) {
        w.humanAction = `Recalc: ${w.calcs[0].name}`;
        w.triggerLabel = w.calcs[0].name;
        w.shortLabel = w.calcs[0].name;
      } else if (w.outputs.length > 0) {
        w.humanAction = `Render: ${w.outputs[0].name}`;
        w.triggerLabel = w.outputs[0].name;
        w.shortLabel = w.outputs[0].name;
      } else {
        w.humanAction = 'Action';
        w.triggerLabel = 'Action';
        w.shortLabel = 'Action';
      }
    }
  });

  allBursts = (initWave && initWave.totalEvents > 0 ? [initWave] : []).concat(actionWaves);
  if (allBursts.length === 0) {
    allBursts = [{
      id: 'burst-init',
      index: 0,
      isInit: true,
      isMark: false,
      startTime: 0,
      endTime: 0,
      time: 0,
      startStep: 0,
      endStep: Math.max(0, (reactlogData.events || []).length - 1),
      triggerLabel: 'Init',
      shortLabel: 'Init',
      humanAction: 'Init',
      triggerNodeId: '',
      triggerValue: null,
      inputs: [],
      calcs: [],
      outputs: [],
      invalidatedNodes: new Set(),
      inferredExecutions: new Set(),
      observedExecutions: new Set(),
      observedOutputs: new Set(),
      totalEvents: Math.max(1, (reactlogData.events || []).length),
      userChanges: 0,
      details: 'Initial State'
    }];
  }
}

function getCurrentStepTime() {
  const events = reactlogData.events || reactlogData.log || [];
  const ev = events[currentStep];
  return ev ? (ev.effective_time !== undefined ? ev.effective_time : ((ev.time_sec !== undefined ? ev.time_sec : ev.time) || 0)) : 0;
}

function initTraceTimeline() {
  const events = reactlogData.events || reactlogData.log || [];
  const video = (document.getElementById('session-video') as any);
  maxSessionDuration = events.reduce((max: any, ev: any) => Math.max(max, ev.effective_time ?? ev.time_sec ?? ev.time ?? 0), Number.isFinite(video?.duration) ? video.duration : 1);
  (document.getElementById('trace-total-time') as any).textContent = formatTime(maxSessionDuration);
  const markers = (document.getElementById('trace-markers') as any);
  markers.replaceChildren();
  timelineStops = [];
  let depth = 0;
  events.forEach((ev: any, step: any) => {
    const action = ev.action || ev.event || '';
    if (['enter', 'execStart'].includes(action)) depth++;
    let outputComplete = action === 'outputUpdated' || ev.event === 'outputUpdated';
    if (['exit', 'execEnd'].includes(action)) {
      depth = Math.max(0, depth - 1);
      outputComplete = depth === 0;
    }
    const kind = isErrorEvent(ev) ? 'error' : ['mark', 'userMark'].includes(action) ? 'mark' : isIdleEvent(ev) ? 'idle' : outputComplete ? 'output' : null;
    if (!kind) return;
    timelineStops.push({ step, kind });
    const label = kind === 'error' ? 'Error' : kind === 'mark' ? 'User mark' : kind === 'idle' ? 'Idle' : 'Output calculation';
    const time = formatTime(ev.time_sec ?? ev.time ?? 0);
    const description = kind === 'error' ? formatEventDetails(ev) : kind === 'mark'
      ? (ev.node_label || ev.label || ev.details || '')
      : nodeDisplayName(ev.node_id || ev.id || ev.node_label || ev.label || '');
    const text = `${label} · Step ${step} · ${time}${description ? ' · ' + description : ''}`;
    const marker = document.createElement('button');
    marker.type = 'button';
    marker.tabIndex = -1;
    marker.className = `timeline-marker is-${kind}`;
    marker.dataset.step = step;
    marker.setAttribute('aria-label', String(text));
    marker.title = text;
    const width = Math.min(100, 75 / Math.max(1, events.length - 1));
    marker.style.width = `${width}%`;
    marker.style.left = `${Math.max(0, 100 * step / Math.max(1, events.length - 1) - width)}%`;
    const tooltip = (document.getElementById('timeline-tooltip') as any);
    marker.onmouseenter = marker.onfocus = () => { tooltip.textContent = text; tooltip.hidden = false; };
    marker.onmouseleave = marker.onblur = () => { tooltip.hidden = true; };
    marker.onclick = () => { seekTo(step); };
    markers.appendChild(marker);
  });
  const track = (document.getElementById('trace-track-wrap') as any);
  const seekPointer = (event: any) => {
    const box = track.getBoundingClientRect();
    const ratio = Math.max(0, Math.min(1, (event.clientX - box.left) / box.width));
    seekTo(Math.round(ratio * Math.max(0, events.length - 1)));
  };
  track.onpointerdown = (event: any) => {
    if (event.button !== 0) return;
    event.preventDefault();
    track._dragging = true;
    try { track.setPointerCapture(event.pointerId); } catch { /* ignore */ }
    (document.getElementById('scrubber-range') as any).focus({ preventScroll: true });
    const marker = event.target.closest('.timeline-marker');
    if (marker) seekTo(Number(marker.dataset.step)); else seekPointer(event);
  };
  track.onpointermove = (event: any) => {
    if ((track._dragging || track.hasPointerCapture(event.pointerId)) && event.buttons === 1) {
      (document.getElementById('timeline-tooltip') as any).hidden = true;
      seekPointer(event);
    }
  };
  track.onpointerup = (event: any) => {
    track._dragging = false;
    if (track.hasPointerCapture(event.pointerId)) track.releasePointerCapture(event.pointerId);
  };
  track.onpointercancel = () => { track._dragging = false; };
  updateTraceTimelineScrubber(getCurrentStepTime());
}

function updateTraceTimelineScrubber(curSec: any) {
  currentTimelineTime = Number(curSec) || 0;
  (document.getElementById('trace-current-time') as any).textContent = formatTime(curSec);
  const events = reactlogData.events || reactlogData.log || [];
  const curWave = allBursts.slice().reverse().find((w: any) => currentStep >= w.startStep) || allBursts[0];
  activeBurstIndex = curWave ? allBursts.indexOf(curWave) : 0;
  const flushText = curWave
    ? (curWave.isInit ? 'Initial render' : (curWave.humanAction || curWave.triggerLabel || 'Initial render'))
    : 'No recorded activity';
  const ev = events[currentStep];
  const statusText = ev ? (isIdleEvent(ev) ? 'Idle' : ['mark', 'userMark'].includes(ev.action || ev.event || '') ? `User mark${ev.details ? ' · ' + nodeDisplayName(String(ev.details)) : ''}` : (formatEventDetails(ev) || ev.action || ev.event || '')) : 'No events';
  const range = (document.getElementById('scrubber-range') as any);
  const percent = 100 * currentStep / Math.max(1, events.length - 1);
  range.style.setProperty('--progress', `${percent}%`);
  (document.getElementById('timeline-playhead') as any).style.left = `calc(${percent}% - ${3 * percent / 100}px)`;
  range.setAttribute('aria-valuetext', `Step ${currentStep} of ${Math.max(0, events.length - 1)}. ${flushText}. ${statusText}`);
}

function nextAction() {
  const events = reactlogData.events || reactlogData.log || [];
  for (let i = currentStep + 1; i < events.length; i++) {
    const ev = events[i]!;
    const act = ev.action || ev.event || '';
    if (ev.phase === 'interaction' && (act === 'inputChange' || act === 'userClick' || act === 'userAction' || act === 'outputUpdated' || act === 'valueChange')) {
      seekTo(i);
      return;
    }
  }
}

function prevAction() {
  const events = reactlogData.events || reactlogData.log || [];
  for (let i = currentStep - 1; i >= 0; i--) {
    const ev = events[i]!;
    const act = ev.action || ev.event || '';
    if (ev.phase === 'interaction' && (act === 'inputChange' || act === 'userClick' || act === 'userAction' || act === 'outputUpdated' || act === 'valueChange')) {
      seekTo(i);
      return;
    }
  }
  seekTo(0);
}

function getCurrentFlushIndex() {
  if (!allBursts || allBursts.length === 0) return 0;
  for (let i = allBursts.length - 1; i >= 0; i--) {
    if (currentStep >= allBursts[i].startStep) return i;
  }
  return 0;
}

function getActiveFlushNodeIds(wave: any) {
  if (!wave) return new Set();
  const set: Set<any> = new Set();
  if (wave.isInit) {
    (reactlogData.nodes || []).forEach((n: any) => {
      set.add(n.id);
      set.add(cleanName(n.id));
    });
    return set;
  }
  if (wave.triggerNodeId) {
    set.add(wave.triggerNodeId);
    set.add(cleanName(wave.triggerNodeId));
    (adjDownstream.get(wave.triggerNodeId) || []).forEach((dn: any) => {
      set.add(dn);
      set.add(cleanName(dn));
    });
  }
  (wave.inputs || []).forEach((i: any) => {
    if (i.nodeId) {
      set.add(i.nodeId);
      set.add(cleanName(i.nodeId));
      (adjDownstream.get(i.nodeId) || []).forEach((dn: any) => {
        set.add(dn);
        set.add(cleanName(dn));
      });
    }
    if (i.name) set.add(i.name);
  });
  (wave.calcs || []).forEach((c: any) => {
    if (c.nodeId) {
      set.add(c.nodeId);
      set.add(cleanName(c.nodeId));
      (adjDownstream.get(c.nodeId) || []).forEach((dn: any) => {
        set.add(dn);
        set.add(cleanName(dn));
      });
    }
    if (c.name) set.add(c.name);
  });
  (wave.outputs || []).forEach((o: any) => {
    if (o.nodeId) { set.add(o.nodeId); set.add(cleanName(o.nodeId)); }
    if (o.name) set.add(o.name);
  });
  if (wave.invalidatedNodes) {
    wave.invalidatedNodes.forEach((id: any) => {
      set.add(id);
      set.add(cleanName(id));
    });
  }
  if (wave.inferredExecutions) {
    wave.inferredExecutions.forEach((id: any) => {
      set.add(id);
      set.add(cleanName(id));
    });
  }
  if (wave.observedExecutions) {
    wave.observedExecutions.forEach((id: any) => {
      set.add(id);
      set.add(cleanName(id));
    });
  }
  const directIds = new Set(set);
  (reactlogData.edges || []).forEach((e: any) => {
    if (directIds.has(e.from) || (e.from && directIds.has(cleanName(e.from)))) {
      set.add(e.to);
      set.add(cleanName(e.to));
    }
    if (directIds.has(e.to) || (e.to && directIds.has(cleanName(e.to)))) {
      set.add(e.from);
      set.add(cleanName(e.from));
    }
  });
  return set;
}

function selectFlush(flushIndex: any) {
  if (!allBursts || allBursts.length === 0) return;
  const idx = Math.max(0, Math.min(flushIndex, allBursts.length - 1));
  activeBurstIndex = idx;
  const targetBurst = allBursts[idx];
  if (!targetBurst) return;
  const targetStep = targetBurst.inputs && targetBurst.inputs[0] ? targetBurst.inputs[0].step : targetBurst.startStep;
  seekTo(targetStep);
  if (currentViewMode === 'flush') {
    renderGraph();
    fitGraph();
  }
}

function isIdleEvent(ev: any) {
  return ev.event !== 'orderingStart' && ['idle', 'queueEmpty'].includes(ev.action || ev.event);
}

function seekTimelineStop(kind: any, direction: any) {
  const stops = direction < 0 ? timelineStops.slice().reverse() : timelineStops;
  const target = stops.find((stop: any) => stop.kind === kind && (direction < 0 ? stop.step < currentStep : stop.step > currentStep));
  if (target) seekTo(target.step);
}

function prevFlush() { seekTimelineStop('idle', -1); }
function nextFlush() { seekTimelineStop('idle', 1); }

function setViewMode(mode: any) {
  currentViewMode = mode;
  const activitySelect = (document.getElementById('activity-select') as any);
  if (activitySelect) activitySelect.value = mode;
  refreshExploration();
  fitGraph();
}

function setPlaybackSpeed(mode: any) {
  const nextMode = mode === 'realtime' ? 'realtime' : 'step';
  const wasPlaying = isPlaying;
  if (wasPlaying) {
    togglePlay();
  }
  playbackSpeed = nextMode;
  const speedSelect = (document.getElementById('playback-speed-select') as any);
  if (speedSelect) speedSelect.value = playbackSpeed;
  if (wasPlaying) {
    togglePlay();
  }
}

function filterFlushStage(stage: any) {
  if (selectedStageFilter === stage) {
    selectedStageFilter = null;
  } else {
    selectedStageFilter = stage;
  }
  document.querySelectorAll('.pipeline-step-item').forEach((el: any) => {
    el.classList.toggle('is-selected-stage', el.id === `pipe-${selectedStageFilter}`);
  });
  renderGraph();
  fitGraph();
}

function toggleCollapseAllModules() {
  toggleSettingsMenu(false);
  const allMods = new Set(filterItems((reactlogData.nodes || []).map((n: any) => n.module), Boolean));
  if (collapsedModules.size >= allMods.size) {
    collapsedModules.clear();
  } else {
    allMods.forEach((m: any) => collapsedModules.add(m));
  }
  renderGraph();
  fitGraph();
}

function nodeRoleKey(n: any) {
  if (n.role === 'source' || n.type === 'input') return 'source';
  if (n.role === 'conductor' || n.type === 'calc') return 'conductor';
  const raw = `${n.type || ''} ${n.label || ''} ${n.id || ''}`.toLowerCase();
  if (n.type === 'effect' || raw.includes('reactive.effect') || String(n.id || '').startsWith('effect:')) return 'effect';
  return 'output';
}

function isClientDataNode(n: any) {
  const raw = `${n.id || ''} ${n.label || ''} ${n.name || ''}`.toLowerCase();
  return raw.includes('.clientdata_') || raw.includes('clientdata') || raw.includes('pixelratio');
}

function syncRoleFilterButtons() {
  document.querySelectorAll('.legend-role-btn').forEach((btn: any) => {
    const role = btn.getAttribute('data-role');
    const active = activeRoles.has(role);
    btn.classList.toggle('is-active', active);
    btn.setAttribute('aria-pressed', String(active));
  });
}

function toggleRoleFilter(role: any) {
  if (activeRoles.has(role)) {
    activeRoles.delete(role);
  } else {
    activeRoles.add(role);
  }
  if (activeRoles.has('effect') || activeRoles.has('output')) activeRoles.add('observer');
  else activeRoles.delete('observer');
  syncRoleFilterButtons();
  refreshExploration();
  fitGraph();
}

function findChangedNodes() {
  const events = reactlogData.events || reactlogData.log || [];
  const boundary = events.findIndex((ev: any) => (ev.action || ev.event) === 'queueEmpty');
  if (boundary < 0) return null;
  const values: Map<any, any> = new Map(), changed: Set<any> = new Set();
  events.forEach((ev: any, index: any) => {
    const action = ev!.action || ev!.event;
    const id = ev.node_id || ev.reactId || ev.id;
    if (!id || ev.provenance === 'inferred') return;
    if (ev.provenance === 'observed' && (action === 'enter' || ev.event === 'outputUpdated')) {
      changed.add(id);
      return;
    }
    if (!['valueChange', 'inputChange'].includes(action)) return;
    const value = JSON.stringify(ev.value);
    if (values.has(id) ? values.get(id) !== value : index > boundary) changed.add(id);
    values.set(id, value);
  });
  return changed;
}

function toggleChangedNodes() {
  changedNodesOnly = !changedNodesOnly;
  refreshExploration();
  fitGraph();
}

function setClientDataVisibility(mode: any) {
  hideClientData = mode === 'hide';
  const clientSelect = (document.getElementById('clientdata-select') as any);
  if (clientSelect) clientSelect.value = hideClientData ? 'hide' : 'show';
  refreshExploration();
  fitGraph();
}

function toggleClientData() {
  setClientDataVisibility(hideClientData ? 'show' : 'hide');
}

function updateFlushUI() {
  if (!allBursts || allBursts.length === 0) return;
  const curIdx = getCurrentFlushIndex();
  const curWave = allBursts[curIdx] || allBursts[0];
  if (!curWave) return;

  const invCount = curWave.invalidatedNodes ? curWave.invalidatedNodes.size : 0;
  const calcCount = curWave.calcs ? curWave.calcs.length : 0;
  const outCount = curWave.outputs ? curWave.outputs.length : 0;

  const cardTitle = (document.getElementById('flush-card-title') as any);
  if (cardTitle) {
    cardTitle.textContent = curWave.isInit ? 'Activity 1: Initial render' : `Activity ${curIdx + 1}: ${curWave.shortLabel || 'Action'}`;
  }
  const cardTime = (document.getElementById('flush-card-time') as any);
  if (cardTime) {
    const dur = Math.max(0, (curWave.endTime - curWave.startTime) * 1000);
    cardTime.textContent = `${formatTime(curWave.startTime)} (${Math.round(dur)}ms)`;
  }
  const cardTrigger = (document.getElementById('flush-card-trigger') as any);
  if (cardTrigger) {
    cardTrigger.textContent = curWave.humanAction || curWave.triggerLabel || (curWave.isInit ? 'Application Initialization' : 'Action');
  }
  const cardInv = (document.getElementById('flush-card-invalidated') as any);
  if (cardInv) cardInv.textContent = `${invCount} nodes marked dirty`;
  const cardCalcs = (document.getElementById('flush-card-calcs') as any);
  if (cardCalcs) cardCalcs.textContent = `${calcCount} calcs re-evaluated`;
  const cardOuts = (document.getElementById('flush-card-outputs') as any);
  if (cardOuts) cardOuts.textContent = `Outputs that ran: ${outCount}`;

  const execOrder = (document.getElementById('flush-execution-order') as any);
  if (execOrder) {
    execOrder.innerHTML = '';
    const sequence: any[] = [];
    if (curWave.inputs) curWave.inputs.forEach((i: any) => sequence.push({ role: 'source', nodeId: i.nodeId, name: i.name || i.nodeId, label: 'Trigger Input' }));
    if (curWave.calcs) curWave.calcs.forEach((c: any) => sequence.push({ role: 'conductor', nodeId: c.nodeId, name: c.name || c.nodeId, label: 'Calc' }));
    if (curWave.outputs) curWave.outputs.forEach((o: any) => sequence.push({ role: 'observer', nodeId: o.nodeId, name: o.name || o.nodeId, label: 'Output' }));
    sequence.slice(0, 12).forEach((item: any, sIdx: any) => {
      const row = document.createElement('div');
      row.className = 'flush-order-item';
      const roleColor = item.role === 'source' ? 'var(--source)' : (item.role === 'conductor' ? 'var(--calc)' : 'var(--output)');
      row.innerHTML = `<span class="flush-order-idx">${sIdx + 1}.</span><span class="flush-order-role" style="background:${roleColor}"></span><span style="font-weight:700;">${nodeLabelHTML(nodeIndex.get(item.nodeId) || { label: item.name })}</span><span style="color:var(--text-muted);font-size:0.6rem;margin-left:auto;">${item.label}</span>`;
      row.onclick = () => {
        const matching = nodeIndex.get(item.nodeId) || (reactlogData.nodes || []).find((n: any) => nodeDisplayName(n) === item.name);
        if (matching) selectNode(matching.id);
      };
      execOrder.appendChild(row);
    });
    if (sequence.length > 12) {
      const more = document.createElement('div');
      more.style.cssText = 'color:var(--text-muted);font-size:0.62rem;font-style:italic;padding-left:18px;';
      more.textContent = `+ ${sequence.length - 12} more steps in cascade`;
      execOrder.appendChild(more);
    }
  }

}

function getScopedNodes() {
  const lineage = getActiveLineageSet();
  const wave = allBursts[getCurrentFlushIndex()] || allBursts[0];
  const active = currentViewMode === 'flush' && !focusedNodeId && wave ? getActiveFlushNodeIds(wave) : null;
  return filterItems(reactlogData.nodes || [], (n: any) => {
    const roleKey = nodeRoleKey(n);
    if (lineage ? !lineage.has(n.id) : ((!activeRoles.has(roleKey) || !activeRoles.has(n.role)) || (searchQuery && !Number.isFinite(nodeSearchScore(n, searchQuery))))) return false;
    if (hideClientData && isClientDataNode(n)) return false;
    if (changedNodesOnly && changedNodeIds && !changedNodeIds.has(n.id)) return false;
    if (active && active.size && !active.has(n.id) && !active.has(cleanName(n.id))) return false;
    if (selectedStageFilter && wave) {
      const members = selectedStageFilter === 'invalidated' ? wave.invalidatedNodes || new Set()
        : new Set((selectedStageFilter === 'calcs' ? wave.calcs || [] : wave.outputs || []).map((x: any) => x.nodeId || x.name));
      if (!members.has(n.id) && !members.has(cleanName(n.id))) return false;
    }
    return true;
  });
}

function refreshExploration() {
  renderGraph();
  renderEventList();
}

function updateFilterState(nodes: any) {
  (document.getElementById('filter-node-count') as any).textContent = `${nodes.length} of ${(reactlogData.nodes || []).length} nodes`;
  syncSearchClearButton();
  const clientSelect = (document.getElementById('clientdata-select') as any);
  if (clientSelect) clientSelect.value = hideClientData ? 'hide' : 'show';
  const activitySelect = (document.getElementById('activity-select') as any);
  if (activitySelect) activitySelect.value = currentViewMode;
  const speedSelect = (document.getElementById('playback-speed-select') as any);
  if (speedSelect) speedSelect.value = playbackSpeed;
  syncRoleFilterButtons();
  const chips = (document.getElementById('active-filters') as any);
  chips.replaceChildren();
  const add = (kind: any, label: any, clear: any) => {
    const button = document.createElement('button');
    button.className = 'btn mini'; button.type = 'button';
    button.textContent = label + ' ×'; button.setAttribute('aria-label', `Remove ${kind} filter`);
    button.onclick = () => { clear(); refreshExploration(); };
    chips.appendChild(button);
  };
  if (selectedStageFilter) add('stage', selectedStageFilter, () => { selectedStageFilter = null; });
  if (ALL_ROLES.some((r: any) => !activeRoles.has(r))) add('role', 'Role filter', () => {
    activeRoles = new Set(['source', 'conductor', 'observer', 'effect', 'output']);
  });

  document.querySelectorAll('.pipeline-step-item').forEach((el: any) => el.classList.toggle('is-selected-stage', el.id === `pipe-${selectedStageFilter}`));
  renderEventList();
}

function init() {
  if (Array.isArray(reactlogData) || (reactlogData && (!reactlogData.nodes || !reactlogData.events))) {
    Object.assign(reactlogData, normalizeReactlogData(reactlogData));
  }
  document.addEventListener('click', (e: any) => {
    if (!e.target.closest('.search-wrap')) closeSearchChoices();
    if (!e.target.closest('.settings-wrap')) toggleSettingsMenu(false);
    const nodeBtn = e.target.closest('[data-node-id]');
    if (nodeBtn && nodeBtn.dataset.nodeId) {
      selectNode(nodeBtn.dataset.nodeId);
      return;
    }
    const jumpBtn = e.target.closest('[data-seek-step]');
    if (jumpBtn && jumpBtn.dataset.seekStep) {
      seekTo(parseInt(jumpBtn.dataset.seekStep, 10));
      return;
    }
  });
  initTheme();
  prepareEventTimings();
  buildGraphIndices();
  buildActionWaves();
  changedNodeIds = findChangedNodes();

  const events = reactlogData.events || reactlogData.log || [];
  const nodes = reactlogData.nodes || [];
  const edges = reactlogData.edges || [];

  const scrubber = (document.getElementById('scrubber-range') as any);
  scrubber.max = Math.max(0, events.length - 1);
  scrubber.value = 0;

  showSourceFile(reactlogData.entry_file || Object.keys(reactlogData.sources || {})[0]);
  renderEventList();
  renderGraph();
  initTraceTimeline();
  seekTo(0);
  updateFlushUI();
  setupPanZoom();
  fitGraph();
  setupVideoSync();
  toggleInspector(false);
  setViewMode('full');
}

const reactiveStateColors: Record<string, string> = { ready: 'var(--state-ready)', calculating: 'var(--state-calculating)', invalidating: 'var(--state-invalidating)', invalidated: 'var(--state-invalidated)', frozen: 'var(--state-frozen)', error: 'var(--state-error)' };

function isErrorEvent(ev: any) {
  return ev && (typeof ev.error === 'string' || (ev.action || ev.event) === 'outputError');
}

function reactiveEventState(ev: any) {
  const action = ev.action || ev.event;
  if (isErrorEvent(ev)) return 'error';
  if (['enter', 'execStart', 'wouldEvaluate', 'recalculate', 'render', 'output'].includes(action)) return 'calculating';
  if (action === 'invalidateStart') return 'invalidating';
  if (['invalidateEnd', 'invalidate', 'propagate', 'define'].includes(action)) return 'invalidated';
  if (['exit', 'execEnd', 'ordered', 'outputUpdated', 'valueChange', 'inputChange', 'assumeValue'].includes(action)) return 'ready';
  return null;
}

function graphStateAtStep() {
  const states: Map<any, any> = new Map(), frozen: Set<any> = new Set(), inactiveEdges: Set<any> = new Set();
  const events = reactlogData.events || reactlogData.log || [];
  events.forEach((ev: any) => {
    if ((ev.action || ev.event) === 'dependsOn') inactiveEdges.add(JSON.stringify([ev.edge_from || ev.dependsOn || ev.depOnReactId, ev.edge_to || ev.node_id || ev.reactId || ev.id]));
  });
  for (let i = 0; i <= currentStep && i < events.length; i++) {
    const ev = events[i]!, action = ev.action || ev.event;
    const id = ev.node_id || ev.reactId || ev.id;
    const state = reactiveEventState(ev);
    if (id && state) states.set(id, state);
    if (action === 'freeze') frozen.add(id);
    if (action === 'thaw') frozen.delete(id);
    const from = ev.edge_from || ev.dependsOn || ev.depOnReactId;
    const to = ev.edge_to || id;
    const key = JSON.stringify([from, to]);
    if (action === 'dependsOnRemove') inactiveEdges.add(key);
    if (action === 'dependsOn') inactiveEdges.delete(key);
  }
  frozen.forEach((id: any) => states.set(id, 'frozen'));
  return { states, inactiveEdges };
}

function nodeKind(n: any) {
  if (n.type === 'module') return { label: 'Module', color: 'var(--effect)', lightColor: '#994a78', darkColor: '#e3a4c8', shape: 'M3.2 0.8H11.2V8.8H9.6V2.4H3.2V0.8ZM0.8 3.2H8.8V11.2H0.8V3.2ZM2.6 5V9.4H7V5H2.6Z', verb: 'run' };
  if (n.render_type === 'plot' || n.render_type === 'image') return { label: 'Plot', color: 'var(--output)', lightColor: '#006e59', darkColor: '#5fc7a7', shape: 'M0.8 1H11.2V11H0.8L3.8 6ZM5.2 4.4H8.4V7.6H5.2Z', verb: 'render' };
  if (n.role === 'source' || n.type === 'input') return { label: 'Input', color: 'var(--source)', lightColor: '#005a9c', darkColor: '#56b4e9', shape: 'M0.8 1H8.2L11.2 6L8.2 11H0.8Z', verb: 'change' };
  if (n.role === 'conductor' || n.type === 'calc') return { label: 'Reactive Calc', color: 'var(--calc)', lightColor: '#9c4f00', darkColor: '#e9b44c', shape: 'M0.8 1H8.2L11.2 6L8.2 11H0.8L3.8 6Z', verb: 'run' };
  if (n.type === 'effect') return { label: 'Effect', color: 'var(--effect)', lightColor: '#994a78', darkColor: '#e3a4c8', shape: 'M6 1.2L11.2 10.8H0.8Z', verb: 'trigger' };
  return { label: 'Output', color: 'var(--output)', lightColor: '#006e59', darkColor: '#5fc7a7', shape: 'M0.8 1H11.2V11H0.8L3.8 6Z', verb: 'render' };
}

function toggleInspector(forceState: any) {
  const sidebar = (document.getElementById('sidebar') as any);
  const shouldOpen = forceState !== undefined ? Boolean(forceState) : sidebar.hidden;
  sidebar.hidden = !shouldOpen;
  const mainView = (document.getElementById('main-view') as any);
  if (mainView) mainView.classList.toggle('is-inspector-open', shouldOpen);
  const inspectBtn = (document.getElementById('btn-inspect-selection') as any);
  if (inspectBtn) inspectBtn.hidden = !focusedNodeId || shouldOpen;
  for (const id of ['btn-toggle-inspector', 'btn-toggle-inspector-bottom']) {
    const button = (document.getElementById(id) as any);
    button.classList.toggle('is-active', shouldOpen);
    button.setAttribute('aria-expanded', String(shouldOpen));
  }
}

function closeSidebarAndClearSelection() {
  clearNodeSelection();
  toggleInspector(false);
}

function toggleSettingsMenu(forceState: any) {
  const menu = (document.getElementById('settings-menu') as any);
  const btn = (document.getElementById('btn-settings') as any);
  if (!menu || !btn) return;
  const shouldOpen = forceState !== undefined ? Boolean(forceState) : menu.hidden;
  menu.hidden = !shouldOpen;
  btn.setAttribute('aria-expanded', String(shouldOpen));
  btn.classList.toggle('is-active', shouldOpen);
}

function showSidebarPanel(panelName: any) {
  toggleInspector(true);
  for (const name of ['timeline', 'source']) {
    (document.getElementById(`${name}-panel`) as any).hidden = name !== panelName;
  }
  (document.getElementById('source-tab') as any).setAttribute('aria-selected', String(panelName === 'source'));
  (document.getElementById('detail-panel-title') as any).textContent = panelName === 'source' ? 'App code' : 'Node details';
  if (panelName === 'source') updateSourceHighlight();
}

function toggleRecording(forceState: any) {
  const panel = (document.getElementById('video-panel') as any);
  if (!panel) return;
  panel.hidden = forceState !== undefined ? !forceState : !panel.hidden;
  (document.getElementById('video-tab') as any).setAttribute('aria-expanded', String(!panel.hidden));
}

function escapeHTML(str: any) {
  if (str === null || str === undefined) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function formatTime(sec: any) {
  if (sec === undefined || sec === null) return '';
  const s = Number(sec);
  const mins = Math.floor(s / 60);
  const rem = (s % 60).toFixed(1);
  return `${mins > 0 ? mins + 'm ' : ''}${rem}s`;
}

function nodeDisplayName(value: any): string {
  if (typeof value === 'string') {
    const map = typeof nodeIndex !== 'undefined' ? nodeIndex : null;
    const node = map ? map.get(value) : null;
    if (node) return nodeDisplayName(node);
    const action = value.match(/^(Recalc: |Render: |Click: )(.+)$/);
    if (action && map && map.has(action[2])) return action[1] + nodeDisplayName(map.get(action[2]));
    if (map && value.includes("'")) {
      return value.replace(/'([^']+)'/g, (match: any, token: any) =>
        map.has(token) ? `'${nodeDisplayName(map.get(token))}'` : match
      );
    }
    return value;
  }
  return String(value?.label || value?.name || value?.id || '');
}

function formatEventDetails(ev: any) {
  if (!ev) return '';
  const act = ev.action || ev.event || '';
  if (isErrorEvent(ev)) {
    const node = nodeDisplayName(ev.node_id || ev.reactId || ev.id || ev.node_label || ev.label || '');
    return `${node ? node + ' failed' : 'Execution failed'}${ev.error ? ': ' + ev.error : ''}`;
  }
  if (ev.details) return nodeDisplayName(String(ev.details));
  const nid = ev.node_id || ev.reactId || ev.id || '';
  const lbl = nodeDisplayName(nid || ev.node_label || ev.label || '');
  const fromId = ev.edge_from || ev.depOnReactId || ev.dependsOn || '';
  const toId = ev.edge_to || nid || '';
  if (act === 'dependsOn' && (fromId || toId)) {
    return `Dependency: '${nodeDisplayName(fromId)}' used by '${nodeDisplayName(toId || lbl)}'`;
  }
  if (act === 'dependsOnRemove' && (fromId || toId)) {
    return `Removed dependency: '${nodeDisplayName(fromId)}' used by '${nodeDisplayName(toId || lbl)}'`;
  }
  if (act === 'define' && lbl) return `Defined reactive node '${lbl}'`;
  if ((act === 'invalidate' || act === 'invalidateEnd') && lbl) return `Invalidated '${lbl}'`;
  if (act === 'invalidateStart' && lbl) return `Invalidating '${lbl}'`;
  if ((act === 'valueChange' || act === 'inputChange') && lbl) {
    return ev.value !== undefined && ev.value !== null
      ? `Value change for '${lbl}': ${ev.value}`
      : `Value change for '${lbl}'`;
  }
  if ((act === 'enter' || act === 'wouldEvaluate') && lbl) return `Evaluating '${lbl}'`;
  if ((act === 'exit' || act === 'ordered') && lbl) return `Completed evaluation of '${lbl}'`;
  if (act === 'freeze' && lbl) return `Froze '${lbl}'`;
  if (act === 'thaw' && lbl) return `Thawed '${lbl}'`;
  return lbl ? `Event '${act}' on '${lbl}'` : act;
}

function nodeLabelHTML(node: any, svg = false, maxChars = Infinity) {
  const label = nodeDisplayName(node), moduleName = String(node.module || '');
  let parts = [{ text: label, module: false }];
  if (moduleName) {
    const start = label.indexOf(moduleName);
    parts = start < 0
      ? [{ text: moduleName, module: true }, { text: ' · ' + label, module: false }]
      : [{ text: label.slice(0, start), module: false }, { text: moduleName, module: true }, { text: label.slice(start + moduleName.length), module: false }];
  }
  const length = parts.reduce((total: any, part: any) => total + part.text.length, 0);
  let remaining = length > maxChars ? maxChars - 1 : length;
  const tag = svg ? 'tspan' : 'span';
  const result = parts.map((part: any) => {
    const text = part.text.slice(0, remaining);
    remaining -= text.length;
    return part.module && text
      ? '<' + tag + ' class="module-name">' + escapeHTML(text) + '</' + tag + '>'
      : escapeHTML(text);
  }).join('');
  return result + (length > maxChars ? '…' : '');
}

function graphNodeLabel(node: any) {
  if (node.type === 'module') return nodeLabelHTML(node, true, 28);
  let label = nodeDisplayName(node);
  if (node.module) {
    const [, prefix = '', name = label] = label.match(/^(input[.]|(?:output|calc|effect|reactive)[: ])(.+)$/) || [];
    const namespace = [node.module + '-', node.module + ':'].find((value: any) => name.startsWith(value));
    if (namespace) label = prefix + name.slice(namespace.length);
  }
  const characters = Array.from(label);
  return escapeHTML(characters.length > 28 ? characters.slice(0, 25).join('') + '...' : label);
}

function renderEventList() {
  const list = (document.getElementById('event-list') as any);
  if (!list) return;
  const events = reactlogData.events || reactlogData.log || [];
  const scopedIds = new Set(getScopedNodes().map((n: any) => n.id));
  const scope = JSON.stringify([searchQuery, selectedStageFilter, currentViewMode, [...scopedIds]]);
  if (eventListScope === scope) return;
  eventListScope = scope;
  list.innerHTML = '';
  let visiblePhase: any = null;
  const filtered = searchQuery || selectedStageFilter || currentViewMode === 'flush';
  events.forEach((ev: any, idx: any) => {
    const eventIds = filterItems([ev.node_id || ev.id, ev.edge_from, ev.edge_to], Boolean);
    if (filtered && eventIds.length && !eventIds.some((id: any) => scopedIds.has(id))) return;

    const eventPhase = ev.phase || 'interaction';
    if (eventPhase !== visiblePhase) {
      const phaseLabel = document.createElement('h2');
      phaseLabel.className = 'event-phase-label';
      phaseLabel.textContent = eventPhase === 'init' ? 'Initialization' : 'Recorded actions';
      list.appendChild(phaseLabel);
      visiblePhase = eventPhase;
    }

    const item = document.createElement('button');
    item.type = 'button';
    item.className = 'event-item' + (idx === currentStep ? ' is-current' : '');
    item.setAttribute('data-step', String(idx));
    const nodeId = ev.node_id || ev.id || '';
    const evName = nodeIndex.has(nodeId) ? nodeDisplayName(nodeIndex.get(nodeId)) : nodeDisplayName(ev.node_label || ev.label || ev.event || ev.action);
    const evDetails = formatEventDetails(ev);
    if (nodeId.startsWith('input:')) item.classList.add('kind-input');
    else if (nodeId.startsWith('calc:')) item.classList.add('kind-calc');
    else if (nodeId.startsWith('output:')) item.classList.add('kind-output');
    else if (nodeId.startsWith('effect:')) item.classList.add('kind-effect');
    item.setAttribute('aria-label', `Step ${idx}: ${evName}. ${evDetails}`);
    item.onclick = () => seekTo(idx);

    const header = document.createElement('div');
    header.className = 'event-header';

    const nameWrap = document.createElement('div');
    nameWrap.className = 'event-name-wrap';

    const stepSpan = document.createElement('span');
    stepSpan.className = 'event-step';
    stepSpan.textContent = `#${idx}`;

    const nameSpan = document.createElement('span');
    nameSpan.className = 'event-name';
    nameSpan.innerHTML = nodeIndex.has(nodeId) ? nodeLabelHTML(nodeIndex.get(nodeId)) : escapeHTML(evName);

    nameWrap.appendChild(stepSpan);
    nameWrap.appendChild(nameSpan);

    const badgesWrap = document.createElement('div');
    badgesWrap.className = 'event-badges';

    const tVal = ev.time_sec !== undefined ? ev.time_sec : ev.time;
    if (tVal !== undefined && tVal > 0) {
      const timeSpan = document.createElement('span');
      timeSpan.className = 'event-time';
      timeSpan.textContent = formatTime(tVal);
      badgesWrap.appendChild(timeSpan);
    }

    const provBadge = document.createElement('span');
    const prov = ev.provenance || 'inferred';
    provBadge.className = `event-badge provenance-${prov}`;
    provBadge.innerHTML = `${prov === 'observed' ? ICONS.eye : ICONS.zap} ${prov.toUpperCase()}`;
    badgesWrap.appendChild(provBadge);

    const badge = document.createElement('span');
    badge.className = `event-badge ${ev.status || 'idle'}`;
    badge.textContent = isIdleEvent(ev) ? 'Idle' : (reactiveEventState(ev) || ev.status || ev.action || ev.event);
    badgesWrap.appendChild(badge);

    header.appendChild(nameWrap);
    header.appendChild(badgesWrap);

    const details = document.createElement('div');
    details.className = 'event-details';
    details.textContent = evDetails;

    item.appendChild(header);
    item.appendChild(details);
    list.appendChild(item);
  });
}

function explainWhyNodeRan(nodeId: any, stepIdx: any) {
  const events = reactlogData.events || reactlogData.log || [];
  if (!nodeId) return null;

  const targetNode = nodeIndex.get(nodeId);
  if (!targetNode) return null;

  const kind = nodeKind(targetNode);
  const questionVerb = kind.verb || 'run';

  let curWave = allBursts.find((w: any) => stepIdx >= w.startStep && stepIdx <= w.endStep) || allBursts[0];
  if (!curWave && allBursts.length > 0) curWave = allBursts[0];

  const burstEvents = (curWave && events.length > 0)
    ? events.slice(curWave.startStep, curWave.endStep + 1)
    : events;

  const targetLabel = nodeDisplayName(targetNode);
  const cleanTargetName = cleanName(targetLabel);
  const cleanTargetId = cleanName(targetNode.name || targetNode.id);
  const burstEventForNode = burstEvents.find((e: any) => {
    const eid = e.node_id || e.id || '';
    return eid === nodeId || cleanName(eid) === cleanTargetId || cleanName(eid) === cleanTargetName || (e.node_label && (cleanName(e.node_label) === cleanTargetName || cleanName(e.node_label) === cleanTargetId));
  });

  const ranInBurst = Boolean(curWave && (curWave.isInit || burstEventForNode));
  const directParents = Array.from(adjUpstream.get(nodeId) || []).map((p: any) => nodeIndex.get(p) || { id: p, label: nodeDisplayName(p) });

  if (ranInBurst) {
    const question = `Why did ${targetLabel} ${questionVerb}?`;
    const execTime = (burstEventForNode && (burstEventForNode.time_sec !== undefined ? burstEventForNode.time_sec : burstEventForNode.time))
      || (curWave ? curWave.time : 0);

    const executedNamesInBurst: Set<any> = new Set();
    burstEvents.forEach((e: any) => {
      const eid = e.node_id || e.id || '';
      if (eid) {
        executedNamesInBurst.add(eid);
        executedNamesInBurst.add(cleanName(eid));
      }
      if (e.node_label) executedNamesInBurst.add(cleanName(e.node_label));
    });

    const activeParents = filterItems(directParents, (p: any) =>
      executedNamesInBurst.has(p.id) ||
      executedNamesInBurst.has(cleanName(p.name || p.id)) ||
      executedNamesInBurst.has(cleanName(nodeDisplayName(p)))
    );
    const inactiveParents = filterItems(directParents, (p: any) => !activeParents.includes(p));

    let narrative = '';
    if (targetNode.role === 'source' || targetNode.type === 'input') {
      const valChange = curWave && curWave.humanAction ? curWave.humanAction : targetLabel;
      narrative = `<p><strong>${escapeHTML(targetLabel)}</strong> changed (${escapeHTML(valChange)}) at ${escapeHTML(formatTime(execTime))}.</p>`;
    } else {
      narrative = `<p><strong>${escapeHTML(targetLabel)}</strong> ${escapeHTML(questionVerb)} at ${escapeHTML(formatTime(execTime))}.</p>`;
      if (activeParents.length > 0) {
        narrative += `<div class="why-section-title">Immediate causes:</div><ul class="why-causes-list">${activeParents.map((p: any) => '<li><strong>' + escapeHTML(nodeDisplayName(p)) + '</strong> recalculated</li>').join('')}</ul>`;
      } else if (directParents.length > 0) {
        narrative += `<div class="why-section-title">Immediate causes:</div><ul class="why-causes-list">${directParents.map((p: any) => '<li><strong>' + escapeHTML(nodeDisplayName(p)) + '</strong> changed</li>').join('')}</ul>`;
      } else if (curWave && curWave.humanAction) {
        narrative += `<div class="why-section-title">Immediate causes:</div><ul class="why-causes-list"><li><strong>${escapeHTML(curWave.humanAction)}</strong></li></ul>`;
      }
      if (inactiveParents.length > 0) {
        narrative += `<div class="why-section-title" style="margin-top:0.4rem;opacity:0.75">Other potential dependencies:</div><div style="font:500 0.68rem var(--mono);color:var(--text-muted)">${inactiveParents.map((p: any) => escapeHTML(nodeDisplayName(p))).join(', ')}</div>`;
      }
    }

    return {
      nodeId,
      targetLabel,
      question,
      time: execTime,
      narrative,
      directParents: activeParents.length > 0 ? activeParents : directParents,
      targetNode,
      ranInBurst: true
    };
  } else {
    const actionName = curWave ? (curWave.humanAction || curWave.triggerLabel || 'this action') : 'this action';
    const question = `${targetLabel} did not ${questionVerb}`;

    let lastExec: any = null;
    for (let i = (curWave ? curWave.startStep - 1 : stepIdx); i >= 0; i--) {
      const e = events[i]!;
      const eid = e.node_id || e.id || '';
      if (eid === nodeId || cleanName(eid) === cleanTargetId || cleanName(eid) === cleanTargetName) {
        lastExec = e;
        break;
      }
    }

    let upstreamNote = 'No upstream dependencies were invalidated in this action.';
    if (curWave && curWave.invalidatedNodes && curWave.invalidatedNodes.size > 0) {
      const invParents = filterItems(directParents, (p: any) => curWave.invalidatedNodes.has(p.id));
      if (invParents.length > 0) {
        upstreamNote = `Upstream dependencies invalidated: ${invParents.map((p: any) => escapeHTML(nodeDisplayName(p))).join(', ')}`;
      }
    }
    let narrative = `<div class="did-not-run-banner" style="background:color-mix(in srgb, var(--surface-3) 80%, transparent);border:1px solid var(--border);border-radius:6px;padding:0.5rem 0.6rem;margin-bottom:0.4rem"><div style="font:700 0.72rem var(--sans);color:var(--text)">Did not ${questionVerb} during ${escapeHTML(actionName)}</div><div style="font:500 0.68rem var(--sans);color:var(--text-muted);margin-top:0.2rem">No execution of <strong>${escapeHTML(targetLabel)}</strong> was observed or inferred during this action.</div><div style="font:500 0.64rem var(--mono);color:var(--text-dim);margin-top:0.2rem">${upstreamNote}</div></div>`;
    if (lastExec) {
      const lastTime = lastExec.time_sec !== undefined ? lastExec.time_sec : (lastExec.time || 0);
      narrative += `<div style="display:flex;align-items:center;justify-content:space-between;margin-top:0.3rem"><span style="font:500 0.66rem var(--mono);color:var(--text-muted)">Last ran at ${escapeHTML(formatTime(lastTime))}</span><button type="button" class="btn mini" data-seek-step="${lastExec.step}">Jump to run</button></div>`;
    }
    if (directParents.length > 0) {
      narrative += `<div class="why-section-title" style="margin-top:0.5rem">Potential dependencies:</div><div style="font:500 0.68rem var(--mono);color:var(--text-muted)">${directParents.map((p: any) => escapeHTML(nodeDisplayName(p))).join(', ')}</div>`;
    }

    return {
      nodeId,
      targetLabel,
      question,
      time: null,
      narrative,
      directParents: [],
      targetNode,
      ranInBurst: false
    };
  }
}

function renderInspector() {
  const events = reactlogData.events || reactlogData.log || [];
  const ev = events[currentStep] || {};
  const currentEventNodeId = ev.node_id || ev.id;
  const targetNodeId = selectedNodeId || currentEventNodeId;
  const node = targetNodeId ? nodeIndex.get(targetNodeId) : null;
  renderPlotPreview(node);

  const whyTitle = (document.getElementById('why-title') as any);
  const whyStory = (document.getElementById('why-story') as any);
  const whyFlow = (document.getElementById('why-cascade-flow') as any);

  if (node) {
    const explanation = explainWhyNodeRan(node.id, currentStep);
    if (explanation) {
      whyTitle.textContent = explanation.question;
      whyStory.innerHTML = explanation.narrative;

      whyFlow.innerHTML = '';
      if (explanation.directParents.length > 1) {
        const parentsCol = document.createElement('div');
        parentsCol.className = 'dag-parents-col';
        explanation.directParents.forEach((p: any) => {
          const pill = document.createElement('button');
          pill.type = 'button';
          pill.className = 'flow-node-pill is-trigger';
          pill.innerHTML = nodeLabelHTML(p);
          pill.onclick = () => selectNode(p.id);
          parentsCol.appendChild(pill);
        });
        whyFlow.appendChild(parentsCol);

        const bracket = document.createElement('div');
        bracket.className = 'dag-bracket';
        bracket.textContent = '➔';
        whyFlow.appendChild(bracket);

        const targetCol = document.createElement('div');
        targetCol.className = 'dag-target-col';
        const targetPill = document.createElement('button');
        targetPill.type = 'button';
        targetPill.className = 'flow-node-pill is-target';
        targetPill.innerHTML = nodeLabelHTML(node);
        targetCol.appendChild(targetPill);
        whyFlow.appendChild(targetCol);
      } else if (explanation.directParents.length === 1) {
        const p = explanation.directParents[0];
        const pPill = document.createElement('button');
        pPill.type = 'button';
        pPill.className = 'flow-node-pill is-trigger';
        pPill.innerHTML = nodeLabelHTML(p);
        pPill.onclick = () => selectNode(p.id);
        whyFlow.appendChild(pPill);

        const arrow = document.createElement('span');
        arrow.className = 'dag-bracket';
        arrow.textContent = '➔';
        whyFlow.appendChild(arrow);

        const targetPill = document.createElement('button');
        targetPill.type = 'button';
        targetPill.className = 'flow-node-pill is-target';
        targetPill.innerHTML = nodeLabelHTML(node);
        whyFlow.appendChild(targetPill);
      } else {
        const targetPill = document.createElement('button');
        targetPill.type = 'button';
        targetPill.className = 'flow-node-pill is-trigger is-target';
        targetPill.innerHTML = nodeLabelHTML(node);
        whyFlow.appendChild(targetPill);
      }
    }

    const kind = nodeKind(node);
    (document.getElementById('insp-title') as any).innerHTML = nodeLabelHTML(node) + ' (' + escapeHTML(kind.label) + ')';
    const execCounts = getNodeExecutionCounts();
    const execCount = execCounts.get(node.id) || 0;
    (document.getElementById('insp-meta-line') as any).textContent = filterItems([node.source_file, node.line ? `Line ${node.line}` : 'Unknown'], Boolean).join(' · ');
    const runsEl = (document.getElementById('insp-runs-badge') as any);
    if (runsEl) {
      runsEl.innerHTML = execCount > 0 ? `· Runs: <b>${execCount}×</b>` : '';
    }

    const downstreamSec = (document.getElementById('insp-downstream-section') as any);
    const downstreamWrap = (document.getElementById('insp-downstream-list') as any);
    downstreamWrap.innerHTML = '';
    const children = Array.from(adjDownstream.get(node.id) || []);
    if (children.length === 0) {
      downstreamSec.hidden = true;
    } else {
      downstreamSec.hidden = false;
      children.forEach((c: any) => {
        const cNode = nodeIndex.get(c);
        const pill = document.createElement('button');
        pill.type = 'button';
        pill.className = 'conn-pill';
        pill.innerHTML = cNode ? nodeLabelHTML(cNode) : escapeHTML(c);
        pill.onclick = () => selectNode(c);
        downstreamWrap.appendChild(pill);
      });
    }

    const upstreamSec = (document.getElementById('insp-upstream-section') as any);
    const upstreamWrap = (document.getElementById('insp-upstream-list') as any);
    upstreamWrap.innerHTML = '';
    const parents = Array.from(adjUpstream.get(node.id) || []);
    if (parents.length === 0) {
      upstreamSec.hidden = true;
    } else {
      upstreamSec.hidden = false;
      parents.forEach((p: any) => {
        const pNode = nodeIndex.get(p);
        const pill = document.createElement('button');
        pill.type = 'button';
        pill.className = 'conn-pill';
        pill.innerHTML = pNode ? nodeLabelHTML(pNode) : escapeHTML(p);
        pill.onclick = () => selectNode(p);
        upstreamWrap.appendChild(pill);
      });
    }

    const inspType = (document.getElementById('insp-type') as any);
    if (inspType) inspType.textContent = kind.label;
    const inspStatus = (document.getElementById('insp-status') as any);
    if (inspStatus) inspStatus.textContent = ev.status || 'active';

    const filterBtn = (document.getElementById('btn-filter-lineage') as any);
    if (filterBtn) filterBtn.style.display = 'inline-flex';

    renderInlineSource(node);
  } else if (ev) {
    const filterBtn = (document.getElementById('btn-filter-lineage') as any);
    if (filterBtn) filterBtn.style.display = 'none';

    const evTitle = nodeDisplayName(ev.node_id || ev.id || ev.node_label || ev.label || ev.action || ev.event);
    whyTitle.textContent = evTitle;
    whyStory.innerHTML = `<p>${escapeHTML(formatEventDetails(ev) || 'Step #' + currentStep)}</p>`;
    whyFlow.innerHTML = '';

    (document.getElementById('insp-title') as any).textContent = evTitle;
    (document.getElementById('insp-meta-line') as any).textContent = '—';
    const runsEl = (document.getElementById('insp-runs-badge') as any);
    if (runsEl) runsEl.textContent = '';
    const inspType = (document.getElementById('insp-type') as any);
    if (inspType) inspType.textContent = ev.phase === 'init' ? 'Initialization event' : (ev.action || 'Event');
    const inspStatus = (document.getElementById('insp-status') as any);
    if (inspStatus) inspStatus.textContent = ev.status || 'active';
    (document.getElementById('insp-upstream-section') as any).hidden = true;
    (document.getElementById('insp-downstream-section') as any).hidden = true;
  }
}

const pythonKeywords = new Set(["False", "None", "True", "and", "as", "assert", "async", "await", "break", "class", "continue", "def", "del", "elif", "else", "except", "finally", "for", "from", "global", "if", "import", "in", "is", "lambda", "nonlocal", "not", "or", "pass", "raise", "return", "try", "while", "with", "yield"]);
const highlightedSourceCache: Map<any, any> = new Map();

function highlightedSourceLines(source: any) {
  if (highlightedSourceCache.has(source)) return highlightedSourceCache.get(source);
  // Tokenize the whole file so triple-quoted strings keep their color across lines.
  // Escape every token before adding our own spans; imported JSON contains raw code.
  const tokens = /#[^\r\n]*|[rRuUbBfF]{0,2}(?:"""[\s\S]*?(?:"""|$)|'''[\s\S]*?(?:'''|$)|"(?:\\.|[^"\\\r\n])*"|'(?:\\.|[^'\\\r\n])*')|\b(?:0[xX][\da-fA-F_]+|0[bB][01_]+|0[oO][0-7_]+|\d[\d_]*(?:\.[\d_]*)?(?:[eE][+-]?[\d_]+)?[jJ]?)|\b[A-Za-z_]\w*\b|[-+*/%=<>!&|^~:@.,;()[\]{}]/g;
  let markup = '', cursor = 0;
  for (const match of source.matchAll(tokens)) {
    const token = match[0];
    markup += escapeHTML(source.slice(cursor, match.index));
    let kind = '';
    if (token.startsWith('#')) kind = 'comment';
    else if (/^[rRuUbBfF]{0,2}["']/.test(token)) kind = 'string';
    else if (/^\d/.test(token)) kind = 'number';
    else if (pythonKeywords.has(token)) kind = 'keyword';
    else if (!/^\w/.test(token)) kind = 'operator';
    // Close spans on each line so snippets can be sliced without broken markup.
    markup += token.split('\n').map((part: any) => kind && part
      ? `<span class="syntax-${kind}">${escapeHTML(part)}</span>` : escapeHTML(part)).join('\n');
    cursor = match.index + token.length;
  }
  markup += escapeHTML(source.slice(cursor));
  const lines = markup.split('\n');
  if (lines.at(-1) === '') lines.pop();
  highlightedSourceCache.set(source, lines);
  return lines;
}

function sourceLineHTML(content: any, lineNum: any, active = false) {
  return `<div class="source-line${active ? ' is-active' : ''}" data-line="${lineNum}"><span class="source-line-num" aria-hidden="true">${lineNum}</span><span class="source-line-content">${content}</span></div>`;
}

let displayedSourceFile = '';

function nodeSource(node: any) {
  return (reactlogData.sources || {})[node?.source_file] || rawAppSource;
}

function showSourceFile(filename: any) {
  const sources = reactlogData.sources || {};
  if (!Object.prototype.hasOwnProperty.call(sources, filename)) return;
  const selector = (document.getElementById('source-file-select') as any);
  selector.replaceChildren();
  Object.keys(sources).forEach((name: any) => {
    const option = document.createElement('option');
    option.value = name; option.textContent = name;
    selector.appendChild(option);
  });
  selector.hidden = false;
  selector.value = filename;
  displayedSourceFile = filename;
  const code = (document.querySelector('#source-panel code') as any);
  code.innerHTML = highlightedSourceLines(sources[filename]).map((line: any, i: any) => sourceLineHTML(line, i + 1)).join('');
}

function renderInlineSource(node: any) {
  const drawer = (document.getElementById('insp-source-drawer') as any);
  const codeBlock = (document.getElementById('insp-source-code') as any);
  const refsBlock = (document.getElementById('insp-source-refs') as any);
  const source = nodeSource(node);
  if (!drawer || !codeBlock || !source) return;

  if (!node.line) {
    drawer.hidden = true;
    return;
  }

  drawer.hidden = false;
  const lines = highlightedSourceLines(source);
  const startLine = Math.max(0, node.line - 1);
  const endLine = Math.min(lines.length, startLine + 4);

  let snippetHtml = '';
  for (let i = startLine; i < endLine; i++) {
    const lineNum = i + 1;
    snippetHtml += sourceLineHTML(lines[i], lineNum, lineNum === node.line);
  }
  codeBlock.querySelector('code').innerHTML = snippetHtml;

  if (refsBlock) {
    const children = Array.from(adjDownstream.get(node.id) || []);
    if (children.length > 0) {
      refsBlock.hidden = false;
      const refButtons = children.map((c: any) => {
        const cNode = nodeIndex.get(c);
        const lbl = cNode ? nodeDisplayName(cNode) : nodeDisplayName(c);
        const lineStr = cNode && cNode.line ? ` · line ${cNode.line}` : '';
        return `<button type="button" class="conn-pill" data-node-id="${escapeHTML(c)}">${escapeHTML(lbl)}${lineStr}</button>`;
      }).join(' ');
      refsBlock.innerHTML = `<span>Referenced by:</span> ${refButtons}`;
    } else {
      refsBlock.hidden = true;
    }
  }
}

function toggleSourceDrawer() {
  const codeBlock = (document.getElementById('insp-source-code') as any);
  const arrow = (document.getElementById('source-drawer-arrow') as any);
  const btn = (document.getElementById('btn-toggle-source-drawer') as any);
  if (!codeBlock || !arrow || !btn) return;
  isSourceDrawerOpen = !isSourceDrawerOpen;
  codeBlock.hidden = !isSourceDrawerOpen;
  arrow.textContent = isSourceDrawerOpen ? '▴' : '▾';
  btn.setAttribute('aria-expanded', String(isSourceDrawerOpen));
}

function selectNode(nodeId: any) {
  selectedNodeId = nodeId;
  focusedNodeId = nodeId;
  showSidebarPanel('timeline');
  renderInspector();
  renderGraph();
  updateSourceHighlight();
  updateTraceTimelineScrubber(getCurrentStepTime());
}

function clearNodeSelection() {
  focusedNodeId = null;
  selectedNodeId = null;
  if (selectedSearchNodeId) {
    selectedSearchNodeId = null;
    searchQuery = '';
    (document.getElementById('search-input') as any).value = '';
  }
  renderInspector();
  renderGraph();
  updateSourceHighlight();
  updateTraceTimelineScrubber(getCurrentStepTime());
}

const collapsedModules: Set<any> = new Set();

// Rank the condensed graph: cycles share a rank, every other edge goes right.
function dependencyRanks(nodes: any, edges: any) {
  const children: Map<any, any[]> = new Map(nodes.map((n: any) => [n.id, []]));
  edges.forEach((e: any) => children.get(e.from)?.push(e.to));
  let serial = 0;
  const indices: Map<any, any> = new Map(), low: Map<any, any> = new Map(), stack: any[] = [], onStack: Set<any> = new Set();
  const component: Map<any, any> = new Map(), components: any[] = [];
  function visit(id: any) {
    indices.set(id, serial); low.set(id, serial++); stack.push(id); onStack.add(id);
    for (const next of children.get(id) || []) {
      if (!indices.has(next)) { visit(next); low.set(id, Math.min(low.get(id), low.get(next))); }
      else if (onStack.has(next)) low.set(id, Math.min(low.get(id), indices.get(next)));
    }
    if (low.get(id) === indices.get(id)) {
      const members: any[] = []; let next: any;
      do { next = stack.pop(); onStack.delete(next); component.set(next, components.length); members.push(next); } while (next !== id);
      components.push(members);
    }
  }
  nodes.forEach((n: any) => { if (!indices.has(n.id)) visit(n.id); });
  const ranks = components.map(() => 0), incoming = components.map(() => 0), outgoing: Set<any>[] = components.map(() => new Set());
  edges.forEach((e: any) => {
    const from = component.get(e.from), to = component.get(e.to);
    if (from !== to && !outgoing[from]!.has(to)) { outgoing[from]!.add(to); incoming[to]++; }
  });
  const queue = filterItems(incoming.map((count: any, i: any) => count === 0 ? i : -1), (i: any) => i >= 0);
  for (let i = 0; i < queue.length; i++) {
    const from = queue[i];
    outgoing[from]!.forEach((to: any) => { ranks[to] = Math.max(ranks[to]!, ranks[from]! + 1); if (--incoming[to]! === 0) queue.push(to); });
  }
  return new Map(nodes.map((n: any) => [n.id, ranks[component.get(n.id)]]));
}

function arrangeGraphBand(members: any, edges: any, ranks: any, top: any, colWidth: any, rowHeight: any) {
  const columns: Map<any, any> = new Map();
  members.forEach((n: any) => {
    const rank = ranks.get(n.id);
    if (!columns.has(rank)) columns.set(rank, []);
    columns.get(rank).push(n);
  });
  const ordered = [...columns.keys()].sort((a: any, b: any) => a - b);
  const order: Map<any, any> = new Map();
  columns.forEach((col: any) => col.forEach((n: any, i: any) => order.set(n.id, i)));
  // Alternate sweeps group nodes by their neighbours without moving them across modules.
  for (let pass = 0; pass < 4; pass++) {
    const reverse = pass % 2 === 1;
    for (const rank of reverse ? ordered.slice().reverse() : ordered) {
      const col = columns.get(rank), scores: Map<any, any> = new Map();
      col.forEach((n: any) => {
        const peers = filterItems(filterItems(edges, (e: any) => reverse ? e.from === n.id : e.to === n.id)
          .map((e: any) => reverse ? e.to : e.from), (id: any) => order.has(id));
        scores.set(n.id, peers.length
          ? peers.reduce((sum: any, id: any) => sum + order.get(id) + ranks.get(id) / 1000, 0) / peers.length
          : order.get(n.id));
      });
      col.sort((a: any, b: any) => scores.get(a.id) - scores.get(b.id) || order.get(a.id) - order.get(b.id));
      col.forEach((n: any, i: any) => order.set(n.id, i));
    }
  }
  const rows = Math.max(1, ...[...columns.values()].map((col: any) => col.length));
  const positions: Record<string, any> = {};
  for (const rank of ordered) {
    const col = columns.get(rank);
    let previous = -1;
    col.forEach((n: any, i: any) => {
      const parents = filterItems(edges, (e: any) => e.to === n.id && positions[e.from]).map((e: any) => positions[e.from].y);
      const preferred = parents.length
        ? Math.round((parents.reduce((sum: any, y: any) => sum + y, 0) / parents.length - top - 40) / rowHeight)
        : i;
      const row = Math.max(previous + 1, Math.min(rows - col.length + i, preferred));
      positions[n.id] = { x: 150 + rank * colWidth, y: top + 40 + row * rowHeight };
      previous = row;
    });
  }
  return { positions, rows };
}

function routeGraphEdge(edge: any, positions: any, nodeWidth: any, nodeHeight: any, edges: any = []) {
  const from = positions[edge.from], to = positions[edge.to];
  if (!from || !to) return [];
  const offset = (outgoing: any, id: any) => {
    const refY = positions[id].y;
    const peers = filterItems(edges, (e: any) => outgoing ? e.from === id : e.to === id)
      .sort((a: any, b: any) => {
        const first = outgoing ? a.to : a.from, second = outgoing ? b.to : b.from;
        const dy = positions[first].y - positions[second].y;
        if (dy !== 0) return dy;
        const dx = positions[first].x - positions[second].x;
        if (dx !== 0) return positions[first].y <= refY ? dx : -dx;
        return first.localeCompare(second);
      });
    const index = peers.indexOf(edge);
    return peers.length > 1 && index >= 0
      ? (index / (peers.length - 1) - 0.5) * Math.min(nodeHeight - 20, (peers.length - 1) * 12) : 0;
  };
  const x1 = from.x + nodeWidth / 2, y1 = from.y + offset(true, edge.from);
  const forward = to.x > from.x;
  const x2 = to.x + (forward ? -1 : 1) * nodeWidth / 2, y2 = to.y + offset(false, edge.to);
  const lane = Math.max(0, edges.indexOf(edge));
  let points: any;
  if (forward && x2 - x1 < nodeWidth) {
    const gutter = x1 + (x2 - x1) * (0.3 + (lane % 7) * 0.065);
    points = [[x1, y1], [gutter, y1], [gutter, y2], [x2, y2]];
  } else {
    const clearance = 12, inset = 18 + (lane % 4) * 4;
    const exit = x1 + inset, entry = x2 + (forward ? -inset : inset);
    const left = Math.min(exit, entry), right = Math.max(exit, entry);
    const obstacles = filterItems(Object.values(positions), (p: any) =>
      p.x + nodeWidth / 2 + clearance > left && p.x - nodeWidth / 2 - clearance < right);
    const gapMidpoints: any[] = [];
    const ys = [...new Set(obstacles.map((p: any) => p.y))].sort((a: any, b: any) => a - b);
    const topPad = (py: any) => {
      const idx = ys.indexOf(py);
      return (idx === 0 || (idx > 0 && py - ys[idx - 1] > 120)) ? 42 : clearance;
    };
    for (let i = 1; i < ys.length; i++) {
      const upperBottom = ys[i - 1] + nodeHeight / 2 + clearance;
      const lowerTop = ys[i] - nodeHeight / 2 - topPad(ys[i]);
      if (lowerTop >= upperBottom) gapMidpoints.push((upperBottom + lowerTop) / 2);
    }
    if (ys.length) {
      gapMidpoints.push(ys[0] - nodeHeight / 2 - topPad(ys[0]) - 6);
      gapMidpoints.push(ys[ys.length - 1] + nodeHeight / 2 + clearance + 10);
    }
    const candidates = [y1, y2, (y1 + y2) / 2, ...gapMidpoints, ...obstacles.flatMap((p: any) =>
      [p.y - nodeHeight / 2 - topPad(p.y), p.y + nodeHeight / 2 + clearance])];
    const minClear = (y: any) => obstacles.length
      ? Math.min(...obstacles.map((p: any) => Math.abs(y - p.y) - nodeHeight / 2))
      : 40;
    const targetColNodes = filterItems(Object.values(positions), (p: any) => p !== to && Math.abs(p.x - to.x) < nodeWidth);
    const spanEdges = filterItems(edges, (o: any) => o !== edge && positions[o.from] && positions[o.to] &&
      Math.max(positions[o.from].x, positions[o.to].x) >= left && Math.min(positions[o.from].x, positions[o.to].x) <= right);
    const crossCost = (y: any) => {
      const minY = Math.min(y, y2), maxY = Math.max(y, y2);
      let penalty = 0;
      for (const p of targetColNodes) {
        if (p.y >= minY - nodeHeight / 2 && p.y <= maxY + nodeHeight / 2) penalty += 500;
      }
      for (const o of spanEdges) {
        const oy1 = positions[o.from].y, oy2 = positions[o.to].y;
        if ((y - oy1) * (y2 - oy2) < 0 || (oy2 > minY && oy2 < maxY)) penalty += 250;
      }
      return penalty;
    };
    const cost = (y: any) => Math.abs(y1 - y) + Math.abs(y2 - y) + Math.abs(y - y2) * 0.15 + crossCost(y) - Math.min(45, minClear(y)) * 0.4;
    const valid = filterItems(candidates, (candidate: any) => obstacles.every((p: any) =>
      candidate <= p.y - nodeHeight / 2 - topPad(p.y) || candidate >= p.y + nodeHeight / 2 + clearance));
    let y = (valid.length ? valid : candidates).sort((a: any, b: any) => cost(a) - cost(b))[0];
    const stagger = ((lane % 5) - 2) * 4;
    if (obstacles.length && y !== y1 && y !== y2 && stagger && obstacles.every((p: any) => (y + stagger) <= p.y - nodeHeight / 2 - topPad(p.y) || (y + stagger) >= p.y + nodeHeight / 2 + clearance)) {
      y += stagger;
    }
    points = [[x1, y1], [exit, y1], [exit, y], [entry, y], [entry, y2], [x2, y2]];
  }
  const route: any[] = [];
  for (const point of points) {
    const last = route[route.length - 1];
    if (last && last[0] === point[0] && last[1] === point[1]) continue;
    while (route.length > 1) {
      const a = route[route.length - 2], b = route[route.length - 1];
      if ((a[0] === b[0] && b[0] === point[0]) || (a[1] === b[1] && b[1] === point[1])) route.pop();
      else break;
    }
    route.push(point);
  }
  return route;
}

function graphEdgePath(edge: any, positions: any, nodeWidth: any, nodeHeight: any, edges: any = []) {
  const route = routeGraphEdge(edge, positions, nodeWidth, nodeHeight, edges);
  if (route.length < 2) return '';
  const from = positions[edge.from], to = positions[edge.to];
  const portX = (p: any, yOff: any, side: any) => {
    const edgeX = p.x + (side === 'right' ? 1 : -1) * nodeWidth / 2;
    const type = p?.nodeType, role = p?.nodeRole || type;
    if (!type || type === 'module') return edgeX;
    const wc = 20, t = Math.min(1, Math.abs(yOff) / (nodeHeight / 2));
    if (side === 'right' && (role === 'source' || type === 'input' || role === 'conductor' || type === 'calc')) return edgeX - wc * t;
    if (side === 'left' && role !== 'source' && type !== 'input') return edgeX + wc * (1 - t);
    return edgeX;
  };
  const forward = to.x > from.x;
  const [, y1] = route[0], [, y2] = route[route.length - 1];
  const x1 = portX(from, y1 - from.y, 'right');
  const x2 = portX(to, y2 - to.y, forward ? 'left' : 'right');
  const clearance = 12;
  const toLeft = to.x - nodeWidth / 2;
  const lineSeg = (ax: number, ay: number, bx: number, by: number) =>
    `C ${(2 * ax + bx) / 3} ${(2 * ay + by) / 3}, ${(ax + 2 * bx) / 3} ${(ay + 2 * by) / 3}, ${bx} ${by}`;
  const hasNotchLead = forward && x2 > toLeft + 0.5 && Math.abs(y2 - y1) > 1;
  const curveEndX = hasNotchLead ? Math.max(x1 + 12, toLeft - 4) : x2;
  const dx = Math.max(24, (curveEndX - x1) * 0.45);
  const canCurveDirectly = curveEndX > x1 && (() => {
    const obs = Object.entries(positions).filter(([id]: any) => id !== edge.from && id !== edge.to);
    if (!obs.length) return true;
    const cx1 = x1 + dx, cx2 = curveEndX - dx;
    for (let step = 1; step < 20; step++) {
      const t = step / 20, mt = 1 - t;
      const bx = mt * mt * mt * x1 + 3 * mt * mt * t * cx1 + 3 * mt * t * t * cx2 + t * t * t * curveEndX;
      const by = mt * mt * mt * y1 + 3 * mt * mt * t * y1 + 3 * mt * t * t * y2 + t * t * t * y2;
      if (obs.some(([, p]: any) => Math.abs(bx - p.x) < nodeWidth / 2 + clearance && Math.abs(by - p.y) < nodeHeight / 2 + clearance)) {
        return false;
      }
    }
    return true;
  })();
  if (canCurveDirectly) {
    const curve = `M ${x1} ${y1} C ${x1 + dx} ${y1}, ${curveEndX - dx} ${y2}, ${curveEndX} ${y2}`;
    return hasNotchLead ? `${curve} ${lineSeg(curveEndX, y2, x2, y2)}` : curve;
  }
  const isGutterRoute = forward && (to.x - from.x - nodeWidth) < nodeWidth;
  const laneY = !isGutterRoute && route.length >= 5
    ? route[2][1]
    : !isGutterRoute && route.length === 4
      ? (Math.abs(route[1][0] - route[0][0]) >= Math.abs(route[3][0] - route[2][0]) ? route[1][1] : route[2][1])
      : (y1 + y2) / 2;
  if (forward) {
    const lane = Math.max(0, edges.indexOf(edge));
    const outPeers = filterItems(edges, (e: any) => e.from === edge.from && positions[e.to])
      .sort((a: any, b: any) => positions[a.to].y - positions[b.to].y || a.to.localeCompare(b.to));
    const outIdx = Math.max(0, outPeers.indexOf(edge));
    const outSlot = laneY < y1 ? outIdx : Math.max(0, outPeers.length - 1 - outIdx);
    const fromRight = from.x + nodeWidth / 2;
    const midObs = filterItems(Object.values(positions), (p: any) => p.x - nodeWidth / 2 > fromRight && p.x + nodeWidth / 2 < toLeft);
    let exitX: any, entryX: any;
    if (midObs.length) {
      const firstObsLeft = Math.min(...midObs.map((p: any) => p.x - nodeWidth / 2));
      const lastObsRight = Math.max(...midObs.map((p: any) => p.x + nodeWidth / 2));
      exitX = Math.max(fromRight + 16, Math.min(firstObsLeft - 16, fromRight + 28 + outSlot * 12));
      entryX = Math.min(toLeft - 24, Math.max(lastObsRight + 16, toLeft - 34 - (lane % 4) * 6));
      if (entryX < exitX) entryX = exitX = (exitX + entryX) / 2;
    } else {
      exitX = Math.min((fromRight + toLeft) / 2, fromRight + 42 + outSlot * 10);
      entryX = Math.max(exitX, toLeft - 42);
    }
    const spanX = Math.max(8, entryX - exitX);
    const dy1 = laneY - y1, ad1 = Math.abs(dy1), s1 = Math.sign(dy1);
    const dy2 = y2 - laneY, ad2 = Math.abs(dy2), s2 = Math.sign(dy2);
    const r1 = Math.min(22, ad1 / 2, spanX / 2);
    const r2 = Math.min(22, ad2 / 2, spanX / 2, Math.max(6, toLeft - entryX - 2));
    const segs = [`M ${x1} ${y1}`];
    if (ad1 < 2) {
      segs.push(lineSeg(x1, y1, exitX + r1, laneY));
    } else {
      segs.push(`C ${(x1 + exitX) / 2} ${y1}, ${exitX} ${y1}, ${exitX} ${y1 + s1 * r1}`);
      if (ad1 > 2 * r1 + 0.5) segs.push(lineSeg(exitX, y1 + s1 * r1, exitX, laneY - s1 * r1));
      segs.push(`C ${exitX} ${laneY - s1 * r1 * 0.45}, ${exitX + r1 * 0.45} ${laneY}, ${exitX + r1} ${laneY}`);
    }
    if (entryX - r2 > exitX + r1 + 0.5) {
      segs.push(lineSeg(exitX + r1, laneY, entryX - r2, laneY));
    }
    if (ad2 < 2) {
      segs.push(lineSeg(Math.max(exitX + r1, entryX - r2), laneY, x2, y2));
    } else {
      segs.push(`C ${entryX - r2 * 0.45} ${laneY}, ${entryX} ${laneY + s2 * r2 * 0.45}, ${entryX} ${laneY + s2 * r2}`);
      if (ad2 > 2 * r2 + 0.5) segs.push(lineSeg(entryX, laneY + s2 * r2, entryX, y2 - s2 * r2));
      segs.push(`C ${entryX} ${y2 - s2 * r2 * 0.45}, ${entryX + r2 * 0.45} ${y2}, ${entryX + r2} ${y2}`);
      segs.push(lineSeg(entryX + r2, y2, x2, y2));
    }
    return segs.join(' ');
  }
  const exitX = route[1][0], entryX = route[route.length - 2][0];
  const midStart = (x1 + exitX) / 2, midEnd = (x2 + entryX) / 2;
  return `M ${x1} ${y1} C ${exitX} ${y1}, ${exitX} ${laneY}, ${midStart} ${laneY} C ${(2 * midStart + midEnd) / 3} ${laneY}, ${(midStart + 2 * midEnd) / 3} ${laneY}, ${midEnd} ${laneY} C ${entryX} ${laneY}, ${entryX} ${y2}, ${x2} ${y2}`;
}

function toggleModule(name: any) {
  if (collapsedModules.has(name)) collapsedModules.delete(name);
  else collapsedModules.add(name);
  renderGraph(); fitGraph();
}

function renderPlotPreview(node: any) {
  const panel = (document.getElementById('insp-plot') as any);
  const img = (document.getElementById('insp-plot-image') as any);
  const caption = (document.getElementById('insp-plot-caption') as any);
  const events = reactlogData.events || reactlogData.log || [];
  const preview = node && events.slice(0, currentStep + 1).reverse().find((e: any) => e.node_id === node.id && e.plot);
  panel.hidden = !node || (node.render_type !== 'plot' && node.render_type !== 'image' && !preview);
  img.hidden = !preview;
  img.removeAttribute('src');
  if (preview && /^data:image\/(png|jpeg|gif|webp);base64,/.test(preview.plot.src)) {
    img.src = preview.plot.src;
    img.alt = preview.plot.alt || node.label;
    caption.textContent = `Recorded plot · ${Number(preview.time_sec || 0).toFixed(2)}s`;
  } else {
    img.hidden = true;
    caption.textContent = 'No plot captured at this step. Record the app to preview rendered plots here.';
  }
}

function getNodeExecutionCounts() {
  const counts: Map<any, any> = new Map();
  const events = reactlogData.events || reactlogData.log || [];
  events.forEach((ev: any) => {
    const nid = ev.node_id || ev.id;
    if (!nid) return;
    if (ev.event === 'ordered' || ev.event === 'outputUpdated' || ev.event === 'inputChange' || ev.event === 'assumeValue') {
      counts.set(nid, (counts.get(nid) || 0) + 1);
    }
  });
  return counts;
}

function toggleShortcutsModal() {
  const modal = (document.getElementById('shortcuts-modal') as any);
  if (!modal) return;
  const isHidden = modal.hidden;
  modal.hidden = !isHidden;
  if (isHidden) {
    modal.querySelector('.modal-close-btn')?.focus();
  }
}

function getNodeShapePath(n: any, p: any, width: any, height: any) {
  const role = n.role || n.type;
  const x0 = p.x - width / 2;
  const x1 = p.x + width / 2;
  const y0 = p.y - height / 2;
  const y1 = p.y + height / 2;
  const ym = p.y;
  const wc = 20;

  if (n.type === 'module') {
    return `M ${x0} ${y0} H ${x1} V ${y1} H ${x0} Z`;
  }
  if (role === 'source' || n.type === 'input') {
    return `M ${x0} ${y0} H ${x1 - wc} L ${x1} ${ym} L ${x1 - wc} ${y1} H ${x0} Z`;
  }
  if (role === 'conductor' || n.type === 'calc') {
    return `M ${x0} ${y0} H ${x1 - wc} L ${x1} ${ym} L ${x1 - wc} ${y1} H ${x0} L ${x0 + wc} ${ym} Z`;
  }
  return `M ${x0} ${y0} H ${x1} V ${y1} H ${x0} L ${x0 + wc} ${ym} Z`;
}

function renderGraph(previousStep = currentStep) {
  const svg = (document.getElementById('graph-content') as any);
  if (!svg) return;
  svg.innerHTML = '';
  const isLight = getActiveTheme() === 'light';
  const visibleNodes: any[] = [];
  const representatives: Map<any, any> = new Map();
  const moduleNodes: Map<any, any> = new Map();
  const focusedNodes = focusedNodeId ? new Set([
    focusedNodeId, ...getUpstreamNodes(focusedNodeId), ...getDownstreamNodes(focusedNodeId)
  ]) : null;
  const clearBtn = (document.getElementById('btn-clear-selection') as any);
  if (clearBtn) clearBtn.hidden = !focusedNodeId;
  const inspectBtn = (document.getElementById('btn-inspect-selection') as any);
  if (inspectBtn) inspectBtn.hidden = !focusedNodeId || !(document.getElementById('sidebar') as any).hidden;
  const railInspectorBtn = (document.getElementById('btn-toggle-inspector-bottom') as any);
  if (railInspectorBtn) railInspectorBtn.classList.toggle('has-selection', Boolean(focusedNodeId));

  const scopedNodes = getScopedNodes();
  (document.getElementById('empty-graph-message') as any).hidden = !(changedNodesOnly && changedNodeIds && !scopedNodes.length && !searchQuery);
  updateFilterState(scopedNodes);
  scopedNodes.forEach((n: any) => {
    if (n.module && collapsedModules.has(n.module)) {
      const id = `module:${n.module}`;
      representatives.set(n.id, id);
      if (!moduleNodes.has(id)) {
        const group = { id, label: n.module, type: 'module', role: 'conductor', module: n.module, members: [] };
        moduleNodes.set(id, group); visibleNodes.push(group);
      }
      moduleNodes.get(id).members.push(n.id);
    } else { representatives.set(n.id, n.id); visibleNodes.push(n); }
  });
  const nodes = visibleNodes;
  const replay = graphStateAtStep();
  const edges: any[] = [], edgeKeys: Map<any, any> = new Map();
  (reactlogData.edges || []).forEach((e: any) => {
    const from = representatives.get(e.from), to = representatives.get(e.to);
    if (!from || !to || from === to) return;
    const key = JSON.stringify([from, to]);
    const related = !focusedNodes || (focusedNodes.has(e.from) && focusedNodes.has(e.to));
    if (!edgeKeys.has(key)) {
      const edge = { from, to, isolated: Boolean(e.isolated), inactive: replay.inactiveEdges.has(JSON.stringify([e.from, e.to])), related };
      edges.push(edge); edgeKeys.set(key, edge);
    } else if (related) edgeKeys.get(key).related = true;
  });

  const ranks = dependencyRanks(nodes, edges);
  const colWidth = 350, rowHeight = 92, nodeWidth = 280, nodeHeight = 64;
  const pos: Record<string, any> = {};
  // Module bands keep boxes disjoint while dependency rank sets horizontal position.
  const bands: Map<any, any> = new Map();
  nodes.forEach((n: any) => { const key = n.module || ''; if (!bands.has(key)) bands.set(key, []); bands.get(key).push(n); });
  const hasAppBand = bands.has('');
  const hasNamedModules = [...bands.keys()].some((name: any) => name !== '');
  const placedBands: any[] = [];
  let top = 70;
  if (hasAppBand && hasNamedModules) {
    const appMembers = bands.get('');
    const appLayout = arrangeGraphBand(appMembers, edges, ranks, 70, colWidth, rowHeight);
    Object.assign(pos, appLayout.positions);
    const appLeft = Math.min(...appMembers.map((n: any) => pos[n.id].x)) - nodeWidth / 2 - 20;
    const appRight = Math.max(appLeft + 320, Math.max(...appMembers.map((n: any) => pos[n.id].x)) + nodeWidth / 2 + 20);
    const appHeight = appLayout.rows * rowHeight + 20;
    let modMinX = Infinity;
    for (const [name, members] of bands) {
      if (!name) continue;
      const layout = arrangeGraphBand(members, edges, ranks, top, colWidth, rowHeight);
      Object.assign(pos, layout.positions);
      members.forEach((n: any) => { if (pos[n.id].x < modMinX) modMinX = pos[n.id].x; });
      placedBands.push({ name, members, rows: layout.rows, top });
      top += layout.rows * rowHeight + 75;
    }
    const modShiftX = (appRight + 140) - (modMinX - nodeWidth / 2 - 20);
    placedBands.forEach((b: any) => b.members.forEach((n: any) => { pos[n.id].x += modShiftX; }));
    const modSpan = (top - 75 + 20 - 28) - (70 - 28);
    const appShiftY = Math.max(0, Math.round((modSpan - appHeight) / 2));
    appMembers.forEach((n: any) => { pos[n.id].y += appShiftY; });
    placedBands.unshift({ name: '', members: appMembers, rows: appLayout.rows, top: 70 + appShiftY });
  } else {
    for (const [name, members] of bands) {
      const layout = arrangeGraphBand(members, edges, ranks, top, colWidth, rowHeight);
      Object.assign(pos, layout.positions);
      placedBands.push({ name, members, rows: layout.rows, top });
      top += layout.rows * rowHeight + 75;
    }
  }
  nodes.forEach((n: any) => {
    if (pos[n.id]) {
      pos[n.id].nodeType = n.type;
      pos[n.id].nodeRole = n.role || n.type;
    }
  });
  for (const { name, members, rows, top: bandTop } of placedBands) {
    if (!name || !collapsedModules.has(name)) {
      const left = Math.min(...members.map((n: any) => pos[n.id].x)) - nodeWidth / 2 - 20;
      const right = Math.max(...members.map((n: any) => pos[n.id].x)) + nodeWidth / 2 + 20;
      const box = document.createElementNS('http://www.w3.org/2000/svg', 'g');
      const dimmed = focusedNodes && !members.some((n: any) => focusedNodes.has(n.id));
      box.setAttribute('class', String((name ? 'module-box' : 'app-box') + (dimmed ? ' is-dimmed' : '')));
      if (name) {
        box.setAttribute('data-module', String(name));
        box.setAttribute('tabindex', '0');
        box.setAttribute('role', 'region');
        box.setAttribute('aria-label', `Module ${name}`);
        box.onkeydown = (e: any) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); e.stopPropagation(); toggleModule(name); } };
      }
      const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
      rect.setAttribute('x', String(left));
      rect.setAttribute('y', String(bandTop - 28));
      rect.setAttribute('width', String(Math.max(320, right - left)));
      rect.setAttribute('height', String(rows * rowHeight + 20));
      rect.setAttribute('rx', '12');
      rect.setAttribute('fill', String(isLight ? '#e0f2fe66' : '#17314b55'));
      rect.setAttribute('stroke', String(isLight ? '#3b6b91' : '#5b82a6'));
      rect.setAttribute('stroke-dasharray', '5 4');
      rect.onclick = (e: any) => e.stopPropagation();
      box.appendChild(rect);

      if (name) {
        const headerBtn = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        headerBtn.setAttribute('class', 'module-collapse-btn');
        headerBtn.setAttribute('tabindex', '0');
        headerBtn.setAttribute('role', 'button');
        headerBtn.setAttribute('aria-expanded', 'true');
        headerBtn.setAttribute('aria-label', `Collapse module ${name}`);
        headerBtn.onclick = (e: any) => { e.stopPropagation(); toggleModule(name); };
        headerBtn.ondblclick = (e: any) => { e.stopPropagation(); toggleModule(name); };
        headerBtn.onkeydown = (e: any) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); e.stopPropagation(); toggleModule(name); } };

        const label = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        label.setAttribute('x', String(left + 14));
        label.setAttribute('y', String(bandTop - 8));
        label.setAttribute('fill', String(isLight ? '#315575' : '#a4c7e7'));
        label.setAttribute('font-size', '12');
        label.innerHTML = nodeLabelHTML({ label: name, module: name }, true) + escapeHTML(` · ${members.length} nodes · click to collapse`);
        headerBtn.appendChild(label);

        const textWidth = (label.getComputedTextLength && label.getComputedTextLength()) || (name.length * 8 + 190);
        const iconX = left + 14 + textWidth + 8;
        const iconY = bandTop - 19;

        const iconG = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        iconG.setAttribute('class', 'module-collapse-icon');
        iconG.setAttribute('transform', `translate(${iconX}, ${iconY})`);
        iconG.setAttribute('aria-hidden', 'true');

        const iconBg = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        iconBg.setAttribute('width', '16');
        iconBg.setAttribute('height', '16');
        iconBg.setAttribute('rx', '3');
        iconBg.setAttribute('fill', String(isLight ? '#e2e8f0' : '#1e293b'));
        iconBg.setAttribute('stroke', String(isLight ? '#94a3b8' : '#475569'));
        iconBg.setAttribute('stroke-width', '1');
        iconG.appendChild(iconBg);

        const iconPath = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        iconPath.setAttribute('d', 'M3.5 6.5h3v-3M3.5 3.5l3 3M12.5 9.5h-3v3M12.5 12.5l-3-3');
        iconPath.setAttribute('fill', 'none');
        iconPath.setAttribute('stroke', String(isLight ? '#0284c7' : '#38bdf8'));
        iconPath.setAttribute('stroke-width', '1.5');
        iconPath.setAttribute('stroke-linecap', 'round');
        iconPath.setAttribute('stroke-linejoin', 'round');
        iconG.appendChild(iconPath);

        headerBtn.appendChild(iconG);

        const hitRect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        hitRect.setAttribute('x', String(left + 8));
        hitRect.setAttribute('y', String(bandTop - 24));
        hitRect.setAttribute('width', String(textWidth + 30));
        hitRect.setAttribute('height', String(22));
        hitRect.setAttribute('fill', 'transparent');
        hitRect.setAttribute('class', 'module-header-hit');
        headerBtn.insertBefore(hitRect, label);

        box.appendChild(headerBtn);
      } else {
        const label = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        label.setAttribute('x', String(left + 14));
        label.setAttribute('y', String(bandTop - 8));
        label.setAttribute('fill', String(isLight ? '#315575' : '#a4c7e7'));
        label.setAttribute('font-size', '12');
        label.textContent = escapeHTML(`App · ${members.length} nodes`);
        box.appendChild(label);
      }
      svg.appendChild(box);
    }
  }

  const events = reactlogData.events || reactlogData.log || [];
  const activeEvent = events[currentStep] || {};
  const activeNodeId = activeEvent.node_id || activeEvent.id;

  const curWave = allBursts.slice().reverse().find((w: any) => currentStep >= w.startStep) || allBursts[0];
  const executedInBurst: Set<any> = new Set();
  if (curWave) {
    curWave.inputs.forEach((i: any) => executedInBurst.add(i.nodeId));
    curWave.calcs.forEach((c: any) => executedInBurst.add(c.nodeId));
    curWave.outputs.forEach((o: any) => executedInBurst.add(o.nodeId));
  }

  const motionPaths: Map<any, any> = new Map();
  edges.forEach((e: any) => {
    const p1 = pos[e.from];
    const p2 = pos[e.to];
    if (p1 && p2) {
      const fromMatch = representatives.get(activeEvent.edge_from || activeEvent.dependsOn);
      const toMatch = representatives.get(activeEvent.edge_to || activeEvent.node_id || activeEvent.id);
      const isEdgeActive = !e.inactive && ((fromMatch && toMatch)
        ? (fromMatch === e.from && toMatch === e.to)
        : (activeEvent.node_id === e.to && (activeEvent.event === 'dependsOn' || activeEvent.event === 'propagate' || activeEvent.action === 'dependsOn' || activeEvent.action === 'invalidate')));

      const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      const d = graphEdgePath(e, pos, nodeWidth, nodeHeight, edges);
      path.setAttribute('d', String(d));
      if (e.related && !e.isolated) motionPaths.set(JSON.stringify([e.from, e.to]), d);
      path.setAttribute('fill', 'none');
      path.setAttribute('stroke-linecap', 'butt');
      path.setAttribute('stroke-linejoin', 'round');
      path.setAttribute('data-from', String(e.from));
      path.setAttribute('data-to', String(e.to));
      path.setAttribute('data-active', String(isEdgeActive ? 'true' : 'false'));
      path.setAttribute('class', 'graph-edge' + (e.isolated ? ' is-isolated' : '') + (e.inactive ? ' is-inactive' : '') + (!e.related ? ' is-dimmed' : ''));
      const edgeTitle = document.createElementNS('http://www.w3.org/2000/svg', 'title');
      const fromLabel = nodeDisplayName(e.from);
      const toLabel = nodeDisplayName(e.to);
      if (e.isolated) {
        path.setAttribute('stroke-dasharray', '5 4');
        path.setAttribute('data-isolated', 'true');
        edgeTitle.textContent = `Isolated read (reactive.isolate) from ${fromLabel} to ${toLabel}`;
      } else {
        edgeTitle.textContent = `${fromLabel} → ${toLabel}`;
      }
      path.appendChild(edgeTitle);
      path.setAttribute('marker-end', String(isEdgeActive ? 'url(#arrow-active)' : (e.isolated ? 'url(#arrow-isolated)' : 'url(#arrow)')));

      svg.appendChild(path);
    }
  });
  updateEdgePulses(motionPaths, representatives, events, previousStep);

  const execCounts = getNodeExecutionCounts();
  nodes.forEach((n: any) => {
    const p = pos[n.id] || { x: 200, y: 200 };
    const isActive = activeNodeId === n.id || (n.members || []).includes(activeNodeId);
    const isSelected = selectedNodeId === n.id || (n.members || []).includes(selectedNodeId);
    const isExecuted = (n.members || []).some((id: any) => executedInBurst.has(id)) || executedInBurst.has(n.id) || (n.id.startsWith('input:') && executedInBurst.has(n.id.replace('input:', '')));
    const kind = nodeKind(n);
    const isDimmed = focusedNodes && !(n.members || [n.id]).some((id: any) => focusedNodes.has(id));
    const isClientData = isClientDataNode(n);

    const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    g.setAttribute('class', 'graph-node' + (isSelected ? ' is-selected' : '') + (isActive ? ' is-active' : '') + (isExecuted ? ' is-executed' : '') + (isDimmed ? ' is-dimmed' : '') + (isClientData ? ' is-clientdata' : ''));
    g.setAttribute('data-id', String(n.id));
    g.setAttribute('data-role', String(n.role));
    const state = replay.states.get(n.id) || 'ready';
    g.setAttribute('data-state', String(state));
    g.setAttribute('aria-pressed', String(isSelected));
    g.style.setProperty('--node-selection-stroke', isLight ? '#0f172a' : '#ffffff');
    g.setAttribute('data-active', String(isActive ? 'true' : 'false'));
    g.setAttribute('tabindex', '0');
    g.setAttribute('role', 'button');
    g.setAttribute('aria-label', `${kind.label} ${nodeDisplayName(n)}, ${state}, line ${n.line || 'unknown'}`);

    g.onclick = (e: any) => {
      e.stopPropagation();
      if (n.type === 'module') {
        toggleModule(n.module);
        return;
      }
      if (e.detail >= 2) {
        filterLineageForNode(n.id);
        return;
      }
      selectNode(n.id);
    };
    g.ondblclick = (e: any) => {
      e.stopPropagation();
      if (n.type === 'module') {
        toggleModule(n.module);
        return;
      }
      filterLineageForNode(n.id);
    };
    g.onkeydown = (e: any) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault(); e.stopPropagation(); selectNode(n.id);
        document.querySelectorAll('.graph-node').forEach((el: any) => { if (el.dataset.id === n.id) el.focus(); });
      }
    };
    if (n.type === 'module') {
      g.setAttribute('aria-expanded', 'false');
      g.setAttribute('aria-label', `Expand module ${n.module}`);
      g.onkeydown = (e: any) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); e.stopPropagation(); toggleModule(n.module); } };
    }
    g.onmouseenter = () => highlightDependencies(n.id);
    g.onmouseleave = () => resetHighlight();

    const role = n.role || n.type;
    const cardPath = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    cardPath.setAttribute('d', String(getNodeShapePath(n, p, nodeWidth, nodeHeight)));

    const fillCol = reactiveStateColors[state];
    const defaultStroke = state === 'frozen'
      ? (isLight ? '#073859' : '#7dd3fc')
      : (isLight ? '#475569' : '#1e293b');
    const strokeCol = isSelected ? (isLight ? '#0f172a' : '#ffffff') : defaultStroke;
    const strokeW = isSelected ? '3' : '1.5';
    const filterVal = isSelected ? (isLight ? 'drop-shadow(0 0 8px rgba(2,132,199,0.35))' : 'drop-shadow(0 0 10px rgba(99,179,255,0.4))') : 'url(#card-shadow)';

    cardPath.setAttribute('fill', String(fillCol));
    cardPath.setAttribute('stroke', String(strokeCol));
    cardPath.setAttribute('stroke-width', String(strokeW));
    cardPath.setAttribute('stroke-linejoin', 'round');
    cardPath.setAttribute('stroke-linecap', 'round');
    cardPath.setAttribute('filter', String(filterVal));
    cardPath.setAttribute('class', 'node-card');
    g.appendChild(cardPath);

    const focusRing = cardPath.cloneNode(false) as any;
    focusRing.setAttribute('class', 'node-focus-ring');
    focusRing.setAttribute('fill', 'none');
    focusRing.removeAttribute('filter');
    focusRing.setAttribute('aria-hidden', 'true');
    g.appendChild(focusRing);

    const textX = p.x - (nodeWidth / 2) + ((role === 'source' || n.type === 'input' || n.type === 'module') ? 22 : 36);

    const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    text.setAttribute('x', String(textX));
    text.setAttribute('y', String(p.y - 4));
    text.setAttribute('fill', String(state === 'frozen' ? '#ffffff' : '#0f172a'));
    text.setAttribute('font-family', 'var(--mono)');
    text.setAttribute('font-size', '14px');
    text.setAttribute('font-weight', '700');
    text.innerHTML = graphNodeLabel(n);
    const title = document.createElementNS('http://www.w3.org/2000/svg', 'title');
    title.textContent = `${nodeDisplayName(n)} · ${state}${n.line ? ' · line ' + n.line : ''}`;
    g.appendChild(title);
    g.appendChild(text);

    const subText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    subText.setAttribute('x', String(textX));
    subText.setAttribute('y', String(p.y + 14));
    subText.setAttribute('fill', String(state === 'frozen' ? '#e2e8f0' : '#1e293b'));
    subText.setAttribute('font-size', '12px');
    subText.textContent = n.type === 'module' ? `${n.members.length} nodes · click to expand` : `${kind.label} · ${state}`;
    g.appendChild(subText);

    const execCount = execCounts.get(n.id) || 0;
    if (execCount > 1) {
      const badgeG = document.createElementNS('http://www.w3.org/2000/svg', 'g');
      badgeG.setAttribute('class', 'node-exec-badge');
      const badgeWidth = 34;
      const badgeHeight = 18;
      const hasRightChevron = (role === 'source' || n.type === 'input' || role === 'conductor' || n.type === 'calc');
      const badgeX = p.x + (nodeWidth / 2) - badgeWidth - (hasRightChevron ? 28 : 10);
      const badgeY = p.y - (nodeHeight / 2) - 9;

      const badgeRect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
      badgeRect.setAttribute('x', String(badgeX));
      badgeRect.setAttribute('y', String(badgeY));
      badgeRect.setAttribute('width', String(badgeWidth));
      badgeRect.setAttribute('height', String(badgeHeight));
      badgeRect.setAttribute('rx', '9');
      badgeRect.setAttribute('fill', String(isLight ? '#f1f5f9' : '#1e293b'));
      badgeRect.setAttribute('stroke', String(isLight ? '#cbd5e1' : '#475569'));
      badgeRect.setAttribute('stroke-width', '1.2');
      badgeRect.setAttribute('filter', 'drop-shadow(0 2px 4px rgba(0,0,0,0.18))');
      badgeG.appendChild(badgeRect);

      const badgeText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      badgeText.setAttribute('x', String(badgeX + (badgeWidth / 2)));
      badgeText.setAttribute('y', String(badgeY + 12));
      badgeText.setAttribute('text-anchor', 'middle');
      badgeText.setAttribute('fill', String(isLight ? '#475569' : '#94a3b8'));
      badgeText.setAttribute('font-size', '10px');
      badgeText.setAttribute('font-weight', '700');
      badgeText.textContent = `${execCount}×`;
      badgeG.appendChild(badgeText);

      const badgeTitle = document.createElementNS('http://www.w3.org/2000/svg', 'title');
      badgeTitle.textContent = `Executed ${execCount} times during session`;
      badgeG.appendChild(badgeTitle);

      g.appendChild(badgeG);
    }

    svg.appendChild(g);
  });
}

function updateEdgePulses(paths: any, representatives: any, events: any, previousStep: any) {
  const layer = (document.getElementById('graph-edge-pulses') as any);
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    layer.replaceChildren();
    return;
  }
  const moving: Set<any> = new Set();
  for (const dot of (Array.from(layer.children) as any[])) {
    const key = dot.dataset.edge;
    if (paths.get(key) === dot.firstElementChild.getAttribute('path')) moving.add(key);
    else dot.remove();
  }

  // A scrub can skip dependency events. Use the closest visible one to where it landed.
  const forward = currentStep > previousStep;
  const direction = forward ? -1 : 1;
  for (let step = currentStep; forward ? step > previousStep : step < previousStep; step += direction) {
    const ev = events[step];
    if (!ev || ev.isolate || !['dependsOn', 'invalidate', 'invalidateStart', 'propagate'].includes(ev.action || ev.event)) continue;
    const from = representatives.get(ev.edge_from || ev.depOnReactId || ev.dependsOn);
    const to = representatives.get(ev.edge_to || ev.node_id || ev.reactId || ev.id);
    const key = JSON.stringify([from, to]);
    const path = paths.get(key);
    if (!path) continue;
    if (moving.has(key)) return;

    const dot = document.createElementNS(layer.namespaceURI, 'circle');
    dot.setAttribute('class', 'graph-edge-pulse');
    dot.setAttribute('r', '6');
    dot.dataset.edge = key;
    const motion = document.createElementNS(layer.namespaceURI, 'animateMotion') as any;
    motion.setAttribute('path', String(path));
    motion.setAttribute('dur', '1.1s');
    motion.setAttribute('begin', 'indefinite');
    motion.addEventListener('endEvent', () => dot.remove(), { once: true });
    dot.appendChild(motion);
    layer.appendChild(dot);
    motion.beginElement();
    return;
  }
}

function highlightDependencies(nodeId: any) {
  if (focusedNodeId) return;
  document.querySelectorAll('.graph-edge').forEach((edge: any) => {
    const from = edge.getAttribute('data-from');
    const to = edge.getAttribute('data-to');
    if (from === nodeId || to === nodeId) {
      edge.style.opacity = '1';
      edge.style.stroke = 'var(--accent)';
      edge.style.strokeWidth = '2.5px';
    } else {
      edge.style.opacity = '0.15';
    }
  });
}

function resetHighlight() {
  if (focusedNodeId) return;
  document.querySelectorAll('.graph-edge').forEach((edge: any) => {
    edge.style.removeProperty('opacity');
    edge.style.removeProperty('stroke');
    edge.style.removeProperty('stroke-width');
  });
}

function seekTo(step: any, fromVideo = false, mediaTime: any = null) {
  const events = reactlogData.events || reactlogData.log || [];
  const previousStep = currentStep;
  currentStep = Math.max(0, Math.min(step, events.length - 1));
  (document.getElementById('scrubber-range') as any).value = currentStep;
  (document.getElementById('step-display') as any).textContent = `Step ${currentStep} / ${Math.max(0, events.length - 1)}`;

  document.querySelectorAll('.event-item').forEach((item: any) => {
    const stepNum = Number(item.getAttribute('data-step'));
    const isCur = stepNum === currentStep;
    item.classList.toggle('is-current', isCur);
    if (isCur) {
      const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      item.scrollIntoView({ block: 'nearest', behavior: reduceMotion ? 'auto' : 'smooth' });
    }
  });

  const ev = events[currentStep];
  if (!focusedNodeId && ev && (ev.node_id || ev.id)) {
    const evNodeId = ev.node_id || ev.id;
    const lineageSet = getActiveLineageSet();
    if (!lineageSet || lineageSet.has(evNodeId)) {
      selectedNodeId = evNodeId;
    }
  }
  renderInspector();
  renderGraph(previousStep);
  updateSourceHighlight();
  updateActionToast();
  updateFlushUI();

  const evTime = ev && (ev.time_sec !== undefined ? ev.time_sec : ev.time);
  const curSec = fromVideo && mediaTime !== null
    ? mediaTime
    : (evTime !== undefined ? evTime : 0);
  updateTraceTimelineScrubber(curSec);

  if (!fromVideo) {
    const video = (document.getElementById('session-video') as any);
    if (video && evTime !== undefined && !isNaN(evTime)) {
      try {
        graphSeekTime = Math.max(0, evTime);
        video.currentTime = graphSeekTime;
      } catch { /* ignore storage errors */ }
    }
  }
}

function updateActionToast() {
  const events = reactlogData.events || reactlogData.log || [];
  const ev = events[currentStep];
  const toast = (document.getElementById('live-action-toast') as any);
  if (!toast) return;

  const act = ev ? (ev.action || ev.event || '') : '';
  if (ev && (ev.phase === 'interaction' || !['define', 'analysisInit', 'createContext', 'sessionInit'].includes(act)) && (act === 'inputChange' || act === 'userClick' || act === 'userAction' || act === 'outputUpdated' || act === 'valueChange')) {
    const evTime = ev.time_sec !== undefined ? ev.time_sec : ev.time;
    const timeStr = evTime !== undefined ? `[${formatTime(evTime)}] ` : '';
    toast.innerHTML = `${ICONS.video} ${escapeHTML(timeStr)}${escapeHTML(formatEventDetails(ev) || act)}`;
    toast.hidden = false;
  } else {
    toast.hidden = true;
  }
}

function setupVideoSync() {
  const video = (document.getElementById('session-video') as any);
  if (!video) return;

  const btn = (document.getElementById('btn-play') as any);
  const syncStatus = (document.getElementById('video-sync-status') as any);

  const updatePlayButton = (playing: any) => {
    if (!btn) return;
    btn.textContent = playing ? '❚❚ Pause' : '▶ Play';
    btn.setAttribute('aria-label', String(playing ? 'Pause recording' : 'Play recording'));
    btn.title = playing ? 'Pause recording' : 'Play recording';
  };

  const updateSyncStatus = (message: any) => {
    if (syncStatus) syncStatus.textContent = `● ${message}`;
  };

  const syncGraphToTime = (curSec: any) => {
    // Paused graph stepping must keep the exact event when timestamps coincide.
    if (video.paused && graphSeekTime !== null && Math.abs(curSec - graphSeekTime) < 0.05) return;
    graphSeekTime = null;
    updateTraceTimelineScrubber(curSec);
    let matchIdx = 0;
    const events = reactlogData.events || reactlogData.log || [];
    for (let i = 0; i < events.length; i++) {
      const ev = events[i]!;
      const t = ev.effective_time !== undefined ? ev.effective_time : ((ev.time_sec !== undefined ? ev.time_sec : ev.time) || 0);
      if (t <= curSec) matchIdx = i;
    }
    if (matchIdx !== currentStep) {
      seekTo(matchIdx, true, curSec);
    }
  };

  const stopFrameSync = () => {
    if (videoFrameRequest === null) return;
    if (videoFrameRequestKind === 'video' && typeof video.cancelVideoFrameCallback === 'function') {
      video.cancelVideoFrameCallback(videoFrameRequest);
    } else if (videoFrameRequestKind === 'animation') {
      cancelAnimationFrame(videoFrameRequest);
    }
    videoFrameRequest = null;
    videoFrameRequestKind = null;
  };

  const syncVideoFrame = (_now: any, metadata: any) => {
    videoFrameRequest = null;
    videoFrameRequestKind = null;
    if (video.paused || video.ended) return;
    const mediaTime = metadata && Number.isFinite(metadata.mediaTime)
      ? metadata.mediaTime
      : video.currentTime;
    syncGraphToTime(mediaTime);
    requestNextFrame();
  };

  const requestNextFrame = () => {
    if (videoFrameRequest !== null || video.paused || video.ended) return;
    if (typeof video.requestVideoFrameCallback === 'function') {
      videoFrameRequestKind = 'video';
      videoFrameRequest = video.requestVideoFrameCallback(syncVideoFrame);
    } else {
      videoFrameRequestKind = 'animation';
      videoFrameRequest = requestAnimationFrame((now: any) => syncVideoFrame(now, null));
    }
  };

  video.addEventListener('loadedmetadata', () => {
    updateSyncStatus(`Paused at ${formatTime(video.currentTime)}`);
    if (video.duration && !isNaN(video.duration)) {
      maxSessionDuration = Math.max(maxSessionDuration, video.duration);
      const totalDisplay = (document.getElementById('trace-total-time') as any);
      if (totalDisplay) totalDisplay.textContent = formatTime(maxSessionDuration);
      initTraceTimeline();
    }
  });

  video.addEventListener('play', () => {
    if (playTimer) {
      clearInterval(playTimer);
      playTimer = null;
    }
    realtimePlayLastTick = null;
    graphSeekTime = null;
    isPlaying = true;
    updatePlayButton(true);
    updateSyncStatus('Following recording');
    requestNextFrame();
  });

  video.addEventListener('pause', () => {
    isPlaying = false;
    stopFrameSync();
    updatePlayButton(false);
    updateSyncStatus(`Paused at ${formatTime(video.currentTime)}`);
  });

  video.addEventListener('ended', () => {
    isPlaying = false;
    stopFrameSync();
    updatePlayButton(false);
    updateSyncStatus('Recording complete');
  });

  video.addEventListener('timeupdate', () => syncGraphToTime(video.currentTime));
  video.addEventListener('seeked', () => syncGraphToTime(video.currentTime));
}

function updateSourceHighlight() {
  const events = reactlogData.events || reactlogData.log || [];
  const ev = events[currentStep];
  const isMark = ['mark', 'userMark'].includes(ev?.action || ev?.event || '');
  const isError = isErrorEvent(ev);
  const eventNode = nodeIndex.get(ev?.node_id || ev?.reactId || ev?.id);
  const selected = nodeIndex.get(selectedNodeId);
  const target = ev?.line ? ev : (isError ? eventNode : (selected?.line ? selected : eventNode));
  const panel = (document.getElementById('source-panel') as any);
  panel.querySelector('.source-line.is-active')?.classList.remove('is-active', 'is-mark', 'is-error');
  if (!Number.isInteger(target?.line)) return;
  if (target.source_file && target.source_file !== displayedSourceFile) {
    showSourceFile(target.source_file);
    if (target.source_file !== displayedSourceFile) return;
  }
  const line = panel.querySelector(`.source-line[data-line="${target.line}"]`);
  if (!line) return;
  line.classList.add('is-active');
  if (isMark && target === ev) line.classList.add('is-mark');
  if (isError) line.classList.add('is-error');
  if (!panel.hidden) {
    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    line.scrollIntoView({ block: 'center', behavior: reduceMotion ? 'auto' : 'smooth' });
  }
}

function togglePlay() {
  const video = (document.getElementById('session-video') as any);
  if (video && playbackSpeed === 'realtime') {
    if (playTimer) {
      clearInterval(playTimer);
      playTimer = null;
    }
    realtimePlayLastTick = null;
    if (video.paused) {
      const atVideoEnd = video.ended || (
        Number.isFinite(video.duration)
        && video.duration > 0
        && video.currentTime >= video.duration - 0.05
      );
      if (atVideoEnd) {
        video.currentTime = 0;
        seekTo(0, true);
      }
      video.play().catch(() => undefined);
    } else {
      video.pause();
    }
    return;
  }

  if (video && !video.paused) {
    video.pause();
  }

  const events = reactlogData.events || reactlogData.log || [];
  isPlaying = !isPlaying;
  const btn = (document.getElementById('btn-play') as any);
  if (btn) {
    btn.textContent = isPlaying ? '❚❚ Pause' : '▶ Play';
    btn.setAttribute('aria-label', String(isPlaying ? 'Pause timeline' : 'Play timeline'));
  }

  if (playTimer) {
    clearInterval(playTimer);
    playTimer = null;
  }
  realtimePlayLastTick = null;

  if (isPlaying) {
    if (playbackSpeed === 'realtime') {
      if (currentTimelineTime >= maxSessionDuration - 0.01 || currentStep >= events.length - 1) {
        currentTimelineTime = 0;
        seekTo(0, true, 0);
      }
      realtimePlayLastTick = performance.now();
      playTimer = setInterval(() => {
        const now = performance.now();
        const dt = Math.max(0, (now - (realtimePlayLastTick || now)) / 1000);
        realtimePlayLastTick = now;
        const nextSec = Math.min(maxSessionDuration, currentTimelineTime + dt);
        let matchIdx = 0;
        for (let i = 0; i < events.length; i++) {
          const ev = events[i]!;
          const t = ev.effective_time !== undefined ? ev.effective_time : ((ev.time_sec !== undefined ? ev.time_sec : ev.time) || 0);
          if (t <= nextSec) matchIdx = i;
        }
        if (matchIdx !== currentStep) {
          seekTo(matchIdx, true, nextSec);
        } else {
          updateTraceTimelineScrubber(nextSec);
        }
        if (nextSec >= maxSessionDuration) {
          togglePlay();
        }
      }, 50);
    } else {
      if (currentStep >= events.length - 1) currentStep = 0;
      playTimer = setInterval(() => {
        if (currentStep < events.length - 1) {
          seekTo(currentStep + 1);
        } else {
          togglePlay();
        }
      }, 600);
    }
  }
}

function stepForward() { seekTo(currentStep + 1); }
function stepBack() { seekTo(currentStep - 1); }
function resetTimeline() { seekTo(0); }

function nodeSearchScore(node: any, query: any) {
  const moduleOnly = query.startsWith('module:');
  if (moduleOnly) {
    const needle = query.slice(7).trim().toLowerCase();
    const module = String(node.module || '__root__').toLowerCase();
    return !needle || module.includes(needle) ? 0 : Infinity;
  }
  const idOnly = query.startsWith('id:');
  const needle = (idOnly ? query.slice(3) : query).trim().toLowerCase();
  if (!needle) return 0;
  if (idOnly) {
    const nid = String(node.id || '').toLowerCase();
    const nlabel = String(node.label || '').toLowerCase();
    const nname = String(node.name || '').toLowerCase();
    if (nid === needle || nid.endsWith(':' + needle) || nlabel === needle || nname === needle) return 0;
    if (nid.includes(needle) || nlabel.includes(needle) || nname.includes(needle)) return 1;
    return Infinity;
  }
  const fields = [node.id, node.label, node.name, node.type, node.role, node.module];
  let best = Infinity;
  fields.forEach((field: any) => {
    const value = String(field || '').toLowerCase();
    if (value === needle) best = Math.min(best, 0);
    else if (value.includes(needle)) best = Math.min(best, 1 + value.indexOf(needle) / Math.max(1, value.length));
    else {
      let pos = 0;
      for (const char of value) if (char === needle[pos]) pos++;
      if (pos === needle.length) best = Math.min(best, 3 + value.length / 1000);
    }
  });
  return best;
}

function closeSearchChoices() {
  (document.getElementById('search-results') as any).hidden = true;
  (document.getElementById('search-input') as any).setAttribute('aria-expanded', 'false');
  (document.querySelector('.search-toggle') as any).setAttribute('aria-expanded', 'false');
}

function toggleSearchChoices() {
  if (!(document.getElementById('search-results') as any).hidden) closeSearchChoices();
  else { handleSearch((document.getElementById('search-input') as any).value, false); (document.getElementById('search-input') as any).focus(); }
}

function clearSearchFilter() {
  selectedSearchNodeId = null;
  focusedNodeId = null;
  selectedNodeId = null;
  searchQuery = '';
  (document.getElementById('search-input') as any).value = '';
  syncSearchClearButton();
  closeSearchChoices();
  refreshExploration();
  renderInspector();
  updateSourceHighlight();
  updateTraceTimelineScrubber(getCurrentStepTime());
  fitGraph();
}

function handleSearch(q: any, isTyping = true) {
  const rawQuery = (q || '').trim().toLowerCase();
  if (isTyping) {
    searchQuery = rawQuery;
    if (!rawQuery) {
      selectedSearchNodeId = null;
      focusedNodeId = null;
      selectedNodeId = null;
    } else if (selectedSearchNodeId) {
      const selNode = nodeIndex.get(selectedSearchNodeId);
      if (!selNode || rawQuery !== nodeDisplayName(selNode).toLowerCase()) {
        selectedSearchNodeId = null;
        focusedNodeId = null;
        selectedNodeId = null;
      }
    }
  } else {
    searchQuery = rawQuery;
  }
  syncSearchClearButton();
  const dropdownQuery = (!isTyping && selectedSearchNodeId) ? '' : searchQuery;
  const results = (document.getElementById('search-results') as any);
  results.replaceChildren();
  results.hidden = false;
  (document.getElementById('search-input') as any).setAttribute('aria-expanded', 'true');
  (document.querySelector('.search-toggle') as any).setAttribute('aria-expanded', 'true');
  {
    const matches = filterItems(
      filterItems(reactlogData.nodes || [], (n: any) => dropdownQuery || n.id === selectedSearchNodeId || ((!hideClientData || !isClientDataNode(n)) && (!changedNodesOnly || !changedNodeIds || changedNodeIds.has(n.id)))).map((n: any) => ({ node: n, score: dropdownQuery ? nodeSearchScore(n, dropdownQuery) : (n.id === selectedSearchNodeId ? -1 : 0) })),
      (m: any) => Number.isFinite(m.score)
    ).sort((a: any, b: any) => a.score - b.score);
    const summary = document.createElement('div');
    summary.className = 'search-summary';
    summary.setAttribute('role', 'status');
    summary.textContent = matches.length
      ? `${matches.length} matches${matches.length > 50 ? ' · showing first 50' : ''}${selectedSearchNodeId ? ' · click checked item to clear' : ' · ↓ to select'}`
      : '0 matches. Try a node name or module:name. Press Escape to clear.';
    results.appendChild(summary);
    matches.slice(0, 50).forEach(({node}: any) => {
      const isSelected = selectedSearchNodeId === node.id;
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'search-option' + (isSelected ? ' is-selected' : '');
      button.setAttribute('role', 'option');
      button.setAttribute('aria-selected', String(isSelected));
      const kind = nodeKind(node);
      const checkSvg = '<span class="search-check" aria-hidden="true"><svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.75" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg></span>';
      button.innerHTML = '<span class="search-item-main">' + checkSvg + '<span><b>' + nodeLabelHTML(node) + '</b></span></span><span style="color:var(--text-muted);font-size:0.68rem;flex-shrink:0;">' + escapeHTML(kind.label) + '</span>';
      button.onclick = () => {
        if (isSelected) {
          clearSearchFilter();
          return;
        }
        filterLineageForNode(node.id);
      };
      results.appendChild(button);
    });
  }
  refreshExploration();
  fitGraph();
}

function resetGraphView() {
  toggleSettingsMenu(false);
  selectedNodeId = null;
  focusedNodeId = null;
  selectedSearchNodeId = null;
  searchQuery = '';
  selectedStageFilter = null;
  hideClientData = false;
  changedNodesOnly = false;
  (document.getElementById('search-input') as any).value = '';
  closeSearchChoices();
  activeRoles = new Set(['source', 'conductor', 'observer', 'effect', 'output']);
  if (currentViewMode === 'flush') setViewMode('full');
  setPlaybackSpeed('step');
  refreshExploration();
  renderInspector();
  updateTraceTimelineScrubber(getCurrentStepTime());
  fitGraph();
}

function handleSearchKey(event: any) {
  const input = (document.getElementById('search-input') as any);
  const results = (document.getElementById('search-results') as any);
  const buttons: any[] = Array.from(results!.querySelectorAll('button'));
  if (event.key === 'Escape') {
    event.preventDefault();
    input.value = '';
    handleSearch('');
    input.focus();
    closeSearchChoices();
  } else if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
    if (results.hidden || !buttons.length) return;
    event.preventDefault();
    const index = buttons.indexOf(document.activeElement as any);
    const next = event.key === 'ArrowDown' ? (index + 1) % buttons.length : (index <= 0 ? buttons.length - 1 : index - 1);
    buttons[next].focus();
  } else if (event.key === 'Enter' && event.target === input && !results.hidden && buttons.length) {
    event.preventDefault();
    buttons[0].click();
  }
}

function setupPanZoom() {
  const svg = (document.getElementById('reactlog-svg') as any);
  if (!svg) return;
  if (svg.dataset.panZoomBound) return;
  svg.dataset.panZoomBound = 'true';
  svg.addEventListener('mousedown', (e: any) => {
    if (e.target.closest('.graph-node, .module-box')) return;
    isPanning = true;
    startPan = { x: e.clientX - panOffset.x, y: e.clientY - panOffset.y };
  });
  window.addEventListener('mousemove', (e: any) => {
    if (!isPanning) return;
    panOffset = { x: e.clientX - startPan.x, y: e.clientY - startPan.y };
    applyZoom();
  });
  window.addEventListener('mouseup', () => isPanning = false);
  svg.addEventListener('wheel', (e: any) => {
    e.preventDefault();
    const delta = e.deltaY > 0 ? 0.9 : 1.1;
    const rect = svg.getBoundingClientRect();
    zoomAt(delta, e.clientX - rect.left, e.clientY - rect.top);
  });
}

function applyZoom() {
  const g = (document.getElementById('viewport-g') as any);
  if (g) g.setAttribute('transform', `translate(${panOffset.x}, ${panOffset.y}) scale(${zoomLevel})`);
}

function zoomAt(factor: any, x?: any, y?: any) {
  const svg = (document.getElementById('reactlog-svg') as any);
  x = x ?? svg.clientWidth / 2;
  y = y ?? svg.clientHeight / 2;
  const next = Math.max(Math.min(0.001, zoomLevel), Math.min(2.5, zoomLevel * factor));
  const ratio = next / zoomLevel;
  panOffset = { x: x - (x - panOffset.x) * ratio, y: y - (y - panOffset.y) * ratio };
  zoomLevel = next;
  applyZoom();
}
function zoomIn() { zoomAt(1.2); }
function zoomOut() { zoomAt(0.8); }
function resetZoom() { zoomLevel = 1; panOffset = { x: 0, y: 0 }; applyZoom(); }
function fitGraph() {
  const svg = (document.getElementById('reactlog-svg') as any);
  const g = (document.getElementById('graph-content') as any);
  if (!svg || !g || !g.childElementCount) return;
  const box = g.getBBox();
  const width = svg.clientWidth, height = svg.clientHeight;
  if (!width || !height || !box.width || !box.height) return;
  zoomLevel = Math.min(1, Math.max(1, width - 48) / box.width, Math.max(1, height - 96) / box.height);
  panOffset = { x: (width - box.width * zoomLevel) / 2 - box.x * zoomLevel,
                 y: (height - box.height * zoomLevel) / 2 - box.y * zoomLevel };
  applyZoom();
}
function isFullscreen() {
  return !!(document.fullscreenElement || (document as any).webkitFullscreenElement || (document as any).mozFullScreenElement || (document as any).msFullscreenElement);
}
function updateFullscreenButton() {
  const btn = (document.getElementById('btn-fullscreen') as any);
  if (!btn) return;
  const fs = isFullscreen();
  btn.setAttribute('aria-label', String(fs ? 'Exit full screen' : 'Full screen'));
  btn.title = fs ? 'Exit full screen' : 'Full screen';
  btn.innerHTML = fs
    ? '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 3v3a2 2 0 0 1-2 2H3"/><path d="M21 8h-3a2 2 0 0 1-2-2V3"/><path d="M3 16h3a2 2 0 0 1 2 2v3"/><path d="M16 21v-3a2 2 0 0 1 2-2h3"/></svg>'
    : '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 3H5a2 2 0 0 0-2 2v3"/><path d="M21 8V5a2 2 0 0 0-2-2h-3"/><path d="M3 16v3a2 2 0 0 0 2 2h3"/><path d="M16 21h3a2 2 0 0 0 2-2v-3"/></svg>';
}
function toggleFullscreen() {
  if (!isFullscreen()) {
    const root = document.documentElement;
    if (root.requestFullscreen) {
      root.requestFullscreen().catch(() => undefined);
    } else if ((root as any).webkitRequestFullscreen) {
      (root as any).webkitRequestFullscreen();
    } else if ((root as any).msRequestFullscreen) {
      (root as any).msRequestFullscreen();
    }
  } else {
    if (document.exitFullscreen) {
      document.exitFullscreen().catch(() => undefined);
    } else if ((document as any).webkitExitFullscreen) {
      (document as any).webkitExitFullscreen();
    } else if ((document as any).msExitFullscreen) {
      (document as any).msExitFullscreen();
    }
  }
}
document.addEventListener('fullscreenchange', () => {
  updateFullscreenButton();
  setTimeout(fitGraph, 100);
});
document.addEventListener('webkitfullscreenchange', () => {
  updateFullscreenButton();
  setTimeout(fitGraph, 100);
});

const R_SENTINEL_IDS = new Set(['rNoCtxReactId', 'rNoCtx', 'rDummyReactId']);

function normalizeReactlogData(loadedData: any): ReactlogData {
  if (!loadedData || typeof loadedData !== 'object') {
    return loadedData;
  }
  if (!Array.isArray(loadedData) && Array.isArray(loadedData.nodes) && Array.isArray(loadedData.events)) {
    const hasSentinel = loadedData.nodes.some((n: any) => n && R_SENTINEL_IDS.has(String(n.reactId || n.id || '')));
    if (!hasSentinel) {
      return loadedData;
    }
    return {
      ...loadedData,
      nodes: loadedData.nodes.filter((n: any) => n && !R_SENTINEL_IDS.has(String(n.reactId || n.id || ''))),
      edges: Array.isArray(loadedData.edges)
        ? loadedData.edges.filter((e: any) => e && !R_SENTINEL_IDS.has(String(e.from || '')) && !R_SENTINEL_IDS.has(String(e.to || '')))
        : []
    };
  }

  const rawEvents: any[] = Array.isArray(loadedData) ? loadedData : (loadedData.log || loadedData.events || loadedData.entries || []);
  const nodesMap: Record<string, any> = Object.create(null);
  const edgesMap: Map<string, any> = new Map();
  const normEvents: any[] = [];
  let sIdx = 0;

  let minEpochTime = Infinity;
  let isEpoch = false;
  rawEvents.forEach((item: any) => {
    const t = Number(item.time || item.time_sec || (Number(item.timestamp || 0) / 1000.0) || 0);
    if (t > 100000) isEpoch = true;
    if (t > 0 && t < minEpochTime) minEpochTime = t;
  });
  const baseEpoch = isEpoch && isFinite(minEpochTime) ? minEpochTime : 0;

  rawEvents.forEach((item: any) => {
    const act = item.action || item.event || '';
    const nid = item.reactId || item.node_id || item.id;
    if (!nid || R_SENTINEL_IDS.has(String(nid))) return;
    const rawLbl = item.label || item.node_label;
    const existing = nodesMap[nid];
    if (!existing || act === 'define' || (rawLbl && rawLbl !== nid && (!existing.label || existing.label === nid))) {
      const ntype = item.type || item.node_type || existing?.type || 'calc';
      let role = 'conductor';
      let ctype = String(ntype).toLowerCase();
      if (['observable', 'reactive'].includes(ctype)) ctype = 'calc';
      if (['input', 'reactiveval', 'reactivevalueskey', 'reactivevaluesnames', 'reactivevaluesaslist', 'reactivevaluesaslistall'].includes(ctype) || String(nid).startsWith('input:') || String(nid).startsWith('input$')) {
        role = 'source'; ctype = 'input';
      } else if (['observer', 'output', 'effect'].includes(ctype) || String(nid).startsWith('output:') || String(nid).startsWith('output$') || String(nid).startsWith('effect:')) {
        role = 'observer'; ctype = 'output';
      }
      const resolvedLbl = (rawLbl && rawLbl !== nid) ? String(rawLbl) : String(existing?.label || rawLbl || nid);
      const fallbackName = String(nid).includes(':') ? String(nid).split(':')[1] : (String(nid).includes('$') ? String(nid).split('$')[1] : (resolvedLbl !== String(nid) ? resolvedLbl : String(nid)));
      nodesMap[nid] = {
        id: nid,
        name: fallbackName,
        type: ctype,
        role: role,
        label: resolvedLbl,
        line: item.line ?? existing?.line,
        module: item.module ?? existing?.module,
        render_type: item.render_type ?? existing?.render_type,
        source_file: item.source_file ?? existing?.source_file
      };
    }
  });

  const resolveNodeLabel = (id: any, fallback: any = '') => {
    const sid = String(id || '');
    const mapped = String(nodesMap[sid]?.label || '');
    const fb = String(fallback || '');
    if (mapped && mapped !== sid) return mapped;
    if (fb && fb !== sid) return fb;
    return mapped || fb || sid;
  };

  const isolateDepthBySession: Map<string, number> = new Map();

  rawEvents.forEach((item: any) => {
    const act = item.action || item.event || '';
    const sessKey = String(item.session || 'default');
    if (act === 'isolateEnter') {
      isolateDepthBySession.set(sessKey, (isolateDepthBySession.get(sessKey) || 0) + 1);
      return;
    }
    if (act === 'isolateExit') {
      isolateDepthBySession.set(sessKey, Math.max(0, (isolateDepthBySession.get(sessKey) || 0) - 1));
      return;
    }

    const nid = item.reactId || item.node_id || item.id;
    const lbl = resolveNodeLabel(nid, item.label || item.node_label);
    const ntype = item.type || item.node_type || 'calc';
    const depFrom = item.depOnReactId || item.dependsOn || item.edge_from;
    const depTo = nid || item.reactId || item.edge_to;
    const depFromLbl = depFrom ? resolveNodeLabel(depFrom) : '';
    const depToLbl = depTo ? resolveNodeLabel(depTo, lbl) : lbl;
    const rawT = Number(item.time || item.time_sec || (Number(item.timestamp || 0) / 1000.0) || 0);
    const tSec = Math.max(0, baseEpoch > 0 ? (rawT - baseEpoch) : rawT);
    const tMs = Number(item.timestamp || (tSec * 1000));
    const prov = item.provenance || (['valueChange', 'inputChange', 'userClick', 'userAction'].includes(act) ? 'observed' : 'inferred');
    const phase = item.phase || (['define', 'analysisInit', 'createContext', 'sessionInit'].includes(act) ? 'init' : 'interaction');
    const isIsolated = Boolean(item.isolate || (isolateDepthBySession.get(sessKey) || 0) > 0);

    if (act === 'dependsOn' && depFrom && depTo && !R_SENTINEL_IDS.has(String(depFrom)) && !R_SENTINEL_IDS.has(String(depTo))) {
      const edgeKey = `${depFrom}==>${depTo}`;
      const prevEdge = edgesMap.get(edgeKey);
      if (!prevEdge) {
        edgesMap.set(edgeKey, { from: depFrom, to: depTo, ...(isIsolated ? { isolated: true } : {}) });
      } else if (!isIsolated && prevEdge.isolated) {
        edgesMap.set(edgeKey, { from: depFrom, to: depTo });
      }
    }

    let details = item.details;
    if (!details) {
      if (act === 'define') details = `Defined reactive node '${lbl}'`;
      else if (act === 'dependsOn') details = `Dependency: '${depFromLbl}' used by '${depToLbl}'`;
      else if (act === 'dependsOnRemove') details = `Removed dependency: '${depFromLbl}' used by '${depToLbl}'`;
      else if (act === 'invalidate' || act === 'invalidateEnd') details = `Invalidated '${lbl}'`;
      else if (act === 'invalidateStart') details = `Invalidating '${lbl}'`;
      else if (act === 'valueChange' || act === 'inputChange') details = `Value change for '${lbl}': ${item.value !== undefined ? String(item.value) : ''}`;
      else if (act === 'enter' || act === 'wouldEvaluate') details = `Evaluating '${lbl}'`;
      else if (act === 'exit' || act === 'ordered') details = `Completed evaluation of '${lbl}'`;
      else if (act === 'idle' || act === 'queueEmpty') details = 'Idle';
      else details = lbl ? `Event '${act}' on '${lbl}'` : `Event '${act}'`;
    }

    normEvents.push({
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
      isolate: isIsolated,
      details: details
    });
    sIdx++;
  });

  const finalNodes = Object.values(nodesMap);
  const finalEdges = Array.from(edgesMap.values());

  return {
    success: true,
    version: (!Array.isArray(loadedData) && loadedData.version) || "1.0",
    session: (!Array.isArray(loadedData) && loadedData.session) || "default",
    nodes: finalNodes,
    edges: finalEdges,
    events: normEvents,
    log: normEvents,
    summary: `Loaded Reactlog: ${finalNodes.length} nodes, ${finalEdges.length} edges, ${normEvents.length} log events`
  };
}

function loadReactlogObject(loadedData: any) {
  const normalized = normalizeReactlogData(loadedData);
  Object.assign(reactlogData, normalized);
  (document.getElementById('graph-edge-pulses') as any).replaceChildren();
  selectedNodeId = null;
  focusedNodeId = null;
  collapsedModules.clear();
  graphSeekTime = null;
  currentStep = 0;
  searchQuery = '';
  selectedStageFilter = null;
  (document.getElementById('search-input') as any).value = '';
  closeSearchChoices();
  activeRoles = new Set(['source', 'conductor', 'observer', 'effect', 'output']);
  hideClientData = true;
  changedNodesOnly = true;
  eventListScope = null;
  init();
  renderGraph();
}

function importReactlogJson() {
  (document.getElementById('json-menu') as any)?.hidePopover?.();
  (document.getElementById('reactlog-file-input') as any)?.click();
}

function exportReactlogJson() {
  (document.getElementById('json-menu') as any)?.hidePopover?.();
  const json = JSON.stringify(reactlogData, null, 2);
  const blob = new Blob([json], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const rawTitle = ((document.querySelector('.brand-title') as any)?.textContent || 'reactlog')
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '') || 'reactlog';
  const link = document.createElement('a');
  link.href = url;
  link.download = `${rawTitle}-reactlog.json`;
  document.body.appendChild(link);
  link.click();
  link.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

function handleReactlogFileUpload(e: any) {
  const file = e.target.files && e.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = (evt: any) => {
    try {
      const parsed = JSON.parse(evt.target.result);
      loadReactlogObject(parsed);
    } catch (err: any) {
      alert('Error parsing JSON file: ' + err.message);
    } finally {
      e.target.value = '';
    }
  };
  reader.readAsText(file);
}

function positionAnchoredPopover(anchor: any, popover: any) {
  if (typeof CSS !== 'undefined' && CSS.supports && CSS.supports('position-area', 'block-end')) return;
  const a = anchor.getBoundingClientRect();
  const pad = 8;
  popover.style.top = '0px';
  popover.style.left = '0px';
  const rect = popover.getBoundingClientRect();
  const vw = window.innerWidth, vh = window.innerHeight;
  const left = Math.max(pad, Math.min(vw - rect.width - pad, a.right - rect.width));
  let top = a.bottom + 6;
  if (top + rect.height + pad > vh && a.top - rect.height - 6 >= pad) {
    top = a.top - rect.height - 6;
  }
  popover.style.left = `${Math.round(left)}px`;
  popover.style.top = `${Math.round(top)}px`;
}

function setupAnchoredPopover(buttonId: any, popoverId: any) {
  const btn = (document.getElementById(buttonId) as any);
  const pop = (document.getElementById(popoverId) as any);
  if (!btn || !pop) return;
  pop.addEventListener('toggle', (e: any) => {
    const open = e.newState === 'open';
    btn.setAttribute('aria-expanded', String(open));
    btn.classList.toggle('is-active', open);
    if (open) positionAnchoredPopover(btn, pop);
  });
  window.addEventListener('resize', () => {
    if (pop.matches(':popover-open')) positionAnchoredPopover(btn, pop);
  });
}

document.addEventListener('keydown', (e: any) => {
  const tag = (e.target && e.target.tagName) ? e.target.tagName.toLowerCase() : '';
  const isInput = tag === 'input' || tag === 'textarea' || tag === 'select' || (e.target && e.target.isContentEditable);

  if (isInput) {
    if (e.key === 'Escape') {
      const openPopover = (document.querySelector('[popover]:popover-open') as any);
      if (openPopover) {
        openPopover.hidePopover?.();
        e.preventDefault();
        return;
      }
      const modal = (document.getElementById('shortcuts-modal') as any);
      if (modal && !modal.hidden) {
        toggleShortcutsModal();
        e.preventDefault();
        return;
      }
      const settingsMenu = (document.getElementById('settings-menu') as any);
      if (settingsMenu && !settingsMenu.hidden) {
        toggleSettingsMenu(false);
        e.preventDefault();
        return;
      }
    }
    return;
  }

  if (e.key === 'Escape') {
    const openPopover = (document.querySelector('[popover]:popover-open') as any);
    if (openPopover) {
      openPopover.hidePopover?.();
      e.preventDefault();
      return;
    }
    const modal = (document.getElementById('shortcuts-modal') as any);
    if (modal && !modal.hidden) {
      toggleShortcutsModal();
      e.preventDefault();
      return;
    }
    const settingsMenu = (document.getElementById('settings-menu') as any);
    if (settingsMenu && !settingsMenu.hidden) {
      toggleSettingsMenu(false);
      e.preventDefault();
      return;
    }
    if (selectedNodeId) {
      clearNodeSelection();
      e.preventDefault();
      return;
    }
  }

  if ((e.shiftKey && e.key === 'ArrowLeft') || e.key === '[') {
    e.preventDefault();
    prevFlush();
  } else if ((e.shiftKey && e.key === 'ArrowRight') || e.key === ']') {
    e.preventDefault();
    nextFlush();
  } else if (e.altKey && (e.key === 'ArrowLeft' || e.key === 'ArrowRight')) {
    e.preventDefault();
    seekTimelineStop('output', e.key === 'ArrowLeft' ? -1 : 1);
  } else if (e.altKey && (e.key === 'ArrowUp' || e.key === 'ArrowDown')) {
    e.preventDefault();
    seekTimelineStop('mark', e.key === 'ArrowUp' ? -1 : 1);
  } else if (e.key === 'f' || e.key === 'F') {
    e.preventDefault();
    setViewMode(currentViewMode === 'flush' ? 'full' : 'flush');
  } else if (e.key === 'ArrowLeft' || e.key === 'h') {
    e.preventDefault();
    stepBack();
  } else if (e.key === 'ArrowRight' || e.key === 'l') {
    e.preventDefault();
    stepForward();
  } else if (e.key === 'ArrowUp' || e.key === 'k') {
    e.preventDefault();
    prevAction();
  } else if (e.key === 'ArrowDown' || e.key === 'j') {
    e.preventDefault();
    nextAction();
  } else if (e.key === ' ' || e.code === 'Space') {
    e.preventDefault();
    togglePlay();
  } else if (e.key === 'Home') {
    e.preventDefault();
    seekTo(0);
  } else if (e.key === 'End') {
    e.preventDefault();
    const evs = reactlogData.events || reactlogData.log || [];
    seekTo(Math.max(0, evs.length - 1));
  } else if (e.key === '?') {
    e.preventDefault();
    toggleShortcutsModal();
  }
});

window.addEventListener('DOMContentLoaded', () => {
  setupAnchoredPopover('btn-graph-legend', 'graph-legend-popover');
  setupAnchoredPopover('btn-json-menu', 'json-menu');
  init();
  new ResizeObserver(() => fitGraph()).observe((document.getElementById('graph-container') as any));
});


const reactlogExports = {
  normalizeReactlogData,
  getActiveTheme,
  updateThemeButton,
  toggleTheme,
  initTheme,
  buildGraphIndices,
  getUpstreamNodes,
  getDownstreamNodes,
  getActiveLineageSet,
  syncSearchClearButton,
  filterLineageForNode,
  prepareEventTimings,
  filterItems,
  cleanName,
  formatHumanValue,
  buildActionWaves,
  getCurrentStepTime,
  initTraceTimeline,
  updateTraceTimelineScrubber,
  nextAction,
  prevAction,
  getCurrentFlushIndex,
  getActiveFlushNodeIds,
  selectFlush,
  isIdleEvent,
  seekTimelineStop,
  prevFlush,
  nextFlush,
  setViewMode,
  setPlaybackSpeed,
  filterFlushStage,
  toggleCollapseAllModules,
  nodeRoleKey,
  isClientDataNode,
  syncRoleFilterButtons,
  toggleRoleFilter,
  findChangedNodes,
  toggleChangedNodes,
  setClientDataVisibility,
  toggleClientData,
  updateFlushUI,
  getScopedNodes,
  refreshExploration,
  updateFilterState,
  init,
  isErrorEvent,
  reactiveEventState,
  graphStateAtStep,
  nodeKind,
  toggleInspector,
  closeSidebarAndClearSelection,
  toggleSettingsMenu,
  showSidebarPanel,
  toggleRecording,
  escapeHTML,
  formatTime,
  nodeDisplayName,
  formatEventDetails,
  nodeLabelHTML,
  graphNodeLabel,
  renderEventList,
  explainWhyNodeRan,
  renderInspector,
  highlightedSourceLines,
  sourceLineHTML,
  nodeSource,
  showSourceFile,
  renderInlineSource,
  toggleSourceDrawer,
  selectNode,
  clearNodeSelection,
  dependencyRanks,
  arrangeGraphBand,
  routeGraphEdge,
  graphEdgePath,
  toggleModule,
  renderPlotPreview,
  getNodeExecutionCounts,
  toggleShortcutsModal,
  getNodeShapePath,
  renderGraph,
  updateEdgePulses,
  highlightDependencies,
  resetHighlight,
  seekTo,
  updateActionToast,
  setupVideoSync,
  updateSourceHighlight,
  togglePlay,
  stepForward,
  stepBack,
  resetTimeline,
  nodeSearchScore,
  closeSearchChoices,
  toggleSearchChoices,
  clearSearchFilter,
  handleSearch,
  resetGraphView,
  handleSearchKey,
  setupPanZoom,
  applyZoom,
  zoomAt,
  zoomIn,
  zoomOut,
  resetZoom,
  fitGraph,
  isFullscreen,
  updateFullscreenButton,
  toggleFullscreen,
  loadReactlogObject,
  importReactlogJson,
  exportReactlogJson,
  handleReactlogFileUpload,
  positionAnchoredPopover,
  setupAnchoredPopover
};

if (typeof window !== "undefined") {
  Object.assign(window, reactlogExports);
  Object.defineProperties(window, {
    zoomLevel: { get: () => zoomLevel, configurable: true },
    panOffset: { get: () => panOffset, configurable: true },
    currentStep: { get: () => currentStep, configurable: true },
    selectedNodeId: { get: () => selectedNodeId, configurable: true },
    allBursts: { get: () => allBursts, configurable: true },
    actionWaves: { get: () => actionWaves, configurable: true },
    activeBurstIndex: { get: () => activeBurstIndex, configurable: true },
    playbackSpeed: { get: () => playbackSpeed, configurable: true }
  });
}

export {
  normalizeReactlogData,
  getActiveTheme,
  updateThemeButton,
  toggleTheme,
  initTheme,
  buildGraphIndices,
  getUpstreamNodes,
  getDownstreamNodes,
  getActiveLineageSet,
  syncSearchClearButton,
  filterLineageForNode,
  prepareEventTimings,
  filterItems,
  cleanName,
  formatHumanValue,
  buildActionWaves,
  getCurrentStepTime,
  initTraceTimeline,
  updateTraceTimelineScrubber,
  nextAction,
  prevAction,
  getCurrentFlushIndex,
  getActiveFlushNodeIds,
  selectFlush,
  isIdleEvent,
  seekTimelineStop,
  prevFlush,
  nextFlush,
  setViewMode,
  setPlaybackSpeed,
  filterFlushStage,
  toggleCollapseAllModules,
  nodeRoleKey,
  isClientDataNode,
  syncRoleFilterButtons,
  toggleRoleFilter,
  findChangedNodes,
  toggleChangedNodes,
  setClientDataVisibility,
  toggleClientData,
  updateFlushUI,
  getScopedNodes,
  refreshExploration,
  updateFilterState,
  init,
  isErrorEvent,
  reactiveEventState,
  graphStateAtStep,
  nodeKind,
  toggleInspector,
  closeSidebarAndClearSelection,
  toggleSettingsMenu,
  showSidebarPanel,
  toggleRecording,
  escapeHTML,
  formatTime,
  nodeDisplayName,
  formatEventDetails,
  nodeLabelHTML,
  graphNodeLabel,
  renderEventList,
  explainWhyNodeRan,
  renderInspector,
  highlightedSourceLines,
  sourceLineHTML,
  nodeSource,
  showSourceFile,
  renderInlineSource,
  toggleSourceDrawer,
  selectNode,
  clearNodeSelection,
  dependencyRanks,
  arrangeGraphBand,
  routeGraphEdge,
  graphEdgePath,
  toggleModule,
  renderPlotPreview,
  getNodeExecutionCounts,
  toggleShortcutsModal,
  getNodeShapePath,
  renderGraph,
  updateEdgePulses,
  highlightDependencies,
  resetHighlight,
  seekTo,
  updateActionToast,
  setupVideoSync,
  updateSourceHighlight,
  togglePlay,
  stepForward,
  stepBack,
  resetTimeline,
  nodeSearchScore,
  closeSearchChoices,
  toggleSearchChoices,
  clearSearchFilter,
  handleSearch,
  resetGraphView,
  handleSearchKey,
  setupPanZoom,
  applyZoom,
  zoomAt,
  zoomIn,
  zoomOut,
  resetZoom,
  fitGraph,
  isFullscreen,
  updateFullscreenButton,
  toggleFullscreen,
  loadReactlogObject,
  importReactlogJson,
  exportReactlogJson,
  handleReactlogFileUpload,
  positionAnchoredPopover,
  setupAnchoredPopover
};
