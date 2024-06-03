// text-area/textarea-autoresize.ts
function onDelegatedEvent(eventName, selector, callback) {
  document.addEventListener(eventName, (e) => {
    const e2 = e;
    if (e2.target.matches(selector)) {
      callback(e2.target);
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
  const textAreas = document.querySelectorAll(
    "textarea.textarea-autoresize"
  );
  textAreas.forEach(update_height);
}
update_on_load();
