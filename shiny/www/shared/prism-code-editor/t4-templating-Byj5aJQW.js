var createBlock = (prefix, insideLang) => ({
  pattern: RegExp(`<#${prefix}[^]*?#>`),
  alias: "block",
  inside: {
    "delimiter": {
      pattern: RegExp(`^<#${prefix}|#>$`),
      alias: "important"
    },
    "content": {
      pattern: /[^]+/,
      alias: typeof insideLang == "string" ? "language-" + insideLang : void 0,
      inside: insideLang
    }
  }
});
var createT4 = (insideLang) => ({
  "block": {
    pattern: /<#[^]+?#>/,
    inside: {
      "directive": createBlock("@", {
        "attr-value": {
          pattern: /=(?:(["'])(?:\\[^]|(?!\1)[^\\])*\1|[^\s"'=>]+)/,
          inside: {
            "punctuation": /^[="']|["']$/
          }
        },
        "keyword": /\b\w+(?=\s)/,
        "attr-name": /\w+/
      }),
      "expression": createBlock("=", insideLang),
      "class-feature": createBlock("\\+", insideLang),
      "standard": createBlock("", insideLang)
    }
  }
});
export {
  createT4 as c
};
//# sourceMappingURL=t4-templating-Byj5aJQW.js.map
