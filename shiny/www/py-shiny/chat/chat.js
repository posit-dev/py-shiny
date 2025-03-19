var __defProp = Object.defineProperty;
var __getOwnPropDesc = Object.getOwnPropertyDescriptor;
var __decorateClass = (decorators, target, key, kind) => {
  var result = kind > 1 ? void 0 : kind ? __getOwnPropDesc(target, key) : target;
  for (var i5 = decorators.length - 1, decorator; i5 >= 0; i5--)
    if (decorator = decorators[i5])
      result = (kind ? decorator(target, key, result) : decorator(result)) || result;
  if (kind && result)
    __defProp(target, key, result);
  return result;
};

// node_modules/@lit/reactive-element/css-tag.js
var t = globalThis;
var e = t.ShadowRoot && (void 0 === t.ShadyCSS || t.ShadyCSS.nativeShadow) && "adoptedStyleSheets" in Document.prototype && "replace" in CSSStyleSheet.prototype;
var s = Symbol();
var o = /* @__PURE__ */ new WeakMap();
var n = class {
  constructor(t4, e7, o6) {
    if (this._$cssResult$ = true, o6 !== s)
      throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");
    this.cssText = t4, this.t = e7;
  }
  get styleSheet() {
    let t4 = this.o;
    const s4 = this.t;
    if (e && void 0 === t4) {
      const e7 = void 0 !== s4 && 1 === s4.length;
      e7 && (t4 = o.get(s4)), void 0 === t4 && ((this.o = t4 = new CSSStyleSheet()).replaceSync(this.cssText), e7 && o.set(s4, t4));
    }
    return t4;
  }
  toString() {
    return this.cssText;
  }
};
var r = (t4) => new n("string" == typeof t4 ? t4 : t4 + "", void 0, s);
var S = (s4, o6) => {
  if (e)
    s4.adoptedStyleSheets = o6.map((t4) => t4 instanceof CSSStyleSheet ? t4 : t4.styleSheet);
  else
    for (const e7 of o6) {
      const o7 = document.createElement("style"), n5 = t.litNonce;
      void 0 !== n5 && o7.setAttribute("nonce", n5), o7.textContent = e7.cssText, s4.appendChild(o7);
    }
};
var c = e ? (t4) => t4 : (t4) => t4 instanceof CSSStyleSheet ? ((t5) => {
  let e7 = "";
  for (const s4 of t5.cssRules)
    e7 += s4.cssText;
  return r(e7);
})(t4) : t4;

