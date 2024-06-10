import { LitElement, html } from "lit";
import { unsafeHTML } from "lit-html/directives/unsafe-html.js";
import { property } from "lit/decorators.js";

import ClipboardJS from "clipboard";
import { sanitize } from "dompurify";
import hljs from "highlight.js/lib/common";
import { parse } from "marked";

import { createElement } from "./_utils";

type Message = {
  content: string;
  role: string;
};
type MessageChunk = {
  content: string;
  role: "user" | "assistant";
  type?: "message_start" | "message_end";
};
type ShinyChatMessage = {
  id: string;
  handler: string;
  obj: Message | MessageChunk;
};

// https://github.com/microsoft/TypeScript/issues/28357#issuecomment-748550734
declare global {
  interface GlobalEventHandlersEventMap {
    "shiny-chat-input-sent": CustomEvent<Message>;
    "shiny-chat-append-message": CustomEvent<Message>;
    "shiny-chat-append-message-chunk": CustomEvent<MessageChunk>;
    "shiny-chat-clear-messages": CustomEvent;
  }
}

const CHAT_MESSAGE_TAG = "shiny-chat-message";
const CHAT_USER_MESSAGE_TAG = "shiny-user-message";
const CHAT_MESSAGES_TAG = "shiny-chat-messages";
const CHAT_INPUT_TAG = "shiny-chat-input";
const CHAT_CONTAINER_TAG = "shiny-chat-container";

// https://lit.dev/docs/components/shadow-dom/#implementing-createrenderroot
class LightElement extends LitElement {
  createRenderRoot() {
    return this;
  }
}

class ChatMessage extends LightElement {
  @property() content = "...";

  render(): ReturnType<LitElement["render"]> {
    // Parse string as markdown and sanitize
    // TODO: allow for customization
    const content_html = parse(this.content) as string;
    const safe_html = sanitize(content_html);

    // TODO: we should allow for custom icons
    return html`
      <span class="badge rounded-pill text-bg-secondary"
        ><svg
          xmlns="http://www.w3.org/2000/svg"
          width="16"
          height="16"
          fill="currentColor"
          class="bi bi-robot"
          viewBox="0 0 16 16"
        >
          <path
            d="M6 12.5a.5.5 0 0 1 .5-.5h3a.5.5 0 0 1 0 1h-3a.5.5 0 0 1-.5-.5M3 8.062C3 6.76 4.235 5.765 5.53 5.886a26.6 26.6 0 0 0 4.94 0C11.765 5.765 13 6.76 13 8.062v1.157a.93.93 0 0 1-.765.935c-.845.147-2.34.346-4.235.346s-3.39-.2-4.235-.346A.93.93 0 0 1 3 9.219zm4.542-.827a.25.25 0 0 0-.217.068l-.92.9a25 25 0 0 1-1.871-.183.25.25 0 0 0-.068.495c.55.076 1.232.149 2.02.193a.25.25 0 0 0 .189-.071l.754-.736.847 1.71a.25.25 0 0 0 .404.062l.932-.97a25 25 0 0 0 1.922-.188.25.25 0 0 0-.068-.495c-.538.074-1.207.145-1.98.189a.25.25 0 0 0-.166.076l-.754.785-.842-1.7a.25.25 0 0 0-.182-.135"
          />
          <path
            d="M8.5 1.866a1 1 0 1 0-1 0V3h-2A4.5 4.5 0 0 0 1 7.5V8a1 1 0 0 0-1 1v2a1 1 0 0 0 1 1v1a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-1a1 1 0 0 0 1-1V9a1 1 0 0 0-1-1v-.5A4.5 4.5 0 0 0 10.5 3h-2zM14 7.5V13a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V7.5A3.5 3.5 0 0 1 5.5 4h5A3.5 3.5 0 0 1 14 7.5"
          /></svg
      ></span>
      <div class="message-content">${unsafeHTML(safe_html)}</div>
    `;
  }

  updated(changedProperties: Map<string, unknown>): void {
    if (changedProperties.has("content")) {
      this.#highlightAndCodeCopy();
    }
  }

  // Highlight code blocks after the element is rendered
  #highlightAndCodeCopy(): void {
    const el = this.querySelector("pre code");
    if (!el) return;
    this.querySelectorAll<HTMLElement>("pre code").forEach((el) => {
      // Highlight the code
      hljs.highlightElement(el);
      // Add a button to the code block to copy to clipboard
      const btn = createElement("button", {
        class: "code-copy-button",
        title: "Copy to clipboard",
      });
      btn.innerHTML = '<i class="bi"></i>';
      el.prepend(btn);
      // Add the clipboard functionality
      const clipboard = new ClipboardJS(btn, { target: () => el });
      clipboard.on("success", function (e: ClipboardJS.Event) {
        btn.classList.add("code-copy-button-checked");
        setTimeout(
          () => btn.classList.remove("code-copy-button-checked"),
          2000
        );
        e.clearSelection();
      });
    });
  }
}

