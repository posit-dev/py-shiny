---
title: "OpenTelemetry Instrumentation"
description: "How Shiny's internal OpenTelemetry spans and logs work: collect levels, the span/log helpers in shiny/otel/, every emission site, naming and attribute conventions, testing, and the bundled otel skill reference. Read before adding or changing a span/log, touching shiny.otel, or editing reactive/session code that is instrumented."
---

# OpenTelemetry Instrumentation

Shiny emits OTel spans and logs for session lifecycle, reactive flushes, and
individual reactive executions. All machinery lives in `shiny/otel/`; the
public API is only `otel.suppress`, `otel.collect`, and `otel.get_level`
(`shiny/otel/__init__.py`, whose module docstring is the user-facing guide).

## Module map

| File | Contents |
|---|---|
| `_collect.py` | `OtelCollectLevel` (IntEnum), `_current_collect_level` ContextVar, `get_level()`, `_get_env_level()` |
| `_decorators.py` | `suppress` / `collect` (decorator or context manager), `_OtelContext`, `_stamp_or_raise` |
| `_function_attrs.py` | `set_otel_collect_level_on_func`, `resolve_func_otel_level` |
| `_core.py` | lazy `get_otel_tracer` / `get_otel_logger`, `is_otel_tracing_enabled`, `emit_otel_log`, `detached_otel_context` |
| `_span_wrappers.py` | `shiny_otel_span` (async CM), `shiny_otel_span_stream` (wraps a byte iterator) |
| `_labels.py` | `create_otel_label`, `create_otel_span_name`, `get/set_otel_label_modifier` |
| `_attributes.py` | `get_session_id_attrs`, `extract_http_attributes`, `extract_source_ref` |
| `_errors.py` | silent-error detection, sanitization, record-once marking |
| `_constants.py` | `TRACER_NAME = "co.posit.python-package.shiny"`, `ATTR_SESSION_ID = "session.id"`, function/exception marker attr names |

## Dependencies and the no-op path

- `opentelemetry-api` is a **hard** dependency (`[project] dependencies` in
  `pyproject.toml`), so `shiny/otel/*` imports `opentelemetry` at module top.
  The SDK is optional: the `shiny[otel]` extra adds `opentelemetry-sdk` and
  `opentelemetry-distro[otlp]` (for `opentelemetry-instrument`).
- `is_otel_tracing_enabled()` returns `True` only if `opentelemetry.sdk` imports
  and the global tracer provider is an SDK `TracerProvider` or a proxy whose
  `.provider` is one (logfire). It is deliberately **not cached**, so a provider
  installed after `import shiny` is picked up.
- `shiny_otel_span` checks it first and yields `None` without touching the
  tracer when disabled. Callers must treat the yielded span as `Span | None`.
- `get_otel_tracer()` / `get_otel_logger()` cache in module globals
  (`_core._tracer`, `_core._logger`) on first use.

## Collect levels

`OtelCollectLevel`: `NONE=0 < SESSION=1 < REACTIVE_UPDATE=2 < REACTIVITY=3 < ALL=4`
(`ALL` currently equals `REACTIVITY` in effect). A span is created iff
`collection_level >= required_level`.

- `_get_env_level()` reads `SHINY_OTEL_COLLECT` (case-insensitive, default
  `all`); invalid values emit a `UserWarning` and fall back to `ALL`.
- `get_level()` returns the ContextVar `_current_collect_level` if set
  (by `with otel.suppress()` → `NONE` / `with otel.collect()` → `ALL`), else
  `_get_env_level()`.
- `@otel.suppress` / `@otel.collect` (no parens) stamp the plain function with
  `_shiny_otel_collect_level` via `set_otel_collect_level_on_func`.
  `_stamp_or_raise` raises `TypeError` if given a `Calc_`, `Effect_`, or
  `Renderer` (wrong decorator order) or a non-callable.
- **Capture happens at object creation.** `Calc_`, `Effect_`, `ExtendedTask`
  and `OutputRenderer` registration (`Outputs.__call__` in
  `shiny/session/_session.py`) call `resolve_func_otel_level(fn)` (stamp →
  else `get_level()`) and store it as `self._otel_level`; `Value.__init__`
  stores `get_level()`. That stored level is passed as `collection_level=`.
- **Infrastructure spans ignore suppress/collect**: `session_start`,
  `session_end`, and `reactive_update` pass `collection_level=_get_env_level()`.

## Where spans and logs are emitted

