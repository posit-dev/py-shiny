import { r as rest, l as languages } from "../../index-C1_GGQ8y.js";
import { b as boolean } from "../../patterns-Cp3h1ylA.js";
import { n as nested } from "../../shared-Sq5P6lf6.js";
var multilineComment = nested("/\\*(?:[^*/]|\\*(?!/)|/(?!\\*)|<self>)*\\*/", 2);
var string = {
  pattern: /b?"(?:\\[^]|[^\\"])*"|b?r(#*)"(?:[^"]|"(?!\1))*"\1/g,
  greedy: true
};
var paramsInside = {
  "closure-punctuation": {
    pattern: /^\||\|$/,
    alias: "punctuation"
  }
};
paramsInside[rest] = languages.rust = {
  "comment": {
    pattern: RegExp("//.*|" + multilineComment, "g"),
    greedy: true
  },
  "string": string,
  "char": {
    pattern: /b?'(?:\\(?:x[0-7][a-fA-F\d]|u\{(?:[a-fA-F\d]_*){1,6}\}|.)|[^\\\n	'])'/g,
    greedy: true
  },
  "attribute": {
    pattern: /#!?\[(?:[^[\]"]|"(?:\\[^]|[^\\"])*")*\]/g,
    greedy: true,
    alias: "attr-name",
    inside: {
      "string": string
    }
  },
  // Closure params should not be confused with bitwise OR |
  "closure-params": {
    pattern: /([=(,:]\s*|\bmove\s*)\|[^|]*\||\|[^|]*\|(?=\s*(?:\{|->))/g,
    lookbehind: true,
    greedy: true,
    inside: paramsInside
  },
  "lifetime-annotation": {
    pattern: /'\w+/,
    alias: "symbol"
  },
  "fragment-specifier": {
    pattern: /(\$\w+:)[a-z]+/,
    lookbehind: true,
    alias: "punctuation"
  },
  "variable": /\$\w+/,
  "function-definition": {
    pattern: /(\bfn\s+)\w+/,
    lookbehind: true,
    alias: "function"
  },
  "type-definition": {
    pattern: /(\b(?:enum|struct|trait|type|union)\s+)\w+/,
    lookbehind: true,
    alias: "class-name"
  },
  "module-declaration": [
    {
      pattern: /(\b(?:crate|mod)\s+)[a-z][a-z_\d]*/,
      lookbehind: true,
      alias: "namespace"
    },
    {
      pattern: /(\b(?:crate|self|super)\s*)::\s*[a-z][a-z_\d]*\b(?:\s*::(?:\s*[a-z][a-z_\d]*\s*::)*)?/,
      lookbehind: true,
      alias: "namespace",
      inside: {
        "punctuation": /::/
      }
    }
  ],
  // https://github.com/rust-lang/reference/blob/master/src/keywords.md
  // primitives and str
  // https://doc.rust-lang.org/stable/rust-by-example/primitives.html
  "keyword": /\b(?:Self|abstract|as|async|await|become|box|break|const|continue|crate|do|dyn|else|enum|extern|final|fn|for|if|impl|in|let|loop|macro|match|mod|move|mut|override|priv|pub|ref|return|self|static|struct|super|trait|try|type|typeof|union|unsafe|unsized|use|virtual|where|while|yield|bool|char|f(?:32|64)|[ui](?:8|16|32|64|128|size)|str)\b/,
  // functions can technically start with an upper-case letter, but this will introduce a lot of false positives
  // and Rust's naming conventions recommend snake_case anyway.
  // https://doc.rust-lang.org/1.0.0/style/style/naming/README.html
  "function": /\b[a-z_]\w*(?=\s*(?:::\s*<|\())/,
  "macro": {
    pattern: /\b\w+!/,
    alias: "property"
  },
  "constant": /\b[A-Z_][A-Z_\d]+\b/,
  "class-name": /\b[A-Z]\w*\b/,
  "namespace": {
    pattern: /(?:\b[a-z][a-z_\d]*\s*::\s*)*\b[a-z][a-z_\d]*\s*::(?!\s*<)/,
    inside: {
      "punctuation": /::/
    }
  },
  // Hex, oct, bin, dec numbers with visual separators and type suffix
  "number": /\b(?:0x[a-fA-F\d](?:_?[a-fA-F\d])*|0o[0-7](?:_?[0-7])*|0b[01](?:_?[01])*|(?:(?:\d(?:_?\d)*)?\.)?\d(?:_?\d)*(?:[Ee][+-]?\d+)?)(?:_?(?:f32|f64|[iu](?:8|16|32|64|size)?))?\b/,
  "boolean": boolean,
  "punctuation": /->|\.\.=|\.{1,3}|::|[()[\]{},:;]/,
  "operator": /&&|\|\||=>|>>=?|<<=?|[%&|^!=<>/*+-]=?|[@?]/
};
//# sourceMappingURL=rust.js.map
