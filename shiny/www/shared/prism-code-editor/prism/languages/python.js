import { r as rest, l as languages } from "../../index-C1_GGQ8y.js";
import { d as clikePunctuation } from "../../patterns-Cp3h1ylA.js";
var inside = {
  "format-spec": {
    pattern: /(:)[^(){}:]+(?=\}$)/,
    lookbehind: true
  },
  "conversion-option": {
    pattern: /![sra](?=[:}]$)/,
    alias: "punctuation"
  }
};
inside[rest] = languages.py = languages.python = {
  "comment": {
    pattern: /#.*/g,
    greedy: true
  },
  "string-interpolation": {
    pattern: /(?:fr?|rf)(?:("""|''')[^]*?\1|(["'])(?:\\[^]|(?!\2)[^\\\n])*\2)/gi,
    greedy: true,
    inside: {
      "interpolation": {
        // "{" <expression> <optional "!s", "!r", or "!a"> <optional ":" format specifier> "}"
        pattern: /((?:^|[^{])(?:\{\{)*)\{(?!\{)(?:[^{}]|\{(?:[^{}]|\{[^}]*\})*\})*\}/,
        lookbehind: true,
        inside
      },
      "string": /[^]+/
    }
  },
  "triple-quoted-string": {
    pattern: /(?:br?|rb?|u)?("""|''')[^]*?\1/gi,
    greedy: true,
    alias: "string"
  },
  "string": {
    pattern: /(?:br?|rb?|u)?(["'])(?:\\[^]|(?!\1)[^\\\n])*\1/gi,
    greedy: true
  },
  "function": {
    pattern: /((?:^|\s)def[ 	]+)(?!\d)\w+(?=\s*\()/,
    lookbehind: true
  },
  "class-name": {
    pattern: /(\bclass\s+)\w+/i,
    lookbehind: true
  },
  "decorator": {
    pattern: /(^[ 	]*)@\w+(?:\.\w+)*/m,
    lookbehind: true,
    alias: "annotation punctuation",
    inside: {
      "punctuation": /\./
    }
  },
  "keyword": /\b(?:_(?=\s*:)|and|as|assert|async|await|break|case|class|continue|de[fl]|elif|else|except|exec|finally|f?or|from|global|i[fns]|import|lambda|match|nonlocal|not|pass|print|raise|return|try|while|with|yield)\b/,
  "builtin": /\b(?:__import__|abs|all|any|apply|ascii|basestring|bin|bool|buffer|bytearray|bytes|callable|chr|classmethod|cmp|coerce|compile|complex|delattr|dict|dir|divmod|enumerate|eval|execfile|file|filter|float|format|frozenset|getattr|globals|hasattr|hash|help|hex|id|input|int|intern|isinstance|issubclass|iter|len|list|locals|long|ma[px]|memoryview|min|next|object|oct|open|ord|pow|property|raw_input|reduce|reload|repr|reversed|round|set|setattr|slice|sorted|staticmethod|str|sum|super|tuple|type|unichr|unicode|vars|x?range|zip)\b/,
  "boolean": /\b(?:False|True|None)\b/,
  "number": /\b0(?:b(?:_?[01])+|o(?:_?[0-7])+|x(?:_?[a-f\d])+)\b|(?:\b\d+(?:_\d+)*(?:\.(?:\d+(?:_\d+)*)?)?|\B\.\d+(?:_\d+)*)(?:e[+-]?\d+(?:_\d+)*)?j?(?!\w)/i,
  "operator": /!=|:=|\*\*=?|\/\/=?|<>|>>|<<|[%=<>/*+-]=?|[&|^~]/,
  "punctuation": clikePunctuation
};
//# sourceMappingURL=python.js.map
