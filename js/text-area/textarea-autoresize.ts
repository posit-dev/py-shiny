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
  // Automatically resize the textarea to fit its content.
  target.style.height = "auto";
  target.style.height = target.scrollHeight + "px";
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
