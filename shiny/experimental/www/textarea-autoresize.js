(() => {
  function onDelegatedEvent(eventName, selector, callback) {
    document.addEventListener(eventName, (e) => {
      if (e.target.matches(selector)) {
        callback(e);
      }
    });
  }

  onDelegatedEvent("input", "textarea.textarea-autoresize", (e) => {
    const { target } = e;
    // Automatically resize the textarea to fit its content.
    target.style.height = "auto";
    target.style.height = target.scrollHeight + "px";
  });
})();
