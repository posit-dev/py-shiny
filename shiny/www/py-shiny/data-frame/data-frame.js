// node_modules/preact/dist/preact.module.js
var n;
var l;
var u;
var t;
var i;
var o;
var r;
var f;
var e;
var c;
var s;
var a;
var h = {};
var p = [];
var v = /acit|ex(?:s|g|n|p|$)|rph|grid|ows|mnc|ntw|ine[ch]|zoo|^ord|itera/i;
var y = Array.isArray;
function d(n2, l3) {
  for (var u3 in l3)
    n2[u3] = l3[u3];
  return n2;
}
function w(n2) {
  var l3 = n2.parentNode;
  l3 && l3.removeChild(n2);
}
function _(l3, u3, t3) {
  var i4, o3, r3, f3 = {};
  for (r3 in u3)
    "key" == r3 ? i4 = u3[r3] : "ref" == r3 ? o3 = u3[r3] : f3[r3] = u3[r3];
  if (arguments.length > 2 && (f3.children = arguments.length > 3 ? n.call(arguments, 2) : t3), "function" == typeof l3 && null != l3.defaultProps)
    for (r3 in l3.defaultProps)
      void 0 === f3[r3] && (f3[r3] = l3.defaultProps[r3]);
  return g(l3, f3, i4, o3, null);
}
function g(n2, t3, i4, o3, r3) {
  var f3 = { type: n2, props: t3, key: i4, ref: o3, __k: null, __: null, __b: 0, __e: null, __d: void 0, __c: null, constructor: void 0, __v: null == r3 ? ++u : r3, __i: -1, __u: 0 };
  return null == r3 && null != l.vnode && l.vnode(f3), f3;
}
function m() {
  return { current: null };
}
function k(n2) {
  return n2.children;
}
function b(n2, l3) {
  this.props = n2, this.context = l3;
}
function x(n2, l3) {
  if (null == l3)
    return n2.__ ? x(n2.__, n2.__i + 1) : null;
  for (var u3; l3 < n2.__k.length; l3++)
    if (null != (u3 = n2.__k[l3]) && null != u3.__e)
      return u3.__e;
  return "function" == typeof n2.type ? x(n2) : null;
}
function C(n2) {
  var l3, u3;
  if (null != (n2 = n2.__) && null != n2.__c) {
    for (n2.__e = n2.__c.base = null, l3 = 0; l3 < n2.__k.length; l3++)
      if (null != (u3 = n2.__k[l3]) && null != u3.__e) {
        n2.__e = n2.__c.base = u3.__e;
        break;
      }
    return C(n2);
  }
}
function M(n2) {
  (!n2.__d && (n2.__d = true) && i.push(n2) && !P.__r++ || o !== l.debounceRendering) && ((o = l.debounceRendering) || r)(P);
}
function P() {
  var n2, u3, t3, o3, r3, e3, c3, s3;
  for (i.sort(f); n2 = i.shift(); )
    n2.__d && (u3 = i.length, o3 = void 0, e3 = (r3 = (t3 = n2).__v).__e, c3 = [], s3 = [], t3.__P && ((o3 = d({}, r3)).__v = r3.__v + 1, l.vnode && l.vnode(o3), O(t3.__P, o3, r3, t3.__n, t3.__P.namespaceURI, 32 & r3.__u ? [e3] : null, c3, null == e3 ? x(r3) : e3, !!(32 & r3.__u), s3), o3.__v = r3.__v, o3.__.__k[o3.__i] = o3, j(c3, o3, s3), o3.__e != e3 && C(o3)), i.length > u3 && i.sort(f));
  P.__r = 0;
}
function S(n2, l3, u3, t3, i4, o3, r3, f3, e3, c3, s3) {
  var a3, v3, y3, d3, w4, _3 = t3 && t3.__k || p, g4 = l3.length;
  for (u3.__d = e3, $2(u3, l3, _3), e3 = u3.__d, a3 = 0; a3 < g4; a3++)
    null != (y3 = u3.__k[a3]) && "boolean" != typeof y3 && "function" != typeof y3 && (v3 = -1 === y3.__i ? h : _3[y3.__i] || h, y3.__i = a3, O(n2, y3, v3, i4, o3, r3, f3, e3, c3, s3), d3 = y3.__e, y3.ref && v3.ref != y3.ref && (v3.ref && N(v3.ref, null, y3), s3.push(y3.ref, y3.__c || d3, y3)), null == w4 && null != d3 && (w4 = d3), 65536 & y3.__u || v3.__k === y3.__k ? (e3 && "string" == typeof y3.type && !n2.contains(e3) && (e3 = x(v3)), e3 = I(y3, e3, n2)) : "function" == typeof y3.type && void 0 !== y3.__d ? e3 = y3.__d : d3 && (e3 = d3.nextSibling), y3.__d = void 0, y3.__u &= -196609);
  u3.__d = e3, u3.__e = w4;
}
function $2(n2, l3, u3) {
  var t3, i4, o3, r3, f3, e3 = l3.length, c3 = u3.length, s3 = c3, a3 = 0;
  for (n2.__k = [], t3 = 0; t3 < e3; t3++)
    r3 = t3 + a3, null != (i4 = n2.__k[t3] = null == (i4 = l3[t3]) || "boolean" == typeof i4 || "function" == typeof i4 ? null : "string" == typeof i4 || "number" == typeof i4 || "bigint" == typeof i4 || i4.constructor == String ? g(null, i4, null, null, null) : y(i4) ? g(k, { children: i4 }, null, null, null) : void 0 === i4.constructor && i4.__b > 0 ? g(i4.type, i4.props, i4.key, i4.ref ? i4.ref : null, i4.__v) : i4) ? (i4.__ = n2, i4.__b = n2.__b + 1, f3 = L(i4, u3, r3, s3), i4.__i = f3, o3 = null, -1 !== f3 && (s3--, (o3 = u3[f3]) && (o3.__u |= 131072)), null == o3 || null === o3.__v ? (-1 == f3 && a3--, "function" != typeof i4.type && (i4.__u |= 65536)) : f3 !== r3 && (f3 == r3 - 1 ? a3 = f3 - r3 : f3 == r3 + 1 ? a3++ : f3 > r3 ? s3 > e3 - r3 ? a3 += f3 - r3 : a3-- : f3 < r3 && a3++, f3 !== t3 + a3 && (i4.__u |= 65536))) : (o3 = u3[r3]) && null == o3.key && o3.__e && 0 == (131072 & o3.__u) && (o3.__e == n2.__d && (n2.__d = x(o3)), V(o3, o3, false), u3[r3] = null, s3--);
  if (s3)
    for (t3 = 0; t3 < c3; t3++)
      null != (o3 = u3[t3]) && 0 == (131072 & o3.__u) && (o3.__e == n2.__d && (n2.__d = x(o3)), V(o3, o3));
}
function I(n2, l3, u3) {
  var t3, i4;
  if ("function" == typeof n2.type) {
    for (t3 = n2.__k, i4 = 0; t3 && i4 < t3.length; i4++)
      t3[i4] && (t3[i4].__ = n2, l3 = I(t3[i4], l3, u3));
    return l3;
  }
  n2.__e != l3 && (u3.insertBefore(n2.__e, l3 || null), l3 = n2.__e);
  do {
    l3 = l3 && l3.nextSibling;
  } while (null != l3 && 8 === l3.nodeType);
  return l3;
}
function H(n2, l3) {
  return l3 = l3 || [], null == n2 || "boolean" == typeof n2 || (y(n2) ? n2.some(function(n3) {
    H(n3, l3);
  }) : l3.push(n2)), l3;
}
function L(n2, l3, u3, t3) {
  var i4 = n2.key, o3 = n2.type, r3 = u3 - 1, f3 = u3 + 1, e3 = l3[u3];
  if (null === e3 || e3 && i4 == e3.key && o3 === e3.type && 0 == (131072 & e3.__u))
    return u3;
  if (t3 > (null != e3 && 0 == (131072 & e3.__u) ? 1 : 0))
    for (; r3 >= 0 || f3 < l3.length; ) {
      if (r3 >= 0) {
        if ((e3 = l3[r3]) && 0 == (131072 & e3.__u) && i4 == e3.key && o3 === e3.type)
          return r3;
        r3--;
      }
      if (f3 < l3.length) {
        if ((e3 = l3[f3]) && 0 == (131072 & e3.__u) && i4 == e3.key && o3 === e3.type)
          return f3;
        f3++;
      }
    }
  return -1;
}
function T(n2, l3, u3) {
  "-" === l3[0] ? n2.setProperty(l3, null == u3 ? "" : u3) : n2[l3] = null == u3 ? "" : "number" != typeof u3 || v.test(l3) ? u3 : u3 + "px";
}
function A(n2, l3, u3, t3, i4) {
  var o3;
  n:
    if ("style" === l3)
      if ("string" == typeof u3)
        n2.style.cssText = u3;
      else {
        if ("string" == typeof t3 && (n2.style.cssText = t3 = ""), t3)
          for (l3 in t3)
            u3 && l3 in u3 || T(n2.style, l3, "");
        if (u3)
          for (l3 in u3)
            t3 && u3[l3] === t3[l3] || T(n2.style, l3, u3[l3]);
      }
    else if ("o" === l3[0] && "n" === l3[1])
      o3 = l3 !== (l3 = l3.replace(/(PointerCapture)$|Capture$/i, "$1")), l3 = l3.toLowerCase() in n2 || "onFocusOut" === l3 || "onFocusIn" === l3 ? l3.toLowerCase().slice(2) : l3.slice(2), n2.l || (n2.l = {}), n2.l[l3 + o3] = u3, u3 ? t3 ? u3.u = t3.u : (u3.u = e, n2.addEventListener(l3, o3 ? s : c, o3)) : n2.removeEventListener(l3, o3 ? s : c, o3);
    else {
      if ("http://www.w3.org/2000/svg" == i4)
        l3 = l3.replace(/xlink(H|:h)/, "h").replace(/sName$/, "s");
      else if ("width" != l3 && "height" != l3 && "href" != l3 && "list" != l3 && "form" != l3 && "tabIndex" != l3 && "download" != l3 && "rowSpan" != l3 && "colSpan" != l3 && "role" != l3 && "popover" != l3 && l3 in n2)
        try {
          n2[l3] = null == u3 ? "" : u3;
          break n;
        } catch (n3) {
        }
      "function" == typeof u3 || (null == u3 || false === u3 && "-" !== l3[4] ? n2.removeAttribute(l3) : n2.setAttribute(l3, "popover" == l3 && 1 == u3 ? "" : u3));
    }
}
function F(n2) {
  return function(u3) {
    if (this.l) {
      var t3 = this.l[u3.type + n2];
      if (null == u3.t)
        u3.t = e++;
      else if (u3.t < t3.u)
        return;
      return t3(l.event ? l.event(u3) : u3);
    }
  };
}
function O(n2, u3, t3, i4, o3, r3, f3, e3, c3, s3) {
  var a3, h3, p3, v3, w4, _3, g4, m3, x4, C4, M3, P4, $4, I3, H3, L3, T4 = u3.type;
  if (void 0 !== u3.constructor)
    return null;
  128 & t3.__u && (c3 = !!(32 & t3.__u), r3 = [e3 = u3.__e = t3.__e]), (a3 = l.__b) && a3(u3);
  n:
    if ("function" == typeof T4)
      try {
        if (m3 = u3.props, x4 = "prototype" in T4 && T4.prototype.render, C4 = (a3 = T4.contextType) && i4[a3.__c], M3 = a3 ? C4 ? C4.props.value : a3.__ : i4, t3.__c ? g4 = (h3 = u3.__c = t3.__c).__ = h3.__E : (x4 ? u3.__c = h3 = new T4(m3, M3) : (u3.__c = h3 = new b(m3, M3), h3.constructor = T4, h3.render = q), C4 && C4.sub(h3), h3.props = m3, h3.state || (h3.state = {}), h3.context = M3, h3.__n = i4, p3 = h3.__d = true, h3.__h = [], h3._sb = []), x4 && null == h3.__s && (h3.__s = h3.state), x4 && null != T4.getDerivedStateFromProps && (h3.__s == h3.state && (h3.__s = d({}, h3.__s)), d(h3.__s, T4.getDerivedStateFromProps(m3, h3.__s))), v3 = h3.props, w4 = h3.state, h3.__v = u3, p3)
          x4 && null == T4.getDerivedStateFromProps && null != h3.componentWillMount && h3.componentWillMount(), x4 && null != h3.componentDidMount && h3.__h.push(h3.componentDidMount);
        else {
          if (x4 && null == T4.getDerivedStateFromProps && m3 !== v3 && null != h3.componentWillReceiveProps && h3.componentWillReceiveProps(m3, M3), !h3.__e && (null != h3.shouldComponentUpdate && false === h3.shouldComponentUpdate(m3, h3.__s, M3) || u3.__v === t3.__v)) {
            for (u3.__v !== t3.__v && (h3.props = m3, h3.state = h3.__s, h3.__d = false), u3.__e = t3.__e, u3.__k = t3.__k, u3.__k.forEach(function(n3) {
              n3 && (n3.__ = u3);
            }), P4 = 0; P4 < h3._sb.length; P4++)
              h3.__h.push(h3._sb[P4]);
            h3._sb = [], h3.__h.length && f3.push(h3);
            break n;
          }
          null != h3.componentWillUpdate && h3.componentWillUpdate(m3, h3.__s, M3), x4 && null != h3.componentDidUpdate && h3.__h.push(function() {
            h3.componentDidUpdate(v3, w4, _3);
          });
        }
        if (h3.context = M3, h3.props = m3, h3.__P = n2, h3.__e = false, $4 = l.__r, I3 = 0, x4) {
          for (h3.state = h3.__s, h3.__d = false, $4 && $4(u3), a3 = h3.render(h3.props, h3.state, h3.context), H3 = 0; H3 < h3._sb.length; H3++)
            h3.__h.push(h3._sb[H3]);
          h3._sb = [];
        } else
          do {
            h3.__d = false, $4 && $4(u3), a3 = h3.render(h3.props, h3.state, h3.context), h3.state = h3.__s;
          } while (h3.__d && ++I3 < 25);
        h3.state = h3.__s, null != h3.getChildContext && (i4 = d(d({}, i4), h3.getChildContext())), x4 && !p3 && null != h3.getSnapshotBeforeUpdate && (_3 = h3.getSnapshotBeforeUpdate(v3, w4)), S(n2, y(L3 = null != a3 && a3.type === k && null == a3.key ? a3.props.children : a3) ? L3 : [L3], u3, t3, i4, o3, r3, f3, e3, c3, s3), h3.base = u3.__e, u3.__u &= -161, h3.__h.length && f3.push(h3), g4 && (h3.__E = h3.__ = null);
      } catch (n3) {
        u3.__v = null, c3 || null != r3 ? (u3.__e = e3, u3.__u |= c3 ? 160 : 32, r3[r3.indexOf(e3)] = null) : (u3.__e = t3.__e, u3.__k = t3.__k), l.__e(n3, u3, t3);
      }
    else
      null == r3 && u3.__v === t3.__v ? (u3.__k = t3.__k, u3.__e = t3.__e) : u3.__e = z(t3.__e, u3, t3, i4, o3, r3, f3, c3, s3);
  (a3 = l.diffed) && a3(u3);
}
function j(n2, u3, t3) {
  u3.__d = void 0;
  for (var i4 = 0; i4 < t3.length; i4++)
    N(t3[i4], t3[++i4], t3[++i4]);
  l.__c && l.__c(u3, n2), n2.some(function(u4) {
    try {
      n2 = u4.__h, u4.__h = [], n2.some(function(n3) {
        n3.call(u4);
      });
    } catch (n3) {
      l.__e(n3, u4.__v);
    }
  });
}
function z(l3, u3, t3, i4, o3, r3, f3, e3, c3) {
  var s3, a3, p3, v3, d3, _3, g4, m3 = t3.props, k4 = u3.props, b2 = u3.type;
  if ("svg" === b2 ? o3 = "http://www.w3.org/2000/svg" : "math" === b2 ? o3 = "http://www.w3.org/1998/Math/MathML" : o3 || (o3 = "http://www.w3.org/1999/xhtml"), null != r3) {
    for (s3 = 0; s3 < r3.length; s3++)
      if ((d3 = r3[s3]) && "setAttribute" in d3 == !!b2 && (b2 ? d3.localName === b2 : 3 === d3.nodeType)) {
        l3 = d3, r3[s3] = null;
        break;
      }
  }
  if (null == l3) {
    if (null === b2)
      return document.createTextNode(k4);
    l3 = document.createElementNS(o3, b2, k4.is && k4), r3 = null, e3 = false;
  }
  if (null === b2)
    m3 === k4 || e3 && l3.data === k4 || (l3.data = k4);
  else {
    if (r3 = r3 && n.call(l3.childNodes), m3 = t3.props || h, !e3 && null != r3)
      for (m3 = {}, s3 = 0; s3 < l3.attributes.length; s3++)
        m3[(d3 = l3.attributes[s3]).name] = d3.value;
    for (s3 in m3)
      if (d3 = m3[s3], "children" == s3)
        ;
      else if ("dangerouslySetInnerHTML" == s3)
        p3 = d3;
      else if ("key" !== s3 && !(s3 in k4)) {
        if ("value" == s3 && "defaultValue" in k4 || "checked" == s3 && "defaultChecked" in k4)
          continue;
        A(l3, s3, null, d3, o3);
      }
    for (s3 in k4)
      d3 = k4[s3], "children" == s3 ? v3 = d3 : "dangerouslySetInnerHTML" == s3 ? a3 = d3 : "value" == s3 ? _3 = d3 : "checked" == s3 ? g4 = d3 : "key" === s3 || e3 && "function" != typeof d3 || m3[s3] === d3 || A(l3, s3, d3, m3[s3], o3);
    if (a3)
      e3 || p3 && (a3.__html === p3.__html || a3.__html === l3.innerHTML) || (l3.innerHTML = a3.__html), u3.__k = [];
    else if (p3 && (l3.innerHTML = ""), S(l3, y(v3) ? v3 : [v3], u3, t3, i4, "foreignObject" === b2 ? "http://www.w3.org/1999/xhtml" : o3, r3, f3, r3 ? r3[0] : t3.__k && x(t3, 0), e3, c3), null != r3)
      for (s3 = r3.length; s3--; )
        null != r3[s3] && w(r3[s3]);
    e3 || (s3 = "value", void 0 !== _3 && (_3 !== l3[s3] || "progress" === b2 && !_3 || "option" === b2 && _3 !== m3[s3]) && A(l3, s3, _3, m3[s3], o3), s3 = "checked", void 0 !== g4 && g4 !== l3[s3] && A(l3, s3, g4, m3[s3], o3));
  }
  return l3;
}
function N(n2, u3, t3) {
  try {
    "function" == typeof n2 ? n2(u3) : n2.current = u3;
  } catch (n3) {
    l.__e(n3, t3);
  }
}
function V(n2, u3, t3) {
  var i4, o3;
  if (l.unmount && l.unmount(n2), (i4 = n2.ref) && (i4.current && i4.current !== n2.__e || N(i4, null, u3)), null != (i4 = n2.__c)) {
    if (i4.componentWillUnmount)
      try {
        i4.componentWillUnmount();
      } catch (n3) {
        l.__e(n3, u3);
      }
    i4.base = i4.__P = null;
  }
  if (i4 = n2.__k)
    for (o3 = 0; o3 < i4.length; o3++)
      i4[o3] && V(i4[o3], u3, t3 || "function" != typeof n2.type);
  t3 || null == n2.__e || w(n2.__e), n2.__c = n2.__ = n2.__e = n2.__d = void 0;
}
function q(n2, l3, u3) {
  return this.constructor(n2, u3);
}
function B(u3, t3, i4) {
  var o3, r3, f3, e3;
  l.__ && l.__(u3, t3), r3 = (o3 = "function" == typeof i4) ? null : i4 && i4.__k || t3.__k, f3 = [], e3 = [], O(t3, u3 = (!o3 && i4 || t3).__k = _(k, null, [u3]), r3 || h, h, t3.namespaceURI, !o3 && i4 ? [i4] : r3 ? null : t3.firstChild ? n.call(t3.childNodes) : null, f3, !o3 && i4 ? i4 : r3 ? r3.__e : t3.firstChild, o3, e3), j(f3, u3, e3);
}
function D(n2, l3) {
  B(n2, l3, D);
}
function E(l3, u3, t3) {
  var i4, o3, r3, f3, e3 = d({}, l3.props);
  for (r3 in l3.type && l3.type.defaultProps && (f3 = l3.type.defaultProps), u3)
    "key" == r3 ? i4 = u3[r3] : "ref" == r3 ? o3 = u3[r3] : e3[r3] = void 0 === u3[r3] && void 0 !== f3 ? f3[r3] : u3[r3];
  return arguments.length > 2 && (e3.children = arguments.length > 3 ? n.call(arguments, 2) : t3), g(l3.type, e3, i4 || l3.key, o3 || l3.ref, null);
}
function G(n2, l3) {
  var u3 = { __c: l3 = "__cC" + a++, __: n2, Consumer: function(n3, l4) {
    return n3.children(l4);
  }, Provider: function(n3) {
    var u4, t3;
    return this.getChildContext || (u4 = [], (t3 = {})[l3] = this, this.getChildContext = function() {
      return t3;
    }, this.componentWillUnmount = function() {
      u4 = null;
    }, this.shouldComponentUpdate = function(n4) {
      this.props.value !== n4.value && u4.some(function(n5) {
        n5.__e = true, M(n5);
      });
    }, this.sub = function(n4) {
      u4.push(n4);
      var l4 = n4.componentWillUnmount;
      n4.componentWillUnmount = function() {
        u4 && u4.splice(u4.indexOf(n4), 1), l4 && l4.call(n4);
      };
    }), n3.children;
  } };
  return u3.Provider.__ = u3.Consumer.contextType = u3;
}
n = p.slice, l = { __e: function(n2, l3, u3, t3) {
  for (var i4, o3, r3; l3 = l3.__; )
    if ((i4 = l3.__c) && !i4.__)
      try {
        if ((o3 = i4.constructor) && null != o3.getDerivedStateFromError && (i4.setState(o3.getDerivedStateFromError(n2)), r3 = i4.__d), null != i4.componentDidCatch && (i4.componentDidCatch(n2, t3 || {}), r3 = i4.__d), r3)
          return i4.__E = i4;
      } catch (l4) {
        n2 = l4;
      }
  throw n2;
} }, u = 0, t = function(n2) {
  return null != n2 && null == n2.constructor;
}, b.prototype.setState = function(n2, l3) {
  var u3;
  u3 = null != this.__s && this.__s !== this.state ? this.__s : this.__s = d({}, this.state), "function" == typeof n2 && (n2 = n2(d({}, u3), this.props)), n2 && d(u3, n2), null != n2 && this.__v && (l3 && this._sb.push(l3), M(this));
}, b.prototype.forceUpdate = function(n2) {
  this.__v && (this.__e = true, n2 && this.__h.push(n2), M(this));
}, b.prototype.render = k, i = [], r = "function" == typeof Promise ? Promise.prototype.then.bind(Promise.resolve()) : setTimeout, f = function(n2, l3) {
  return n2.__v.__b - l3.__v.__b;
}, P.__r = 0, e = 0, c = F(false), s = F(true), a = 0;

// node_modules/preact/hooks/dist/hooks.module.js
var t2;
var r2;
var u2;
var i2;
var o2 = 0;
var f2 = [];
var c2 = l;
var e2 = c2.__b;
var a2 = c2.__r;
var v2 = c2.diffed;
var l2 = c2.__c;
var m2 = c2.unmount;
var s2 = c2.__;
function d2(n2, t3) {
  c2.__h && c2.__h(r2, n2, o2 || t3), o2 = 0;
  var u3 = r2.__H || (r2.__H = { __: [], __h: [] });
  return n2 >= u3.__.length && u3.__.push({}), u3.__[n2];
}
function h2(n2) {
  return o2 = 1, p2(D2, n2);
}
function p2(n2, u3, i4) {
  var o3 = d2(t2++, 2);
  if (o3.t = n2, !o3.__c && (o3.__ = [i4 ? i4(u3) : D2(void 0, u3), function(n3) {
    var t3 = o3.__N ? o3.__N[0] : o3.__[0], r3 = o3.t(t3, n3);
    t3 !== r3 && (o3.__N = [r3, o3.__[1]], o3.__c.setState({}));
  }], o3.__c = r2, !r2.u)) {
    var f3 = function(n3, t3, r3) {
      if (!o3.__c.__H)
        return true;
      var u4 = o3.__c.__H.__.filter(function(n4) {
        return !!n4.__c;
      });
      if (u4.every(function(n4) {
        return !n4.__N;
      }))
        return !c3 || c3.call(this, n3, t3, r3);
      var i5 = false;
      return u4.forEach(function(n4) {
        if (n4.__N) {
          var t4 = n4.__[0];
          n4.__ = n4.__N, n4.__N = void 0, t4 !== n4.__[0] && (i5 = true);
        }
      }), !(!i5 && o3.__c.props === n3) && (!c3 || c3.call(this, n3, t3, r3));
    };
    r2.u = true;
    var c3 = r2.shouldComponentUpdate, e3 = r2.componentWillUpdate;
    r2.componentWillUpdate = function(n3, t3, r3) {
      if (this.__e) {
        var u4 = c3;
        c3 = void 0, f3(n3, t3, r3), c3 = u4;
      }
      e3 && e3.call(this, n3, t3, r3);
    }, r2.shouldComponentUpdate = f3;
  }
  return o3.__N || o3.__;
}
function y2(n2, u3) {
  var i4 = d2(t2++, 3);
  !c2.__s && C2(i4.__H, u3) && (i4.__ = n2, i4.i = u3, r2.__H.__h.push(i4));
}
function _2(n2, u3) {
  var i4 = d2(t2++, 4);
  !c2.__s && C2(i4.__H, u3) && (i4.__ = n2, i4.i = u3, r2.__h.push(i4));
}
function A2(n2) {
  return o2 = 5, T2(function() {
    return { current: n2 };
  }, []);
}
function F2(n2, t3, r3) {
  o2 = 6, _2(function() {
    return "function" == typeof n2 ? (n2(t3()), function() {
      return n2(null);
    }) : n2 ? (n2.current = t3(), function() {
      return n2.current = null;
    }) : void 0;
  }, null == r3 ? r3 : r3.concat(n2));
}
function T2(n2, r3) {
  var u3 = d2(t2++, 7);
  return C2(u3.__H, r3) && (u3.__ = n2(), u3.__H = r3, u3.__h = n2), u3.__;
}
function q2(n2, t3) {
  return o2 = 8, T2(function() {
    return n2;
  }, t3);
}
function x2(n2) {
  var u3 = r2.context[n2.__c], i4 = d2(t2++, 9);
  return i4.c = n2, u3 ? (null == i4.__ && (i4.__ = true, u3.sub(r2)), u3.props.value) : n2.__;
}
function P2(n2, t3) {
  c2.useDebugValue && c2.useDebugValue(t3 ? t3(n2) : n2);
}
function g2() {
  var n2 = d2(t2++, 11);
  if (!n2.__) {
    for (var u3 = r2.__v; null !== u3 && !u3.__m && null !== u3.__; )
      u3 = u3.__;
    var i4 = u3.__m || (u3.__m = [0, 0]);
    n2.__ = "P" + i4[0] + "-" + i4[1]++;
  }
  return n2.__;
}
function j2() {
  for (var n2; n2 = f2.shift(); )
    if (n2.__P && n2.__H)
      try {
        n2.__H.__h.forEach(z2), n2.__H.__h.forEach(B2), n2.__H.__h = [];
      } catch (t3) {
        n2.__H.__h = [], c2.__e(t3, n2.__v);
      }
}
c2.__b = function(n2) {
  r2 = null, e2 && e2(n2);
}, c2.__ = function(n2, t3) {
  n2 && t3.__k && t3.__k.__m && (n2.__m = t3.__k.__m), s2 && s2(n2, t3);
}, c2.__r = function(n2) {
  a2 && a2(n2), t2 = 0;
  var i4 = (r2 = n2.__c).__H;
  i4 && (u2 === r2 ? (i4.__h = [], r2.__h = [], i4.__.forEach(function(n3) {
    n3.__N && (n3.__ = n3.__N), n3.i = n3.__N = void 0;
  })) : (i4.__h.forEach(z2), i4.__h.forEach(B2), i4.__h = [], t2 = 0)), u2 = r2;
}, c2.diffed = function(n2) {
  v2 && v2(n2);
  var t3 = n2.__c;
  t3 && t3.__H && (t3.__H.__h.length && (1 !== f2.push(t3) && i2 === c2.requestAnimationFrame || ((i2 = c2.requestAnimationFrame) || w2)(j2)), t3.__H.__.forEach(function(n3) {
    n3.i && (n3.__H = n3.i), n3.i = void 0;
  })), u2 = r2 = null;
}, c2.__c = function(n2, t3) {
  t3.some(function(n3) {
    try {
      n3.__h.forEach(z2), n3.__h = n3.__h.filter(function(n4) {
        return !n4.__ || B2(n4);
      });
    } catch (r3) {
      t3.some(function(n4) {
        n4.__h && (n4.__h = []);
      }), t3 = [], c2.__e(r3, n3.__v);
    }
  }), l2 && l2(n2, t3);
}, c2.unmount = function(n2) {
  m2 && m2(n2);
  var t3, r3 = n2.__c;
  r3 && r3.__H && (r3.__H.__.forEach(function(n3) {
    try {
      z2(n3);
    } catch (n4) {
      t3 = n4;
    }
  }), r3.__H = void 0, t3 && c2.__e(t3, r3.__v));
};
var k2 = "function" == typeof requestAnimationFrame;
function w2(n2) {
  var t3, r3 = function() {
    clearTimeout(u3), k2 && cancelAnimationFrame(t3), setTimeout(n2);
  }, u3 = setTimeout(r3, 100);
  k2 && (t3 = requestAnimationFrame(r3));
}
function z2(n2) {
  var t3 = r2, u3 = n2.__c;
  "function" == typeof u3 && (n2.__c = void 0, u3()), r2 = t3;
}
function B2(n2) {
  var t3 = r2;
  n2.__c = n2.__(), r2 = t3;
}
function C2(n2, t3) {
  return !n2 || n2.length !== t3.length || t3.some(function(t4, r3) {
    return t4 !== n2[r3];
  });
}
function D2(n2, t3) {
  return "function" == typeof t3 ? t3(n2) : t3;
}

