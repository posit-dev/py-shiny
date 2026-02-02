import { b as createTemplate, a as addListener, d as doc } from "../../index-CKRNGLIi.js";
import { a as addOverlay, s as setSelection } from "../../index-DYIRSLx1.js";
const createCopyButton = /* @__PURE__ */ createTemplate(
  '<div style=display:flex;align-items:flex-start;justify-content:flex-end><button type=button dir=ltr style=display:none class=pce-copy aria-label=Copy><svg width=1.2em aria-hidden=true viewBox="0 0 16 16" overflow=visible stroke-linecap=round fill=none stroke=currentColor><rect x=4 y=4 width=11 height=11 rx=1 /><path d="m12 2a1 1 0 00-1-1H2A1 1 0 001 2v9a1 1 0 001 1">'
);
const copyButton = () => (editor) => {
  const container = createCopyButton();
  const btn = container.firstChild;
  addListener(btn, "click", () => {
    btn.setAttribute("aria-label", "Copied!");
    if (!navigator.clipboard?.writeText(editor.extensions.codeFold?.fullCode ?? editor.value)) {
      editor.textarea.select();
      doc.execCommand("copy");
      setSelection(editor, 0);
    }
  });
  addListener(btn, "pointerenter", () => btn.setAttribute("aria-label", "Copy"));
  addOverlay(editor, container);
};
export {
  copyButton,
  createCopyButton
};
//# sourceMappingURL=index.js.map
