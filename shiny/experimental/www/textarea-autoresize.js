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

    // Removed lines!
    // This may remove 1 too many lines. (Which will be added back in the next loop)
    while (target.rows > 1 && target.scrollHeight === target.clientHeight) {
      target.rows -= 1;
    }
    // Added lines!
    while (target.scrollHeight > target.clientHeight) {
      target.rows += 1;
    }
  });
})();
