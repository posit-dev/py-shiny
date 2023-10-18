// text-area/textarea-autoresize.ts
function onDelegatedEvent(eventName, selector, callback) {
  document.addEventListener(eventName, (e) => {
    if (e.target.matches(selector)) {
      callback(e.target);
    }
  });
}
function update_height(target) {
  target.style.height = "auto";
  target.style.height = target.scrollHeight + "px";
}
onDelegatedEvent(
  "input",
  "textarea.textarea-autoresize",
  (target) => {
    update_height(target);
  }
);
function update_on_load() {
  if (document.readyState === "loading") {
    setTimeout(update_on_load, 10);
    return;
  }
  document.querySelectorAll("textarea.textarea-autoresize").forEach(update_height);
}
update_on_load();