// node_modules/preact/compat/dist/compat.module.js
function g3(n2, t3) {
  for (var e3 in t3)
    n2[e3] = t3[e3];
  return n2;
}
function E2(n2, t3) {
  for (var e3 in n2)
    if ("__source" !== e3 && !(e3 in t3))
      return true;
  for (var r3 in t3)
    if ("__source" !== r3 && n2[r3] !== t3[r3])
      return true;
  return false;
}
function C3(n2, t3) {
  this.props = n2, this.context = t3;
}
function x3(n2, e3) {
  function r3(n3) {
    var t3 = this.props.ref, r4 = t3 == n3.ref;
    return !r4 && t3 && (t3.call ? t3(null) : t3.current = null), e3 ? !e3(this.props, n3) || !r4 : E2(this.props, n3);
  }
  function u3(e4) {
    return this.shouldComponentUpdate = r3, _(n2, e4);
  }
  return u3.displayName = "Memo(" + (n2.displayName || n2.name) + ")", u3.prototype.isReactComponent = true, u3.__f = true, u3;
}
(C3.prototype = new b()).isPureReactComponent = true, C3.prototype.shouldComponentUpdate = function(n2, t3) {
  return E2(this.props, n2) || E2(this.state, t3);
};
var R = l.__b;
l.__b = function(n2) {
  n2.type && n2.type.__f && n2.ref && (n2.props.ref = n2.ref, n2.ref = null), R && R(n2);
};
var w3 = "undefined" != typeof Symbol && Symbol.for && Symbol.for("react.forward_ref") || 3911;
function k3(n2) {
  function t3(t4) {
    var e3 = g3({}, t4);
    return delete e3.ref, n2(e3, t4.ref || null);
  }
  return t3.$$typeof = w3, t3.render = t3, t3.prototype.isReactComponent = t3.__f = true, t3.displayName = "ForwardRef(" + (n2.displayName || n2.name) + ")", t3;
}
var I2 = function(n2, t3) {
  return null == n2 ? null : H(H(n2).map(t3));
};
var N2 = { map: I2, forEach: I2, count: function(n2) {
  return n2 ? H(n2).length : 0;
}, only: function(n2) {
  var t3 = H(n2);
  if (1 !== t3.length)
    throw "Children.only";
  return t3[0];
}, toArray: H };
var M2 = l.__e;
l.__e = function(n2, t3, e3, r3) {
  if (n2.then) {
    for (var u3, o3 = t3; o3 = o3.__; )
      if ((u3 = o3.__c) && u3.__c)
        return null == t3.__e && (t3.__e = e3.__e, t3.__k = e3.__k), u3.__c(n2, t3);
  }
  M2(n2, t3, e3, r3);
};
var T3 = l.unmount;
function A3(n2, t3, e3) {
  return n2 && (n2.__c && n2.__c.__H && (n2.__c.__H.__.forEach(function(n3) {
    "function" == typeof n3.__c && n3.__c();
  }), n2.__c.__H = null), null != (n2 = g3({}, n2)).__c && (n2.__c.__P === e3 && (n2.__c.__P = t3), n2.__c = null), n2.__k = n2.__k && n2.__k.map(function(n3) {
    return A3(n3, t3, e3);
  })), n2;
}
function D3(n2, t3, e3) {
  return n2 && e3 && (n2.__v = null, n2.__k = n2.__k && n2.__k.map(function(n3) {
    return D3(n3, t3, e3);
  }), n2.__c && n2.__c.__P === t3 && (n2.__e && e3.appendChild(n2.__e), n2.__c.__e = true, n2.__c.__P = e3)), n2;
}
function L2() {
  this.__u = 0, this.t = null, this.__b = null;
}
function O2(n2) {
  var t3 = n2.__.__c;
  return t3 && t3.__a && t3.__a(n2);
}
function F3(n2) {
  var e3, r3, u3;
  function o3(o4) {
    if (e3 || (e3 = n2()).then(function(n3) {
      r3 = n3.default || n3;
    }, function(n3) {
      u3 = n3;
    }), u3)
      throw u3;
    if (!r3)
      throw e3;
    return _(r3, o4);
  }
  return o3.displayName = "Lazy", o3.__f = true, o3;
}
function U() {
  this.u = null, this.o = null;
}
l.unmount = function(n2) {
  var t3 = n2.__c;
  t3 && t3.__R && t3.__R(), t3 && 32 & n2.__u && (n2.type = null), T3 && T3(n2);
}, (L2.prototype = new b()).__c = function(n2, t3) {
  var e3 = t3.__c, r3 = this;
  null == r3.t && (r3.t = []), r3.t.push(e3);
  var u3 = O2(r3.__v), o3 = false, i4 = function() {
    o3 || (o3 = true, e3.__R = null, u3 ? u3(c3) : c3());
  };
  e3.__R = i4;
  var c3 = function() {
    if (!--r3.__u) {
      if (r3.state.__a) {
        var n3 = r3.state.__a;
        r3.__v.__k[0] = D3(n3, n3.__c.__P, n3.__c.__O);
      }
      var t4;
      for (r3.setState({ __a: r3.__b = null }); t4 = r3.t.pop(); )
        t4.forceUpdate();
    }
  };
  r3.__u++ || 32 & t3.__u || r3.setState({ __a: r3.__b = r3.__v.__k[0] }), n2.then(i4, i4);
}, L2.prototype.componentWillUnmount = function() {
  this.t = [];
}, L2.prototype.render = function(n2, e3) {
  if (this.__b) {
    if (this.__v.__k) {
      var r3 = document.createElement("div"), o3 = this.__v.__k[0].__c;
      this.__v.__k[0] = A3(this.__b, r3, o3.__O = o3.__P);
    }
    this.__b = null;
  }
  var i4 = e3.__a && _(k, null, n2.fallback);
  return i4 && (i4.__u &= -33), [_(k, null, e3.__a ? null : n2.children), i4];
};
var V2 = function(n2, t3, e3) {
  if (++e3[1] === e3[0] && n2.o.delete(t3), n2.props.revealOrder && ("t" !== n2.props.revealOrder[0] || !n2.o.size))
    for (e3 = n2.u; e3; ) {
      for (; e3.length > 3; )
        e3.pop()();
      if (e3[1] < e3[0])
        break;
      n2.u = e3 = e3[2];
    }
};
function W(n2) {
  return this.getChildContext = function() {
    return n2.context;
  }, n2.children;
}
function P3(n2) {
  var e3 = this, r3 = n2.i;
  e3.componentWillUnmount = function() {
    B(null, e3.l), e3.l = null, e3.i = null;
  }, e3.i && e3.i !== r3 && e3.componentWillUnmount(), e3.l || (e3.i = r3, e3.l = { nodeType: 1, parentNode: r3, childNodes: [], contains: function() {
    return true;
  }, appendChild: function(n3) {
    this.childNodes.push(n3), e3.i.appendChild(n3);
  }, insertBefore: function(n3, t3) {
    this.childNodes.push(n3), e3.i.appendChild(n3);
  }, removeChild: function(n3) {
    this.childNodes.splice(this.childNodes.indexOf(n3) >>> 1, 1), e3.i.removeChild(n3);
  } }), B(_(W, { context: e3.context }, n2.__v), e3.l);
}
function j3(n2, e3) {
  var r3 = _(P3, { __v: n2, i: e3 });
  return r3.containerInfo = e3, r3;
}
(U.prototype = new b()).__a = function(n2) {
  var t3 = this, e3 = O2(t3.__v), r3 = t3.o.get(n2);
  return r3[0]++, function(u3) {
    var o3 = function() {
      t3.props.revealOrder ? (r3.push(u3), V2(t3, n2, r3)) : u3();
    };
    e3 ? e3(o3) : o3();
  };
}, U.prototype.render = function(n2) {
  this.u = null, this.o = /* @__PURE__ */ new Map();
  var t3 = H(n2.children);
  n2.revealOrder && "b" === n2.revealOrder[0] && t3.reverse();
  for (var e3 = t3.length; e3--; )
    this.o.set(t3[e3], this.u = [1, 0, this.u]);
  return n2.children;
}, U.prototype.componentDidUpdate = U.prototype.componentDidMount = function() {
  var n2 = this;
  this.o.forEach(function(t3, e3) {
    V2(n2, e3, t3);
  });
};
var z3 = "undefined" != typeof Symbol && Symbol.for && Symbol.for("react.element") || 60103;
var B3 = /^(?:accent|alignment|arabic|baseline|cap|clip(?!PathU)|color|dominant|fill|flood|font|glyph(?!R)|horiz|image(!S)|letter|lighting|marker(?!H|W|U)|overline|paint|pointer|shape|stop|strikethrough|stroke|text(?!L)|transform|underline|unicode|units|v|vector|vert|word|writing|x(?!C))[A-Z]/;
var H2 = /^on(Ani|Tra|Tou|BeforeInp|Compo)/;
var Z = /[A-Z0-9]/g;
var Y = "undefined" != typeof document;
var $3 = function(n2) {
  return ("undefined" != typeof Symbol && "symbol" == typeof Symbol() ? /fil|che|rad/ : /fil|che|ra/).test(n2);
};
function q3(n2, t3, e3) {
  return null == t3.__k && (t3.textContent = ""), B(n2, t3), "function" == typeof e3 && e3(), n2 ? n2.__c : null;
}
function G2(n2, t3, e3) {
  return D(n2, t3), "function" == typeof e3 && e3(), n2 ? n2.__c : null;
}
b.prototype.isReactComponent = {}, ["componentWillMount", "componentWillReceiveProps", "componentWillUpdate"].forEach(function(t3) {
  Object.defineProperty(b.prototype, t3, { configurable: true, get: function() {
    return this["UNSAFE_" + t3];
  }, set: function(n2) {
    Object.defineProperty(this, t3, { configurable: true, writable: true, value: n2 });
  } });
});
var J = l.event;
function K() {
}
function Q() {
  return this.cancelBubble;
}
function X() {
  return this.defaultPrevented;
}
l.event = function(n2) {
  return J && (n2 = J(n2)), n2.persist = K, n2.isPropagationStopped = Q, n2.isDefaultPrevented = X, n2.nativeEvent = n2;
};
var nn;
var tn = { enumerable: false, configurable: true, get: function() {
  return this.class;
} };
var en = l.vnode;
l.vnode = function(n2) {
  "string" == typeof n2.type && function(n3) {
    var t3 = n3.props, e3 = n3.type, u3 = {};
    for (var o3 in t3) {
      var i4 = t3[o3];
      if (!("value" === o3 && "defaultValue" in t3 && null == i4 || Y && "children" === o3 && "noscript" === e3 || "class" === o3 || "className" === o3)) {
        var c3 = o3.toLowerCase();
        "defaultValue" === o3 && "value" in t3 && null == t3.value ? o3 = "value" : "download" === o3 && true === i4 ? i4 = "" : "translate" === c3 && "no" === i4 ? i4 = false : "ondoubleclick" === c3 ? o3 = "ondblclick" : "onchange" !== c3 || "input" !== e3 && "textarea" !== e3 || $3(t3.type) ? "onfocus" === c3 ? o3 = "onfocusin" : "onblur" === c3 ? o3 = "onfocusout" : H2.test(o3) ? o3 = c3 : -1 === e3.indexOf("-") && B3.test(o3) ? o3 = o3.replace(Z, "-$&").toLowerCase() : null === i4 && (i4 = void 0) : c3 = o3 = "oninput", "oninput" === c3 && u3[o3 = c3] && (o3 = "oninputCapture"), u3[o3] = i4;
      }
    }
    "select" == e3 && u3.multiple && Array.isArray(u3.value) && (u3.value = H(t3.children).forEach(function(n4) {
      n4.props.selected = -1 != u3.value.indexOf(n4.props.value);
    })), "select" == e3 && null != u3.defaultValue && (u3.value = H(t3.children).forEach(function(n4) {
      n4.props.selected = u3.multiple ? -1 != u3.defaultValue.indexOf(n4.props.value) : u3.defaultValue == n4.props.value;
    })), t3.class && !t3.className ? (u3.class = t3.class, Object.defineProperty(u3, "className", tn)) : (t3.className && !t3.class || t3.class && t3.className) && (u3.class = u3.className = t3.className), n3.props = u3;
  }(n2), n2.$$typeof = z3, en && en(n2);
};
var rn = l.__r;
l.__r = function(n2) {
  rn && rn(n2), nn = n2.__c;
};
var un = l.diffed;
l.diffed = function(n2) {
  un && un(n2);
  var t3 = n2.props, e3 = n2.__e;
  null != e3 && "textarea" === n2.type && "value" in t3 && t3.value !== e3.value && (e3.value = null == t3.value ? "" : t3.value), nn = null;
};
var on = { ReactCurrentDispatcher: { current: { readContext: function(n2) {
  return nn.__n[n2.__c].props.value;
}, useCallback: q2, useContext: x2, useDebugValue: P2, useDeferredValue: bn, useEffect: y2, useId: g2, useImperativeHandle: F2, useInsertionEffect: gn, useLayoutEffect: _2, useMemo: T2, useReducer: p2, useRef: A2, useState: h2, useSyncExternalStore: Cn, useTransition: Sn } } };
function ln(n2) {
  return _.bind(null, n2);
}
function fn(n2) {
  return !!n2 && n2.$$typeof === z3;
}
function an(n2) {
  return fn(n2) && n2.type === k;
}
function sn(n2) {
  return !!n2 && !!n2.displayName && ("string" == typeof n2.displayName || n2.displayName instanceof String) && n2.displayName.startsWith("Memo(");
}
function hn(n2) {
  return fn(n2) ? E.apply(null, arguments) : n2;
}
function vn(n2) {
  return !!n2.__k && (B(null, n2), true);
}
function dn(n2) {
  return n2 && (n2.base || 1 === n2.nodeType && n2) || null;
}
var pn = function(n2, t3) {
  return n2(t3);
};
var mn = function(n2, t3) {
  return n2(t3);
};
var yn = k;
function _n(n2) {
  n2();
}
function bn(n2) {
  return n2;
}
function Sn() {
  return [false, _n];
}
var gn = _2;
var En = fn;
function Cn(n2, t3) {
  var e3 = t3(), r3 = h2({ h: { __: e3, v: t3 } }), u3 = r3[0].h, o3 = r3[1];
  return _2(function() {
    u3.__ = e3, u3.v = t3, xn(u3) && o3({ h: u3 });
  }, [n2, e3, t3]), y2(function() {
    return xn(u3) && o3({ h: u3 }), n2(function() {
      xn(u3) && o3({ h: u3 });
    });
  }, [n2]), e3;
}
function xn(n2) {
  var t3, e3, r3 = n2.v, u3 = n2.__;
  try {
    var o3 = r3();
    return !((t3 = u3) === (e3 = o3) && (0 !== t3 || 1 / t3 == 1 / e3) || t3 != t3 && e3 != e3);
  } catch (n3) {
    return true;
  }
}
var Rn = { useState: h2, useId: g2, useReducer: p2, useEffect: y2, useLayoutEffect: _2, useInsertionEffect: gn, useTransition: Sn, useDeferredValue: bn, useSyncExternalStore: Cn, startTransition: _n, useRef: A2, useImperativeHandle: F2, useMemo: T2, useCallback: q2, useContext: x2, useDebugValue: P2, version: "17.0.2", Children: N2, render: q3, hydrate: G2, unmountComponentAtNode: vn, createPortal: j3, createElement: _, createContext: G, createFactory: ln, cloneElement: hn, createRef: m, Fragment: k, isValidElement: fn, isElement: En, isFragment: an, isMemo: sn, findDOMNode: dn, Component: b, PureComponent: C3, memo: x3, forwardRef: k3, flushSync: mn, unstable_batchedUpdates: pn, StrictMode: yn, Suspense: L2, SuspenseList: U, lazy: F3, __SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED: on };

