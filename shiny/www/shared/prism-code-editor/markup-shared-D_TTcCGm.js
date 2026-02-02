import { a as tokenize, w as withoutTokenizer } from "./index-C1_GGQ8y.js";
import { b as braces } from "./jsx-shared-Dd7t2otl.js";
import { r as re } from "./shared-Sq5P6lf6.js";
var addInlined = (tagName, tagInside, getLang) => ({
  pattern: RegExp(`<${tagName}(?:\\s[^>]*)?>[^]*?</${tagName}\\s*>`, "g"),
  greedy: true,
  inside: {
    "code-block": {
      pattern: /(>)[^]+(?=<)/,
      lookbehind: true
    },
    "tag": {
      pattern: /[^>]+>/,
      inside: tagInside
    },
    [tokenize]: (code, grammar) => {
      grammar["code-block"].alias = "language-" + (grammar["code-block"].inside = getLang(code));
      return withoutTokenizer(code, grammar);
    }
  }
});
var astroTag = (expression) => ({
  pattern: re(
    `</?(?:(?!\\d)[^\\s%=<>/]+(?:\\s(?:\\s*[^\\s{=<>/]+(?:\\s*=\\s*(?!\\s)(?:"[^"]*"|'[^']*'|[^\\s{=<>/"']+(?=[\\s/>])|<0>)?|(?=[\\s/>]))|\\s*<0>)*)?\\s*/?)?>`,
    [braces],
    "g"
  ),
  greedy: true,
  inside: {
    "punctuation": /^<\/?|\/?>$/,
    "tag": {
      pattern: /^\S+/,
      inside: {
        "namespace": /^[^:]+:/,
        "class-name": /^[A-Z]\w*(?:\.[A-Z]\w*)*$/
      }
    },
    "attr-value": {
      pattern: /(=\s*)(?:"[^"]*"|'[^']*'|[^\s>{]+)/,
      lookbehind: true,
      inside: {
        "punctuation": /^["']|["']$/
      }
    },
    "expression": expression,
    "attr-equals": /=/,
    "attr-name": {
      pattern: /\S+/,
      inside: {
        "namespace": /^[^:]+:/
      }
    }
  }
});
export {
  astroTag as a,
  addInlined as b
};
//# sourceMappingURL=markup-shared-D_TTcCGm.js.map
