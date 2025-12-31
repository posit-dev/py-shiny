var __defProp = Object.defineProperty;
var __defNormalProp = (obj, key, value) => key in obj ? __defProp(obj, key, { enumerable: true, configurable: true, writable: true, value }) : obj[key] = value;
var __publicField = (obj, key, value) => __defNormalProp(obj, typeof key !== "symbol" ? key + "" : key, value);
import { basicEditor, readonlyEditor, minimalEditor } from "./setups/index.js";
const attributeMap = {
  language: [(value) => value || "text"],
  "tab-size": [(value) => +value || 2, "tabSize"],
  "insert-spaces": [(value) => value != null, "insertSpaces"],
  "line-numbers": [(value) => value != null, "lineNumbers"],
  readonly: [(value) => value != null, "readOnly"],
  "word-wrap": [(value) => value != null, "wordWrap"],
  rtl: [(value) => value != null],
  theme: [(value) => value || "vs-code-dark"]
};
const attributes = Object.keys(attributeMap);
const getOptions = (el) => {
  const options = {};
  for (let key in attributeMap)
    options[attributeMap[key][1] || key] = attributeMap[key][0](el.getAttribute(key));
  options.value = el.textContent;
  el.textContent = "";
  return options;
};
const addComponent = (createEditor, name) => {
  var _a;
  customElements.define(
    name,
    (_a = class extends HTMLElement {
      constructor() {
        super();
        __publicField(this, "editor");
        const internals = this.attachInternals?.();
        this.editor = createEditor(
          this,
          getOptions(this),
          () => this.dispatchEvent(new CustomEvent("ready"))
        );
        if (internals) {
          this.editor.on("update", internals.setFormValue.bind(internals));
        }
        for (const attr in attributeMap)
          Object.defineProperty(this, attributeMap[attr][1] || attr, {
            enumerable: true,
            get: () => attributeMap[attr][0](this.getAttribute(attr)),
            set: /language|theme|tab-size/.test(attr) ? (val) => this.setAttribute(attr, val) : (val) => this.toggleAttribute(attr, val)
          });
      }
      get value() {
        return this.editor.value;
      }
      set value(value) {
        this.editor.setOptions({ value });
      }
      formResetCallback() {
        this.value = this.editor.options.value;
      }
      attributeChangedCallback(name2, oldValue, newValue) {
        const [fn, propName] = attributeMap[name2];
        const newVal = fn(newValue);
        if (fn(oldValue) != newVal) {
          this.editor.setOptions({
            [propName || name2]: newVal
          });
        }
      }
    }, __publicField(_a, "observedAttributes", attributes), __publicField(_a, "formAssociated", true), _a)
  );
};
const addMinimalEditor = (name) => addComponent(minimalEditor, name);
const addBasicEditor = (name) => addComponent(basicEditor, name);
const addReadonlyEditor = (name) => addComponent(readonlyEditor, name);
export {
  addBasicEditor,
  addMinimalEditor,
  addReadonlyEditor
};
//# sourceMappingURL=webComponent.js.map
