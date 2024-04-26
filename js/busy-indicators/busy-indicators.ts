import { OutputBinding } from "rstudio-shiny/srcts/types/src/bindings";

interface BoundEvent extends JQuery.Event {
  binding: OutputBinding;
  bindingType: string;
  target: HTMLElement;
}

// Put a class on the root element up until the "1st" idle.
// busy-indicators.scss uses this class for showing busy status
// when the app is first loading.
// TODO: maybe shiny.js should be doing something like this?
document.documentElement.classList.add("shiny-not-yet-idle");
$(document).one("shiny:idle", function () {
  document.documentElement.classList.remove("shiny-not-yet-idle");
});

// Think of this like the recalculating class that shiny.js when recalculating,
// except it also gets added to output bindings that haven't yet received their
// 1st value.
const BUSY_CLASS = "shiny-output-busy";

// Add BUSY_CLASS to output bindings that haven't yet received their value
// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
$(document).on("shiny:bound", function (e: BoundEvent) {
  if (e.bindingType !== "output") {
    return;
  }

  const target = e.target;
  if (!(target instanceof HTMLElement)) {
    return;
  }

  // Downloads are implemented via an output binding...
  // Instead of showing a spinner on the button/link itself, we'll add a busy status
  // to the page.
  if (e.binding.name === "shiny.downloadLink") {
    return;
  }

  target.classList.add(BUSY_CLASS);
  // TODO: do this on shiny:disconnected too?
  $(target).on("shiny:value shiny:error", function () {
    target.classList.remove(BUSY_CLASS);
  });
});

// Add BUSY_CLASS to recalculating outputs
$(document).on("shiny:recalculating", function (e: Event) {
  const target = e.target;
  if (!(target instanceof HTMLElement)) {
    return;
  }

  target.classList.add(BUSY_CLASS);
  $(target).on("shiny:recalculated", function () {
    target.classList.remove(BUSY_CLASS);
  });
});
