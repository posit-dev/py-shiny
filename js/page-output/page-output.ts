import type { ErrorsMessageValue } from "rstudio-shiny/srcts/types/src/shiny/shinyapp";

class PageOutputBinding extends Shiny.OutputBinding {
  originalBodyTagAttrs: Array<Attr> | null = null;

  find(scope: HTMLElement | JQuery<HTMLElement>): JQuery<HTMLElement> {
    return $(scope).find(".shiny-page-output");
  }

  onValueError(el: HTMLElement, err: ErrorsMessageValue): void {
    if (Shiny.unbindAll) Shiny.unbindAll(el);
    this.renderError(el, err);
  }

  async renderValue(
    el: HTMLElement,
    data: Parameters<typeof Shiny.renderContentAsync>[1]
  ): Promise<void> {
    if (data === null) return;
    if (el !== document.body) {
      throw new Error(
        'Output with class "shiny-page-output" must be a <body> tag.'
      );
    }

    if (this.originalBodyTagAttrs === null) {
      // On the first run, store el's attributes so that on later runs we can clear
      // any added attributes and reset this element to its original state.
      this.originalBodyTagAttrs = Array.from(el.attributes);
    } else {
      // This is a later run. Reset attributes to their inital state.
      for (const attr of this.originalBodyTagAttrs) {
        el.setAttribute(attr.name, attr.value);
      }
    }

    let content = typeof data === "string" ? data : data.html;

    // Parse the HTML
    const parser = new DOMParser();
    const doc = parser.parseFromString(content, "text/html");

    // Copy the <html> tag's lang attribute, if present.
    if (doc.documentElement.lang) {
      document.documentElement.lang = doc.documentElement.lang;
    }

    // Copy the <title>, if present.
    if (doc.title) {
      document.title = doc.title;
    }

    // Copy attributes from parsed <body> to the output element (which should be a
    // <body>)
    for (const attr of Array.from(doc.body.attributes)) {
      if (attr.name === "class") el.classList.add(...attr.value.split(" "));
      else el.setAttribute(attr.name, attr.value);
    }

    content = content
      .replace(/<html>.*<body[^>]*>/gis, "")
      .replace(/<\/body>.*<\/html>/gis, "");

    if (typeof data === "string") {
      data = content;
    } else {
      data.html = content;
    }

    await Shiny.renderContentAsync(el, data);
  }
}

Shiny.outputBindings.register(
  new PageOutputBinding(),
  "shinyPageOutputBinding"
);

export { PageOutputBinding };
