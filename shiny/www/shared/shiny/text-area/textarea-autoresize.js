(() => {
  function onDelegatedEvent(eventName, selector, callback) {
    document.addEventListener(eventName, (e) => {
      if (e.target.matches(selector)) {
        callback(e.target);
      }
    });
  }

  function update_height(target) {
    window.console.log("update_height", target);
    // Automatically resize the textarea to fit its content.
    target.style.height = "auto";
    target.style.height = target.scrollHeight + "px";
  }

  // Update on change
  onDelegatedEvent("input", "textarea.textarea-autoresize", update_height);

  // Update on load
  document.addEventListener("shiny:connected", () => {
    document
      .querySelectorAll("textarea.textarea-autoresize")
      .forEach(update_height);
  });
  $(document).on("shiny:inputchanged", function (event) {
    if (event.name === "foo") {
      event.value *= 2;
    }
  });
})();