// node_modules/@lit/reactive-element/reactive-element.js
var { is: i2, defineProperty: e2, getOwnPropertyDescriptor: r2, getOwnPropertyNames: h, getOwnPropertySymbols: o2, getPrototypeOf: n2 } = Object;
var a = globalThis;
var c2 = a.trustedTypes;
var l = c2 ? c2.emptyScript : "";
var p = a.reactiveElementPolyfillSupport;
var d = (t4, s4) => t4;
var u = { toAttribute(t4, s4) {
  switch (s4) {
    case Boolean:
      t4 = t4 ? l : null;
      break;
    case Object:
    case Array:
      t4 = null == t4 ? t4 : JSON.stringify(t4);
  }
  return t4;
}, fromAttribute(t4, s4) {
  let i5 = t4;
  switch (s4) {
    case Boolean:
      i5 = null !== t4;
      break;
    case Number:
      i5 = null === t4 ? null : Number(t4);
      break;
    case Object:
    case Array:
      try {
        i5 = JSON.parse(t4);
      } catch (t5) {
        i5 = null;
      }
  }
  return i5;
} };
var f = (t4, s4) => !i2(t4, s4);
var y = { attribute: true, type: String, converter: u, reflect: false, hasChanged: f };
Symbol.metadata ??= Symbol("metadata"), a.litPropertyMetadata ??= /* @__PURE__ */ new WeakMap();
var b = class extends HTMLElement {
  static addInitializer(t4) {
    this._$Ei(), (this.l ??= []).push(t4);
  }
  static get observedAttributes() {
    return this.finalize(), this._$Eh && [...this._$Eh.keys()];
  }
  static createProperty(t4, s4 = y) {
    if (s4.state && (s4.attribute = false), this._$Ei(), this.elementProperties.set(t4, s4), !s4.noAccessor) {
      const i5 = Symbol(), r6 = this.getPropertyDescriptor(t4, i5, s4);
      void 0 !== r6 && e2(this.prototype, t4, r6);
    }
  }
  static getPropertyDescriptor(t4, s4, i5) {
    const { get: e7, set: h3 } = r2(this.prototype, t4) ?? { get() {
      return this[s4];
    }, set(t5) {
      this[s4] = t5;
    } };
    return { get() {
      return e7?.call(this);
    }, set(s5) {
      const r6 = e7?.call(this);
      h3.call(this, s5), this.requestUpdate(t4, r6, i5);
    }, configurable: true, enumerable: true };
  }
  static getPropertyOptions(t4) {
    return this.elementProperties.get(t4) ?? y;
  }
  static _$Ei() {
    if (this.hasOwnProperty(d("elementProperties")))
      return;
    const t4 = n2(this);
    t4.finalize(), void 0 !== t4.l && (this.l = [...t4.l]), this.elementProperties = new Map(t4.elementProperties);
  }
  static finalize() {
    if (this.hasOwnProperty(d("finalized")))
      return;
    if (this.finalized = true, this._$Ei(), this.hasOwnProperty(d("properties"))) {
      const t5 = this.properties, s4 = [...h(t5), ...o2(t5)];
      for (const i5 of s4)
        this.createProperty(i5, t5[i5]);
    }
    const t4 = this[Symbol.metadata];
    if (null !== t4) {
      const s4 = litPropertyMetadata.get(t4);
      if (void 0 !== s4)
        for (const [t5, i5] of s4)
          this.elementProperties.set(t5, i5);
    }
    this._$Eh = /* @__PURE__ */ new Map();
    for (const [t5, s4] of this.elementProperties) {
      const i5 = this._$Eu(t5, s4);
      void 0 !== i5 && this._$Eh.set(i5, t5);
    }
    this.elementStyles = this.finalizeStyles(this.styles);
  }
  static finalizeStyles(s4) {
    const i5 = [];
    if (Array.isArray(s4)) {
      const e7 = new Set(s4.flat(1 / 0).reverse());
      for (const s5 of e7)
        i5.unshift(c(s5));
    } else
      void 0 !== s4 && i5.push(c(s4));
    return i5;
  }
  static _$Eu(t4, s4) {
    const i5 = s4.attribute;
    return false === i5 ? void 0 : "string" == typeof i5 ? i5 : "string" == typeof t4 ? t4.toLowerCase() : void 0;
  }
  constructor() {
    super(), this._$Ep = void 0, this.isUpdatePending = false, this.hasUpdated = false, this._$Em = null, this._$Ev();
  }
  _$Ev() {
    this._$ES = new Promise((t4) => this.enableUpdating = t4), this._$AL = /* @__PURE__ */ new Map(), this._$E_(), this.requestUpdate(), this.constructor.l?.forEach((t4) => t4(this));
  }
  addController(t4) {
    (this._$EO ??= /* @__PURE__ */ new Set()).add(t4), void 0 !== this.renderRoot && this.isConnected && t4.hostConnected?.();
  }
  removeController(t4) {
    this._$EO?.delete(t4);
  }
  _$E_() {
    const t4 = /* @__PURE__ */ new Map(), s4 = this.constructor.elementProperties;
    for (const i5 of s4.keys())
      this.hasOwnProperty(i5) && (t4.set(i5, this[i5]), delete this[i5]);
    t4.size > 0 && (this._$Ep = t4);
  }
  createRenderRoot() {
    const t4 = this.shadowRoot ?? this.attachShadow(this.constructor.shadowRootOptions);
    return S(t4, this.constructor.elementStyles), t4;
  }
  connectedCallback() {
    this.renderRoot ??= this.createRenderRoot(), this.enableUpdating(true), this._$EO?.forEach((t4) => t4.hostConnected?.());
  }
  enableUpdating(t4) {
  }
  disconnectedCallback() {
    this._$EO?.forEach((t4) => t4.hostDisconnected?.());
  }
  attributeChangedCallback(t4, s4, i5) {
    this._$AK(t4, i5);
  }
  _$EC(t4, s4) {
    const i5 = this.constructor.elementProperties.get(t4), e7 = this.constructor._$Eu(t4, i5);
    if (void 0 !== e7 && true === i5.reflect) {
      const r6 = (void 0 !== i5.converter?.toAttribute ? i5.converter : u).toAttribute(s4, i5.type);
      this._$Em = t4, null == r6 ? this.removeAttribute(e7) : this.setAttribute(e7, r6), this._$Em = null;
    }
  }
  _$AK(t4, s4) {
    const i5 = this.constructor, e7 = i5._$Eh.get(t4);
    if (void 0 !== e7 && this._$Em !== e7) {
      const t5 = i5.getPropertyOptions(e7), r6 = "function" == typeof t5.converter ? { fromAttribute: t5.converter } : void 0 !== t5.converter?.fromAttribute ? t5.converter : u;
      this._$Em = e7, this[e7] = r6.fromAttribute(s4, t5.type), this._$Em = null;
    }
  }
  requestUpdate(t4, s4, i5) {
    if (void 0 !== t4) {
      if (i5 ??= this.constructor.getPropertyOptions(t4), !(i5.hasChanged ?? f)(this[t4], s4))
        return;
      this.P(t4, s4, i5);
    }
    false === this.isUpdatePending && (this._$ES = this._$ET());
  }
  P(t4, s4, i5) {
    this._$AL.has(t4) || this._$AL.set(t4, s4), true === i5.reflect && this._$Em !== t4 && (this._$Ej ??= /* @__PURE__ */ new Set()).add(t4);
  }
  async _$ET() {
    this.isUpdatePending = true;
    try {
      await this._$ES;
    } catch (t5) {
      Promise.reject(t5);
    }
    const t4 = this.scheduleUpdate();
    return null != t4 && await t4, !this.isUpdatePending;
  }
  scheduleUpdate() {
    return this.performUpdate();
  }
  performUpdate() {
    if (!this.isUpdatePending)
      return;
    if (!this.hasUpdated) {
      if (this.renderRoot ??= this.createRenderRoot(), this._$Ep) {
        for (const [t6, s5] of this._$Ep)
          this[t6] = s5;
        this._$Ep = void 0;
      }
      const t5 = this.constructor.elementProperties;
      if (t5.size > 0)
        for (const [s5, i5] of t5)
          true !== i5.wrapped || this._$AL.has(s5) || void 0 === this[s5] || this.P(s5, this[s5], i5);
    }
    let t4 = false;
    const s4 = this._$AL;
    try {
      t4 = this.shouldUpdate(s4), t4 ? (this.willUpdate(s4), this._$EO?.forEach((t5) => t5.hostUpdate?.()), this.update(s4)) : this._$EU();
    } catch (s5) {
      throw t4 = false, this._$EU(), s5;
    }
    t4 && this._$AE(s4);
  }
  willUpdate(t4) {
  }
  _$AE(t4) {
    this._$EO?.forEach((t5) => t5.hostUpdated?.()), this.hasUpdated || (this.hasUpdated = true, this.firstUpdated(t4)), this.updated(t4);
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
  shouldUpdate(t4) {
    return true;
  }
  update(t4) {
    this._$Ej &&= this._$Ej.forEach((t5) => this._$EC(t5, this[t5])), this._$EU();
  }
  updated(t4) {
  }
  firstUpdated(t4) {
  }
};
b.elementStyles = [], b.shadowRootOptions = { mode: "open" }, b[d("elementProperties")] = /* @__PURE__ */ new Map(), b[d("finalized")] = /* @__PURE__ */ new Map(), p?.({ ReactiveElement: b }), (a.reactiveElementVersions ??= []).push("2.0.4");

// node_modules/lit-html/lit-html.js
var t2 = globalThis;
var i3 = t2.trustedTypes;
var s2 = i3 ? i3.createPolicy("lit-html", { createHTML: (t4) => t4 }) : void 0;
var e3 = "$lit$";
var h2 = `lit$${Math.random().toFixed(9).slice(2)}$`;
var o3 = "?" + h2;
var n3 = `<${o3}>`;
var r3 = document;
var l2 = () => r3.createComment("");
var c3 = (t4) => null === t4 || "object" != typeof t4 && "function" != typeof t4;
var a2 = Array.isArray;
var u2 = (t4) => a2(t4) || "function" == typeof t4?.[Symbol.iterator];
var d2 = "[ 	\n\f\r]";
var f2 = /<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g;
var v = /-->/g;
var _ = />/g;
var m = RegExp(`>|${d2}(?:([^\\s"'>=/]+)(${d2}*=${d2}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`, "g");
var p2 = /'/g;
var g = /"/g;
var $ = /^(?:script|style|textarea|title)$/i;
var y2 = (t4) => (i5, ...s4) => ({ _$litType$: t4, strings: i5, values: s4 });
var x = y2(1);
var b2 = y2(2);
var w = Symbol.for("lit-noChange");
var T = Symbol.for("lit-nothing");
var A = /* @__PURE__ */ new WeakMap();
var E = r3.createTreeWalker(r3, 129);
function C(t4, i5) {
  if (!Array.isArray(t4) || !t4.hasOwnProperty("raw"))
    throw Error("invalid template strings array");
  return void 0 !== s2 ? s2.createHTML(i5) : i5;
}
var P = (t4, i5) => {
  const s4 = t4.length - 1, o6 = [];
  let r6, l3 = 2 === i5 ? "<svg>" : "", c4 = f2;
  for (let i6 = 0; i6 < s4; i6++) {
    const s5 = t4[i6];
    let a3, u3, d3 = -1, y3 = 0;
    for (; y3 < s5.length && (c4.lastIndex = y3, u3 = c4.exec(s5), null !== u3); )
      y3 = c4.lastIndex, c4 === f2 ? "!--" === u3[1] ? c4 = v : void 0 !== u3[1] ? c4 = _ : void 0 !== u3[2] ? ($.test(u3[2]) && (r6 = RegExp("</" + u3[2], "g")), c4 = m) : void 0 !== u3[3] && (c4 = m) : c4 === m ? ">" === u3[0] ? (c4 = r6 ?? f2, d3 = -1) : void 0 === u3[1] ? d3 = -2 : (d3 = c4.lastIndex - u3[2].length, a3 = u3[1], c4 = void 0 === u3[3] ? m : '"' === u3[3] ? g : p2) : c4 === g || c4 === p2 ? c4 = m : c4 === v || c4 === _ ? c4 = f2 : (c4 = m, r6 = void 0);
    const x2 = c4 === m && t4[i6 + 1].startsWith("/>") ? " " : "";
    l3 += c4 === f2 ? s5 + n3 : d3 >= 0 ? (o6.push(a3), s5.slice(0, d3) + e3 + s5.slice(d3) + h2 + x2) : s5 + h2 + (-2 === d3 ? i6 : x2);
  }
  return [C(t4, l3 + (t4[s4] || "<?>") + (2 === i5 ? "</svg>" : "")), o6];
};
var V = class _V {
  constructor({ strings: t4, _$litType$: s4 }, n5) {
    let r6;
    this.parts = [];
    let c4 = 0, a3 = 0;
    const u3 = t4.length - 1, d3 = this.parts, [f3, v2] = P(t4, s4);
    if (this.el = _V.createElement(f3, n5), E.currentNode = this.el.content, 2 === s4) {
      const t5 = this.el.content.firstChild;
      t5.replaceWith(...t5.childNodes);
    }
    for (; null !== (r6 = E.nextNode()) && d3.length < u3; ) {
      if (1 === r6.nodeType) {
        if (r6.hasAttributes())
          for (const t5 of r6.getAttributeNames())
            if (t5.endsWith(e3)) {
              const i5 = v2[a3++], s5 = r6.getAttribute(t5).split(h2), e7 = /([.?@])?(.*)/.exec(i5);
              d3.push({ type: 1, index: c4, name: e7[2], strings: s5, ctor: "." === e7[1] ? k : "?" === e7[1] ? H : "@" === e7[1] ? I : R }), r6.removeAttribute(t5);
            } else
              t5.startsWith(h2) && (d3.push({ type: 6, index: c4 }), r6.removeAttribute(t5));
        if ($.test(r6.tagName)) {
          const t5 = r6.textContent.split(h2), s5 = t5.length - 1;
          if (s5 > 0) {
            r6.textContent = i3 ? i3.emptyScript : "";
            for (let i5 = 0; i5 < s5; i5++)
              r6.append(t5[i5], l2()), E.nextNode(), d3.push({ type: 2, index: ++c4 });
            r6.append(t5[s5], l2());
          }
        }
      } else if (8 === r6.nodeType)
        if (r6.data === o3)
          d3.push({ type: 2, index: c4 });
        else {
          let t5 = -1;
          for (; -1 !== (t5 = r6.data.indexOf(h2, t5 + 1)); )
            d3.push({ type: 7, index: c4 }), t5 += h2.length - 1;
        }
      c4++;
    }
  }
  static createElement(t4, i5) {
    const s4 = r3.createElement("template");
    return s4.innerHTML = t4, s4;
  }
};
function N(t4, i5, s4 = t4, e7) {
  if (i5 === w)
    return i5;
  let h3 = void 0 !== e7 ? s4._$Co?.[e7] : s4._$Cl;
  const o6 = c3(i5) ? void 0 : i5._$litDirective$;
  return h3?.constructor !== o6 && (h3?._$AO?.(false), void 0 === o6 ? h3 = void 0 : (h3 = new o6(t4), h3._$AT(t4, s4, e7)), void 0 !== e7 ? (s4._$Co ??= [])[e7] = h3 : s4._$Cl = h3), void 0 !== h3 && (i5 = N(t4, h3._$AS(t4, i5.values), h3, e7)), i5;
}
var S2 = class {
  constructor(t4, i5) {
    this._$AV = [], this._$AN = void 0, this._$AD = t4, this._$AM = i5;
  }
  get parentNode() {
    return this._$AM.parentNode;
  }
  get _$AU() {
    return this._$AM._$AU;
  }
  u(t4) {
    const { el: { content: i5 }, parts: s4 } = this._$AD, e7 = (t4?.creationScope ?? r3).importNode(i5, true);
    E.currentNode = e7;
    let h3 = E.nextNode(), o6 = 0, n5 = 0, l3 = s4[0];
    for (; void 0 !== l3; ) {
      if (o6 === l3.index) {
        let i6;
        2 === l3.type ? i6 = new M(h3, h3.nextSibling, this, t4) : 1 === l3.type ? i6 = new l3.ctor(h3, l3.name, l3.strings, this, t4) : 6 === l3.type && (i6 = new L(h3, this, t4)), this._$AV.push(i6), l3 = s4[++n5];
      }
      o6 !== l3?.index && (h3 = E.nextNode(), o6++);
    }
    return E.currentNode = r3, e7;
  }
  p(t4) {
    let i5 = 0;
    for (const s4 of this._$AV)
      void 0 !== s4 && (void 0 !== s4.strings ? (s4._$AI(t4, s4, i5), i5 += s4.strings.length - 2) : s4._$AI(t4[i5])), i5++;
  }
};
var M = class _M {
  get _$AU() {
    return this._$AM?._$AU ?? this._$Cv;
  }
  constructor(t4, i5, s4, e7) {
    this.type = 2, this._$AH = T, this._$AN = void 0, this._$AA = t4, this._$AB = i5, this._$AM = s4, this.options = e7, this._$Cv = e7?.isConnected ?? true;
  }
  get parentNode() {
    let t4 = this._$AA.parentNode;
    const i5 = this._$AM;
    return void 0 !== i5 && 11 === t4?.nodeType && (t4 = i5.parentNode), t4;
  }
  get startNode() {
    return this._$AA;
  }
  get endNode() {
    return this._$AB;
  }
  _$AI(t4, i5 = this) {
    t4 = N(this, t4, i5), c3(t4) ? t4 === T || null == t4 || "" === t4 ? (this._$AH !== T && this._$AR(), this._$AH = T) : t4 !== this._$AH && t4 !== w && this._(t4) : void 0 !== t4._$litType$ ? this.$(t4) : void 0 !== t4.nodeType ? this.T(t4) : u2(t4) ? this.k(t4) : this._(t4);
  }
  S(t4) {
    return this._$AA.parentNode.insertBefore(t4, this._$AB);
  }
  T(t4) {
    this._$AH !== t4 && (this._$AR(), this._$AH = this.S(t4));
  }
  _(t4) {
    this._$AH !== T && c3(this._$AH) ? this._$AA.nextSibling.data = t4 : this.T(r3.createTextNode(t4)), this._$AH = t4;
  }
  $(t4) {
    const { values: i5, _$litType$: s4 } = t4, e7 = "number" == typeof s4 ? this._$AC(t4) : (void 0 === s4.el && (s4.el = V.createElement(C(s4.h, s4.h[0]), this.options)), s4);
    if (this._$AH?._$AD === e7)
      this._$AH.p(i5);
    else {
      const t5 = new S2(e7, this), s5 = t5.u(this.options);
      t5.p(i5), this.T(s5), this._$AH = t5;
    }
  }
  _$AC(t4) {
    let i5 = A.get(t4.strings);
    return void 0 === i5 && A.set(t4.strings, i5 = new V(t4)), i5;
  }
  k(t4) {
    a2(this._$AH) || (this._$AH = [], this._$AR());
    const i5 = this._$AH;
    let s4, e7 = 0;
    for (const h3 of t4)
      e7 === i5.length ? i5.push(s4 = new _M(this.S(l2()), this.S(l2()), this, this.options)) : s4 = i5[e7], s4._$AI(h3), e7++;
    e7 < i5.length && (this._$AR(s4 && s4._$AB.nextSibling, e7), i5.length = e7);
  }
  _$AR(t4 = this._$AA.nextSibling, i5) {
    for (this._$AP?.(false, true, i5); t4 && t4 !== this._$AB; ) {
      const i6 = t4.nextSibling;
      t4.remove(), t4 = i6;
    }
  }
  setConnected(t4) {
    void 0 === this._$AM && (this._$Cv = t4, this._$AP?.(t4));
  }
};
var R = class {
  get tagName() {
    return this.element.tagName;
  }
  get _$AU() {
    return this._$AM._$AU;
  }
  constructor(t4, i5, s4, e7, h3) {
    this.type = 1, this._$AH = T, this._$AN = void 0, this.element = t4, this.name = i5, this._$AM = e7, this.options = h3, s4.length > 2 || "" !== s4[0] || "" !== s4[1] ? (this._$AH = Array(s4.length - 1).fill(new String()), this.strings = s4) : this._$AH = T;
  }
  _$AI(t4, i5 = this, s4, e7) {
    const h3 = this.strings;
    let o6 = false;
    if (void 0 === h3)
      t4 = N(this, t4, i5, 0), o6 = !c3(t4) || t4 !== this._$AH && t4 !== w, o6 && (this._$AH = t4);
    else {
      const e8 = t4;
      let n5, r6;
      for (t4 = h3[0], n5 = 0; n5 < h3.length - 1; n5++)
        r6 = N(this, e8[s4 + n5], i5, n5), r6 === w && (r6 = this._$AH[n5]), o6 ||= !c3(r6) || r6 !== this._$AH[n5], r6 === T ? t4 = T : t4 !== T && (t4 += (r6 ?? "") + h3[n5 + 1]), this._$AH[n5] = r6;
    }
    o6 && !e7 && this.j(t4);
  }
  j(t4) {
    t4 === T ? this.element.removeAttribute(this.name) : this.element.setAttribute(this.name, t4 ?? "");
  }
};
var k = class extends R {
  constructor() {
    super(...arguments), this.type = 3;
  }
  j(t4) {
    this.element[this.name] = t4 === T ? void 0 : t4;
  }
};
var H = class extends R {
  constructor() {
    super(...arguments), this.type = 4;
  }
  j(t4) {
    this.element.toggleAttribute(this.name, !!t4 && t4 !== T);
  }
};
var I = class extends R {
  constructor(t4, i5, s4, e7, h3) {
    super(t4, i5, s4, e7, h3), this.type = 5;
  }
  _$AI(t4, i5 = this) {
    if ((t4 = N(this, t4, i5, 0) ?? T) === w)
      return;
    const s4 = this._$AH, e7 = t4 === T && s4 !== T || t4.capture !== s4.capture || t4.once !== s4.once || t4.passive !== s4.passive, h3 = t4 !== T && (s4 === T || e7);
    e7 && this.element.removeEventListener(this.name, this, s4), h3 && this.element.addEventListener(this.name, this, t4), this._$AH = t4;
  }
  handleEvent(t4) {
    "function" == typeof this._$AH ? this._$AH.call(this.options?.host ?? this.element, t4) : this._$AH.handleEvent(t4);
  }
};
var L = class {
  constructor(t4, i5, s4) {
    this.element = t4, this.type = 6, this._$AN = void 0, this._$AM = i5, this.options = s4;
  }
  get _$AU() {
    return this._$AM._$AU;
  }
  _$AI(t4) {
    N(this, t4);
  }
};
var Z = t2.litHtmlPolyfillSupport;
Z?.(V, M), (t2.litHtmlVersions ??= []).push("3.1.3");
var j = (t4, i5, s4) => {
  const e7 = s4?.renderBefore ?? i5;
  let h3 = e7._$litPart$;
  if (void 0 === h3) {
    const t5 = s4?.renderBefore ?? null;
    e7._$litPart$ = h3 = new M(i5.insertBefore(l2(), t5), t5, void 0, s4 ?? {});
  }
  return h3._$AI(t4), h3;
};

// node_modules/lit-element/lit-element.js
var s3 = class extends b {
  constructor() {
    super(...arguments), this.renderOptions = { host: this }, this._$Do = void 0;
  }
  createRenderRoot() {
    const t4 = super.createRenderRoot();
    return this.renderOptions.renderBefore ??= t4.firstChild, t4;
  }
  update(t4) {
    const i5 = this.render();
    this.hasUpdated || (this.renderOptions.isConnected = this.isConnected), super.update(t4), this._$Do = j(i5, this.renderRoot, this.renderOptions);
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

// node_modules/lit-html/directive.js
var t3 = { ATTRIBUTE: 1, CHILD: 2, PROPERTY: 3, BOOLEAN_ATTRIBUTE: 4, EVENT: 5, ELEMENT: 6 };
var e4 = (t4) => (...e7) => ({ _$litDirective$: t4, values: e7 });
var i4 = class {
  constructor(t4) {
  }
  get _$AU() {
    return this._$AM._$AU;
  }
  _$AT(t4, e7, i5) {
    this._$Ct = t4, this._$AM = e7, this._$Ci = i5;
  }
  _$AS(t4, e7) {
    return this.update(t4, e7);
  }
  update(t4, e7) {
    return this.render(...e7);
  }
};

// node_modules/lit-html/directives/unsafe-html.js
var e5 = class extends i4 {
  constructor(i5) {
    if (super(i5), this.it = T, i5.type !== t3.CHILD)
      throw Error(this.constructor.directiveName + "() can only be used in child bindings");
  }
  render(r6) {
    if (r6 === T || null == r6)
      return this._t = void 0, this.it = r6;
    if (r6 === w)
      return r6;
    if ("string" != typeof r6)
      throw Error(this.constructor.directiveName + "() called with a non-string value");
    if (r6 === this.it)
      return this._t;
    this.it = r6;
    const s4 = [r6];
    return s4.raw = s4, this._t = { _$litType$: this.constructor.resultType, strings: s4, values: [] };
  }
};
e5.directiveName = "unsafeHTML", e5.resultType = 1;
var o4 = e4(e5);

// node_modules/@lit/reactive-element/decorators/property.js
var o5 = { attribute: true, type: String, converter: u, reflect: false, hasChanged: f };
var r5 = (t4 = o5, e7, r6) => {
  const { kind: n5, metadata: i5 } = r6;
  let s4 = globalThis.litPropertyMetadata.get(i5);
  if (void 0 === s4 && globalThis.litPropertyMetadata.set(i5, s4 = /* @__PURE__ */ new Map()), s4.set(r6.name, t4), "accessor" === n5) {
    const { name: o6 } = r6;
    return { set(r7) {
      const n6 = e7.get.call(this);
      e7.set.call(this, r7), this.requestUpdate(o6, n6, t4);
    }, init(e8) {
      return void 0 !== e8 && this.P(o6, void 0, t4), e8;
    } };
  }
  if ("setter" === n5) {
    const { name: o6 } = r6;
    return function(r7) {
      const n6 = this[o6];
      e7.call(this, r7), this.requestUpdate(o6, n6, t4);
    };
  }
  throw Error("Unsupported decorator location: " + n5);
};
function n4(t4) {
  return (e7, o6) => "object" == typeof o6 ? r5(t4, e7, o6) : ((t5, e8, o7) => {
    const r6 = e8.hasOwnProperty(o7);
    return e8.constructor.createProperty(o7, r6 ? { ...t5, wrapped: true } : t5), r6 ? Object.getOwnPropertyDescriptor(e8, o7) : void 0;
  })(t4, e7, o6);
}

// utils/_utils.ts
function createElement(tag_name, attrs) {
  const el = document.createElement(tag_name);
  for (const [key, value] of Object.entries(attrs)) {
    if (value !== null)
      el.setAttribute(key, value);
  }
  return el;
}
var LightElement = class extends s3 {
  createRenderRoot() {
    return this;
  }
};
function showShinyClientMessage({
  headline = "",
  message,
  status = "warning"
}) {
  document.dispatchEvent(
    new CustomEvent("shiny:client-message", {
      detail: { headline, message, status }
    })
  );
}

// chat/chat.ts
var CHAT_MESSAGE_TAG = "shiny-chat-message";
var CHAT_USER_MESSAGE_TAG = "shiny-user-message";
var CHAT_MESSAGES_TAG = "shiny-chat-messages";
var CHAT_INPUT_TAG = "shiny-chat-input";
var CHAT_CONTAINER_TAG = "shiny-chat-container";
var ICONS = {
  robot: '<svg fill="currentColor" class="bi bi-robot" viewBox="0 0 16 16" xmlns="http://www.w3.org/2000/svg"><path d="M6 12.5a.5.5 0 0 1 .5-.5h3a.5.5 0 0 1 0 1h-3a.5.5 0 0 1-.5-.5M3 8.062C3 6.76 4.235 5.765 5.53 5.886a26.6 26.6 0 0 0 4.94 0C11.765 5.765 13 6.76 13 8.062v1.157a.93.93 0 0 1-.765.935c-.845.147-2.34.346-4.235.346s-3.39-.2-4.235-.346A.93.93 0 0 1 3 9.219zm4.542-.827a.25.25 0 0 0-.217.068l-.92.9a25 25 0 0 1-1.871-.183.25.25 0 0 0-.068.495c.55.076 1.232.149 2.02.193a.25.25 0 0 0 .189-.071l.754-.736.847 1.71a.25.25 0 0 0 .404.062l.932-.97a25 25 0 0 0 1.922-.188.25.25 0 0 0-.068-.495c-.538.074-1.207.145-1.98.189a.25.25 0 0 0-.166.076l-.754.785-.842-1.7a.25.25 0 0 0-.182-.135"/><path d="M8.5 1.866a1 1 0 1 0-1 0V3h-2A4.5 4.5 0 0 0 1 7.5V8a1 1 0 0 0-1 1v2a1 1 0 0 0 1 1v1a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-1a1 1 0 0 0 1-1V9a1 1 0 0 0-1-1v-.5A4.5 4.5 0 0 0 10.5 3h-2zM14 7.5V13a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V7.5A3.5 3.5 0 0 1 5.5 4h5A3.5 3.5 0 0 1 14 7.5"/></svg>',
  // https://github.com/n3r4zzurr0/svg-spinners/blob/main/svg-css/3-dots-fade.svg
  dots_fade: '<svg width="24" height="24" fill="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><style>.spinner_S1WN{animation:spinner_MGfb .8s linear infinite;animation-delay:-.8s}.spinner_Km9P{animation-delay:-.65s}.spinner_JApP{animation-delay:-.5s}@keyframes spinner_MGfb{93.75%,100%{opacity:.2}}</style><circle class="spinner_S1WN" cx="4" cy="12" r="3"/><circle class="spinner_S1WN spinner_Km9P" cx="12" cy="12" r="3"/><circle class="spinner_S1WN spinner_JApP" cx="20" cy="12" r="3"/></svg>'
};
var ChatMessage = class extends LightElement {
  constructor() {
    super(...arguments);
    this.content = "...";
    this.content_type = "markdown";
    this.streaming = false;
    this.icon = "";
  }
  render() {
    const isEmpty = this.content.trim().length === 0;
    const icon = isEmpty ? ICONS.dots_fade : this.icon || ICONS.robot;
    return x`
      <div class="message-icon">${o4(icon)}</div>
      <shiny-markdown-stream
        content=${this.content}
        content-type=${this.content_type}
        ?streaming=${this.streaming}
        auto-scroll
        .onContentChange=${this.#onContentChange.bind(this)}
        .onStreamEnd=${this.#makeSuggestionsAccessible.bind(this)}
      ></shiny-markdown-stream>
    `;
  }
  #onContentChange() {
    if (!this.streaming)
      this.#makeSuggestionsAccessible();
  }
  #makeSuggestionsAccessible() {
    this.querySelectorAll(".suggestion,[data-suggestion]").forEach((el) => {
      if (!(el instanceof HTMLElement))
        return;
      if (el.hasAttribute("tabindex"))
        return;
      el.setAttribute("tabindex", "0");
      el.setAttribute("role", "button");
      const suggestion = el.dataset.suggestion || el.textContent;
      el.setAttribute("aria-label", `Use chat suggestion: ${suggestion}`);
    });
  }
};
__decorateClass([
  n4()
], ChatMessage.prototype, "content", 2);
__decorateClass([
  n4()
], ChatMessage.prototype, "content_type", 2);
__decorateClass([
  n4({ type: Boolean, reflect: true })
], ChatMessage.prototype, "streaming", 2);
__decorateClass([
  n4()
], ChatMessage.prototype, "icon", 2);
var ChatUserMessage = class extends LightElement {
  constructor() {
    super(...arguments);
    this.content = "...";
  }
  render() {
    return x`
      <shiny-markdown-stream
        content=${this.content}
        content-type="semi-markdown"
      ></shiny-markdown-stream>
    `;
  }
};
__decorateClass([
  n4()
], ChatUserMessage.prototype, "content", 2);
var ChatMessages = class extends LightElement {
  render() {
    return x``;
  }
};
var ChatInput = class extends LightElement {
  constructor() {
    super(...arguments);
    this._disabled = false;
    this.placeholder = "Enter a message...";
  }
  get disabled() {
    return this._disabled;
  }
  set disabled(value) {
    const oldValue = this._disabled;
    if (value === oldValue) {
      return;
    }
    this._disabled = value;
    value ? this.setAttribute("disabled", "") : this.removeAttribute("disabled");
    this.requestUpdate("disabled", oldValue);
    this.#onInput();
  }
  attributeChangedCallback(name, _old, value) {
    super.attributeChangedCallback(name, _old, value);
    if (name === "disabled") {
      this.disabled = value !== null;
    }
  }
  get textarea() {
    return this.querySelector("textarea");
  }
  get value() {
    return this.textarea.value;
  }
  get valueIsEmpty() {
    return this.value.trim().length === 0;
  }
  get button() {
    return this.querySelector("button");
  }
  render() {
    const icon = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" class="bi bi-arrow-up-circle-fill" viewBox="0 0 16 16"><path d="M16 8A8 8 0 1 0 0 8a8 8 0 0 0 16 0m-7.5 3.5a.5.5 0 0 1-1 0V5.707L5.354 7.854a.5.5 0 1 1-.708-.708l3-3a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1-.708.708L8.5 5.707z"/></svg>';
    return x`
      <textarea
        id="${this.id}"
        class="form-control textarea-autoresize"
        rows="1"
        placeholder="${this.placeholder}"
        @keydown=${this.#onKeyDown}
        @input=${this.#onInput}
        data-shiny-no-bind-input
      ></textarea>
      <button
        type="button"
        title="Send message"
        aria-label="Send message"
        @click=${this.#sendInput}
      >
        ${o4(icon)}
      </button>
    `;
  }
  // Pressing enter sends the message (if not empty)
  #onKeyDown(e7) {
    const isEnter = e7.code === "Enter" && !e7.shiftKey;
    if (isEnter && !this.valueIsEmpty) {
      e7.preventDefault();
      this.#sendInput();
    }
  }
  #onInput() {
    this.button.disabled = this.disabled ? true : this.value.trim().length === 0;
  }
  // Determine whether the button should be enabled/disabled on first render
  firstUpdated() {
    this.#onInput();
  }
  #sendInput(focus = true) {
    if (this.valueIsEmpty)
      return;
    if (this.disabled)
      return;
    window.Shiny.setInputValue(this.id, this.value, { priority: "event" });
    const sentEvent = new CustomEvent("shiny-chat-input-sent", {
      detail: { content: this.value, role: "user" },
      bubbles: true,
      composed: true
    });
    this.dispatchEvent(sentEvent);
    this.setInputValue("");
    this.disabled = true;
    if (focus)
      this.textarea.focus();
  }
  setInputValue(value, { submit = false, focus = false } = {}) {
    const oldValue = this.textarea.value;
    this.textarea.value = value;
    const inputEvent = new Event("input", { bubbles: true, cancelable: true });
    this.textarea.dispatchEvent(inputEvent);
    if (submit) {
      this.#sendInput(false);
      if (oldValue)
        this.setInputValue(oldValue);
    }
    if (focus) {
      this.textarea.focus();
    }
  }
};
__decorateClass([
  n4()
], ChatInput.prototype, "placeholder", 2);
__decorateClass([
  n4({ type: Boolean })
], ChatInput.prototype, "disabled", 1);
var ChatContainer = class extends LightElement {
  constructor() {
    super(...arguments);
    this.iconAssistant = "";
  }
  get input() {
    return this.querySelector(CHAT_INPUT_TAG);
  }
  get messages() {
    return this.querySelector(CHAT_MESSAGES_TAG);
  }
  get lastMessage() {
    const last = this.messages.lastElementChild;
    return last ? last : null;
  }
  render() {
    return x``;
  }
  connectedCallback() {
    super.connectedCallback();
    let sentinel = this.querySelector("div");
    if (!sentinel) {
      sentinel = createElement("div", {
        style: "width: 100%; height: 0;"
      });
      this.input.insertAdjacentElement("afterend", sentinel);
    }
    this.inputSentinelObserver = new IntersectionObserver(
      (entries) => {
        const inputTextarea = this.input.querySelector("textarea");
        if (!inputTextarea)
          return;
        const addShadow = entries[0]?.intersectionRatio === 0;
        inputTextarea.classList.toggle("shadow", addShadow);
      },
      {
        threshold: [0, 1],
        rootMargin: "0px"
      }
    );
    this.inputSentinelObserver.observe(sentinel);
  }
  firstUpdated() {
    if (!this.messages)
      return;
    this.addEventListener("shiny-chat-input-sent", this.#onInputSent);
    this.addEventListener("shiny-chat-append-message", this.#onAppend);
    this.addEventListener(
      "shiny-chat-append-message-chunk",
      this.#onAppendChunk
    );
    this.addEventListener("shiny-chat-clear-messages", this.#onClear);
    this.addEventListener(
      "shiny-chat-update-user-input",
      this.#onUpdateUserInput
    );
    this.addEventListener(
      "shiny-chat-remove-loading-message",
      this.#onRemoveLoadingMessage
    );
    this.addEventListener("click", this.#onInputSuggestionClick);
    this.addEventListener("keydown", this.#onInputSuggestionKeydown);
  }
  disconnectedCallback() {
    super.disconnectedCallback();
    this.inputSentinelObserver?.disconnect();
    this.inputSentinelObserver = void 0;
    this.removeEventListener("shiny-chat-input-sent", this.#onInputSent);
    this.removeEventListener("shiny-chat-append-message", this.#onAppend);
    this.removeEventListener(
      "shiny-chat-append-message-chunk",
      this.#onAppendChunk
    );
    this.removeEventListener("shiny-chat-clear-messages", this.#onClear);
    this.removeEventListener(
      "shiny-chat-update-user-input",
      this.#onUpdateUserInput
    );
    this.removeEventListener(
      "shiny-chat-remove-loading-message",
      this.#onRemoveLoadingMessage
    );
    this.removeEventListener("click", this.#onInputSuggestionClick);
    this.removeEventListener("keydown", this.#onInputSuggestionKeydown);
  }
  // When user submits input, append it to the chat, and add a loading message
  #onInputSent(event) {
    this.#appendMessage(event.detail);
    this.#addLoadingMessage();
  }
  // Handle an append message event from server
  #onAppend(event) {
    this.#appendMessage(event.detail);
  }
  #initMessage() {
    this.#removeLoadingMessage();
    if (!this.input.disabled) {
      this.input.disabled = true;
    }
  }
  #appendMessage(message, finalize = true) {
    this.#initMessage();
    const TAG_NAME = message.role === "user" ? CHAT_USER_MESSAGE_TAG : CHAT_MESSAGE_TAG;
    if (this.iconAssistant) {
      message.icon = message.icon || this.iconAssistant;
    }
    const msg = createElement(TAG_NAME, message);
    this.messages.appendChild(msg);
    if (finalize) {
      this.#finalizeMessage();
    }
  }
  // Loading message is just an empty message
  #addLoadingMessage() {
    const loading_message = {
      content: "",
      role: "assistant"
    };
    const message = createElement(CHAT_MESSAGE_TAG, loading_message);
    this.messages.appendChild(message);
  }
  #removeLoadingMessage() {
    const content = this.lastMessage?.content;
    if (!content)
      this.lastMessage?.remove();
  }
  #onAppendChunk(event) {
    this.#appendMessageChunk(event.detail);
  }
  #appendMessageChunk(message) {
    if (message.chunk_type === "message_start") {
      this.#appendMessage(message, false);
    }
    const lastMessage = this.lastMessage;
    if (!lastMessage)
      throw new Error("No messages found in the chat output");
    if (message.chunk_type === "message_start") {
      lastMessage.setAttribute("streaming", "");
      return;
    }
    const content = message.operation === "append" ? lastMessage.getAttribute("content") + message.content : message.content;
    lastMessage.setAttribute("content", content);
    if (message.chunk_type === "message_end") {
      this.lastMessage?.removeAttribute("streaming");
      this.#finalizeMessage();
    }
  }
  #onClear() {
    this.messages.innerHTML = "";
  }
  #onUpdateUserInput(event) {
    const { value, placeholder, submit, focus } = event.detail;
    if (value !== void 0) {
      this.input.setInputValue(value, { submit, focus });
    }
    if (placeholder !== void 0) {
      this.input.placeholder = placeholder;
    }
  }
  #onInputSuggestionClick(e7) {
    this.#onInputSuggestionEvent(e7);
  }
  #onInputSuggestionKeydown(e7) {
    const isEnterOrSpace = e7.key === "Enter" || e7.key === " ";
    if (!isEnterOrSpace)
      return;
    this.#onInputSuggestionEvent(e7);
  }
  #onInputSuggestionEvent(e7) {
    const { suggestion, submit } = this.#getSuggestion(e7.target);
    if (!suggestion)
      return;
    e7.preventDefault();
    const shouldSubmit = e7.metaKey || e7.ctrlKey ? true : e7.altKey ? false : submit;
    this.input.setInputValue(suggestion, {
      submit: shouldSubmit,
      focus: !shouldSubmit
    });
  }
  #getSuggestion(x2) {
    if (!(x2 instanceof HTMLElement))
      return {};
    const el = x2.closest(".suggestion, [data-suggestion]");
    if (!(el instanceof HTMLElement))
      return {};
    const isSuggestion = el.classList.contains("suggestion") || el.dataset.suggestion !== void 0;
    if (!isSuggestion)
      return {};
    const suggestion = el.dataset.suggestion || el.textContent;
    return {
      suggestion: suggestion || void 0,
      submit: el.classList.contains("submit") || el.dataset.suggestionSubmit === "" || el.dataset.suggestionSubmit === "true"
    };
  }
  #onRemoveLoadingMessage() {
    this.#removeLoadingMessage();
    this.#finalizeMessage();
  }
  #finalizeMessage() {
    this.input.disabled = false;
  }
};
__decorateClass([
  n4({ attribute: "icon-assistant" })
], ChatContainer.prototype, "iconAssistant", 2);
customElements.define(CHAT_MESSAGE_TAG, ChatMessage);
customElements.define(CHAT_USER_MESSAGE_TAG, ChatUserMessage);
customElements.define(CHAT_MESSAGES_TAG, ChatMessages);
customElements.define(CHAT_INPUT_TAG, ChatInput);
customElements.define(CHAT_CONTAINER_TAG, ChatContainer);
window.Shiny.addCustomMessageHandler(
  "shinyChatMessage",
  function(message) {
    const evt = new CustomEvent(message.handler, {
      detail: message.obj
    });
    const el = document.getElementById(message.id);
    if (!el) {
      showShinyClientMessage({
        status: "error",
        message: `Unable to handle Chat() message since element with id
          ${message.id} wasn't found. Do you need to call .ui() (Express) or need a
          chat_ui('${message.id}') in the UI (Core)?
        `
      });
      return;
    }
    el.dispatchEvent(evt);
  }
);
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

