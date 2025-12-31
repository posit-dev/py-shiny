import { l as languages } from "../../index-C1_GGQ8y.js";
import { e as extend, i as insertBefore } from "../../language-gdIi4UL0.js";
import "./css.js";
var variable = /\$[-\w]+|#\{\$[-\w]+\}/;
var operator = {
  pattern: /[%/*+]|[!=]=|<=?|>=?|\b(?:and|not|or)\b|(\s)-(?!\S)/,
  lookbehind: true
};
var sass = languages.sass = extend("css", {
  // Sass comments don't need to be closed, only indented
  "comment": {
    pattern: /^([ 	]*)\/[/*].*(?:$\s*?\n\1[ 	]+\S.*)*/mg,
    lookbehind: true,
    greedy: true
  }
});
insertBefore(sass, "atrule", {
  // We want to consume the whole line
  "atrule-line": {
    // Includes support for = and + shortcuts
    pattern: /^(?:[ 	]*)[@+=].+/mg,
    greedy: true,
    inside: {
      "atrule": /(?:@[\w-]+|[+=])/
    }
  }
});
delete sass.atrule;
insertBefore(sass, "property", {
  // We want to consume the whole line
  "variable-line": {
    pattern: /^[ 	]*\$.+/mg,
    greedy: true,
    inside: {
      "punctuation": /:/,
      "variable": variable,
      "operator": operator
    }
  },
  // We want to consume the whole line
  "property-line": {
    pattern: /^[ 	]*(?:[^:\s]+ *:.*|:[^:\s].*)/mg,
    greedy: true,
    inside: {
      "property": [
        /[^:\s]+(?=\s*:)/,
        {
          pattern: /(:)[^:\s]+/,
          lookbehind: true
        }
      ],
      "punctuation": /:/,
      "variable": variable,
      "operator": operator,
      "important": sass.important
    }
  }
});
delete sass.property;
delete sass.important;
insertBefore(sass, "punctuation", {
  "selector": {
    pattern: /^([ 	]*)\S(?:,[^\n,]+|[^\n,]*)(?:,[^\n,]+)*(?:,\n\1[ 	]+\S(?:,[^\n,]+|[^\n,]*)(?:,[^\n,]+)*)*/mg,
    lookbehind: true,
    greedy: true
  }
});
//# sourceMappingURL=sass.js.map
