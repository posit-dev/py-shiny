import { l as languageMap } from "./index-CKRNGLIi.js";
import { b as braces } from "./jsx-shared-Dd7t2otl.js";
import { r as re } from "./shared-Sq5P6lf6.js";
import { n as getClosestToken, e as getLineBefore, o as voidTags } from "./index-DYIRSLx1.js";
const clikeIndent = /[([{][^)\]}]*$|^[^.]*\b(?:case .+?|default):\s*$/;
const isBracketPair = /\[]|\(\)|{}/;
const xmlOpeningTag = /<(?![\d?!#@])([^\s/=>$<%]+)(?:\s(?:\s*[^\s/"'=>]+(?:\s*=\s*(?!\s)(?:"[^"]*"|'[^']*'|[^\s"'=>]+(?=[\s>]))?|(?=[\s/>])))+)?\s*>[ 	]*$/;
const xmlClosingTag = /^<\/(?!\d)[^\s/=>$<%]+\s*>/;
const openBracket = /[([{][^)\]}]*$/;
const astroOpeningTag = /* @__PURE__ */ re(
  `<(?:(?![\\d!])([^\\s%=<>/]+)(?:\\s(?:\\s*(?:[^\\s{=<>/]+(?:\\s*=\\s*(?!\\s)(?:"[^"]*"|'[^']*'|[^\\s{=<>/"']+(?=[\\s/>])|<0>)?|(?=[\\s/>]))|<0>))*)?\\s*)?>[ 	]*$`,
  [braces]
);
const testBracketPair = ([start, end], value) => {
  return isBracketPair.test(value[start - 1] + value[end]);
};
const clikeComment = {
  line: "//",
  block: ["/*", "*/"]
};
const isOpen = (match, voidTags2) => !!match && !voidTags2?.test(match[1]);
const htmlAutoIndent = (tagPattern, voidTags2) => [
  ([start], value) => isOpen(value.slice(0, start).match(tagPattern), voidTags2) || openBracket.test(getLineBefore(value, start)),
  (selection, value) => testBracketPair(selection, value) || isOpen(value.slice(0, selection[0]).match(tagPattern), voidTags2) && xmlClosingTag.test(value.slice(selection[1]))
];
const markupComment = {
  block: ["<!--", "-->"]
};
const markupLanguage = (comment = markupComment, tagPattern = xmlOpeningTag, voidTags2) => ({
  comments: comment,
  autoIndent: htmlAutoIndent(tagPattern, voidTags2),
  autoCloseTags: ([start, end], value, editor) => {
    return autoCloseTags(editor, start, end, value, tagPattern, voidTags2);
  }
});
const autoCloseTags = (editor, start, end, value, tagPattern, voidTags2) => {
  if (start == end) {
    let match = tagPattern.exec(value.slice(0, start) + ">");
    let tagMatcher = editor.extensions.matchTags;
    if (match && (match = match[1] || "", !voidTags2?.test(match))) {
      if (tagMatcher) {
        let { pairs, tags } = tagMatcher;
        for (let i = tags.length; i; ) {
          let tag = tags[--i];
          if (tag[1] >= start && tag[4] && tag[5] && tag[3] == match && pairs[i] == null) {
            return;
          }
        }
      }
      return `</${match}>`;
    }
  }
};
const bracketIndenting = (comments = clikeComment, indentPattern = openBracket) => ({
  comments,
  autoIndent: [
    ([start], value) => indentPattern.test(getLineBefore(value, start)),
    testBracketPair
  ]
});
const markupTemplateLang = (name, comments) => languageMap[name] = {
  comments,
  autoIndent: htmlAutoIndent(xmlOpeningTag, voidTags),
  autoCloseTags: ([start, end], value, editor) => {
    return getClosestToken(editor, "." + name, 0, 0, start) ? "" : autoCloseTags(editor, start, end, value, xmlOpeningTag, voidTags);
  }
};
export {
  clikeIndent as a,
  bracketIndenting as b,
  clikeComment as c,
  astroOpeningTag as d,
  markupComment as e,
  autoCloseTags as f,
  markupTemplateLang as g,
  htmlAutoIndent as h,
  markupLanguage as m,
  testBracketPair as t,
  xmlOpeningTag as x
};
//# sourceMappingURL=index-BZh6eCR8.js.map