lit-html/directive.js:
  (**
   * @license
   * Copyright 2017 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

lit-html/directives/unsafe-html.js:
  (**
   * @license
   * Copyright 2017 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

@lit/reactive-element/decorators/custom-element.js:
  (**
   * @license
   * Copyright 2017 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

@lit/reactive-element/decorators/property.js:
  (**
   * @license
   * Copyright 2017 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

@lit/reactive-element/decorators/state.js:
  (**
   * @license
   * Copyright 2017 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

@lit/reactive-element/decorators/event-options.js:
  (**
   * @license
   * Copyright 2017 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

@lit/reactive-element/decorators/base.js:
  (**
   * @license
   * Copyright 2017 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

@lit/reactive-element/decorators/query.js:
  (**
   * @license
   * Copyright 2017 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

@lit/reactive-element/decorators/query-all.js:
  (**
   * @license
   * Copyright 2017 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

@lit/reactive-element/decorators/query-async.js:
  (**
   * @license
   * Copyright 2017 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

@lit/reactive-element/decorators/query-assigned-elements.js:
  (**
   * @license
   * Copyright 2021 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

@lit/reactive-element/decorators/query-assigned-nodes.js:
  (**
   * @license
   * Copyright 2017 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)
*/
//# sourceMappingURL=chat.js.map
