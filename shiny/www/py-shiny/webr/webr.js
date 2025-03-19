// node_modules/@lit/reactive-element/css-tag.js
var t = globalThis;
var e = t.ShadowRoot && (void 0 === t.ShadyCSS || t.ShadyCSS.nativeShadow) && "adoptedStyleSheets" in Document.prototype && "replace" in CSSStyleSheet.prototype;
var s = Symbol();
var o = /* @__PURE__ */ new WeakMap();
var n = class {
  constructor(t3, e4, o4) {
    if (this._$cssResult$ = true, o4 !== s)
      throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");
    this.cssText = t3, this.t = e4;
  }
  get styleSheet() {
    let t3 = this.o;
    const s4 = this.t;
    if (e && void 0 === t3) {
      const e4 = void 0 !== s4 && 1 === s4.length;
      e4 && (t3 = o.get(s4)), void 0 === t3 && ((this.o = t3 = new CSSStyleSheet()).replaceSync(this.cssText), e4 && o.set(s4, t3));
    }
    return t3;
  }
  toString() {
    return this.cssText;
  }
};
var r = (t3) => new n("string" == typeof t3 ? t3 : t3 + "", void 0, s);
var S = (s4, o4) => {
  if (e)
    s4.adoptedStyleSheets = o4.map((t3) => t3 instanceof CSSStyleSheet ? t3 : t3.styleSheet);
  else
    for (const e4 of o4) {
      const o5 = document.createElement("style"), n4 = t.litNonce;
      void 0 !== n4 && o5.setAttribute("nonce", n4), o5.textContent = e4.cssText, s4.appendChild(o5);
    }
};
var c = e ? (t3) => t3 : (t3) => t3 instanceof CSSStyleSheet ? ((t4) => {
  let e4 = "";
  for (const s4 of t4.cssRules)
    e4 += s4.cssText;
  return r(e4);
})(t3) : t3;

