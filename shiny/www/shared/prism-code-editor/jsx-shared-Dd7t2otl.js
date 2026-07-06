import { l as languages, a as tokenize, w as withoutTokenizer, T as Token } from "./index-C1_GGQ8y.js";
import { i as insertBefore, c as clone } from "./language-gdIi4UL0.js";
import { r as re } from "./shared-Sq5P6lf6.js";
var space = "\\s|//.*(?!.)|/\\*(?:[^*]|\\*(?!/))*\\*/";
var braces = "\\{(?:[^{}]|\\{(?:[^{}]|\\{(?:[^{}]|\\{[^}]*\\})*\\})*\\})*\\}";
var isText = (token) => token && (!token.type || token.type == "plain-text");
var tokenizer = (code, grammar) => {
  var position = 0, tokens = withoutTokenizer(code, grammar);
  var i = 0, openedTags = [], l = 0;
  for (; i < tokens.length; i++, position += length) {
    var token = tokens[i];
    var length = token.length;
    var type = token.type;
    var notTagNorBrace = !type;
    var last, tag, start, plainText, content;
    if (type) {
      content = token.content;
      if (type == "tag") {
        start = content[0].length;
        tag = content[2] ? code.substr(position + start, content[1].length) : "";
        if (start > 1) {
          if (l && openedTags[l - 1][0] == tag) {
            l--;
          }
        } else {
          if (content[content.length - 1].length < 2) {
            openedTags[l++] = [tag, 0];
          }
        }
      } else if (l && type == "punctuation") {
        last = openedTags[l - 1];
        if (content == "{") last[1]++;
        else if (last[1] && content == "}") last[1]--;
        else {
          notTagNorBrace = !"}()[]".includes(content);
        }
      } else {
        notTagNorBrace = true;
      }
    }
    if (notTagNorBrace && l && !openedTags[l - 1][1]) {
      start = position;
      if (isText(tokens[i + 1])) {
        length += tokens[i + 1].length;
        tokens.splice(i + 1, 1);
      }
      if (isText(tokens[i - 1])) {
        start -= tokens[--i].length;
        tokens.splice(i, 1);
      }
      plainText = code.slice(start, position + length);
      tokens[i] = new Token("plain-text", plainText, plainText);
    }
  }
  return tokens;
};
var addJsxTag = (grammar, name) => {
  insertBefore(languages[name] = grammar = clone(grammar), "regex", {
    "tag": {
      pattern: re(
        `</?(?:(?!\\d)[^\\s%=<>/]+(?:<0>(?:<0>*(?:[^\\s{=<>/*]+(?:<0>*=<0>*(?!\\s)(?:"[^"]*"|'[^']*'|<1>)?|(?=[\\s/>]))|<1>))*)?<0>*/?)?>`,
        [space, braces],
        "g"
      ),
      greedy: true,
      inside: {
        "punctuation": /^<\/?|\/?>$/,
        "tag": {
          pattern: /^[^\s/<]+/,
          inside: {
            "namespace": /^[^:]+:/,
            "class-name": /^[A-Z]\w*(?:\.[A-Z]\w*)*$/
          }
        },
        "attr-value": {
          pattern: re(`(=<0>*)(?:"[^"]*"|'[^']*')`, [space]),
          lookbehind: true,
          inside: {
            "punctuation": /^["']|["']$/
          }
        },
        "expression": {
          pattern: RegExp(braces, "g"),
          greedy: true,
          alias: "language-" + name,
          inside: grammar
        },
        "comment": grammar["comment"],
        "attr-equals": /=/,
        "attr-name": {
          pattern: /\S+/,
          inside: {
            "namespace": /^[^:]+:/
          }
        }
      }
    }
  });
  grammar[tokenize] = tokenizer;
  return grammar;
};
export {
  addJsxTag as a,
  braces as b,
  space as s
};
//# sourceMappingURL=jsx-shared-Dd7t2otl.js.map
