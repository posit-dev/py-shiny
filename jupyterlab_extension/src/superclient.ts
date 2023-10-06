interface SuperclientWebSocketEventMap extends WebSocketEventMap {
  send: MessageEvent;
}

/**
 * This is the only WebSocket that shiny.js sees. As far as shiny.js is concerned, it's
 * a normal websocket and only one server is on the other side.
 *
 * In reality, there are multiple IPython kernels simultaneously running on the server,
 * but they are all presented through this one web page. So we use this "super" client
 * as a proxy to all of the real clients, one per kernel, that are each backed by a Comm
 * channel. Calling .send() on this superclient will cause the message to be broadcast
 * to all of the kernels. When a message is received from any of the kernels, it will be
 * received by shiny.js as usual.
 */
export class SuperclientWebSocket extends EventTarget {
  extensions: string;
  onclose: ((ev: CloseEvent) => any) | null;
  onerror: ((ev: Event) => any) | null;
  onmessage: ((ev: MessageEvent<any>) => any) | null;
  onopen: ((ev: Event) => any) | null;
  readyState: number;

  constructor() {
    super();

    this.readyState = WebSocket.CONNECTING;
    this.extensions = '';
    this.onclose = this.onerror = this.onmessage = this.onopen = () => {};

    this.addEventListener('message', event => {
      if (this.onmessage) this.onmessage(event);
    });
    this.addEventListener('open', event => {
      if (this.onopen) this.onopen(event);
    });
    this.addEventListener('error', event => {
      if (this.onerror) this.onerror(event);
    });
    this.addEventListener('close', event => {
      if (this.onclose) this.onclose(event);
    });
  }

  setToOpen() {
    this.readyState = WebSocket.OPEN;
    this.dispatchEvent(new Event('open'));
  }

  close(code?: number | undefined, reason?: string | undefined): void {
    throw new Error('Method not implemented.');
  }
  send(data: string | ArrayBufferLike | Blob | ArrayBufferView): void {
    this.dispatchEvent(new MessageEvent('send', { data }));
  }
  addEventListener<K extends keyof SuperclientWebSocketEventMap>(
    type: K,
    listener: (ev: SuperclientWebSocketEventMap[K]) => any,
    options?: boolean | AddEventListenerOptions | undefined
  ): void;
  addEventListener(
    type: string,
    listener: EventListenerOrEventListenerObject,
    options?: boolean | AddEventListenerOptions | undefined
  ): void {
    console.log('SuperclientWebSocket.addEventListener');
    super.addEventListener(type, listener, options);
  }
  removeEventListener<K extends keyof SuperclientWebSocketEventMap>(
    type: K,
    listener: (ev: SuperclientWebSocketEventMap[K]) => any,
    options?: boolean | EventListenerOptions | undefined
  ): void;
  removeEventListener(
    type: string,
    listener: EventListenerOrEventListenerObject,
    options?: boolean | EventListenerOptions | undefined
  ): void {
    console.log('SuperclientWebSocket.removeEventListener');
    super.removeEventListener(type, listener, options);
  }
}
