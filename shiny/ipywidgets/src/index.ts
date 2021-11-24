import { HTMLManager, requireLoader } from '@jupyter-widgets/html-manager';
// N.B. for this to work properly, it seems we must include
// https://unpkg.com/@jupyter-widgets/html-manager@*/dist/libembed-amd.js
// on the page first, which is why that comes in as a
import { renderWidgets } from '@jupyter-widgets/html-manager/lib/libembed';

import type { renderContent } from 'rstudio-shiny/srcts/types/src/shiny/render';
import type { ErrorsMessageValue } from 'rstudio-shiny/srcts/types/src/shiny/shinyapp';

// Whenever the ipywidget's state changes, let Shiny know about it
class ShinyHTMLManager extends HTMLManager {
  input_id: string = null;
  constructor(options, input_id) {
    super(options);
    this.input_id = input_id;
  }
  set_state(state): ReturnType<typeof HTMLManager.prototype.set_state> {
    console.log("I can has your state!!!!", state, this);
    // TODO: is this actually accessible from the session?
    window.Shiny.setInputValue(this.input_id, state);
    return super.set_state(state);
  }
}

// Register the output binding on the next tick because Shiny wants to come
// after static HTML dependencies (the libembed dependency doesn't seem to work when
// rendered dynamically, so I think this is our only option?).
setTimeout(() => {
  // Ideally IPyWidgetBinding would extend HTMLOutputBinding,
  // but the implementation isn't exported
  class IPyWidgetBinding extends window.Shiny.OutputBinding {
    find(scope: HTMLElement): JQuery<HTMLElement> {
      return $(scope).find(".shiny-ipywidget-output");
    }
    onValueError(el: HTMLElement, err: ErrorsMessageValue): void {
      window.Shiny.unbindAll(el);
      this.renderError(el, err);
    }
    renderValue(el: HTMLElement, data: Parameters<typeof renderContent>[1]): void {
      window.Shiny.renderContent(el, data);
      renderWidgets(() => new ShinyHTMLManager({ loader: requireLoader }, el.id), el);
    }
  }

  window.Shiny.outputBindings.register(new IPyWidgetBinding(), "shiny.ipywidget");
}, 0);
