// page-output/page-output.ts
var PageOutputBinding = class extends Shiny.OutputBinding {
  constructor() {
    super(...arguments);
    this.originalBodyTagAttrs = null;
  }
  find(scope) {
    return $(scope).find(".shiny-page-output");
  }
  onValueError(el, err) {
    Shiny.unbindAll(el);
    this.renderError(el, err);
  }
  async renderValue(el, data) {
    if (el !== document.body) {
      throw new Error(
        'Output with class "shiny-page-output" must be a <body> tag.'
      );
    }
    if (this.originalBodyTagAttrs === null) {
      this.originalBodyTagAttrs = Array.from(el.attributes);
    } else {
      for (const attr of this.originalBodyTagAttrs) {
        el.setAttribute(attr.name, attr.value);
      }
    }
    let content = typeof data === "string" ? data : data.html;
    const parser = new DOMParser();
    const doc = parser.parseFromString(content, "text/html");
    if (doc.documentElement.lang) {
      document.documentElement.lang = doc.documentElement.lang;
    }
    if (doc.title) {
      document.title = doc.title;
    }
    for (const attr of Array.from(doc.body.attributes)) {
      if (attr.name === "class")
        el.classList.add(...attr.value.split(" "));
      else
        el.setAttribute(attr.name, attr.value);
    }
    content = content.replace(/<html>.*<body[^>]*>/gis, "").replace(/<\/body>.*<\/html>/gis, "");
    if (typeof data === "string") {
      data = content;
    } else {
      data.html = content;
    }
    await Shiny.renderContent(el, data);
  }
};
Shiny.outputBindings.register(
  new PageOutputBinding(),
  "shinyPageOutputBinding"
);
export {
  PageOutputBinding
};
