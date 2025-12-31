import { t as tokenizeText, l as languages, h as highlightTokens } from "./index-C1_GGQ8y.js";
const createEditor = (container, options, ...extensions) => {
  let language;
  let prevLines = [];
  let activeLine;
  let value = "";
  let activeLineNumber;
  let focused = false;
  let handleSelectionChange = true;
  let tokens = [];
  let readOnly;
  let lineCount = 0;
  const scrollContainer = editorTemplate();
  const wrapper = scrollContainer.firstChild;
  const lines = wrapper.children;
  const overlays = lines[0];
  const textarea = overlays.firstChild;
  const currentOptions = { language: "text", value };
  const currentExtensions = new Set(extensions);
  const listeners = {};
  const setOptions = (options2) => {
    Object.assign(currentOptions, options2);
    let isNewVal = value != (value = options2.value ?? value);
    let isNewLang = language != (language = currentOptions.language);
    readOnly = !!currentOptions.readOnly;
    scrollContainer.style.tabSize = currentOptions.tabSize || 2;
    textarea.inputMode = readOnly ? "none" : "";
    textarea.setAttribute("aria-readonly", readOnly);
    updateClassName();
    updateExtensions();
    if (isNewVal) {
      if (!focused) textarea.remove();
      textarea.value = value;
      textarea.selectionEnd = 0;
      if (!focused) overlays.prepend(textarea);
    }
    if (isNewVal || isNewLang) {
      update();
    }
  };
  const update = () => {
    tokens = tokenizeText(value = textarea.value, languages[language] || {});
    dispatchEvent("tokenize", tokens, language, value);
    let newLines = highlightTokens(tokens).split("\n");
    let start = 0;
    let end2 = lineCount;
    let end1 = lineCount = newLines.length;
    while (newLines[start] == prevLines[start] && start < end1) ++start;
    while (end1 && newLines[--end1] == prevLines[--end2]) ;
    if (start == end1 && start == end2) lines[start + 1].innerHTML = newLines[start] + "\n";
    else {
      let insertStart = end2 < start ? end2 : start - 1;
      let i = insertStart;
      let newHTML = "";
      while (i < end1) newHTML += `<div class=pce-line aria-hidden=true>${newLines[++i]}
</div>`;
      for (i = end1 < start ? end1 : start - 1; i < end2; i++) lines[start + 1].remove();
      if (newHTML) lines[insertStart + 1].insertAdjacentHTML("afterend", newHTML);
      for (i = insertStart + 1; i < lineCount; ) lines[++i].setAttribute("data-line", i);
      scrollContainer.style.setProperty(
        "--number-width",
        (0 | Math.log10(lineCount)) + 1 + ".001ch"
      );
    }
    dispatchEvent("update", value);
    dispatchSelection(true);
    if (handleSelectionChange) setTimeout(setTimeout, 0, () => handleSelectionChange = true);
    prevLines = newLines;
    handleSelectionChange = false;
  };
  const updateExtensions = (newExtensions) => {
    (newExtensions || currentExtensions).forEach((extension) => {
      if (typeof extension == "object") {
        extension.update(self, currentOptions);
        if (newExtensions) currentExtensions.add(extension);
      } else {
        extension(self, currentOptions);
        if (!newExtensions) currentExtensions.delete(extension);
      }
    });
  };
  const updateClassName = ([start, end] = getInputSelection()) => {
    scrollContainer.className = `prism-code-editor language-${language}${currentOptions.lineNumbers == false ? "" : " show-line-numbers"} pce-${currentOptions.wordWrap ? "" : "no"}wrap${currentOptions.rtl ? " pce-rtl" : ""} pce-${start < end ? "has" : "no"}-selection${focused ? " pce-focus" : ""}${readOnly ? " pce-readonly" : ""}${currentOptions.class ? " " + currentOptions.class : ""}`;
  };
  const getInputSelection = () => [
    textarea.selectionStart,
    textarea.selectionEnd,
    textarea.selectionDirection
  ];
  const keyCommandMap = {
    Escape() {
      textarea.blur();
    }
  };
  const inputCommandMap = {};
  const dispatchEvent = (name, ...args) => {
    listeners[name]?.forEach((handler) => handler.apply(self, args));
    currentOptions["on" + name[0].toUpperCase() + name.slice(1)]?.apply(self, args);
  };
  const dispatchSelection = (force) => {
    if (force || handleSelectionChange) {
      const selection = getInputSelection();
      const newLine = lines[activeLineNumber = numLines(value, 0, selection[selection[2] < "f" ? 0 : 1])];
      if (newLine != activeLine) {
        activeLine?.classList.remove("active-line");
        newLine.classList.add("active-line");
        activeLine = newLine;
      }
      updateClassName(selection);
      dispatchEvent("selectionChange", selection, value);
    }
  };
  const self = {
    container: scrollContainer,
    wrapper,
    lines,
    textarea,
    get activeLine() {
      return activeLineNumber;
    },
    get value() {
      return value;
    },
    options: currentOptions,
    get focused() {
      return focused;
    },
    get tokens() {
      return tokens;
    },
    inputCommandMap,
    keyCommandMap,
    extensions: {},
    setOptions,
    update,
    getSelection: getInputSelection,
    addExtensions(...extensions2) {
      updateExtensions(extensions2);
    },
    on: (name, handler) => {
      (listeners[name] ||= /* @__PURE__ */ new Set()).add(handler);
      return () => listeners[name].delete(handler);
    },
    remove() {
      scrollContainer.remove();
    }
  };
  addListener(textarea, "keydown", (e) => {
    keyCommandMap[e.key]?.(e, getInputSelection(), value) && preventDefault(e);
  });
  addListener(textarea, "beforeinput", (e) => {
    if (readOnly || e.inputType == "insertText" && inputCommandMap[e.data]?.(e, getInputSelection(), value))
      preventDefault(e);
  });
  addListener(textarea, "input", update);
  addListener(textarea, "blur", () => {
    selectionChange = null;
    focused = false;
    updateClassName();
  });
  addListener(textarea, "focus", () => {
    selectionChange = dispatchSelection;
    focused = true;
    updateClassName();
  });
  addListener(textarea, "selectionchange", (e) => {
    dispatchSelection();
    preventDefault(e);
  });
  getElement(container)?.append(scrollContainer);
  options && setOptions(options);
  return self;
};
const editorFromPlaceholder = (placeholder, options, ...extensions) => {
  const el = getElement(placeholder);
  const editor = createEditor(
    null,
    Object.assign({ value: el.textContent }, options),
    ...extensions
  );
  el.replaceWith(editor.container);
  return editor;
};
const doc = "u" > typeof window ? document : null;
const templateEl = /* @__PURE__ */ doc?.createElement("div");
const createTemplate = (html, node) => {
  if (templateEl) {
    templateEl.innerHTML = html;
    node = templateEl.firstChild;
  }
  return () => node.cloneNode(true);
};
const addListener = (target, type, listener, options) => target.addEventListener(type, listener, options);
const getElement = (el) => typeof el == "string" ? doc.querySelector(el) : el;
const numLines = (str, start = 0, end = Infinity) => {
  let count = 1;
  for (; (start = str.indexOf("\n", start) + 1) && start <= end; count++) ;
  return count;
};
const languageMap = {};
const editorTemplate = /* @__PURE__ */ createTemplate(
  "<div><div class=pce-wrapper><div class=pce-overlays><textarea class=pce-textarea spellcheck=false autocapitalize=off autocomplete=off>"
);
const preventDefault = (e) => {
  e.preventDefault();
  e.stopImmediatePropagation();
};
const setSelectionChange = (f) => selectionChange = f;
let selectionChange;
if (doc) addListener(doc, "selectionchange", () => selectionChange?.());
export {
  addListener as a,
  createTemplate as b,
  createEditor as c,
  doc as d,
  selectionChange as e,
  editorFromPlaceholder as f,
  getElement as g,
  languageMap as l,
  numLines as n,
  preventDefault as p,
  setSelectionChange as s
};
//# sourceMappingURL=index-CKRNGLIi.js.map
