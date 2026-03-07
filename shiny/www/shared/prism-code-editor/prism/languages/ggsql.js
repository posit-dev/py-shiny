// ggsql.js — ggsql language for prism-code-editor
//
// Extends the SQL grammar with ggsql-specific tokens.
// Derived from the TextMate grammar at:
// https://github.com/posit-dev/ggsql/blob/main/ggsql-vscode/syntaxes/ggsql.tmLanguage.json
//
// NOTE: The import path (index-XXXXXXX.js) is a content-hashed internal module.
// If bslib updates prism-code-editor, this hash may change. Check sql.js for
// the current filename.

import "./sql.js";
import { l as languages } from "../../index-C1_GGQ8y.js";

var sql = languages.sql;
var ggsql = {};

// Copy SQL tokens
Object.keys(sql).forEach(function(k) { ggsql[k] = sql[k]; });

// ggsql clause keywords
ggsql["ggsql-keyword"] = {
  pattern: /\b(?:VISUALISE|VISUALIZE|DRAW|MAPPING|REMAPPING|SETTING|FILTER|PARTITION|SCALE|FACET|PROJECT|LABEL|THEME|RENAMING|VIA|TO)\b/i,
  alias: "keyword",
};

// Geom types
ggsql["ggsql-geom"] = {
  pattern: /\b(?:point|line|path|bar|col|area|tile|polygon|ribbon|histogram|density|smooth|boxplot|violin|text|label|segment|arrow|hline|vline|abline|errorbar)\b/,
  alias: "builtin",
};

// Scale type modifiers
ggsql["ggsql-scale-type"] = {
  pattern: /\b(?:CONTINUOUS|DISCRETE|BINNED|ORDINAL|IDENTITY)\b/i,
  alias: "builtin",
};

// Aesthetic names
ggsql["ggsql-aesthetic"] = {
  pattern: /\b(?:x|y|xmin|xmax|ymin|ymax|xend|yend|weight|color|colour|fill|stroke|opacity|size|shape|linetype|linewidth|width|height|family|fontface|hjust|vjust|panel|row|column|theta|radius|thetamin|thetamax|radiusmin|radiusmax|thetaend|radiusend|offset)\b/,
  alias: "attr-name",
};

// Theme names
ggsql["ggsql-theme"] = {
  pattern: /\b(?:minimal|classic|gray|grey|bw|dark|light|void)\b/,
  alias: "class-name",
};

// Project types
ggsql["ggsql-project"] = {
  pattern: /\b(?:cartesian|polar|flip|fixed|trans|map|quickmap)\b/,
  alias: "class-name",
};

// Fat arrow operator
ggsql["ggsql-arrow"] = {
  pattern: /=>/,
  alias: "operator",
};

// Broader SQL function list
ggsql["function"] = /\b(?:count|sum|avg|min|max|stddev|variance|array_agg|string_agg|group_concat|row_number|rank|dense_rank|ntile|lag|lead|first_value|last_value|nth_value|cume_dist|percent_rank|date_trunc|date_part|datepart|datename|dateadd|datediff|extract|now|current_date|current_time|current_timestamp|getdate|getutcdate|strftime|strptime|make_date|make_time|make_timestamp|concat|substring|substr|left|right|length|len|char_length|lower|upper|trim|ltrim|rtrim|replace|reverse|repeat|lpad|rpad|split_part|string_split|format|printf|regexp_replace|regexp_extract|regexp_matches|abs|ceil|ceiling|floor|round|trunc|truncate|mod|power|sqrt|exp|ln|log|log10|log2|sign|sin|cos|tan|asin|acos|atan|atan2|pi|degrees|radians|random|rand|cast|convert|coalesce|nullif|ifnull|isnull|nvl|try_cast|typeof|if|iff|iif|greatest|least|decode|json|json_extract|json_extract_path|json_extract_string|json_value|json_query|json_object|json_array|json_array_length|to_json|from_json|list|list_value|list_aggregate|array_length|unnest|generate_series|range|first|last)(?=\s*\()/i;

// Reorder: ggsql tokens before generic SQL keyword/boolean
var ordered = {};
["comment", "variable", "string", "identifier"].forEach(function(k) {
  if (k in ggsql) ordered[k] = ggsql[k];
});
["ggsql-keyword", "ggsql-geom", "ggsql-scale-type", "ggsql-aesthetic",
 "ggsql-theme", "ggsql-project", "ggsql-arrow"].forEach(function(k) {
  if (k in ggsql) ordered[k] = ggsql[k];
});
Object.keys(ggsql).forEach(function(k) {
  if (!(k in ordered)) ordered[k] = ggsql[k];
});

languages.ggsql = ordered;
