// Framework-owned WebMCP adapter. The server opt-in controls both registration
// and the RPC handlers; no test-mode or arbitrary server-state endpoint is used.
type Schema = {
  type: string;
  description?: string;
  enum?: unknown[];
  minimum?: number;
  maximum?: number;
  minItems?: number;
  maxItems?: number;
  items?: Schema;
  properties?: Record<string, Schema>;
  required?: string[];
  additionalProperties?: boolean;
};
type Definition = {
  name: string;
  description: string;
  inputSchema: Schema;
  annotations?: Record<string, boolean>;
};
type Tool = Definition & {
  execute: (
    args: Record<string, unknown>,
    options?: { signal?: AbortSignal }
  ) => Promise<string>;
};
interface ModelContext {
  registerTool(tool: Tool, options: { signal: AbortSignal }): Promise<void>;
}
interface Binding {
  name: string;
  getId(el: HTMLElement): string;
  getType(el: HTMLElement): string | null;
  getValue(el: HTMLElement): unknown;
  setValue(el: HTMLElement, value: unknown): void;
  getState(el: HTMLElement): Record<string, unknown> | undefined;
}
interface ShinyClient {
  initializedPromise: Promise<void>;
  setInputValue(
    id: string,
    value: unknown,
    options?: { priority: string }
  ): void;
  addCustomMessageHandler(
    name: string,
    handler: (data: { tools: Definition[] }) => void
  ): void;
  shinyapp: {
    makeRequest(
      method: string,
      args: unknown[],
      success: (value: unknown) => void,
      error: (message: string) => void
    ): void;
  };
}
const shiny = window.Shiny as unknown as ShinyClient;
const emptySchema: Schema = {
  type: "object",
  properties: {},
  additionalProperties: false,
};
const supported = new Set([
  "shiny.textInput",
  "shiny.textareaInput",
  "shiny.numberInput",
  "shiny.checkboxInput",
  "shiny.checkboxGroupInput",
  "shiny.radioInput",
  "shiny.selectInput",
  "shiny.sliderInput",
  "shiny.dateInput",
  "shiny.dateRangeInput",
]);
function visible(el: HTMLElement): boolean {
  const container = el.closest<HTMLElement>(".shiny-input-container") || el;
  return (
    !!container.getClientRects().length &&
    getComputedStyle(container).visibility !== "hidden"
  );
}
function excluded(el: HTMLElement): boolean {
  return !!el.closest('[data-webmcp="exclude"]');
}
function label(el: HTMLElement): string {
  const explicit = document
    .querySelector(`label[for="${CSS.escape(el.id)}"]`)
    ?.textContent?.trim();
  if (explicit) return explicit;
  const implicit = el.closest("label")?.textContent?.trim();
  if (implicit) return implicit;
  const labelledBy = el.getAttribute("aria-labelledby");
  if (labelledBy) {
    const text = labelledBy
      .split(/\s+/)
      .map((id) => document.getElementById(id)?.textContent?.trim())
      .filter(Boolean)
      .join(" ");
    if (text) return text;
  }
  return el.getAttribute("aria-label")?.trim() || el.id;
}
function slider(el: HTMLElement): {
  options: { min: number; max: number; disable?: boolean };
} {
  return $(el).data("ionRangeSlider");
}
function dateBounds(el: HTMLElement) {
  // DateInputBinding.getState() depends on obsolete datepicker fields. Use the
  // same datepicker methods as DateRangeInputBinding to read current bounds.
  const picker = $(el).find("input").first().data("datepicker") as {
    getStartDate(): Date | number;
    getEndDate(): Date | number;
  };
  const format = (date: Date | number) =>
    date instanceof Date && Number.isFinite(date.getTime())
      ? date.toISOString().slice(0, 10)
      : undefined;
  return {
    min: format(picker.getStartDate()),
    max: format(picker.getEndDate()),
  };
}
function schemaFor(el: HTMLElement, name: string, binding: Binding): Schema {
  const value = binding.getValue(el);
  let item: Schema;
  if (name === "shiny.checkboxInput") item = { type: "boolean" };
  else if (name === "shiny.numberInput" || name === "shiny.sliderInput") {
    item = { type: "number" };
    const min =
      name === "shiny.sliderInput"
        ? slider(el).options.min
        : el.getAttribute("min");
    const max =
      name === "shiny.sliderInput"
        ? slider(el).options.max
        : el.getAttribute("max");
    if (min !== null && min !== "" && Number.isFinite(Number(min)))
      item.minimum = Number(min);
    if (max !== null && max !== "" && Number.isFinite(Number(max)))
      item.maximum = Number(max);
  } else {
    item = { type: "string" };
    if (
      [
        "shiny.selectInput",
        "shiny.radioInput",
        "shiny.checkboxGroupInput",
      ].includes(name)
    ) {
      const options = binding.getState(el)?.options as
        | { value: string }[]
        | undefined;
      item.enum = options?.map((o) => o.value) || [];
      // Selectize may retain choices that are absent from the underlying select.
      const selectize = (
        el as HTMLElement & {
          selectize?: {
            options: Record<string, Record<string, unknown>>;
            settings: { valueField: string; disabledField: string };
          };
        }
      ).selectize;
      if (selectize)
        item.enum = Object.values(selectize.options)
          .filter((o) => !o[selectize.settings.disabledField])
          .map((o) => o[selectize.settings.valueField]);
      const disabledChoices = Array.from(
        el.querySelectorAll<HTMLOptionElement>("option:disabled")
      ).map((option) => option.value);
      item.enum = item.enum.filter(
        (value) => !disabledChoices.includes(String(value))
      );
    }
  }
  const multiple =
    Array.isArray(value) ||
    (el instanceof HTMLSelectElement && el.multiple) ||
    name === "shiny.checkboxGroupInput";
  const schema: Schema = multiple ? { type: "array", items: item } : item;
  if (
    (name === "shiny.sliderInput" && multiple) ||
    name === "shiny.dateRangeInput"
  ) {
    schema.minItems = 2;
    schema.maxItems = 2;
  }
  schema.description = label(el);
  if (name.startsWith("shiny.date")) {
    const state = dateBounds(el);
    schema.description += `; YYYY-MM-DD dates${
      state?.min ? `, minimum ${state.min}` : ""
    }${state?.max ? `, maximum ${state.max}` : ""}`;
  }
  return schema;
}
function inputs() {
  return Array.from(
    document.querySelectorAll<HTMLElement>(".shiny-bound-input")
  ).flatMap((el) => {
    if (excluded(el) || !visible(el)) return [];
    const binding = $(el).data("shiny-input-binding") as Binding;
    if (!binding) return [];
    const name = binding.name;
    if (!supported.has(name)) return [];
    // Date/time sliders have different units; use an app-defined tool for them.
    if (name === "shiny.sliderInput" && binding.getType(el)) return [];
    const disabled =
      el.matches(":disabled") ||
      // Group setters replace the whole value, including disabled children.
      !!el.querySelector("input:disabled, option:disabled:checked") ||
      (name === "shiny.sliderInput" && !!slider(el).options.disable);
    return [
      {
        el,
        binding,
        name,
        id: binding.getId(el),
        disabled,
        schema: schemaFor(el, name, binding),
      },
    ];
  });
}
function actions() {
  return Array.from(
    document.querySelectorAll<HTMLElement>(
      '.action-button.shiny-bound-input[data-webmcp="action"]'
    )
  ).filter(
    (el) =>
      !excluded(el) &&
      visible(el) &&
      !el.matches(":disabled, [disabled], .disabled, [aria-disabled='true']")
  );
}
function readOutputs(ids?: string[]) {
  const outputs: Record<
    string,
    { status: string; type: string; value?: string; truncated?: boolean }
  > = {};
  for (const el of document.querySelectorAll<HTMLElement>(
    ".shiny-bound-output"
  )) {
    if (excluded(el) || !visible(el) || (ids && !ids.includes(el.id))) continue;
    const text = el.matches(".shiny-text-output, .shiny-code-output");
    const error = el.classList.contains("shiny-output-error");
    const status = error
      ? "error"
      : el.classList.contains("recalculating")
      ? "recalculating"
      : text
      ? "ready"
      : "unsupported";
    outputs[el.id] = { status, type: text ? "text" : "visual" };
    if (text || error) {
      const value = el.innerText;
      outputs[el.id]!.value = value.slice(0, 20000);
      outputs[el.id]!.truncated = value.length > 20000;
    }
  }
  if (ids?.some((id) => !Object.hasOwn(outputs, id)))
    throw new Error("Unknown, hidden or excluded output ID.");
  return outputs;
}
function describe() {
  return {
    inputs: inputs().map(({ id, el, binding, disabled, schema }) => ({
      id,
      label: label(el),
      value: binding.getValue(el),
      disabled,
      schema,
    })),
    actions: actions().map((el) => ({
      id: el.id,
      label: el.textContent?.trim(),
    })),
    outputs: readOutputs(),
  };
}
function validate(value: unknown, schema: Schema, id: string): void {
  if (schema.type === "array") {
    if (
      !Array.isArray(value) ||
      (schema.minItems !== undefined && value.length < schema.minItems) ||
      (schema.maxItems !== undefined && value.length > schema.maxItems)
    )
      throw new Error(`Invalid array for ${id}.`);
    value.forEach((v) => validate(v, schema.items!, id));
  } else if (
    typeof value !== schema.type ||
    (schema.type === "number" && !Number.isFinite(value))
  )
    throw new Error(`Invalid ${schema.type} for ${id}.`);
  if (schema.enum && !schema.enum.includes(value))
    throw new Error(`Choose a listed value for ${id}.`);
  if (
    typeof value === "number" &&
    ((schema.minimum !== undefined && value < schema.minimum) ||
      (schema.maximum !== undefined && value > schema.maximum))
  )
    throw new Error(`Value outside bounds for ${id}.`);
}
function rpc(method: string, args: unknown[] = []): Promise<unknown> {
  return new Promise((resolve, reject) =>
    shiny.shinyapp.makeRequest(method, args, resolve, (error) =>
      reject(new Error(error))
    )
  );
}
async function flush() {
  // Force any queued client inputs onto the socket before the correlated RPC.
  shiny.setInputValue(".clientdata_webmcp_flush", crypto.randomUUID(), {
    priority: "event",
  });
  await rpc("shiny_webmcp_flush");
}
let applying = false;
async function setInputs(args: Record<string, unknown>) {
  const values = args.values;
  if (!values || typeof values !== "object" || Array.isArray(values))
    throw new Error("values must be an object.");
  const available = inputs();
  const changes = Object.entries(values).map(([id, value]) => {
    const input = available.find((i) => i.id === id && !i.disabled);
    if (!input)
      throw new Error(
        `Input is unknown, unsupported, hidden, excluded or disabled: ${id}`
      );
    validate(value, input.schema, id);
    if (
      (input.name === "shiny.sliderInput" ||
        input.name === "shiny.dateRangeInput") &&
      Array.isArray(value) &&
      value[0] > value[1]
    )
      throw new Error(`Range start must not exceed end for ${id}.`);
    if (input.name.startsWith("shiny.date")) {
      const state = dateBounds(input.el);
      for (const date of Array.isArray(value) ? value : [value]) {
        if (
          typeof date !== "string" ||
          !/^\d{4}-\d{2}-\d{2}$/.test(date) ||
          !Number.isFinite(Date.parse(date)) ||
          new Date(date).toISOString().slice(0, 10) !== date
        )
          throw new Error(`Use valid YYYY-MM-DD dates for ${id}.`);
        if (
          (typeof state?.min === "string" && date < state.min) ||
          (typeof state?.max === "string" && date > state.max)
        )
          throw new Error(`Date outside bounds for ${id}.`);
      }
    }
    return { ...input, value };
  });
  // Validate every field before changing any widget. Suppress binding-generated
  // input events while updating widgets, then submit their actual values together.
  applying = true;
  try {
    for (const { el, binding, name, value } of changes) {
      binding.setValue(
        el,
        name === "shiny.dateRangeInput"
          ? { start: (value as string[])[0], end: (value as string[])[1] }
          : value
      );
    }
  } finally {
    applying = false;
  }
  for (const { el, binding, id } of changes) {
    const type = binding.getType(el);
    shiny.setInputValue(type ? `${id}:${type}` : id, binding.getValue(el));
  }
  await flush();
  return describe();
}

