import { l as languages, a as tokenize, w as withoutTokenizer, t as tokenizeText } from "../../index-C1_GGQ8y.js";
import { c as clone, i as insertBefore } from "../../language-gdIi4UL0.js";
import { a as replace, r as re } from "../../shared-Sq5P6lf6.js";
import "./markup.js";
var inner = ["(?:\\\\.|[^\\\\\n]|\n(?!\n))"];
var createInline = (pattern) => re(`((?:^|[^\\\\])(?:\\\\\\\\)*)(?:${pattern})`, inner, "g");
var tableCell = /(?:\\.|``(?:[^\n`]|`(?!`))+``|`[^\n`]+`|[^\\\n|`])+/;
var tableRow = replace("\\|?<0>(?:\\|<0>)+\\|?(?:\n|(?![\\s\\S]))", [tableCell.source]);
var tableLine = "\\|?[ 	]*:?-{3,}:?[ 	]*(?:\\|[ 	]*:?-{3,}:?[ 	]*)+\\|?\n";
var markdown = languages.md = languages.markdown = clone(languages.html);
insertBefore(markdown, "prolog", {
  "front-matter-block": {
    pattern: /(^(?:\s*\n)?)---(?!.)[^]*?\n---(?!.)/g,
    lookbehind: true,
    greedy: true,
    inside: {
      "punctuation": /^---|---$/,
      "front-matter": {
        pattern: /\S(?:[^]*\S)?/,
        alias: "language-yaml",
        inside: "yaml"
      }
    }
  },
  "blockquote": {
    // > ...
    pattern: /^>(?:[ 	]*>)*/m,
    alias: "punctuation"
  },
  "table": {
    pattern: RegExp("^" + tableRow + tableLine + "(?:" + tableRow + ")*", "m"),
    inside: {
      "table-header-row": {
        pattern: /^.+/,
        inside: {
          "table-header": {
            pattern: tableCell,
            alias: "important",
            inside: markdown
          },
          "punctuation": /\|/
        }
      },
      "table-data-rows": {
        pattern: /(.+\n)[^]+/,
        lookbehind: true,
        inside: {
          "table-data": {
            pattern: tableCell,
            inside: markdown
          },
          "punctuation": /\|/
        }
      },
      "table-line": {
        pattern: /.+/,
        inside: {
          "punctuation": /\S+/
        }
      }
    }
  },
  "code": [
    {
      // Prefixed by 4 spaces or 1 tab and preceded by an empty line
      pattern: /(^[ 	]*\n)(?:    |	).+(?:\n(?:    |	).+)*/m,
      lookbehind: true,
      alias: "keyword"
    },
    {
      // ```optional language
      // code block
      // ```
      pattern: /^(```+)[^`][^]*?^\1`*$/mg,
      greedy: true,
      inside: {
        "punctuation": /^`+|`+$/,
        "code-language": /^.+/,
        "code-block": /(?!^)[^]+(?=\n)/,
        [tokenize](code, grammar) {
          var tokens = withoutTokenizer(code, grammar);
          var language;
          if (tokens[5]) {
            language = (/[a-z][\w-]*/i.exec(
              tokens[1].content.replace(/\b#/g, "sharp").replace(/\b\+\+/g, "pp")
            ) || [""])[0].toLowerCase();
            tokens[3].alias = "language-" + language;
            if (grammar = languages[language]) {
              tokens[3].content = tokenizeText(tokens[3].content, grammar);
            }
          }
          return tokens;
        }
      }
    }
  ],
  "title": [
    {
      // title 1
      // =======
      // title 2
      // -------
      pattern: /\S.*\n(?:==+|--+)(?=[ 	]*$)/m,
      alias: "important",
      inside: {
        punctuation: /=+$|-+$/
      }
    },
    {
      // # title 1
      // ###### title 6
      pattern: /(^\s*)#.+/m,
      lookbehind: true,
      alias: "important",
      inside: {
        punctuation: /^#+|#+$/
      }
    }
  ],
  "hr": {
    // ***
    // ---
    // * * *
    // -----------
    pattern: /(^\s*)([*-])(?:[ 	]*\2){2,}(?=\s*$)/m,
    lookbehind: true,
    alias: "punctuation"
  },
  "list": {
    // * item
    // + item
    // - item
    // 1. item
    pattern: /(^\s*)(?:[*+-]|\d+\.)(?=[ 	].)/m,
    lookbehind: true,
    alias: "punctuation"
  },
  "url-reference": {
    // [id]: http://example.com "Optional title"
    // [id]: http://example.com 'Optional title'
    // [id]: http://example.com (Optional title)
    // [id]: <http://example.com> "Optional title"
    pattern: /!?\[[^\]]+\]:[ 	]+(?:\S+|<(?:\\.|[^\\>])+>)(?:[ 	]+(?:"(?:\\.|[^\\"])*"|'(?:\\.|[^\\'])*'|\((?:\\.|[^\\)])*\)))?/,
    inside: {
      "variable": {
        pattern: /^(!?\[)[^\]]+/,
        lookbehind: true
      },
      "string": /(?:"(?:\\.|[^\\"])*"|'(?:\\.|[^\\'])*'|\((?:\\.|[^\\)])*\))$/,
      "punctuation": /^[[\]!:]|<|>/
    },
    alias: "url"
  },
  "bold": {
    // **strong**
    // __strong__
    // allow one nested instance of italic text using the same delimiter
    pattern: createInline("\\b__(?:(?!_)<0>|_(?:(?!_)<0>)+_)+__\\b|\\*\\*(?:(?!\\*)<0>|\\*(?:(?!\\*)<0>)+\\*)+\\*\\*"),
    lookbehind: true,
    greedy: true,
    inside: {
      "content": {
        pattern: /(^..)[^]+(?=..)/,
        lookbehind: true,
        inside: {}
        // see below
      },
      "punctuation": /../
    }
  },
  "italic": {
    // *em*
    // _em_
    // allow one nested instance of bold text using the same delimiter
    pattern: createInline("\\b_(?:(?!_)<0>|__(?:(?!_)<0>)+__)+_\\b|\\*(?:(?!\\*)<0>|\\*\\*(?:(?!\\*)<0>)+\\*\\*)+\\*"),
    lookbehind: true,
    greedy: true,
    inside: {
      "content": {
        pattern: /(?!^)[^]+(?=.)/,
        inside: {}
        // see below
      },
      "punctuation": /./
    }
  },
  "strike": {
    // ~~strike through~~
    // ~strike~
    // eslint-disable-next-line regexp/strict
    pattern: createInline("(~~?)(?:(?!~)<0>)+\\2"),
    lookbehind: true,
    greedy: true,
    inside: {
      "punctuation": /^~~?|~~?$/,
      "content": {
        pattern: /[^]+/,
        inside: {}
        // see below
      }
    }
  },
  "code-snippet": {
    // `code`
    // ``code``
    pattern: /(^|[^\\`])(`+)[^\n`](?:|.*?[^\n`])\2(?!`)/g,
    lookbehind: true,
    greedy: true,
    alias: "code keyword"
  },
  "url": {
    // [example](http://example.com "Optional title")
    // [example][id]
    // [example] [id]
    pattern: createInline('!?\\[(?:(?!\\])<0>)+\\](?:\\([^\\s)]+(?:[ 	]+"(?:\\\\.|[^\\\\"])*")?\\)|[ 	]?\\[(?:(?!\\])<0>)+\\])'),
    lookbehind: true,
    greedy: true,
    inside: {
      "operator": /^!/,
      "content": {
        pattern: /(^\[)[^\]]+(?=\])/,
        lookbehind: true,
        inside: {}
        // see below
      },
      "variable": {
        pattern: /(^\][ 	]?\[)[^\]]+(?=\]$)/,
        lookbehind: true
      },
      "url": {
        pattern: /(^\]\()[^\s)]+/,
        lookbehind: true
      },
      "string": {
        pattern: /(^[ 	]+)"(?:\\.|[^\\"])*"(?=\)$)/,
        lookbehind: true
      },
      "markup-bracket": markdown["markup-bracket"]
    }
  }
});
["url", "bold", "italic", "strike"].forEach((token) => {
  ["url", "bold", "italic", "strike", "code-snippet", "markup-bracket"].forEach((inside) => {
    if (token != inside) {
      markdown[token].inside.content.inside[inside] = markdown[inside];
    }
  });
});
//# sourceMappingURL=markdown.js.map
