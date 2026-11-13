/* eslint-disable @typescript-eslint/no-explicit-any */
export interface ReactlogNode {
  id: string;
  reactId?: string;
  name?: string;
  label?: string;
  type?: string;
  role?: string;
  session?: string | null;
  value?: string;
  source?: string;
  file?: string;
  source_file?: string;
  line?: number;
  endLine?: number;
  module?: string;
  render_type?: string;
  scope?: string;
  executionCount?: number;
  lastTimestamp?: number;
  [key: string]: any;
}

export interface ReactlogEdge {
  from: string;
  to: string;
  isolated?: boolean;
  inactive?: boolean;
  [key: string]: any;
}

export interface ReactlogEvent {
  action?: string;
  event?: string;
  id?: string;
  reactId?: string;
  node_id?: string;
  ctxId?: string;
  depOnReactId?: string;
  dependsOn?: string;
  edge_from?: string;
  edge_to?: string;
  label?: string;
  node_label?: string;
  type?: string;
  node_type?: string;
  value?: any;
  step?: number;
  time?: number;
  time_sec?: number;
  timestamp?: number;
  elapsed?: number;
  session?: string | null;
  status?: string;
  phase?: string;
  provenance?: string;
  details?: string;
  error?: string;
  message?: string;
  note?: string;
  file?: string;
  line?: number;
  endLine?: number;
  isolate?: boolean;
  isolated?: boolean;
  isError?: boolean;
  [key: string]: any;
}

export interface ReactlogData {
  success?: boolean;
  version?: string;
  session?: string;
  error?: string;
  summary?: string;
  nodes?: ReactlogNode[];
  edges?: ReactlogEdge[];
  events?: ReactlogEvent[];
  log?: ReactlogEvent[];
  entries?: ReactlogEvent[];
  sources?: Record<string, string>;
  entry_file?: string;
  source?: string;
  appSource?: string;
  file?: string;
  source_file?: string;
  title?: string;
  theme?: string;
  [key: string]: any;
}
