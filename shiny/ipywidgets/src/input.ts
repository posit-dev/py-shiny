import { HTMLManager, requireLoader } from '@jupyter-widgets/html-manager';
// N.B. for this to work properly, it seems we must include
// https://unpkg.com/@jupyter-widgets/html-manager@*/dist/libembed-amd.js
// on the page first, which is why that comes in as a
import { renderWidgets } from '@jupyter-widgets/html-manager/lib/libembed';


class IPyWidgetInput extends window.Shiny.InputBinding {
  find(scope: HTMLElement): JQuery<HTMLElement> {
    var inputs = $(scope).find(".shiny-ipywidget-input");
    this._render();
    return inputs;
  }
  getValue(el: HTMLElement): any {
    return this.getState(el).value;
  }
  setValue(el: HTMLElement, value: any): void {
    let state = this.getState(el);
    state.value = value;
    let el_state = el.querySelector('script[type="application/vnd.jupyter.widget-state+json"]');
    el_state.textContent = JSON.stringify(state);
    this._render();
  }
  getState(el: HTMLElement): object {
    const el_state = el.querySelector('script[type="application/vnd.jupyter.widget-state+json"]');
    const state = JSON.parse(el_state.textContent).state;
    // I think state should just have one key, since input widgets
    // should only have one value/model??
    const model_ids = Object.keys(state);
    if (model_ids.length != 1) {
      console.warn("Expected exactly one model id, but found", model_ids);
      return {};
    }
    const st = state[model_ids[0]];
    if (!st.hasOwnProperty("value")) {
      console.warn("Model id ", model_ids[0], " doesn't have a value");
      return {};
    }
    return st;
  }
  _render() {
    //renderWidgets(() => new ShinyHTMLManager({ loader: requireLoader }, null));
    renderWidgets(() => new HTMLManager());
  }
  // It doesn't seem possible to subscribe to changes without a reference to the
  // underlying Backbone model. Perhaps there is a way to query it from the state object?

  //subscribe(el: HTMLElement, callback: (x: boolean) => void): void {
  //  $(el).on("change.checkboxInputBinding", function () {
  //    callback(true);
  //  });
  //}
  //unsubscribe(el: HTMLElement): void {
  //  $(el).off(".checkboxInputBinding");
  //}
  //receiveMessage(
  //  el: CheckedHTMLElement,
  //  data: CheckboxReceiveMessageData
  //): void {
  //  if (hasOwnProperty(data, "value")) el.checked = data.value;
  //
  //  // checkboxInput()'s label works different from other
  //  // input labels...the label container should always exist
  //  if (hasOwnProperty(data, "label"))
  //    $(el).parent().find("span").text(data.label);
  //
  //  $(el).trigger("change");
  //}
}

window.Shiny.inputBindings.register(new IPyWidgetInput(), "shiny.ipywidget_input");
