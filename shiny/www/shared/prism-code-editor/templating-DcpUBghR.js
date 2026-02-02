import { w as withoutTokenizer, t as tokenizeText, b as resolve } from "./index-C1_GGQ8y.js";
var embeddedIn = (hostGrammar) => (code, templateGrammar) => {
  var host = resolve(hostGrammar);
  var hostCode = "";
  var tokenStack = [];
  var stackLength = 0;
  var templateTokens = withoutTokenizer(code, templateGrammar);
  var i = 0, l = templateTokens.length, position = 0;
  while (i < l) {
    var token = templateTokens[i++];
    var length = token.length;
    var type = token.type;
    if (type && type.slice(0, 6) != "ignore") {
      tokenStack[stackLength++] = [position, token];
      hostCode += " ".repeat(length);
    } else {
      hostCode += code.slice(position, position + length);
    }
    position += length;
  }
  var j = 0;
  var position = 0;
  var walkTokens = (tokens2) => {
    for (var i2 = 0; j < stackLength && i2 < tokens2.length; i2++) {
      var token2 = tokens2[i2];
      var content = token2.content;
      if (Array.isArray(content)) {
        walkTokens(content);
      } else {
        var length2 = token2.length;
        var replacement = [];
        var offset, t, k = 0;
        var pos = position;
        while ([offset, t] = tokenStack[j], offset >= position && offset < position + length2) {
          if (pos < offset) replacement[k++] = hostCode.slice(pos, offset);
          pos = offset + t.length;
          replacement[k++] = t;
          if (++j == stackLength) break;
        }
        position += length2;
        if (k) {
          if (pos < position) replacement[k++] = hostCode.slice(pos, position);
          if (content) {
            token2.content = replacement;
          } else {
            tokens2.splice(i2, 1, ...replacement);
            i2 += k - 1;
          }
        }
      }
    }
  };
  var tokens = host ? tokenizeText(hostCode, host) : [hostCode];
  walkTokens(tokens);
  return tokens;
};
export {
  embeddedIn as e
};
//# sourceMappingURL=templating-DcpUBghR.js.map
