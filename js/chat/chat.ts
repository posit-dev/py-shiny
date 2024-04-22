import { LitElement, html } from "lit";
import { unsafeHTML } from "lit-html/directives/unsafe-html.js";
import { property } from "lit/decorators.js";

import { parse } from "marked";

type Message = {
  content: string;
  role: string;
};
type Messages = Array<Message>;
type InsertMessageData = {
  type: "insert_message" | "insert_streaming_message";
  message: Message;
};

type BoxComponents = {
  inputContainer: HTMLElement;
  input: HTMLTextAreaElement;
  button: HTMLButtonElement;
};

const ICONS: { [key: string]: string } = {
  user: '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-person" viewBox="0 0 16 16"><path d="M8 8a3 3 0 1 0 0-6 3 3 0 0 0 0 6m2-3a2 2 0 1 1-4 0 2 2 0 0 1 4 0m4 8c0 1-1 1-1 1H3s-1 0-1-1 1-4 6-4 6 3 6 4m-1-.004c-.001-.246-.154-.986-.832-1.664C11.516 10.68 10.289 10 8 10s-3.516.68-4.168 1.332c-.678.678-.83 1.418-.832 1.664z"/></svg>',
  assistant:
    '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-robot" viewBox="0 0 16 16"><path d="M6 12.5a.5.5 0 0 1 .5-.5h3a.5.5 0 0 1 0 1h-3a.5.5 0 0 1-.5-.5M3 8.062C3 6.76 4.235 5.765 5.53 5.886a26.6 26.6 0 0 0 4.94 0C11.765 5.765 13 6.76 13 8.062v1.157a.93.93 0 0 1-.765.935c-.845.147-2.34.346-4.235.346s-3.39-.2-4.235-.346A.93.93 0 0 1 3 9.219zm4.542-.827a.25.25 0 0 0-.217.068l-.92.9a25 25 0 0 1-1.871-.183.25.25 0 0 0-.068.495c.55.076 1.232.149 2.02.193a.25.25 0 0 0 .189-.071l.754-.736.847 1.71a.25.25 0 0 0 .404.062l.932-.97a25 25 0 0 0 1.922-.188.25.25 0 0 0-.068-.495c-.538.074-1.207.145-1.98.189a.25.25 0 0 0-.166.076l-.754.785-.842-1.7a.25.25 0 0 0-.182-.135"/><path d="M8.5 1.866a1 1 0 1 0-1 0V3h-2A4.5 4.5 0 0 0 1 7.5V8a1 1 0 0 0-1 1v2a1 1 0 0 0 1 1v1a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-1a1 1 0 0 0 1-1V9a1 1 0 0 0-1-1v-.5A4.5 4.5 0 0 0 10.5 3h-2zM14 7.5V13a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V7.5A3.5 3.5 0 0 1 5.5 4h5A3.5 3.5 0 0 1 14 7.5"/></svg>',
  system:
    '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-gear" viewBox="0 0 16 16"><path d="M8 4.754a3.246 3.246 0 1 0 0 6.492 3.246 3.246 0 0 0 0-6.492M5.754 8a2.246 2.246 0 1 1 4.492 0 2.246 2.246 0 0 1-4.492 0"/><path d="M9.796 1.343c-.527-1.79-3.065-1.79-3.592 0l-.094.319a.873.873 0 0 1-1.255.52l-.292-.16c-1.64-.892-3.433.902-2.54 2.541l.159.292a.873.873 0 0 1-.52 1.255l-.319.094c-1.79.527-1.79 3.065 0 3.592l.319.094a.873.873 0 0 1 .52 1.255l-.16.292c-.892 1.64.901 3.434 2.541 2.54l.292-.159a.873.873 0 0 1 1.255.52l.094.319c.527 1.79 3.065 1.79 3.592 0l.094-.319a.873.873 0 0 1 1.255-.52l.292.16c1.64.893 3.434-.902 2.54-2.541l-.159-.292a.873.873 0 0 1 .52-1.255l.319-.094c1.79-.527 1.79-3.065 0-3.592l-.319-.094a.873.873 0 0 1-.52-1.255l.16-.292c.893-1.64-.902-3.433-2.541-2.54l-.292.159a.873.873 0 0 1-1.255-.52zm-2.633.283c.246-.835 1.428-.835 1.674 0l.094.319a1.873 1.873 0 0 0 2.693 1.115l.291-.16c.764-.415 1.6.42 1.184 1.185l-.159.292a1.873 1.873 0 0 0 1.116 2.692l.318.094c.835.246.835 1.428 0 1.674l-.319.094a1.873 1.873 0 0 0-1.115 2.693l.16.291c.415.764-.42 1.6-1.185 1.184l-.291-.159a1.873 1.873 0 0 0-2.693 1.116l-.094.318c-.246.835-1.428.835-1.674 0l-.094-.319a1.873 1.873 0 0 0-2.692-1.115l-.292.16c-.764.415-1.6-.42-1.184-1.185l.159-.291A1.873 1.873 0 0 0 1.945 8.93l-.319-.094c-.835-.246-.835-1.428 0-1.674l.319-.094A1.873 1.873 0 0 0 3.06 4.377l-.16-.292c-.415-.764.42-1.6 1.185-1.184l.292.159a1.873 1.873 0 0 0 2.692-1.115z"/></svg>',
};