| Name | Site | `required_level` |
|---|---|---|
| `session_start` (attrs: `extract_http_attributes`) | `AppSession._run_impl`, wraps `app.server(...)` | `SESSION` |
| `session_end` | `AppSession._run_session_ended_tasks` | `SESSION` |
| `reactive_update` | `ReactiveEnvironment.flush` (`shiny/reactive/_core.py`) | `REACTIVE_UPDATE` |
| `reactive.calc [mods] [ns:]name` | `Calc_._run` | `REACTIVITY` |
| `reactive.effect [mods] [ns:]name` | `Effect_._run` | `REACTIVITY` |
| `output [ns:]name` | `output_obs` inside `Outputs.__call__`'s `set_renderer` | `REACTIVITY` |
| `extended_task [ns:]name` | `ExtendedTask._execution_wrapper` | `REACTIVITY` |
| `download [ns:]id` | download handler in `AppSession._handle_request_impl` (`FileResponse` path: `shiny_otel_span`; iterator path: `shiny_otel_span_stream`) | `REACTIVITY` |

Logs (via `emit_otel_log`, gated on `is_otel_tracing_enabled()` and
`self._otel_level >= REACTIVITY`):

- `Set reactive.value [ns:]name` (INFO) from `Value._emit_otel_log`, called on
  every successful `_set`. Skipped when no session is current (initial
  `input.*`/clientdata values). Non-read-only values add the caller's source
  ref; read-only (input) values carry `"read-only": True`.
- `extended_task queued [ns:]name` (DEBUG, `queue.size`) from
  `ExtendedTask.invoke` when an invocation is queued.

`invalidate_later`'s timer task (`shiny/reactive/_core.py`, used by
`reactive.poll`) runs its invalidate + flush inside `detached_otel_context()`,
so that `reactive_update` is a root span, not a child of whatever was current.

## Naming and attribute conventions

- Span name = `"<type> [modifiers] [namespace:]<name>"` from
  `create_otel_span_name(func, label_type, session=, modifier=)`. Namespace is
  `str(session.ns)` when non-empty; names that are empty, `_`, or `<lambda>`
  become `<anonymous>`. `@reactive.event` prepends the `event` modifier via
  `set_otel_label_modifier(..., mode="prepend")` (stored in
  `_shiny_otel_label_modifier`, carried through `functools.wraps`).
- Attributes follow OTel semconv: `session.id`; `code.file.path`,
  `code.line.number`, `code.column.number`, `code.function.name` from
  `extract_source_ref` (unwraps `__wrapped__`, scans past decorator lines);
  `server.address/port/path/origin` from `extract_http_attributes`; ad hoc keys
  like `download.id`, `download.filename`, `queue.size`.
- Reactive objects precompute attrs/labels at init and pass
  `infer_session_id=False`. Infrastructure spans pass `infer_session_id=True`
  so `session.id` comes from `get_current_session()`. `infer_session_id` is a
  required keyword on both `shiny_otel_span` and `emit_otel_log`.
