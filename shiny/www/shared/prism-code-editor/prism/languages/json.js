import { l as languages } from "../../index-C1_GGQ8y.js";
import { b as boolean, a as clikeComment } from "../../patterns-Cp3h1ylA.js";
languages.webmanifest = languages.json = {
  "property": {
    pattern: /"(?:\\.|[^\\\n"])*"(?=\s*:)/g,
    greedy: true
  },
  "string": {
    pattern: /"(?:\\.|[^\\\n"])*"/g,
    greedy: true
  },
  "comment": clikeComment(),
  "number": /-?\b\d+(?:\.\d+)?(?:e[+-]?\d+)?\b/i,
  "operator": /:/,
  "punctuation": /[[\]{},]/,
  "boolean": boolean,
  "null": {
    pattern: /\bnull\b/,
    alias: "keyword"
  }
};
//# sourceMappingURL=json.js.map