class ChatUserMessage extends LightElement {
  @property() content = "...";

  render(): ReturnType<LitElement["render"]> {
    return html`${this.content}`;
  }
}

class ChatMessages extends LightElement {
  render(): ReturnType<LitElement["render"]> {
    return html``;
  }
}

class ChatInput extends LightElement {
  @property() placeholder = "Enter a message...";
  @property({ type: Boolean, reflect: true }) disabled = false;

  private get textarea(): HTMLTextAreaElement {
    return this.querySelector("textarea") as HTMLTextAreaElement;
  }

  private get value(): string {
    return this.textarea.value;
  }

  private get valueIsEmpty(): boolean {
    return this.value.trim().length === 0;
  }

  private get button(): HTMLButtonElement {
    return this.querySelector("button") as HTMLButtonElement;
  }

  render(): ReturnType<LitElement["render"]> {
    return html`
      <div class="input-group">
        <textarea
          id="${this.id}"
          class="form-control textarea-autoresize"
          rows="1"
          placeholder="${this.placeholder}"
          @keydown=${this.#onKeyDown}
          @input=${this.#onInput}
          data-shiny-no-bind-input
        ></textarea>
        <button
          class="btn btn-primary"
          type="button"
          title="Send message"
          aria-label="Send message"
          @click=${this.#sendInput}
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="18"
            height="18"
            fill="currentColor"
            class="bi bi-send"
            viewBox="0 0 16 16"
          >
            <path
              d="M15.854.146a.5.5 0 0 1 .11.54l-5.819 14.547a.75.75 0 0 1-1.329.124l-3.178-4.995L.643 7.184a.75.75 0 0 1 .124-1.33L15.314.037a.5.5 0 0 1 .54.11ZM6.636 10.07l2.761 4.338L14.13 2.576zm6.787-8.201L1.591 6.602l4.339 2.76z"
            />
          </svg>
        </button>
      </div>
    `;
  }

  // Pressing enter sends the message (if not empty)
  #onKeyDown(e: KeyboardEvent): void {
    const isEnter = e.code === "Enter" && !e.shiftKey;
    if (isEnter && !this.valueIsEmpty) {
      e.preventDefault();
      this.#sendInput();
    }
  }

  #onInput(): void {
    this.button.disabled = this.value.trim().length === 0;
  }

  // Determine whether the button should be enabled/disabled on first render
  protected firstUpdated(): void {
    this.#onInput();
  }

  #sendInput(): void {
    if (this.valueIsEmpty) return;
    if (this.disabled) return;

    Shiny.setInputValue!(this.id, this.value, { priority: "event" });

    // Emit event so parent element knows to insert the message
    const sentEvent = new CustomEvent("shiny-chat-input-sent", {
      detail: { content: this.value, role: "user" },
      bubbles: true,
      composed: true,
    });
    this.dispatchEvent(sentEvent);

    // Clear and 'disable' the input after sending (ChatContainer will re-enable
    // when response has been received)
    this.textarea.value = "";
    this.disabled = true;

    // Simulate an input event (to trigger the textarea autoresize)
    const inputEvent = new Event("input", { bubbles: true, cancelable: true });
    this.textarea.dispatchEvent(inputEvent);

    // Keep focus on the textarea
    this.textarea.focus();
  }
}

class ChatContainer extends LightElement {
  @property() placeholder = "Enter a message...";

  private get input(): ChatInput {
    return this.querySelector(CHAT_INPUT_TAG) as ChatInput;
  }

  private get messages(): ChatMessages {
    return this.querySelector(CHAT_MESSAGES_TAG) as ChatMessages;
  }

  render(): ReturnType<LitElement["render"]> {
    const input_id = this.id + "_user_input";
    return html`
      <shiny-chat-messages></shiny-chat-messages>
      <shiny-chat-input
        id=${input_id}
        placeholder=${this.placeholder}
      ></shiny-chat-input>
    `;
  }

