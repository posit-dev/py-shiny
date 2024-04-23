// Add a CSS class to the root element up until the next idle.
// busy-indicators.scss uses this class for showing busy status
// when the app is first loading.
// TODO: maybe shiny.js should be doing something like this?
document.documentElement.classList.add("shiny-not-yet-idle");
$(document).one("shiny:idle", function () {
  document.documentElement.classList.remove("shiny-not-yet-idle");
});