// node_modules/@tanstack/table-core/build/lib/index.mjs
function functionalUpdate(updater, input) {
  return typeof updater === "function" ? updater(input) : updater;
}
function makeStateUpdater(key, instance) {
  return (updater) => {
    instance.setState((old) => {
      return {
        ...old,
        [key]: functionalUpdate(updater, old[key])
      };
    });
  };
}
function isFunction(d3) {
  return d3 instanceof Function;
}
function isNumberArray(d3) {
  return Array.isArray(d3) && d3.every((val) => typeof val === "number");
}
function flattenBy(arr, getChildren) {
  const flat = [];
  const recurse = (subArr) => {
    subArr.forEach((item) => {
      flat.push(item);
      const children = getChildren(item);
      if (children != null && children.length) {
        recurse(children);
      }
    });
  };
  recurse(arr);
  return flat;
}
function memo(getDeps, fn2, opts) {
  let deps = [];
  let result;
  return (depArgs) => {
    let depTime;
    if (opts.key && opts.debug)
      depTime = Date.now();
    const newDeps = getDeps(depArgs);
    const depsChanged = newDeps.length !== deps.length || newDeps.some((dep, index) => deps[index] !== dep);
    if (!depsChanged) {
      return result;
    }
    deps = newDeps;
    let resultTime;
    if (opts.key && opts.debug)
      resultTime = Date.now();
    result = fn2(...newDeps);
    opts == null || opts.onChange == null || opts.onChange(result);
    if (opts.key && opts.debug) {
      if (opts != null && opts.debug()) {
        const depEndTime = Math.round((Date.now() - depTime) * 100) / 100;
        const resultEndTime = Math.round((Date.now() - resultTime) * 100) / 100;
        const resultFpsPercentage = resultEndTime / 16;
        const pad = (str, num) => {
          str = String(str);
          while (str.length < num) {
            str = " " + str;
          }
          return str;
        };
        console.info(`%c\u23F1 ${pad(resultEndTime, 5)} /${pad(depEndTime, 5)} ms`, `
            font-size: .6rem;
            font-weight: bold;
            color: hsl(${Math.max(0, Math.min(120 - 120 * resultFpsPercentage, 120))}deg 100% 31%);`, opts == null ? void 0 : opts.key);
      }
    }
    return result;
  };
}
function getMemoOptions(tableOptions, debugLevel, key, onChange) {
  return {
    debug: () => {
      var _tableOptions$debugAl;
      return (_tableOptions$debugAl = tableOptions == null ? void 0 : tableOptions.debugAll) != null ? _tableOptions$debugAl : tableOptions[debugLevel];
    },
    key,
    onChange
  };
}
function createCell(table, row, column, columnId) {
  const getRenderValue = () => {
    var _cell$getValue;
    return (_cell$getValue = cell.getValue()) != null ? _cell$getValue : table.options.renderFallbackValue;
  };
  const cell = {
    id: `${row.id}_${column.id}`,
    row,
    column,
    getValue: () => row.getValue(columnId),
    renderValue: getRenderValue,
    getContext: memo(() => [table, column, row, cell], (table2, column2, row2, cell2) => ({
      table: table2,
      column: column2,
      row: row2,
      cell: cell2,
      getValue: cell2.getValue,
      renderValue: cell2.renderValue
    }), getMemoOptions(table.options, "debugCells", "cell.getContext"))
  };
  table._features.forEach((feature) => {
    feature.createCell == null || feature.createCell(cell, column, row, table);
  }, {});
  return cell;
}
function createColumn(table, columnDef, depth, parent) {
  var _ref, _resolvedColumnDef$id;
  const defaultColumn = table._getDefaultColumnDef();
  const resolvedColumnDef = {
    ...defaultColumn,
    ...columnDef
  };
  const accessorKey = resolvedColumnDef.accessorKey;
  let id = (_ref = (_resolvedColumnDef$id = resolvedColumnDef.id) != null ? _resolvedColumnDef$id : accessorKey ? accessorKey.replace(".", "_") : void 0) != null ? _ref : typeof resolvedColumnDef.header === "string" ? resolvedColumnDef.header : void 0;
  let accessorFn;
  if (resolvedColumnDef.accessorFn) {
    accessorFn = resolvedColumnDef.accessorFn;
  } else if (accessorKey) {
    if (accessorKey.includes(".")) {
      accessorFn = (originalRow) => {
        let result = originalRow;
        for (const key of accessorKey.split(".")) {
          var _result;
          result = (_result = result) == null ? void 0 : _result[key];
          if (result === void 0) {
            console.warn(`"${key}" in deeply nested key "${accessorKey}" returned undefined.`);
          }
        }
        return result;
      };
    } else {
      accessorFn = (originalRow) => originalRow[resolvedColumnDef.accessorKey];
    }
  }
  if (!id) {
    if (true) {
      throw new Error(resolvedColumnDef.accessorFn ? `Columns require an id when using an accessorFn` : `Columns require an id when using a non-string header`);
    }
    throw new Error();
  }
  let column = {
    id: `${String(id)}`,
    accessorFn,
    parent,
    depth,
    columnDef: resolvedColumnDef,
    columns: [],
    getFlatColumns: memo(() => [true], () => {
      var _column$columns;
      return [column, ...(_column$columns = column.columns) == null ? void 0 : _column$columns.flatMap((d3) => d3.getFlatColumns())];
    }, getMemoOptions(table.options, "debugColumns", "column.getFlatColumns")),
    getLeafColumns: memo(() => [table._getOrderColumnsFn()], (orderColumns2) => {
      var _column$columns2;
      if ((_column$columns2 = column.columns) != null && _column$columns2.length) {
        let leafColumns = column.columns.flatMap((column2) => column2.getLeafColumns());
        return orderColumns2(leafColumns);
      }
      return [column];
    }, getMemoOptions(table.options, "debugColumns", "column.getLeafColumns"))
  };
  for (const feature of table._features) {
    feature.createColumn == null || feature.createColumn(column, table);
  }
  return column;
}
var debug = "debugHeaders";
function createHeader(table, column, options) {
  var _options$id;
  const id = (_options$id = options.id) != null ? _options$id : column.id;
  let header = {
    id,
    column,
    index: options.index,
    isPlaceholder: !!options.isPlaceholder,
    placeholderId: options.placeholderId,
    depth: options.depth,
    subHeaders: [],
    colSpan: 0,
    rowSpan: 0,
    headerGroup: null,
    getLeafHeaders: () => {
      const leafHeaders = [];
      const recurseHeader = (h3) => {
        if (h3.subHeaders && h3.subHeaders.length) {
          h3.subHeaders.map(recurseHeader);
        }
        leafHeaders.push(h3);
      };
      recurseHeader(header);
      return leafHeaders;
    },
    getContext: () => ({
      table,
      header,
      column
    })
  };
  table._features.forEach((feature) => {
    feature.createHeader == null || feature.createHeader(header, table);
  });
  return header;
}
var Headers = {
  createTable: (table) => {
    table.getHeaderGroups = memo(() => [table.getAllColumns(), table.getVisibleLeafColumns(), table.getState().columnPinning.left, table.getState().columnPinning.right], (allColumns, leafColumns, left, right) => {
      var _left$map$filter, _right$map$filter;
      const leftColumns = (_left$map$filter = left == null ? void 0 : left.map((columnId) => leafColumns.find((d3) => d3.id === columnId)).filter(Boolean)) != null ? _left$map$filter : [];
      const rightColumns = (_right$map$filter = right == null ? void 0 : right.map((columnId) => leafColumns.find((d3) => d3.id === columnId)).filter(Boolean)) != null ? _right$map$filter : [];
      const centerColumns = leafColumns.filter((column) => !(left != null && left.includes(column.id)) && !(right != null && right.includes(column.id)));
      const headerGroups = buildHeaderGroups(allColumns, [...leftColumns, ...centerColumns, ...rightColumns], table);
      return headerGroups;
    }, getMemoOptions(table.options, debug, "getHeaderGroups"));
    table.getCenterHeaderGroups = memo(() => [table.getAllColumns(), table.getVisibleLeafColumns(), table.getState().columnPinning.left, table.getState().columnPinning.right], (allColumns, leafColumns, left, right) => {
      leafColumns = leafColumns.filter((column) => !(left != null && left.includes(column.id)) && !(right != null && right.includes(column.id)));
      return buildHeaderGroups(allColumns, leafColumns, table, "center");
    }, getMemoOptions(table.options, debug, "getCenterHeaderGroups"));
    table.getLeftHeaderGroups = memo(() => [table.getAllColumns(), table.getVisibleLeafColumns(), table.getState().columnPinning.left], (allColumns, leafColumns, left) => {
      var _left$map$filter2;
      const orderedLeafColumns = (_left$map$filter2 = left == null ? void 0 : left.map((columnId) => leafColumns.find((d3) => d3.id === columnId)).filter(Boolean)) != null ? _left$map$filter2 : [];
      return buildHeaderGroups(allColumns, orderedLeafColumns, table, "left");
    }, getMemoOptions(table.options, debug, "getLeftHeaderGroups"));
    table.getRightHeaderGroups = memo(() => [table.getAllColumns(), table.getVisibleLeafColumns(), table.getState().columnPinning.right], (allColumns, leafColumns, right) => {
      var _right$map$filter2;
      const orderedLeafColumns = (_right$map$filter2 = right == null ? void 0 : right.map((columnId) => leafColumns.find((d3) => d3.id === columnId)).filter(Boolean)) != null ? _right$map$filter2 : [];
      return buildHeaderGroups(allColumns, orderedLeafColumns, table, "right");
    }, getMemoOptions(table.options, debug, "getRightHeaderGroups"));
    table.getFooterGroups = memo(() => [table.getHeaderGroups()], (headerGroups) => {
      return [...headerGroups].reverse();
    }, getMemoOptions(table.options, debug, "getFooterGroups"));
    table.getLeftFooterGroups = memo(() => [table.getLeftHeaderGroups()], (headerGroups) => {
      return [...headerGroups].reverse();
    }, getMemoOptions(table.options, debug, "getLeftFooterGroups"));
    table.getCenterFooterGroups = memo(() => [table.getCenterHeaderGroups()], (headerGroups) => {
      return [...headerGroups].reverse();
    }, getMemoOptions(table.options, debug, "getCenterFooterGroups"));
    table.getRightFooterGroups = memo(() => [table.getRightHeaderGroups()], (headerGroups) => {
      return [...headerGroups].reverse();
    }, getMemoOptions(table.options, debug, "getRightFooterGroups"));
    table.getFlatHeaders = memo(() => [table.getHeaderGroups()], (headerGroups) => {
      return headerGroups.map((headerGroup) => {
        return headerGroup.headers;
      }).flat();
    }, getMemoOptions(table.options, debug, "getFlatHeaders"));
    table.getLeftFlatHeaders = memo(() => [table.getLeftHeaderGroups()], (left) => {
      return left.map((headerGroup) => {
        return headerGroup.headers;
      }).flat();
    }, getMemoOptions(table.options, debug, "getLeftFlatHeaders"));
    table.getCenterFlatHeaders = memo(() => [table.getCenterHeaderGroups()], (left) => {
      return left.map((headerGroup) => {
        return headerGroup.headers;
      }).flat();
    }, getMemoOptions(table.options, debug, "getCenterFlatHeaders"));
    table.getRightFlatHeaders = memo(() => [table.getRightHeaderGroups()], (left) => {
      return left.map((headerGroup) => {
        return headerGroup.headers;
      }).flat();
    }, getMemoOptions(table.options, debug, "getRightFlatHeaders"));
    table.getCenterLeafHeaders = memo(() => [table.getCenterFlatHeaders()], (flatHeaders) => {
      return flatHeaders.filter((header) => {
        var _header$subHeaders;
        return !((_header$subHeaders = header.subHeaders) != null && _header$subHeaders.length);
      });
    }, getMemoOptions(table.options, debug, "getCenterLeafHeaders"));
    table.getLeftLeafHeaders = memo(() => [table.getLeftFlatHeaders()], (flatHeaders) => {
      return flatHeaders.filter((header) => {
        var _header$subHeaders2;
        return !((_header$subHeaders2 = header.subHeaders) != null && _header$subHeaders2.length);
      });
    }, getMemoOptions(table.options, debug, "getLeftLeafHeaders"));
    table.getRightLeafHeaders = memo(() => [table.getRightFlatHeaders()], (flatHeaders) => {
      return flatHeaders.filter((header) => {
        var _header$subHeaders3;
        return !((_header$subHeaders3 = header.subHeaders) != null && _header$subHeaders3.length);
      });
    }, getMemoOptions(table.options, debug, "getRightLeafHeaders"));
    table.getLeafHeaders = memo(() => [table.getLeftHeaderGroups(), table.getCenterHeaderGroups(), table.getRightHeaderGroups()], (left, center, right) => {
      var _left$0$headers, _left$, _center$0$headers, _center$, _right$0$headers, _right$;
      return [...(_left$0$headers = (_left$ = left[0]) == null ? void 0 : _left$.headers) != null ? _left$0$headers : [], ...(_center$0$headers = (_center$ = center[0]) == null ? void 0 : _center$.headers) != null ? _center$0$headers : [], ...(_right$0$headers = (_right$ = right[0]) == null ? void 0 : _right$.headers) != null ? _right$0$headers : []].map((header) => {
        return header.getLeafHeaders();
      }).flat();
    }, getMemoOptions(table.options, debug, "getLeafHeaders"));
  }
};
function buildHeaderGroups(allColumns, columnsToGroup, table, headerFamily) {
  var _headerGroups$0$heade, _headerGroups$;
  let maxDepth = 0;
  const findMaxDepth = function(columns, depth) {
    if (depth === void 0) {
      depth = 1;
    }
    maxDepth = Math.max(maxDepth, depth);
    columns.filter((column) => column.getIsVisible()).forEach((column) => {
      var _column$columns;
      if ((_column$columns = column.columns) != null && _column$columns.length) {
        findMaxDepth(column.columns, depth + 1);
      }
    }, 0);
  };
  findMaxDepth(allColumns);
  let headerGroups = [];
  const createHeaderGroup = (headersToGroup, depth) => {
    const headerGroup = {
      depth,
      id: [headerFamily, `${depth}`].filter(Boolean).join("_"),
      headers: []
    };
    const pendingParentHeaders = [];
    headersToGroup.forEach((headerToGroup) => {
      const latestPendingParentHeader = [...pendingParentHeaders].reverse()[0];
      const isLeafHeader = headerToGroup.column.depth === headerGroup.depth;
      let column;
      let isPlaceholder = false;
      if (isLeafHeader && headerToGroup.column.parent) {
        column = headerToGroup.column.parent;
      } else {
        column = headerToGroup.column;
        isPlaceholder = true;
      }
      if (latestPendingParentHeader && (latestPendingParentHeader == null ? void 0 : latestPendingParentHeader.column) === column) {
        latestPendingParentHeader.subHeaders.push(headerToGroup);
      } else {
        const header = createHeader(table, column, {
          id: [headerFamily, depth, column.id, headerToGroup == null ? void 0 : headerToGroup.id].filter(Boolean).join("_"),
          isPlaceholder,
          placeholderId: isPlaceholder ? `${pendingParentHeaders.filter((d3) => d3.column === column).length}` : void 0,
          depth,
          index: pendingParentHeaders.length
        });
        header.subHeaders.push(headerToGroup);
        pendingParentHeaders.push(header);
      }
      headerGroup.headers.push(headerToGroup);
      headerToGroup.headerGroup = headerGroup;
    });
    headerGroups.push(headerGroup);
    if (depth > 0) {
      createHeaderGroup(pendingParentHeaders, depth - 1);
    }
  };
  const bottomHeaders = columnsToGroup.map((column, index) => createHeader(table, column, {
    depth: maxDepth,
    index
  }));
  createHeaderGroup(bottomHeaders, maxDepth - 1);
  headerGroups.reverse();
  const recurseHeadersForSpans = (headers) => {
    const filteredHeaders = headers.filter((header) => header.column.getIsVisible());
    return filteredHeaders.map((header) => {
      let colSpan = 0;
      let rowSpan = 0;
      let childRowSpans = [0];
      if (header.subHeaders && header.subHeaders.length) {
        childRowSpans = [];
        recurseHeadersForSpans(header.subHeaders).forEach((_ref) => {
          let {
            colSpan: childColSpan,
            rowSpan: childRowSpan
          } = _ref;
          colSpan += childColSpan;
          childRowSpans.push(childRowSpan);
        });
      } else {
        colSpan = 1;
      }
      const minChildRowSpan = Math.min(...childRowSpans);
      rowSpan = rowSpan + minChildRowSpan;
      header.colSpan = colSpan;
      header.rowSpan = rowSpan;
      return {
        colSpan,
        rowSpan
      };
    });
  };
  recurseHeadersForSpans((_headerGroups$0$heade = (_headerGroups$ = headerGroups[0]) == null ? void 0 : _headerGroups$.headers) != null ? _headerGroups$0$heade : []);
  return headerGroups;
}
var createRow = (table, id, original, rowIndex, depth, subRows, parentId) => {
  let row = {
    id,
    index: rowIndex,
    original,
    depth,
    parentId,
    _valuesCache: {},
    _uniqueValuesCache: {},
    getValue: (columnId) => {
      if (row._valuesCache.hasOwnProperty(columnId)) {
        return row._valuesCache[columnId];
      }
      const column = table.getColumn(columnId);
      if (!(column != null && column.accessorFn)) {
        return void 0;
      }
      row._valuesCache[columnId] = column.accessorFn(row.original, rowIndex);
      return row._valuesCache[columnId];
    },
    getUniqueValues: (columnId) => {
      if (row._uniqueValuesCache.hasOwnProperty(columnId)) {
        return row._uniqueValuesCache[columnId];
      }
      const column = table.getColumn(columnId);
      if (!(column != null && column.accessorFn)) {
        return void 0;
      }
      if (!column.columnDef.getUniqueValues) {
        row._uniqueValuesCache[columnId] = [row.getValue(columnId)];
        return row._uniqueValuesCache[columnId];
      }
      row._uniqueValuesCache[columnId] = column.columnDef.getUniqueValues(row.original, rowIndex);
      return row._uniqueValuesCache[columnId];
    },
    renderValue: (columnId) => {
      var _row$getValue;
      return (_row$getValue = row.getValue(columnId)) != null ? _row$getValue : table.options.renderFallbackValue;
    },
    subRows: subRows != null ? subRows : [],
    getLeafRows: () => flattenBy(row.subRows, (d3) => d3.subRows),
    getParentRow: () => row.parentId ? table.getRow(row.parentId, true) : void 0,
    getParentRows: () => {
      let parentRows = [];
      let currentRow = row;
      while (true) {
        const parentRow = currentRow.getParentRow();
        if (!parentRow)
          break;
        parentRows.push(parentRow);
        currentRow = parentRow;
      }
      return parentRows.reverse();
    },
    getAllCells: memo(() => [table.getAllLeafColumns()], (leafColumns) => {
      return leafColumns.map((column) => {
        return createCell(table, row, column, column.id);
      });
    }, getMemoOptions(table.options, "debugRows", "getAllCells")),
    _getAllCellsByColumnId: memo(() => [row.getAllCells()], (allCells) => {
      return allCells.reduce((acc, cell) => {
        acc[cell.column.id] = cell;
        return acc;
      }, {});
    }, getMemoOptions(table.options, "debugRows", "getAllCellsByColumnId"))
  };
  for (let i4 = 0; i4 < table._features.length; i4++) {
    const feature = table._features[i4];
    feature == null || feature.createRow == null || feature.createRow(row, table);
  }
  return row;
};
var ColumnFaceting = {
  createColumn: (column, table) => {
    column._getFacetedRowModel = table.options.getFacetedRowModel && table.options.getFacetedRowModel(table, column.id);
    column.getFacetedRowModel = () => {
      if (!column._getFacetedRowModel) {
        return table.getPreFilteredRowModel();
      }
      return column._getFacetedRowModel();
    };
    column._getFacetedUniqueValues = table.options.getFacetedUniqueValues && table.options.getFacetedUniqueValues(table, column.id);
    column.getFacetedUniqueValues = () => {
      if (!column._getFacetedUniqueValues) {
        return /* @__PURE__ */ new Map();
      }
      return column._getFacetedUniqueValues();
    };
    column._getFacetedMinMaxValues = table.options.getFacetedMinMaxValues && table.options.getFacetedMinMaxValues(table, column.id);
    column.getFacetedMinMaxValues = () => {
      if (!column._getFacetedMinMaxValues) {
        return void 0;
      }
      return column._getFacetedMinMaxValues();
    };
  }
};
var includesString = (row, columnId, filterValue) => {
  var _row$getValue;
  const search = filterValue.toLowerCase();
  return Boolean((_row$getValue = row.getValue(columnId)) == null || (_row$getValue = _row$getValue.toString()) == null || (_row$getValue = _row$getValue.toLowerCase()) == null ? void 0 : _row$getValue.includes(search));
};
includesString.autoRemove = (val) => testFalsey(val);
var includesStringSensitive = (row, columnId, filterValue) => {
  var _row$getValue2;
  return Boolean((_row$getValue2 = row.getValue(columnId)) == null || (_row$getValue2 = _row$getValue2.toString()) == null ? void 0 : _row$getValue2.includes(filterValue));
};
includesStringSensitive.autoRemove = (val) => testFalsey(val);
var equalsString = (row, columnId, filterValue) => {
  var _row$getValue3;
  return ((_row$getValue3 = row.getValue(columnId)) == null || (_row$getValue3 = _row$getValue3.toString()) == null ? void 0 : _row$getValue3.toLowerCase()) === (filterValue == null ? void 0 : filterValue.toLowerCase());
};
equalsString.autoRemove = (val) => testFalsey(val);
var arrIncludes = (row, columnId, filterValue) => {
  var _row$getValue4;
  return (_row$getValue4 = row.getValue(columnId)) == null ? void 0 : _row$getValue4.includes(filterValue);
};
arrIncludes.autoRemove = (val) => testFalsey(val) || !(val != null && val.length);
var arrIncludesAll = (row, columnId, filterValue) => {
  return !filterValue.some((val) => {
    var _row$getValue5;
    return !((_row$getValue5 = row.getValue(columnId)) != null && _row$getValue5.includes(val));
  });
};
arrIncludesAll.autoRemove = (val) => testFalsey(val) || !(val != null && val.length);
var arrIncludesSome = (row, columnId, filterValue) => {
  return filterValue.some((val) => {
    var _row$getValue6;
    return (_row$getValue6 = row.getValue(columnId)) == null ? void 0 : _row$getValue6.includes(val);
  });
};
arrIncludesSome.autoRemove = (val) => testFalsey(val) || !(val != null && val.length);
var equals = (row, columnId, filterValue) => {
  return row.getValue(columnId) === filterValue;
};
equals.autoRemove = (val) => testFalsey(val);
var weakEquals = (row, columnId, filterValue) => {
  return row.getValue(columnId) == filterValue;
};
weakEquals.autoRemove = (val) => testFalsey(val);
var inNumberRange = (row, columnId, filterValue) => {
  let [min2, max2] = filterValue;
  const rowValue = row.getValue(columnId);
  return rowValue >= min2 && rowValue <= max2;
};
inNumberRange.resolveFilterValue = (val) => {
  let [unsafeMin, unsafeMax] = val;
  let parsedMin = typeof unsafeMin !== "number" ? parseFloat(unsafeMin) : unsafeMin;
  let parsedMax = typeof unsafeMax !== "number" ? parseFloat(unsafeMax) : unsafeMax;
  let min2 = unsafeMin === null || Number.isNaN(parsedMin) ? -Infinity : parsedMin;
  let max2 = unsafeMax === null || Number.isNaN(parsedMax) ? Infinity : parsedMax;
  if (min2 > max2) {
    const temp = min2;
    min2 = max2;
    max2 = temp;
  }
  return [min2, max2];
};
inNumberRange.autoRemove = (val) => testFalsey(val) || testFalsey(val[0]) && testFalsey(val[1]);
var filterFns = {
  includesString,
  includesStringSensitive,
  equalsString,
  arrIncludes,
  arrIncludesAll,
  arrIncludesSome,
  equals,
  weakEquals,
  inNumberRange
};
function testFalsey(val) {
  return val === void 0 || val === null || val === "";
}
var ColumnFiltering = {
  getDefaultColumnDef: () => {
    return {
      filterFn: "auto"
    };
  },
  getInitialState: (state) => {
    return {
      columnFilters: [],
      ...state
    };
  },
  getDefaultOptions: (table) => {
    return {
      onColumnFiltersChange: makeStateUpdater("columnFilters", table),
      filterFromLeafRows: false,
      maxLeafRowFilterDepth: 100
    };
  },
  createColumn: (column, table) => {
    column.getAutoFilterFn = () => {
      const firstRow = table.getCoreRowModel().flatRows[0];
      const value = firstRow == null ? void 0 : firstRow.getValue(column.id);
      if (typeof value === "string") {
        return filterFns.includesString;
      }
      if (typeof value === "number") {
        return filterFns.inNumberRange;
      }
      if (typeof value === "boolean") {
        return filterFns.equals;
      }
      if (value !== null && typeof value === "object") {
        return filterFns.equals;
      }
      if (Array.isArray(value)) {
        return filterFns.arrIncludes;
      }
      return filterFns.weakEquals;
    };
    column.getFilterFn = () => {
      var _table$options$filter, _table$options$filter2;
      return isFunction(column.columnDef.filterFn) ? column.columnDef.filterFn : column.columnDef.filterFn === "auto" ? column.getAutoFilterFn() : (
        // @ts-ignore
        (_table$options$filter = (_table$options$filter2 = table.options.filterFns) == null ? void 0 : _table$options$filter2[column.columnDef.filterFn]) != null ? _table$options$filter : filterFns[column.columnDef.filterFn]
      );
    };
    column.getCanFilter = () => {
      var _column$columnDef$ena, _table$options$enable, _table$options$enable2;
      return ((_column$columnDef$ena = column.columnDef.enableColumnFilter) != null ? _column$columnDef$ena : true) && ((_table$options$enable = table.options.enableColumnFilters) != null ? _table$options$enable : true) && ((_table$options$enable2 = table.options.enableFilters) != null ? _table$options$enable2 : true) && !!column.accessorFn;
    };
    column.getIsFiltered = () => column.getFilterIndex() > -1;
    column.getFilterValue = () => {
      var _table$getState$colum;
      return (_table$getState$colum = table.getState().columnFilters) == null || (_table$getState$colum = _table$getState$colum.find((d3) => d3.id === column.id)) == null ? void 0 : _table$getState$colum.value;
    };
    column.getFilterIndex = () => {
      var _table$getState$colum2, _table$getState$colum3;
      return (_table$getState$colum2 = (_table$getState$colum3 = table.getState().columnFilters) == null ? void 0 : _table$getState$colum3.findIndex((d3) => d3.id === column.id)) != null ? _table$getState$colum2 : -1;
    };
    column.setFilterValue = (value) => {
      table.setColumnFilters((old) => {
        const filterFn = column.getFilterFn();
        const previousFilter = old == null ? void 0 : old.find((d3) => d3.id === column.id);
        const newFilter = functionalUpdate(value, previousFilter ? previousFilter.value : void 0);
        if (shouldAutoRemoveFilter(filterFn, newFilter, column)) {
          var _old$filter;
          return (_old$filter = old == null ? void 0 : old.filter((d3) => d3.id !== column.id)) != null ? _old$filter : [];
        }
        const newFilterObj = {
          id: column.id,
          value: newFilter
        };
        if (previousFilter) {
          var _old$map;
          return (_old$map = old == null ? void 0 : old.map((d3) => {
            if (d3.id === column.id) {
              return newFilterObj;
            }
            return d3;
          })) != null ? _old$map : [];
        }
        if (old != null && old.length) {
          return [...old, newFilterObj];
        }
        return [newFilterObj];
      });
    };
  },
  createRow: (row, _table) => {
    row.columnFilters = {};
    row.columnFiltersMeta = {};
  },
  createTable: (table) => {
    table.setColumnFilters = (updater) => {
      const leafColumns = table.getAllLeafColumns();
      const updateFn = (old) => {
        var _functionalUpdate;
        return (_functionalUpdate = functionalUpdate(updater, old)) == null ? void 0 : _functionalUpdate.filter((filter) => {
          const column = leafColumns.find((d3) => d3.id === filter.id);
          if (column) {
            const filterFn = column.getFilterFn();
            if (shouldAutoRemoveFilter(filterFn, filter.value, column)) {
              return false;
            }
          }
          return true;
        });
      };
      table.options.onColumnFiltersChange == null || table.options.onColumnFiltersChange(updateFn);
    };
    table.resetColumnFilters = (defaultState) => {
      var _table$initialState$c, _table$initialState;
      table.setColumnFilters(defaultState ? [] : (_table$initialState$c = (_table$initialState = table.initialState) == null ? void 0 : _table$initialState.columnFilters) != null ? _table$initialState$c : []);
    };
    table.getPreFilteredRowModel = () => table.getCoreRowModel();
    table.getFilteredRowModel = () => {
      if (!table._getFilteredRowModel && table.options.getFilteredRowModel) {
        table._getFilteredRowModel = table.options.getFilteredRowModel(table);
      }
      if (table.options.manualFiltering || !table._getFilteredRowModel) {
        return table.getPreFilteredRowModel();
      }
      return table._getFilteredRowModel();
    };
  }
};
function shouldAutoRemoveFilter(filterFn, value, column) {
  return (filterFn && filterFn.autoRemove ? filterFn.autoRemove(value, column) : false) || typeof value === "undefined" || typeof value === "string" && !value;
}
var sum = (columnId, _leafRows, childRows) => {
  return childRows.reduce((sum2, next) => {
    const nextValue = next.getValue(columnId);
    return sum2 + (typeof nextValue === "number" ? nextValue : 0);
  }, 0);
};
var min = (columnId, _leafRows, childRows) => {
  let min2;
  childRows.forEach((row) => {
    const value = row.getValue(columnId);
    if (value != null && (min2 > value || min2 === void 0 && value >= value)) {
      min2 = value;
    }
  });
  return min2;
};
var max = (columnId, _leafRows, childRows) => {
  let max2;
  childRows.forEach((row) => {
    const value = row.getValue(columnId);
    if (value != null && (max2 < value || max2 === void 0 && value >= value)) {
      max2 = value;
    }
  });
  return max2;
};
var extent = (columnId, _leafRows, childRows) => {
  let min2;
  let max2;
  childRows.forEach((row) => {
    const value = row.getValue(columnId);
    if (value != null) {
      if (min2 === void 0) {
        if (value >= value)
          min2 = max2 = value;
      } else {
        if (min2 > value)
          min2 = value;
        if (max2 < value)
          max2 = value;
      }
    }
  });
  return [min2, max2];
};
var mean = (columnId, leafRows) => {
  let count2 = 0;
  let sum2 = 0;
  leafRows.forEach((row) => {
    let value = row.getValue(columnId);
    if (value != null && (value = +value) >= value) {
      ++count2, sum2 += value;
    }
  });
  if (count2)
    return sum2 / count2;
  return;
};
var median = (columnId, leafRows) => {
  if (!leafRows.length) {
    return;
  }
  const values = leafRows.map((row) => row.getValue(columnId));
  if (!isNumberArray(values)) {
    return;
  }
  if (values.length === 1) {
    return values[0];
  }
  const mid = Math.floor(values.length / 2);
  const nums = values.sort((a3, b2) => a3 - b2);
  return values.length % 2 !== 0 ? nums[mid] : (nums[mid - 1] + nums[mid]) / 2;
};
var unique = (columnId, leafRows) => {
  return Array.from(new Set(leafRows.map((d3) => d3.getValue(columnId))).values());
};
var uniqueCount = (columnId, leafRows) => {
  return new Set(leafRows.map((d3) => d3.getValue(columnId))).size;
};
var count = (_columnId, leafRows) => {
  return leafRows.length;
};
var aggregationFns = {
  sum,
  min,
  max,
  extent,
  mean,
  median,
  unique,
  uniqueCount,
  count
};
var ColumnGrouping = {
  getDefaultColumnDef: () => {
    return {
      aggregatedCell: (props) => {
        var _toString, _props$getValue;
        return (_toString = (_props$getValue = props.getValue()) == null || _props$getValue.toString == null ? void 0 : _props$getValue.toString()) != null ? _toString : null;
      },
      aggregationFn: "auto"
    };
  },
  getInitialState: (state) => {
    return {
      grouping: [],
      ...state
    };
  },
  getDefaultOptions: (table) => {
    return {
      onGroupingChange: makeStateUpdater("grouping", table),
      groupedColumnMode: "reorder"
    };
  },
  createColumn: (column, table) => {
    column.toggleGrouping = () => {
      table.setGrouping((old) => {
        if (old != null && old.includes(column.id)) {
          return old.filter((d3) => d3 !== column.id);
        }
        return [...old != null ? old : [], column.id];
      });
    };
    column.getCanGroup = () => {
      var _column$columnDef$ena, _table$options$enable;
      return ((_column$columnDef$ena = column.columnDef.enableGrouping) != null ? _column$columnDef$ena : true) && ((_table$options$enable = table.options.enableGrouping) != null ? _table$options$enable : true) && (!!column.accessorFn || !!column.columnDef.getGroupingValue);
    };
    column.getIsGrouped = () => {
      var _table$getState$group;
      return (_table$getState$group = table.getState().grouping) == null ? void 0 : _table$getState$group.includes(column.id);
    };
    column.getGroupedIndex = () => {
      var _table$getState$group2;
      return (_table$getState$group2 = table.getState().grouping) == null ? void 0 : _table$getState$group2.indexOf(column.id);
    };
    column.getToggleGroupingHandler = () => {
      const canGroup = column.getCanGroup();
      return () => {
        if (!canGroup)
          return;
        column.toggleGrouping();
      };
    };
    column.getAutoAggregationFn = () => {
      const firstRow = table.getCoreRowModel().flatRows[0];
      const value = firstRow == null ? void 0 : firstRow.getValue(column.id);
      if (typeof value === "number") {
        return aggregationFns.sum;
      }
      if (Object.prototype.toString.call(value) === "[object Date]") {
        return aggregationFns.extent;
      }
    };
    column.getAggregationFn = () => {
      var _table$options$aggreg, _table$options$aggreg2;
      if (!column) {
        throw new Error();
      }
      return isFunction(column.columnDef.aggregationFn) ? column.columnDef.aggregationFn : column.columnDef.aggregationFn === "auto" ? column.getAutoAggregationFn() : (_table$options$aggreg = (_table$options$aggreg2 = table.options.aggregationFns) == null ? void 0 : _table$options$aggreg2[column.columnDef.aggregationFn]) != null ? _table$options$aggreg : aggregationFns[column.columnDef.aggregationFn];
    };
  },
  createTable: (table) => {
    table.setGrouping = (updater) => table.options.onGroupingChange == null ? void 0 : table.options.onGroupingChange(updater);
    table.resetGrouping = (defaultState) => {
      var _table$initialState$g, _table$initialState;
      table.setGrouping(defaultState ? [] : (_table$initialState$g = (_table$initialState = table.initialState) == null ? void 0 : _table$initialState.grouping) != null ? _table$initialState$g : []);
    };
    table.getPreGroupedRowModel = () => table.getFilteredRowModel();
    table.getGroupedRowModel = () => {
      if (!table._getGroupedRowModel && table.options.getGroupedRowModel) {
        table._getGroupedRowModel = table.options.getGroupedRowModel(table);
      }
      if (table.options.manualGrouping || !table._getGroupedRowModel) {
        return table.getPreGroupedRowModel();
      }
      return table._getGroupedRowModel();
    };
  },
  createRow: (row, table) => {
    row.getIsGrouped = () => !!row.groupingColumnId;
    row.getGroupingValue = (columnId) => {
      if (row._groupingValuesCache.hasOwnProperty(columnId)) {
        return row._groupingValuesCache[columnId];
      }
      const column = table.getColumn(columnId);
      if (!(column != null && column.columnDef.getGroupingValue)) {
        return row.getValue(columnId);
      }
      row._groupingValuesCache[columnId] = column.columnDef.getGroupingValue(row.original);
      return row._groupingValuesCache[columnId];
    };
    row._groupingValuesCache = {};
  },
  createCell: (cell, column, row, table) => {
    cell.getIsGrouped = () => column.getIsGrouped() && column.id === row.groupingColumnId;
    cell.getIsPlaceholder = () => !cell.getIsGrouped() && column.getIsGrouped();
    cell.getIsAggregated = () => {
      var _row$subRows;
      return !cell.getIsGrouped() && !cell.getIsPlaceholder() && !!((_row$subRows = row.subRows) != null && _row$subRows.length);
    };
  }
};
function orderColumns(leafColumns, grouping, groupedColumnMode) {
  if (!(grouping != null && grouping.length) || !groupedColumnMode) {
    return leafColumns;
  }
  const nonGroupingColumns = leafColumns.filter((col) => !grouping.includes(col.id));
  if (groupedColumnMode === "remove") {
    return nonGroupingColumns;
  }
  const groupingColumns = grouping.map((g4) => leafColumns.find((col) => col.id === g4)).filter(Boolean);
  return [...groupingColumns, ...nonGroupingColumns];
}
var ColumnOrdering = {
  getInitialState: (state) => {
    return {
      columnOrder: [],
      ...state
    };
  },
  getDefaultOptions: (table) => {
    return {
      onColumnOrderChange: makeStateUpdater("columnOrder", table)
    };
  },
  createColumn: (column, table) => {
    column.getIndex = memo((position) => [_getVisibleLeafColumns(table, position)], (columns) => columns.findIndex((d3) => d3.id === column.id), getMemoOptions(table.options, "debugColumns", "getIndex"));
    column.getIsFirstColumn = (position) => {
      var _columns$;
      const columns = _getVisibleLeafColumns(table, position);
      return ((_columns$ = columns[0]) == null ? void 0 : _columns$.id) === column.id;
    };
    column.getIsLastColumn = (position) => {
      var _columns;
      const columns = _getVisibleLeafColumns(table, position);
      return ((_columns = columns[columns.length - 1]) == null ? void 0 : _columns.id) === column.id;
    };
  },
  createTable: (table) => {
    table.setColumnOrder = (updater) => table.options.onColumnOrderChange == null ? void 0 : table.options.onColumnOrderChange(updater);
    table.resetColumnOrder = (defaultState) => {
      var _table$initialState$c;
      table.setColumnOrder(defaultState ? [] : (_table$initialState$c = table.initialState.columnOrder) != null ? _table$initialState$c : []);
    };
    table._getOrderColumnsFn = memo(() => [table.getState().columnOrder, table.getState().grouping, table.options.groupedColumnMode], (columnOrder, grouping, groupedColumnMode) => (columns) => {
      let orderedColumns = [];
      if (!(columnOrder != null && columnOrder.length)) {
        orderedColumns = columns;
      } else {
        const columnOrderCopy = [...columnOrder];
        const columnsCopy = [...columns];
        while (columnsCopy.length && columnOrderCopy.length) {
          const targetColumnId = columnOrderCopy.shift();
          const foundIndex = columnsCopy.findIndex((d3) => d3.id === targetColumnId);
          if (foundIndex > -1) {
            orderedColumns.push(columnsCopy.splice(foundIndex, 1)[0]);
          }
        }
        orderedColumns = [...orderedColumns, ...columnsCopy];
      }
      return orderColumns(orderedColumns, grouping, groupedColumnMode);
    }, getMemoOptions(table.options, "debugTable", "_getOrderColumnsFn"));
  }
};
var getDefaultColumnPinningState = () => ({
  left: [],
  right: []
});
var ColumnPinning = {
  getInitialState: (state) => {
    return {
      columnPinning: getDefaultColumnPinningState(),
      ...state
    };
  },
  getDefaultOptions: (table) => {
    return {
      onColumnPinningChange: makeStateUpdater("columnPinning", table)
    };
  },
  createColumn: (column, table) => {
    column.pin = (position) => {
      const columnIds = column.getLeafColumns().map((d3) => d3.id).filter(Boolean);
      table.setColumnPinning((old) => {
        var _old$left3, _old$right3;
        if (position === "right") {
          var _old$left, _old$right;
          return {
            left: ((_old$left = old == null ? void 0 : old.left) != null ? _old$left : []).filter((d3) => !(columnIds != null && columnIds.includes(d3))),
            right: [...((_old$right = old == null ? void 0 : old.right) != null ? _old$right : []).filter((d3) => !(columnIds != null && columnIds.includes(d3))), ...columnIds]
          };
        }
        if (position === "left") {
          var _old$left2, _old$right2;
          return {
            left: [...((_old$left2 = old == null ? void 0 : old.left) != null ? _old$left2 : []).filter((d3) => !(columnIds != null && columnIds.includes(d3))), ...columnIds],
            right: ((_old$right2 = old == null ? void 0 : old.right) != null ? _old$right2 : []).filter((d3) => !(columnIds != null && columnIds.includes(d3)))
          };
        }
        return {
          left: ((_old$left3 = old == null ? void 0 : old.left) != null ? _old$left3 : []).filter((d3) => !(columnIds != null && columnIds.includes(d3))),
          right: ((_old$right3 = old == null ? void 0 : old.right) != null ? _old$right3 : []).filter((d3) => !(columnIds != null && columnIds.includes(d3)))
        };
      });
    };
    column.getCanPin = () => {
      const leafColumns = column.getLeafColumns();
      return leafColumns.some((d3) => {
        var _d$columnDef$enablePi, _ref, _table$options$enable;
        return ((_d$columnDef$enablePi = d3.columnDef.enablePinning) != null ? _d$columnDef$enablePi : true) && ((_ref = (_table$options$enable = table.options.enableColumnPinning) != null ? _table$options$enable : table.options.enablePinning) != null ? _ref : true);
      });
    };
    column.getIsPinned = () => {
      const leafColumnIds = column.getLeafColumns().map((d3) => d3.id);
      const {
        left,
        right
      } = table.getState().columnPinning;
      const isLeft = leafColumnIds.some((d3) => left == null ? void 0 : left.includes(d3));
      const isRight = leafColumnIds.some((d3) => right == null ? void 0 : right.includes(d3));
      return isLeft ? "left" : isRight ? "right" : false;
    };
    column.getPinnedIndex = () => {
      var _table$getState$colum, _table$getState$colum2;
      const position = column.getIsPinned();
      return position ? (_table$getState$colum = (_table$getState$colum2 = table.getState().columnPinning) == null || (_table$getState$colum2 = _table$getState$colum2[position]) == null ? void 0 : _table$getState$colum2.indexOf(column.id)) != null ? _table$getState$colum : -1 : 0;
    };
  },
  createRow: (row, table) => {
    row.getCenterVisibleCells = memo(() => [row._getAllVisibleCells(), table.getState().columnPinning.left, table.getState().columnPinning.right], (allCells, left, right) => {
      const leftAndRight = [...left != null ? left : [], ...right != null ? right : []];
      return allCells.filter((d3) => !leftAndRight.includes(d3.column.id));
    }, getMemoOptions(table.options, "debugRows", "getCenterVisibleCells"));
    row.getLeftVisibleCells = memo(() => [row._getAllVisibleCells(), table.getState().columnPinning.left], (allCells, left) => {
      const cells = (left != null ? left : []).map((columnId) => allCells.find((cell) => cell.column.id === columnId)).filter(Boolean).map((d3) => ({
        ...d3,
        position: "left"
      }));
      return cells;
    }, getMemoOptions(table.options, "debugRows", "getLeftVisibleCells"));
    row.getRightVisibleCells = memo(() => [row._getAllVisibleCells(), table.getState().columnPinning.right], (allCells, right) => {
      const cells = (right != null ? right : []).map((columnId) => allCells.find((cell) => cell.column.id === columnId)).filter(Boolean).map((d3) => ({
        ...d3,
        position: "right"
      }));
      return cells;
    }, getMemoOptions(table.options, "debugRows", "getRightVisibleCells"));
  },
  createTable: (table) => {
    table.setColumnPinning = (updater) => table.options.onColumnPinningChange == null ? void 0 : table.options.onColumnPinningChange(updater);
    table.resetColumnPinning = (defaultState) => {
      var _table$initialState$c, _table$initialState;
      return table.setColumnPinning(defaultState ? getDefaultColumnPinningState() : (_table$initialState$c = (_table$initialState = table.initialState) == null ? void 0 : _table$initialState.columnPinning) != null ? _table$initialState$c : getDefaultColumnPinningState());
    };
    table.getIsSomeColumnsPinned = (position) => {
      var _pinningState$positio;
      const pinningState = table.getState().columnPinning;
      if (!position) {
        var _pinningState$left, _pinningState$right;
        return Boolean(((_pinningState$left = pinningState.left) == null ? void 0 : _pinningState$left.length) || ((_pinningState$right = pinningState.right) == null ? void 0 : _pinningState$right.length));
      }
      return Boolean((_pinningState$positio = pinningState[position]) == null ? void 0 : _pinningState$positio.length);
    };
    table.getLeftLeafColumns = memo(() => [table.getAllLeafColumns(), table.getState().columnPinning.left], (allColumns, left) => {
      return (left != null ? left : []).map((columnId) => allColumns.find((column) => column.id === columnId)).filter(Boolean);
    }, getMemoOptions(table.options, "debugColumns", "getLeftLeafColumns"));
    table.getRightLeafColumns = memo(() => [table.getAllLeafColumns(), table.getState().columnPinning.right], (allColumns, right) => {
      return (right != null ? right : []).map((columnId) => allColumns.find((column) => column.id === columnId)).filter(Boolean);
    }, getMemoOptions(table.options, "debugColumns", "getRightLeafColumns"));
    table.getCenterLeafColumns = memo(() => [table.getAllLeafColumns(), table.getState().columnPinning.left, table.getState().columnPinning.right], (allColumns, left, right) => {
      const leftAndRight = [...left != null ? left : [], ...right != null ? right : []];
      return allColumns.filter((d3) => !leftAndRight.includes(d3.id));
    }, getMemoOptions(table.options, "debugColumns", "getCenterLeafColumns"));
  }
};
var defaultColumnSizing = {
  size: 150,
  minSize: 20,
  maxSize: Number.MAX_SAFE_INTEGER
};
var getDefaultColumnSizingInfoState = () => ({
  startOffset: null,
  startSize: null,
  deltaOffset: null,
  deltaPercentage: null,
  isResizingColumn: false,
  columnSizingStart: []
});
var ColumnSizing = {
  getDefaultColumnDef: () => {
    return defaultColumnSizing;
  },
  getInitialState: (state) => {
    return {
      columnSizing: {},
      columnSizingInfo: getDefaultColumnSizingInfoState(),
      ...state
    };
  },
  getDefaultOptions: (table) => {
    return {
      columnResizeMode: "onEnd",
      columnResizeDirection: "ltr",
      onColumnSizingChange: makeStateUpdater("columnSizing", table),
      onColumnSizingInfoChange: makeStateUpdater("columnSizingInfo", table)
    };
  },
  createColumn: (column, table) => {
    column.getSize = () => {
      var _column$columnDef$min, _ref, _column$columnDef$max;
      const columnSize = table.getState().columnSizing[column.id];
      return Math.min(Math.max((_column$columnDef$min = column.columnDef.minSize) != null ? _column$columnDef$min : defaultColumnSizing.minSize, (_ref = columnSize != null ? columnSize : column.columnDef.size) != null ? _ref : defaultColumnSizing.size), (_column$columnDef$max = column.columnDef.maxSize) != null ? _column$columnDef$max : defaultColumnSizing.maxSize);
    };
    column.getStart = memo((position) => [position, _getVisibleLeafColumns(table, position), table.getState().columnSizing], (position, columns) => columns.slice(0, column.getIndex(position)).reduce((sum2, column2) => sum2 + column2.getSize(), 0), getMemoOptions(table.options, "debugColumns", "getStart"));
    column.getAfter = memo((position) => [position, _getVisibleLeafColumns(table, position), table.getState().columnSizing], (position, columns) => columns.slice(column.getIndex(position) + 1).reduce((sum2, column2) => sum2 + column2.getSize(), 0), getMemoOptions(table.options, "debugColumns", "getAfter"));
    column.resetSize = () => {
      table.setColumnSizing((_ref2) => {
        let {
          [column.id]: _3,
          ...rest
        } = _ref2;
        return rest;
      });
    };
    column.getCanResize = () => {
      var _column$columnDef$ena, _table$options$enable;
      return ((_column$columnDef$ena = column.columnDef.enableResizing) != null ? _column$columnDef$ena : true) && ((_table$options$enable = table.options.enableColumnResizing) != null ? _table$options$enable : true);
    };
    column.getIsResizing = () => {
      return table.getState().columnSizingInfo.isResizingColumn === column.id;
    };
  },
  createHeader: (header, table) => {
    header.getSize = () => {
      let sum2 = 0;
      const recurse = (header2) => {
        if (header2.subHeaders.length) {
          header2.subHeaders.forEach(recurse);
        } else {
          var _header$column$getSiz;
          sum2 += (_header$column$getSiz = header2.column.getSize()) != null ? _header$column$getSiz : 0;
        }
      };
      recurse(header);
      return sum2;
    };
    header.getStart = () => {
      if (header.index > 0) {
        const prevSiblingHeader = header.headerGroup.headers[header.index - 1];
        return prevSiblingHeader.getStart() + prevSiblingHeader.getSize();
      }
      return 0;
    };
    header.getResizeHandler = (_contextDocument) => {
      const column = table.getColumn(header.column.id);
      const canResize = column == null ? void 0 : column.getCanResize();
      return (e3) => {
        if (!column || !canResize) {
          return;
        }
        e3.persist == null || e3.persist();
        if (isTouchStartEvent(e3)) {
          if (e3.touches && e3.touches.length > 1) {
            return;
          }
        }
        const startSize = header.getSize();
        const columnSizingStart = header ? header.getLeafHeaders().map((d3) => [d3.column.id, d3.column.getSize()]) : [[column.id, column.getSize()]];
        const clientX = isTouchStartEvent(e3) ? Math.round(e3.touches[0].clientX) : e3.clientX;
        const newColumnSizing = {};
        const updateOffset = (eventType, clientXPos) => {
          if (typeof clientXPos !== "number") {
            return;
          }
          table.setColumnSizingInfo((old) => {
            var _old$startOffset, _old$startSize;
            const deltaDirection = table.options.columnResizeDirection === "rtl" ? -1 : 1;
            const deltaOffset = (clientXPos - ((_old$startOffset = old == null ? void 0 : old.startOffset) != null ? _old$startOffset : 0)) * deltaDirection;
            const deltaPercentage = Math.max(deltaOffset / ((_old$startSize = old == null ? void 0 : old.startSize) != null ? _old$startSize : 0), -0.999999);
            old.columnSizingStart.forEach((_ref3) => {
              let [columnId, headerSize] = _ref3;
              newColumnSizing[columnId] = Math.round(Math.max(headerSize + headerSize * deltaPercentage, 0) * 100) / 100;
            });
            return {
              ...old,
              deltaOffset,
              deltaPercentage
            };
          });
          if (table.options.columnResizeMode === "onChange" || eventType === "end") {
            table.setColumnSizing((old) => ({
              ...old,
              ...newColumnSizing
            }));
          }
        };
        const onMove = (clientXPos) => updateOffset("move", clientXPos);
        const onEnd = (clientXPos) => {
          updateOffset("end", clientXPos);
          table.setColumnSizingInfo((old) => ({
            ...old,
            isResizingColumn: false,
            startOffset: null,
            startSize: null,
            deltaOffset: null,
            deltaPercentage: null,
            columnSizingStart: []
          }));
        };
        const contextDocument = _contextDocument || typeof document !== "undefined" ? document : null;
        const mouseEvents = {
          moveHandler: (e4) => onMove(e4.clientX),
          upHandler: (e4) => {
            contextDocument == null || contextDocument.removeEventListener("mousemove", mouseEvents.moveHandler);
            contextDocument == null || contextDocument.removeEventListener("mouseup", mouseEvents.upHandler);
            onEnd(e4.clientX);
          }
        };
        const touchEvents = {
          moveHandler: (e4) => {
            if (e4.cancelable) {
              e4.preventDefault();
              e4.stopPropagation();
            }
            onMove(e4.touches[0].clientX);
            return false;
          },
          upHandler: (e4) => {
            var _e$touches$;
            contextDocument == null || contextDocument.removeEventListener("touchmove", touchEvents.moveHandler);
            contextDocument == null || contextDocument.removeEventListener("touchend", touchEvents.upHandler);
            if (e4.cancelable) {
              e4.preventDefault();
              e4.stopPropagation();
            }
            onEnd((_e$touches$ = e4.touches[0]) == null ? void 0 : _e$touches$.clientX);
          }
        };
        const passiveIfSupported = passiveEventSupported() ? {
          passive: false
        } : false;
        if (isTouchStartEvent(e3)) {
          contextDocument == null || contextDocument.addEventListener("touchmove", touchEvents.moveHandler, passiveIfSupported);
          contextDocument == null || contextDocument.addEventListener("touchend", touchEvents.upHandler, passiveIfSupported);
        } else {
          contextDocument == null || contextDocument.addEventListener("mousemove", mouseEvents.moveHandler, passiveIfSupported);
          contextDocument == null || contextDocument.addEventListener("mouseup", mouseEvents.upHandler, passiveIfSupported);
        }
        table.setColumnSizingInfo((old) => ({
          ...old,
          startOffset: clientX,
          startSize,
          deltaOffset: 0,
          deltaPercentage: 0,
          columnSizingStart,
          isResizingColumn: column.id
        }));
      };
    };
  },
  createTable: (table) => {
    table.setColumnSizing = (updater) => table.options.onColumnSizingChange == null ? void 0 : table.options.onColumnSizingChange(updater);
    table.setColumnSizingInfo = (updater) => table.options.onColumnSizingInfoChange == null ? void 0 : table.options.onColumnSizingInfoChange(updater);
    table.resetColumnSizing = (defaultState) => {
      var _table$initialState$c;
      table.setColumnSizing(defaultState ? {} : (_table$initialState$c = table.initialState.columnSizing) != null ? _table$initialState$c : {});
    };
    table.resetHeaderSizeInfo = (defaultState) => {
      var _table$initialState$c2;
      table.setColumnSizingInfo(defaultState ? getDefaultColumnSizingInfoState() : (_table$initialState$c2 = table.initialState.columnSizingInfo) != null ? _table$initialState$c2 : getDefaultColumnSizingInfoState());
    };
    table.getTotalSize = () => {
      var _table$getHeaderGroup, _table$getHeaderGroup2;
      return (_table$getHeaderGroup = (_table$getHeaderGroup2 = table.getHeaderGroups()[0]) == null ? void 0 : _table$getHeaderGroup2.headers.reduce((sum2, header) => {
        return sum2 + header.getSize();
      }, 0)) != null ? _table$getHeaderGroup : 0;
    };
    table.getLeftTotalSize = () => {
      var _table$getLeftHeaderG, _table$getLeftHeaderG2;
      return (_table$getLeftHeaderG = (_table$getLeftHeaderG2 = table.getLeftHeaderGroups()[0]) == null ? void 0 : _table$getLeftHeaderG2.headers.reduce((sum2, header) => {
        return sum2 + header.getSize();
      }, 0)) != null ? _table$getLeftHeaderG : 0;
    };
    table.getCenterTotalSize = () => {
      var _table$getCenterHeade, _table$getCenterHeade2;
      return (_table$getCenterHeade = (_table$getCenterHeade2 = table.getCenterHeaderGroups()[0]) == null ? void 0 : _table$getCenterHeade2.headers.reduce((sum2, header) => {
        return sum2 + header.getSize();
      }, 0)) != null ? _table$getCenterHeade : 0;
    };
    table.getRightTotalSize = () => {
      var _table$getRightHeader, _table$getRightHeader2;
      return (_table$getRightHeader = (_table$getRightHeader2 = table.getRightHeaderGroups()[0]) == null ? void 0 : _table$getRightHeader2.headers.reduce((sum2, header) => {
        return sum2 + header.getSize();
      }, 0)) != null ? _table$getRightHeader : 0;
    };
  }
};
var passiveSupported = null;
function passiveEventSupported() {
  if (typeof passiveSupported === "boolean")
    return passiveSupported;
  let supported = false;
  try {
    const options = {
      get passive() {
        supported = true;
        return false;
      }
    };
    const noop = () => {
    };
    window.addEventListener("test", noop, options);
    window.removeEventListener("test", noop);
  } catch (err) {
    supported = false;
  }
  passiveSupported = supported;
  return passiveSupported;
}
function isTouchStartEvent(e3) {
  return e3.type === "touchstart";
}
var ColumnVisibility = {
  getInitialState: (state) => {
    return {
      columnVisibility: {},
      ...state
    };
  },
  getDefaultOptions: (table) => {
    return {
      onColumnVisibilityChange: makeStateUpdater("columnVisibility", table)
    };
  },
  createColumn: (column, table) => {
    column.toggleVisibility = (value) => {
      if (column.getCanHide()) {
        table.setColumnVisibility((old) => ({
          ...old,
          [column.id]: value != null ? value : !column.getIsVisible()
        }));
      }
    };
    column.getIsVisible = () => {
      var _ref, _table$getState$colum;
      const childColumns = column.columns;
      return (_ref = childColumns.length ? childColumns.some((c3) => c3.getIsVisible()) : (_table$getState$colum = table.getState().columnVisibility) == null ? void 0 : _table$getState$colum[column.id]) != null ? _ref : true;
    };
    column.getCanHide = () => {
      var _column$columnDef$ena, _table$options$enable;
      return ((_column$columnDef$ena = column.columnDef.enableHiding) != null ? _column$columnDef$ena : true) && ((_table$options$enable = table.options.enableHiding) != null ? _table$options$enable : true);
    };
    column.getToggleVisibilityHandler = () => {
      return (e3) => {
        column.toggleVisibility == null || column.toggleVisibility(e3.target.checked);
      };
    };
  },
  createRow: (row, table) => {
    row._getAllVisibleCells = memo(() => [row.getAllCells(), table.getState().columnVisibility], (cells) => {
      return cells.filter((cell) => cell.column.getIsVisible());
    }, getMemoOptions(table.options, "debugRows", "_getAllVisibleCells"));
    row.getVisibleCells = memo(() => [row.getLeftVisibleCells(), row.getCenterVisibleCells(), row.getRightVisibleCells()], (left, center, right) => [...left, ...center, ...right], getMemoOptions(table.options, "debugRows", "getVisibleCells"));
  },
  createTable: (table) => {
    const makeVisibleColumnsMethod = (key, getColumns) => {
      return memo(() => [getColumns(), getColumns().filter((d3) => d3.getIsVisible()).map((d3) => d3.id).join("_")], (columns) => {
        return columns.filter((d3) => d3.getIsVisible == null ? void 0 : d3.getIsVisible());
      }, getMemoOptions(table.options, "debugColumns", key));
    };
    table.getVisibleFlatColumns = makeVisibleColumnsMethod("getVisibleFlatColumns", () => table.getAllFlatColumns());
    table.getVisibleLeafColumns = makeVisibleColumnsMethod("getVisibleLeafColumns", () => table.getAllLeafColumns());
    table.getLeftVisibleLeafColumns = makeVisibleColumnsMethod("getLeftVisibleLeafColumns", () => table.getLeftLeafColumns());
    table.getRightVisibleLeafColumns = makeVisibleColumnsMethod("getRightVisibleLeafColumns", () => table.getRightLeafColumns());
    table.getCenterVisibleLeafColumns = makeVisibleColumnsMethod("getCenterVisibleLeafColumns", () => table.getCenterLeafColumns());
    table.setColumnVisibility = (updater) => table.options.onColumnVisibilityChange == null ? void 0 : table.options.onColumnVisibilityChange(updater);
    table.resetColumnVisibility = (defaultState) => {
      var _table$initialState$c;
      table.setColumnVisibility(defaultState ? {} : (_table$initialState$c = table.initialState.columnVisibility) != null ? _table$initialState$c : {});
    };
    table.toggleAllColumnsVisible = (value) => {
      var _value;
      value = (_value = value) != null ? _value : !table.getIsAllColumnsVisible();
      table.setColumnVisibility(table.getAllLeafColumns().reduce((obj, column) => ({
        ...obj,
        [column.id]: !value ? !(column.getCanHide != null && column.getCanHide()) : value
      }), {}));
    };
    table.getIsAllColumnsVisible = () => !table.getAllLeafColumns().some((column) => !(column.getIsVisible != null && column.getIsVisible()));
    table.getIsSomeColumnsVisible = () => table.getAllLeafColumns().some((column) => column.getIsVisible == null ? void 0 : column.getIsVisible());
    table.getToggleAllColumnsVisibilityHandler = () => {
      return (e3) => {
        var _target;
        table.toggleAllColumnsVisible((_target = e3.target) == null ? void 0 : _target.checked);
      };
    };
  }
};
function _getVisibleLeafColumns(table, position) {
  return !position ? table.getVisibleLeafColumns() : position === "center" ? table.getCenterVisibleLeafColumns() : position === "left" ? table.getLeftVisibleLeafColumns() : table.getRightVisibleLeafColumns();
}
var GlobalFaceting = {
  createTable: (table) => {
    table._getGlobalFacetedRowModel = table.options.getFacetedRowModel && table.options.getFacetedRowModel(table, "__global__");
    table.getGlobalFacetedRowModel = () => {
      if (table.options.manualFiltering || !table._getGlobalFacetedRowModel) {
        return table.getPreFilteredRowModel();
      }
      return table._getGlobalFacetedRowModel();
    };
    table._getGlobalFacetedUniqueValues = table.options.getFacetedUniqueValues && table.options.getFacetedUniqueValues(table, "__global__");
    table.getGlobalFacetedUniqueValues = () => {
      if (!table._getGlobalFacetedUniqueValues) {
        return /* @__PURE__ */ new Map();
      }
      return table._getGlobalFacetedUniqueValues();
    };
    table._getGlobalFacetedMinMaxValues = table.options.getFacetedMinMaxValues && table.options.getFacetedMinMaxValues(table, "__global__");
    table.getGlobalFacetedMinMaxValues = () => {
      if (!table._getGlobalFacetedMinMaxValues) {
        return;
      }
      return table._getGlobalFacetedMinMaxValues();
    };
  }
};
var GlobalFiltering = {
  getInitialState: (state) => {
    return {
      globalFilter: void 0,
      ...state
    };
  },
  getDefaultOptions: (table) => {
    return {
      onGlobalFilterChange: makeStateUpdater("globalFilter", table),
      globalFilterFn: "auto",
      getColumnCanGlobalFilter: (column) => {
        var _table$getCoreRowMode;
        const value = (_table$getCoreRowMode = table.getCoreRowModel().flatRows[0]) == null || (_table$getCoreRowMode = _table$getCoreRowMode._getAllCellsByColumnId()[column.id]) == null ? void 0 : _table$getCoreRowMode.getValue();
        return typeof value === "string" || typeof value === "number";
      }
    };
  },
  createColumn: (column, table) => {
    column.getCanGlobalFilter = () => {
      var _column$columnDef$ena, _table$options$enable, _table$options$enable2, _table$options$getCol;
      return ((_column$columnDef$ena = column.columnDef.enableGlobalFilter) != null ? _column$columnDef$ena : true) && ((_table$options$enable = table.options.enableGlobalFilter) != null ? _table$options$enable : true) && ((_table$options$enable2 = table.options.enableFilters) != null ? _table$options$enable2 : true) && ((_table$options$getCol = table.options.getColumnCanGlobalFilter == null ? void 0 : table.options.getColumnCanGlobalFilter(column)) != null ? _table$options$getCol : true) && !!column.accessorFn;
    };
  },
  createTable: (table) => {
    table.getGlobalAutoFilterFn = () => {
      return filterFns.includesString;
    };
    table.getGlobalFilterFn = () => {
      var _table$options$filter, _table$options$filter2;
      const {
        globalFilterFn
      } = table.options;
      return isFunction(globalFilterFn) ? globalFilterFn : globalFilterFn === "auto" ? table.getGlobalAutoFilterFn() : (_table$options$filter = (_table$options$filter2 = table.options.filterFns) == null ? void 0 : _table$options$filter2[globalFilterFn]) != null ? _table$options$filter : filterFns[globalFilterFn];
    };
    table.setGlobalFilter = (updater) => {
      table.options.onGlobalFilterChange == null || table.options.onGlobalFilterChange(updater);
    };
    table.resetGlobalFilter = (defaultState) => {
      table.setGlobalFilter(defaultState ? void 0 : table.initialState.globalFilter);
    };
  }
};
var RowExpanding = {
  getInitialState: (state) => {
    return {
      expanded: {},
      ...state
    };
  },
  getDefaultOptions: (table) => {
    return {
      onExpandedChange: makeStateUpdater("expanded", table),
      paginateExpandedRows: true
    };
  },
  createTable: (table) => {
    let registered = false;
    let queued = false;
    table._autoResetExpanded = () => {
      var _ref, _table$options$autoRe;
      if (!registered) {
        table._queue(() => {
          registered = true;
        });
        return;
      }
      if ((_ref = (_table$options$autoRe = table.options.autoResetAll) != null ? _table$options$autoRe : table.options.autoResetExpanded) != null ? _ref : !table.options.manualExpanding) {
        if (queued)
          return;
        queued = true;
        table._queue(() => {
          table.resetExpanded();
          queued = false;
        });
      }
    };
    table.setExpanded = (updater) => table.options.onExpandedChange == null ? void 0 : table.options.onExpandedChange(updater);
    table.toggleAllRowsExpanded = (expanded) => {
      if (expanded != null ? expanded : !table.getIsAllRowsExpanded()) {
        table.setExpanded(true);
      } else {
        table.setExpanded({});
      }
    };
    table.resetExpanded = (defaultState) => {
      var _table$initialState$e, _table$initialState;
      table.setExpanded(defaultState ? {} : (_table$initialState$e = (_table$initialState = table.initialState) == null ? void 0 : _table$initialState.expanded) != null ? _table$initialState$e : {});
    };
    table.getCanSomeRowsExpand = () => {
      return table.getPrePaginationRowModel().flatRows.some((row) => row.getCanExpand());
    };
    table.getToggleAllRowsExpandedHandler = () => {
      return (e3) => {
        e3.persist == null || e3.persist();
        table.toggleAllRowsExpanded();
      };
    };
    table.getIsSomeRowsExpanded = () => {
      const expanded = table.getState().expanded;
      return expanded === true || Object.values(expanded).some(Boolean);
    };
    table.getIsAllRowsExpanded = () => {
      const expanded = table.getState().expanded;
      if (typeof expanded === "boolean") {
        return expanded === true;
      }
      if (!Object.keys(expanded).length) {
        return false;
      }
      if (table.getRowModel().flatRows.some((row) => !row.getIsExpanded())) {
        return false;
      }
      return true;
    };
    table.getExpandedDepth = () => {
      let maxDepth = 0;
      const rowIds = table.getState().expanded === true ? Object.keys(table.getRowModel().rowsById) : Object.keys(table.getState().expanded);
      rowIds.forEach((id) => {
        const splitId = id.split(".");
        maxDepth = Math.max(maxDepth, splitId.length);
      });
      return maxDepth;
    };
    table.getPreExpandedRowModel = () => table.getSortedRowModel();
    table.getExpandedRowModel = () => {
      if (!table._getExpandedRowModel && table.options.getExpandedRowModel) {
        table._getExpandedRowModel = table.options.getExpandedRowModel(table);
      }
      if (table.options.manualExpanding || !table._getExpandedRowModel) {
        return table.getPreExpandedRowModel();
      }
      return table._getExpandedRowModel();
    };
  },
  createRow: (row, table) => {
    row.toggleExpanded = (expanded) => {
      table.setExpanded((old) => {
        var _expanded;
        const exists = old === true ? true : !!(old != null && old[row.id]);
        let oldExpanded = {};
        if (old === true) {
          Object.keys(table.getRowModel().rowsById).forEach((rowId) => {
            oldExpanded[rowId] = true;
          });
        } else {
          oldExpanded = old;
        }
        expanded = (_expanded = expanded) != null ? _expanded : !exists;
        if (!exists && expanded) {
          return {
            ...oldExpanded,
            [row.id]: true
          };
        }
        if (exists && !expanded) {
          const {
            [row.id]: _3,
            ...rest
          } = oldExpanded;
          return rest;
        }
        return old;
      });
    };
    row.getIsExpanded = () => {
      var _table$options$getIsR;
      const expanded = table.getState().expanded;
      return !!((_table$options$getIsR = table.options.getIsRowExpanded == null ? void 0 : table.options.getIsRowExpanded(row)) != null ? _table$options$getIsR : expanded === true || (expanded == null ? void 0 : expanded[row.id]));
    };
    row.getCanExpand = () => {
      var _table$options$getRow, _table$options$enable, _row$subRows;
      return (_table$options$getRow = table.options.getRowCanExpand == null ? void 0 : table.options.getRowCanExpand(row)) != null ? _table$options$getRow : ((_table$options$enable = table.options.enableExpanding) != null ? _table$options$enable : true) && !!((_row$subRows = row.subRows) != null && _row$subRows.length);
    };
    row.getIsAllParentsExpanded = () => {
      let isFullyExpanded = true;
      let currentRow = row;
      while (isFullyExpanded && currentRow.parentId) {
        currentRow = table.getRow(currentRow.parentId, true);
        isFullyExpanded = currentRow.getIsExpanded();
      }
      return isFullyExpanded;
    };
    row.getToggleExpandedHandler = () => {
      const canExpand = row.getCanExpand();
      return () => {
        if (!canExpand)
          return;
        row.toggleExpanded();
      };
    };
  }
};
var defaultPageIndex = 0;
var defaultPageSize = 10;
var getDefaultPaginationState = () => ({
  pageIndex: defaultPageIndex,
  pageSize: defaultPageSize
});
var RowPagination = {
  getInitialState: (state) => {
    return {
      ...state,
      pagination: {
        ...getDefaultPaginationState(),
        ...state == null ? void 0 : state.pagination
      }
    };
  },
  getDefaultOptions: (table) => {
    return {
      onPaginationChange: makeStateUpdater("pagination", table)
    };
  },
  createTable: (table) => {
    let registered = false;
    let queued = false;
    table._autoResetPageIndex = () => {
      var _ref, _table$options$autoRe;
      if (!registered) {
        table._queue(() => {
          registered = true;
        });
        return;
      }
      if ((_ref = (_table$options$autoRe = table.options.autoResetAll) != null ? _table$options$autoRe : table.options.autoResetPageIndex) != null ? _ref : !table.options.manualPagination) {
        if (queued)
          return;
        queued = true;
        table._queue(() => {
          table.resetPageIndex();
          queued = false;
        });
      }
    };
    table.setPagination = (updater) => {
      const safeUpdater = (old) => {
        let newState = functionalUpdate(updater, old);
        return newState;
      };
      return table.options.onPaginationChange == null ? void 0 : table.options.onPaginationChange(safeUpdater);
    };
    table.resetPagination = (defaultState) => {
      var _table$initialState$p;
      table.setPagination(defaultState ? getDefaultPaginationState() : (_table$initialState$p = table.initialState.pagination) != null ? _table$initialState$p : getDefaultPaginationState());
    };
    table.setPageIndex = (updater) => {
      table.setPagination((old) => {
        let pageIndex = functionalUpdate(updater, old.pageIndex);
        const maxPageIndex = typeof table.options.pageCount === "undefined" || table.options.pageCount === -1 ? Number.MAX_SAFE_INTEGER : table.options.pageCount - 1;
        pageIndex = Math.max(0, Math.min(pageIndex, maxPageIndex));
        return {
          ...old,
          pageIndex
        };
      });
    };
    table.resetPageIndex = (defaultState) => {
      var _table$initialState$p2, _table$initialState;
      table.setPageIndex(defaultState ? defaultPageIndex : (_table$initialState$p2 = (_table$initialState = table.initialState) == null || (_table$initialState = _table$initialState.pagination) == null ? void 0 : _table$initialState.pageIndex) != null ? _table$initialState$p2 : defaultPageIndex);
    };
    table.resetPageSize = (defaultState) => {
      var _table$initialState$p3, _table$initialState2;
      table.setPageSize(defaultState ? defaultPageSize : (_table$initialState$p3 = (_table$initialState2 = table.initialState) == null || (_table$initialState2 = _table$initialState2.pagination) == null ? void 0 : _table$initialState2.pageSize) != null ? _table$initialState$p3 : defaultPageSize);
    };
    table.setPageSize = (updater) => {
      table.setPagination((old) => {
        const pageSize = Math.max(1, functionalUpdate(updater, old.pageSize));
        const topRowIndex = old.pageSize * old.pageIndex;
        const pageIndex = Math.floor(topRowIndex / pageSize);
        return {
          ...old,
          pageIndex,
          pageSize
        };
      });
    };
    table.setPageCount = (updater) => table.setPagination((old) => {
      var _table$options$pageCo;
      let newPageCount = functionalUpdate(updater, (_table$options$pageCo = table.options.pageCount) != null ? _table$options$pageCo : -1);
      if (typeof newPageCount === "number") {
        newPageCount = Math.max(-1, newPageCount);
      }
      return {
        ...old,
        pageCount: newPageCount
      };
    });
    table.getPageOptions = memo(() => [table.getPageCount()], (pageCount) => {
      let pageOptions = [];
      if (pageCount && pageCount > 0) {
        pageOptions = [...new Array(pageCount)].fill(null).map((_3, i4) => i4);
      }
      return pageOptions;
    }, getMemoOptions(table.options, "debugTable", "getPageOptions"));
    table.getCanPreviousPage = () => table.getState().pagination.pageIndex > 0;
    table.getCanNextPage = () => {
      const {
        pageIndex
      } = table.getState().pagination;
      const pageCount = table.getPageCount();
      if (pageCount === -1) {
        return true;
      }
      if (pageCount === 0) {
        return false;
      }
      return pageIndex < pageCount - 1;
    };
    table.previousPage = () => {
      return table.setPageIndex((old) => old - 1);
    };
    table.nextPage = () => {
      return table.setPageIndex((old) => {
        return old + 1;
      });
    };
    table.firstPage = () => {
      return table.setPageIndex(0);
    };
    table.lastPage = () => {
      return table.setPageIndex(table.getPageCount() - 1);
    };
    table.getPrePaginationRowModel = () => table.getExpandedRowModel();
    table.getPaginationRowModel = () => {
      if (!table._getPaginationRowModel && table.options.getPaginationRowModel) {
        table._getPaginationRowModel = table.options.getPaginationRowModel(table);
      }
      if (table.options.manualPagination || !table._getPaginationRowModel) {
        return table.getPrePaginationRowModel();
      }
      return table._getPaginationRowModel();
    };
    table.getPageCount = () => {
      var _table$options$pageCo2;
      return (_table$options$pageCo2 = table.options.pageCount) != null ? _table$options$pageCo2 : Math.ceil(table.getRowCount() / table.getState().pagination.pageSize);
    };
    table.getRowCount = () => {
      var _table$options$rowCou;
      return (_table$options$rowCou = table.options.rowCount) != null ? _table$options$rowCou : table.getPrePaginationRowModel().rows.length;
    };
  }
};
var getDefaultRowPinningState = () => ({
  top: [],
  bottom: []
});
var RowPinning = {
  getInitialState: (state) => {
    return {
      rowPinning: getDefaultRowPinningState(),
      ...state
    };
  },
  getDefaultOptions: (table) => {
    return {
      onRowPinningChange: makeStateUpdater("rowPinning", table)
    };
  },
  createRow: (row, table) => {
    row.pin = (position, includeLeafRows, includeParentRows) => {
      const leafRowIds = includeLeafRows ? row.getLeafRows().map((_ref) => {
        let {
          id
        } = _ref;
        return id;
      }) : [];
      const parentRowIds = includeParentRows ? row.getParentRows().map((_ref2) => {
        let {
          id
        } = _ref2;
        return id;
      }) : [];
      const rowIds = /* @__PURE__ */ new Set([...parentRowIds, row.id, ...leafRowIds]);
      table.setRowPinning((old) => {
        var _old$top3, _old$bottom3;
        if (position === "bottom") {
          var _old$top, _old$bottom;
          return {
            top: ((_old$top = old == null ? void 0 : old.top) != null ? _old$top : []).filter((d3) => !(rowIds != null && rowIds.has(d3))),
            bottom: [...((_old$bottom = old == null ? void 0 : old.bottom) != null ? _old$bottom : []).filter((d3) => !(rowIds != null && rowIds.has(d3))), ...Array.from(rowIds)]
          };
        }
        if (position === "top") {
          var _old$top2, _old$bottom2;
          return {
            top: [...((_old$top2 = old == null ? void 0 : old.top) != null ? _old$top2 : []).filter((d3) => !(rowIds != null && rowIds.has(d3))), ...Array.from(rowIds)],
            bottom: ((_old$bottom2 = old == null ? void 0 : old.bottom) != null ? _old$bottom2 : []).filter((d3) => !(rowIds != null && rowIds.has(d3)))
          };
        }
        return {
          top: ((_old$top3 = old == null ? void 0 : old.top) != null ? _old$top3 : []).filter((d3) => !(rowIds != null && rowIds.has(d3))),
          bottom: ((_old$bottom3 = old == null ? void 0 : old.bottom) != null ? _old$bottom3 : []).filter((d3) => !(rowIds != null && rowIds.has(d3)))
        };
      });
    };
    row.getCanPin = () => {
      var _ref3;
      const {
        enableRowPinning,
        enablePinning
      } = table.options;
      if (typeof enableRowPinning === "function") {
        return enableRowPinning(row);
      }
      return (_ref3 = enableRowPinning != null ? enableRowPinning : enablePinning) != null ? _ref3 : true;
    };
    row.getIsPinned = () => {
      const rowIds = [row.id];
      const {
        top,
        bottom
      } = table.getState().rowPinning;
      const isTop = rowIds.some((d3) => top == null ? void 0 : top.includes(d3));
      const isBottom = rowIds.some((d3) => bottom == null ? void 0 : bottom.includes(d3));
      return isTop ? "top" : isBottom ? "bottom" : false;
    };
    row.getPinnedIndex = () => {
      var _ref4, _visiblePinnedRowIds$;
      const position = row.getIsPinned();
      if (!position)
        return -1;
      const visiblePinnedRowIds = (_ref4 = position === "top" ? table.getTopRows() : table.getBottomRows()) == null ? void 0 : _ref4.map((_ref5) => {
        let {
          id
        } = _ref5;
        return id;
      });
      return (_visiblePinnedRowIds$ = visiblePinnedRowIds == null ? void 0 : visiblePinnedRowIds.indexOf(row.id)) != null ? _visiblePinnedRowIds$ : -1;
    };
  },
  createTable: (table) => {
    table.setRowPinning = (updater) => table.options.onRowPinningChange == null ? void 0 : table.options.onRowPinningChange(updater);
    table.resetRowPinning = (defaultState) => {
      var _table$initialState$r, _table$initialState;
      return table.setRowPinning(defaultState ? getDefaultRowPinningState() : (_table$initialState$r = (_table$initialState = table.initialState) == null ? void 0 : _table$initialState.rowPinning) != null ? _table$initialState$r : getDefaultRowPinningState());
    };
    table.getIsSomeRowsPinned = (position) => {
      var _pinningState$positio;
      const pinningState = table.getState().rowPinning;
      if (!position) {
        var _pinningState$top, _pinningState$bottom;
        return Boolean(((_pinningState$top = pinningState.top) == null ? void 0 : _pinningState$top.length) || ((_pinningState$bottom = pinningState.bottom) == null ? void 0 : _pinningState$bottom.length));
      }
      return Boolean((_pinningState$positio = pinningState[position]) == null ? void 0 : _pinningState$positio.length);
    };
    table._getPinnedRows = (visibleRows, pinnedRowIds, position) => {
      var _table$options$keepPi;
      const rows = ((_table$options$keepPi = table.options.keepPinnedRows) != null ? _table$options$keepPi : true) ? (
        //get all rows that are pinned even if they would not be otherwise visible
        //account for expanded parent rows, but not pagination or filtering
        (pinnedRowIds != null ? pinnedRowIds : []).map((rowId) => {
          const row = table.getRow(rowId, true);
          return row.getIsAllParentsExpanded() ? row : null;
        })
      ) : (
        //else get only visible rows that are pinned
        (pinnedRowIds != null ? pinnedRowIds : []).map((rowId) => visibleRows.find((row) => row.id === rowId))
      );
      return rows.filter(Boolean).map((d3) => ({
        ...d3,
        position
      }));
    };
    table.getTopRows = memo(() => [table.getRowModel().rows, table.getState().rowPinning.top], (allRows, topPinnedRowIds) => table._getPinnedRows(allRows, topPinnedRowIds, "top"), getMemoOptions(table.options, "debugRows", "getTopRows"));
    table.getBottomRows = memo(() => [table.getRowModel().rows, table.getState().rowPinning.bottom], (allRows, bottomPinnedRowIds) => table._getPinnedRows(allRows, bottomPinnedRowIds, "bottom"), getMemoOptions(table.options, "debugRows", "getBottomRows"));
    table.getCenterRows = memo(() => [table.getRowModel().rows, table.getState().rowPinning.top, table.getState().rowPinning.bottom], (allRows, top, bottom) => {
      const topAndBottom = /* @__PURE__ */ new Set([...top != null ? top : [], ...bottom != null ? bottom : []]);
      return allRows.filter((d3) => !topAndBottom.has(d3.id));
    }, getMemoOptions(table.options, "debugRows", "getCenterRows"));
  }
};
var RowSelection = {
  getInitialState: (state) => {
    return {
      rowSelection: {},
      ...state
    };
  },
  getDefaultOptions: (table) => {
    return {
      onRowSelectionChange: makeStateUpdater("rowSelection", table),
      enableRowSelection: true,
      enableMultiRowSelection: true,
      enableSubRowSelection: true
      // enableGroupingRowSelection: false,
      // isAdditiveSelectEvent: (e: unknown) => !!e.metaKey,
      // isInclusiveSelectEvent: (e: unknown) => !!e.shiftKey,
    };
  },
  createTable: (table) => {
    table.setRowSelection = (updater) => table.options.onRowSelectionChange == null ? void 0 : table.options.onRowSelectionChange(updater);
    table.resetRowSelection = (defaultState) => {
      var _table$initialState$r;
      return table.setRowSelection(defaultState ? {} : (_table$initialState$r = table.initialState.rowSelection) != null ? _table$initialState$r : {});
    };
    table.toggleAllRowsSelected = (value) => {
      table.setRowSelection((old) => {
        value = typeof value !== "undefined" ? value : !table.getIsAllRowsSelected();
        const rowSelection = {
          ...old
        };
        const preGroupedFlatRows = table.getPreGroupedRowModel().flatRows;
        if (value) {
          preGroupedFlatRows.forEach((row) => {
            if (!row.getCanSelect()) {
              return;
            }
            rowSelection[row.id] = true;
          });
        } else {
          preGroupedFlatRows.forEach((row) => {
            delete rowSelection[row.id];
          });
        }
        return rowSelection;
      });
    };
    table.toggleAllPageRowsSelected = (value) => table.setRowSelection((old) => {
      const resolvedValue = typeof value !== "undefined" ? value : !table.getIsAllPageRowsSelected();
      const rowSelection = {
        ...old
      };
      table.getRowModel().rows.forEach((row) => {
        mutateRowIsSelected(rowSelection, row.id, resolvedValue, true, table);
      });
      return rowSelection;
    });
    table.getPreSelectedRowModel = () => table.getCoreRowModel();
    table.getSelectedRowModel = memo(() => [table.getState().rowSelection, table.getCoreRowModel()], (rowSelection, rowModel) => {
      if (!Object.keys(rowSelection).length) {
        return {
          rows: [],
          flatRows: [],
          rowsById: {}
        };
      }
      return selectRowsFn(table, rowModel);
    }, getMemoOptions(table.options, "debugTable", "getSelectedRowModel"));
    table.getFilteredSelectedRowModel = memo(() => [table.getState().rowSelection, table.getFilteredRowModel()], (rowSelection, rowModel) => {
      if (!Object.keys(rowSelection).length) {
        return {
          rows: [],
          flatRows: [],
          rowsById: {}
        };
      }
      return selectRowsFn(table, rowModel);
    }, getMemoOptions(table.options, "debugTable", "getFilteredSelectedRowModel"));
    table.getGroupedSelectedRowModel = memo(() => [table.getState().rowSelection, table.getSortedRowModel()], (rowSelection, rowModel) => {
      if (!Object.keys(rowSelection).length) {
        return {
          rows: [],
          flatRows: [],
          rowsById: {}
        };
      }
      return selectRowsFn(table, rowModel);
    }, getMemoOptions(table.options, "debugTable", "getGroupedSelectedRowModel"));
    table.getIsAllRowsSelected = () => {
      const preGroupedFlatRows = table.getFilteredRowModel().flatRows;
      const {
        rowSelection
      } = table.getState();
      let isAllRowsSelected = Boolean(preGroupedFlatRows.length && Object.keys(rowSelection).length);
      if (isAllRowsSelected) {
        if (preGroupedFlatRows.some((row) => row.getCanSelect() && !rowSelection[row.id])) {
          isAllRowsSelected = false;
        }
      }
      return isAllRowsSelected;
    };
    table.getIsAllPageRowsSelected = () => {
      const paginationFlatRows = table.getPaginationRowModel().flatRows.filter((row) => row.getCanSelect());
      const {
        rowSelection
      } = table.getState();
      let isAllPageRowsSelected = !!paginationFlatRows.length;
      if (isAllPageRowsSelected && paginationFlatRows.some((row) => !rowSelection[row.id])) {
        isAllPageRowsSelected = false;
      }
      return isAllPageRowsSelected;
    };
    table.getIsSomeRowsSelected = () => {
      var _table$getState$rowSe;
      const totalSelected = Object.keys((_table$getState$rowSe = table.getState().rowSelection) != null ? _table$getState$rowSe : {}).length;
      return totalSelected > 0 && totalSelected < table.getFilteredRowModel().flatRows.length;
    };
    table.getIsSomePageRowsSelected = () => {
      const paginationFlatRows = table.getPaginationRowModel().flatRows;
      return table.getIsAllPageRowsSelected() ? false : paginationFlatRows.filter((row) => row.getCanSelect()).some((d3) => d3.getIsSelected() || d3.getIsSomeSelected());
    };
    table.getToggleAllRowsSelectedHandler = () => {
      return (e3) => {
        table.toggleAllRowsSelected(e3.target.checked);
      };
    };
    table.getToggleAllPageRowsSelectedHandler = () => {
      return (e3) => {
        table.toggleAllPageRowsSelected(e3.target.checked);
      };
    };
  },
  createRow: (row, table) => {
    row.toggleSelected = (value, opts) => {
      const isSelected = row.getIsSelected();
      table.setRowSelection((old) => {
        var _opts$selectChildren;
        value = typeof value !== "undefined" ? value : !isSelected;
        if (row.getCanSelect() && isSelected === value) {
          return old;
        }
        const selectedRowIds = {
          ...old
        };
        mutateRowIsSelected(selectedRowIds, row.id, value, (_opts$selectChildren = opts == null ? void 0 : opts.selectChildren) != null ? _opts$selectChildren : true, table);
        return selectedRowIds;
      });
    };
    row.getIsSelected = () => {
      const {
        rowSelection
      } = table.getState();
      return isRowSelected(row, rowSelection);
    };
    row.getIsSomeSelected = () => {
      const {
        rowSelection
      } = table.getState();
      return isSubRowSelected(row, rowSelection) === "some";
    };
    row.getIsAllSubRowsSelected = () => {
      const {
        rowSelection
      } = table.getState();
      return isSubRowSelected(row, rowSelection) === "all";
    };
    row.getCanSelect = () => {
      var _table$options$enable;
      if (typeof table.options.enableRowSelection === "function") {
        return table.options.enableRowSelection(row);
      }
      return (_table$options$enable = table.options.enableRowSelection) != null ? _table$options$enable : true;
    };
    row.getCanSelectSubRows = () => {
      var _table$options$enable2;
      if (typeof table.options.enableSubRowSelection === "function") {
        return table.options.enableSubRowSelection(row);
      }
      return (_table$options$enable2 = table.options.enableSubRowSelection) != null ? _table$options$enable2 : true;
    };
    row.getCanMultiSelect = () => {
      var _table$options$enable3;
      if (typeof table.options.enableMultiRowSelection === "function") {
        return table.options.enableMultiRowSelection(row);
      }
      return (_table$options$enable3 = table.options.enableMultiRowSelection) != null ? _table$options$enable3 : true;
    };
    row.getToggleSelectedHandler = () => {
      const canSelect = row.getCanSelect();
      return (e3) => {
        var _target;
        if (!canSelect)
          return;
        row.toggleSelected((_target = e3.target) == null ? void 0 : _target.checked);
      };
    };
  }
};
var mutateRowIsSelected = (selectedRowIds, id, value, includeChildren, table) => {
  var _row$subRows;
  const row = table.getRow(id, true);
  if (value) {
    if (!row.getCanMultiSelect()) {
      Object.keys(selectedRowIds).forEach((key) => delete selectedRowIds[key]);
    }
    if (row.getCanSelect()) {
      selectedRowIds[id] = true;
    }
  } else {
    delete selectedRowIds[id];
  }
  if (includeChildren && (_row$subRows = row.subRows) != null && _row$subRows.length && row.getCanSelectSubRows()) {
    row.subRows.forEach((row2) => mutateRowIsSelected(selectedRowIds, row2.id, value, includeChildren, table));
  }
};
function selectRowsFn(table, rowModel) {
  const rowSelection = table.getState().rowSelection;
  const newSelectedFlatRows = [];
  const newSelectedRowsById = {};
  const recurseRows = function(rows, depth) {
    return rows.map((row) => {
      var _row$subRows2;
      const isSelected = isRowSelected(row, rowSelection);
      if (isSelected) {
        newSelectedFlatRows.push(row);
        newSelectedRowsById[row.id] = row;
      }
      if ((_row$subRows2 = row.subRows) != null && _row$subRows2.length) {
        row = {
          ...row,
          subRows: recurseRows(row.subRows)
        };
      }
      if (isSelected) {
        return row;
      }
    }).filter(Boolean);
  };
  return {
    rows: recurseRows(rowModel.rows),
    flatRows: newSelectedFlatRows,
    rowsById: newSelectedRowsById
  };
}
function isRowSelected(row, selection) {
  var _selection$row$id;
  return (_selection$row$id = selection[row.id]) != null ? _selection$row$id : false;
}
function isSubRowSelected(row, selection, table) {
  var _row$subRows3;
  if (!((_row$subRows3 = row.subRows) != null && _row$subRows3.length))
    return false;
  let allChildrenSelected = true;
  let someSelected = false;
  row.subRows.forEach((subRow) => {
    if (someSelected && !allChildrenSelected) {
      return;
    }
    if (subRow.getCanSelect()) {
      if (isRowSelected(subRow, selection)) {
        someSelected = true;
      } else {
        allChildrenSelected = false;
      }
    }
    if (subRow.subRows && subRow.subRows.length) {
      const subRowChildrenSelected = isSubRowSelected(subRow, selection);
      if (subRowChildrenSelected === "all") {
        someSelected = true;
      } else if (subRowChildrenSelected === "some") {
        someSelected = true;
        allChildrenSelected = false;
      } else {
        allChildrenSelected = false;
      }
    }
  });
  return allChildrenSelected ? "all" : someSelected ? "some" : false;
}
var reSplitAlphaNumeric = /([0-9]+)/gm;
var alphanumeric = (rowA, rowB, columnId) => {
  return compareAlphanumeric(toString(rowA.getValue(columnId)).toLowerCase(), toString(rowB.getValue(columnId)).toLowerCase());
};
var alphanumericCaseSensitive = (rowA, rowB, columnId) => {
  return compareAlphanumeric(toString(rowA.getValue(columnId)), toString(rowB.getValue(columnId)));
};
var text = (rowA, rowB, columnId) => {
  return compareBasic(toString(rowA.getValue(columnId)).toLowerCase(), toString(rowB.getValue(columnId)).toLowerCase());
};
var textCaseSensitive = (rowA, rowB, columnId) => {
  return compareBasic(toString(rowA.getValue(columnId)), toString(rowB.getValue(columnId)));
};
var datetime = (rowA, rowB, columnId) => {
  const a3 = rowA.getValue(columnId);
  const b2 = rowB.getValue(columnId);
  return a3 > b2 ? 1 : a3 < b2 ? -1 : 0;
};
var basic = (rowA, rowB, columnId) => {
  return compareBasic(rowA.getValue(columnId), rowB.getValue(columnId));
};
function compareBasic(a3, b2) {
  return a3 === b2 ? 0 : a3 > b2 ? 1 : -1;
}
function toString(a3) {
  if (typeof a3 === "number") {
    if (isNaN(a3) || a3 === Infinity || a3 === -Infinity) {
      return "";
    }
    return String(a3);
  }
  if (typeof a3 === "string") {
    return a3;
  }
  return "";
}
function compareAlphanumeric(aStr, bStr) {
  const a3 = aStr.split(reSplitAlphaNumeric).filter(Boolean);
  const b2 = bStr.split(reSplitAlphaNumeric).filter(Boolean);
  while (a3.length && b2.length) {
    const aa = a3.shift();
    const bb = b2.shift();
    const an2 = parseInt(aa, 10);
    const bn2 = parseInt(bb, 10);
    const combo = [an2, bn2].sort();
    if (isNaN(combo[0])) {
      if (aa > bb) {
        return 1;
      }
      if (bb > aa) {
        return -1;
      }
      continue;
    }
    if (isNaN(combo[1])) {
      return isNaN(an2) ? -1 : 1;
    }
    if (an2 > bn2) {
      return 1;
    }
    if (bn2 > an2) {
      return -1;
    }
  }
  return a3.length - b2.length;
}
var sortingFns = {
  alphanumeric,
  alphanumericCaseSensitive,
  text,
  textCaseSensitive,
  datetime,
  basic
};
var RowSorting = {
  getInitialState: (state) => {
    return {
      sorting: [],
      ...state
    };
  },
  getDefaultColumnDef: () => {
    return {
      sortingFn: "auto",
      sortUndefined: 1
    };
  },
  getDefaultOptions: (table) => {
    return {
      onSortingChange: makeStateUpdater("sorting", table),
      isMultiSortEvent: (e3) => {
        return e3.shiftKey;
      }
    };
  },
  createColumn: (column, table) => {
    column.getAutoSortingFn = () => {
      const firstRows = table.getFilteredRowModel().flatRows.slice(10);
      let isString = false;
      for (const row of firstRows) {
        const value = row == null ? void 0 : row.getValue(column.id);
        if (Object.prototype.toString.call(value) === "[object Date]") {
          return sortingFns.datetime;
        }
        if (typeof value === "string") {
          isString = true;
          if (value.split(reSplitAlphaNumeric).length > 1) {
            return sortingFns.alphanumeric;
          }
        }
      }
      if (isString) {
        return sortingFns.text;
      }
      return sortingFns.basic;
    };
    column.getAutoSortDir = () => {
      const firstRow = table.getFilteredRowModel().flatRows[0];
      const value = firstRow == null ? void 0 : firstRow.getValue(column.id);
      if (typeof value === "string") {
        return "asc";
      }
      return "desc";
    };
    column.getSortingFn = () => {
      var _table$options$sortin, _table$options$sortin2;
      if (!column) {
        throw new Error();
      }
      return isFunction(column.columnDef.sortingFn) ? column.columnDef.sortingFn : column.columnDef.sortingFn === "auto" ? column.getAutoSortingFn() : (_table$options$sortin = (_table$options$sortin2 = table.options.sortingFns) == null ? void 0 : _table$options$sortin2[column.columnDef.sortingFn]) != null ? _table$options$sortin : sortingFns[column.columnDef.sortingFn];
    };
    column.toggleSorting = (desc, multi) => {
      const nextSortingOrder = column.getNextSortingOrder();
      const hasManualValue = typeof desc !== "undefined" && desc !== null;
      table.setSorting((old) => {
        const existingSorting = old == null ? void 0 : old.find((d3) => d3.id === column.id);
        const existingIndex = old == null ? void 0 : old.findIndex((d3) => d3.id === column.id);
        let newSorting = [];
        let sortAction;
        let nextDesc = hasManualValue ? desc : nextSortingOrder === "desc";
        if (old != null && old.length && column.getCanMultiSort() && multi) {
          if (existingSorting) {
            sortAction = "toggle";
          } else {
            sortAction = "add";
          }
        } else {
          if (old != null && old.length && existingIndex !== old.length - 1) {
            sortAction = "replace";
          } else if (existingSorting) {
            sortAction = "toggle";
          } else {
            sortAction = "replace";
          }
        }
        if (sortAction === "toggle") {
          if (!hasManualValue) {
            if (!nextSortingOrder) {
              sortAction = "remove";
            }
          }
        }
        if (sortAction === "add") {
          var _table$options$maxMul;
          newSorting = [...old, {
            id: column.id,
            desc: nextDesc
          }];
          newSorting.splice(0, newSorting.length - ((_table$options$maxMul = table.options.maxMultiSortColCount) != null ? _table$options$maxMul : Number.MAX_SAFE_INTEGER));
        } else if (sortAction === "toggle") {
          newSorting = old.map((d3) => {
            if (d3.id === column.id) {
              return {
                ...d3,
                desc: nextDesc
              };
            }
            return d3;
          });
        } else if (sortAction === "remove") {
          newSorting = old.filter((d3) => d3.id !== column.id);
        } else {
          newSorting = [{
            id: column.id,
            desc: nextDesc
          }];
        }
        return newSorting;
      });
    };
    column.getFirstSortDir = () => {
      var _ref, _column$columnDef$sor;
      const sortDescFirst = (_ref = (_column$columnDef$sor = column.columnDef.sortDescFirst) != null ? _column$columnDef$sor : table.options.sortDescFirst) != null ? _ref : column.getAutoSortDir() === "desc";
      return sortDescFirst ? "desc" : "asc";
    };
    column.getNextSortingOrder = (multi) => {
      var _table$options$enable, _table$options$enable2;
      const firstSortDirection = column.getFirstSortDir();
      const isSorted = column.getIsSorted();
      if (!isSorted) {
        return firstSortDirection;
      }
      if (isSorted !== firstSortDirection && ((_table$options$enable = table.options.enableSortingRemoval) != null ? _table$options$enable : true) && // If enableSortRemove, enable in general
      (multi ? (_table$options$enable2 = table.options.enableMultiRemove) != null ? _table$options$enable2 : true : true)) {
        return false;
      }
      return isSorted === "desc" ? "asc" : "desc";
    };
    column.getCanSort = () => {
      var _column$columnDef$ena, _table$options$enable3;
      return ((_column$columnDef$ena = column.columnDef.enableSorting) != null ? _column$columnDef$ena : true) && ((_table$options$enable3 = table.options.enableSorting) != null ? _table$options$enable3 : true) && !!column.accessorFn;
    };
    column.getCanMultiSort = () => {
      var _ref2, _column$columnDef$ena2;
      return (_ref2 = (_column$columnDef$ena2 = column.columnDef.enableMultiSort) != null ? _column$columnDef$ena2 : table.options.enableMultiSort) != null ? _ref2 : !!column.accessorFn;
    };
    column.getIsSorted = () => {
      var _table$getState$sorti;
      const columnSort = (_table$getState$sorti = table.getState().sorting) == null ? void 0 : _table$getState$sorti.find((d3) => d3.id === column.id);
      return !columnSort ? false : columnSort.desc ? "desc" : "asc";
    };
    column.getSortIndex = () => {
      var _table$getState$sorti2, _table$getState$sorti3;
      return (_table$getState$sorti2 = (_table$getState$sorti3 = table.getState().sorting) == null ? void 0 : _table$getState$sorti3.findIndex((d3) => d3.id === column.id)) != null ? _table$getState$sorti2 : -1;
    };
    column.clearSorting = () => {
      table.setSorting((old) => old != null && old.length ? old.filter((d3) => d3.id !== column.id) : []);
    };
    column.getToggleSortingHandler = () => {
      const canSort = column.getCanSort();
      return (e3) => {
        if (!canSort)
          return;
        e3.persist == null || e3.persist();
        column.toggleSorting == null || column.toggleSorting(void 0, column.getCanMultiSort() ? table.options.isMultiSortEvent == null ? void 0 : table.options.isMultiSortEvent(e3) : false);
      };
    };
  },
  createTable: (table) => {
    table.setSorting = (updater) => table.options.onSortingChange == null ? void 0 : table.options.onSortingChange(updater);
    table.resetSorting = (defaultState) => {
      var _table$initialState$s, _table$initialState;
      table.setSorting(defaultState ? [] : (_table$initialState$s = (_table$initialState = table.initialState) == null ? void 0 : _table$initialState.sorting) != null ? _table$initialState$s : []);
    };
    table.getPreSortedRowModel = () => table.getGroupedRowModel();
    table.getSortedRowModel = () => {
      if (!table._getSortedRowModel && table.options.getSortedRowModel) {
        table._getSortedRowModel = table.options.getSortedRowModel(table);
      }
      if (table.options.manualSorting || !table._getSortedRowModel) {
        return table.getPreSortedRowModel();
      }
      return table._getSortedRowModel();
    };
  }
};
var builtInFeatures = [
  Headers,
  ColumnVisibility,
  ColumnOrdering,
  ColumnPinning,
  ColumnFaceting,
  ColumnFiltering,
  GlobalFaceting,
  //depends on ColumnFaceting
  GlobalFiltering,
  //depends on ColumnFiltering
  RowSorting,
  ColumnGrouping,
  //depends on RowSorting
  RowExpanding,
  RowPagination,
  RowPinning,
  RowSelection,
  ColumnSizing
];
function createTable(options) {
  var _options$_features, _options$initialState;
  if (options.debugAll || options.debugTable) {
    console.info("Creating Table Instance...");
  }
  const _features = [...builtInFeatures, ...(_options$_features = options._features) != null ? _options$_features : []];
  let table = {
    _features
  };
  const defaultOptions = table._features.reduce((obj, feature) => {
    return Object.assign(obj, feature.getDefaultOptions == null ? void 0 : feature.getDefaultOptions(table));
  }, {});
  const mergeOptions = (options2) => {
    if (table.options.mergeOptions) {
      return table.options.mergeOptions(defaultOptions, options2);
    }
    return {
      ...defaultOptions,
      ...options2
    };
  };
  const coreInitialState = {};
  let initialState = {
    ...coreInitialState,
    ...(_options$initialState = options.initialState) != null ? _options$initialState : {}
  };
  table._features.forEach((feature) => {
    var _feature$getInitialSt;
    initialState = (_feature$getInitialSt = feature.getInitialState == null ? void 0 : feature.getInitialState(initialState)) != null ? _feature$getInitialSt : initialState;
  });
  const queued = [];
  let queuedTimeout = false;
  const coreInstance = {
    _features,
    options: {
      ...defaultOptions,
      ...options
    },
    initialState,
    _queue: (cb) => {
      queued.push(cb);
      if (!queuedTimeout) {
        queuedTimeout = true;
        Promise.resolve().then(() => {
          while (queued.length) {
            queued.shift()();
          }
          queuedTimeout = false;
        }).catch((error) => setTimeout(() => {
          throw error;
        }));
      }
    },
    reset: () => {
      table.setState(table.initialState);
    },
    setOptions: (updater) => {
      const newOptions = functionalUpdate(updater, table.options);
      table.options = mergeOptions(newOptions);
    },
    getState: () => {
      return table.options.state;
    },
    setState: (updater) => {
      table.options.onStateChange == null || table.options.onStateChange(updater);
    },
    _getRowId: (row, index, parent) => {
      var _table$options$getRow;
      return (_table$options$getRow = table.options.getRowId == null ? void 0 : table.options.getRowId(row, index, parent)) != null ? _table$options$getRow : `${parent ? [parent.id, index].join(".") : index}`;
    },
    getCoreRowModel: () => {
      if (!table._getCoreRowModel) {
        table._getCoreRowModel = table.options.getCoreRowModel(table);
      }
      return table._getCoreRowModel();
    },
    // The final calls start at the bottom of the model,
    // expanded rows, which then work their way up
    getRowModel: () => {
      return table.getPaginationRowModel();
    },
    //in next version, we should just pass in the row model as the optional 2nd arg
    getRow: (id, searchAll) => {
      let row = (searchAll ? table.getPrePaginationRowModel() : table.getRowModel()).rowsById[id];
      if (!row) {
        row = table.getCoreRowModel().rowsById[id];
        if (!row) {
          if (true) {
            throw new Error(`getRow could not find row with ID: ${id}`);
          }
          throw new Error();
        }
      }
      return row;
    },
    _getDefaultColumnDef: memo(() => [table.options.defaultColumn], (defaultColumn) => {
      var _defaultColumn;
      defaultColumn = (_defaultColumn = defaultColumn) != null ? _defaultColumn : {};
      return {
        header: (props) => {
          const resolvedColumnDef = props.header.column.columnDef;
          if (resolvedColumnDef.accessorKey) {
            return resolvedColumnDef.accessorKey;
          }
          if (resolvedColumnDef.accessorFn) {
            return resolvedColumnDef.id;
          }
          return null;
        },
        // footer: props => props.header.column.id,
        cell: (props) => {
          var _props$renderValue$to, _props$renderValue;
          return (_props$renderValue$to = (_props$renderValue = props.renderValue()) == null || _props$renderValue.toString == null ? void 0 : _props$renderValue.toString()) != null ? _props$renderValue$to : null;
        },
        ...table._features.reduce((obj, feature) => {
          return Object.assign(obj, feature.getDefaultColumnDef == null ? void 0 : feature.getDefaultColumnDef());
        }, {}),
        ...defaultColumn
      };
    }, getMemoOptions(options, "debugColumns", "_getDefaultColumnDef")),
    _getColumnDefs: () => table.options.columns,
    getAllColumns: memo(() => [table._getColumnDefs()], (columnDefs) => {
      const recurseColumns = function(columnDefs2, parent, depth) {
        if (depth === void 0) {
          depth = 0;
        }
        return columnDefs2.map((columnDef) => {
          const column = createColumn(table, columnDef, depth, parent);
          const groupingColumnDef = columnDef;
          column.columns = groupingColumnDef.columns ? recurseColumns(groupingColumnDef.columns, column, depth + 1) : [];
          return column;
        });
      };
      return recurseColumns(columnDefs);
    }, getMemoOptions(options, "debugColumns", "getAllColumns")),
    getAllFlatColumns: memo(() => [table.getAllColumns()], (allColumns) => {
      return allColumns.flatMap((column) => {
        return column.getFlatColumns();
      });
    }, getMemoOptions(options, "debugColumns", "getAllFlatColumns")),
    _getAllFlatColumnsById: memo(() => [table.getAllFlatColumns()], (flatColumns) => {
      return flatColumns.reduce((acc, column) => {
        acc[column.id] = column;
        return acc;
      }, {});
    }, getMemoOptions(options, "debugColumns", "getAllFlatColumnsById")),
    getAllLeafColumns: memo(() => [table.getAllColumns(), table._getOrderColumnsFn()], (allColumns, orderColumns2) => {
      let leafColumns = allColumns.flatMap((column) => column.getLeafColumns());
      return orderColumns2(leafColumns);
    }, getMemoOptions(options, "debugColumns", "getAllLeafColumns")),
    getColumn: (columnId) => {
      const column = table._getAllFlatColumnsById()[columnId];
      if (!column) {
        console.error(`[Table] Column with id '${columnId}' does not exist.`);
      }
      return column;
    }
  };
  Object.assign(table, coreInstance);
  for (let index = 0; index < table._features.length; index++) {
    const feature = table._features[index];
    feature == null || feature.createTable == null || feature.createTable(table);
  }
  return table;
}
function getCoreRowModel() {
  return (table) => memo(() => [table.options.data], (data) => {
    const rowModel = {
      rows: [],
      flatRows: [],
      rowsById: {}
    };
    const accessRows = function(originalRows, depth, parentRow) {
      if (depth === void 0) {
        depth = 0;
      }
      const rows = [];
      for (let i4 = 0; i4 < originalRows.length; i4++) {
        const row = createRow(table, table._getRowId(originalRows[i4], i4, parentRow), originalRows[i4], i4, depth, void 0, parentRow == null ? void 0 : parentRow.id);
        rowModel.flatRows.push(row);
        rowModel.rowsById[row.id] = row;
        rows.push(row);
        if (table.options.getSubRows) {
          var _row$originalSubRows;
          row.originalSubRows = table.options.getSubRows(originalRows[i4], i4);
          if ((_row$originalSubRows = row.originalSubRows) != null && _row$originalSubRows.length) {
            row.subRows = accessRows(row.originalSubRows, depth + 1, row);
          }
        }
      }
      return rows;
    };
    rowModel.rows = accessRows(data);
    return rowModel;
  }, getMemoOptions(table.options, "debugTable", "getRowModel", () => table._autoResetPageIndex()));
}
function getFacetedMinMaxValues() {
  return (table, columnId) => memo(() => {
    var _table$getColumn;
    return [(_table$getColumn = table.getColumn(columnId)) == null ? void 0 : _table$getColumn.getFacetedRowModel()];
  }, (facetedRowModel) => {
    var _facetedRowModel$flat;
    if (!facetedRowModel)
      return void 0;
    const firstValue = (_facetedRowModel$flat = facetedRowModel.flatRows[0]) == null ? void 0 : _facetedRowModel$flat.getUniqueValues(columnId);
    if (typeof firstValue === "undefined") {
      return void 0;
    }
    let facetedMinMaxValues = [firstValue, firstValue];
    for (let i4 = 0; i4 < facetedRowModel.flatRows.length; i4++) {
      const values = facetedRowModel.flatRows[i4].getUniqueValues(columnId);
      for (let j4 = 0; j4 < values.length; j4++) {
        const value = values[j4];
        if (value < facetedMinMaxValues[0]) {
          facetedMinMaxValues[0] = value;
        } else if (value > facetedMinMaxValues[1]) {
          facetedMinMaxValues[1] = value;
        }
      }
    }
    return facetedMinMaxValues;
  }, getMemoOptions(table.options, "debugTable", "getFacetedMinMaxValues"));
}
function filterRows(rows, filterRowImpl, table) {
  if (table.options.filterFromLeafRows) {
    return filterRowModelFromLeafs(rows, filterRowImpl, table);
  }
  return filterRowModelFromRoot(rows, filterRowImpl, table);
}
function filterRowModelFromLeafs(rowsToFilter, filterRow, table) {
  var _table$options$maxLea;
  const newFilteredFlatRows = [];
  const newFilteredRowsById = {};
  const maxDepth = (_table$options$maxLea = table.options.maxLeafRowFilterDepth) != null ? _table$options$maxLea : 100;
  const recurseFilterRows = function(rowsToFilter2, depth) {
    if (depth === void 0) {
      depth = 0;
    }
    const rows = [];
    for (let i4 = 0; i4 < rowsToFilter2.length; i4++) {
      var _row$subRows;
      let row = rowsToFilter2[i4];
      const newRow = createRow(table, row.id, row.original, row.index, row.depth, void 0, row.parentId);
      newRow.columnFilters = row.columnFilters;
      if ((_row$subRows = row.subRows) != null && _row$subRows.length && depth < maxDepth) {
        newRow.subRows = recurseFilterRows(row.subRows, depth + 1);
        row = newRow;
        if (filterRow(row) && !newRow.subRows.length) {
          rows.push(row);
          newFilteredRowsById[row.id] = row;
          newFilteredFlatRows.push(row);
          continue;
        }
        if (filterRow(row) || newRow.subRows.length) {
          rows.push(row);
          newFilteredRowsById[row.id] = row;
          newFilteredFlatRows.push(row);
          continue;
        }
      } else {
        row = newRow;
        if (filterRow(row)) {
          rows.push(row);
          newFilteredRowsById[row.id] = row;
          newFilteredFlatRows.push(row);
        }
      }
    }
    return rows;
  };
  return {
    rows: recurseFilterRows(rowsToFilter),
    flatRows: newFilteredFlatRows,
    rowsById: newFilteredRowsById
  };
}
function filterRowModelFromRoot(rowsToFilter, filterRow, table) {
  var _table$options$maxLea2;
  const newFilteredFlatRows = [];
  const newFilteredRowsById = {};
  const maxDepth = (_table$options$maxLea2 = table.options.maxLeafRowFilterDepth) != null ? _table$options$maxLea2 : 100;
  const recurseFilterRows = function(rowsToFilter2, depth) {
    if (depth === void 0) {
      depth = 0;
    }
    const rows = [];
    for (let i4 = 0; i4 < rowsToFilter2.length; i4++) {
      let row = rowsToFilter2[i4];
      const pass = filterRow(row);
      if (pass) {
        var _row$subRows2;
        if ((_row$subRows2 = row.subRows) != null && _row$subRows2.length && depth < maxDepth) {
          const newRow = createRow(table, row.id, row.original, row.index, row.depth, void 0, row.parentId);
          newRow.subRows = recurseFilterRows(row.subRows, depth + 1);
          row = newRow;
        }
        rows.push(row);
        newFilteredFlatRows.push(row);
        newFilteredRowsById[row.id] = row;
      }
    }
    return rows;
  };
  return {
    rows: recurseFilterRows(rowsToFilter),
    flatRows: newFilteredFlatRows,
    rowsById: newFilteredRowsById
  };
}
function getFacetedRowModel() {
  return (table, columnId) => memo(() => [table.getPreFilteredRowModel(), table.getState().columnFilters, table.getState().globalFilter, table.getFilteredRowModel()], (preRowModel, columnFilters, globalFilter) => {
    if (!preRowModel.rows.length || !(columnFilters != null && columnFilters.length) && !globalFilter) {
      return preRowModel;
    }
    const filterableIds = [...columnFilters.map((d3) => d3.id).filter((d3) => d3 !== columnId), globalFilter ? "__global__" : void 0].filter(Boolean);
    const filterRowsImpl = (row) => {
      for (let i4 = 0; i4 < filterableIds.length; i4++) {
        if (row.columnFilters[filterableIds[i4]] === false) {
          return false;
        }
      }
      return true;
    };
    return filterRows(preRowModel.rows, filterRowsImpl, table);
  }, getMemoOptions(table.options, "debugTable", "getFacetedRowModel"));
}
function getFacetedUniqueValues() {
  return (table, columnId) => memo(() => {
    var _table$getColumn;
    return [(_table$getColumn = table.getColumn(columnId)) == null ? void 0 : _table$getColumn.getFacetedRowModel()];
  }, (facetedRowModel) => {
    if (!facetedRowModel)
      return /* @__PURE__ */ new Map();
    let facetedUniqueValues = /* @__PURE__ */ new Map();
    for (let i4 = 0; i4 < facetedRowModel.flatRows.length; i4++) {
      const values = facetedRowModel.flatRows[i4].getUniqueValues(columnId);
      for (let j4 = 0; j4 < values.length; j4++) {
        const value = values[j4];
        if (facetedUniqueValues.has(value)) {
          var _facetedUniqueValues$;
          facetedUniqueValues.set(value, ((_facetedUniqueValues$ = facetedUniqueValues.get(value)) != null ? _facetedUniqueValues$ : 0) + 1);
        } else {
          facetedUniqueValues.set(value, 1);
        }
      }
    }
    return facetedUniqueValues;
  }, getMemoOptions(table.options, "debugTable", `getFacetedUniqueValues_${columnId}`));
}
function getFilteredRowModel() {
  return (table) => memo(() => [table.getPreFilteredRowModel(), table.getState().columnFilters, table.getState().globalFilter], (rowModel, columnFilters, globalFilter) => {
    if (!rowModel.rows.length || !(columnFilters != null && columnFilters.length) && !globalFilter) {
      for (let i4 = 0; i4 < rowModel.flatRows.length; i4++) {
        rowModel.flatRows[i4].columnFilters = {};
        rowModel.flatRows[i4].columnFiltersMeta = {};
      }
      return rowModel;
    }
    const resolvedColumnFilters = [];
    const resolvedGlobalFilters = [];
    (columnFilters != null ? columnFilters : []).forEach((d3) => {
      var _filterFn$resolveFilt;
      const column = table.getColumn(d3.id);
      if (!column) {
        return;
      }
      const filterFn = column.getFilterFn();
      if (!filterFn) {
        if (true) {
          console.warn(`Could not find a valid 'column.filterFn' for column with the ID: ${column.id}.`);
        }
        return;
      }
      resolvedColumnFilters.push({
        id: d3.id,
        filterFn,
        resolvedValue: (_filterFn$resolveFilt = filterFn.resolveFilterValue == null ? void 0 : filterFn.resolveFilterValue(d3.value)) != null ? _filterFn$resolveFilt : d3.value
      });
    });
    const filterableIds = (columnFilters != null ? columnFilters : []).map((d3) => d3.id);
    const globalFilterFn = table.getGlobalFilterFn();
    const globallyFilterableColumns = table.getAllLeafColumns().filter((column) => column.getCanGlobalFilter());
    if (globalFilter && globalFilterFn && globallyFilterableColumns.length) {
      filterableIds.push("__global__");
      globallyFilterableColumns.forEach((column) => {
        var _globalFilterFn$resol;
        resolvedGlobalFilters.push({
          id: column.id,
          filterFn: globalFilterFn,
          resolvedValue: (_globalFilterFn$resol = globalFilterFn.resolveFilterValue == null ? void 0 : globalFilterFn.resolveFilterValue(globalFilter)) != null ? _globalFilterFn$resol : globalFilter
        });
      });
    }
    let currentColumnFilter;
    let currentGlobalFilter;
    for (let j4 = 0; j4 < rowModel.flatRows.length; j4++) {
      const row = rowModel.flatRows[j4];
      row.columnFilters = {};
      if (resolvedColumnFilters.length) {
        for (let i4 = 0; i4 < resolvedColumnFilters.length; i4++) {
          currentColumnFilter = resolvedColumnFilters[i4];
          const id = currentColumnFilter.id;
          row.columnFilters[id] = currentColumnFilter.filterFn(row, id, currentColumnFilter.resolvedValue, (filterMeta) => {
            row.columnFiltersMeta[id] = filterMeta;
          });
        }
      }
      if (resolvedGlobalFilters.length) {
        for (let i4 = 0; i4 < resolvedGlobalFilters.length; i4++) {
          currentGlobalFilter = resolvedGlobalFilters[i4];
          const id = currentGlobalFilter.id;
          if (currentGlobalFilter.filterFn(row, id, currentGlobalFilter.resolvedValue, (filterMeta) => {
            row.columnFiltersMeta[id] = filterMeta;
          })) {
            row.columnFilters.__global__ = true;
            break;
          }
        }
        if (row.columnFilters.__global__ !== true) {
          row.columnFilters.__global__ = false;
        }
      }
    }
    const filterRowsImpl = (row) => {
      for (let i4 = 0; i4 < filterableIds.length; i4++) {
        if (row.columnFilters[filterableIds[i4]] === false) {
          return false;
        }
      }
      return true;
    };
    return filterRows(rowModel.rows, filterRowsImpl, table);
  }, getMemoOptions(table.options, "debugTable", "getFilteredRowModel", () => table._autoResetPageIndex()));
}
function getSortedRowModel() {
  return (table) => memo(() => [table.getState().sorting, table.getPreSortedRowModel()], (sorting, rowModel) => {
    if (!rowModel.rows.length || !(sorting != null && sorting.length)) {
      return rowModel;
    }
    const sortingState = table.getState().sorting;
    const sortedFlatRows = [];
    const availableSorting = sortingState.filter((sort) => {
      var _table$getColumn;
      return (_table$getColumn = table.getColumn(sort.id)) == null ? void 0 : _table$getColumn.getCanSort();
    });
    const columnInfoById = {};
    availableSorting.forEach((sortEntry) => {
      const column = table.getColumn(sortEntry.id);
      if (!column)
        return;
      columnInfoById[sortEntry.id] = {
        sortUndefined: column.columnDef.sortUndefined,
        invertSorting: column.columnDef.invertSorting,
        sortingFn: column.getSortingFn()
      };
    });
    const sortData = (rows) => {
      const sortedData = rows.map((row) => ({
        ...row
      }));
      sortedData.sort((rowA, rowB) => {
        for (let i4 = 0; i4 < availableSorting.length; i4 += 1) {
          var _sortEntry$desc;
          const sortEntry = availableSorting[i4];
          const columnInfo = columnInfoById[sortEntry.id];
          const sortUndefined = columnInfo.sortUndefined;
          const isDesc = (_sortEntry$desc = sortEntry == null ? void 0 : sortEntry.desc) != null ? _sortEntry$desc : false;
          let sortInt = 0;
          if (sortUndefined) {
            const aValue = rowA.getValue(sortEntry.id);
            const bValue = rowB.getValue(sortEntry.id);
            const aUndefined = aValue === void 0;
            const bUndefined = bValue === void 0;
            if (aUndefined || bUndefined) {
              if (sortUndefined === "first")
                return aUndefined ? -1 : 1;
              if (sortUndefined === "last")
                return aUndefined ? 1 : -1;
              sortInt = aUndefined && bUndefined ? 0 : aUndefined ? sortUndefined : -sortUndefined;
            }
          }
          if (sortInt === 0) {
            sortInt = columnInfo.sortingFn(rowA, rowB, sortEntry.id);
          }
          if (sortInt !== 0) {
            if (isDesc) {
              sortInt *= -1;
            }
            if (columnInfo.invertSorting) {
              sortInt *= -1;
            }
            return sortInt;
          }
        }
        return rowA.index - rowB.index;
      });
      sortedData.forEach((row) => {
        var _row$subRows;
        sortedFlatRows.push(row);
        if ((_row$subRows = row.subRows) != null && _row$subRows.length) {
          row.subRows = sortData(row.subRows);
        }
      });
      return sortedData;
    };
    return {
      rows: sortData(rowModel.rows),
      flatRows: sortedFlatRows,
      rowsById: rowModel.rowsById
    };
  }, getMemoOptions(table.options, "debugTable", "getSortedRowModel", () => table._autoResetPageIndex()));
}

