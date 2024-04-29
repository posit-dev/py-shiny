// busy-indicators/busy-indicators.ts
document.documentElement.classList.add("shiny-not-yet-idle");
$(document).one("shiny:idle", function() {
  document.documentElement.classList.remove("shiny-not-yet-idle");
});
var BUSY_CLASS = "shiny-output-busy";
function isDownloadBinding(binding) {
  return binding.name === "shiny.downloadLink";
}
$(document).on("shiny:bound", function(x) {
  const e = x;
  if (e.bindingType !== "output")
    return;
  if (isDownloadBinding(e.binding))
    return;
  e.target.classList.add(BUSY_CLASS);
});
$(document).on("shiny:outputinvalidated", function(x) {
  const e = x;
  if (isDownloadBinding(e.binding))
    return;
  e.target.classList.add(BUSY_CLASS);
});
$(document).on("shiny:value", function(e) {
  e.target.classList.remove(BUSY_CLASS);
});
$(document).on("shiny:error", function(e) {
  e.target.classList.remove(BUSY_CLASS);
});
