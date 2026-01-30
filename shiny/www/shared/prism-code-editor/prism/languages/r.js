import { l as languages } from "../../index-C1_GGQ8y.js";
languages.r = {
  "comment": /#.*/,
  "string": {
    pattern: /(["'])(?:\\.|(?!\1)[^\\\n])*\1/g,
    greedy: true
  },
  "percent-operator": {
    // Includes user-defined operators
    // and %%, %*%, %/%, %in%, %o%, %x%
    pattern: /%[^%\s]*%/,
    alias: "operator"
  },
  "boolean": /\b(?:FALSE|TRUE)\b/,
  "ellipsis": /\.\.(?:\.|\d+)/,
  "number": [
    /\b(?:Inf|NaN)\b/,
    /(?:\b0x[a-fA-F\d]+(?:\.\d*)?|\b\d+(?:\.\d*)?|\B\.\d+)(?:[EePp][+-]?\d+)?[iL]?/
  ],
  "keyword": /\b(?:NA|NA_character_|NA_complex_|NA_integer_|NA_real_|NULL|break|else|for|function|if|in|next|repeat|while)\b/,
  "operator": /->>?|<=|<<?-|[!=<>]=?|::?|&&?|\|\|?|[~^$@/*+-]/,
  "punctuation": /[()[\]{},;]/
};
//# sourceMappingURL=r.js.map