const BOX_CLASS = "shiny-chat-box";
const INPUT_CLASS = "shiny-chat-input";
const CHAT_MESSAGE_TAG = "shiny-chat-message";

class ShinyChatMessage extends LitElement {
  @property() role = "user";
  @property() content = "...";

  render(): ReturnType<LitElement["render"]> {
    const content_html = parse(this.content) as string;

    // TODO: sanitize `role: user` messages?
    return html`
      <div class="message-container message-${this.role}">
        <span class="badge rounded-pill text-bg-secondary">
          ${unsafeHTML(ICONS[this.role])}
        </span>
        <div class="message-content">${unsafeHTML(content_html)}</div>
      </div>
    `;
  }

  createRenderRoot() {
    return this;
  }
}

customElements.define(CHAT_MESSAGE_TAG, ShinyChatMessage);

class ShinyChatBoxInputBinding extends Shiny.InputBinding {
  private components!: BoxComponents;

  constructor() {
    super();
    this._clickButtonOnEnter = this._clickButtonOnEnter.bind(this);
  }

  find(scope: HTMLElement): JQuery<HTMLElement> {
    return $(scope).find(`.${BOX_CLASS}`);
  }

  initialize(el: HTMLElement): void {
    const components = this._getComponents(el);
    this.components = components;

    components.input.addEventListener("keydown", this._clickButtonOnEnter);
    components.button.addEventListener("click", (e) => {
      this._submitInput(el);
    });
  }

  getValue(el: HTMLElement): Messages {
    const messageContainers =
      el.querySelectorAll<HTMLElement>(CHAT_MESSAGE_TAG);

    const messages: Messages = [];
    messageContainers.forEach(function (x) {
      const msg = {
        content: x.getAttribute("content") as string,
        role: x.getAttribute("role") as string,
      };
      messages.push(msg);
    });

    return messages;
  }

  receiveMessage(
    el: HTMLElement,
    data: InsertMessageData
  ): void | Promise<void> {
    if (data.type === "insert_message") {
      this._insertMessage(el, data.message);
    } else if (data.type === "insert_streaming_message") {
      this._insertStreamingMessage(el, data.message);
    } else {
      console.error("Unknown message type:", data.type);
    }
  }

  subscribe(el: HTMLElement, callback: (value: boolean) => void): void {
    this.components.button.addEventListener("click", (e) => {
      callback(true);
    });
  }

  _insertMessage(el: HTMLElement, message: Message): void {
    const msg = document.createElement(CHAT_MESSAGE_TAG);
    msg.setAttribute("role", message.role);
    msg.setAttribute("content", message.content);
    Shiny.renderContent(
      this.components.inputContainer,
      msg.outerHTML,
      "beforeBegin"
    );

    // Re-enable inputs after the message has been inserted
    this.components.input.disabled = false;
    this.components.button.disabled = false;
  }

  _insertStreamingMessage(el: HTMLElement, message: Message): void {
    const messageContainers =
      el.querySelectorAll<HTMLElement>(CHAT_MESSAGE_TAG);

    // TODO: this is a quick and dirty POC that assumes we should always
    // replace the last message if it's from the assistant. We should probably
    // have more robust logic for this.
    const lastMessage = messageContainers[messageContainers.length - 1];
    if (!lastMessage) {
      this._insertMessage(el, message);
      return;
    }
    if (lastMessage.getAttribute("role") === "assistant") {
      const content = lastMessage.getAttribute("content");
      lastMessage.setAttribute("content", content + message.content);
    } else {
      this._insertMessage(el, message);
    }
  }

  _submitInput(el: HTMLElement): void {
    const input = this.components.input;
    this._insertMessage(el, { content: input?.value || "", role: "user" });
    input.value = "";

    // On submit, disable inputs to prevent multiple submissions
    // (on the next message, the inputs will be re-enabled)
    this.components.input.disabled = true;
    this.components.button.disabled = true;
  }

  _getComponents(el: HTMLElement): BoxComponents {
    return {
      inputContainer: el.querySelector(
        `:scope > .${INPUT_CLASS}`
      ) as HTMLElement,
      input: el.querySelector("textarea") as HTMLTextAreaElement,
      button: el.querySelector("button") as HTMLButtonElement,
    };
  }

  // When the user presses Enter inside the query textarea, trigger a click on the "ask"
  // button. We also have to trigger a "change" event on the textarea just before that,
  // because otherwise Shiny will debounce changes to the value in the textarea, and the
  // value may not be updated before the "ask" button click event happens.
  _clickButtonOnEnter(e: KeyboardEvent): void {
    if (!(e.target instanceof HTMLTextAreaElement)) return;
    if (e.code === "Enter" && !e.shiftKey) {
      e.preventDefault();
      this.components.button.click();
    }
  }
}

if (Shiny) {
  Shiny.inputBindings.register(
    new ShinyChatBoxInputBinding(),
    "shiny.chatBoxInput"
  );
}
