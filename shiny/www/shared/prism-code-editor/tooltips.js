import { b as createTemplate } from "./index-CKRNGLIi.js";
import { a as addOverlay, g as getStyleValue } from "./index-DYIRSLx1.js";
const template = /* @__PURE__ */ createTemplate(
  "<div class=pce-tooltip style=z-index:5;top:auto;display:flex;overflow-x:clip><div>"
);
const addTooltip = (editor, element, fixedWidth = true) => {
  const container = template();
  const style = container.style;
  const spacer = container.firstChild;
  container.append(element);
  (fixedWidth ? element : spacer).style.flexShrink = 0;
  return [
    (above) => {
      let cursor = editor.extensions.cursor;
      if (cursor) {
        let { left, right, top, bottom, height } = cursor.getPosition();
        container.parentNode || addOverlay(editor, container);
        spacer.style.width = (editor.options.rtl ? right : left) + "px";
        let placeAbove = !above == top > bottom && (above ? top : bottom) < container.clientHeight ? !above : above;
        style[placeAbove ? "bottom" : "top"] = height + (placeAbove ? bottom : top) + "px";
        style[placeAbove ? "top" : "bottom"] = "auto";
      }
    },
    () => container.remove()
  ];
};
const observer = window.ResizeObserver && /* @__PURE__ */ new ResizeObserver(
  (e) => e.forEach((entry) => {
    const el = entry.target;
    const wrapper = el.querySelector(".pce-wrapper");
    wrapper.style.paddingBottom = `${el.clientHeight - getStyleValue(wrapper, "marginBottom") - getStyleValue(wrapper, "lineHeight")}px`;
  })
);
const addOverscroll = (editor) => {
  observer && observer.observe(editor.container);
};
const removeOverscroll = (editor) => {
  observer && observer.unobserve(editor.container);
  editor.wrapper.style.paddingBottom = "";
};
export {
  addOverscroll,
  addTooltip,
  removeOverscroll
};
//# sourceMappingURL=tooltips.js.map