// node_modules/@tanstack/react-table/build/lib/index.mjs
function flexRender(Comp, props) {
  return !Comp ? null : isReactComponent(Comp) ? /* @__PURE__ */ _(Comp, props) : Comp;
}
function isReactComponent(component) {
  return isClassComponent(component) || typeof component === "function" || isExoticComponent(component);
}
function isClassComponent(component) {
  return typeof component === "function" && (() => {
    const proto = Object.getPrototypeOf(component);
    return proto.prototype && proto.prototype.isReactComponent;
  })();
}
function isExoticComponent(component) {
  return typeof component === "object" && typeof component.$$typeof === "symbol" && ["react.memo", "react.forward_ref"].includes(component.$$typeof.description);
}
function useReactTable(options) {
  const resolvedOptions = {
    state: {},
    // Dummy state
    onStateChange: () => {
    },
    // noop
    renderFallbackValue: null,
    ...options
  };
  const [tableRef] = h2(() => ({
    current: createTable(resolvedOptions)
  }));
  const [state, setState] = h2(() => tableRef.current.initialState);
  tableRef.current.setOptions((prev) => ({
    ...prev,
    ...options,
    state: {
      ...state,
      ...options.state
    },
    // Similarly, we'll maintain both our internal state and any user-provided
    // state.
    onStateChange: (updater) => {
      setState(updater);
      options.onStateChange == null || options.onStateChange(updater);
    }
  }));
  return tableRef.current;
}

