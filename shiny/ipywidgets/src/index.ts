import { HTMLManager } from '@jupyter-widgets/html-manager/lib/htmlmanager';
import { renderWidgets } from '@jupyter-widgets/html-manager/lib/libembed-amd';
import { requireLoader } from '@jupyter-widgets/html-manager/lib/libembed-amd';
import type { renderContent } from 'rstudio-shiny/srcts/types/src/shiny/render';
import type { ErrorsMessageValue } from 'rstudio-shiny/srcts/types/src/shiny/shinyapp';

type DataType = Parameters < typeof renderContent > [1];

class ShinyHTMLManager extends HTMLManager {
  set_state(state): ReturnType<typeof HTMLManager.prototype.set_state> {
    console.log("I can has your state!!!!", state, this);
    //window.Shiny.setInputValue(this.model.get('id'), state);
    return super.set_state(state);
  }
}

// Ideally IPyWidgetBinding would extend HTMLOutputBinding, but the implementation isn't exported
class IPyWidgetBinding extends window.Shiny.OutputBinding {
  find(scope: HTMLElement): JQuery<HTMLElement> {
    return $(scope).find(".shiny-ipywidget-output");
  }
  onValueError(el: HTMLElement, err: ErrorsMessageValue): void {
    window.Shiny.unbindAll(el);
    this.renderError(el, err);
  }
  renderValue(el: HTMLElement, data: DataType): void {
    window.Shiny.renderContent(el, data);
    console.log("render");
    renderWidgets(el);

    //renderWidgets(() => new HTMLManager({ loader: requireLoader }), el);

    //renderWidgets(() => new ShinyHTMLManager({ loader: requireLoader }), el);
  }
}


(window as any).require.config({
  paths: {
   '@jupyter-widgets/html-manager': 'https://unpkg.com/@jupyter-widgets/html-manager@0.20.0/dist/embed-amd'
    //'@jupyter-widgets/base': 'https://unpkg.com/@jupyter-widgets/base@4.0.0/lib/manager-base'
  }
});
//
//(window as any).require(["@jupyter-widgets/base"]);

window.Shiny.outputBindings.register(new IPyWidgetBinding(), "shiny.ipywidget");

export { IPyWidgetBinding };
