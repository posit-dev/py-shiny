import { l as languages } from "../../index-C1_GGQ8y.js";
import { a as replace, r as re } from "../../shared-Sq5P6lf6.js";
var spaceAfterBackSlash = "\\\\\n(?:\\s|\\\\\n|#.*(?!.))*(?![\\s#]|\\\\\n)";
var space = replace("(?:[ 	]+(?![ 	])<0>?|<0>)", [spaceAfterBackSlash]);
var string = /"(?:\\[^]|[^\\\n"])*"|'(?:\\[^]|[^\\\n'])*'/g;
var stringSrc = string.source;
var option = replace(`--[\\w-]+=(?:<0>|(?!["'])(?:\\\\.|[^\\\\\\s])+)`, [stringSrc]);
var stringRule = {
  pattern: string,
  greedy: true
};
var commentRule = {
  pattern: /(^[ 	]*)#.*/mg,
  lookbehind: true,
  greedy: true
};
languages.dockerfile = languages.docker = {
  "instruction": {
    pattern: /(^[ 	]*)(?:add|arg|cmd|copy|entrypoint|env|expose|from|healthcheck|label|maintainer|onbuild|run|shell|stopsignal|user|volume|workdir)(?=\s)(?:\\.|[^\\\n])*(?:\\$(?:\s|#.*$)*(?![\s#])(?:\\.|[^\\\n])*)*/img,
    lookbehind: true,
    greedy: true,
    inside: {
      "options": {
        pattern: re("(^(?:onbuild<0>)?\\w+<0>)<1>(?:<0><1>)*", [space, option], "gi"),
        lookbehind: true,
        greedy: true,
        inside: {
          "property": {
            pattern: /(^|\s)--[\w-]+/,
            lookbehind: true
          },
          "string": [
            stringRule,
            {
              pattern: /(=)(?!["'])(?:\\.|[^\\\s])+/,
              lookbehind: true
            }
          ],
          "operator": /\\$/m,
          "punctuation": /=/
        }
      },
      "keyword": [
        {
          // https://docs.docker.com/engine/reference/builder/#healthcheck
          pattern: re("(^(?:onbuild<0>)?healthcheck<0>(?:<1><0>)*)(?:cmd|none)\\b", [space, option], "gi"),
          lookbehind: true,
          greedy: true
        },
        {
          // https://docs.docker.com/engine/reference/builder/#from
          pattern: re("(^(?:onbuild<0>)?from<0>(?:<1><0>)*(?!--)[^\\\\ 	]+<0>)as", [space, option], "gi"),
          lookbehind: true,
          greedy: true
        },
        {
          // https://docs.docker.com/engine/reference/builder/#onbuild
          pattern: re("(^onbuild<0>)\\w+", [space], "gi"),
          lookbehind: true,
          greedy: true
        },
        {
          pattern: /^\w+/g,
          greedy: true
        }
      ],
      "comment": commentRule,
      "string": stringRule,
      "variable": /\$(?:\w+|\{[^\\{}"']*\})/,
      "operator": /\\$/m
    }
  },
  "comment": commentRule
};
//# sourceMappingURL=docker.js.map
