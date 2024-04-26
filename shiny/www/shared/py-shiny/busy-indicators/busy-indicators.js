// busy-indicators/busy-indicators.ts
document.documentElement.classList.add("shiny-not-yet-idle");
$(document).one("shiny:idle", function() {
  document.documentElement.classList.remove("shiny-not-yet-idle");
});
var BUSY_CLASS = "shiny-output-busy";
$(document).on("shiny:bound", function(e) {
  if (e.bindingType !== "output") {
    return;
  }
  const target = e.target;
  if (!(target instanceof HTMLElement)) {
    return;
  }
  if (e.binding.name === "shiny.downloadLink") {
    return;
  }
  target.classList.add(BUSY_CLASS);
  $(target).on("shiny:value shiny:error", function() {
    target.classList.remove(BUSY_CLASS);
  });
});
$(document).on("shiny:recalculating", function(e) {
  const target = e.target;
  if (!(target instanceof HTMLElement)) {
    return;
  }
  target.classList.add(BUSY_CLASS);
  $(target).on("shiny:recalculated", function() {
    target.classList.remove(BUSY_CLASS);
  });
});
