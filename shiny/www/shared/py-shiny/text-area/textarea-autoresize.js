(() => {
  // text-area/textarea-autoresize.ts
  function onDelegatedEvent(eventName, selector, callback) {
    document.addEventListener(eventName, (e) => {
      if (e.target.matches(selector)) {
        callback(e.target);
      }
    });
  }
  function update_height(target) {
    window.console.log("update_height", target, document.readyState);
    target.style.height = "auto";
    target.style.height = target.scrollHeight + "px";
  }
  onDelegatedEvent(
    "input",
    "textarea.textarea-autoresize",
    (target) => {
      window.console.log("delegated update");
      update_height(target);
    }
  );
  function update_on_load() {
    if (document.readyState === "loading") {
      setTimeout(update_on_load, 10);
      return;
    }
    window.console.log("load update");
    document.querySelectorAll("textarea.textarea-autoresize").forEach(update_height);
  }
  update_on_load();
})();
