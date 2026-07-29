var plainTextGrammar = {};
var rest = Symbol();
var tokenize = Symbol();
var resolve = (id) => typeof id == "string" ? languages[id] : id;
var languages = {
  plain: plainTextGrammar,
  plaintext: plainTextGrammar,
  text: plainTextGrammar,
  txt: plainTextGrammar
};
var tokenizeText = (text, grammar) => (grammar[tokenize] || withoutTokenizer)(text, grammar);
var withoutTokenizer = (text, grammar) => {
  var startNode = [text];
  var restGrammar;
  var array = [], i = 0;
  while (restGrammar = resolve(grammar[rest])) {
    delete grammar[rest];
    Object.assign(grammar, restGrammar);
  }
  matchGrammar(text, grammar, startNode, 0);
  while (array[i++] = startNode[0], startNode = startNode[1]) ;
  return array;
};
var escapeHtml = (string, pattern, replacement) => {
  return string.replace(/&/g, "&amp;").replace(pattern, replacement);
};
var closingTag = "</span>";
var openingTags = "";
var closingTags = "";
var highlightTokens = (tokens) => {
  var str = "", l = tokens.length, i = 0;
  while (i < l) str += stringify(tokens[i++]);
  return str;
};
var stringify = (token) => {
  if (token instanceof Token) {
    var { type, alias, content } = token;
    var prevOpening = openingTags;
    var prevClosing = closingTags;
    var opening = `<span class="token ${type + (alias ? " " + alias : "") + (type == "keyword" && typeof content == "string" ? " keyword-" + content : "")}">`;
    closingTags += closingTag;
    openingTags += opening;
    var contentStr = stringify(content);
    openingTags = prevOpening;
    closingTags = prevClosing;
    return opening + contentStr + closingTag;
  }
  if (typeof token != "string") return highlightTokens(token);
  token = escapeHtml(token, /</g, "&lt;");
  if (closingTags && token.includes("\n")) {
    return token.replace(/\n/g, closingTags + "\n" + openingTags);
  }
  return token;
};
var highlightText = (text, ref) => highlightTokens(tokenizeText(text, resolve(ref)));
var matchGrammar = (text, grammar, startNode, startPos, rematch) => {
  for (var token in grammar) {
    if (grammar[token]) for (var j = 0, p = grammar[token], patterns = Array.isArray(p) ? p : [p]; j < patterns.length; ++j) {
      if (rematch && rematch[0] == token && rematch[1] == j) {
        return;
      }
      var patternObj = patterns[j];
      var pattern = patternObj.pattern || patternObj;
      var inside = resolve(patternObj.inside);
      var lookbehind = patternObj.lookbehind;
      var greedy = patternObj.greedy && pattern.global;
      var alias = patternObj.alias;
      for (var currentNode = startNode, pos = startPos; currentNode && (!rematch || pos < rematch[2]); pos += currentNode[0].length, currentNode = currentNode[1]) {
        var str = currentNode[0];
        var removeCount = 0;
        var match, lookbehindLength;
        if (str instanceof Token) {
          continue;
        }
        pattern.lastIndex = greedy ? pos : 0;
        match = pattern.exec(greedy ? text : str);
        if (!match && greedy) {
          break;
        }
        if (!(match && match[0])) {
          continue;
        }
        if (lookbehind && match[1]) {
          lookbehindLength = match[1].length;
          match.index += lookbehindLength;
          match[0] = match[0].slice(lookbehindLength);
        }
        if (greedy) {
          for (var from = match.index, to = from + match[0].length, l; from >= pos + (l = currentNode[0].length); currentNode = currentNode[1], pos += l) ;
          if (currentNode[0] instanceof Token) {
            continue;
          }
          for (var k = currentNode, p = pos; (p += k[0].length) < to; k = k[1], removeCount++) ;
          str = text.slice(pos, p);
          match.index -= pos;
        }
        var from = match.index;
        var matchStr = match[0];
        var after = str.slice(from + matchStr.length);
        var reach = pos + str.length;
        var newToken = new Token(token, inside ? tokenizeText(matchStr, inside) : matchStr, matchStr, alias);
        var next = currentNode, i = 0;
        var nestedRematch;
        while (next = next[1], i++ < removeCount) ;
        if (after) {
          if (!next || next[0] instanceof Token) next = [after, next];
          else next[0] = after + next[0];
        }
        pos += from;
        currentNode[0] = from ? str.slice(0, from) : newToken;
        if (from) currentNode = currentNode[1] = [newToken, next];
        else currentNode[1] = next;
        if (removeCount) {
          matchGrammar(text, grammar, currentNode, pos, nestedRematch = [token, j, reach]);
          reach = nestedRematch[2];
        }
        if (rematch && reach > rematch[2]) rematch[2] = reach;
      }
    }
  }
};
function Token(type, content, matchedStr, alias) {
  this.type = type;
  this.content = content;
  this.alias = alias;
  this.length = matchedStr.length;
}
export {
  Token as T,
  tokenize as a,
  resolve as b,
  highlightText as c,
  escapeHtml as e,
  highlightTokens as h,
  languages as l,
  rest as r,
  tokenizeText as t,
  withoutTokenizer as w
};
//# sourceMappingURL=index-C1_GGQ8y.js.map