// node_modules/@tanstack/virtual-core/dist/esm/utils.js
function memo2(getDeps, fn2, opts) {
  let deps = opts.initialDeps ?? [];
  let result;
  return () => {
    var _a, _b, _c, _d;
    let depTime;
    if (opts.key && ((_a = opts.debug) == null ? void 0 : _a.call(opts)))
      depTime = Date.now();
    const newDeps = getDeps();
    const depsChanged = newDeps.length !== deps.length || newDeps.some((dep, index) => deps[index] !== dep);
    if (!depsChanged) {
      return result;
    }
    deps = newDeps;
    let resultTime;
    if (opts.key && ((_b = opts.debug) == null ? void 0 : _b.call(opts)))
      resultTime = Date.now();
    result = fn2(...newDeps);
    if (opts.key && ((_c = opts.debug) == null ? void 0 : _c.call(opts))) {
      const depEndTime = Math.round((Date.now() - depTime) * 100) / 100;
      const resultEndTime = Math.round((Date.now() - resultTime) * 100) / 100;
      const resultFpsPercentage = resultEndTime / 16;
      const pad = (str, num) => {
        str = String(str);
        while (str.length < num) {
          str = " " + str;
        }
        return str;
      };
      console.info(
        `%c\u23F1 ${pad(resultEndTime, 5)} /${pad(depEndTime, 5)} ms`,
        `
            font-size: .6rem;
            font-weight: bold;
            color: hsl(${Math.max(
          0,
          Math.min(120 - 120 * resultFpsPercentage, 120)
        )}deg 100% 31%);`,
        opts == null ? void 0 : opts.key
      );
    }
    (_d = opts == null ? void 0 : opts.onChange) == null ? void 0 : _d.call(opts, result);
    return result;
  };
}
function notUndefined(value, msg) {
  if (value === void 0) {
    throw new Error(`Unexpected undefined${msg ? `: ${msg}` : ""}`);
  } else {
    return value;
  }
}
var approxEqual = (a3, b2) => Math.abs(a3 - b2) < 1;
var debounce = (targetWindow, fn2, ms) => {
  let timeoutId;
  return function(...args) {
    targetWindow.clearTimeout(timeoutId);
    timeoutId = targetWindow.setTimeout(() => fn2.apply(this, args), ms);
  };
};

