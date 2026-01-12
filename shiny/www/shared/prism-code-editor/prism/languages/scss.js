import { l as languages, r as rest } from "../../index-C1_GGQ8y.js";
import { e as extend, i as insertBefore } from "../../language-gdIi4UL0.js";
import { a as clikeComment, b as boolean } from "../../patterns-Cp3h1ylA.js";
import "./css.js";
var scss = languages.scss = extend("css", {
  "comment": clikeComment(),
  "atrule": {
    pattern: /@[\w-](?:\([^()]+\)|[^()\s]|\s+(?!\s))*?(?=\s+[{;])/,
    inside: {
      "rule": /@[\w-]+/,
      [rest]: "scss"
    }
  },
  // url, compassified
  "url": /(?:[-a-z]+-)?url(?=\()/i,
  // CSS selector regex is not appropriate for Sass
  // since there can be lot more things (var, @ directive, nesting..)
  // a selector must start at the end of a property or after a brace (end of other rules or nesting)
  // it can contain some characters that aren't used for defining rules or end of selector, & (parent selector), or interpolated variable
  // the end of a selector is found when there is no rules in it ( {} or {\s}) or if there is a property (because an interpolated var
  // can "pass" as a selector- e.g: proper#{$erty})
  // this one was hard to do, so please be careful if you edit this one :)
  "selector": {
    // Initial look-ahead is used to prevent matching of blank selectors
    pattern: /(?!\s)[^@;(){}]?(?:[^@;(){}\s]|\s+(?!\s)|#\{\$[-\w]+\})+(?=\s*\{(?:\}|\s|[^}][^:{}]*[:{][^}]))/,
    inside: {
      "parent": {
        pattern: /&/,
        alias: "important"
      },
      "placeholder": /%[-\w]+/,
      "variable": /\$[-\w]+|#\{\$[-\w]+\}/
    }
  },
  "property": {
    pattern: /(?:[-\w]|\$[-\w]|#\{\$[-\w]+\})+(?=\s*:)/,
    inside: {
      "variable": /\$[-\w]+|#\{\$[-\w]+\}/
    }
  }
});
insertBefore(scss, "atrule", {
  "keyword": [
    /@(?:content|debug|each|else(?: if)?|extend|for|forward|function|if|import|include|mixin|return|use|warn|while)\b/i,
    {
      pattern: /( )(?:from|through)(?= )/,
      lookbehind: true
    }
  ]
});
insertBefore(scss, "important", {
  // var and interpolated vars
  "variable": /\$[-\w]+|#\{\$[-\w]+\}/
});
insertBefore(scss, "function", {
  "module-modifier": {
    pattern: /\b(?:as|hide|show|with)\b/i,
    alias: "keyword"
  },
  "placeholder": {
    pattern: /%[-\w]+/,
    alias: "selector"
  },
  "statement": {
    pattern: /\B!(?:default|optional)\b/i,
    alias: "keyword"
  },
  "boolean": boolean,
  "null": {
    pattern: /\bnull\b/,
    alias: "keyword"
  },
  "operator": {
    pattern: /(\s)(?:[%/*+-]|[!=]=|[<>]=?|and|not|or)(?!\S)/,
    lookbehind: true
  }
});
//# sourceMappingURL=scss.js.map
