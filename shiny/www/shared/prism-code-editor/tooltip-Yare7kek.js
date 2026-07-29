import { b as createTemplate, a as addListener, p as preventDefault } from "./index-CKRNGLIi.js";
import { addTooltip } from "./tooltips.js";
import { u as updateNode, e as getLineBefore, i as insertText, a as addOverlay, b as getLanguage, p as prevSelection, c as getModifierCode, g as getStyleValue, s as setSelection } from "./index-DYIRSLx1.js";
import { m as matchTemplate, s as searchTemplate } from "./search-5POIiI4Y.js";
const optionsFromKeys = (obj, icon) => Object.keys(obj).map((tag) => ({ label: tag, icon }));
const updateMatched = (container, matched, text) => {
  let nodes = container.childNodes;
  let nodeCount = nodes.length - 1;
  let pos = 0;
  let i = 0;
  let l = matched.length;
  for (; i < l; ) {
    if (i >= nodeCount) {
      nodes[i].before("", matchTemplate());
    }
    updateNode(nodes[i], text.slice(pos, pos = matched[i++]));
    updateNode(nodes[i].firstChild, text.slice(pos, pos = matched[i++]));
  }
  for (; nodeCount > i; ) {
    nodes[--nodeCount].remove();
  }
  updateNode(nodes[l], text.slice(pos));
};
const completeFromList = (options) => {
  return ({ path, explicit, pos }) => {
    if (path?.length == 1 && (path[0] || explicit)) {
      return {
        from: pos - path[0].length,
        options
      };
    }
  };
};
const findWords = (context, editor, filter, pattern, init, tokensOnly) => {
  const cursorPos = context.pos;
  const definition = map[context.language];
  const result = new Set(init);
  const search = (tokens, pos, isCorrectLang) => {
    let i = 0;
    let token;
    for (; token = tokens[i++]; ) {
      if (typeof token == "string") {
        if (!tokensOnly && isCorrectLang) match(token, pos);
      } else {
        const type = token.type;
        const content = token.content;
        const aliasType = token.alias || type;
        if (Array.isArray(content)) {
          if (!isCorrectLang || filter(type, pos)) {
            search(
              content,
              pos,
              aliasType.slice(0, 9) == "language-" ? definition == map[aliasType.slice(9)] : isCorrectLang
            );
          }
        } else if (isCorrectLang && filter(type, pos)) match(content, pos);
      }
      pos += token.length;
    }
  };
  const match = (token, pos) => {
    let match2;
    while (match2 = pattern.exec(token)) {
      let start = pos + match2.index;
      let str = match2[0];
      if (start > cursorPos || start + str.length < cursorPos) result.add(str);
    }
  };
  search(editor.tokens, 0, definition == map[editor.options.language]);
  return result;
};
const attrSnippet = (name, quotes, icon, boost) => ({
  label: name,
  icon,
  insert: name + "=" + quotes,
  tabStops: [name.length + 2, name.length + 2, name.length + 3],
  boost
});
const completionsFromRecords = (records, icon) => {
  const names = /* @__PURE__ */ new Set();
  records.forEach((tags) => {
    for (let key in tags) names.add(key);
  });
  return Array.from(names, (name) => ({
    label: name,
    icon
  }));
};
let count = 0;
const template = /* @__PURE__ */ createTemplate("<div class=pce-ac-tooltip><ul role=listbox>");
const rowTemplate = /* @__PURE__ */ createTemplate(
  "<li class=pce-ac-row role=option><div></div><div> </div><div class=pce-ac-details> "
);
const map = {};
const registerCompletions = (langs, definition) => {
  langs.forEach((lang) => map[lang] = definition);
};
const autoComplete = (config) => {
  const self = (editor, options) => {
    let isOpen;
    let isTyping;
    let shouldOpen;
    let currentOptions;
    let numOptions;
    let activeIndex;
    let active;
    let pos;
    let offset;
    let rowHeight;
    let cursor;
    let stops;
    let activeStop;
    let currentSelection;
    let prevLength;
    let isDeleteForwards;
    const windowSize = 13;
    const textarea = editor.textarea;
    const getSelection = editor.getSelection;
    const tooltip = template();
    const tabStopsContainer = searchTemplate();
    const [show, _hide] = addTooltip(editor, tooltip);
    const list = tooltip.firstChild;
    const id = list.id = "pce-ac-" + count++;
    const rows = list.children;
    const prevIcons = [];
    const hide = () => {
      if (isOpen) {
        _hide();
        textarea.removeAttribute("aria-controls");
        textarea.removeAttribute("aria-haspopup");
        textarea.removeAttribute("aria-activedescendant");
        isOpen = false;
      }
    };
    const setRowHeight = () => {
      rowHeight = getStyleValue(rows[0], "height");
    };
    const updateRow = (index) => {
      const option = currentOptions[index + offset];
      const [iconEl, labelEl, detailsEl] = rows[index].children;
      const completion = option[4];
      const icon = completion.icon || "variable";
      updateMatched(labelEl, option[1], completion.label);
      updateNode(detailsEl.firstChild, completion.detail || "");
      if (prevIcons[index] != icon) {
        iconEl.className = `pce-ac-icon pce-ac-icon-${prevIcons[index] = icon}`;
        iconEl.style.color = `var(--pce-ac-icon-${icon})`;
      }
    };
    const scrollActiveIntoView = () => {
      setRowHeight();
      const scrollTop = tooltip.scrollTop;
      const lower = rowHeight * activeIndex;
      const upper = rowHeight * (activeIndex + 1) - tooltip.clientHeight;
      tooltip.scrollTop = scrollTop > lower ? lower : scrollTop < upper ? upper : scrollTop;
    };
    const updateActive = () => {
      const newActive = rows[activeIndex - offset];
      if (newActive != active) {
        active?.removeAttribute("aria-selected");
        if (newActive) {
          textarea.setAttribute("aria-activedescendant", newActive.id);
          newActive.setAttribute("aria-selected", true);
        } else {
          textarea.removeAttribute("aria-activedescendant");
        }
        active = newActive;
      }
    };
    const move = (decrement) => {
      if (decrement) activeIndex = activeIndex ? activeIndex - 1 : numOptions - 1;
      else activeIndex = activeIndex + 1 < numOptions ? activeIndex + 1 : 0;
      scrollActiveIntoView();
      updateActive();
    };
    const insertOption = (index) => insertCompletion(currentOptions[index][4], currentOptions[index][2], currentOptions[index][3]);
    const insertCompletion = self.insertCompletion = (completion, start, end = start) => {
      if (options.readOnly) return;
      let { label, tabStops = [], insert } = completion;
      let l = tabStops.length;
      tabStops = tabStops.map((stop) => stop + start);
      if (insert) {
        let indent = "\n" + getLineBefore(editor.value, pos).match(/\s*/)[0];
        let tab = options.insertSpaces == false ? "	" : " ".repeat(options.tabSize || 2);
        let temp = tabStops.slice();
        insert = insert.replace(/\n|	/g, (match, index) => {
          let replacement = match == "	" ? tab : indent;
          let diff = replacement.length - 1;
          let i = 0;
          while (i < l) {
            if (temp[i] > index + start) tabStops[i] += diff;
            i++;
          }
          return replacement;
        });
      } else insert = label;
      if (l % 2) tabStops[l] = tabStops[l - 1];
      insertText(editor, insert, start, end, tabStops[0], tabStops[1]);
      if (l > 2) {
        if (!stops) addOverlay(editor, tabStopsContainer);
        stops = tabStops;
        activeStop = 0;
        prevLength = editor.value.length;
        updateStops();
        currentSelection = getSelection();
      }
      cursor.scrollIntoView();
    };
    const moveActiveStop = (offset2) => {
      activeStop += offset2;
      setSelection(editor, stops[activeStop], stops[activeStop + 1]);
      tabStopsContainer.children[activeStop / 2].scrollIntoView({ block: "nearest" });
    };
    const clearStops = () => {
      tabStopsContainer.remove();
      stops = null;
    };
    const updateStops = () => {
      let sorted = [];
      let i = 0;
      for (; i < stops.length; ) sorted[i / 2] = [stops[i++], stops[i++]];
      sorted.sort((a, b) => a[0] - b[0]);
      updateMatched(tabStopsContainer, sorted.flat(), editor.value);
    };
    const startQuery = self.startQuery = (explicit) => {
      const [start, end, dir] = getSelection();
      const language = getLanguage(editor, pos = dir < "f" ? start : end);
      const definition = map[language];
      if (definition && (explicit || start == end) && !options.readOnly) {
        const value = editor.value;
        const lineBefore = getLineBefore(value, pos);
        const before = value.slice(0, pos);
        const context = {
          before,
          lineBefore,
          language,
          explicit: !!explicit,
          pos
        };
        const newContext = Object.assign(context, definition.context?.(context, editor));
        const filter = config.filter;
        currentOptions = [];
        definition.sources.forEach((source) => {
          const result = source(newContext, editor);
          if (result) {
            const from = result.from;
            const query = before.slice(from);
            result.options.forEach((option) => {
              const filterResult = filter(query, option.label);
              if (filterResult) {
                filterResult[0] += option.boost || 0;
                filterResult.push(from, result.to ?? end, option);
                currentOptions.push(filterResult);
              }
            });
          }
        });
        if (currentOptions[0]) {
          currentOptions.sort((a, b) => b[0] - a[0] || a[4].label.localeCompare(b[4].label));
          numOptions = currentOptions.length;
          activeIndex = offset = 0;
          for (let i = 0, l = numOptions < windowSize ? numOptions : windowSize; i < l; ) {
            updateRow(i++);
          }
          if (!isOpen) {
            const { clientHeight, clientWidth } = editor.container;
            const pos2 = cursor.getPosition();
            const max = Math.max(pos2.bottom, pos2.top);
            tooltip.style.width = `min(25em, ${clientWidth}px - var(--padding-left) - 1em)`;
            tooltip.style.maxHeight = `min(17em, ${max}px + .25em, ${clientHeight}px - 2em)`;
          }
          list.style.paddingTop = "";
          list.style.height = rowHeight ? rowHeight * numOptions + "px" : 1.4 * numOptions + "em";
          tooltip.scrollTop = 0;
          isOpen = true;
          show(config.preferAbove);
          textarea.setAttribute("aria-controls", id);
          textarea.setAttribute("aria-haspopup", "listbox");
          updateActive();
        } else hide();
      } else hide();
    };
    const addSelectionHandler = () => {
      if (!cursor && (cursor = editor.extensions.cursor)) {
        editor.on("selectionChange", (selection) => {
          if (stops && (selection[0] < stops[activeStop] || selection[1] > stops[activeStop + 1])) {
            clearStops();
          }
          if (shouldOpen) {
            shouldOpen = false;
            startQuery();
          } else hide();
          isTyping = false;
        });
      }
    };
    tabStopsContainer.className = "pce-tabstops";
    textarea.setAttribute("aria-autocomplete", "list");
    for (let i = 0; i < windowSize; ) {
      list.append(rowTemplate());
      rows[i].id = id + "-" + i++;
    }
    addListener(tooltip, "scroll", () => {
      setRowHeight();
      const newOffset = Math.min(Math.floor(tooltip.scrollTop / rowHeight), numOptions - windowSize);
      if (newOffset == offset || newOffset < 0) return;
      offset = newOffset;
      for (let i = 0; i < windowSize; i) {
        updateRow(i++);
      }
      list.style.paddingTop = offset * rowHeight + "px";
      updateActive();
    });
    editor.on("update", () => {
      addSelectionHandler();
      if (stops) {
        let value = editor.value;
        let diff = prevLength - (prevLength = value.length);
        let [start, end] = currentSelection;
        let i = 0;
        let l = stops.length;
        let activeStart = stops[activeStop];
        let activeEnd = stops[activeStop + 1];
        if (start < stops[activeStop] || end > activeEnd) {
          clearStops();
        } else {
          if (isDeleteForwards) end++;
          if (end <= activeEnd) stops[activeStop + 1] -= diff;
          if (end <= activeStart && diff > 0) stops[activeStop] -= diff;
          for (; i < l; i += 2) {
            if (i != activeStop && stops[i] >= activeEnd) {
              stops[i] = Math.max(stops[i] - diff, stops[activeStop + 1]);
              stops[i + 1] = Math.max(stops[i + 1] - diff, stops[activeStop + 1]);
            }
          }
          updateStops();
        }
        isDeleteForwards = false;
        currentSelection = getSelection();
      }
      shouldOpen = isTyping;
    });
    addListener(textarea, "mousedown", () => {
      if (stops) {
        setTimeout(() => {
          const [start, end] = getSelection();
          if (stops && (start < stops[activeStop] || end > stops[activeStop + 1])) {
            for (let i = 0, l = stops.length; i < stops.length; i += 2) {
              if (start >= stops[i] && end <= stops[i + 1]) {
                if (i + 3 > l) clearStops();
                else activeStop = i;
                break;
              }
            }
          }
        });
      }
    });
    addListener(
      textarea,
      "beforeinput",
      (e) => {
        let inputType = e.inputType;
        let isDelete = inputType[0] == "d";
        let isInsert = inputType == "insertText";
        let data = e.data;
        if (isOpen && isInsert && !prevSelection && data && !data[1] && currentOptions[activeIndex][4].commitChars?.includes(data)) {
          insertOption(activeIndex);
        }
        if (stops) {
          currentSelection = getSelection();
          isDeleteForwards = isDelete && inputType[13] == "F" && currentSelection[0] == currentSelection[1];
        }
        isTyping = !config.explicitOnly && (isTyping || isInsert && !prevSelection || isDelete && isOpen);
      },
      true
    );
    addListener(textarea, "blur", (e) => {
      if (config.closeOnBlur != false && !tooltip.contains(e.relatedTarget)) hide();
    });
    addListener(
      textarea,
      "keydown",
      (e) => {
        let key = e.key;
        let code = getModifierCode(e);
        let top;
        let height;
        let newActive;
        if (key == " " && code == 2) {
          addSelectionHandler();
          if (cursor) startQuery(true);
          preventDefault(e);
        } else if (isOpen) {
          if (!code) {
            if (/^Arrow[UD]/.test(key)) {
              move(key[5] == "U");
              preventDefault(e);
            } else if (key == "Tab" || key == "Enter") {
              insertOption(activeIndex);
              preventDefault(e);
            } else if (key == "Escape") {
              hide();
              preventDefault(e);
            } else if (key.slice(0, 4) == "Page") {
              setRowHeight();
              top = tooltip.scrollTop;
              height = tooltip.clientHeight;
              if (key[4] == "U") {
                newActive = Math.ceil(top / rowHeight);
                activeIndex = activeIndex == newActive || newActive - 1 == activeIndex ? Math.ceil(Math.max(0, (top - height) / rowHeight + 1)) : newActive;
              } else {
                top += height + 1;
                newActive = Math.ceil(top / rowHeight - 2);
                activeIndex = activeIndex == newActive || newActive + 1 == activeIndex ? Math.ceil(Math.min(numOptions - 1, (top + height) / rowHeight - 3)) : newActive;
              }
              scrollActiveIntoView();
              updateActive();
              preventDefault(e);
            }
          }
        } else if (stops) {
          if (!(code & 7) && key == "Tab") {
            if (!code) {
              moveActiveStop(2);
              if (activeStop + 3 > stops.length) clearStops();
              preventDefault(e);
            } else if (activeStop) {
              moveActiveStop(-2);
              preventDefault(e);
            }
          } else if (!code && key == "Escape") {
            clearStops();
            preventDefault(e);
          }
        }
      },
      true
    );
    addListener(list, "mousedown", (e) => {
      insertOption([].indexOf.call(rows, e.target.closest("li")) + offset);
      preventDefault(e);
    });
    addListener(tooltip, "focusout", (e) => {
      if (config.closeOnBlur != false && e.relatedTarget != textarea) hide();
    });
    editor.extensions.autoComplete = self;
  };
  self.startQuery = self.insertCompletion = () => {
  };
  return self;
};
export {
  autoComplete as a,
  completionsFromRecords as b,
  completeFromList as c,
  attrSnippet as d,
  findWords as f,
  optionsFromKeys as o,
  registerCompletions as r
};
//# sourceMappingURL=tooltip-Yare7kek.js.map