// node_modules/@tanstack/virtual-core/dist/esm/index.js
var defaultKeyExtractor = (index) => index;
var defaultRangeExtractor = (range) => {
  const start = Math.max(range.startIndex - range.overscan, 0);
  const end = Math.min(range.endIndex + range.overscan, range.count - 1);
  const arr = [];
  for (let i4 = start; i4 <= end; i4++) {
    arr.push(i4);
  }
  return arr;
};
var observeElementRect = (instance, cb) => {
  const element = instance.scrollElement;
  if (!element) {
    return;
  }
  const targetWindow = instance.targetWindow;
  if (!targetWindow) {
    return;
  }
  const handler = (rect) => {
    const { width, height } = rect;
    cb({ width: Math.round(width), height: Math.round(height) });
  };
  handler(element.getBoundingClientRect());
  if (!targetWindow.ResizeObserver) {
    return () => {
    };
  }
  const observer = new targetWindow.ResizeObserver((entries) => {
    const entry = entries[0];
    if (entry == null ? void 0 : entry.borderBoxSize) {
      const box = entry.borderBoxSize[0];
      if (box) {
        handler({ width: box.inlineSize, height: box.blockSize });
        return;
      }
    }
    handler(element.getBoundingClientRect());
  });
  observer.observe(element, { box: "border-box" });
  return () => {
    observer.unobserve(element);
  };
};
var addEventListenerOptions = {
  passive: true
};
var supportsScrollend = typeof window == "undefined" ? true : "onscrollend" in window;
var observeElementOffset = (instance, cb) => {
  const element = instance.scrollElement;
  if (!element) {
    return;
  }
  const targetWindow = instance.targetWindow;
  if (!targetWindow) {
    return;
  }
  let offset = 0;
  const fallback = supportsScrollend ? () => void 0 : debounce(
    targetWindow,
    () => {
      cb(offset, false);
    },
    instance.options.isScrollingResetDelay
  );
  const createHandler = (isScrolling) => () => {
    offset = element[instance.options.horizontal ? "scrollLeft" : "scrollTop"];
    fallback();
    cb(offset, isScrolling);
  };
  const handler = createHandler(true);
  const endHandler = createHandler(false);
  endHandler();
  element.addEventListener("scroll", handler, addEventListenerOptions);
  element.addEventListener("scrollend", endHandler, addEventListenerOptions);
  return () => {
    element.removeEventListener("scroll", handler);
    element.removeEventListener("scrollend", endHandler);
  };
};
var measureElement = (element, entry, instance) => {
  if (entry == null ? void 0 : entry.borderBoxSize) {
    const box = entry.borderBoxSize[0];
    if (box) {
      const size = Math.round(
        box[instance.options.horizontal ? "inlineSize" : "blockSize"]
      );
      return size;
    }
  }
  return Math.round(
    element.getBoundingClientRect()[instance.options.horizontal ? "width" : "height"]
  );
};
var elementScroll = (offset, {
  adjustments = 0,
  behavior
}, instance) => {
  var _a, _b;
  const toOffset = offset + adjustments;
  (_b = (_a = instance.scrollElement) == null ? void 0 : _a.scrollTo) == null ? void 0 : _b.call(_a, {
    [instance.options.horizontal ? "left" : "top"]: toOffset,
    behavior
  });
};
var Virtualizer = class {
  constructor(opts) {
    this.unsubs = [];
    this.scrollElement = null;
    this.targetWindow = null;
    this.isScrolling = false;
    this.scrollToIndexTimeoutId = null;
    this.measurementsCache = [];
    this.itemSizeCache = /* @__PURE__ */ new Map();
    this.pendingMeasuredCacheIndexes = [];
    this.scrollRect = null;
    this.scrollOffset = null;
    this.scrollDirection = null;
    this.scrollAdjustments = 0;
    this.elementsCache = /* @__PURE__ */ new Map();
    this.observer = /* @__PURE__ */ (() => {
      let _ro = null;
      const get = () => {
        if (_ro) {
          return _ro;
        }
        if (!this.targetWindow || !this.targetWindow.ResizeObserver) {
          return null;
        }
        return _ro = new this.targetWindow.ResizeObserver((entries) => {
          entries.forEach((entry) => {
            this._measureElement(entry.target, entry);
          });
        });
      };
      return {
        disconnect: () => {
          var _a;
          return (_a = get()) == null ? void 0 : _a.disconnect();
        },
        observe: (target) => {
          var _a;
          return (_a = get()) == null ? void 0 : _a.observe(target, { box: "border-box" });
        },
        unobserve: (target) => {
          var _a;
          return (_a = get()) == null ? void 0 : _a.unobserve(target);
        }
      };
    })();
    this.range = null;
    this.setOptions = (opts2) => {
      Object.entries(opts2).forEach(([key, value]) => {
        if (typeof value === "undefined")
          delete opts2[key];
      });
      this.options = {
        debug: false,
        initialOffset: 0,
        overscan: 1,
        paddingStart: 0,
        paddingEnd: 0,
        scrollPaddingStart: 0,
        scrollPaddingEnd: 0,
        horizontal: false,
        getItemKey: defaultKeyExtractor,
        rangeExtractor: defaultRangeExtractor,
        onChange: () => {
        },
        measureElement,
        initialRect: { width: 0, height: 0 },
        scrollMargin: 0,
        gap: 0,
        indexAttribute: "data-index",
        initialMeasurementsCache: [],
        lanes: 1,
        isScrollingResetDelay: 150,
        enabled: true,
        ...opts2
      };
    };
    this.notify = (force, sync) => {
      var _a, _b;
      const { startIndex, endIndex } = this.range ?? {
        startIndex: void 0,
        endIndex: void 0
      };
      const range = this.calculateRange();
      if (force || startIndex !== (range == null ? void 0 : range.startIndex) || endIndex !== (range == null ? void 0 : range.endIndex)) {
        (_b = (_a = this.options).onChange) == null ? void 0 : _b.call(_a, this, sync);
      }
    };
    this.cleanup = () => {
      this.unsubs.filter(Boolean).forEach((d3) => d3());
      this.unsubs = [];
      this.scrollElement = null;
      this.targetWindow = null;
      this.observer.disconnect();
      this.elementsCache.clear();
    };
    this._didMount = () => {
      return () => {
        this.cleanup();
      };
    };
    this._willUpdate = () => {
      var _a;
      const scrollElement = this.options.enabled ? this.options.getScrollElement() : null;
      if (this.scrollElement !== scrollElement) {
        this.cleanup();
        if (!scrollElement) {
          this.notify(false, false);
          return;
        }
        this.scrollElement = scrollElement;
        if (this.scrollElement && "ownerDocument" in this.scrollElement) {
          this.targetWindow = this.scrollElement.ownerDocument.defaultView;
        } else {
          this.targetWindow = ((_a = this.scrollElement) == null ? void 0 : _a.window) ?? null;
        }
        this._scrollToOffset(this.getScrollOffset(), {
          adjustments: void 0,
          behavior: void 0
        });
        this.unsubs.push(
          this.options.observeElementRect(this, (rect) => {
            this.scrollRect = rect;
            this.notify(false, false);
          })
        );
        this.unsubs.push(
          this.options.observeElementOffset(this, (offset, isScrolling) => {
            this.scrollAdjustments = 0;
            this.scrollDirection = isScrolling ? this.getScrollOffset() < offset ? "forward" : "backward" : null;
            this.scrollOffset = offset;
            const prevIsScrolling = this.isScrolling;
            this.isScrolling = isScrolling;
            this.notify(prevIsScrolling !== isScrolling, isScrolling);
          })
        );
      }
    };
    this.getSize = () => {
      if (!this.options.enabled) {
        this.scrollRect = null;
        return 0;
      }
      this.scrollRect = this.scrollRect ?? this.options.initialRect;
      return this.scrollRect[this.options.horizontal ? "width" : "height"];
    };
    this.getScrollOffset = () => {
      if (!this.options.enabled) {
        this.scrollOffset = null;
        return 0;
      }
      this.scrollOffset = this.scrollOffset ?? (typeof this.options.initialOffset === "function" ? this.options.initialOffset() : this.options.initialOffset);
      return this.scrollOffset;
    };
    this.getFurthestMeasurement = (measurements, index) => {
      const furthestMeasurementsFound = /* @__PURE__ */ new Map();
      const furthestMeasurements = /* @__PURE__ */ new Map();
      for (let m3 = index - 1; m3 >= 0; m3--) {
        const measurement = measurements[m3];
        if (furthestMeasurementsFound.has(measurement.lane)) {
          continue;
        }
        const previousFurthestMeasurement = furthestMeasurements.get(
          measurement.lane
        );
        if (previousFurthestMeasurement == null || measurement.end > previousFurthestMeasurement.end) {
          furthestMeasurements.set(measurement.lane, measurement);
        } else if (measurement.end < previousFurthestMeasurement.end) {
          furthestMeasurementsFound.set(measurement.lane, true);
        }
        if (furthestMeasurementsFound.size === this.options.lanes) {
          break;
        }
      }
      return furthestMeasurements.size === this.options.lanes ? Array.from(furthestMeasurements.values()).sort((a3, b2) => {
        if (a3.end === b2.end) {
          return a3.index - b2.index;
        }
        return a3.end - b2.end;
      })[0] : void 0;
    };
    this.getMeasurementOptions = memo2(
      () => [
        this.options.count,
        this.options.paddingStart,
        this.options.scrollMargin,
        this.options.getItemKey,
        this.options.enabled
      ],
      (count2, paddingStart, scrollMargin, getItemKey, enabled) => {
        this.pendingMeasuredCacheIndexes = [];
        return {
          count: count2,
          paddingStart,
          scrollMargin,
          getItemKey,
          enabled
        };
      },
      {
        key: false
      }
    );
    this.getMeasurements = memo2(
      () => [this.getMeasurementOptions(), this.itemSizeCache],
      ({ count: count2, paddingStart, scrollMargin, getItemKey, enabled }, itemSizeCache) => {
        var _a;
        if (!enabled) {
          this.measurementsCache = [];
          this.itemSizeCache.clear();
          return [];
        }
        if (this.measurementsCache.length === 0) {
          this.measurementsCache = this.options.initialMeasurementsCache;
          this.measurementsCache.forEach((item) => {
            this.itemSizeCache.set(item.key, item.size);
          });
        }
        const min2 = this.pendingMeasuredCacheIndexes.length > 0 ? Math.min(...this.pendingMeasuredCacheIndexes) : 0;
        this.pendingMeasuredCacheIndexes = [];
        const measurements = this.measurementsCache.slice(0, min2);
        for (let i4 = min2; i4 < count2; i4++) {
          let measureElement2 = (_a = this.measurementsCache[i4]) == null ? void 0 : _a.measureElement;
          if (!measureElement2) {
            measureElement2 = (node) => {
              const key2 = getItemKey(i4);
              const prevNode = this.elementsCache.get(key2);
              if (!node) {
                if (prevNode) {
                  this.observer.unobserve(prevNode);
                  this.elementsCache.delete(key2);
                }
                return;
              }
              if (prevNode !== node) {
                if (prevNode) {
                  this.observer.unobserve(prevNode);
                }
                this.observer.observe(node);
                this.elementsCache.set(key2, node);
              }
              if (node.isConnected) {
                this.resizeItem(
                  i4,
                  this.options.measureElement(node, void 0, this)
                );
              }
            };
          }
          const key = getItemKey(i4);
          const furthestMeasurement = this.options.lanes === 1 ? measurements[i4 - 1] : this.getFurthestMeasurement(measurements, i4);
          const start = furthestMeasurement ? furthestMeasurement.end + this.options.gap : paddingStart + scrollMargin;
          const measuredSize = itemSizeCache.get(key);
          const size = typeof measuredSize === "number" ? measuredSize : this.options.estimateSize(i4);
          const end = start + size;
          const lane = furthestMeasurement ? furthestMeasurement.lane : i4 % this.options.lanes;
          measurements[i4] = {
            index: i4,
            start,
            size,
            end,
            key,
            lane,
            measureElement: measureElement2
          };
        }
        this.measurementsCache = measurements;
        return measurements;
      },
      {
        key: "getMeasurements",
        debug: () => this.options.debug
      }
    );
    this.calculateRange = memo2(
      () => [this.getMeasurements(), this.getSize(), this.getScrollOffset()],
      (measurements, outerSize, scrollOffset) => {
        return this.range = measurements.length > 0 && outerSize > 0 ? calculateRange({
          measurements,
          outerSize,
          scrollOffset
        }) : null;
      },
      {
        key: "calculateRange",
        debug: () => this.options.debug
      }
    );
    this.getIndexes = memo2(
      () => [
        this.options.rangeExtractor,
        this.calculateRange(),
        this.options.overscan,
        this.options.count
      ],
      (rangeExtractor, range, overscan, count2) => {
        return range === null ? [] : rangeExtractor({
          startIndex: range.startIndex,
          endIndex: range.endIndex,
          overscan,
          count: count2
        });
      },
      {
        key: "getIndexes",
        debug: () => this.options.debug
      }
    );
    this.indexFromElement = (node) => {
      const attributeName = this.options.indexAttribute;
      const indexStr = node.getAttribute(attributeName);
      if (!indexStr) {
        console.warn(
          `Missing attribute name '${attributeName}={index}' on measured element.`
        );
        return -1;
      }
      return parseInt(indexStr, 10);
    };
    this._measureElement = (node, entry) => {
      const i4 = this.indexFromElement(node);
      const item = this.getMeasurements()[i4];
      if (!item || !node.isConnected) {
        this.elementsCache.forEach((cached, key) => {
          if (cached === node) {
            this.observer.unobserve(node);
            this.elementsCache.delete(key);
          }
        });
        return;
      }
      const prevNode = this.elementsCache.get(item.key);
      if (prevNode !== node) {
        if (prevNode) {
          this.observer.unobserve(prevNode);
        }
        this.observer.observe(node);
        this.elementsCache.set(item.key, node);
      }
      this.resizeItem(i4, this.options.measureElement(node, entry, this));
    };
    this.resizeItem = (index, size) => {
      const item = this.getMeasurements()[index];
      if (!item) {
        return;
      }
      const itemSize = this.itemSizeCache.get(item.key) ?? item.size;
      const delta = size - itemSize;
      if (delta !== 0) {
        if (this.shouldAdjustScrollPositionOnItemSizeChange !== void 0 ? this.shouldAdjustScrollPositionOnItemSizeChange(item, delta, this) : item.start < this.getScrollOffset() + this.scrollAdjustments) {
          if (this.options.debug) {
            console.info("correction", delta);
          }
          this._scrollToOffset(this.getScrollOffset(), {
            adjustments: this.scrollAdjustments += delta,
            behavior: void 0
          });
        }
        this.pendingMeasuredCacheIndexes.push(item.index);
        this.itemSizeCache = new Map(this.itemSizeCache.set(item.key, size));
        this.notify(true, false);
      }
    };
    this.measureElement = (node) => {
      if (!node) {
        return;
      }
      this._measureElement(node, void 0);
    };
    this.getVirtualItems = memo2(
      () => [this.getIndexes(), this.getMeasurements()],
      (indexes, measurements) => {
        const virtualItems = [];
        for (let k4 = 0, len = indexes.length; k4 < len; k4++) {
          const i4 = indexes[k4];
          const measurement = measurements[i4];
          virtualItems.push(measurement);
        }
        return virtualItems;
      },
      {
        key: "getIndexes",
        debug: () => this.options.debug
      }
    );
    this.getVirtualItemForOffset = (offset) => {
      const measurements = this.getMeasurements();
      if (measurements.length === 0) {
        return void 0;
      }
      return notUndefined(
        measurements[findNearestBinarySearch(
          0,
          measurements.length - 1,
          (index) => notUndefined(measurements[index]).start,
          offset
        )]
      );
    };
    this.getOffsetForAlignment = (toOffset, align) => {
      const size = this.getSize();
      const scrollOffset = this.getScrollOffset();
      if (align === "auto") {
        if (toOffset <= scrollOffset) {
          align = "start";
        } else if (toOffset >= scrollOffset + size) {
          align = "end";
        } else {
          align = "start";
        }
      }
      if (align === "start") {
        toOffset = toOffset;
      } else if (align === "end") {
        toOffset = toOffset - size;
      } else if (align === "center") {
        toOffset = toOffset - size / 2;
      }
      const scrollSizeProp = this.options.horizontal ? "scrollWidth" : "scrollHeight";
      const scrollSize = this.scrollElement ? "document" in this.scrollElement ? this.scrollElement.document.documentElement[scrollSizeProp] : this.scrollElement[scrollSizeProp] : 0;
      const maxOffset = scrollSize - size;
      return Math.max(Math.min(maxOffset, toOffset), 0);
    };
    this.getOffsetForIndex = (index, align = "auto") => {
      index = Math.max(0, Math.min(index, this.options.count - 1));
      const item = this.getMeasurements()[index];
      if (!item) {
        return void 0;
      }
      const size = this.getSize();
      const scrollOffset = this.getScrollOffset();
      if (align === "auto") {
        if (item.end >= scrollOffset + size - this.options.scrollPaddingEnd) {
          align = "end";
        } else if (item.start <= scrollOffset + this.options.scrollPaddingStart) {
          align = "start";
        } else {
          return [scrollOffset, align];
        }
      }
      const toOffset = align === "end" ? item.end + this.options.scrollPaddingEnd : item.start - this.options.scrollPaddingStart;
      return [this.getOffsetForAlignment(toOffset, align), align];
    };
    this.isDynamicMode = () => this.elementsCache.size > 0;
    this.cancelScrollToIndex = () => {
      if (this.scrollToIndexTimeoutId !== null && this.targetWindow) {
        this.targetWindow.clearTimeout(this.scrollToIndexTimeoutId);
        this.scrollToIndexTimeoutId = null;
      }
    };
    this.scrollToOffset = (toOffset, { align = "start", behavior } = {}) => {
      this.cancelScrollToIndex();
      if (behavior === "smooth" && this.isDynamicMode()) {
        console.warn(
          "The `smooth` scroll behavior is not fully supported with dynamic size."
        );
      }
      this._scrollToOffset(this.getOffsetForAlignment(toOffset, align), {
        adjustments: void 0,
        behavior
      });
    };
    this.scrollToIndex = (index, { align: initialAlign = "auto", behavior } = {}) => {
      index = Math.max(0, Math.min(index, this.options.count - 1));
      this.cancelScrollToIndex();
      if (behavior === "smooth" && this.isDynamicMode()) {
        console.warn(
          "The `smooth` scroll behavior is not fully supported with dynamic size."
        );
      }
      const offsetAndAlign = this.getOffsetForIndex(index, initialAlign);
      if (!offsetAndAlign)
        return;
      const [offset, align] = offsetAndAlign;
      this._scrollToOffset(offset, { adjustments: void 0, behavior });
      if (behavior !== "smooth" && this.isDynamicMode() && this.targetWindow) {
        this.scrollToIndexTimeoutId = this.targetWindow.setTimeout(() => {
          this.scrollToIndexTimeoutId = null;
          const elementInDOM = this.elementsCache.has(
            this.options.getItemKey(index)
          );
          if (elementInDOM) {
            const [latestOffset] = notUndefined(
              this.getOffsetForIndex(index, align)
            );
            if (!approxEqual(latestOffset, this.getScrollOffset())) {
              this.scrollToIndex(index, { align, behavior });
            }
          } else {
            this.scrollToIndex(index, { align, behavior });
          }
        });
      }
    };
    this.scrollBy = (delta, { behavior } = {}) => {
      this.cancelScrollToIndex();
      if (behavior === "smooth" && this.isDynamicMode()) {
        console.warn(
          "The `smooth` scroll behavior is not fully supported with dynamic size."
        );
      }
      this._scrollToOffset(this.getScrollOffset() + delta, {
        adjustments: void 0,
        behavior
      });
    };
    this.getTotalSize = () => {
      var _a;
      const measurements = this.getMeasurements();
      let end;
      if (measurements.length === 0) {
        end = this.options.paddingStart;
      } else {
        end = this.options.lanes === 1 ? ((_a = measurements[measurements.length - 1]) == null ? void 0 : _a.end) ?? 0 : Math.max(
          ...measurements.slice(-this.options.lanes).map((m3) => m3.end)
        );
      }
      return end - this.options.scrollMargin + this.options.paddingEnd;
    };
    this._scrollToOffset = (offset, {
      adjustments,
      behavior
    }) => {
      this.options.scrollToFn(offset, { behavior, adjustments }, this);
    };
    this.measure = () => {
      var _a, _b;
      this.itemSizeCache = /* @__PURE__ */ new Map();
      (_b = (_a = this.options).onChange) == null ? void 0 : _b.call(_a, this, false);
    };
    this.setOptions(opts);
  }
};
var findNearestBinarySearch = (low, high, getCurrentValue, value) => {
  while (low <= high) {
    const middle = (low + high) / 2 | 0;
    const currentValue = getCurrentValue(middle);
    if (currentValue < value) {
      low = middle + 1;
    } else if (currentValue > value) {
      high = middle - 1;
    } else {
      return middle;
    }
  }
  if (low > 0) {
    return low - 1;
  } else {
    return 0;
  }
};
function calculateRange({
  measurements,
  outerSize,
  scrollOffset
}) {
  const count2 = measurements.length - 1;
  const getOffset = (index) => measurements[index].start;
  const startIndex = findNearestBinarySearch(0, count2, getOffset, scrollOffset);
  let endIndex = startIndex;
  while (endIndex < count2 && measurements[endIndex].end < scrollOffset + outerSize) {
    endIndex++;
  }
  return { startIndex, endIndex };
}

// node_modules/@tanstack/react-virtual/dist/esm/index.js
var useIsomorphicLayoutEffect = typeof document !== "undefined" ? _2 : y2;
function useVirtualizerBase(options) {
  const rerender = p2(() => ({}), {})[1];
  const resolvedOptions = {
    ...options,
    onChange: (instance2, sync) => {
      var _a;
      if (sync) {
        mn(rerender);
      } else {
        rerender();
      }
      (_a = options.onChange) == null ? void 0 : _a.call(options, instance2, sync);
    }
  };
  const [instance] = h2(
    () => new Virtualizer(resolvedOptions)
  );
  instance.setOptions(resolvedOptions);
  y2(() => {
    return instance._didMount();
  }, []);
  useIsomorphicLayoutEffect(() => {
    return instance._willUpdate();
  });
  return instance;
}
function useVirtualizer(options) {
  return useVirtualizerBase({
    observeElementRect,
    observeElementOffset,
    scrollToFn: elementScroll,
    ...options
  });
}

// node_modules/preact/compat/client.mjs
function createRoot(container) {
  return {
    // eslint-disable-next-line
    render: function(children) {
      q3(children, container);
    },
    // eslint-disable-next-line
    unmount: function() {
      vn(container);
    }
  };
}

// node_modules/immer/dist/immer.mjs
var NOTHING = Symbol.for("immer-nothing");
var DRAFTABLE = Symbol.for("immer-draftable");
var DRAFT_STATE = Symbol.for("immer-state");
var errors = true ? [
  // All error codes, starting by 0:
  function(plugin) {
    return `The plugin for '${plugin}' has not been loaded into Immer. To enable the plugin, import and call \`enable${plugin}()\` when initializing your application.`;
  },
  function(thing) {
    return `produce can only be called on things that are draftable: plain objects, arrays, Map, Set or classes that are marked with '[immerable]: true'. Got '${thing}'`;
  },
  "This object has been frozen and should not be mutated",
  function(data) {
    return "Cannot use a proxy that has been revoked. Did you pass an object from inside an immer function to an async process? " + data;
  },
  "An immer producer returned a new value *and* modified its draft. Either return a new value *or* modify the draft.",
  "Immer forbids circular references",
  "The first or second argument to `produce` must be a function",
  "The third argument to `produce` must be a function or undefined",
  "First argument to `createDraft` must be a plain object, an array, or an immerable object",
  "First argument to `finishDraft` must be a draft returned by `createDraft`",
  function(thing) {
    return `'current' expects a draft, got: ${thing}`;
  },
  "Object.defineProperty() cannot be used on an Immer draft",
  "Object.setPrototypeOf() cannot be used on an Immer draft",
  "Immer only supports deleting array indices",
  "Immer only supports setting array indices and the 'length' property",
  function(thing) {
    return `'original' expects a draft, got: ${thing}`;
  }
  // Note: if more errors are added, the errorOffset in Patches.ts should be increased
  // See Patches.ts for additional errors
] : [];
function die(error, ...args) {
  if (true) {
    const e3 = errors[error];
    const msg = typeof e3 === "function" ? e3.apply(null, args) : e3;
    throw new Error(`[Immer] ${msg}`);
  }
  throw new Error(
    `[Immer] minified error nr: ${error}. Full error at: https://bit.ly/3cXEKWf`
  );
}
var getPrototypeOf = Object.getPrototypeOf;
function isDraft(value) {
  return !!value && !!value[DRAFT_STATE];
}
function isDraftable(value) {
  if (!value)
    return false;
  return isPlainObject(value) || Array.isArray(value) || !!value[DRAFTABLE] || !!value.constructor?.[DRAFTABLE] || isMap(value) || isSet(value);
}
var objectCtorString = Object.prototype.constructor.toString();
function isPlainObject(value) {
  if (!value || typeof value !== "object")
    return false;
  const proto = getPrototypeOf(value);
  if (proto === null) {
    return true;
  }
  const Ctor = Object.hasOwnProperty.call(proto, "constructor") && proto.constructor;
  if (Ctor === Object)
    return true;
  return typeof Ctor == "function" && Function.toString.call(Ctor) === objectCtorString;
}
function each(obj, iter) {
  if (getArchtype(obj) === 0) {
    Object.entries(obj).forEach(([key, value]) => {
      iter(key, value, obj);
    });
  } else {
    obj.forEach((entry, index) => iter(index, entry, obj));
  }
}
function getArchtype(thing) {
  const state = thing[DRAFT_STATE];
  return state ? state.type_ : Array.isArray(thing) ? 1 : isMap(thing) ? 2 : isSet(thing) ? 3 : 0;
}
function has(thing, prop) {
  return getArchtype(thing) === 2 ? thing.has(prop) : Object.prototype.hasOwnProperty.call(thing, prop);
}
function set(thing, propOrOldValue, value) {
  const t3 = getArchtype(thing);
  if (t3 === 2)
    thing.set(propOrOldValue, value);
  else if (t3 === 3) {
    thing.add(value);
  } else
    thing[propOrOldValue] = value;
}
function is(x4, y3) {
  if (x4 === y3) {
    return x4 !== 0 || 1 / x4 === 1 / y3;
  } else {
    return x4 !== x4 && y3 !== y3;
  }
}
function isMap(target) {
  return target instanceof Map;
}
function isSet(target) {
  return target instanceof Set;
}
function latest(state) {
  return state.copy_ || state.base_;
}
function shallowCopy(base, strict) {
  if (isMap(base)) {
    return new Map(base);
  }
  if (isSet(base)) {
    return new Set(base);
  }
  if (Array.isArray(base))
    return Array.prototype.slice.call(base);
  if (!strict && isPlainObject(base)) {
    if (!getPrototypeOf(base)) {
      const obj = /* @__PURE__ */ Object.create(null);
      return Object.assign(obj, base);
    }
    return { ...base };
  }
  const descriptors = Object.getOwnPropertyDescriptors(base);
  delete descriptors[DRAFT_STATE];
  let keys = Reflect.ownKeys(descriptors);
  for (let i4 = 0; i4 < keys.length; i4++) {
    const key = keys[i4];
    const desc = descriptors[key];
    if (desc.writable === false) {
      desc.writable = true;
      desc.configurable = true;
    }
    if (desc.get || desc.set)
      descriptors[key] = {
        configurable: true,
        writable: true,
        // could live with !!desc.set as well here...
        enumerable: desc.enumerable,
        value: base[key]
      };
  }
  return Object.create(getPrototypeOf(base), descriptors);
}
function freeze(obj, deep = false) {
  if (isFrozen(obj) || isDraft(obj) || !isDraftable(obj))
    return obj;
  if (getArchtype(obj) > 1) {
    obj.set = obj.add = obj.clear = obj.delete = dontMutateFrozenCollections;
  }
  Object.freeze(obj);
  if (deep)
    each(obj, (_key, value) => freeze(value, true), true);
  return obj;
}
function dontMutateFrozenCollections() {
  die(2);
}
function isFrozen(obj) {
  return Object.isFrozen(obj);
}
var plugins = {};
function getPlugin(pluginKey) {
  const plugin = plugins[pluginKey];
  if (!plugin) {
    die(0, pluginKey);
  }
  return plugin;
}
function loadPlugin(pluginKey, implementation) {
  if (!plugins[pluginKey])
    plugins[pluginKey] = implementation;
}
var currentScope;
function getCurrentScope() {
  return currentScope;
}
function createScope(parent_, immer_) {
  return {
    drafts_: [],
    parent_,
    immer_,
    // Whenever the modified draft contains a draft from another scope, we
    // need to prevent auto-freezing so the unowned draft can be finalized.
    canAutoFreeze_: true,
    unfinalizedDrafts_: 0
  };
}
function usePatchesInScope(scope, patchListener) {
  if (patchListener) {
    getPlugin("Patches");
    scope.patches_ = [];
    scope.inversePatches_ = [];
    scope.patchListener_ = patchListener;
  }
}
function revokeScope(scope) {
  leaveScope(scope);
  scope.drafts_.forEach(revokeDraft);
  scope.drafts_ = null;
}
function leaveScope(scope) {
  if (scope === currentScope) {
    currentScope = scope.parent_;
  }
}
function enterScope(immer2) {
  return currentScope = createScope(currentScope, immer2);
}
function revokeDraft(draft) {
  const state = draft[DRAFT_STATE];
  if (state.type_ === 0 || state.type_ === 1)
    state.revoke_();
  else
    state.revoked_ = true;
}
function processResult(result, scope) {
  scope.unfinalizedDrafts_ = scope.drafts_.length;
  const baseDraft = scope.drafts_[0];
  const isReplaced = result !== void 0 && result !== baseDraft;
  if (isReplaced) {
    if (baseDraft[DRAFT_STATE].modified_) {
      revokeScope(scope);
      die(4);
    }
    if (isDraftable(result)) {
      result = finalize(scope, result);
      if (!scope.parent_)
        maybeFreeze(scope, result);
    }
    if (scope.patches_) {
      getPlugin("Patches").generateReplacementPatches_(
        baseDraft[DRAFT_STATE].base_,
        result,
        scope.patches_,
        scope.inversePatches_
      );
    }
  } else {
    result = finalize(scope, baseDraft, []);
  }
  revokeScope(scope);
  if (scope.patches_) {
    scope.patchListener_(scope.patches_, scope.inversePatches_);
  }
  return result !== NOTHING ? result : void 0;
}
function finalize(rootScope, value, path) {
  if (isFrozen(value))
    return value;
  const state = value[DRAFT_STATE];
  if (!state) {
    each(
      value,
      (key, childValue) => finalizeProperty(rootScope, state, value, key, childValue, path),
      true
      // See #590, don't recurse into non-enumerable of non drafted objects
    );
    return value;
  }
  if (state.scope_ !== rootScope)
    return value;
  if (!state.modified_) {
    maybeFreeze(rootScope, state.base_, true);
    return state.base_;
  }
  if (!state.finalized_) {
    state.finalized_ = true;
    state.scope_.unfinalizedDrafts_--;
    const result = state.copy_;
    let resultEach = result;
    let isSet2 = false;
    if (state.type_ === 3) {
      resultEach = new Set(result);
      result.clear();
      isSet2 = true;
    }
    each(
      resultEach,
      (key, childValue) => finalizeProperty(rootScope, state, result, key, childValue, path, isSet2)
    );
    maybeFreeze(rootScope, result, false);
    if (path && rootScope.patches_) {
      getPlugin("Patches").generatePatches_(
        state,
        path,
        rootScope.patches_,
        rootScope.inversePatches_
      );
    }
  }
  return state.copy_;
}
function finalizeProperty(rootScope, parentState, targetObject, prop, childValue, rootPath, targetIsSet) {
  if (childValue === targetObject)
    die(5);
  if (isDraft(childValue)) {
    const path = rootPath && parentState && parentState.type_ !== 3 && // Set objects are atomic since they have no keys.
    !has(parentState.assigned_, prop) ? rootPath.concat(prop) : void 0;
    const res = finalize(rootScope, childValue, path);
    set(targetObject, prop, res);
    if (isDraft(res)) {
      rootScope.canAutoFreeze_ = false;
    } else
      return;
  } else if (targetIsSet) {
    targetObject.add(childValue);
  }
  if (isDraftable(childValue) && !isFrozen(childValue)) {
    if (!rootScope.immer_.autoFreeze_ && rootScope.unfinalizedDrafts_ < 1) {
      return;
    }
    finalize(rootScope, childValue);
    if (!parentState || !parentState.scope_.parent_)
      maybeFreeze(rootScope, childValue);
  }
}
function maybeFreeze(scope, value, deep = false) {
  if (!scope.parent_ && scope.immer_.autoFreeze_ && scope.canAutoFreeze_) {
    freeze(value, deep);
  }
}
function createProxyProxy(base, parent) {
  const isArray = Array.isArray(base);
  const state = {
    type_: isArray ? 1 : 0,
    // Track which produce call this is associated with.
    scope_: parent ? parent.scope_ : getCurrentScope(),
    // True for both shallow and deep changes.
    modified_: false,
    // Used during finalization.
    finalized_: false,
    // Track which properties have been assigned (true) or deleted (false).
    assigned_: {},
    // The parent draft state.
    parent_: parent,
    // The base state.
    base_: base,
    // The base proxy.
    draft_: null,
    // set below
    // The base copy with any updated values.
    copy_: null,
    // Called by the `produce` function.
    revoke_: null,
    isManual_: false
  };
  let target = state;
  let traps = objectTraps;
  if (isArray) {
    target = [state];
    traps = arrayTraps;
  }
  const { revoke, proxy } = Proxy.revocable(target, traps);
  state.draft_ = proxy;
  state.revoke_ = revoke;
  return proxy;
}
var objectTraps = {
  get(state, prop) {
    if (prop === DRAFT_STATE)
      return state;
    const source = latest(state);
    if (!has(source, prop)) {
      return readPropFromProto(state, source, prop);
    }
    const value = source[prop];
    if (state.finalized_ || !isDraftable(value)) {
      return value;
    }
    if (value === peek(state.base_, prop)) {
      prepareCopy(state);
      return state.copy_[prop] = createProxy(value, state);
    }
    return value;
  },
  has(state, prop) {
    return prop in latest(state);
  },
  ownKeys(state) {
    return Reflect.ownKeys(latest(state));
  },
  set(state, prop, value) {
    const desc = getDescriptorFromProto(latest(state), prop);
    if (desc?.set) {
      desc.set.call(state.draft_, value);
      return true;
    }
    if (!state.modified_) {
      const current2 = peek(latest(state), prop);
      const currentState = current2?.[DRAFT_STATE];
      if (currentState && currentState.base_ === value) {
        state.copy_[prop] = value;
        state.assigned_[prop] = false;
        return true;
      }
      if (is(value, current2) && (value !== void 0 || has(state.base_, prop)))
        return true;
      prepareCopy(state);
      markChanged(state);
    }
    if (state.copy_[prop] === value && // special case: handle new props with value 'undefined'
    (value !== void 0 || prop in state.copy_) || // special case: NaN
    Number.isNaN(value) && Number.isNaN(state.copy_[prop]))
      return true;
    state.copy_[prop] = value;
    state.assigned_[prop] = true;
    return true;
  },
  deleteProperty(state, prop) {
    if (peek(state.base_, prop) !== void 0 || prop in state.base_) {
      state.assigned_[prop] = false;
      prepareCopy(state);
      markChanged(state);
    } else {
      delete state.assigned_[prop];
    }
    if (state.copy_) {
      delete state.copy_[prop];
    }
    return true;
  },
  // Note: We never coerce `desc.value` into an Immer draft, because we can't make
  // the same guarantee in ES5 mode.
  getOwnPropertyDescriptor(state, prop) {
    const owner = latest(state);
    const desc = Reflect.getOwnPropertyDescriptor(owner, prop);
    if (!desc)
      return desc;
    return {
      writable: true,
      configurable: state.type_ !== 1 || prop !== "length",
      enumerable: desc.enumerable,
      value: owner[prop]
    };
  },
  defineProperty() {
    die(11);
  },
  getPrototypeOf(state) {
    return getPrototypeOf(state.base_);
  },
  setPrototypeOf() {
    die(12);
  }
};
var arrayTraps = {};
each(objectTraps, (key, fn2) => {
  arrayTraps[key] = function() {
    arguments[0] = arguments[0][0];
    return fn2.apply(this, arguments);
  };
});
arrayTraps.deleteProperty = function(state, prop) {
  if (isNaN(parseInt(prop)))
    die(13);
  return arrayTraps.set.call(this, state, prop, void 0);
};
arrayTraps.set = function(state, prop, value) {
  if (prop !== "length" && isNaN(parseInt(prop)))
    die(14);
  return objectTraps.set.call(this, state[0], prop, value, state[0]);
};
function peek(draft, prop) {
  const state = draft[DRAFT_STATE];
  const source = state ? latest(state) : draft;
  return source[prop];
}
function readPropFromProto(state, source, prop) {
  const desc = getDescriptorFromProto(source, prop);
  return desc ? `value` in desc ? desc.value : (
    // This is a very special case, if the prop is a getter defined by the
    // prototype, we should invoke it with the draft as context!
    desc.get?.call(state.draft_)
  ) : void 0;
}
function getDescriptorFromProto(source, prop) {
  if (!(prop in source))
    return void 0;
  let proto = getPrototypeOf(source);
  while (proto) {
    const desc = Object.getOwnPropertyDescriptor(proto, prop);
    if (desc)
      return desc;
    proto = getPrototypeOf(proto);
  }
  return void 0;
}
function markChanged(state) {
  if (!state.modified_) {
    state.modified_ = true;
    if (state.parent_) {
      markChanged(state.parent_);
    }
  }
}
function prepareCopy(state) {
  if (!state.copy_) {
    state.copy_ = shallowCopy(
      state.base_,
      state.scope_.immer_.useStrictShallowCopy_
    );
  }
}
var Immer2 = class {
  constructor(config) {
    this.autoFreeze_ = true;
    this.useStrictShallowCopy_ = false;
    this.produce = (base, recipe, patchListener) => {
      if (typeof base === "function" && typeof recipe !== "function") {
        const defaultBase = recipe;
        recipe = base;
        const self = this;
        return function curriedProduce(base2 = defaultBase, ...args) {
          return self.produce(base2, (draft) => recipe.call(this, draft, ...args));
        };
      }
      if (typeof recipe !== "function")
        die(6);
      if (patchListener !== void 0 && typeof patchListener !== "function")
        die(7);
      let result;
      if (isDraftable(base)) {
        const scope = enterScope(this);
        const proxy = createProxy(base, void 0);
        let hasError = true;
        try {
          result = recipe(proxy);
          hasError = false;
        } finally {
          if (hasError)
            revokeScope(scope);
          else
            leaveScope(scope);
        }
        usePatchesInScope(scope, patchListener);
        return processResult(result, scope);
      } else if (!base || typeof base !== "object") {
        result = recipe(base);
        if (result === void 0)
          result = base;
        if (result === NOTHING)
          result = void 0;
        if (this.autoFreeze_)
          freeze(result, true);
        if (patchListener) {
          const p3 = [];
          const ip = [];
          getPlugin("Patches").generateReplacementPatches_(base, result, p3, ip);
          patchListener(p3, ip);
        }
        return result;
      } else
        die(1, base);
    };
    this.produceWithPatches = (base, recipe) => {
      if (typeof base === "function") {
        return (state, ...args) => this.produceWithPatches(state, (draft) => base(draft, ...args));
      }
      let patches, inversePatches;
      const result = this.produce(base, recipe, (p3, ip) => {
        patches = p3;
        inversePatches = ip;
      });
      return [result, patches, inversePatches];
    };
    if (typeof config?.autoFreeze === "boolean")
      this.setAutoFreeze(config.autoFreeze);
    if (typeof config?.useStrictShallowCopy === "boolean")
      this.setUseStrictShallowCopy(config.useStrictShallowCopy);
  }
  createDraft(base) {
    if (!isDraftable(base))
      die(8);
    if (isDraft(base))
      base = current(base);
    const scope = enterScope(this);
    const proxy = createProxy(base, void 0);
    proxy[DRAFT_STATE].isManual_ = true;
    leaveScope(scope);
    return proxy;
  }
  finishDraft(draft, patchListener) {
    const state = draft && draft[DRAFT_STATE];
    if (!state || !state.isManual_)
      die(9);
    const { scope_: scope } = state;
    usePatchesInScope(scope, patchListener);
    return processResult(void 0, scope);
  }
  /**
   * Pass true to automatically freeze all copies created by Immer.
   *
   * By default, auto-freezing is enabled.
   */
  setAutoFreeze(value) {
    this.autoFreeze_ = value;
  }
  /**
   * Pass true to enable strict shallow copy.
   *
   * By default, immer does not copy the object descriptors such as getter, setter and non-enumrable properties.
   */
  setUseStrictShallowCopy(value) {
    this.useStrictShallowCopy_ = value;
  }
  applyPatches(base, patches) {
    let i4;
    for (i4 = patches.length - 1; i4 >= 0; i4--) {
      const patch = patches[i4];
      if (patch.path.length === 0 && patch.op === "replace") {
        base = patch.value;
        break;
      }
    }
    if (i4 > -1) {
      patches = patches.slice(i4 + 1);
    }
    const applyPatchesImpl = getPlugin("Patches").applyPatches_;
    if (isDraft(base)) {
      return applyPatchesImpl(base, patches);
    }
    return this.produce(
      base,
      (draft) => applyPatchesImpl(draft, patches)
    );
  }
};
function createProxy(value, parent) {
  const draft = isMap(value) ? getPlugin("MapSet").proxyMap_(value, parent) : isSet(value) ? getPlugin("MapSet").proxySet_(value, parent) : createProxyProxy(value, parent);
  const scope = parent ? parent.scope_ : getCurrentScope();
  scope.drafts_.push(draft);
  return draft;
}
function current(value) {
  if (!isDraft(value))
    die(10, value);
  return currentImpl(value);
}
function currentImpl(value) {
  if (!isDraftable(value) || isFrozen(value))
    return value;
  const state = value[DRAFT_STATE];
  let copy;
  if (state) {
    if (!state.modified_)
      return state.base_;
    state.finalized_ = true;
    copy = shallowCopy(value, state.scope_.immer_.useStrictShallowCopy_);
  } else {
    copy = shallowCopy(value, true);
  }
  each(copy, (key, childValue) => {
    set(copy, key, currentImpl(childValue));
  });
  if (state) {
    state.finalized_ = false;
  }
  return copy;
}
function enableMapSet() {
  class DraftMap extends Map {
    constructor(target, parent) {
      super();
      this[DRAFT_STATE] = {
        type_: 2,
        parent_: parent,
        scope_: parent ? parent.scope_ : getCurrentScope(),
        modified_: false,
        finalized_: false,
        copy_: void 0,
        assigned_: void 0,
        base_: target,
        draft_: this,
        isManual_: false,
        revoked_: false
      };
    }
    get size() {
      return latest(this[DRAFT_STATE]).size;
    }
    has(key) {
      return latest(this[DRAFT_STATE]).has(key);
    }
    set(key, value) {
      const state = this[DRAFT_STATE];
      assertUnrevoked(state);
      if (!latest(state).has(key) || latest(state).get(key) !== value) {
        prepareMapCopy(state);
        markChanged(state);
        state.assigned_.set(key, true);
        state.copy_.set(key, value);
        state.assigned_.set(key, true);
      }
      return this;
    }
    delete(key) {
      if (!this.has(key)) {
        return false;
      }
      const state = this[DRAFT_STATE];
      assertUnrevoked(state);
      prepareMapCopy(state);
      markChanged(state);
      if (state.base_.has(key)) {
        state.assigned_.set(key, false);
      } else {
        state.assigned_.delete(key);
      }
      state.copy_.delete(key);
      return true;
    }
    clear() {
      const state = this[DRAFT_STATE];
      assertUnrevoked(state);
      if (latest(state).size) {
        prepareMapCopy(state);
        markChanged(state);
        state.assigned_ = /* @__PURE__ */ new Map();
        each(state.base_, (key) => {
          state.assigned_.set(key, false);
        });
        state.copy_.clear();
      }
    }
    forEach(cb, thisArg) {
      const state = this[DRAFT_STATE];
      latest(state).forEach((_value, key, _map) => {
        cb.call(thisArg, this.get(key), key, this);
      });
    }
    get(key) {
      const state = this[DRAFT_STATE];
      assertUnrevoked(state);
      const value = latest(state).get(key);
      if (state.finalized_ || !isDraftable(value)) {
        return value;
      }
      if (value !== state.base_.get(key)) {
        return value;
      }
      const draft = createProxy(value, state);
      prepareMapCopy(state);
      state.copy_.set(key, draft);
      return draft;
    }
    keys() {
      return latest(this[DRAFT_STATE]).keys();
    }
    values() {
      const iterator = this.keys();
      return {
        [Symbol.iterator]: () => this.values(),
        next: () => {
          const r3 = iterator.next();
          if (r3.done)
            return r3;
          const value = this.get(r3.value);
          return {
            done: false,
            value
          };
        }
      };
    }
    entries() {
      const iterator = this.keys();
      return {
        [Symbol.iterator]: () => this.entries(),
        next: () => {
          const r3 = iterator.next();
          if (r3.done)
            return r3;
          const value = this.get(r3.value);
          return {
            done: false,
            value: [r3.value, value]
          };
        }
      };
    }
    [(DRAFT_STATE, Symbol.iterator)]() {
      return this.entries();
    }
  }
  function proxyMap_(target, parent) {
    return new DraftMap(target, parent);
  }
  function prepareMapCopy(state) {
    if (!state.copy_) {
      state.assigned_ = /* @__PURE__ */ new Map();
      state.copy_ = new Map(state.base_);
    }
  }
  class DraftSet extends Set {
    constructor(target, parent) {
      super();
      this[DRAFT_STATE] = {
        type_: 3,
        parent_: parent,
        scope_: parent ? parent.scope_ : getCurrentScope(),
        modified_: false,
        finalized_: false,
        copy_: void 0,
        base_: target,
        draft_: this,
        drafts_: /* @__PURE__ */ new Map(),
        revoked_: false,
        isManual_: false
      };
    }
    get size() {
      return latest(this[DRAFT_STATE]).size;
    }
    has(value) {
      const state = this[DRAFT_STATE];
      assertUnrevoked(state);
      if (!state.copy_) {
        return state.base_.has(value);
      }
      if (state.copy_.has(value))
        return true;
      if (state.drafts_.has(value) && state.copy_.has(state.drafts_.get(value)))
        return true;
      return false;
    }
    add(value) {
      const state = this[DRAFT_STATE];
      assertUnrevoked(state);
      if (!this.has(value)) {
        prepareSetCopy(state);
        markChanged(state);
        state.copy_.add(value);
      }
      return this;
    }
    delete(value) {
      if (!this.has(value)) {
        return false;
      }
      const state = this[DRAFT_STATE];
      assertUnrevoked(state);
      prepareSetCopy(state);
      markChanged(state);
      return state.copy_.delete(value) || (state.drafts_.has(value) ? state.copy_.delete(state.drafts_.get(value)) : (
        /* istanbul ignore next */
        false
      ));
    }
    clear() {
      const state = this[DRAFT_STATE];
      assertUnrevoked(state);
      if (latest(state).size) {
        prepareSetCopy(state);
        markChanged(state);
        state.copy_.clear();
      }
    }
    values() {
      const state = this[DRAFT_STATE];
      assertUnrevoked(state);
      prepareSetCopy(state);
      return state.copy_.values();
    }
    entries() {
      const state = this[DRAFT_STATE];
      assertUnrevoked(state);
      prepareSetCopy(state);
      return state.copy_.entries();
    }
    keys() {
      return this.values();
    }
    [(DRAFT_STATE, Symbol.iterator)]() {
      return this.values();
    }
    forEach(cb, thisArg) {
      const iterator = this.values();
      let result = iterator.next();
      while (!result.done) {
        cb.call(thisArg, result.value, result.value, this);
        result = iterator.next();
      }
    }
  }
  function proxySet_(target, parent) {
    return new DraftSet(target, parent);
  }
  function prepareSetCopy(state) {
    if (!state.copy_) {
      state.copy_ = /* @__PURE__ */ new Set();
      state.base_.forEach((value) => {
        if (isDraftable(value)) {
          const draft = createProxy(value, state);
          state.drafts_.set(value, draft);
          state.copy_.add(draft);
        } else {
          state.copy_.add(value);
        }
      });
    }
  }
  function assertUnrevoked(state) {
    if (state.revoked_)
      die(3, JSON.stringify(latest(state)));
  }
  loadPlugin("MapSet", { proxyMap_, proxySet_ });
}
var immer = new Immer2();
var produce = immer.produce;
var produceWithPatches = immer.produceWithPatches.bind(
  immer
);
var setAutoFreeze = immer.setAutoFreeze.bind(immer);
var setUseStrictShallowCopy = immer.setUseStrictShallowCopy.bind(immer);
var applyPatches = immer.applyPatches.bind(immer);
var createDraft = immer.createDraft.bind(immer);
var finishDraft = immer.finishDraft.bind(immer);