// node_modules/@lit/reactive-element/reactive-element.js
var { is: i2, defineProperty: e2, getOwnPropertyDescriptor: r2, getOwnPropertyNames: h, getOwnPropertySymbols: o2, getPrototypeOf: n2 } = Object;
var a = globalThis;
var c2 = a.trustedTypes;
var l = c2 ? c2.emptyScript : "";
var p = a.reactiveElementPolyfillSupport;
var d = (t3, s4) => t3;
var u = { toAttribute(t3, s4) {
  switch (s4) {
    case Boolean:
      t3 = t3 ? l : null;
      break;
    case Object:
    case Array:
      t3 = null == t3 ? t3 : JSON.stringify(t3);
  }
  return t3;
}, fromAttribute(t3, s4) {
  let i4 = t3;
  switch (s4) {
    case Boolean:
      i4 = null !== t3;
      break;
    case Number:
      i4 = null === t3 ? null : Number(t3);
      break;
    case Object:
    case Array:
      try {
        i4 = JSON.parse(t3);
      } catch (t4) {
        i4 = null;
      }
  }
  return i4;
} };
var f = (t3, s4) => !i2(t3, s4);
var y = { attribute: true, type: String, converter: u, reflect: false, hasChanged: f };
Symbol.metadata ??= Symbol("metadata"), a.litPropertyMetadata ??= /* @__PURE__ */ new WeakMap();
var b = class extends HTMLElement {
  static addInitializer(t3) {
    this._$Ei(), (this.l ??= []).push(t3);
  }
  static get observedAttributes() {
    return this.finalize(), this._$Eh && [...this._$Eh.keys()];
  }
  static createProperty(t3, s4 = y) {
    if (s4.state && (s4.attribute = false), this._$Ei(), this.elementProperties.set(t3, s4), !s4.noAccessor) {
      const i4 = Symbol(), r5 = this.getPropertyDescriptor(t3, i4, s4);
      void 0 !== r5 && e2(this.prototype, t3, r5);
    }
  }
  static getPropertyDescriptor(t3, s4, i4) {
    const { get: e4, set: h3 } = r2(this.prototype, t3) ?? { get() {
      return this[s4];
    }, set(t4) {
      this[s4] = t4;
    } };
    return { get() {
      return e4?.call(this);
    }, set(s5) {
      const r5 = e4?.call(this);
      h3.call(this, s5), this.requestUpdate(t3, r5, i4);
    }, configurable: true, enumerable: true };
  }
  static getPropertyOptions(t3) {
    return this.elementProperties.get(t3) ?? y;
  }
  static _$Ei() {
    if (this.hasOwnProperty(d("elementProperties")))
      return;
    const t3 = n2(this);
    t3.finalize(), void 0 !== t3.l && (this.l = [...t3.l]), this.elementProperties = new Map(t3.elementProperties);
  }
  static finalize() {
    if (this.hasOwnProperty(d("finalized")))
      return;
    if (this.finalized = true, this._$Ei(), this.hasOwnProperty(d("properties"))) {
      const t4 = this.properties, s4 = [...h(t4), ...o2(t4)];
      for (const i4 of s4)
        this.createProperty(i4, t4[i4]);
    }
    const t3 = this[Symbol.metadata];
    if (null !== t3) {
      const s4 = litPropertyMetadata.get(t3);
      if (void 0 !== s4)
        for (const [t4, i4] of s4)
          this.elementProperties.set(t4, i4);
    }
    this._$Eh = /* @__PURE__ */ new Map();
    for (const [t4, s4] of this.elementProperties) {
      const i4 = this._$Eu(t4, s4);
      void 0 !== i4 && this._$Eh.set(i4, t4);
    }
    this.elementStyles = this.finalizeStyles(this.styles);
  }
  static finalizeStyles(s4) {
    const i4 = [];
    if (Array.isArray(s4)) {
      const e4 = new Set(s4.flat(1 / 0).reverse());
      for (const s5 of e4)
        i4.unshift(c(s5));
    } else
      void 0 !== s4 && i4.push(c(s4));
    return i4;
  }
  static _$Eu(t3, s4) {
    const i4 = s4.attribute;
    return false === i4 ? void 0 : "string" == typeof i4 ? i4 : "string" == typeof t3 ? t3.toLowerCase() : void 0;
  }
  constructor() {
    super(), this._$Ep = void 0, this.isUpdatePending = false, this.hasUpdated = false, this._$Em = null, this._$Ev();
  }
  _$Ev() {
    this._$ES = new Promise((t3) => this.enableUpdating = t3), this._$AL = /* @__PURE__ */ new Map(), this._$E_(), this.requestUpdate(), this.constructor.l?.forEach((t3) => t3(this));
  }
  addController(t3) {
    (this._$EO ??= /* @__PURE__ */ new Set()).add(t3), void 0 !== this.renderRoot && this.isConnected && t3.hostConnected?.();
  }
  removeController(t3) {
    this._$EO?.delete(t3);
  }
  _$E_() {
    const t3 = /* @__PURE__ */ new Map(), s4 = this.constructor.elementProperties;
    for (const i4 of s4.keys())
      this.hasOwnProperty(i4) && (t3.set(i4, this[i4]), delete this[i4]);
    t3.size > 0 && (this._$Ep = t3);
  }
  createRenderRoot() {
    const t3 = this.shadowRoot ?? this.attachShadow(this.constructor.shadowRootOptions);
    return S(t3, this.constructor.elementStyles), t3;
  }
  connectedCallback() {
    this.renderRoot ??= this.createRenderRoot(), this.enableUpdating(true), this._$EO?.forEach((t3) => t3.hostConnected?.());
  }
  enableUpdating(t3) {
  }
  disconnectedCallback() {
    this._$EO?.forEach((t3) => t3.hostDisconnected?.());
  }
  attributeChangedCallback(t3, s4, i4) {
    this._$AK(t3, i4);
  }
  _$EC(t3, s4) {
    const i4 = this.constructor.elementProperties.get(t3), e4 = this.constructor._$Eu(t3, i4);
    if (void 0 !== e4 && true === i4.reflect) {
      const r5 = (void 0 !== i4.converter?.toAttribute ? i4.converter : u).toAttribute(s4, i4.type);
      this._$Em = t3, null == r5 ? this.removeAttribute(e4) : this.setAttribute(e4, r5), this._$Em = null;
    }
  }
  _$AK(t3, s4) {
    const i4 = this.constructor, e4 = i4._$Eh.get(t3);
    if (void 0 !== e4 && this._$Em !== e4) {
      const t4 = i4.getPropertyOptions(e4), r5 = "function" == typeof t4.converter ? { fromAttribute: t4.converter } : void 0 !== t4.converter?.fromAttribute ? t4.converter : u;
      this._$Em = e4, this[e4] = r5.fromAttribute(s4, t4.type), this._$Em = null;
    }
  }
  requestUpdate(t3, s4, i4) {
    if (void 0 !== t3) {
      if (i4 ??= this.constructor.getPropertyOptions(t3), !(i4.hasChanged ?? f)(this[t3], s4))
        return;
      this.P(t3, s4, i4);
    }
    false === this.isUpdatePending && (this._$ES = this._$ET());
  }
  P(t3, s4, i4) {
    this._$AL.has(t3) || this._$AL.set(t3, s4), true === i4.reflect && this._$Em !== t3 && (this._$Ej ??= /* @__PURE__ */ new Set()).add(t3);
  }
  async _$ET() {
    this.isUpdatePending = true;
    try {
      await this._$ES;
    } catch (t4) {
      Promise.reject(t4);
    }
    const t3 = this.scheduleUpdate();
    return null != t3 && await t3, !this.isUpdatePending;
  }
  scheduleUpdate() {
    return this.performUpdate();
  }
  performUpdate() {
    if (!this.isUpdatePending)
      return;
    if (!this.hasUpdated) {
      if (this.renderRoot ??= this.createRenderRoot(), this._$Ep) {
        for (const [t5, s5] of this._$Ep)
          this[t5] = s5;
        this._$Ep = void 0;
      }
      const t4 = this.constructor.elementProperties;
      if (t4.size > 0)
        for (const [s5, i4] of t4)
          true !== i4.wrapped || this._$AL.has(s5) || void 0 === this[s5] || this.P(s5, this[s5], i4);
    }
    let t3 = false;
    const s4 = this._$AL;
    try {
      t3 = this.shouldUpdate(s4), t3 ? (this.willUpdate(s4), this._$EO?.forEach((t4) => t4.hostUpdate?.()), this.update(s4)) : this._$EU();
    } catch (s5) {
      throw t3 = false, this._$EU(), s5;
    }
    t3 && this._$AE(s4);
  }
  willUpdate(t3) {
  }
  _$AE(t3) {
    this._$EO?.forEach((t4) => t4.hostUpdated?.()), this.hasUpdated || (this.hasUpdated = true, this.firstUpdated(t3)), this.updated(t3);
  }
  _$EU() {
    this._$AL = /* @__PURE__ */ new Map(), this.isUpdatePending = false;
  }
  get updateComplete() {
    return this.getUpdateComplete();
  }
  getUpdateComplete() {
    return this._$ES;
  }
  shouldUpdate(t3) {
    return true;
  }
  update(t3) {
    this._$Ej &&= this._$Ej.forEach((t4) => this._$EC(t4, this[t4])), this._$EU();
  }
  updated(t3) {
  }
  firstUpdated(t3) {
  }
};
b.elementStyles = [], b.shadowRootOptions = { mode: "open" }, b[d("elementProperties")] = /* @__PURE__ */ new Map(), b[d("finalized")] = /* @__PURE__ */ new Map(), p?.({ ReactiveElement: b }), (a.reactiveElementVersions ??= []).push("2.0.4");