- `attributes=` may be a callable; it's only evaluated if the span is created
  (used for `session_start`'s HTTP attrs).

## Error recording (`shiny_otel_span`)

- Spans are started with `record_exception=False, set_status_on_exception=False`;
  the wrapper handles it.
- Silent exceptions (`SilentException`, `SilentCancelOutputException`,
  `SilentOperationInProgressException`) → status `OK`, nothing recorded.
- Other exceptions are passed through `maybe_sanitize_error`, recorded only on
  the innermost span (marker `_shiny_otel_exception_recorded` in the
  exception's `__dict__`), and every enclosing span gets `ERROR` status. The
  original exception is re-raised.
- Sanitization is controlled by `App.sanitize_otel_errors` (default `True`,
  separate from `App.sanitize_errors`), uses `app.sanitize_error_msg`, always
  sanitizes when no session is current, and never sanitizes `SafeException`.

## Adding a new span or log

1. Async code: `async with shiny_otel_span("type name", attributes=...,
   infer_session_id=..., required_level=OtelCollectLevel.X,
   collection_level=...)`. Streams: `shiny_otel_span_stream`. There is no sync
   span helper; sync code emits logs via `emit_otel_log`.
2. Pass every argument after the name by keyword. Per `AGENTS.md`,
   `required_level` is the threshold, `collection_level` the current setting.
3. Per-object work: capture `resolve_func_otel_level(fn)` at construction and
   pass it as `collection_level`. Infrastructure work: pass `_get_env_level()`.
   Omitting `collection_level` uses `get_level()` at call time.
4. Build names with `create_otel_span_name` / `create_otel_label`; use semconv
   attribute keys; compute expensive attrs lazily or once at init.
5. For logs, check `is_otel_tracing_enabled()` and the stored level before
   building attributes; `emit_otel_log` itself swallows all exceptions.
6. Internal plumbing reactives that users shouldn't see must be suppressed:
   see `output_obs` (`@otel_suppress`), `bind_task_button`'s
   `effect_sync_button`, bookmark effects in `shiny/bookmark/_bookmark.py`,
   `data_frame._init_reactives` and `@otel.suppress` calcs in
   `shiny/render/_data_frame.py`, and `with otel.suppress()` in `poll()`.
7. If the public API changes, update the user guide docstring in
   `shiny/otel/__init__.py`, `docs/_quartodoc-core.yml` (`otel` section), and
   the bundled skill reference (below).

## Testing

- Unit tests: `tests/pytest/test_otel_*.py` (collect levels, foundation,
  session, reactive execution/flush, poll, download, data frame, async context,
  error handling, value logging, logfire). Async-context propagation is
  verified in `test_otel_async_context.py`.
- Fixtures in `tests/pytest/conftest.py`: session-scoped
  `_otel_tracer_provider_session` installs one SDK `TracerProvider` +
  `InMemorySpanExporter` per worker (OTel forbids re-setting providers);
  function-scoped `otel_tracer_provider` clears the exporter and forces
  `_core._tracer = provider.get_tracer(TRACER_NAME)` in case another test
  (e.g. logfire) owns the global provider.
- `tests/pytest/otel_helpers.py`: `patch_otel_tracing_state(tracing_enabled=)`
  sets `_core._test_tracing_override` to force `is_otel_tracing_enabled()`;
  `get_exported_spans()` calls `provider.force_flush()` first (xdist races);
  `reset_otel_tracing_state()` clears the cached tracer/logger.
- Log tests (`test_otel_value_logging.py`) use an `InMemoryLogExporter` and
  point `_core._logger` at the test provider's logger.
- Use `monkeypatch.setenv/delenv("SHINY_OTEL_COLLECT", ...)`;
  `test_otel_collect.py` has an autouse fixture that clears it.
- Playwright: `tests/playwright/shiny/otel/` (`async/`,
  `client-data-inputs-init/`, `express-session-start/`). Demo app:
  `examples/open-telemetry/`.

## Bundled skill reference

`shiny/.agents/skills/shiny-for-python/references/otel.md` is the user-facing
agent reference (setup, levels table, `suppress`/`collect`, custom spans).
`tests/pytest/test_agent_skills_sync.py` fails if it stops mentioning
`otel.<name>` for every name in `shiny.otel.__all__`, `SHINY_OTEL_COLLECT`, or
`` `<level>` `` (lowercase, backticked) for every `OtelCollectLevel` member. It
checks presence only, not accuracy. See `memory-bank/agentSkills.md`.

## Pitfalls

- `with otel.suppress()` inside a reactive function body does nothing for
  Shiny's spans: levels are captured when the object is created.
- `@otel.suppress` must sit below `@reactive.calc` / `@render.*`; the reverse
  order raises `TypeError`.
- Forgetting `collection_level=_get_env_level()` on a new infrastructure span
  makes it suppressible by an enclosing `with otel.suppress()` context (the
  ContextVar is inherited by tasks).
- A new internal effect/calc/value that isn't suppressed shows up as user
  spans/logs (e.g. the output wrapper effect would double every `output` span).
- `shiny_otel_span` is async-only; there is no sync span helper.
- The user docstring's "Enable Error Sanitization" section in
  `shiny/otel/__init__.py` cites `sanitize_errors=True`, but spans actually use
  `App.sanitize_otel_errors` (already `True` by default).
- `_span_wrappers.py`'s module docstring points to
  `tests/playwright/shiny/otel-async/`; the real path is
  `tests/playwright/shiny/otel/async/`.
- `emit_otel_log` catches `TypeError` from `Logger.emit(**kwargs)` and falls
  back to building a `LogRecord` (`_emit_otel_log_record`) for
  opentelemetry-api < 1.38; keep both paths working when touching it.
- Tests that install their own provider must reset `_core._tracer` /
  `_core._logger`, or Shiny keeps using the cached tracer from the old provider.
