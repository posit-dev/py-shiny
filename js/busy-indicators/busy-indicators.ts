import { OutputBinding } from "rstudio-shiny/srcts/types/src/bindings";

interface BoundEvent extends JQuery.TriggeredEvent {
  binding: OutputBinding;
  bindingType: string;
}

interface InvalidatedEvent extends JQuery.TriggeredEvent {
  name: string;
  binding: OutputBinding;
}

// This of this like the .shiny-busy class that shiny.js puts on the root element,
// except it's added before shiny.js is initialized, connected, etc.
// TODO: maybe shiny.js should be doing something like this?
document.documentElement.classList.add("shiny-not-yet-idle");
$(document).one("shiny:idle", function () {
  document.documentElement.classList.remove("shiny-not-yet-idle");
});

// Think of this like the .recalculating class that shiny.js when recalculating,
// except it also gets added to output bindings that haven't yet received their
// 1st value.
const BUSY_CLASS = "shiny-output-busy";

// Downloads are implemented via an output binding, but we don't want to
// show a busy indicator on the trigger.
function isDownloadBinding(binding: OutputBinding): boolean {
  return binding.name === "shiny.downloadLink";
}

// Add BUSY_CLASS to output bindings that haven't yet received their value
$(document).on("shiny:bound", function (x) {
  const e = x as BoundEvent;

  if (e.bindingType !== "output") return;
  if (isDownloadBinding(e.binding)) return;

  e.target.classList.add(BUSY_CLASS);
});

$(document).on("shiny:outputinvalidated", function (x) {
  const e = x as InvalidatedEvent;

  if (isDownloadBinding(e.binding)) return;

  e.target.classList.add(BUSY_CLASS);
});

$(document).on("shiny:value", function (e: JQuery.TriggeredEvent) {
  e.target.classList.remove(BUSY_CLASS);
});

$(document).on("shiny:error", function (e: JQuery.TriggeredEvent) {
  e.target.classList.remove(BUSY_CLASS);
});

// TODO: remove all on shiny:disconnected?