// node_modules/lit-html/lit-html.js
var t2 = globalThis;
var i3 = t2.trustedTypes;
var s2 = i3 ? i3.createPolicy("lit-html", { createHTML: (t3) => t3 }) : void 0;
var e3 = "$lit$";
var h2 = `lit$${Math.random().toFixed(9).slice(2)}$`;
var o3 = "?" + h2;
var n3 = `<${o3}>`;
var r3 = document;
var l2 = () => r3.createComment("");
var c3 = (t3) => null === t3 || "object" != typeof t3 && "function" != typeof t3;
var a2 = Array.isArray;
var u2 = (t3) => a2(t3) || "function" == typeof t3?.[Symbol.iterator];
var d2 = "[ 	\n\f\r]";
var f2 = /<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g;
var v = /-->/g;
var _ = />/g;
var m = RegExp(`>|${d2}(?:([^\\s"'>=/]+)(${d2}*=${d2}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`, "g");
var p2 = /'/g;
var g = /"/g;
var $ = /^(?:script|style|textarea|title)$/i;
var y2 = (t3) => (i4, ...s4) => ({ _$litType$: t3, strings: i4, values: s4 });
var x = y2(1);
var b2 = y2(2);
var w = Symbol.for("lit-noChange");
var T = Symbol.for("lit-nothing");
var A = /* @__PURE__ */ new WeakMap();
var E = r3.createTreeWalker(r3, 129);
function C(t3, i4) {
  if (!Array.isArray(t3) || !t3.hasOwnProperty("raw"))
    throw Error("invalid template strings array");
  return void 0 !== s2 ? s2.createHTML(i4) : i4;
}
var P = (t3, i4) => {
  const s4 = t3.length - 1, o4 = [];
  let r5, l3 = 2 === i4 ? "<svg>" : "", c4 = f2;
  for (let i5 = 0; i5 < s4; i5++) {
    const s5 = t3[i5];
    let a3, u3, d3 = -1, y3 = 0;
    for (; y3 < s5.length && (c4.lastIndex = y3, u3 = c4.exec(s5), null !== u3); )
      y3 = c4.lastIndex, c4 === f2 ? "!--" === u3[1] ? c4 = v : void 0 !== u3[1] ? c4 = _ : void 0 !== u3[2] ? ($.test(u3[2]) && (r5 = RegExp("</" + u3[2], "g")), c4 = m) : void 0 !== u3[3] && (c4 = m) : c4 === m ? ">" === u3[0] ? (c4 = r5 ?? f2, d3 = -1) : void 0 === u3[1] ? d3 = -2 : (d3 = c4.lastIndex - u3[2].length, a3 = u3[1], c4 = void 0 === u3[3] ? m : '"' === u3[3] ? g : p2) : c4 === g || c4 === p2 ? c4 = m : c4 === v || c4 === _ ? c4 = f2 : (c4 = m, r5 = void 0);
    const x2 = c4 === m && t3[i5 + 1].startsWith("/>") ? " " : "";
    l3 += c4 === f2 ? s5 + n3 : d3 >= 0 ? (o4.push(a3), s5.slice(0, d3) + e3 + s5.slice(d3) + h2 + x2) : s5 + h2 + (-2 === d3 ? i5 : x2);
  }
  return [C(t3, l3 + (t3[s4] || "<?>") + (2 === i4 ? "</svg>" : "")), o4];
};
var V = class _V {
  constructor({ strings: t3, _$litType$: s4 }, n4) {
    let r5;
    this.parts = [];
    let c4 = 0, a3 = 0;
    const u3 = t3.length - 1, d3 = this.parts, [f3, v2] = P(t3, s4);
    if (this.el = _V.createElement(f3, n4), E.currentNode = this.el.content, 2 === s4) {
      const t4 = this.el.content.firstChild;
      t4.replaceWith(...t4.childNodes);
    }
    for (; null !== (r5 = E.nextNode()) && d3.length < u3; ) {
      if (1 === r5.nodeType) {
        if (r5.hasAttributes())
          for (const t4 of r5.getAttributeNames())
            if (t4.endsWith(e3)) {
              const i4 = v2[a3++], s5 = r5.getAttribute(t4).split(h2), e4 = /([.?@])?(.*)/.exec(i4);
              d3.push({ type: 1, index: c4, name: e4[2], strings: s5, ctor: "." === e4[1] ? k : "?" === e4[1] ? H : "@" === e4[1] ? I : R }), r5.removeAttribute(t4);
            } else
              t4.startsWith(h2) && (d3.push({ type: 6, index: c4 }), r5.removeAttribute(t4));
        if ($.test(r5.tagName)) {
          const t4 = r5.textContent.split(h2), s5 = t4.length - 1;
          if (s5 > 0) {
            r5.textContent = i3 ? i3.emptyScript : "";
            for (let i4 = 0; i4 < s5; i4++)
              r5.append(t4[i4], l2()), E.nextNode(), d3.push({ type: 2, index: ++c4 });
            r5.append(t4[s5], l2());
          }
        }
      } else if (8 === r5.nodeType)
        if (r5.data === o3)
          d3.push({ type: 2, index: c4 });
        else {
          let t4 = -1;
          for (; -1 !== (t4 = r5.data.indexOf(h2, t4 + 1)); )
            d3.push({ type: 7, index: c4 }), t4 += h2.length - 1;
        }
      c4++;
    }
  }
  static createElement(t3, i4) {
    const s4 = r3.createElement("template");
    return s4.innerHTML = t3, s4;
  }
};
function N(t3, i4, s4 = t3, e4) {
  if (i4 === w)
    return i4;
  let h3 = void 0 !== e4 ? s4._$Co?.[e4] : s4._$Cl;
  const o4 = c3(i4) ? void 0 : i4._$litDirective$;
  return h3?.constructor !== o4 && (h3?._$AO?.(false), void 0 === o4 ? h3 = void 0 : (h3 = new o4(t3), h3._$AT(t3, s4, e4)), void 0 !== e4 ? (s4._$Co ??= [])[e4] = h3 : s4._$Cl = h3), void 0 !== h3 && (i4 = N(t3, h3._$AS(t3, i4.values), h3, e4)), i4;
}
var S2 = class {
  constructor(t3, i4) {
    this._$AV = [], this._$AN = void 0, this._$AD = t3, this._$AM = i4;
  }
  get parentNode() {
    return this._$AM.parentNode;
  }
  get _$AU() {
    return this._$AM._$AU;
  }
  u(t3) {
    const { el: { content: i4 }, parts: s4 } = this._$AD, e4 = (t3?.creationScope ?? r3).importNode(i4, true);
    E.currentNode = e4;
    let h3 = E.nextNode(), o4 = 0, n4 = 0, l3 = s4[0];
    for (; void 0 !== l3; ) {
      if (o4 === l3.index) {
        let i5;
        2 === l3.type ? i5 = new M(h3, h3.nextSibling, this, t3) : 1 === l3.type ? i5 = new l3.ctor(h3, l3.name, l3.strings, this, t3) : 6 === l3.type && (i5 = new L(h3, this, t3)), this._$AV.push(i5), l3 = s4[++n4];
      }
      o4 !== l3?.index && (h3 = E.nextNode(), o4++);
    }
    return E.currentNode = r3, e4;
  }
  p(t3) {
    let i4 = 0;
    for (const s4 of this._$AV)
      void 0 !== s4 && (void 0 !== s4.strings ? (s4._$AI(t3, s4, i4), i4 += s4.strings.length - 2) : s4._$AI(t3[i4])), i4++;
  }
};
var M = class _M {
  get _$AU() {
    return this._$AM?._$AU ?? this._$Cv;
  }
  constructor(t3, i4, s4, e4) {
    this.type = 2, this._$AH = T, this._$AN = void 0, this._$AA = t3, this._$AB = i4, this._$AM = s4, this.options = e4, this._$Cv = e4?.isConnected ?? true;
  }
  get parentNode() {
    let t3 = this._$AA.parentNode;
    const i4 = this._$AM;
    return void 0 !== i4 && 11 === t3?.nodeType && (t3 = i4.parentNode), t3;
  }
  get startNode() {
    return this._$AA;
  }
  get endNode() {
    return this._$AB;
  }
  _$AI(t3, i4 = this) {
    t3 = N(this, t3, i4), c3(t3) ? t3 === T || null == t3 || "" === t3 ? (this._$AH !== T && this._$AR(), this._$AH = T) : t3 !== this._$AH && t3 !== w && this._(t3) : void 0 !== t3._$litType$ ? this.$(t3) : void 0 !== t3.nodeType ? this.T(t3) : u2(t3) ? this.k(t3) : this._(t3);
  }
  S(t3) {
    return this._$AA.parentNode.insertBefore(t3, this._$AB);
  }
  T(t3) {
    this._$AH !== t3 && (this._$AR(), this._$AH = this.S(t3));
  }
  _(t3) {
    this._$AH !== T && c3(this._$AH) ? this._$AA.nextSibling.data = t3 : this.T(r3.createTextNode(t3)), this._$AH = t3;
  }
  $(t3) {
    const { values: i4, _$litType$: s4 } = t3, e4 = "number" == typeof s4 ? this._$AC(t3) : (void 0 === s4.el && (s4.el = V.createElement(C(s4.h, s4.h[0]), this.options)), s4);
    if (this._$AH?._$AD === e4)
      this._$AH.p(i4);
    else {
      const t4 = new S2(e4, this), s5 = t4.u(this.options);
      t4.p(i4), this.T(s5), this._$AH = t4;
    }
  }
  _$AC(t3) {
    let i4 = A.get(t3.strings);
    return void 0 === i4 && A.set(t3.strings, i4 = new V(t3)), i4;
  }
  k(t3) {
    a2(this._$AH) || (this._$AH = [], this._$AR());
    const i4 = this._$AH;
    let s4, e4 = 0;
    for (const h3 of t3)
      e4 === i4.length ? i4.push(s4 = new _M(this.S(l2()), this.S(l2()), this, this.options)) : s4 = i4[e4], s4._$AI(h3), e4++;
    e4 < i4.length && (this._$AR(s4 && s4._$AB.nextSibling, e4), i4.length = e4);
  }
  _$AR(t3 = this._$AA.nextSibling, i4) {
    for (this._$AP?.(false, true, i4); t3 && t3 !== this._$AB; ) {
      const i5 = t3.nextSibling;
      t3.remove(), t3 = i5;
    }
  }
  setConnected(t3) {
    void 0 === this._$AM && (this._$Cv = t3, this._$AP?.(t3));
  }
};
var R = class {
  get tagName() {
    return this.element.tagName;
  }
  get _$AU() {
    return this._$AM._$AU;
  }
  constructor(t3, i4, s4, e4, h3) {
    this.type = 1, this._$AH = T, this._$AN = void 0, this.element = t3, this.name = i4, this._$AM = e4, this.options = h3, s4.length > 2 || "" !== s4[0] || "" !== s4[1] ? (this._$AH = Array(s4.length - 1).fill(new String()), this.strings = s4) : this._$AH = T;
  }
  _$AI(t3, i4 = this, s4, e4) {
    const h3 = this.strings;
    let o4 = false;
    if (void 0 === h3)
      t3 = N(this, t3, i4, 0), o4 = !c3(t3) || t3 !== this._$AH && t3 !== w, o4 && (this._$AH = t3);
    else {
      const e5 = t3;
      let n4, r5;
      for (t3 = h3[0], n4 = 0; n4 < h3.length - 1; n4++)
        r5 = N(this, e5[s4 + n4], i4, n4), r5 === w && (r5 = this._$AH[n4]), o4 ||= !c3(r5) || r5 !== this._$AH[n4], r5 === T ? t3 = T : t3 !== T && (t3 += (r5 ?? "") + h3[n4 + 1]), this._$AH[n4] = r5;
    }
    o4 && !e4 && this.j(t3);
  }
  j(t3) {
    t3 === T ? this.element.removeAttribute(this.name) : this.element.setAttribute(this.name, t3 ?? "");
  }
};
var k = class extends R {
  constructor() {
    super(...arguments), this.type = 3;
  }
  j(t3) {
    this.element[this.name] = t3 === T ? void 0 : t3;
  }
};
var H = class extends R {
  constructor() {
    super(...arguments), this.type = 4;
  }
  j(t3) {
    this.element.toggleAttribute(this.name, !!t3 && t3 !== T);
  }
};
var I = class extends R {
  constructor(t3, i4, s4, e4, h3) {
    super(t3, i4, s4, e4, h3), this.type = 5;
  }
  _$AI(t3, i4 = this) {
    if ((t3 = N(this, t3, i4, 0) ?? T) === w)
      return;
    const s4 = this._$AH, e4 = t3 === T && s4 !== T || t3.capture !== s4.capture || t3.once !== s4.once || t3.passive !== s4.passive, h3 = t3 !== T && (s4 === T || e4);
    e4 && this.element.removeEventListener(this.name, this, s4), h3 && this.element.addEventListener(this.name, this, t3), this._$AH = t3;
  }
  handleEvent(t3) {
    "function" == typeof this._$AH ? this._$AH.call(this.options?.host ?? this.element, t3) : this._$AH.handleEvent(t3);
  }
};
var L = class {
  constructor(t3, i4, s4) {
    this.element = t3, this.type = 6, this._$AN = void 0, this._$AM = i4, this.options = s4;
  }
  get _$AU() {
    return this._$AM._$AU;
  }
  _$AI(t3) {
    N(this, t3);
  }
};
var Z = t2.litHtmlPolyfillSupport;
Z?.(V, M), (t2.litHtmlVersions ??= []).push("3.1.3");
var j = (t3, i4, s4) => {
  const e4 = s4?.renderBefore ?? i4;
  let h3 = e4._$litPart$;
  if (void 0 === h3) {
    const t4 = s4?.renderBefore ?? null;
    e4._$litPart$ = h3 = new M(i4.insertBefore(l2(), t4), t4, void 0, s4 ?? {});
  }
  return h3._$AI(t3), h3;
};