// node_modules/use-immer/dist/use-immer.module.mjs
function i3(f3) {
  var u3 = h2(function() {
    return freeze("function" == typeof f3 ? f3() : f3, true);
  }), i4 = u3[1];
  return [u3[0], q2(function(t3) {
    i4("function" == typeof t3 ? produce(t3) : freeze(t3));
  }, [])];
}

// data-frame/request.ts
function makeRequest(method, args, onSuccess, onError, blobs) {
  window.Shiny.shinyapp.makeRequest(method, args, onSuccess, onError, blobs);
}
function makeRequestPromise({
  method,
  args,
  blobs
}) {
  return new Promise((resolve, reject) => {
    makeRequest(
      method,
      args,
      (value) => {
        resolve(value);
      },
      (err) => {
        reject(err);
      },
      blobs
    );
  });
}

// data-frame/data-update.tsx
function addPatchToData({
  setData,
  newPatches,
  setCellEditMapAtLoc
}) {
  setData((draft) => {
    newPatches.forEach(({ rowIndex, columnIndex, value }) => {
      draft[rowIndex][columnIndex] = value;
    });
  });
  newPatches.forEach(({ rowIndex, columnIndex, value }) => {
    setCellEditMapAtLoc(rowIndex, columnIndex, (obj_draft) => {
      obj_draft.value = value;
      obj_draft.state = CellStateEnum.EditSuccess;
      obj_draft.errorTitle = void 0;
    });
  });
}
function cellPatchPyArrToCellPatchArr(patchesPy) {
  const patches = patchesPy.map(
    (patch) => {
      return {
        rowIndex: patch.row_index,
        columnIndex: patch.column_index,
        value: patch.value
      };
    }
  );
  return patches;
}
function cellPatchArrToCellPatchPyArr(patches) {
  const patchesPy = patches.map((patch) => {
    return {
      row_index: patch.rowIndex,
      column_index: patch.columnIndex,
      value: patch.value
    };
  });
  return patchesPy;
}
function updateCellsData({
  patchInfo,
  patches,
  onSuccess,
  onError,
  columns,
  setData,
  setCellEditMapAtLoc
}) {
  const patchesPy = cellPatchArrToCellPatchPyArr(patches);
  makeRequestPromise({
    method: patchInfo.key,
    args: [
      // list[CellPatch]
      patchesPy
    ]
  }).then((newPatchesPy) => {
    if (!Array.isArray(newPatchesPy)) {
      throw new Error("Expected a response of a list of patches");
    }
    for (const patch of newPatchesPy) {
      if (!("row_index" in patch && "column_index" in patch && "value" in patch)) {
        throw new Error(
          "Expected list of patches containing `row_index`, `column_index`, and `value`"
        );
      }
    }
    newPatchesPy = newPatchesPy;
    const newPatches = cellPatchPyArrToCellPatchArr(newPatchesPy);
    patches.forEach(({ rowIndex, columnIndex, value }) => {
      setCellEditMapAtLoc(rowIndex, columnIndex, (obj_draft) => {
        if (obj_draft.state !== CellStateEnum.EditSaving)
          return;
        obj_draft.state = CellStateEnum.Ready;
        obj_draft.value = value;
        obj_draft.errorTitle = void 0;
      });
    });
    addPatchToData({ setData, newPatches, setCellEditMapAtLoc });
    onSuccess(newPatches);
  }).catch((err) => {
    patches.forEach(({ rowIndex, columnIndex, value }) => {
      setCellEditMapAtLoc(rowIndex, columnIndex, (obj_draft) => {
        obj_draft.value = String(value);
        obj_draft.state = CellStateEnum.EditFailure;
        obj_draft.errorTitle = String(err);
      });
    });
    onError(err);
  });
}

// data-frame/cell.tsx
var CellStateEnum = {
  EditSaving: "EditSaving",
  EditSuccess: "EditSuccess",
  EditFailure: "EditFailure",
  Editing: "Editing",
  Ready: "Ready"
};
var CellStateClassEnum = {
  EditSaving: "cell-edit-saving",
  EditSuccess: "cell-edit-success",
  EditFailure: "cell-edit-failure",
  Editing: "cell-edit-editing",
  Ready: void 0
};
var isShinyHtml = (x4) => {
  return x4 !== null && // Note: x === null has `typeof x === "object"`
  typeof x4 === "object" && Object.prototype.hasOwnProperty.call(x4, "isShinyHtml") && x4.isShinyHtml === true;
};
var getCellValueText = (cellValue) => {
  if (cellValue === null)
    return "";
  if (isShinyHtml(cellValue))
    return cellValue.obj.html;
  return cellValue;
};
var TableBodyCell = ({
  containerRef,
  rowId,
  cell,
  patchInfo,
  columns,
  coldefs,
  rowIndex,
  columnIndex,
  editCellsIsAllowed,
  getSortedRowModel: getSortedRowModel3,
  cellEditInfo,
  cellStyle,
  cellClassName,
  setData,
  setCellEditMapAtLoc,
  selection
}) => {
  const initialValue = cell.getValue();
  const isHtmlColumn = cell.column.columnDef.meta.isHtmlColumn;
  const cellValue = cellEditInfo?.value ?? initialValue;
  const cellState = cellEditInfo?.state ?? CellStateEnum.Ready;
  const errorTitle = cellEditInfo?.errorTitle;
  const isEditing = cellEditInfo?.isEditing ?? false;
  const editValue = cellEditInfo?.editValue ?? getCellValueText(cellValue);
  const tdRef = A2(null);
  const inputRef = A2(null);
  const resetEditing = q2(
    ({
      resetIsEditing = false,
      resetEditValue = false
    } = {
      resetIsEditing: true,
      resetEditValue: true
    }) => {
      setCellEditMapAtLoc(rowIndex, columnIndex, (obj_draft) => {
        if (resetIsEditing)
          obj_draft.isEditing = false;
        if (resetEditValue)
          obj_draft.editValue = void 0;
      });
    },
    [rowIndex, columnIndex, setCellEditMapAtLoc]
  );
  const handleEsc = (e3) => {
    if (e3.key !== "Escape")
      return;
    e3.preventDefault();
    e3.stopPropagation();
    resetEditing();
    selection.focusOffset(rowId, 0);
  };
  const handleTab = (e3) => {
    if (e3.key !== "Tab")
      return;
    e3.preventDefault();
    e3.stopPropagation();
    const hasShift = e3.shiftKey;
    let nextColumnIndex = columnIndex;
    while (true) {
      const newColumnIndex = nextColumnIndex + (hasShift ? -1 : 1);
      if (newColumnIndex < 0 || newColumnIndex >= coldefs.length) {
        return;
      }
      nextColumnIndex = newColumnIndex;
      if (coldefs[newColumnIndex].meta.isHtmlColumn !== true) {
        break;
      }
    }
    attemptUpdate();
    setCellEditMapAtLoc(rowIndex, nextColumnIndex, (obj_draft) => {
      obj_draft.isEditing = true;
    });
  };
  const handleEnter = (e3) => {
    if (e3.key !== "Enter")
      return;
    e3.preventDefault();
    e3.stopPropagation();
    const hasShift = e3.shiftKey;
    const rowModel = getSortedRowModel3();
    const sortedRowIndex = rowModel.rows.findIndex((row) => row.id === rowId);
    if (sortedRowIndex < 0) {
      return;
    }
    const nextSortedRowIndex = sortedRowIndex + (hasShift ? -1 : 1);
    if (nextSortedRowIndex < 0 || nextSortedRowIndex >= rowModel.rows.length) {
      return;
    }
    attemptUpdate();
    const targetRowIndex = rowModel.rows[nextSortedRowIndex].index;
    setCellEditMapAtLoc(targetRowIndex, columnIndex, (obj_draft) => {
      obj_draft.isEditing = true;
    });
  };
  const onInputKeyDown = (e3) => {
    [handleEsc, handleEnter, handleTab].forEach((fn2) => fn2(e3));
  };
  const attemptUpdate = q2(() => {
    setCellEditMapAtLoc(rowIndex, columnIndex, (obj_draft) => {
      obj_draft.errorTitle = void 0;
    });
    if (`${getCellValueText(cellValue)}` === `${editValue}`) {
      resetEditing();
      setCellEditMapAtLoc(rowIndex, columnIndex, (obj_draft) => {
        obj_draft.state = cellState;
      });
      return;
    }
    resetEditing({ resetIsEditing: true });
    setCellEditMapAtLoc(rowIndex, columnIndex, (obj_draft) => {
      obj_draft.state = CellStateEnum.EditSaving;
    });
    updateCellsData({
      patchInfo,
      patches: [{ rowIndex, columnIndex, value: editValue }],
      onSuccess: (_patches) => {
        resetEditing({ resetEditValue: true });
      },
      onError: (_err) => {
      },
      columns,
      setData,
      setCellEditMapAtLoc
    });
  }, [
    setCellEditMapAtLoc,
    rowIndex,
    columnIndex,
    cellValue,
    editValue,
    resetEditing,
    patchInfo,
    columns,
    setData,
    cellState
  ]);
  y2(() => {
    if (!isEditing)
      return;
    if (!inputRef.current)
      return;
    inputRef.current.focus();
    inputRef.current.select();
  }, [isEditing]);
  y2(() => {
    if (!isEditing)
      return;
    if (!tdRef.current)
      return;
    if (!inputRef.current)
      return;
    const onEdtingCellMouseDown = (e3) => {
      if (!tdRef.current?.contains(e3.target))
        return;
      e3.stopPropagation();
    };
    const curRef = tdRef.current;
    curRef.addEventListener("mousedown", onEdtingCellMouseDown);
    const onBodyMouseDown = (e3) => {
      if (e3.target === inputRef.current)
        return;
      attemptUpdate();
      resetEditing();
    };
    document.body.addEventListener("mousedown", onBodyMouseDown);
    return () => {
      curRef.removeEventListener("mousedown", onEdtingCellMouseDown);
      document.body.removeEventListener("mousedown", onBodyMouseDown);
    };
  }, [
    cellState,
    attemptUpdate,
    rowIndex,
    columnIndex,
    isEditing,
    resetEditing
  ]);
  function onFocus(e3) {
    if (isEditing) {
      e3.target.select();
    }
  }
  function onChange(e3) {
    setCellEditMapAtLoc(rowIndex, columnIndex, (obj_draft) => {
      obj_draft.editValue = e3.target.value;
    });
  }
  let onCellDoubleClick = void 0;
  let content = void 0;
  const cellTitle = errorTitle;
  let tableCellClass = cellClassName;
  const addToTableCellClass = (x4) => {
    if (!x4)
      return;
    if (tableCellClass) {
      tableCellClass += " ";
      tableCellClass += x4;
    } else {
      tableCellClass = x4;
    }
  };
  addToTableCellClass(
    CellStateClassEnum[isEditing ? CellStateEnum.Editing : cellState]
  );
  let attemptRenderAsync = false;
  let editContent = null;
  if (cellState === CellStateEnum.EditSaving) {
    content = editValue;
  } else {
    if (isEditing) {
      editContent = /* @__PURE__ */ Rn.createElement(
        "textarea",
        {
          value: String(editValue),
          onChange,
          onFocus,
          onKeyDown: onInputKeyDown,
          ref: inputRef
        }
      );
    } else if (isHtmlColumn) {
      addToTableCellClass("cell-html");
    } else {
      if (editCellsIsAllowed) {
        addToTableCellClass("cell-editable");
        onCellDoubleClick = (e3) => {
          setCellEditMapAtLoc(rowIndex, columnIndex, (obj_draft) => {
            obj_draft.isEditing = true;
            obj_draft.editValue = getCellValueText(cellValue);
          });
        };
      }
    }
    if (isShinyHtml(cellValue)) {
      attemptRenderAsync = true;
    } else {
      content = flexRender(cell.column.columnDef.cell, cell.getContext());
    }
  }
  y2(() => {
    if (!tdRef.current)
      return;
    if (!attemptRenderAsync)
      return;
    if (!isShinyHtml(cellValue))
      return;
    const cellValueObjDeepCopy = JSON.parse(JSON.stringify(cellValue.obj));
    window.Shiny.renderContentAsync(tdRef.current, cellValueObjDeepCopy);
    const curTdRef = tdRef.current;
    return () => {
      window.Shiny.unbindAll(curTdRef);
      curTdRef.replaceChildren("");
    };
  }, [tdRef, cellValue, rowIndex, columnIndex, attemptRenderAsync]);
  return /* @__PURE__ */ Rn.createElement(
    "td",
    {
      ref: tdRef,
      onDoubleClick: onCellDoubleClick,
      title: cellTitle,
      className: tableCellClass,
      style: { ...cellStyle }
    },
    editContent,
    content
  );
};

// data-frame/cell-edit-map.tsx
var useCellEditMap = () => {
  const [cellEditMap, setCellEditMap] = i3(
    /* @__PURE__ */ new Map()
  );
  enableMapSet();
  const setCellEditMapAtLoc = (rowIndex, columnIndex, obj_fn) => {
    setCellEditMap((draft) => {
      const key = makeCellEditMapKey(rowIndex, columnIndex);
      const obj = draft.get(key) ?? {};
      obj_fn(obj);
      draft.set(key, obj);
    });
  };
  return {
    cellEditMap,
    // setCellEditMap,
    setCellEditMapAtLoc,
    resetCellEditMap: () => {
      setCellEditMap(/* @__PURE__ */ new Map());
    }
  };
};
var makeCellEditMapKey = (rowIndex, columnIndex) => {
  return `[${rowIndex}, ${columnIndex}]`;
};
var getCellEditMapObj = (x4, rowIndex, columnIndex) => {
  const key = makeCellEditMapKey(rowIndex, columnIndex);
  return [x4.get(key) ?? {}, key];
};

// data-frame/dom-utils.tsx
function findFirstItemInView(scrollContainer, items, extraPadding) {
  const pad = Object.assign(
    { top: 0, right: 0, bottom: 0, left: 0 },
    extraPadding
  );
  const container = scrollContainer;
  const top = container.scrollTop + pad.top;
  const left = container.scrollLeft + pad.left;
  const bottom = top + container.clientHeight - pad.top - pad.bottom;
  const right = left + container.clientWidth - pad.left - pad.right;
  for (let i4 = 0; i4 < items.length; i4++) {
    const el = items[i4];
    const y3 = el.offsetTop, x4 = el.offsetLeft;
    if (y3 >= top && y3 <= bottom && x4 >= left && x4 <= right) {
      return el;
    }
  }
  return null;
}
function getStyle(el, styleProp) {
  return document?.defaultView?.getComputedStyle(el, null)?.getPropertyValue(styleProp);
}

// data-frame/filter-numeric.tsx
var FilterNumeric = (props) => {
  const [editing, setEditing] = h2(false);
  const { range, from, to, onRangeChange } = props;
  return /* @__PURE__ */ Rn.createElement(
    FilterNumericImpl,
    {
      range,
      value: [from, to],
      editing,
      onValueChange: (x4) => onRangeChange(...x4),
      onFocus: () => setEditing(true),
      onBlur: () => setEditing(false)
    }
  );
};
var FilterNumericImpl = (props) => {
  const [min2, max2] = props.value;
  const { editing, onFocus } = props;
  const [rangeMin, rangeMax] = props.range();
  const minInputRef = A2(null);
  const maxInputRef = A2(null);
  return /* @__PURE__ */ Rn.createElement(
    "div",
    {
      onBlur: (e3) => {
        if (e3.currentTarget.contains(e3.relatedTarget)) {
          return;
        }
        return props.onBlur();
      },
      onFocus: () => onFocus(),
      style: {
        display: "flex",
        gap: "0.5rem"
      }
    },
    /* @__PURE__ */ Rn.createElement(
      "input",
      {
        ref: minInputRef,
        className: `form-control form-control-sm ${minInputRef.current?.checkValidity() ? "" : "is-invalid"}`,
        style: { flex: "1 1 0", width: "0" },
        type: "number",
        placeholder: createPlaceholder(editing, "Min", rangeMin),
        defaultValue: min2,
        step: "any",
        onChange: (e3) => {
          const value = coerceToNum(e3.target.value);
          if (!minInputRef.current)
            return;
          minInputRef.current.classList.toggle(
            "is-invalid",
            !e3.target.checkValidity()
          );
          props.onValueChange([value, max2]);
        }
      }
    ),
    /* @__PURE__ */ Rn.createElement(
      "input",
      {
        ref: maxInputRef,
        className: `form-control form-control-sm ${maxInputRef.current?.checkValidity() ? "" : "is-invalid"}`,
        style: { flex: "1 1 0", width: "0" },
        type: "number",
        placeholder: createPlaceholder(editing, "Max", rangeMax),
        defaultValue: max2,
        step: "any",
        onChange: (e3) => {
          const value = coerceToNum(e3.target.value);
          if (!maxInputRef.current)
            return;
          maxInputRef.current.classList.toggle(
            "is-invalid",
            !e3.target.checkValidity()
          );
          props.onValueChange([min2, value]);
        }
      }
    )
  );
};
function createPlaceholder(editing, label, value) {
  if (!editing) {
    return void 0;
  } else if (typeof value === "undefined") {
    return label;
  } else {
    return `${label} (${value})`;
  }
}
function coerceToNum(value) {
  if (value === "") {
    return void 0;
  }
  return +value;
}

// data-frame/filter.tsx
function useFilters(enabled) {
  const [columnFilters, setColumnFilters] = h2([]);
  const filtersTableOptions = enabled ? {
    getFilteredRowModel: getFilteredRowModel(),
    getFacetedRowModel: getFacetedRowModel(),
    getFacetedUniqueValues: getFacetedUniqueValues(),
    getFacetedMinMaxValues: getFacetedMinMaxValues(),
    filterFns: {
      substring: (row, columnId, value, addMeta) => {
        return row.getValue(columnId)?.toString().includes(value) ?? false;
      }
    },
    onColumnFiltersChange: setColumnFilters
  } : {};
  return {
    columnFilters,
    columnFiltersState: {
      columnFilters
    },
    filtersTableOptions,
    setColumnFilters
  };
}
var Filter = ({ header, className, ...props }) => {
  const typeHint = header.column.columnDef.meta?.typeHint;
  if (!typeHint)
    return null;
  if (typeHint.type === "html")
    return null;
  if (typeHint.type === "numeric") {
    const [from, to] = header.column.getFilterValue() ?? [void 0, void 0];
    const range = () => {
      return header.column.getFacetedMinMaxValues() ?? [void 0, void 0];
    };
    return FilterNumeric({
      from,
      to,
      range,
      onRangeChange: (from2, to2) => header.column.setFilterValue([from2, to2])
    });
  }
  return /* @__PURE__ */ Rn.createElement(
    "input",
    {
      ...props,
      value: header.column.getFilterValue() || "",
      className: `form-control form-control-sm ${className}`,
      type: "text",
      onChange: (e3) => header.column.setFilterValue(e3.target.value)
    }
  );
};

// data-frame/immutable-set.tsx
var ImmutableSet = class _ImmutableSet {
  static {
    this._empty = new _ImmutableSet(/* @__PURE__ */ new Set());
  }
  constructor(set2) {
    this._set = set2;
  }
  static empty() {
    return this._empty;
  }
  static just(...values) {
    return this.empty().add(...values);
  }
  has(value) {
    return this._set.has(value);
  }
  add(...values) {
    const newSet = new Set(this._set.keys());
    for (const value of values) {
      newSet.add(value);
    }
    return new _ImmutableSet(newSet);
  }
  toggle(value) {
    if (this.has(value)) {
      return this.delete(value);
    } else {
      return this.add(value);
    }
  }
  delete(value) {
    const newSet = new Set(this._set.keys());
    newSet.delete(value);
    return new _ImmutableSet(newSet);
  }
  clear() {
    return _ImmutableSet.empty();
  }
  [Symbol.iterator]() {
    return this._set[Symbol.iterator]();
  }
  toList() {
    return [...this._set.keys()];
  }
};

// data-frame/selection.tsx
var SelectionModes = class _SelectionModes {
  static {
    this._NONE = "none";
  }
  static {
    this._ROW_SINGLE = "single";
  }
  static {
    this._ROW_MULTIPLE = "multiple";
  }
  static {
    this._COL_SINGLE = "single";
  }
  static {
    this._col_multiple = "multiple";
  }
  static {
    this._RECT_CELL = "cell";
  }
  static {
    this._RECT_REGION = "region";
  }
  static {
    this._rowEnum = {
      NONE: _SelectionModes._NONE,
      SINGLE: _SelectionModes._ROW_SINGLE,
      MULTIPLE: _SelectionModes._ROW_MULTIPLE
    };
  }
  static {
    this._colEnum = {
      NONE: _SelectionModes._NONE,
      SINGLE: _SelectionModes._COL_SINGLE,
      MULTIPLE: _SelectionModes._col_multiple
    };
  }
  static {
    this._rectEnum = {
      NONE: _SelectionModes._NONE,
      REGION: _SelectionModes._RECT_REGION,
      CELL: _SelectionModes._RECT_CELL
    };
  }
  constructor({
    row,
    col,
    rect
  }) {
    if (!Object.values(_SelectionModes._rowEnum).includes(row)) {
      throw new Error(`Invalid row selection mode: ${row}`);
    }
    if (!Object.values(_SelectionModes._colEnum).includes(col)) {
      throw new Error(`Invalid col selection mode: ${col}`);
    }
    if (!Object.values(_SelectionModes._rectEnum).includes(rect)) {
      throw new Error(`Invalid rect selection mode: ${rect}`);
    }
    this.row = row;
    this.col = col;
    this.rect = rect;
  }
  isNone() {
    return this.row === _SelectionModes._rowEnum.NONE && this.col === _SelectionModes._colEnum.NONE && this.rect === _SelectionModes._rectEnum.NONE;
  }
};
function initSelectionModes(selectionModesOption) {
  if (!selectionModesOption) {
    selectionModesOption = { row: "multiple", col: "none", rect: "none" };
  }
  return new SelectionModes({
    row: selectionModesOption.row,
    col: selectionModesOption.col,
    rect: selectionModesOption.rect
  });
}
function useSelection({
  isEditingCell,
  editCellsIsAllowed,
  selectionModes,
  keyAccessor,
  focusOffset,
  focusEscape,
  onKeyDownEnter,
  between
}) {
  const [selectedKeys, setSelectedKeys] = h2(
    ImmutableSet.empty()
  );
  const [anchor, setAnchor] = h2(null);
  const onMouseDown = (event) => {
    if (selectionModes.isNone()) {
      return;
    }
    const el = event.currentTarget;
    const key = keyAccessor(el);
    if (isEditingCell) {
      if (el.classList.contains(CellStateClassEnum[CellStateEnum.Editing])) {
        return;
      }
    }
    const result = performMouseDownAction(
      selectionModes,
      between,
      selectedKeys,
      event,
      key,
      anchor
    );
    if (result) {
      setSelectedKeys(result.selection);
      if (result.anchor) {
        setAnchor(key);
        el.focus();
      }
      event.preventDefault();
    }
  };
  const onKeyDown = (event) => {
    if (isEditingCell) {
      return;
    }
    if (selectionModes.isNone()) {
      return;
    }
    const el = event.currentTarget;
    const key = keyAccessor(el);
    const selected = selectedKeys.has(key);
    if (event.key === "Escape") {
      focusEscape(el);
      event.preventDefault();
      return;
    }
    if (selectionModes.row === SelectionModes._rowEnum.SINGLE) {
      if (event.key === " " || event.key === "Enter") {
        event.preventDefault();
        if (editCellsIsAllowed && event.key === "Enter") {
          onKeyDownEnter(el);
        } else {
          if (selectedKeys.has(key)) {
            setSelectedKeys(ImmutableSet.empty());
          } else {
            setSelectedKeys(ImmutableSet.just(key));
          }
        }
      } else if (event.key === "ArrowUp" || event.key === "ArrowDown") {
        const targetKey = focusOffset(key, event.key === "ArrowUp" ? -1 : 1);
        if (targetKey) {
          event.preventDefault();
          if (selected) {
            setSelectedKeys(ImmutableSet.just(targetKey));
          }
        }
      }
    } else if (selectionModes.row === SelectionModes._rowEnum.MULTIPLE) {
      if (event.key === " " || event.key === "Enter") {
        event.preventDefault();
        if (editCellsIsAllowed && event.key === "Enter") {
          onKeyDownEnter(el);
        } else {
          setSelectedKeys(selectedKeys.toggle(key));
        }
      } else if (event.key === "ArrowUp" || event.key === "ArrowDown") {
        if (focusOffset(key, event.key === "ArrowUp" ? -1 : 1)) {
          event.preventDefault();
        }
      }
    }
  };
  const selection = {
    has(key) {
      return selectedKeys.has(key);
    },
    set(key, selected) {
      if (selected) {
        setSelectedKeys(selectedKeys.add(key));
      } else {
        setSelectedKeys(selectedKeys.delete(key));
      }
    },
    setMultiple(keyArr) {
      setSelectedKeys(ImmutableSet.just(...keyArr));
    },
    clear() {
      setSelectedKeys(selectedKeys.clear());
    },
    keys() {
      return selectedKeys;
    },
    itemHandlers() {
      return { onMouseDown, onKeyDown };
    },
    focusOffset
  };
  return selection;
}
var isMac = /^mac/i.test(
  window.navigator.userAgentData?.platform ?? window.navigator.platform
);
function performMouseDownAction(selectionModes, between, selectedKeys, event, key, anchor) {
  const { shiftKey, altKey } = event;
  const ctrlKey = isMac ? event.metaKey : event.ctrlKey;
  const metaKey = isMac ? event.ctrlKey : event.metaKey;
  if (metaKey || altKey) {
    return null;
  }
  if (selectionModes.row === SelectionModes._rowEnum.NONE) {
    return null;
  } else if (selectionModes.row === SelectionModes._rowEnum.SINGLE) {
    if (ctrlKey && !shiftKey) {
      if (selectedKeys.has(key)) {
        return { selection: ImmutableSet.empty(), anchor: true };
      } else {
        return { selection: ImmutableSet.just(key), anchor: true };
      }
    } else {
      return { selection: ImmutableSet.just(key), anchor: true };
    }
  } else if (selectionModes.row === SelectionModes._rowEnum.MULTIPLE) {
    if (shiftKey && ctrlKey) {
      if (anchor !== null && between) {
        const toSelect = between(anchor, key);
        return { selection: selectedKeys.add(...toSelect) };
      }
    } else if (ctrlKey) {
      return { selection: selectedKeys.toggle(key), anchor: true };
    } else if (shiftKey) {
      if (anchor !== null && between) {
        const toSelect = between(anchor, key);
        return { selection: ImmutableSet.just(...toSelect) };
      }
    } else {
      return { selection: ImmutableSet.just(key), anchor: true };
    }
  } else {
    throw new Error(`Unsupported row selection mode: ${selectionModes.row}`);
  }
  return null;
}

// data-frame/sort.ts
function useSort({
  getColDefs
}) {
  const [sorting, setSorting] = h2([]);
  return {
    sorting,
    sortTableStateOptions: {
      sorting
    },
    sortTableOptions: {
      onSortingChange: (sortUpdater) => {
        const newSorting = typeof sortUpdater === "function" ? sortUpdater(sorting) : sortUpdater;
        const coldefs = getColDefs();
        const htmlColumnsSet = new Set(
          coldefs.filter((col) => col.meta.isHtmlColumn).map((col) => col.header)
        );
        const filteredSort = htmlColumnsSet.size == 0 ? newSorting : newSorting.filter((sort) => {
          return !htmlColumnsSet.has(sort.id);
        });
        setSorting(filteredSort);
      },
      getSortedRowModel: getSortedRowModel()
    },
    setSorting
  };
}

// data-frame/sort-arrows.tsx
var sortClassName = "sort-arrow";
var sortCommonProps = {
  viewBox: [-1, -1, 2, 2].map((x4) => x4 * 1.4).join(" "),
  width: "100%",
  height: "100%",
  style: { paddingLeft: "3px" }
};
var sortPathCommonProps = {
  stroke: "#333333",
  strokeWidth: "0.6",
  fill: "transparent"
};
var sortArrowUp = /* @__PURE__ */ Rn.createElement(
  "svg",
  {
    xmlns: "http://www.w3.org/2000/svg",
    ...{ ...sortCommonProps, className: `${sortClassName} sort-arrow-up` }
  },
  /* @__PURE__ */ Rn.createElement(
    "path",
    {
      d: "M -1 0.5 L 0 -0.5 L 1 0.5",
      ...sortPathCommonProps,
      strokeLinecap: "round"
    }
  )
);
var sortArrowDown = /* @__PURE__ */ Rn.createElement(
  "svg",
  {
    xmlns: "http://www.w3.org/2000/svg",
    ...{ ...sortCommonProps, className: `${sortClassName} sort-arrow-down` }
  },
  /* @__PURE__ */ Rn.createElement(
    "path",
    {
      d: "M -1 -0.5 L 0 0.5 L 1 -0.5",
      ...sortPathCommonProps,
      strokeLinecap: "round"
    }
  )
);
var SortArrow = ({ direction }) => {
  if (!direction) {
    return null;
  }
  if (direction === "asc") {
    return sortArrowUp;
  }
  if (direction === "desc") {
    return sortArrowDown;
  }
  throw new Error(`Unexpected sort direction: '${direction}'`);
};

// data-frame/style-info.ts
enableMapSet();
var makeStyleInfoMapKey = ({
  location,
  rowIndex,
  columnIndex
}) => {
  return `[${location}, ${rowIndex}, ${columnIndex}]`;
};
var useStyleInfoMap = ({
  initStyleInfos,
  nrow,
  ncol
}) => {
  const [styleInfoMap, setStyleInfoMap] = i3(
    /* @__PURE__ */ new Map()
  );
  const setStyleInfo = q2(
    (styleInfo) => {
      const { location, rows, cols } = styleInfo;
      setStyleInfoMap((draft) => {
        const rowArr = rows ?? Array.from({ length: nrow }, (_3, i4) => i4);
        const colArr = cols ?? Array.from({ length: ncol }, (_3, j4) => j4);
        for (const rowIndex of rowArr) {
          for (const columnIndex of colArr) {
            const key = makeStyleInfoMapKey({
              location,
              rowIndex,
              columnIndex
            });
            const prevObj = draft.get(key) ?? { style: {}, class: void 0 };
            let newClass = void 0;
            if (prevObj.class) {
              if (styleInfo.class) {
                newClass = `${prevObj.class} ${styleInfo.class}`;
              } else {
                newClass = prevObj.class;
              }
            } else {
              if (styleInfo.class) {
                newClass = styleInfo.class;
              } else {
                newClass = void 0;
              }
            }
            draft.set(key, {
              location,
              rowIndex,
              columnIndex,
              style: {
                ...prevObj.style,
                ...styleInfo.style
              },
              class: newClass
            });
          }
        }
      });
    },
    [ncol, nrow, setStyleInfoMap]
  );
  const resetStyleInfos = q2(() => {
    setStyleInfoMap((draft) => {
      draft.clear();
    });
  }, [setStyleInfoMap]);
  const setStyleInfos = q2(
    (styleInfos) => {
      resetStyleInfos();
      for (const styleInfo of styleInfos) {
        setStyleInfo(styleInfo);
      }
    },
    [setStyleInfo, resetStyleInfos]
  );
  y2(() => {
    setStyleInfos(initStyleInfos);
  }, [initStyleInfos, setStyleInfos]);
  return {
    styleInfoMap,
    setStyleInfo,
    setStyleInfos,
    resetStyleInfos
  };
};
var getCellStyle = (x4, location, rowIndex, columnIndex) => {
  const key = makeStyleInfoMapKey({ location, rowIndex, columnIndex });
  const obj = x4.get(key);
  return {
    cellStyle: obj?.style,
    cellClassName: obj?.class
  };
};
var cssStringToObjDomElement = document.createElement("cssStringToObj");

