import { a as addListener, n as numLines, d as doc, e as selectionChange } from "./index-CKRNGLIi.js";
import { e as escapeHtml } from "./index-C1_GGQ8y.js";
const scrollToEl = (editor, el, paddingTop = 0) => {
  const style = editor.container.style;
  style.scrollPaddingBlock = `calc(var(--_sp) + ${paddingTop}px) calc(var(--_sp) + ${isChrome && !el.textContent ? el.offsetHeight : 0}px)`;
  el.scrollIntoView({ block: "nearest" });
  style.scrollPaddingBlock = "";
};
const getLineStart = (text, position) => position ? text.lastIndexOf("\n", position - 1) + 1 : 0;
const getLineEnd = (text, position) => (position = text.indexOf("\n", position)) + 1 ? position : text.length;
const addTextareaListener = (editor, type, listener, options) => addListener(editor.textarea, type, listener, options);
const getStyleValue = (el, prop) => parseFloat(getComputedStyle(el)[prop]);
const getPosition = (editor, el) => {
  const rect1 = el.getBoundingClientRect();
  const rect2 = editor.lines[0].getBoundingClientRect();
  return {
    top: rect1.y - rect2.y,
    bottom: rect2.bottom - rect1.bottom,
    left: rect1.x - rect2.x,
    right: rect2.right - rect1.right,
    height: rect1.height
  };
};
const updateNode = (node, text) => {
  if (node.data != text) node.data = text;
};
const voidlessLangs = new Set("xml,rss,atom,jsx,tsx,xquery,xeora,xeoracube,actionscript".split(","));
const voidTags = /^(?:area|base|w?br|col|embed|hr|img|input|link|meta|source|track)$/i;
let prevSelection;
const regexEscape = (str) => str.replace(/[$+?|.^*()[\]{}\\]/g, "\\$&");
const getLineBefore = (text, position) => text.slice(getLineStart(text, position), position);
const getLines = (text, start, end = start) => [
  text.slice(start = getLineStart(text, start), end = getLineEnd(text, end)).split("\n"),
  start,
  end
];
const getClosestToken = (editor, selector, marginLeft = 0, marginRight = marginLeft, position = editor.getSelection()[0]) => {
  const value = editor.value;
  const line = editor.lines[numLines(value, 0, position)];
  const walker = doc.createTreeWalker(line, 5);
  let node = walker.lastChild();
  let offset = getLineEnd(value, position) + 1 - position - node.length;
  while (-offset <= marginRight && (node = walker.previousNode())) {
    if (node.lastChild) continue;
    offset -= node.length || 0;
    if (offset <= marginLeft) {
      for (; node != line; node = node.parentNode) {
        if (node.matches?.(selector)) return node;
      }
    }
  }
};
const getLanguage = (editor, position) => getClosestToken(editor, "[class*=language-]", 0, 0, position)?.className.match(
  /language-(\S*)/
)[1] || editor.options.language;
const insertText = (editor, text, start, end, newCursorStart, newCursorEnd) => {
  if (editor.options.readOnly) return;
  prevSelection = editor.getSelection();
  end ??= start;
  let textarea = editor.textarea;
  let value = editor.value;
  let avoidBug = isChrome && !value[end ?? prevSelection[1]] && /\n$/.test(text) && /^$|\n$/.test(value);
  let removeListener;
  editor.focused || textarea.focus();
  if (start != null) textarea.setSelectionRange(start, end);
  if (newCursorStart != null) {
    removeListener = editor.on("update", () => {
      textarea.setSelectionRange(
        newCursorStart,
        newCursorEnd ?? newCursorStart,
        prevSelection[2]
      );
      removeListener();
    });
  }
  isWebKit || textarea.dispatchEvent(new InputEvent("beforeinput", { data: text }));
  if (isChrome || isWebKit) {
    if (avoidBug) {
      textarea.selectionEnd--;
      text = text.slice(0, -1);
    }
    if (isWebKit) text += "\n";
    doc.execCommand(text ? "insertHTML" : "delete", false, escapeHtml(text, /</g, "&lt;"));
    if (avoidBug) textarea.selectionStart++;
  } else doc.execCommand(text ? "insertText" : "delete", false, text);
  prevSelection = 0;
};
const setSelection = (editor, start, end = start, direction) => {
  let focused = editor.focused;
  let textarea = editor.textarea;
  let relatedTarget;
  if (!focused) {
    addListener(
      textarea,
      "focus",
      (e) => {
        relatedTarget = e.relatedTarget;
      },
      { once: true }
    );
    textarea.focus();
  }
  textarea.setSelectionRange(start, end, direction);
  selectionChange(!(!focused && (relatedTarget ? relatedTarget.focus() : textarea.blur())));
};
const userAgent = doc ? navigator.userAgent : "";
const isMac = doc ? /Mac|iPhone|iP[ao]d/.test(navigator.platform) : false;
const isChrome = /Chrome\//.test(userAgent);
const isWebKit = !isChrome && /AppleWebKit\//.test(userAgent);
const getModifierCode = (e) => e.altKey + e.ctrlKey * 2 + e.metaKey * 4 + e.shiftKey * 8;
const addOverlay = (editor, overlay) => editor.lines[0].append(overlay);
export {
  addOverlay as a,
  getLanguage as b,
  getModifierCode as c,
  getLines as d,
  getLineBefore as e,
  getLineStart as f,
  getStyleValue as g,
  isMac as h,
  insertText as i,
  addTextareaListener as j,
  getLineEnd as k,
  getPosition as l,
  scrollToEl as m,
  getClosestToken as n,
  voidTags as o,
  prevSelection as p,
  isWebKit as q,
  regexEscape as r,
  setSelection as s,
  isChrome as t,
  updateNode as u,
  voidlessLangs as v
};
//# sourceMappingURL=index-DYIRSLx1.js.map