// node_modules/lit-element/lit-element.js
var s3 = class extends b {
  constructor() {
    super(...arguments), this.renderOptions = { host: this }, this._$Do = void 0;
  }
  createRenderRoot() {
    const t3 = super.createRenderRoot();
    return this.renderOptions.renderBefore ??= t3.firstChild, t3;
  }
  update(t3) {
    const i4 = this.render();
    this.hasUpdated || (this.renderOptions.isConnected = this.isConnected), super.update(t3), this._$Do = j(i4, this.renderRoot, this.renderOptions);
  }
  connectedCallback() {
    super.connectedCallback(), this._$Do?.setConnected(true);
  }
  disconnectedCallback() {
    super.disconnectedCallback(), this._$Do?.setConnected(false);
  }
  render() {
    return w;
  }
};
s3._$litElement$ = true, s3["finalized", "finalized"] = true, globalThis.litElementHydrateSupport?.({ LitElement: s3 });
var r4 = globalThis.litElementPolyfillSupport;
r4?.({ LitElement: s3 });
(globalThis.litElementVersions ??= []).push("4.0.5");

// webr/webr.ts
import { WebR } from "https://webr.r-wasm.org/latest/webr.mjs";

// utils/_utils.ts
var LightElement = class extends s3 {
  createRenderRoot() {
    return this;
  }
};