  firstUpdated(): void {
    // Don't attach event listeners until child elements are rendered
    if (!this.messages) return;

    this.addEventListener("shiny-chat-input-sent", this.#onInputSent);
    this.addEventListener("shiny-chat-append-message", this.#onAppend);
    this.addEventListener(
      "shiny-chat-append-message-chunk",
      this.#onAppendChunk
    );
    this.addEventListener("shiny-chat-clear-messages", this.#onClear);
    this.addEventListener(
      "shiny-chat-remove-loading-message",
      this.#onRemoveLoadingMessage
    );
  }

  disconnectedCallback(): void {
    super.disconnectedCallback();
    this.removeEventListener("shiny-chat-input-sent", this.#onInputSent);
    this.removeEventListener("shiny-chat-append-message", this.#onAppend);
    this.removeEventListener(
      "shiny-chat-append-message-chunk",
      this.#onAppendChunk
    );
    this.removeEventListener("shiny-chat-clear-messages", this.#onClear);
    this.removeEventListener(
      "shiny-chat-remove-loading-message",
      this.#onRemoveLoadingMessage
    );
  }

  // When user submits input, append it to the chat, and add a loading message
  #onInputSent(event: CustomEvent<Message>): void {
    this.#appendMessage(event.detail);
    this.#addLoadingMessage();
  }

  // Handle an append message event from server
  #onAppend(event: CustomEvent<Message>): void {
    this.#appendMessage(event.detail);
  }

  #appendMessage(message: Message, finalize = true): void {
    this.#removeLoadingMessage();

    const TAG_NAME =
      message.role === "user" ? CHAT_USER_MESSAGE_TAG : CHAT_MESSAGE_TAG;
    const msg = createElement(TAG_NAME, message);
    this.messages.appendChild(msg);

    // Scroll to the bottom to show the new message
    this.#scrollToBottom();

    if (finalize) {
      this.#finalizeMessage();
    }
  }

  #addLoadingMessage(): void {
    const loading_message = {
      // https://github.com/n3r4zzurr0/svg-spinners/blob/main/svg-css/3-dots-fade.svg
      content:
        '<svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><style>.spinner_S1WN{animation:spinner_MGfb .8s linear infinite;animation-delay:-.8s}.spinner_Km9P{animation-delay:-.65s}.spinner_JApP{animation-delay:-.5s}@keyframes spinner_MGfb{93.75%,100%{opacity:.2}}</style><circle class="spinner_S1WN" cx="4" cy="12" r="3"/><circle class="spinner_S1WN spinner_Km9P" cx="12" cy="12" r="3"/><circle class="spinner_S1WN spinner_JApP" cx="20" cy="12" r="3"/></svg>',
      role: "assistant",
      id: `${this.id}-loading-message`,
    };
    const message = createElement(CHAT_MESSAGE_TAG, loading_message);
    this.messages.appendChild(message);
  }

  #removeLoadingMessage(): void {
    const id = `${this.id}-loading-message`;
    const message = this.messages.querySelector(`#${id}`);
    if (message) message.remove();
  }

  #onAppendChunk(event: CustomEvent<MessageChunk>): void {
    this.#appendMessageChunk(event.detail);
  }

  #appendMessageChunk(message: MessageChunk): void {
    if (message.type === "message_start") {
      this.#appendMessage(message, false);
      return;
    }
    if (message.type === "message_end") {
      this.#finalizeMessage();
      return;
    }

    const messages = this.messages;
    const lastMessage = messages.lastElementChild as HTMLElement;
    if (!lastMessage) throw new Error("No messages found in the chat output");
    const content = lastMessage.getAttribute("content");
    lastMessage.setAttribute("content", content + message.content);

    // Don't scroll to bottom if the user has scrolled up a bit
    if (
      messages.scrollTop + messages.clientHeight <
      messages.scrollHeight - 50
    ) {
      return;
    }

    this.#scrollToBottom();
  }

  #onClear(): void {
    this.messages.innerHTML = "";
  }

  #onRemoveLoadingMessage(): void {
    this.#removeLoadingMessage();
    this.#finalizeMessage();
  }

  #finalizeMessage(): void {
    this.input.disabled = false;
  }

  #scrollToBottom(): void {
    this.messages.scrollTop = this.messages.scrollHeight;
  }
}

// ------- Register custom elements and shiny bindings ---------

customElements.define(CHAT_MESSAGE_TAG, ChatMessage);
customElements.define(CHAT_USER_MESSAGE_TAG, ChatUserMessage);
customElements.define(CHAT_MESSAGES_TAG, ChatMessages);
customElements.define(CHAT_INPUT_TAG, ChatInput);
customElements.define(CHAT_CONTAINER_TAG, ChatContainer);

$(function () {
  Shiny.addCustomMessageHandler(
    "shinyChatMessage",
    function (message: ShinyChatMessage) {
      const evt = new CustomEvent(message.handler, {
        detail: message.obj,
      });
      const el = document.getElementById(message.id);
      el?.dispatchEvent(evt);
    }
  );
});
