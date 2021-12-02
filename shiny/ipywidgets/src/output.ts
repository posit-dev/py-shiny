import { HTMLManager, requireLoader } from '@jupyter-widgets/html-manager';
// N.B. for this to work properly, it seems we must include
// https://unpkg.com/@jupyter-widgets/html-manager@*/dist/libembed-amd.js
// on the page first, which is why that comes in as a
import { renderWidgets } from '@jupyter-widgets/html-manager/lib/libembed';

import type { renderContent } from 'rstudio-shiny/srcts/types/src/shiny/render';
import type { ErrorsMessageValue } from 'rstudio-shiny/srcts/types/src/shiny/shinyapp';

//if (window.require) {
//  console.log("require")
//  // @ts-ignore: this is a dynamic import
//  window.require.config({
//    paths: {
//      '@jupyter-widgets/base': 'https://unpkg.com/@jupyter-widgets/base@4.0.0/lib/index.js'
//    }
//  });
//}

// Whenever the ipywidget's state changes, let Shiny know about it
class ShinyHTMLManager extends HTMLManager {
  input_id: string = null;

  constructor(options, input_id) {
    super(options);
    this.input_id = input_id;
  }

  set_state(state): ReturnType<typeof HTMLManager.prototype.set_state> {
    // Make each model's state a bit more human-readable before sending it to Shiny
    const shinyState = {};
    Object.entries(state.state).forEach(([key, value]) => {
      // @ts-ignore: I don't think ipywidgets provides a type for this
      shinyState[value.model_name] = value.state;
    });
    window.Shiny.setInputValue(this.input_id, JSON.stringify(shinyState, null, 2));

    return super.set_state(state);
  }

}

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
