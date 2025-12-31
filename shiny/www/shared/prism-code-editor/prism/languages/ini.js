import { l as languages } from "../../index-C1_GGQ8y.js";
languages.ini = {
  /**
   * The component mimics the behavior of the Win32 API parser.
   *
   * @see {@link https://github.com/PrismJS/prism/issues/2775#issuecomment-787477723}
   */
  "comment": {
    pattern: /(^[ \f	\v]*)[#;].*/m,
    lookbehind: true
  },
  "section": {
    pattern: /(^[ \f	\v]*)\[[^\n\]]*\]?/m,
    lookbehind: true,
    inside: {
      "section-name": {
        pattern: /(^\[[ \f	\v]*)[^ \f	\v\]]+(?:[ \f	\v]+[^ \f	\v\]]+)*/,
        lookbehind: true,
        alias: "selector"
      },
      "punctuation": /[[\]]/
    }
  },
  "key": {
    pattern: /(^[ \f	\v]*)[^ \f\n	\v=]+(?:[ \f	\v]+[^ \f\n	\v=]+)*(?=[ \f	\v]*=)/m,
    lookbehind: true,
    alias: "attr-name"
  },
  "value": {
    pattern: /(=[ \f	\v]*)[^ \f\n	\v]+(?:[ \f	\v]+[^ \f\n	\v]+)*/,
    lookbehind: true,
    alias: "attr-value",
    inside: {
      "inner-value": {
        pattern: /^(["']).+(?=\1$)/,
        lookbehind: true
      }
    }
  },
  "punctuation": /=/
};
//# sourceMappingURL=ini.js.map