// data-frame/styles.scss
var styles_default = `
/*
 *
 * # Variables
 *
 */
shiny-data-frame {
  --shiny-datagrid-font-size: 0.9em;
  --shiny-datagrid-padding-x: 0.5em;
  --shiny-datagrid-padding-y: 0.3em;
  --shiny-datagrid-padding: var(--shiny-datagrid-padding-y) var(--shiny-datagrid-padding-x);
  --shiny-datagrid-grid-header-bgcolor: var(--bs-light, #eee);
  --shiny-datagrid-grid-header-gridlines-color: var(--bs-border-color, #ccc);
  --shiny-datagrid-grid-header-gridlines-style: solid;
  --shiny-datagrid-grid-gridlines-color: var(--bs-border-color, #ccc);
  --shiny-datagrid-grid-gridlines-style: solid;
  --shiny-datagrid-table-header-bottom-border: 1px solid;
  --shiny-datagrid-table-top-border: 1px solid;
  --shiny-datagrid-table-bottom-border: 1px solid;
  --shiny-datagrid-grid-body-hover-bgcolor: var(--shiny-datagrid-grid-header-bgcolor);
  --shiny-datagrid-grid-body-selected-bgcolor: #b4d5fe;
  --shiny-datagrid-grid-body-selected-color: var(--bs-dark);
  --shiny-datagrid-grid-header-selected-bgcolor: color-mix(
    in srgb,
    var(--shiny-datagrid-grid-header-bgcolor) 30%,
    var(--shiny-datagrid-grid-body-selected-bgcolor)
  );
  --shiny-datagrid-table-cell-edit-background-color: var(--bs-body-bg);
  --shiny-datagrid-table-cell-edit-success-border-color: color-mix(in srgb, var(--bs-success) 20%, transparent);
  --shiny-datagrid-table-cell-edit-success-border-style: var(--shiny-datagrid-grid-gridlines-style);
  --shiny-datagrid-table-cell-edit-success-bgcolor: color-mix(in srgb, var(--bs-success) 10%, transparent);
  --shiny-datagrid-table-cell-edit-failure-border-color: color-mix(in srgb, var(--bs-danger) 40%, transparent);
  --shiny-datagrid-table-cell-edit-failure-border-style: var(--shiny-datagrid-grid-gridlines-style);
  --shiny-datagrid-table-cell-edit-failure-bgcolor: color-mix(in srgb, var(--bs-danger) 10%, transparent);
  --shiny-datagrid-table-cell-edit-saving-color: var(--bs-gray-500);
}

/*
 *
 * # BASE STYLES
 *
 */
shiny-data-frame *,
shiny-data-frame *::before,
shiny-data-frame *::after {
  box-sizing: border-box;
}

shiny-data-frame .shiny-data-grid svg.sort-arrow {
  display: inline-block;
  width: 0.85em;
  height: 0.85em;
  margin-bottom: 0.15em;
}

shiny-data-frame .shiny-data-grid {
  max-width: 100%;
  height: auto;
}
shiny-data-frame .shiny-data-grid.scrolling {
  height: 500px;
}
shiny-data-frame .shiny-data-grid > table {
  border-collapse: separate;
  border-spacing: 0;
}
shiny-data-frame .shiny-data-grid > table > thead {
  position: sticky;
  top: 0;
}
shiny-data-frame .shiny-data-grid > table > thead > tr > th {
  text-align: left;
  white-space: nowrap;
}
shiny-data-frame .shiny-data-grid > table > thead > tr > th:focus-visible {
  outline: 5px auto Highlight;
  outline: 5px auto -webkit-focus-ring-color;
}
shiny-data-frame .shiny-data-grid > table.filtering > thead > tr:nth-last-child(2) > th {
  border-bottom: none;
}
shiny-data-frame .shiny-data-grid > table.filtering > thead > tr.filters > th {
  font-weight: unset;
  padding-top: 0;
  /* Slight boost to bottom padding */
  padding-bottom: var(--shiny-datagrid-padding-x);
}
shiny-data-frame .shiny-data-grid > table.filtering > thead > tr.filters > th > input {
  width: 100%;
}

shiny-data-frame .shiny-data-grid > .shiny-data-grid-summary {
  font-size: var(--shiny-datagrid-font-size);
  padding-top: 0.3em;
}

/*
 *
 * # DATATABLE STYLES
 *
 */
shiny-data-frame .shiny-data-grid.shiny-data-grid-table {
  border-top: var(--shiny-datagrid-table-top-border);
}
shiny-data-frame .shiny-data-grid.shiny-data-grid-table.scrolling {
  border-bottom: var(--shiny-datagrid-table-bottom-border);
}
shiny-data-frame .shiny-data-grid.shiny-data-grid-table > table > thead > tr:last-child > th {
  border-bottom: var(--shiny-datagrid-table-header-bottom-border);
}
shiny-data-frame .shiny-data-grid.shiny-data-grid-table > table > tbody > tr[aria-selected=true] {
  --shiny-datagrid-grid-gridlines-color: var(--shiny-datagrid-grid-body-selected-bgcolor);
  background-color: var(--shiny-datagrid-grid-body-selected-bgcolor);
  color: var(--shiny-datagrid-grid-body-selected-color);
}
shiny-data-frame .shiny-data-grid.shiny-data-grid-table > table > tbody > tr[aria-selected=true] td {
  background-color: var(--shiny-datagrid-grid-body-selected-bgcolor);
  color: var(--shiny-datagrid-grid-body-selected-color);
}

/*
 *
 * # GRID STYLES
 *
 */
shiny-data-frame .shiny-data-grid.shiny-data-grid-grid > table {
  font-size: var(--shiny-datagrid-font-size);
}
shiny-data-frame .shiny-data-grid.shiny-data-grid-grid > table > thead > tr > th,
shiny-data-frame .shiny-data-grid.shiny-data-grid-grid > table > thead > tr > td {
  background-color: var(--shiny-datagrid-grid-header-bgcolor);
  padding: var(--shiny-datagrid-padding);
}
shiny-data-frame .shiny-data-grid.shiny-data-grid-grid > table > tbody > tr:focus-visible {
  outline: 5px auto Highlight;
  outline: 5px auto -webkit-focus-ring-color;
}
shiny-data-frame .shiny-data-grid.shiny-data-grid-grid > table > tbody > tr:hover {
  --shiny-datagrid-grid-gridlines-color: inherit;
  background-color: var(--shiny-datagrid-grid-body-hover-bgcolor);
}
shiny-data-frame .shiny-data-grid.shiny-data-grid-grid > table > tbody > tr[aria-selected=true] {
  background-color: var(--shiny-datagrid-grid-body-selected-bgcolor);
  color: var(--shiny-datagrid-grid-body-selected-color);
}
shiny-data-frame .shiny-data-grid.shiny-data-grid-grid > table > tbody > tr > td {
  padding: var(--shiny-datagrid-padding);
}
shiny-data-frame .shiny-data-grid.shiny-data-grid-grid > table > tbody > tr:not([aria-selected=true]) > td.row-number {
  background-color: var(--shiny-datagrid-grid-header-bgcolor);
}
shiny-data-frame .shiny-data-grid.shiny-data-grid-grid > table > tbody > tr[aria-selected=true] > td.row-number {
  background-color: var(--shiny-datagrid-grid-header-selected-bgcolor);
}

/* ## Grid borders */
shiny-data-frame .shiny-data-grid.shiny-data-grid-grid > table {
  border-collapse: separate;
}
shiny-data-frame .shiny-data-grid.shiny-data-grid-grid > table > thead > tr:first-child > th {
  border-top-style: var(--shiny-datagrid-grid-gridlines-style);
}
shiny-data-frame .shiny-data-grid.shiny-data-grid-grid > table > thead > tr > th {
  border: 1px var(--shiny-datagrid-grid-gridlines-style) var(--shiny-datagrid-grid-header-gridlines-color);
  border-top-style: none;
  border-left-style: none;
}
shiny-data-frame .shiny-data-grid.shiny-data-grid-grid > table > thead > tr > th:first-child {
  border-left-style: var(--shiny-datagrid-grid-gridlines-style);
}
shiny-data-frame .shiny-data-grid.shiny-data-grid-grid > table > tbody > tr > td {
  border: 1px var(--shiny-datagrid-grid-gridlines-style) var(--shiny-datagrid-grid-gridlines-color);
  border-top-style: none;
  border-left-style: none;
}
shiny-data-frame .shiny-data-grid.shiny-data-grid-grid > table > tbody > tr > td:first-child {
  border-left-style: var(--shiny-datagrid-grid-gridlines-style);
}
shiny-data-frame .shiny-data-grid.shiny-data-grid-grid.scrolling {
  border: var(--shiny-datagrid-grid-gridlines-style) 1px var(--shiny-datagrid-grid-header-gridlines-color);
}
shiny-data-frame .shiny-data-grid.shiny-data-grid-grid.scrolling > table > thead > tr:first-child > th {
  border-top-style: none;
}
shiny-data-frame .shiny-data-grid.shiny-data-grid-grid.scrolling > table > tbody > tr:last-child > td {
  border-bottom-style: none;
}
shiny-data-frame .shiny-data-grid.shiny-data-grid-grid.scrolling > table > thead > tr > th:first-child,
shiny-data-frame .shiny-data-grid.shiny-data-grid-grid.scrolling > table > tbody > tr > td:first-child {
  border-left-style: none;
}
shiny-data-frame .shiny-data-grid.shiny-data-grid-grid.scrolling > table > thead > tr > th:last-child,
shiny-data-frame .shiny-data-grid.shiny-data-grid-grid.scrolling > table > tbody > tr > td:last-child {
  border-right-style: none;
}

/*
 *
 * # FILLING LAYOUT STYLES
 *
 */
/* Center the table when inside of a card */
.card-body shiny-data-frame .shiny-data-grid {
  margin-left: auto;
  margin-right: auto;
}

/* When .shiny-data-grid is not scrolling, the containers shouldn't flex */
shiny-data-frame:has(> div > .shiny-data-grid:not(.scrolling)) {
  flex: 0 0 auto;
}
shiny-data-frame > div:has(> .shiny-data-grid:not(.scrolling)) {
  flex: 0 0 auto;
}

shiny-data-frame .table-corner {
  width: 0;
  min-width: 25px;
}

/*
 *
 * # CELL EDITING STYLES
 *
 */
shiny-data-frame .shiny-data-grid > table > tbody > tr > td.cell-edit-editing {
  color: transparent;
  position: relative;
}
shiny-data-frame .shiny-data-grid > table > tbody > tr > td.cell-edit-editing :not(textarea) {
  visibility: hidden;
}
shiny-data-frame .shiny-data-grid > table > tbody > tr > td.cell-edit-editing > textarea {
  position: absolute;
  padding: var(--shiny-datagrid-padding);
  background-color: var(--shiny-datagrid-table-cell-edit-background-color);
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border: none;
  resize: none;
}

shiny-data-frame .shiny-data-grid > table > tbody > tr > td.cell-html {
  cursor: default;
}
shiny-data-frame .shiny-data-grid > table > tbody > tr > td.cell-editable {
  cursor: text;
}
shiny-data-frame .shiny-data-grid > table > tbody > tr > td.cell-edit-saving {
  color: var(--shiny-datagrid-table-cell-edit-saving-color);
  font-style: var(--shiny-datagrid-table-cell-edit-saving-font-style);
}
shiny-data-frame .shiny-data-grid > table > tbody > tr > td.cell-edit-failure {
  outline: 2px var(--shiny-datagrid-table-cell-edit-failure-border-style) var(--shiny-datagrid-table-cell-edit-failure-border-color);
  background-color: var(--shiny-datagrid-table-cell-edit-failure-bgcolor);
}`;

// data-frame/tabindex-group.ts
function useTabindexGroup(container, focusableItems, extraPadding) {
  const [tabIndex, setTabIndex] = h2(0);
  const onFocus = Rn.useCallback(
    (event) => {
      setTabIndex(-1);
      if (event.target !== event.currentTarget) {
        return;
      }
      findFirstItemInView(container, focusableItems(), extraPadding)?.focus();
    },
    [container, focusableItems, extraPadding]
  );
  const onBlur = Rn.useCallback(
    (event) => {
      setTabIndex(0);
    },
    []
  );
  return {
    containerTabIndex: tabIndex,
    containerHandlers: {
      onFocus,
      onBlur
    }
  };
}

// data-frame/table-summary.tsx
function useSummary(summaryTemplate, scrollContainer, virtualRows, thead, nrows) {
  return T2(() => {
    const summaryOption = summaryTemplate ?? true;
    if (!summaryOption) {
      return null;
    }
    const template = typeof summaryOption === "string" ? summaryOption : "Viewing rows {start} through {end} of {total}";
    if (!scrollContainer) {
      return null;
    }
    if (virtualRows.length === 0) {
      return null;
    }
    if (!thead)
      return null;
    const top = scrollContainer.scrollTop + thead.clientHeight;
    const bot = scrollContainer.scrollTop + scrollContainer.clientHeight;
    const [firstIndex, lastIndex] = findRangeIndex(
      top,
      bot,
      virtualRows,
      (vrow, start) => vrow.start + vrow.size / 2
    );
    if (firstIndex === null || lastIndex === null) {
      return null;
    }
    const firstRow = virtualRows[firstIndex];
    const lastRow = virtualRows[lastIndex];
    if (firstRow === void 0 || lastRow === void 0) {
      return null;
    }
    if (firstRow.index === 0 && lastRow.index === nrows - 1) {
      return null;
    }
    const summaryMessage = formatSummary(
      template,
      firstRow.index + 1,
      lastRow.index + 1,
      nrows
    );
    return /* @__PURE__ */ Rn.createElement("div", { className: "shiny-data-grid-summary" }, summaryMessage);
  }, [summaryTemplate, scrollContainer, virtualRows, thead, nrows]);
}
function findRangeIndex(start, end, items, map) {
  let first = null;
  let last = null;
  for (let i4 = 0; i4 < items.length; i4++) {
    const item = items[i4];
    if (first === null) {
      if (map(item, true) >= start) {
        first = i4;
        last = i4;
      }
    } else {
      if (map(item, false) <= end) {
        last = i4;
      } else {
        break;
      }
    }
  }
  return [first, last];
}
function formatSummary(template, start, end, total) {
  return template.replace(/\{(start|end|total)\}/g, (substr, token) => {
    if (token === "start") {
      return start + "";
    } else if (token === "end") {
      return end + "";
    } else if (token === "total") {
      return total + "";
    } else {
      return substr;
    }
  });
}

// data-frame/index.tsx
var ShinyDataGrid = ({
  id,
  gridInfo: { payload, patchInfo, selectionModes: selectionModesProp },
  bgcolor
}) => {
  const {
    columns: columnsProp,
    typeHints: typeHintsProp,
    data: tableDataProp,
    options: payloadOptions = {
      width: void 0,
      height: void 0,
      fill: false,
      styles: []
    },
    htmlDeps
  } = payload;
  const {
    width,
    height,
    fill,
    filters: withFilters,
    styles: initStyleInfos
  } = payloadOptions;
  const containerRef = A2(null);
  const theadRef = A2(null);
  const tbodyRef = A2(null);
  const [columns, setColumns] = i3(columnsProp);
  const [typeHints, setTypeHints] = i3(typeHintsProp);
  const _useStyleInfo = useStyleInfoMap({
    initStyleInfos: initStyleInfos ?? [],
    nrow: tableDataProp.length,
    ncol: columns.length
  });
  const styleInfoMap = _useStyleInfo.styleInfoMap;
  const { setStyleInfos } = _useStyleInfo;
  const _cellEditMap = useCellEditMap();
  const cellEditMap = _cellEditMap.cellEditMap;
  const setCellEditMapAtLoc = _cellEditMap.setCellEditMapAtLoc;
  const resetCellEditMap = _cellEditMap.resetCellEditMap;
  const editCellsIsAllowed = payloadOptions["editable"] === true;
  const isEditingCell = T2(() => {
    for (const cellEdit of cellEditMap.values()) {
      if (cellEdit.isEditing) {
        return true;
      }
    }
    return false;
  }, [cellEditMap]);
  const coldefs = T2(
    () => columns.map((colname, colIndex) => {
      const typeHint = typeHints?.[colIndex];
      const isHtmlColumn = typeHint?.type === "html";
      const enableSorting = isHtmlColumn ? false : void 0;
      return {
        accessorFn: (row, index) => {
          return row[colIndex];
        },
        // TODO: delegate this decision to something in filter.tsx
        filterFn: typeHint?.type === "numeric" ? "inNumberRange" : "includesString",
        header: colname,
        meta: {
          colIndex,
          isHtmlColumn,
          typeHint
        },
        cell: ({ getValue }) => {
          const ret = getValue();
          if (ret === null || ret === void 0) {
            return "";
          }
          switch (typeHint?.type) {
            case "numeric":
            case "date":
            case "datetime":
            case "duration":
            case "categorical":
            case "html":
              return ret;
            case "string":
            case "boolean":
              return String(ret);
            case "unknown":
            case "object":
              if (typeof ret === "string") {
                return ret;
              }
              return JSON.stringify(ret);
            default:
              return ret;
          }
        },
        enableSorting
      };
    }),
    [columns, typeHints]
  );
  const dataOriginal = T2(() => tableDataProp, [tableDataProp]);
  const _tableData = i3(tableDataProp);
  const tableData = _tableData[0];
  const setTableData = _tableData[1];
  const getColDefs = () => {
    return coldefs;
  };
  const _sort = useSort({ getColDefs });
  const sorting = _sort.sorting;
  const sortTableStateOptions = _sort.sortTableStateOptions;
  const sortTableOptions = _sort.sortTableOptions;
  const setSorting = _sort.setSorting;
  const {
    columnFilters,
    columnFiltersState,
    filtersTableOptions,
    setColumnFilters
  } = useFilters(withFilters);
  const updateData = q2(
    ({
      data,
      columns: columns2,
      typeHints: typeHints2
    }) => {
      setColumns(columns2);
      setTableData(data);
      setTypeHints(typeHints2);
      resetCellEditMap();
      const newTypeHintMap = /* @__PURE__ */ new Map();
      typeHints2?.forEach((hint, i4) => {
        newTypeHintMap.set(columns2[i4], hint);
      });
      const newSort = sorting.filter((sort) => newTypeHintMap.has(sort.id));
      const newColumnFilter = columnFilters.filter((filter) => {
        const typeHint = newTypeHintMap.get(filter.id);
        if (!typeHint)
          return false;
        if (typeHint.type === "numeric") {
          return filter.value === null || Array.isArray(filter.value) && filter.value.every((v3) => v3 !== null);
        }
        return typeof filter.value === "string";
      });
      setColumnFilters(newColumnFilter);
      setSorting(newSort);
    },
    [
      columnFilters,
      resetCellEditMap,
      setColumnFilters,
      setColumns,
      setSorting,
      setTableData,
      setTypeHints,
      sorting
    ]
  );
  const options = {
    data: tableData,
    columns: coldefs,
    state: {
      ...sortTableStateOptions,
      ...columnFiltersState
    },
    getCoreRowModel: getCoreRowModel(),
    ...sortTableOptions,
    ...filtersTableOptions
    // debugAll: true,
    // Provide our updateCellsData function to our table meta
    // autoResetPageIndex,
    // meta: {
    //   updateCellsData: (cellInfos: UpdateCellData[]) => {},
    // },
  };
  const table = useReactTable(options);
  const rowVirtualizer = useVirtualizer({
    count: table.getFilteredRowModel().rows.length,
    getScrollElement: () => containerRef.current,
    estimateSize: () => 31,
    overscan: 15,
    paddingStart: theadRef.current?.clientHeight ?? 0,
    // In response to https://github.com/posit-dev/py-shiny/pull/538/files#r1228352446
    // (the default scrollingDelay is 150)
    isScrollingResetDelay: 10
  });
  _2(() => {
    rowVirtualizer.scrollToOffset(0);
  }, [payload, rowVirtualizer]);
  const totalSize = rowVirtualizer.getTotalSize();
  const virtualRows = rowVirtualizer.getVirtualItems();
  const paddingTop = (virtualRows.length > 0 ? virtualRows?.[0]?.start || 0 : 0) - (theadRef.current?.clientHeight ?? 0);
  const paddingBottom = virtualRows.length > 0 ? totalSize - (virtualRows?.[virtualRows.length - 1]?.end || 0) : 0;
  const summary = useSummary(
    payloadOptions["summary"],
    containerRef?.current,
    virtualRows,
    theadRef.current,
    rowVirtualizer.options.count
  );
  const tableStyle = payloadOptions["style"] ?? "grid";
  const containerClass = tableStyle === "grid" ? "shiny-data-grid-grid" : "shiny-data-grid-table";
  const tableClass = tableStyle === "table" ? "table table-sm" : null;
  const selectionModes = initSelectionModes(selectionModesProp);
  const canSelect = !selectionModes.isNone();
  const canMultiRowSelect = selectionModes.row !== SelectionModes._rowEnum.NONE;
  const selection = useSelection({
    isEditingCell,
    editCellsIsAllowed,
    selectionModes,
    keyAccessor: (el) => {
      return el.dataset.key;
    },
    focusEscape: (el) => {
      setTimeout(() => {
        el?.blur();
        containerRef.current?.focus();
      }, 0);
    },
    focusOffset: (key, offset = 0) => {
      const rowModel = table.getSortedRowModel();
      let index = rowModel.rows.findIndex((row) => row.id === key);
      if (index < 0) {
        return null;
      }
      index += offset;
      if (index < 0 || index >= rowModel.rows.length) {
        return null;
      }
      const targetKey = rowModel.rows[index].id;
      rowVirtualizer.scrollToIndex(index);
      setTimeout(() => {
        const targetEl = containerRef.current?.querySelector(
          `[data-key='${targetKey}']`
        );
        targetEl?.focus();
      }, 0);
      return targetKey;
    },
    between: (fromKey, toKey) => findKeysBetween(table.getSortedRowModel(), fromKey, toKey),
    onKeyDownEnter: (el) => {
      const childrenNodes = Array(...el.childNodes.values()).filter((node) => {
        return node instanceof HTMLElement && node.classList.contains("cell-editable");
      });
      if (childrenNodes.length === 0)
        return;
      const firstItem = findFirstItemInView(
        containerRef.current,
        childrenNodes
      );
      if (!firstItem)
        return;
      const doubleClickEvent = new MouseEvent("dblclick", {
        bubbles: true,
        cancelable: true
      });
      firstItem.dispatchEvent(doubleClickEvent);
    }
  });
  y2(() => {
    const handleCellSelection = (event) => {
      const cellSelection = event.detail.cellSelection;
      if (cellSelection.type === "none") {
        selection.clear();
        return;
      } else if (cellSelection.type === "row") {
        selection.setMultiple(cellSelection.rows.map(String));
        return;
      } else {
        console.error("Unhandled cell selection update:", cellSelection);
      }
    };
    if (!id)
      return;
    const element = document.getElementById(id);
    if (!element)
      return;
    element.addEventListener(
      "updateCellSelection",
      handleCellSelection
    );
    return () => {
      element.removeEventListener(
        "updateCellSelection",
        handleCellSelection
      );
    };
  }, [id, selection, tableData]);
  y2(() => {
    if (!htmlDeps)
      return;
    window.Shiny.renderDependenciesAsync([...htmlDeps]);
  }, [htmlDeps]);
  y2(() => {
    const handleAddPatches = (event) => {
      const evtPatches = event.detail.patches;
      const newPatches = cellPatchPyArrToCellPatchArr(evtPatches);
      addPatchToData({
        setData: setTableData,
        newPatches,
        setCellEditMapAtLoc
      });
    };
    if (!id)
      return;
    const element = document.getElementById(id);
    if (!element)
      return;
    element.addEventListener("addPatches", handleAddPatches);
    return () => {
      element.removeEventListener(
        "addPatches",
        handleAddPatches
      );
    };
  }, [columns, id, setCellEditMapAtLoc, setSorting, setTableData]);
  y2(() => {
    const handleUpdateData = (event) => {
      const evtData = event.detail;
      updateData(evtData);
    };
    if (!id)
      return;
    const element = document.getElementById(id);
    if (!element)
      return;
    element.addEventListener("updateData", handleUpdateData);
    return () => {
      element.removeEventListener(
        "updateData",
        handleUpdateData
      );
    };
  }, [columns, id, resetCellEditMap, setTableData, updateData]);
  y2(() => {
    const handleColumnSort = (event) => {
      const shinySorting = event.detail.sort;
      const columnSorting = [];
      shinySorting.map((sort) => {
        columnSorting.push({
          id: columns[sort.col],
          desc: sort.desc
        });
      });
      setSorting(columnSorting);
    };
    if (!id)
      return;
    const element = document.getElementById(id);
    if (!element)
      return;
    element.addEventListener(
      "updateColumnSort",
      handleColumnSort
    );
    return () => {
      element.removeEventListener(
        "updateColumnSort",
        handleColumnSort
      );
    };
  }, [columns, id, setSorting]);
  y2(() => {
    const handleColumnFilter = (event) => {
      const shinyFilters = event.detail.filter;
      const columnFilters2 = [];
      shinyFilters.map((filter) => {
        columnFilters2.push({
          id: columns[filter.col],
          value: filter.value
        });
      });
      setColumnFilters(columnFilters2);
    };
    if (!id)
      return;
    const element = document.getElementById(id);
    if (!element)
      return;
    element.addEventListener(
      "updateColumnFilter",
      handleColumnFilter
    );
    return () => {
      element.removeEventListener(
        "updateColumnFilter",
        handleColumnFilter
      );
    };
  }, [columns, id, setColumnFilters]);
  y2(() => {
    const handleStyles = (event) => {
      const styles = event.detail.styles;
      setStyleInfos(styles);
    };
    if (!id)
      return;
    const element = document.getElementById(id);
    if (!element)
      return;
    element.addEventListener("updateStyles", handleStyles);
    return () => {
      element.removeEventListener(
        "updateStyles",
        handleStyles
      );
    };
  }, [id, setStyleInfos]);
  y2(() => {
    if (!id)
      return;
    let shinyValue = null;
    if (selectionModes.isNone()) {
      shinyValue = null;
    } else if (selectionModes.row !== SelectionModes._rowEnum.NONE) {
      const rowSelectionKeys = selection.keys().toList();
      const rowsById = table.getSortedRowModel().rowsById;
      shinyValue = {
        type: "row",
        rows: rowSelectionKeys.map((key) => {
          if (!(key in rowsById)) {
            return null;
          }
          return rowsById[key].index;
        }).filter((x4) => x4 !== null)
      };
    } else {
      console.error("Unhandled row selection mode:", selectionModes);
    }
    window.Shiny.setInputValue(`${id}_cell_selection`, shinyValue);
  }, [id, selection, selectionModes, table, table.getSortedRowModel]);
  y2(() => {
    if (!id)
      return;
    const shinySort = [];
    sorting.map((sortObj) => {
      const columnNum = columns.indexOf(sortObj.id);
      shinySort.push({
        col: columnNum,
        desc: sortObj.desc
      });
    });
    window.Shiny.setInputValue(`${id}_sort`, shinySort);
    window.Shiny.setInputValue(`${id}_column_sort`, shinySort);
  }, [columns, id, sorting]);
  y2(() => {
    if (!id)
      return;
    const shinyFilter = [];
    columnFilters.map((filterObj) => {
      const columnNum = columns.indexOf(filterObj.id);
      shinyFilter.push({
        col: columnNum,
        value: filterObj.value
      });
    });
    window.Shiny.setInputValue(`${id}_filter`, shinyFilter);
    window.Shiny.setInputValue(`${id}_column_filter`, shinyFilter);
  }, [id, columnFilters, columns]);
  y2(() => {
    if (!id)
      return;
    const shinyRows = table.getSortedRowModel().rows.map((row) => row.index);
    window.Shiny.setInputValue(`${id}_data_view_rows`, shinyRows);
    window.Shiny.setInputValue(`${id}_data_view_indices`, shinyRows);
  }, [
    id,
    table,
    // Update with either sorting or columnFilters update!
    sorting,
    columnFilters
  ]);
  y2(() => {
    if (!id)
      return;
    let shinyValue = null;
    if (selectionModes.row !== SelectionModes._rowEnum.NONE) {
      const rowSelectionKeys = selection.keys().toList();
      const rowsById = table.getSortedRowModel().rowsById;
      shinyValue = rowSelectionKeys.map((key) => {
        if (!(key in rowsById)) {
          return null;
        }
        return rowsById[key].index;
      }).filter((x4) => x4 !== null).sort();
    }
    window.Shiny.setInputValue(`${id}_selected_rows`, shinyValue);
  }, [id, selection, selectionModes, table]);
  const tbodyTabItems = Rn.useCallback(
    () => tbodyRef.current.querySelectorAll("[tabindex='-1']"),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [tbodyRef.current]
  );
  const tbodyTabGroup = useTabindexGroup(containerRef.current, tbodyTabItems, {
    top: theadRef.current?.clientHeight ?? 0
  });
  y2(() => {
    return () => {
      table.resetSorting();
      selection.clear();
    };
  }, [payload]);
  const headerRowCount = table.getHeaderGroups().length;
  _2(() => {
    let scrolling = tableData.length > 0;
    if (scrolling) {
      containerRef.current?.classList.add("scrolling");
      const scrollHeight = containerRef.current?.scrollHeight;
      const clientHeight = containerRef.current?.clientHeight;
      if (scrollHeight && clientHeight && scrollHeight <= clientHeight) {
        scrolling = false;
      }
    }
    containerRef.current?.classList.toggle("scrolling", scrolling);
  }, [
    tableData.length,
    containerRef.current?.scrollHeight,
    containerRef.current?.clientHeight
  ]);
  const makeHeaderKeyDown = (column) => (event) => {
    if (event.key === " " || event.key === "Enter") {
      column.toggleSorting(void 0, event.shiftKey);
    }
  };
  const measureEl = useVirtualizerMeasureWorkaround(rowVirtualizer);
  let className = `shiny-data-grid ${containerClass}`;
  if (fill) {
    className += " html-fill-item";
  }
  const includeRowNumbers = false;
  return /* @__PURE__ */ Rn.createElement(Rn.Fragment, null, /* @__PURE__ */ Rn.createElement(
    "div",
    {
      className,
      ref: containerRef,
      style: { width, height, overflow: "auto" }
    },
    /* @__PURE__ */ Rn.createElement(
      "table",
      {
        className: tableClass + (withFilters ? " filtering" : ""),
        "aria-rowcount": table.getRowCount(),
        "aria-multiselectable": canMultiRowSelect,
        style: {
          width: width === null || width === "auto" ? void 0 : "100%"
        }
      },
      /* @__PURE__ */ Rn.createElement("thead", { ref: theadRef, style: { backgroundColor: bgcolor } }, table.getHeaderGroups().map((headerGroup, i4) => /* @__PURE__ */ Rn.createElement(
        "tr",
        {
          key: headerGroup.id,
          "aria-rowindex": i4 + 1
        },
        includeRowNumbers && /* @__PURE__ */ Rn.createElement("th", { className: "table-corner" }),
        headerGroup.headers.map((header) => {
          const headerContent = header.isPlaceholder ? void 0 : /* @__PURE__ */ Rn.createElement(
            "div",
            {
              style: {
                cursor: header.column.getCanSort() ? "pointer" : void 0,
                userSelect: header.column.getCanSort() ? "none" : void 0
              }
            },
            flexRender(
              header.column.columnDef.header,
              header.getContext()
            ),
            /* @__PURE__ */ Rn.createElement(SortArrow, { direction: header.column.getIsSorted() })
          );
          return /* @__PURE__ */ Rn.createElement(
            "th",
            {
              key: header.id,
              colSpan: header.colSpan,
              style: {
                width: header.getSize()
                // When row numbers are displayed, this value is helpful instead of `width`
                // minWidth: header.getSize()
              },
              scope: "col",
              tabIndex: 0,
              onClick: header.column.getToggleSortingHandler(),
              onKeyDown: makeHeaderKeyDown(header.column),
              className: header.column.getCanSort() ? void 0 : "header-html"
            },
            headerContent
          );
        })
      )), withFilters && /* @__PURE__ */ Rn.createElement("tr", { className: "filters" }, includeRowNumbers && /* @__PURE__ */ Rn.createElement("th", { className: "table-corner" }), table.getFlatHeaders().map((header) => {
        const thKey = `filter-${header.id}`;
        return /* @__PURE__ */ Rn.createElement(
          "th",
          {
            key: thKey
          },
          /* @__PURE__ */ Rn.createElement(Filter, { header })
        );
      }))),
      /* @__PURE__ */ Rn.createElement(
        "tbody",
        {
          ref: tbodyRef,
          tabIndex: tbodyTabGroup.containerTabIndex,
          ...tbodyTabGroup.containerHandlers
        },
        paddingTop > 0 && /* @__PURE__ */ Rn.createElement("tr", { style: { height: `${paddingTop}px` } }),
        virtualRows.map((virtualRow) => {
          const row = table.getRowModel().rows[virtualRow.index];
          return row && /* @__PURE__ */ Rn.createElement(
            "tr",
            {
              key: virtualRow.key,
              "data-index": virtualRow.index,
              "aria-rowindex": virtualRow.index + headerRowCount,
              "data-key": row.id,
              ref: measureEl,
              "aria-selected": selection.has(row.id),
              tabIndex: -1,
              ...selection.itemHandlers()
            },
            includeRowNumbers && /* @__PURE__ */ Rn.createElement("td", { className: "row-number" }, row.index + 1),
            row.getVisibleCells().map((cell) => {
              const rowIndex = cell.row.index;
              const columnIndex = cell.column.columnDef.meta.colIndex;
              const [cellEditInfo, _key] = getCellEditMapObj(
                cellEditMap,
                rowIndex,
                columnIndex
              );
              const { cellStyle, cellClassName } = getCellStyle(
                styleInfoMap,
                "body",
                rowIndex,
                columnIndex
              );
              return /* @__PURE__ */ Rn.createElement(
                TableBodyCell,
                {
                  key: cell.id,
                  rowId: cell.row.id,
                  containerRef,
                  cell,
                  patchInfo,
                  editCellsIsAllowed,
                  columns,
                  coldefs,
                  rowIndex,
                  columnIndex,
                  getSortedRowModel: table.getSortedRowModel,
                  cellEditInfo,
                  cellStyle,
                  cellClassName,
                  setData: setTableData,
                  setCellEditMapAtLoc,
                  selection
                }
              );
            })
          );
        }),
        paddingBottom > 0 && /* @__PURE__ */ Rn.createElement("tr", { style: { height: `${paddingBottom}px` } })
      )
    )
  ), summary);
};
function findKeysBetween(rowModel, fromKey, toKey) {
  let fromIdx = rowModel.rows.findIndex((row) => row.id === fromKey);
  let toIdx = rowModel.rows.findIndex((row) => row.id === toKey);
  if (fromIdx < 0 || toIdx < 0) {
    return [];
  }
  if (fromIdx > toIdx) {
    [fromIdx, toIdx] = [toIdx, fromIdx];
  }
  const keys = [];
  for (let i4 = fromIdx; i4 <= toIdx; i4++) {
    keys.push(rowModel.rows[i4].id);
  }
  return keys;
}
function useVirtualizerMeasureWorkaround(rowVirtualizer) {
  const measureTodoQueue = A2([]);
  const measureElementWithRetry = q2(
    (el) => {
      if (!el) {
        return;
      }
      if (el.isConnected) {
        rowVirtualizer.measureElement(el);
      } else {
        measureTodoQueue.current.push(el);
      }
    },
    [rowVirtualizer]
  );
  _2(() => {
    if (measureTodoQueue.current.length > 0) {
      const todo = measureTodoQueue.current.splice(0);
      todo.forEach(rowVirtualizer.measureElement);
    }
  });
  return measureElementWithRetry;
}
var ShinyDataFrameOutputBinding = class extends window.Shiny.OutputBinding {
  find(scope) {
    return $(scope).find("shiny-data-frame");
  }
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  renderValue(el, data) {
    el.renderValue(data);
  }
  renderError(el, err) {
    el.classList.add("shiny-output-error");
    el.renderError(err);
  }
  clearError(el) {
    el.classList.remove("shiny-output-error");
    el.clearError();
  }
};
window.Shiny.outputBindings.register(
  new ShinyDataFrameOutputBinding(),
  "shinyDataFrame"
);
function getComputedBgColor(el) {
  if (!el) {
    return void 0;
  }
  const bgColor = getStyle(el, "background-color");
  if (!bgColor)
    return bgColor;
  const m3 = bgColor.match(
    /^rgba\(\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)\s*\)$/
  );
  if (bgColor === "transparent" || m3 && parseFloat(m3[4]) === 0) {
    const bgImage = getStyle(el, "background-image");
    if (bgImage && bgImage !== "none") {
      return void 0;
    } else {
      return getComputedBgColor(el.parentElement);
    }
  }
  return bgColor;
}
var cssTemplate = document.createElement("template");
cssTemplate.innerHTML = `<style>${styles_default}</style>`;
var ShinyDataFrameOutput = class extends HTMLElement {
  connectedCallback() {
    const [target] = [this];
    target.appendChild(cssTemplate.content.cloneNode(true));
    this.errorRoot = document.createElement("span");
    target.appendChild(this.errorRoot);
    const myDiv = document.createElement("div");
    myDiv.classList.add("html-fill-container", "html-fill-item");
    target.appendChild(myDiv);
    this.reactRoot = createRoot(myDiv);
    const dataEl = this.querySelector(
      "script.data"
    );
    if (dataEl) {
      const data = JSON.parse(dataEl.innerText);
      this.renderValue(data);
    }
  }
  renderValue(value) {
    this.clearError();
    if (!value) {
      this.reactRoot.render(null);
      return;
    }
    this.reactRoot.render(
      /* @__PURE__ */ Rn.createElement(yn, null, /* @__PURE__ */ Rn.createElement(
        ShinyDataGrid,
        {
          id: this.id,
          gridInfo: value,
          bgcolor: getComputedBgColor(this)
        }
      ))
    );
  }
  renderError(err) {
    this.reactRoot.render(null);
    this.errorRoot.innerText = err.message;
  }
  clearError() {
    this.reactRoot.render(null);
    this.errorRoot.innerText = "";
  }
};
customElements.define("shiny-data-frame", ShinyDataFrameOutput);
window.Shiny.addCustomMessageHandler(
  "shinyDataFrameMessage",
  function(message) {
    const evt = new CustomEvent(message.handler, {
      detail: message.obj
    });
    const el = document.getElementById(message.id);
    el?.dispatchEvent(evt);
  }
);
export {
  ShinyDataFrameOutput
};
/*! Bundled license information:

@tanstack/table-core/build/lib/index.mjs:
  (**
     * table-core
     *
     * Copyright (c) TanStack
     *
     * This source code is licensed under the MIT license found in the
     * LICENSE.md file in the root directory of this source tree.
     *
     * @license MIT
     *)

@tanstack/react-table/build/lib/index.mjs:
  (**
     * react-table
     *
     * Copyright (c) TanStack
     *
     * This source code is licensed under the MIT license found in the
     * LICENSE.md file in the root directory of this source tree.
     *
     * @license MIT
     *)
*/
//# sourceMappingURL=data-frame.js.map
