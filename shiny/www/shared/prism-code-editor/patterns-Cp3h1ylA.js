var clikeComment = () => ({
  pattern: /\/\/.*|\/\*[^]*?(?:\*\/|$)/g,
  greedy: true
});
var clikeString = () => ({
  pattern: /(["'])(?:\\[^]|(?!\1)[^\\\n])*\1/g,
  greedy: true
});
var clikeNumber = /\b0x[a-f\d]+\b|(?:\b\d+(?:\.\d*)?|\B\.\d+)(?:e[+-]?\d+)?/i;
var clikePunctuation = /[()[\]{}.,:;]/;
var boolean = /\b(?:false|true)\b/;
export {
  clikeComment as a,
  boolean as b,
  clikeString as c,
  clikePunctuation as d,
  clikeNumber as e
};
//# sourceMappingURL=patterns-Cp3h1ylA.js.map
