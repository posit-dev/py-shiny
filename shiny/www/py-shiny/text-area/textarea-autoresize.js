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
  if (target.scrollHeight > 0) {
    target.style.height = "auto";
    target.style.height = target.scrollHeight + "px";
    return;
  }
  const observer = new IntersectionObserver((entries, observer2) => {
    entries.forEach((entry) => {
      if (entry.intersectionRatio > 0) {
        observer2.unobserve(entry.target);
        update_height(entry.target);
      }
    });
  });
  observer.observe(target);
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
