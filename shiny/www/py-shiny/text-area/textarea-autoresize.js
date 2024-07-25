// text-area/textarea-autoresize.ts
function onDelegatedEvent(eventName, selector, callback) {
  document.addEventListener(eventName, (e) => {
    const e2 = e;
    if (e2.target.matches(selector)) {
      callback(e2.target);
    }
  });
}
var textAreaIntersectionObserver = null;
function callUpdateHeightWhenTargetIsVisible(target) {
  if (textAreaIntersectionObserver === null) {
    textAreaIntersectionObserver = new IntersectionObserver(
      (entries, observer) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) {
            return;
          }
          textAreaIntersectionObserver.unobserve(entry.target);
          update_height(entry.target);
        });
      }
    );
  }
  textAreaIntersectionObserver.observe(target);
}
function update_height(target) {
  if (target.scrollHeight > 0) {
    target.style.height = "auto";
    target.style.height = target.scrollHeight + "px";
  } else {
    callUpdateHeightWhenTargetIsVisible(target);
  }
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
