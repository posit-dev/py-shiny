const attrValueB = ["true", "false"];
const attrValueU = ["true", "false", "undefined"];
const attrValueO = ["on", "off"];
const attrValueY = ["yes", "no"];
const attrValueW = ["soft", "hard"];
const attrValueD = ["ltr", "rtl", "auto"];
const attrValueM = ["get", "post", "dialog"];
const attrValueFm = ["get", "post"];
const attrValueS = ["row", "col", "rowgroup", "colgroup"];
const attrValueT = ["hidden", "text", "search", "tel", "url", "email", "password", "datetime", "date", "month", "week", "time", "datetime-local", "number", "range", "color", "checkbox", "radio", "file", "submit", "image", "reset", "button"];
const attrValueIm = ["none", "text", "decimal", "numeric", "tel", "search", "email", "url"];
const attrValueBt = ["button", "submit", "reset"];
const attrValueLt = ["1", "a", "A", "i", "I"];
const attrValueEt = ["application/x-www-form-urlencoded", "multipart/form-data", "text/plain"];
const attrValueTk = ["subtitles", "captions", "descriptions", "chapters", "metadata"];
const attrValuePl = ["none", "metadata", "auto"];
const attrValueSh = ["circle", "default", "poly", "rect"];
const attrValueXo = ["anonymous", "use-credentials"];
const attrValueTarget = ["_self", "_blank", "_parent", "_top"];
const attrValueSb = ["allow-forms", "allow-modals", "allow-pointer-lock", "allow-popups", "allow-popups-to-escape-sandbox", "allow-same-origin", "allow-scripts", "allow-top-navigation"];
const attrValueTristate = ["true", "false", "mixed", "undefined"];
const attrValueInputautocomplete = ["additional-name", "address-level1", "address-level2", "address-level3", "address-level4", "address-line1", "address-line2", "address-line3", "bday", "bday-year", "bday-day", "bday-month", "billing", "cc-additional-name", "cc-csc", "cc-exp", "cc-exp-month", "cc-exp-year", "cc-family-name", "cc-given-name", "cc-name", "cc-number", "cc-type", "country", "country-name", "current-password", "email", "family-name", "fax", "given-name", "home", "honorific-prefix", "honorific-suffix", "impp", "language", "mobile", "name", "new-password", "nickname", "off", "on", "organization", "organization-title", "pager", "photo", "postal-code", "sex", "shipping", "street-address", "tel-area-code", "tel", "tel-country-code", "tel-extension", "tel-local", "tel-local-prefix", "tel-local-suffix", "tel-national", "transaction-amount", "transaction-currency", "url", "username", "work"];
const attrValueAutocomplete = ["inline", "list", "both", "none"];
const attrValueCurrent = ["true", "false", "page", "step", "location", "date", "time"];
const attrValueDropeffect = ["copy", "move", "link", "execute", "popup", "none"];
const attrValueInvalid = ["true", "false", "grammar", "spelling"];
const attrValueLive = ["off", "polite", "assertive"];
const attrValueOrientation = ["vertical", "horizontal", "undefined"];
const attrValueRelevant = ["additions", "removals", "text", "all"];
const attrValueSort = ["ascending", "descending", "none", "other"];
const attrValueRoles = ["alert", "alertdialog", "button", "checkbox", "dialog", "gridcell", "link", "log", "marquee", "menuitem", "menuitemcheckbox", "menuitemradio", "option", "progressbar", "radio", "scrollbar", "searchbox", "slider", "spinbutton", "status", "switch", "tab", "tabpanel", "textbox", "timer", "tooltip", "treeitem", "combobox", "grid", "listbox", "menu", "menubar", "radiogroup", "tablist", "tree", "treegrid", "application", "article", "cell", "columnheader", "definition", "directory", "document", "feed", "figure", "group", "heading", "img", "list", "listitem", "math", "none", "note", "presentation", "region", "row", "rowgroup", "rowheader", "separator", "table", "term", "text", "toolbar", "banner", "complementary", "contentinfo", "form", "main", "navigation", "region", "search"];
const attrValueHaspopup = ["true", "false", "menu", "listbox", "tree", "grid", "dialog"];
const attrValueDecoding = ["sync", "async", "auto"];
const attrValueLoading = ["eager", "lazy"];
const attrValueReferrerpolicy = ["no-referrer", "no-referrer-when-downgrade", "origin", "origin-when-cross-origin", "same-origin", "strict-origin", "strict-origin-when-cross-origin", "unsafe-url"];
const attrValueEnterkeyhint = ["enter", "done", "go", "next", "previous", "search", "send"];
const attrValuePopover = ["auto", "hint", "manual"];
const attrValueFetchpriority = ["high", "low", "auto"];
const attrValueCe = ["true", "false", "plaintext-only"];
const htmlEventHandlers = {
  onabort: null,
  onblur: null,
  oncanplay: null,
  oncanplaythrough: null,
  onchange: null,
  onclick: null,
  oncontextmenu: null,
  ondblclick: null,
  ondrag: null,
  ondragend: null,
  ondragenter: null,
  ondragleave: null,
  ondragover: null,
  ondragstart: null,
  ondrop: null,
  ondurationchange: null,
  onemptied: null,
  onended: null,
  onerror: null,
  onfocus: null,
  onformchange: null,
  onforminput: null,
  oninput: null,
  oninvalid: null,
  onkeydown: null,
  onkeypress: null,
  onkeyup: null,
  onload: null,
  onloadeddata: null,
  onloadedmetadata: null,
  onloadstart: null,
  onmousedown: null,
  onmousemove: null,
  onmouseout: null,
  onmouseover: null,
  onmouseup: null,
  onmousewheel: null,
  onmouseenter: null,
  onmouseleave: null,
  onpause: null,
  onplay: null,
  onplaying: null,
  onprogress: null,
  onratechange: null,
  onreset: null,
  onresize: null,
  onreadystatechange: null,
  onscroll: null,
  onseeked: null,
  onseeking: null,
  onselect: null,
  onshow: null,
  onstalled: null,
  onsubmit: null,
  onsuspend: null,
  ontimeupdate: null,
  onvolumechange: null,
  onwaiting: null,
  onpointercancel: null,
  onpointerdown: null,
  onpointerenter: null,
  onpointerleave: null,
  onpointerlockchange: null,
  onpointerlockerror: null,
  onpointermove: null,
  onpointerout: null,
  onpointerover: null,
  onpointerup: null
};
const ariaAttributes = {
  "aria-activedescendant": null,
  "aria-atomic": attrValueB,
  "aria-autocomplete": attrValueAutocomplete,
  "aria-busy": attrValueB,
  "aria-checked": attrValueTristate,
  "aria-colcount": null,
  "aria-colindex": null,
  "aria-colspan": null,
  "aria-controls": null,
  "aria-current": attrValueCurrent,
  "aria-describedby": null,
  "aria-disabled": attrValueB,
  "aria-dropeffect": attrValueDropeffect,
  "aria-errormessage": null,
  "aria-expanded": attrValueU,
  "aria-flowto": null,
  "aria-grabbed": attrValueU,
  "aria-haspopup": attrValueHaspopup,
  "aria-hidden": attrValueB,
  "aria-invalid": attrValueInvalid,
  "aria-label": null,
  "aria-labelledby": null,
  "aria-level": null,
  "aria-live": attrValueLive,
  "aria-modal": attrValueB,
  "aria-multiline": attrValueB,
  "aria-multiselectable": attrValueB,
  "aria-orientation": attrValueOrientation,
  "aria-owns": null,
  "aria-placeholder": null,
  "aria-posinset": null,
  "aria-pressed": attrValueTristate,
  "aria-readonly": attrValueB,
  "aria-relevant": attrValueRelevant,
  "aria-required": attrValueB,
  "aria-roledescription": null,
  "aria-rowcount": null,
  "aria-rowindex": null,
  "aria-rowspan": null,
  "aria-selected": attrValueU,
  "aria-setsize": null,
  "aria-sort": attrValueSort,
  "aria-valuemax": null,
  "aria-valuemin": null,
  "aria-valuenow": null,
  "aria-valuetext": null,
  "aria-details": null,
  "aria-keyshortcuts": null
};
const globalHtmlAttributes = {
  ...ariaAttributes,
  ...htmlEventHandlers,
  accesskey: null,
  autocapitalize: null,
  autocorrect: attrValueO,
  autofocus: null,
  class: null,
  contenteditable: attrValueCe,
  contextmenu: null,
  dir: attrValueD,
  draggable: attrValueB,
  dropzone: null,
  enterkeyhint: attrValueEnterkeyhint,
  exportparts: null,
  hidden: null,
  id: null,
  inert: null,
  inputmode: attrValueIm,
  is: null,
  itemid: null,
  itemprop: null,
  itemref: null,
  itemscope: null,
  itemtype: null,
  lang: null,
  nonce: null,
  part: null,
  popover: attrValuePopover,
  role: attrValueRoles,
  slot: null,
  spellcheck: attrValueB,
  style: null,
  tabindex: null,
  title: null,
  translate: attrValueY,
  virtualkeyboardpolicy: attrValueB
};
const empty = {};
const htmlTags = {
  html: {
    manifest: null,
    version: null,
    xmlns: null
  },
  head: {
    profile: null
  },
  title: empty,
  base: {
    href: null,
    target: attrValueTarget
  },
  link: {
    href: null,
    crossorigin: attrValueXo,
    rel: null,
    media: null,
    hreflang: null,
    type: null,
    sizes: null,
    as: null,
    importance: null,
    integrity: null,
    referrerpolicy: null
  },
  meta: {
    name: null,
    "http-equiv": null,
    content: null,
    charset: null,
    scheme: null
  },
  style: {
    media: null,
    type: null,
    scoped: null
  },
  body: {
    onafterprint: null,
    onbeforeprint: null,
    onbeforeunload: null,
    onhashchange: null,
    onlanguagechange: null,
    onmessage: null,
    onoffline: null,
    ononline: null,
    onpagehide: null,
    onpageshow: null,
    onpopstate: null,
    onstorage: null,
    onunload: null,
    alink: null,
    background: null,
    bgcolor: null,
    bottommargin: null,
    leftmargin: null,
    link: null,
    onredo: null,
    onundo: null,
    rightmargin: null,
    text: null,
    topmargin: null,
    vlink: null
  },
  article: empty,
  section: empty,
  nav: empty,
  aside: empty,
  h1: empty,
  h2: empty,
  h3: empty,
  h4: empty,
  h5: empty,
  h6: empty,
  header: empty,
  footer: empty,
  address: empty,
  p: empty,
  hr: {
    align: null,
    color: null,
    noshade: null,
    size: null,
    width: null
  },
  pre: {
    cols: null,
    width: null,
    wrap: null
  },
  blockquote: {
    cite: null
  },
  ol: {
    reversed: null,
    start: null,
    type: attrValueLt,
    compact: null
  },
  ul: {
    compact: null
  },
  li: {
    value: null,
    type: null
  },
  dl: empty,
  dt: empty,
  dd: {
    nowrap: null
  },
  figure: empty,
  figcaption: empty,
  main: empty,
  div: empty,
  a: {
    href: null,
    target: attrValueTarget,
    download: null,
    ping: null,
    rel: null,
    hreflang: null,
    type: null,
    referrerpolicy: null
  },
  em: empty,
  strong: empty,
  small: empty,
  s: empty,
  cite: empty,
  q: {
    cite: null
  },
  dfn: empty,
  abbr: empty,
  ruby: empty,
  rb: empty,
  rt: empty,
  rp: empty,
  time: {
    datetime: null
  },
  code: empty,
  var: empty,
  samp: empty,
  kbd: empty,
  sub: empty,
  sup: empty,
  i: empty,
  b: empty,
  u: empty,
  mark: empty,
  bdi: empty,
  bdo: {},
  span: empty,
  br: {
    clear: null
  },
  wbr: empty,
  ins: {
    cite: null,
    datetime: null
  },
  del: {
    cite: null,
    datetime: null
  },
  picture: empty,
  img: {
    alt: null,
    src: null,
    srcset: null,
    crossorigin: attrValueXo,
    usemap: null,
    ismap: null,
    width: null,
    height: null,
    decoding: attrValueDecoding,
    loading: attrValueLoading,
    fetchpriority: attrValueFetchpriority,
    referrerpolicy: attrValueReferrerpolicy,
    sizes: null,
    importance: null,
    intrinsicsize: null
  },
  iframe: {
    src: null,
    srcdoc: null,
    name: null,
    sandbox: attrValueSb,
    seamless: null,
    allowfullscreen: null,
    width: null,
    height: null,
    allow: null,
    allowpaymentrequest: null,
    csp: null,
    importance: null,
    referrerpolicy: null
  },
  embed: {
    src: null,
    type: null,
    width: null,
    height: null
  },
  object: {
    data: null,
    type: null,
    typemustmatch: null,
    name: null,
    usemap: null,
    form: null,
    width: null,
    height: null,
    archive: null,
    border: null,
    classid: null,
    codebase: null,
    codetype: null,
    declare: null,
    standby: null
  },
  param: {
    name: null,
    value: null,
    type: null,
    valuetype: null
  },
  video: {
    src: null,
    crossorigin: attrValueXo,
    poster: null,
    preload: attrValuePl,
    autoplay: null,
    mediagroup: null,
    loop: null,
    muted: null,
    controls: null,
    width: null,
    height: null
  },
  audio: {
    src: null,
    crossorigin: attrValueXo,
    preload: attrValuePl,
    autoplay: null,
    mediagroup: null,
    loop: null,
    muted: null,
    controls: null
  },
  source: {
    src: null,
    type: null,
    sizes: null,
    srcset: null,
    media: null
  },
  track: {
    default: null,
    kind: attrValueTk,
    label: null,
    src: null,
    srclang: null
  },
  map: {
    name: null
  },
  area: {
    alt: null,
    coords: null,
    shape: attrValueSh,
    href: null,
    target: attrValueTarget,
    download: null,
    ping: null,
    rel: null,
    hreflang: null,
    type: null
  },
  table: {
    border: null,
    align: null
  },
  caption: {
    align: null
  },
  colgroup: {
    span: null,
    align: null
  },
  col: {
    span: null,
    align: null
  },
  tbody: {
    align: null
  },
  thead: {
    align: null
  },
  tfoot: {
    align: null
  },
  tr: {
    align: null
  },
  td: {
    colspan: null,
    rowspan: null,
    headers: null,
    abbr: null,
    align: null,
    axis: null,
    bgcolor: null
  },
  th: {
    colspan: null,
    rowspan: null,
    headers: null,
    scope: attrValueS,
    sorted: null,
    abbr: null,
    align: null,
    axis: null,
    bgcolor: null
  },
  form: {
    "accept-charset": null,
    action: null,
    autocomplete: attrValueO,
    enctype: attrValueEt,
    method: attrValueM,
    name: null,
    novalidate: null,
    target: attrValueTarget,
    accept: null
  },
  label: {
    form: null,
    for: null
  },
  input: {
    accept: null,
    alt: null,
    autocomplete: attrValueInputautocomplete,
    checked: null,
    dirname: null,
    disabled: null,
    form: null,
    formaction: null,
    formenctype: attrValueEt,
    formmethod: attrValueFm,
    formnovalidate: null,
    formtarget: null,
    height: null,
    list: null,
    max: null,
    maxlength: null,
    min: null,
    minlength: null,
    multiple: null,
    name: null,
    pattern: null,
    placeholder: null,
    popovertarget: null,
    popovertargetaction: null,
    readonly: null,
    required: null,
    size: null,
    src: null,
    step: null,
    type: attrValueT,
    value: null,
    width: null
  },
  button: {
    disabled: null,
    form: null,
    formaction: null,
    formenctype: attrValueEt,
    formmethod: attrValueFm,
    formnovalidate: null,
    formtarget: null,
    name: null,
    popovertarget: null,
    popovertargetaction: null,
    type: attrValueBt,
    value: null,
    autocomplete: null
  },
  select: {
    autocomplete: attrValueInputautocomplete,
    disabled: null,
    form: null,
    multiple: null,
    name: null,
    required: null,
    size: null
  },
  datalist: empty,
  optgroup: {
    disabled: null,
    label: null
  },
  option: {
    disabled: null,
    label: null,
    selected: null,
    value: null
  },
  textarea: {
    autocomplete: attrValueInputautocomplete,
    cols: null,
    dirname: null,
    disabled: null,
    form: null,
    maxlength: null,
    minlength: null,
    name: null,
    placeholder: null,
    readonly: null,
    required: null,
    rows: null,
    wrap: attrValueW
  },
  output: {
    for: null,
    form: null,
    name: null
  },
  progress: {
    value: null,
    max: null
  },
  meter: {
    value: null,
    min: null,
    max: null,
    low: null,
    high: null,
    optimum: null,
    form: null
  },
  fieldset: {
    disabled: null,
    form: null,
    name: null
  },
  legend: empty,
  details: {
    open: null
  },
  summary: empty,
  dialog: {
    open: null
  },
  script: {
    src: null,
    type: null,
    charset: null,
    async: null,
    defer: null,
    crossorigin: attrValueXo,
    integrity: null,
    nomodule: null,
    referrerpolicy: null,
    text: null
  },
  noscript: empty,
  template: empty,
  canvas: {
    width: null,
    height: null,
    "moz-opaque": null
  },
  slot: {
    name: null
  },
  data: {
    value: null
  },
  hgroup: empty,
  menu: empty,
  search: empty,
  fencedframe: {
    allow: null,
    height: null,
    width: null
  },
  selectedcontent: empty
};
export {
  attrValuePl as A,
  attrValueSb as B,
  attrValueLoading as C,
  attrValueLt as D,
  htmlEventHandlers as a,
  attrValueXo as b,
  attrValueDecoding as c,
  attrValueB as d,
  attrValueTarget as e,
  attrValueReferrerpolicy as f,
  globalHtmlAttributes as g,
  htmlTags as h,
  ariaAttributes as i,
  attrValueIm as j,
  attrValueO as k,
  attrValueRoles as l,
  attrValueY as m,
  attrValueEnterkeyhint as n,
  attrValueD as o,
  attrValueCe as p,
  attrValueW as q,
  attrValueInputautocomplete as r,
  attrValueBt as s,
  attrValueFm as t,
  attrValueEt as u,
  attrValueT as v,
  attrValueM as w,
  attrValueS as x,
  attrValueSh as y,
  attrValueTk as z
};
//# sourceMappingURL=data-C0_TsXpU.js.map
