// An app-owned bridge using Shiny's public input/output events. No MCP server,
// test-mode endpoint, or access to arbitrary session values is needed.
(async () => {
  await Shiny.initializedPromise;
  const status = document.getElementById("webmcp-status");
  const modelContext = document.modelContext;
  if (!modelContext?.registerTool) {
    status.textContent = "WebMCP unavailable — use the filters normally";
    return;
  }

  const choices = JSON.parse(
    document.getElementById("sales-choices").textContent
  );
  let pending = false;
  let connected = true;
  $(document).on("shiny:connected", () => {
    connected = true;
  });
  $(document).on("shiny:disconnected", () => {
    connected = false;
  });

  function requestSummary(filters, signal) {
    if (!connected)
      return Promise.reject(
        new Error("Shiny is disconnected. Reconnect before retrying.")
      );
    if (pending)
      return Promise.reject(
        new Error("A sales tool is already running. Wait for it to finish.")
      );
    if (signal?.aborted) return Promise.reject(new Error("Tool cancelled."));
    if (
      filters !== null &&
      (!filters ||
        !choices.regions.includes(filters.region) ||
        !choices.channels.includes(filters.channel))
    ) {
      return Promise.reject(new Error("Choose a listed region and channel."));
    }

    pending = true;
    const requestId = crypto.randomUUID();
    return new Promise((resolve, reject) => {
      let settled = false;
      let frame;
      const cleanup = () => {
        settled = true;
        clearTimeout(timer);
        cancelAnimationFrame(frame);
        $(document).off("shiny:value", onValue);
        $(document).off("shiny:disconnected", onDisconnect);
        signal?.removeEventListener("abort", onAbort);
        pending = false;
      };
      const fail = (message) => {
        if (settled) return;
        cleanup();
        reject(new Error(message));
      };
      const onDisconnect = () =>
        fail("Shiny disconnected before returning the result.");
      const onAbort = () =>
        fail("Tool cancelled. Filters already applied are not rolled back.");
      const timer = setTimeout(
        () =>
          fail(
            "Shiny did not return a result within 10 seconds. Check the dashboard before retrying."
          ),
        10000
      );
      function onValue(event) {
        if (event.name !== "summary" || frame !== undefined) return;
        const result = JSON.parse(event.value);
        if (result.request_id !== requestId) return;
        // shiny:value fires before the output binding updates its element.
        // Yield to the next frame so the visible result has been applied.
        frame = requestAnimationFrame(() => {
          if (settled) return;
          cleanup();
          if (result.error) reject(new Error(result.error));
          else {
            delete result.request_id;
            resolve(JSON.stringify(result));
          }
        });
      }
      $(document).on("shiny:value", onValue);
      $(document).on("shiny:disconnected", onDisconnect);
      signal?.addEventListener("abort", onAbort, { once: true });

      if (filters) {
        // These are plain select inputs. Reflect the action in
        // the UI and send the same values through Shiny's normal input pipeline.
        for (const name of ["region", "channel"]) {
          document.getElementById(name).value = filters[name];
          Shiny.setInputValue(name, filters[name]);
        }
      }
      // A fresh token forces an answer even for unchanged filters, and prevents
      // a previous reactive flush from satisfying this call.
      Shiny.setInputValue("webmcp_request_id", requestId, {
        priority: "event",
      });
    });
  }

  try {
    await modelContext.registerTool({
      name: "set_sales_filters",
      description:
        "Filter this sales dashboard by region and channel. Updates the visible controls and returns the resulting order count, revenue and average order in USD. All includes every value. Data is fictional.",
      inputSchema: {
        type: "object",
        properties: {
          region: { type: "string", enum: choices.regions },
          channel: { type: "string", enum: choices.channels },
        },
        required: ["region", "channel"],
        additionalProperties: false,
      },
      execute: (filters, { signal } = {}) =>
        requestSummary(filters ?? {}, signal),
    });
    await modelContext.registerTool({
      name: "get_sales_summary",
      description:
        "Read the current sales dashboard filters, order count, revenue and average order in USD, including changes made by the user. Data is fictional.",
      inputSchema: {
        type: "object",
        properties: {},
        additionalProperties: false,
      },
      annotations: { readOnlyHint: true },
      execute: (_args, { signal } = {}) => requestSummary(null, signal),
    });
    status.textContent = "Agent tools ready";
  } catch (error) {
    status.textContent = `WebMCP registration failed: ${error.message}`;
  }
})();
