import { l as languages } from "../../index-C1_GGQ8y.js";
var funcPattern = /\\(?:[^a-z()[\]]|[a-z*]+)/i;
var insideEqu = {
  "equation-command": {
    pattern: funcPattern,
    alias: "regex"
  }
};
languages.context = languages.tex = languages.latex = {
  "comment": /%.*/,
  // the verbatim environment prints whitespace to the document
  "cdata": {
    pattern: /(\\begin\{((?:lstlisting|verbatim)\*?)\})(?!\\end\{\2\})[^]+?(?=\\end\{\2\})/,
    lookbehind: true
  },
  /*
   * equations can be between $$ $$ or $ $ or \( \) or \[ \]
   * (all are multiline)
   */
  "equation": [
    {
      pattern: /\$\$(?:\\[^]|[^\\$])+\$\$|\$(?:\\[^]|[^\\$])+\$|\\\([^]*?\\\)|\\\[[^]*?\\\]/,
      inside: insideEqu,
      alias: "string"
    },
    {
      pattern: /(\\begin\{((?:align|eqnarray|equation|gather|math|multline)\*?)\})(?!\\end\{\2\})[^]+?(?=\\end\{\2\})/,
      lookbehind: true,
      inside: insideEqu,
      alias: "string"
    }
  ],
  /*
   * arguments which are keywords or references are highlighted
   * as keywords
   */
  "keyword": {
    pattern: /(\\(?:begin|cite|documentclass|end|label|ref|usepackage)(?:\[[^\]]+\])?\{)[^}]+(?=\})/,
    lookbehind: true
  },
  "url": {
    pattern: /(\\url\{)[^}]+(?=\})/,
    lookbehind: true
  },
  /*
   * section or chapter headlines are highlighted as bold so that
   * they stand out more
   */
  "headline": {
    pattern: /(\\(?:chapter|frametitle|paragraph|part|section|subparagraph|subsection|subsubparagraph|subsubsection|subsubsubparagraph)\*?(?:\[[^\]]+\])?\{)[^}]+(?=\})/,
    lookbehind: true,
    alias: "class-name"
  },
  "function": {
    pattern: funcPattern,
    alias: "selector"
  },
  "punctuation": /[[\]{}&]/
};
//# sourceMappingURL=latex.js.map
