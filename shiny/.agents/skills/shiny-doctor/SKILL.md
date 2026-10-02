---
name: shiny-doctor
description: "Audits, validates, and diagnoses health issues in existing Shiny for Python applications. Use when inspecting an app for reactive bugs, event loop blocks, or session state leaks, or when asked to validate or doctor an app. For building or developing apps, use `shiny-for-python`."
---

# Shiny Doctor (`/shiny-doctor`)

Shiny Doctor is a diagnostic and validation engine for Shiny for Python applications. It audits reactive graph architecture, concurrency health, UI/server bindings, session isolation, framework idioms, and performs runtime verification.

## Diagnostic Workflow

1. **CLI Validation**: Discover installed capabilities with `shiny --help`. If available, read `shiny validate --help` and run it against the target app using documented arguments. Use its diagnostics for checks it covers; CLI diagnostics alone do not establish session-level runtime verification.
2. **Systematic Audit**: Follow the 7-phase audit checklist in [Diagnostic Checklist](references/diagnostics-checklist.md) to inspect architecture, reactivity, concurrency, contracts, session scope, and performance.
3. **Fix Antipatterns**: Consult the [Antipatterns Catalog](references/antipatterns.md) for detailed bad vs. good code prescriptions, root cause analyses, and fixes.
4. **Runtime Verification**: Verify server startup and interactive session execution per the verification protocol below before completing diagnosis.

---

## Runtime Verification Protocol

1. **Server Startup Validation**:
   - When execution is available, verify application import and ASGI server startup using a managed background process or test fixture with a readiness check and timeout (e.g., launching `shiny run app.py` as a managed subprocess, polling for readiness or port listening within a timeout such as 5-10 seconds, performing the check, and ensuring process termination during cleanup). Do not run bare `shiny run` as a blocking foreground command, which causes the agent to hang indefinitely. (Do not rely on `python app.py`, which only executes top-level module code and exits without booting the ASGI Shiny server).
2. **Session-Level Verification**:
   - To claim full session-level runtime verification, connect to the application through a browser or Playwright test harness (typically using `shiny.pytest` fixtures such as `local_app` or `create_app_fixture`) so that the `server(input, output, session)` function, reactive graph initialization, WebSocket connection, and `@render.*` outputs are genuinely exercised. See the [Testing guide](../shiny-for-python/references/testing.md).
   - For behavioral bugs where the app runs but behaves incorrectly, use test-mode snapshots (`SHINY_TESTMODE=1`) or `export_test_values()` to inspect internal reactive state over HTTP between static inspection and a full Playwright run. See the [Debugging guide](../shiny-for-python/references/debugging.md).
3. **Strict Verification Labeling Rule**:
   - **Never** claim an app's behavior is fully verified based purely on static code inspection or server port listening alone.
   - If connected client tests (e.g. Playwright or `shiny.pytest` fixtures) passed, label as **Runtime Verified (Session Level)**.
   - If only server startup was executed without a client connection, label as **Server Startup Verified**.
   - If runtime execution was unavailable, explicitly label the diagnosis as **Static Diagnosis Only**.

---

## Detailed References

| Reference | Description |
|---|---|
| [Diagnostic Checklist & Verification Guide](references/diagnostics-checklist.md) | Authoritative 7-phase audit checklist for Shiny app architecture, reactivity, concurrency, and state scope |
| [Antipatterns & Prescriptions Catalog](references/antipatterns.md) | In-depth catalog of Shiny antipatterns with symptoms, bad vs. good code examples, and prescriptions |
