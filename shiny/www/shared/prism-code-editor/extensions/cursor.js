import { b as createTemplate } from "../index-CKRNGLIi.js";
import { l as getPosition, m as scrollToEl, j as addTextareaListener, u as updateNode, e as getLineBefore, k as getLineEnd } from "../index-DYIRSLx1.js";
const cursorTemplate = /* @__PURE__ */ createTemplate(
  "<div style=position:absolute;top:0;opacity:0;padding-right:inherit> <span><span></span> "
);
const cursorPosition = () => {
  let cEditor;
  const cursorContainer = cursorTemplate();
  const [before, span] = cursorContainer.childNodes;
  const [cursor, after] = span.childNodes;
  const selectionChange = (selection) => {
    const value = cEditor.value;
    const activeLine = cEditor.lines[cEditor.activeLine];
    const position = selection[selection[2] < "f" ? 0 : 1];
    updateNode(before, getLineBefore(value, position));
    updateNode(after, value.slice(position, getLineEnd(value, position)) + "\n");
    if (cursorContainer.parentNode != activeLine) activeLine.prepend(cursorContainer);
  };
  const scrollIntoView = () => scrollToEl(cEditor, cursor);
  const self = (editor) => {
    editor.on("selectionChange", selectionChange);
    cEditor = editor;
    editor.extensions.cursor = self;
    addTextareaListener(editor, "input", (e) => {
      if (/history/.test(e.inputType)) scrollIntoView();
    });
    if (editor.activeLine) selectionChange(editor.getSelection());
  };
  self.getPosition = () => getPosition(cEditor, cursor);
  self.scrollIntoView = scrollIntoView;
  self.element = cursor;
  return self;
};
export {
  cursorPosition
};
//# sourceMappingURL=cursor.js.map
