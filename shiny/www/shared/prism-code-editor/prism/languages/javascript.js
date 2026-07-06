import { r as rest, l as languages } from "../../index-C1_GGQ8y.js";
import { b as boolean, c as clikeString, a as clikeComment } from "../../patterns-Cp3h1ylA.js";
var js = {};
languages.js = languages.javascript = Object.assign(js, {
  "doc-comment": {
    pattern: /\/\*\*(?!\/)[^]*?(?:\*\/|$)/g,
    greedy: true,
    alias: "comment",
    inside: "jsdoc"
  },
  "comment": clikeComment(),
  "hashbang": {
    pattern: /^#!.*/g,
    greedy: true,
    alias: "comment"
  },
  "template-string": {
    pattern: /`(?:\\[^]|\$\{(?:[^{}]|\{(?:[^{}]|\{[^}]*\})*\})*\}|(?!\$\{)[^\\`])*`/g,
    greedy: true,
    inside: {
      "template-punctuation": {
        pattern: /^`|`$/,
        alias: "string"
      },
      "interpolation": {
        pattern: /((?:^|[^\\])(?:\\\\)*)\$\{(?:[^{}]|\{(?:[^{}]|\{[^}]*\})*\})*\}/,
        lookbehind: true,
        inside: {
          "interpolation-punctuation": {
            pattern: /^\$\{|\}$/,
            alias: "punctuation"
          },
          [rest]: js
        }
      },
      "string": /[^]+/
    }
  },
  "string-property": {
    pattern: /((?:^|[,{])[ 	]*)(["'])(?:\\[^]|(?!\2)[^\\\n])*\2(?=\s*:)/mg,
    lookbehind: true,
    greedy: true,
    alias: "property"
  },
  "string": clikeString(),
  "regex": {
    pattern: /((?:^|[^$\w\xa0-\uffff"'`.)\]\s]|\b(?:return|yield))\s*)\/(?:(?:\[(?:\\.|[^\\\n\]])*\]|\\.|[^\\\n/[])+\/[dgimyus]{0,7}|(?:\[(?:\\.|[^\\\n[\]]|\[(?:\\.|[^\\\n[\]]|\[(?:\\.|[^\\\n[\]])*\])*\])*\]|\\.|[^\\\n/[])+\/[dgimyus]{0,7}v[dgimyus]{0,7})(?=(?:\s|\/\*(?:[^*]|\*(?!\/))*\*\/)*(?!\/\*|[^()[\]{}.,:;?`\n%&|^!=<>/*+-]))/g,
    lookbehind: true,
    greedy: true,
    inside: {
      "regex-flags": /\w+$/,
      "regex-delimiter": /^\/|\/$/,
      "regex-source": {
        pattern: /.+/,
        alias: "language-regex",
        inside: "regex"
      }
    }
  },
  "class-name": [
    {
      pattern: /(\b(?:class|extends|implements|instanceof|interface|new)\s+)(?!\d)(?:(?!\s)[$\w\xa0-\uffff.])+/,
      lookbehind: true,
      inside: {
        "punctuation": /\./
      }
    },
    {
      pattern: /(^|[^$\w\xa0-\uffff]|\s)(?![a-z\d])(?:(?!\s)[$\w\xa0-\uffff])+(?=\.(?:constructor|prototype)\b)/,
      lookbehind: true
    }
  ],
  // This must be declared before keyword because we use "function" inside the look-forward
  "function-variable": {
    pattern: /#?(?!\d)(?:(?!\s)[$\w\xa0-\uffff])+(?=\s*[=:]\s*(?:async\s*)?(?:\bfunction\b|(?:\((?:[^()]|\([^)]*\))*\)|(?!\d)(?:(?!\s)[$\w\xa0-\uffff])+)\s*=>))/,
    alias: "function",
    inside: {
      "maybe-class-name": /^[A-Z].*/
    }
  },
  "parameter": [
    /(function(?:\s+(?!\d)(?:(?!\s)[$\w\xa0-\uffff])+)?\s*\(\s*)(?!\s)(?:[^()\s]|\s+(?![\s)])|\([^()]*\))+(?=\s*\))/,
    /(^|[^$\w\xa0-\uffff]|\s)(?!\d)(?:(?!\s)[$\w\xa0-\uffff])+(?=\s*=>)/,
    /(\(\s*)(?!\s)(?:[^()\s]|\s+(?![\s)])|\([^()]*\))+(?=\s*\)\s*=>)/,
    /((?:\b|\s|^)(?!(?:as|async|await|break|case|catch|continue|default|do|else|finally|for|if|return|switch|throw|try|while|yield|class|const|debugger|delete|enum|extends|function|[gs]et|export|from|import|implements|in|instanceof|interface|let|new|null|of|package|private|protected|public|static|super|this|typeof|undefined|var|void|with)(?![$\w\xa0-\uffff]))(?:(?!\d)(?:(?!\s)[$\w\xa0-\uffff])+\s*)\(\s*|\]\s*\(\s*)(?!\s)(?:[^()\s]|\s+(?![\s)])|\([^()]*\))+(?=\s*\)\s*\{)/
  ].map((pattern) => ({
    pattern,
    lookbehind: true,
    inside: js
  })),
  "constant": /\b[A-Z](?:[A-Z_]|\dx?)*\b/,
  "keyword": [
    {
      pattern: /(^|[^.]|\.{3}\s*)\b(?:as|assert(?=\s*\{)|export|from(?!\s*[^\s"'])|import)\b/,
      alias: "module",
      lookbehind: true
    },
    {
      pattern: /(^|[^.]|\.{3}\s*)\b(?:await|break|case|catch|continue|default|do|else|finally|for|if|return|switch|throw|try|while|yield)\b/,
      alias: "control-flow",
      lookbehind: true
    },
    {
      pattern: /(^|[^.]|\.{3}\s*)\b(?:async(?!\s*[^\s($\w\xa0-\uffff])|class|const|debugger|delete|enum|extends|function|[gs]et(?!\s*[^\s#[$\w\xa0-\uffff])|implements|in|instanceof|interface|let|new|null|of|package|private|protected|public|static|super|this|typeof|undefined|var|void|with)\b/,
      lookbehind: true
    }
  ],
  "boolean": boolean,
  // Allow for all non-ASCII characters (See http://stackoverflow.com/a/2008444)
  "function": {
    pattern: /#?(?!\d)(?:(?!\s)[$\w\xa0-\uffff])+(?=\s*(?:\.\s*(?:apply|bind|call)\s*)?\()/,
    inside: {
      "maybe-class-name": /^[A-Z].*/
    }
  },
  "number": {
    pattern: /(^|[^$\w])(?:NaN|Infinity|0[bB][01]+(?:_[01]+)*n?|0[oO][0-7]+(?:_[0-7]+)*n?|0[xX][a-fA-F\d]+(?:_[a-fA-F\d]+)*n?|\d+(?:_\d+)*n|(?:\d+(?:_\d+)*(?:\.(?:\d+(?:_\d+)*)?)?|\.\d+(?:_\d+)*)(?:[Ee][+-]?\d+(?:_\d+)*)?)(?![$\w])/,
    lookbehind: true
  },
  "literal-property": {
    pattern: /([\n,{][ 	]*)(?!\d)(?:(?!\s)[$\w\xa0-\uffff])+(?=\s*:)/,
    lookbehind: true,
    alias: "property"
  },
  "operator": [
    {
      pattern: /=>/,
      alias: "arrow"
    },
    /--|\+\+|(?:\*\*|&&|\|\||[!=]=|>>>?|<<|[%&|^!=<>/*+-]|\?\?)=?|\.{3}|\?(?!\.)|~|:/
  ],
  "property-access": {
    pattern: /(\.\s*)#?(?!\d)(?:(?!\s)[$\w\xa0-\uffff])+/,
    lookbehind: true,
    inside: {
      "maybe-class-name": /^[A-Z].*/
    }
  },
  "maybe-class-name": {
    pattern: /(^|[^$\w\xa0-\uffff])[A-Z][$\w\xa0-\uffff]+/,
    lookbehind: true
  },
  "punctuation": /\?\.|[()[\]{}.,:;]/
});
//# sourceMappingURL=javascript.js.map
