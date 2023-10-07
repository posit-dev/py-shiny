import { makeDraggable, makePopover } from './draggable-popover';
import { tag } from './tag';

const DRAG_TO_DETACH = false;

/**
 * The purpose of <shiny-bind> is to wrap HTML elements that might contain Shiny inputs
 * and/or outputs. This helps us to initializeInput/bindAll (though we could do that
 * using our custom MIME renderer) and unbindAll (I do not know of another way to do
 * this).
 *
 * It's conceivable this would also be a useful place to introduce a shadow DOM if we
 * want to protect the Shiny widgets from the rest of JupyterLab and vice versa.
 */
class ShinyBindElement extends HTMLElement {
  _initialized: boolean;

  _css = `
  shiny-popover-handle {
    display: none;
  }
  :host(:popover-open) {
    border-color: var(--jp-border-color1);
    border-width: var(--jp-border-width);
    border-radius: var(--jp-border-radius);
    padding: 0;
    box-shadow: 2px 2px 8px 0 rgba(0, 0, 0, 0.1);
  }
  :host(:popover-open) shiny-popover-handle {
    display: block;
    background: var(--jp-layout-color2);
    color: var(--jp-ui-font-color2);
    text-align: right;
  }
  .content-container {
    padding: 9px;
  }
  a.close-button {
    cursor: pointer;
    text-decoration: none;
    padding: 0 0.5em;
  }
  `;

  constructor() {
    super();
    this._initialized = false;

    let drag_handle: HTMLElement;
    let close_button: HTMLElement;
    const container = tag('div', {}, [
      tag('style', {}, [this._css]),
      (drag_handle = tag('shiny-popover-handle', {}, [
        (close_button = tag(
          'a',
          {
            class: 'close-button'
          },
          ['✕']
        ))
      ])),
      tag('div', { class: 'content-container' }, [tag('slot')])
    ]);

    this.attachShadow({ mode: 'open' });
    this.shadowRoot!.append(container);

    const dragStart = makeDraggable(drag_handle, this);
    makePopover(this, close_button, DRAG_TO_DETACH ? dragStart : undefined);
  }

  /**
   * When <shiny-bind> is added to the DOM, initialize Shiny inputs and outputs
   */
  connectedCallback() {
    if (!this._initialized) {
      // Not sure if this _initialized tracking is necessary. I added it to try to fix
      // a weird bug where input_slider was stacking on top of itself every time Shiny
      // loaded, but this didn't fix it.
      this._initialized = true;
      window.Shiny.initializeInputs(this);
    }
    window.Shiny.bindAll(this);
    this.draggable = DRAG_TO_DETACH;
  }

  /**
   * When <shiny-bind> is removed from the DOM, unbind Shiny inputs and outputs
   */
  disconnectedCallback() {
    window.Shiny.unbindAll(this);
  }
}

class ShinyPopoverHandleElement extends HTMLElement {
  constructor() {
    super();
  }
}

export function registerElement() {
  console.log('Registering <shiny-bind>');
  customElements.define('shiny-bind', ShinyBindElement);
  customElements.define('shiny-popover-handle', ShinyPopoverHandleElement);
}

export class ShinyShadowDomElement extends HTMLElement {
  _initialized: boolean;

  constructor() {
    super();
    this._initialized = false;
    const shadowRoot = this.attachShadow({ mode: 'open' });
    shadowRoot.append(...this.childNodes);

    const observer = new MutationObserver(mutationList => {
      mutationList.forEach(mutation => {
        switch (mutation.type) {
          case 'childList':
            shadowRoot.append(...this.childNodes);
            break;
        }
      });
    });
    observer.observe(this, { childList: true, subtree: false });
  }

  /**
   * When <shiny-bind> is added to the DOM, initialize Shiny inputs and outputs
   */
  connectedCallback() {
    if (!this._initialized) {
      // Not sure if this _initialized tracking is necessary. I added it to try to fix
      // a weird bug where input_slider was stacking on top of itself every time Shiny
      // loaded, but this didn't fix it.
      this._initialized = true;
      window.Shiny.initializeInputs(this.shadowRoot);
    }
    window.Shiny.bindAll(this.shadowRoot);
  }

  /**
   * When <shiny-bind> is removed from the DOM, unbind Shiny inputs and outputs
   */
  disconnectedCallback() {
    window.Shiny.unbindAll(this.shadowRoot);
  }
}
