import { l as languages } from "../../index-C1_GGQ8y.js";
languages.sql = {
  "comment": /\/\*[^]*?\*\/|(?:--|\/\/|#).*/,
  "variable": [
    {
      pattern: /@(["'`])(?:\\[^]|(?!\1)[^\\])+\1/g,
      greedy: true
    },
    /@[\w.$]+/
  ],
  "string": {
    pattern: /(^|[^\\@])(["'])(?:\\[^]|(?!\2)[^\\]|\2\2)*\2/g,
    lookbehind: true,
    greedy: true
  },
  "identifier": {
    pattern: /(^|[^\\@])`(?:\\[^]|[^\\`]|``)*`/g,
    lookbehind: true,
    greedy: true,
    inside: {
      "punctuation": /^`|`$/
    }
  },
  "function": /\b(?:avg|count|first|format|last|[lu]case|len|max|mi[dn]|mod|now|round|sum)(?=\s*\()/i,
  // Should we highlight user defined functions too?
  "keyword": /\b(?:action|add|after|algorithm|alter|analyze|any|apply|asc?|authorization|auto_increment|backup|bdb|begin|berkeleydb|bigint|binary|bit|blob|bool|boolean|break|browse|[br]tree|bulk|by|c?all|cascaded?|case|chain|character|charset|check(?:point)?|close|clustered|coalesce|collate|columns?|comment|commit(?:ted)?|compute|connect|consistent|constraint|contains(?:table)?|continue|convert|create|cross|current(?:_date|_time|_timestamp|_user)?|cursor|cycle|data(?:bases?)?|date(?:time)?|day|dbcc|deallocate|dec|decimal|declare|default|definer|delayed|delete|delimiters?|deny|desc|describe|deterministic|disable|discard|disk|distinct|distinctrow|distributed|do|double|drop|dummy|dump(?:file)?|duplicate|else(?:if)?|enable|enclosed|end|engine|enum|errlvl|errors|escaped?|except|exec(?:ute)?|exists|exit|explain|extended|fetch|fields|file|fillfactor|first|fixed|float|following|for each row|for|force|foreign|freetexttable|freetext|from|full|function|geometry(?:collection)?|global|goto|grant|group|handler|hash|having|holdlock|hour|identity(?:col|_insert)?|if|ignore|import|index|infile|inner|innodb|inout|insert|integer|intersect|interval|into?|invoker|isolation|iterate|join|keys?|kill|language|last|leave|left|level|limit|lineno|lines|linestring|load|local|lock|long(?:blob|text)|loop|matched|match|(?:medium|tiny)(?:blob|int|text)|merge|middleint|minute|mode|modifies|modify|month|multi(?:linestring|point|polygon)|national|natural|n?char|next|no|nonclustered|nullif|numeric|off?|offsets?|on|open(?:datasource|query|rowset)?|optimize|option(?:ally)?|order|out(?:er|file)?|over|partial|partition|percent|pivot|plan|point|polygon|preceding|precision|prepare|prev|primary|print|privileges|proc(?:edure)?|public|purge|quick|raiserror|reads?|real|reconfigure|references|release|rename|repeat(?:able)?|replace|replication|require|resignal|restore|restrict|returning|returns?|revoke|right|rollback|routine|row(?:count|guidcol|s)?|rule|savepoint|save|schema|second|select|serializable|serial|session_user|session|setuser|set|share|show|shutdown|simple|smallint|snapshot|some|soname|sql|start(?:ing)?|statistics|status|striped|system_user|tables?|tablespace|temp(?:orary|table)?|terminated|textsize|text|[tw]hen|timestamp|time|top?|transactions?|tran|trigger|truncate|tsequal|types?|unbounded|uncommitted|undefined|union|unique|unlock|unpivot|unsigned|updatetext|update|usage|user?|using|values?|var(?:binary|char|character|ying)|view|waitfor|warnings|where|while|with(?: rollup|in)?|work|writetext|write|year)\b/i,
  "boolean": /\b(?:false|true|null)\b/i,
  "number": /\b0x[a-f\d]+\b|\b\d+(?:\.\d*)?|\B\.\d+\b/i,
  "operator": /[=%~^/*+-]|&&?|\|\|?|!=?|<<|<=?>?|>[>=]?|\b(?:and|between|div|[ir]?like|in|is|not|x?or|regexp|sounds like)\b/i,
  "punctuation": /[()[\].,;`]/
};
//# sourceMappingURL=sql.js.map
