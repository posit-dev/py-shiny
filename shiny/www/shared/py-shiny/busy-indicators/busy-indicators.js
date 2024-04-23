// busy-indicators/busy-indicators.ts
document.documentElement.classList.add("shiny-not-yet-idle");
$(document).one("shiny:idle", function() {
  document.documentElement.classList.remove("shiny-not-yet-idle");
});