// webr/webr.ts
var WEBR_COMPONENT_TAG = "shiny-webr-component";
var PLOT_WIDTH = 400;
var PLOT_HEIGHT = 300;
var WebRComponent = class extends LightElement {
  constructor() {
    super();
    this.outputId = this.id + "_output";
    this.inputId = this.id + "_input";
    this.runId = this.id + "_run";
    this.plotId = this.id + "_plot";
    this.dropZoneId = this.id + "_dropzone";
    this.fileListId = this.id + "_filelist";
    this.dropZoneTextId = this.id + "_dropzone_text";
    this.webR = new WebR();
  }
  render() {
    return x`<div>
      <pre style="max-height: 500px"><code id="${this.outputId}">Loading webR, please wait...</code></pre>
      <div>
        <input
          spellcheck="false"
          autocomplete="off"
          id="${this.inputId}"
          type="text"
          style="width: 100%;"
        />
        <button id="${this.runId}">Run</button>
      </div>
      <div id="${this.plotId}"></div>
      <div
        id="${this.dropZoneId}"
        style="border: 2px dashed #ccc; border-radius: 5px; padding: 20px; text-align: center; margin-top: 20px; cursor: pointer;"
      >
        <p id="${this.dropZoneTextId}">
          Drag and drop files here or click to upload
        </p>
        <input type="file" style="display: none;" multiple />
      </div>
      <div id="${this.fileListId}" style="margin-top: 10px;"></div>
    </div>`;
  }
  firstUpdated() {
    this.output = document.getElementById(this.outputId);
    this.input = document.getElementById(this.inputId);
    this.plot = document.getElementById(this.plotId);
    this.dropZone = document.getElementById(this.dropZoneId);
    this.fileList = document.getElementById(this.fileListId);
    this.dropZoneText = document.getElementById(
      this.dropZoneTextId
    );
    (async () => {
      await this.webR.init();
      this.output.textContent = `webR ${this.webR.version}
`;
      const result = await this.webR.flush();
      result.forEach((msg) => this.handleOutput(msg));
    })();
    const sendInput = async () => {
      await this.evalInConsole(this.input.value);
      this.input.value = "";
    };
    this.input.addEventListener("keydown", (e4) => {
      if (e4.code === "Enter")
        sendInput();
    });
    const runButton = document.getElementById(this.runId);
    runButton.addEventListener("click", sendInput);
    this.setupFileDragAndDrop();
  }
  setupFileDragAndDrop() {
    const dropZone = this.dropZone;
    const fileInput = dropZone.querySelector(
      'input[type="file"]'
    );
    dropZone.addEventListener("click", () => {
      fileInput.click();
    });
    fileInput.addEventListener("change", (e4) => {
      const files = fileInput.files;
      if (files) {
        void this.handleFiles(files);
      }
    });
    ["dragenter", "dragover", "dragleave", "drop"].forEach((eventName) => {
      dropZone.addEventListener(
        eventName,
        (e4) => {
          e4.preventDefault();
          e4.stopPropagation();
        },
        false
      );
    });
    ["dragenter", "dragover"].forEach((eventName) => {
      dropZone.addEventListener(
        eventName,
        () => {
          dropZone.style.borderColor = "#2196F3";
          dropZone.style.backgroundColor = "rgba(33, 150, 243, 0.1)";
        },
        false
      );
    });
    ["dragleave", "drop"].forEach((eventName) => {
      dropZone.addEventListener(
        eventName,
        () => {
          dropZone.style.borderColor = "#ccc";
          dropZone.style.backgroundColor = "";
        },
        false
      );
    });
    dropZone.addEventListener(
      "drop",
      (e4) => {
        const dt = e4.dataTransfer;
        if (dt && dt.files) {
          void this.handleFiles(dt.files);
        }
      },
      false
    );
  }
  async handleFiles(files) {
    for (let i4 = 0; i4 < files.length; i4++) {
      const file = files[i4];
      if (file) {
        await this.uploadFileToWebR(file);
      }
    }
  }
  async uploadFileToWebR(file) {
    try {
      const arrayBuffer = await file.arrayBuffer();
      const uint8Array = new Uint8Array(arrayBuffer);
      await this.webR.FS.writeFile(file.name, uint8Array);
      this.addFileToList(file.name);
      this.showSuccessMessage(`${file.name} uploaded successfully!`);
      this.appendToOutEl(`File uploaded to webR: ${file.name}
`);
      await this.evalInConsole(`list.files()`);
    } catch (error) {
      console.error("Error uploading file to webR:", error);
      this.appendToOutEl(`Error uploading file: ${file.name}
`);
    }
  }
  showSuccessMessage(message) {
    const originalText = this.dropZoneText.textContent;
    const originalBorderColor = this.dropZone.style.borderColor;
    const originalBackgroundColor = this.dropZone.style.backgroundColor;
    this.dropZoneText.textContent = message;
    this.dropZone.style.borderColor = "#4CAF50";
    this.dropZone.style.backgroundColor = "rgba(76, 175, 80, 0.1)";
    setTimeout(() => {
      this.dropZoneText.textContent = originalText;
      this.dropZone.style.borderColor = originalBorderColor;
      this.dropZone.style.backgroundColor = originalBackgroundColor;
    }, 2e3);
  }
  addFileToList(fileName) {
    const fileItem = document.createElement("div");
    fileItem.style.margin = "5px 0";
    fileItem.style.padding = "5px";
    fileItem.style.backgroundColor = "#f5f5f5";
    fileItem.style.borderRadius = "3px";
    fileItem.style.display = "flex";
    fileItem.style.justifyContent = "space-between";
    const fileNameSpan = document.createElement("span");
    fileNameSpan.textContent = fileName;
    fileItem.appendChild(fileNameSpan);
    const loadButton = document.createElement("button");
    loadButton.textContent = "Load in R";
    loadButton.style.marginLeft = "10px";
    loadButton.addEventListener("click", async () => {
      const ext = fileName.split(".").pop()?.toLowerCase();
      let rCode = "";
      switch (ext) {
        case "csv":
          rCode = `data <- read.csv("${fileName}")
head(data)`;
          break;
        case "rds":
          rCode = `data <- readRDS("${fileName}")
print(data)`;
          break;
        case "r":
          rCode = `source("${fileName}")`;
          break;
        default:
          rCode = `# File loaded: ${fileName}
# Use appropriate R function to read this file type`;
      }
      await this.evalInConsole(rCode);
    });
    fileItem.appendChild(loadButton);
    this.fileList.appendChild(fileItem);
  }
  handleOutput(msg) {
    switch (msg.type) {
      case "stdout":
        this.appendToOutEl(msg.data + "\n");
        break;
      case "stderr":
        this.appendToOutEl(msg.data + "\n");
        break;
      case "prompt":
        console.log("prompt");
        this.appendToOutEl(msg.data);
        break;
      case "canvas":
        this.handleImage(msg.data.image);
        break;
      case "closed":
        return;
      default:
        console.warn(`Unhandled output type for webR: ${msg.type}.`);
    }
  }
  handleImage(img) {
    const canvas = document.createElement("canvas");
    canvas.style.width = `${img.width / 2}px`;
    canvas.style.height = `${img.height / 2}px`;
    canvas.style.margin = "2px";
    canvas.style.border = "1px solid black";
    canvas.style.borderRadius = "3";
    canvas.width = img.width;
    canvas.height = img.height;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(img, 0, 0, img.width, img.height);
    this.plot.insertBefore(canvas, this.plot.firstChild);
  }
  async evalInConsole(code) {
    this.appendToOutEl(code + "\n");
    const shelter = await new this.webR.Shelter();
    const res = await shelter.captureR(code, {
      withAutoprint: true,
      captureGraphics: {
        width: PLOT_WIDTH,
        height: PLOT_HEIGHT
      }
    });
    const moreResults = await this.webR.flush();
    res.output.forEach((msg) => this.handleOutput(msg));
    res.images.forEach((img) => this.handleImage(img));
    console.log(res);
    console.log(moreResults);
    let resultJson = {
      type: "null"
    };
    let imagesJson = [];
    try {
      resultJson = await res.result.toJs();
      imagesJson = await Promise.all(
        res.images.map(async (img) => {
          return await imageBitmapToPngBase64(img);
        })
      );
    } catch (e4) {
      console.warn(e4);
    }
    const newResult = {
      ...res,
      result: resultJson,
      images: imagesJson
    };
    await shelter.purge();
    this.prompt();
    return newResult;
  }
  prompt() {
    this.appendToOutEl("> ");
  }
  appendToOutEl(line) {
    this.output.append(line);
    const parent = this.output.parentElement;
    parent.scrollTo({
      top: parent.scrollHeight,
      behavior: "smooth"
    });
  }
};
customElements.define(WEBR_COMPONENT_TAG, WebRComponent);
window.Shiny.addCustomMessageHandler("eval_r", async function(message) {
  const el = document.getElementById(message.id);
  const result = await el.evalInConsole(message.code);
  window.Shiny.shinyapp.makeRequest(
    message.handler_id,
    [result],
    // eslint-disable-next-line @typescript-eslint/no-empty-function
    (msg) => {
    },
    // eslint-disable-next-line @typescript-eslint/no-empty-function
    (msg) => {
    },
    void 0
  );
});
async function imageBitmapToPngBase64(bitmap) {
  const canvas = document.createElement("canvas");
  canvas.width = bitmap.width;
  canvas.height = bitmap.height;
  const ctx = canvas.getContext("2d");
  if (!ctx) {
    throw new Error("Could not get canvas context");
  }
  ctx.drawImage(bitmap, 0, 0);
  const dataURL = canvas.toDataURL("image/png");
  const base64Data = dataURL.split(",")[1];
  return base64Data;
}
/*! Bundled license information:

@lit/reactive-element/css-tag.js:
  (**
   * @license
   * Copyright 2019 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

@lit/reactive-element/reactive-element.js:
  (**
   * @license
   * Copyright 2017 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

lit-html/lit-html.js:
  (**
   * @license
   * Copyright 2017 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

lit-element/lit-element.js:
  (**
   * @license
   * Copyright 2017 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

lit-html/is-server.js:
  (**
   * @license
   * Copyright 2022 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)
*/
//# sourceMappingURL=webr.js.map
