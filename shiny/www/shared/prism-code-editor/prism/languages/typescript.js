import { l as languages } from "../../index-C1_GGQ8y.js";
import { e as extend, i as insertBefore } from "../../language-gdIi4UL0.js";
import "./javascript.js";
var className = {
  pattern: /(\b(?:class|extends|implements|instanceof|interface|new|type)\s+)(?!keyof\b)(?!\d)(?:(?!\s)[$\w\xa0-\uffff])+(?:\s*<(?:[^<>]|<(?:[^<>]|<[^<>]*>)*>)*>)?/g,
  lookbehind: true,
  greedy: true
};
var ts = languages.ts = languages.typescript = extend("js", {
  "class-name": className
});
insertBefore(ts, "operator", {
  "builtin": /\b(?:Array|Function|Promise|any|boolean|never|number|string|symbol|unknown)\b/
});
ts.keyword.push(
  /\b(?:abstract|declare|is|keyof|readonly|require)\b|\b(?:asserts|infer|interface|module|namespace|type)\b(?!\s*[^\s{_$a-zA-Z\xa0-\uffff])|\btype(?=\s*\*)/
);
delete ts["parameter"];
delete ts["literal-property"];
var typeInside = className.inside = Object.assign({}, ts);
delete typeInside["class-name"];
delete typeInside["maybe-class-name"];
insertBefore(ts, "function", {
  "decorator": {
    pattern: /@[$\w\xa0-\uffff]+/,
    inside: {
      "at": {
        pattern: /^@/,
        alias: "operator"
      },
      "function": /.+/
    }
  },
  "generic-function": {
    // e.g. foo<T extends "bar" | "baz">( ...
    pattern: /#?(?!\d)(?:(?!\s)[$\w\xa0-\uffff])+\s*<(?:[^<>=]|=[^<]|=?<(?:[^<>]|<[^<>]*>)*>)*>(?=\s*\()/g,
    greedy: true,
    inside: {
      "generic": {
        pattern: /<[^]+/,
        // everything after the first <
        alias: "class-name",
        inside: typeInside
      },
      "function": /\S+/
    }
  }
});
//# sourceMappingURL=typescript.js.map
