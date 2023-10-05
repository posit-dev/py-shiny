/**
 * The purpose of <shiny-bind> is to wrap HTML elements that might contain Shiny inputs
 * and/or outputs. This helps us to initializeInput/bindAll (though we could do that
 * using our custom MIME renderer) and unbindAll (I do not know of another way to do
 * this).
 *
 * It's conceivable this would also be a useful place to introduce a shadow DOM if we
 * want to protect the Shiny widgets from the rest of JupyterLab and vice versa.
 */
class ShinyElement extends HTMLElement {
  _initialized: boolean;

  constructor() {
    super();
    this._initialized = false;
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
  }

  /**
   * When <shiny-bind> is removed from the DOM, unbind Shiny inputs and outputs
   */
  disconnectedCallback() {
    window.Shiny.unbindAll(this);
  }
}

export function registerElement() {
  console.log('Registering <shiny-bind>');
  customElements.define('shiny-bind', ShinyElement);
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
