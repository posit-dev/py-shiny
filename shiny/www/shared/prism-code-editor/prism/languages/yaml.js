import { l as languages } from "../../index-C1_GGQ8y.js";
import { a as replace, r as re } from "../../shared-Sq5P6lf6.js";
var anchorOrAlias = /[*&][^\s[\]{},]+/;
var tag = /!(?:<[\w%#;/?:@&=$,.!~*'()[\]+-]+>|(?:[a-zA-Z\d-]*!)?[\w%#;/?:@&=$.~*'()+-]+)?/;
var properties = `(?:${tag.source}(?:[ 	]+${anchorOrAlias.source})?|${anchorOrAlias.source}(?:[ 	]+${tag.source})?)`;
var plainKey = replace(
  "(?:[^\\s\0-\\x08\\x0e-\\x1f!\"#%&'*,:>?@[\\]{}`|\\x7f-\\x84\\x86-\\x9f\\ud800-\\udfff\\ufffe\\uffff-]|[?:-]<0>)(?:[ 	]*(?:(?![#:])<0>|:<0>))*",
  ["[^\\s\0-\\x08\\x0e-\\x1f,[\\]{}\\x7f-\\x84\\x86-\\x9f\\ud800-\\udfff\\ufffe\\uffff]"]
);
var string = `"(?:\\\\.|[^\\\\
"])*"|'(?:\\\\.|[^\\\\
'])*'`;
var createValuePattern = (value, flags) => re(
  "([:,[{-]\\s*(?:\\s<0>[ 	]+)?)<1>(?=[ 	]*(?:$|,|\\]|\\}|(?:\n\\s*)?#))",
  [properties, value],
  flags
);
languages.yml = languages.yaml = {
  "scalar": {
    pattern: re("([:-]\\s*(?:\\s<0>[ 	]+)?[|>])[ 	]*(?:(\n[ 	]+)\\S.*(?:\\2.+)*)", [properties]),
    lookbehind: true,
    alias: "string"
  },
  "comment": /#.*/,
  "key": {
    pattern: re(
      "((?:^|[:,[{\n?-])[ 	]*(?:<0>[ 	]+)?)<1>(?=\\s*:\\s)",
      [properties, "(?:" + plainKey + "|" + string + ")"],
      "g"
    ),
    lookbehind: true,
    greedy: true,
    alias: "atrule"
  },
  "directive": {
    pattern: /(^[ 	]*)%.+/m,
    lookbehind: true,
    alias: "important"
  },
  "datetime": {
    pattern: createValuePattern("\\d{4}-\\d\\d?-\\d\\d?(?:[tT]|[ 	]+)\\d\\d?:\\d\\d:\\d\\d(?:\\.\\d*)?(?:[ 	]*(?:Z|[+-]\\d\\d?(?::\\d\\d)?))?|\\d{4}-\\d\\d-\\d\\d|\\d\\d?:\\d\\d(?::\\d\\d(?:\\.\\d*)?)?", "m"),
    lookbehind: true,
    alias: "number"
  },
  "boolean": {
    pattern: createValuePattern("false|true", "im"),
    lookbehind: true,
    alias: "important"
  },
  "null": {
    pattern: createValuePattern("null|~", "im"),
    lookbehind: true,
    alias: "important"
  },
  "string": {
    pattern: createValuePattern(string, "mg"),
    lookbehind: true,
    greedy: true
  },
  "number": {
    pattern: createValuePattern("[+-]?(?:0x[a-f\\d]+|0o[0-7]+|(?:\\d+(?:\\.\\d*)?|\\.\\d+)(?:e[+-]?\\d+)?|\\.inf|\\.nan)", "im"),
    lookbehind: true
  },
  "tag": tag,
  "important": anchorOrAlias,
  "punctuation": /---|[:[\]{},|>?-]|\.{3}/
};
//# sourceMappingURL=yaml.js.map
