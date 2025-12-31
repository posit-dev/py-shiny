import { c as createSearchAPI } from "./search-5POIiI4Y.js";
const highlightSelectionMatches = (caseSensitive, minLength = 1, maxLength = 200) => {
  const self = (editor) => {
    const searchAPI = self.api = createSearchAPI(editor);
    const container = searchAPI.container;
    container.style.zIndex = -1;
    container.className = "selection-matches";
    editor.on("selectionChange", ([start, end], value) => {
      value = editor.focused ? value.slice(start, end) : "";
      start += value.search(/\S/);
      value = value.trim();
      let l = value.length;
      searchAPI.search(
        minLength > l || l > maxLength ? "" : value,
        caseSensitive,
        false,
        false,
        void 0,
        (mStart, mEnd) => mStart > start || mEnd <= start
      );
    });
  };
  return self;
};
const highlightCurrentWord = (filter, includeHyphens) => {
  const self = (editor) => {
    let noHighlight = false;
    let searchAPI = self.api = createSearchAPI(editor);
    let container = searchAPI.container;
    container.style.zIndex = -1;
    container.className = "word-matches";
    editor.on("update", () => noHighlight = true);
    editor.on("selectionChange", ([start, end], value) => {
      if (start < end || !editor.focused || noHighlight) searchAPI.search("");
      else {
        let group = `[_$\\p{L}\\d${includeHyphens && includeHyphens(start) ? "-" : ""}]`;
        let before = value.slice(0, start).match(RegExp(group + "*$", "u"));
        let index = before.index;
        let word = before[0] + value.slice(start).match(RegExp("^" + group + "*", "u"))[0];
        searchAPI.search(
          /^-*(\d|$)/.test(word) || filter && !filter(index, index + word.length) ? "" : word,
          true,
          true,
          false,
          void 0,
          filter,
          RegExp(group + "{2}", "u")
        );
      }
      noHighlight = false;
    });
  };
  self.setFilter = (newFilter) => filter = newFilter;
  return self;
};
export {
  highlightCurrentWord as a,
  highlightSelectionMatches as h
};
//# sourceMappingURL=selection-CYI5EdcY.js.map
