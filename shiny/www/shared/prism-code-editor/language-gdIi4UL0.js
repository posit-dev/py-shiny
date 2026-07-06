import { r as rest, a as tokenize, l as languages } from "./index-C1_GGQ8y.js";
var _clone = (o, visited) => {
  if (visited.has(o)) return visited.get(o);
  var copy = o, t = toString.call(o).slice(8, -1);
  if (t == "Object") {
    visited.set(o, copy = {});
    for (var key in o) {
      copy[key] = _clone(o[key], visited);
    }
    if (o[rest]) copy[rest] = _clone(o[rest], visited);
    if (o[tokenize]) copy[tokenize] = o[tokenize];
  } else if (t == "Array") {
    visited.set(o, copy = []);
    for (var i = 0, l = o.length; i < l; i++) {
      copy[i] = _clone(o[i], visited);
    }
  }
  return copy;
};
var clone = (o) => _clone(o, /* @__PURE__ */ new Map());
var extend = (id, redef) => Object.assign(clone(languages[id]), redef);
var insertBefore = (grammar, before, insert) => {
  var temp = {};
  for (var token in grammar) {
    temp[token] = grammar[token];
    delete grammar[token];
  }
  for (var token in temp) {
    if (token == before) Object.assign(grammar, insert);
    if (!insert.hasOwnProperty(token)) {
      grammar[token] = temp[token];
    }
  }
};
var toString = {}.toString;
export {
  clone as c,
  extend as e,
  insertBefore as i
};
//# sourceMappingURL=language-gdIi4UL0.js.map
