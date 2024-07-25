// By importing the css file, it will be copied to the output directory.
import "./textarea-autoresize.css";

export interface DOMEvent<T extends EventTarget> extends Event {
  readonly target: T;
}

function onDelegatedEvent(
  eventName: string,
  selector: string,
  callback: (target: HTMLTextAreaElement) => void
) {
  document.addEventListener(eventName, (e) => {
    const e2 = e as DOMEvent<HTMLTextAreaElement>;
    if (e2.target.matches(selector)) {
      callback(e2.target);
    }
  });
}

function update_height(target: HTMLTextAreaElement) {
  if (target.scrollHeight > 0) {
    // Automatically resize the textarea to fit its content.
    target.style.height = "auto";
    target.style.height = target.scrollHeight + "px";
  } else {
    // The textarea is not visible on the page, therefore it has a 0 scroll height.

    // If `.getAttribute("rows")` is set to 0 (as `target.rows` is always > 0 and
    // invalid values use the default value of `2`), then we can wait for the textarea
    // to become visible and call `update_height` again as the scroll height should not
    // be 0.
    //
    // Note: `rows` is only set to `0` from the python code when the textarea is
    // autoresized and no `rows` value is given.
    const targetRows = target.getAttribute("rows");
    if (targetRows == "0") {
      // Create an observer to watch for the textarea becoming visible
      const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach((entry) => {
          // If the entry is visible (even if it's just a single pixel)
          if (entry.intersectionRatio > 0) {
            // Stop observing the target
            observer.unobserve(entry.target);

            // Reset rows to `1` so that the textarea shrinks when content is removed.
            // (Otherwise the `0` value placeholder actually represents the default value of `2`)
            const entryTarget = entry.target as HTMLTextAreaElement;
            entryTarget.rows = 1;
            update_height(entryTarget);
          }
        });
      });
      observer.observe(target);
    }
  }
}

// Update on change
onDelegatedEvent(
  "input",
  "textarea.textarea-autoresize",
  (target: HTMLTextAreaElement) => {
    update_height(target);
  }
);

// Update on load
function update_on_load() {
  if (document.readyState === "loading") {
    // Document still loading, wait 10ms to check again.
    setTimeout(update_on_load, 10);
    return;
  }

  // document.readyState in ["interactive", "complete"];\
  const textAreas = document.querySelectorAll(
    "textarea.textarea-autoresize"
  ) as NodeListOf<HTMLTextAreaElement>;
  textAreas.forEach(update_height);
}
update_on_load();