async function initialize() {
  await shiny.initializedPromise;
  const modelContext = (document as Document & { modelContext?: ModelContext })
    .modelContext;
  if (!modelContext?.registerTool) return;
  let connected = true;
  let pending = false;
  let custom = (await rpc("shiny_webmcp_describe")) as Definition[];
  const registered = new Map<
    string,
    { signature: string; controller: AbortController }
  >();
  const run = (
    operation: () => Promise<unknown>,
    signal?: AbortSignal
  ): Promise<string> => {
    if (!connected || pending || signal?.aborted)
      return Promise.reject(
        new Error(
          !connected
            ? "Shiny is disconnected."
            : pending
            ? "A Shiny tool is already running."
            : "Tool cancelled."
        )
      );
    pending = true;
    return new Promise((resolve, reject) => {
      let done = false;
      const finish = (error?: Error, value?: unknown) => {
        if (done) return;
        done = true;
        clearTimeout(timer);
        signal?.removeEventListener("abort", abort);
        $(document).off("shiny:disconnected", disconnect);
        // Release the browser guard even on cancellation/timeout. Dispatched
        // Python work continues; later RPCs queue behind it in the same session.
        pending = false;
        if (error) reject(error);
        else resolve(JSON.stringify(value));
      };
      const abort = () =>
        finish(
          new Error(
            "Tool cancelled. Work already sent to Python may still complete."
          )
        );
      const disconnect = () =>
        finish(new Error("Shiny disconnected during the tool call."));
      const timer = setTimeout(
        () =>
          finish(
            new Error(
              "Shiny tool timed out after 30 seconds. Work may still complete."
            )
          ),
        30000
      );
      signal?.addEventListener("abort", abort, { once: true });
      $(document).on("shiny:disconnected", disconnect);
      operation().then(
        (value) => finish(undefined, value),
        (error) => finish(error)
      );
    });
  };
  async function refresh() {
    if (!connected) return;
    const properties = Object.fromEntries(
      inputs()
        .filter((i) => !i.disabled)
        .map((i) => [i.id, i.schema])
    );
    const tools: Tool[] = [
      {
        name: "shiny_describe_app",
        description:
          "Describe visible supported Shiny controls, allowed values, exposed actions and output status. IDs include module namespaces.",
        inputSchema: emptySchema,
        annotations: { readOnlyHint: true },
        execute: (_args, { signal } = {}) =>
          run(async () => describe(), signal),
      },
      {
        name: "shiny_set_inputs",
        // No blanket consequentialHint: ordinary filters need not be consequential.
        // Apps with meaningful side effects should expose purpose-built custom
        // tools and enforce permissions server-side; annotations are only hints.
        description:
          "Update Shiny input widgets by ID and return their state and visible outputs after a server reactive flush. Input changes can trigger application effects. This does not wait for background tasks.",
        inputSchema: {
          type: "object",
          properties: {
            values: { type: "object", properties, additionalProperties: false },
          },
          required: ["values"],
          additionalProperties: false,
        },
        execute: (args, { signal } = {}) => run(() => setInputs(args), signal),
      },
      {
        name: "shiny_read_outputs",
        description:
          "Read currently displayed text/code outputs and error or recalculating status. Visual outputs are described as unsupported; their underlying data is not exposed. Long text is truncated.",
        inputSchema: {
          type: "object",
          properties: { ids: { type: "array", items: { type: "string" } } },
          additionalProperties: false,
        },
        annotations: { readOnlyHint: true },
        execute: (args, { signal } = {}) =>
          run(async () => {
            if (
              args.ids !== undefined &&
              (!Array.isArray(args.ids) ||
                !args.ids.every((id) => typeof id === "string"))
            )
              throw new Error("ids must be an array of strings.");
            await flush();
            return readOutputs(args.ids as string[] | undefined);
          }, signal),
      },
      ...custom.map((definition) => ({
        ...definition,
        execute: (
          args: Record<string, unknown>,
          { signal }: { signal?: AbortSignal } = {}
        ) =>
          run(
            () => rpc("shiny_webmcp_invoke", [definition.name, args]),
            signal
          ),
      })),
    ];
    const buttons = actions();
    if (buttons.length)
      tools.push({
        name: "shiny_invoke_action",
        description:
          "Activate an explicitly exposed Shiny action button and return the dashboard after a reactive flush. This can perform consequential application actions.",
        inputSchema: {
          type: "object",
          properties: {
            id: { type: "string", enum: buttons.map((el) => el.id) },
          },
          required: ["id"],
          additionalProperties: false,
        },
        annotations: { consequentialHint: true },
        execute: (args, { signal } = {}) =>
          run(async () => {
            const button = actions().find((el) => el.id === args.id);
            if (!button) throw new Error("Action is unavailable.");
            button.click();
            await flush();
            return describe();
          }, signal),
      });
    for (const [name, registration] of registered) {
      if (!tools.some((tool) => tool.name === name)) {
        registration.controller.abort();
        registered.delete(name);
      }
    }
    for (const tool of tools) {
      const signature = JSON.stringify({ ...tool, execute: undefined });
      if (registered.get(tool.name)?.signature === signature) continue;
      registered.get(tool.name)?.controller.abort();
      registered.delete(tool.name);
      const controller = new AbortController();
      await modelContext!.registerTool(tool, { signal: controller.signal });
      if (!connected) {
        controller.abort();
        return;
      }
      registered.set(tool.name, { signature, controller });
    }
  }
  let refreshChain = Promise.resolve();
  let refreshQueued = false;
  const schedule = () => {
    if (refreshQueued) return;
    refreshQueued = true;
    refreshChain = refreshChain
      .then(async () => {
        refreshQueued = false;
        await refresh();
      })
      .catch((error) =>
        console.error("Shiny WebMCP registration failed", error)
      );
  };
  shiny.addCustomMessageHandler("shiny-webmcp-tools", (message) => {
    custom = message.tools;
    schedule();
  });
  $(document).on("shiny:inputchanged", (event) => {
    if (applying) event.preventDefault();
  });
  $(document).on("shiny:bound shiny:unbound change", schedule);
  // Attribute/choice updates and conditional panels can change the schema even
  // when no new binding is created. Registration is unchanged if schemas match.
  const observer = new MutationObserver(schedule);
  observer.observe(document.body, {
    childList: true,
    subtree: true,
    attributes: true,
    attributeFilter: [
      "disabled",
      "hidden",
      "style",
      "class",
      "min",
      "max",
      "data-webmcp",
    ],
  });
  $(document).on("shiny:disconnected", () => {
    connected = false;
    registered.forEach((r) => r.controller.abort());
    registered.clear();
  });
  $(document).on("shiny:connected", () => {
    connected = true;
    rpc("shiny_webmcp_describe").then((tools) => {
      custom = tools as Definition[];
      schedule();
    });
  });
  schedule();
  await refreshChain;
}
// Register before initialization so an initial custom-tool manifest is harmless.
shiny.addCustomMessageHandler("shiny-webmcp-tools", (_message) => {
  /* Pulled after initialization. */
});
void initialize().catch((error) =>
  console.error("Shiny WebMCP initialization failed", error)
);
