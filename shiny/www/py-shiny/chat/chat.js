var kt=Object.defineProperty;var Nt=Object.getOwnPropertyDescriptor;var E=(n,t,e,s)=>{for(var i=s>1?void 0:s?Nt(t,e):t,r=n.length-1,o;r>=0;r--)(o=n[r])&&(i=(s?o(t,e,i):o(i))||i);return s&&i&&kt(t,e,i),i};var B=globalThis,V=B.ShadowRoot&&(B.ShadyCSS===void 0||B.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,ct=Symbol(),lt=new WeakMap,q=class{constructor(t,e,s){if(this._$cssResult$=!0,s!==ct)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t,this.t=e}get styleSheet(){let t=this.o,e=this.t;if(V&&t===void 0){let s=e!==void 0&&e.length===1;s&&(t=lt.get(e)),t===void 0&&((this.o=t=new CSSStyleSheet).replaceSync(this.cssText),s&&lt.set(e,t))}return t}toString(){return this.cssText}},dt=n=>new q(typeof n=="string"?n:n+"",void 0,ct);var Z=(n,t)=>{if(V)n.adoptedStyleSheets=t.map(e=>e instanceof CSSStyleSheet?e:e.styleSheet);else for(let e of t){let s=document.createElement("style"),i=B.litNonce;i!==void 0&&s.setAttribute("nonce",i),s.textContent=e.cssText,n.appendChild(s)}},j=V?n=>n:n=>n instanceof CSSStyleSheet?(t=>{let e="";for(let s of t.cssRules)e+=s.cssText;return dt(e)})(n):n;var{is:Rt,defineProperty:Ot,getOwnPropertyDescriptor:It,getOwnPropertyNames:Dt,getOwnPropertySymbols:Bt,getPrototypeOf:qt}=Object,z=globalThis,ut=z.trustedTypes,Vt=ut?ut.emptyScript:"",jt=z.reactiveElementPolyfillSupport,P=(n,t)=>n,U={toAttribute(n,t){switch(t){case Boolean:n=n?Vt:null;break;case Object:case Array:n=n==null?n:JSON.stringify(n)}return n},fromAttribute(n,t){let e=n;switch(t){case Boolean:e=n!==null;break;case Number:e=n===null?null:Number(n);break;case Object:case Array:try{e=JSON.parse(n)}catch{e=null}}return e}},K=(n,t)=>!Rt(n,t),pt={attribute:!0,type:String,converter:U,reflect:!1,hasChanged:K};Symbol.metadata??=Symbol("metadata"),z.litPropertyMetadata??=new WeakMap;var m=class extends HTMLElement{static addInitializer(t){this._$Ei(),(this.l??=[]).push(t)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(t,e=pt){if(e.state&&(e.attribute=!1),this._$Ei(),this.elementProperties.set(t,e),!e.noAccessor){let s=Symbol(),i=this.getPropertyDescriptor(t,s,e);i!==void 0&&Ot(this.prototype,t,i)}}static getPropertyDescriptor(t,e,s){let{get:i,set:r}=It(this.prototype,t)??{get(){return this[e]},set(o){this[e]=o}};return{get(){return i?.call(this)},set(o){let c=i?.call(this);r.call(this,o),this.requestUpdate(t,c,s)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)??pt}static _$Ei(){if(this.hasOwnProperty(P("elementProperties")))return;let t=qt(this);t.finalize(),t.l!==void 0&&(this.l=[...t.l]),this.elementProperties=new Map(t.elementProperties)}static finalize(){if(this.hasOwnProperty(P("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(P("properties"))){let e=this.properties,s=[...Dt(e),...Bt(e)];for(let i of s)this.createProperty(i,e[i])}let t=this[Symbol.metadata];if(t!==null){let e=litPropertyMetadata.get(t);if(e!==void 0)for(let[s,i]of e)this.elementProperties.set(s,i)}this._$Eh=new Map;for(let[e,s]of this.elementProperties){let i=this._$Eu(e,s);i!==void 0&&this._$Eh.set(i,e)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(t){let e=[];if(Array.isArray(t)){let s=new Set(t.flat(1/0).reverse());for(let i of s)e.unshift(j(i))}else t!==void 0&&e.push(j(t));return e}static _$Eu(t,e){let s=e.attribute;return s===!1?void 0:typeof s=="string"?s:typeof t=="string"?t.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(t=>this.enableUpdating=t),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(t=>t(this))}addController(t){(this._$EO??=new Set).add(t),this.renderRoot!==void 0&&this.isConnected&&t.hostConnected?.()}removeController(t){this._$EO?.delete(t)}_$E_(){let t=new Map,e=this.constructor.elementProperties;for(let s of e.keys())this.hasOwnProperty(s)&&(t.set(s,this[s]),delete this[s]);t.size>0&&(this._$Ep=t)}createRenderRoot(){let t=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return Z(t,this.constructor.elementStyles),t}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(t=>t.hostConnected?.())}enableUpdating(t){}disconnectedCallback(){this._$EO?.forEach(t=>t.hostDisconnected?.())}attributeChangedCallback(t,e,s){this._$AK(t,s)}_$EC(t,e){let s=this.constructor.elementProperties.get(t),i=this.constructor._$Eu(t,s);if(i!==void 0&&s.reflect===!0){let r=(s.converter?.toAttribute!==void 0?s.converter:U).toAttribute(e,s.type);this._$Em=t,r==null?this.removeAttribute(i):this.setAttribute(i,r),this._$Em=null}}_$AK(t,e){let s=this.constructor,i=s._$Eh.get(t);if(i!==void 0&&this._$Em!==i){let r=s.getPropertyOptions(i),o=typeof r.converter=="function"?{fromAttribute:r.converter}:r.converter?.fromAttribute!==void 0?r.converter:U;this._$Em=i,this[i]=o.fromAttribute(e,r.type),this._$Em=null}}requestUpdate(t,e,s){if(t!==void 0){if(s??=this.constructor.getPropertyOptions(t),!(s.hasChanged??K)(this[t],e))return;this.P(t,e,s)}this.isUpdatePending===!1&&(this._$ES=this._$ET())}P(t,e,s){this._$AL.has(t)||this._$AL.set(t,e),s.reflect===!0&&this._$Em!==t&&(this._$Ej??=new Set).add(t)}async _$ET(){this.isUpdatePending=!0;try{await this._$ES}catch(e){Promise.reject(e)}let t=this.scheduleUpdate();return t!=null&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(let[i,r]of this._$Ep)this[i]=r;this._$Ep=void 0}let s=this.constructor.elementProperties;if(s.size>0)for(let[i,r]of s)r.wrapped!==!0||this._$AL.has(i)||this[i]===void 0||this.P(i,this[i],r)}let t=!1,e=this._$AL;try{t=this.shouldUpdate(e),t?(this.willUpdate(e),this._$EO?.forEach(s=>s.hostUpdate?.()),this.update(e)):this._$EU()}catch(s){throw t=!1,this._$EU(),s}t&&this._$AE(e)}willUpdate(t){}_$AE(t){this._$EO?.forEach(e=>e.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$EU(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(t){return!0}update(t){this._$Ej&&=this._$Ej.forEach(e=>this._$EC(e,this[e])),this._$EU()}updated(t){}firstUpdated(t){}};m.elementStyles=[],m.shadowRootOptions={mode:"open"},m[P("elementProperties")]=new Map,m[P("finalized")]=new Map,jt?.({ReactiveElement:m}),(z.reactiveElementVersions??=[]).push("2.0.4");var it=globalThis,G=it.trustedTypes,mt=G?G.createPolicy("lit-html",{createHTML:n=>n}):void 0,$t="$lit$",y=`lit$${Math.random().toFixed(9).slice(2)}$`,At="?"+y,zt=`<${At}>`,C=document,H=()=>C.createComment(""),k=n=>n===null||typeof n!="object"&&typeof n!="function",Et=Array.isArray,Kt=n=>Et(n)||typeof n?.[Symbol.iterator]=="function",Y=`[ 	
\f\r]`,L=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,gt=/-->/g,ft=/>/g,b=RegExp(`>|${Y}(?:([^\\s"'>=/]+)(${Y}*=${Y}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`,"g"),yt=/'/g,vt=/"/g,bt=/^(?:script|style|textarea|title)$/i,St=n=>(t,...e)=>({_$litType$:n,strings:t,values:e}),M=St(1),ne=St(2),g=Symbol.for("lit-noChange"),l=Symbol.for("lit-nothing"),_t=new WeakMap,S=C.createTreeWalker(C,129);function Ct(n,t){if(!Array.isArray(n)||!n.hasOwnProperty("raw"))throw Error("invalid template strings array");return mt!==void 0?mt.createHTML(t):t}var Gt=(n,t)=>{let e=n.length-1,s=[],i,r=t===2?"<svg>":"",o=L;for(let c=0;c<e;c++){let a=n[c],d,u,h=-1,p=0;for(;p<a.length&&(o.lastIndex=p,u=o.exec(a),u!==null);)p=o.lastIndex,o===L?u[1]==="!--"?o=gt:u[1]!==void 0?o=ft:u[2]!==void 0?(bt.test(u[2])&&(i=RegExp("</"+u[2],"g")),o=b):u[3]!==void 0&&(o=b):o===b?u[0]===">"?(o=i??L,h=-1):u[1]===void 0?h=-2:(h=o.lastIndex-u[2].length,d=u[1],o=u[3]===void 0?b:u[3]==='"'?vt:yt):o===vt||o===yt?o=b:o===gt||o===ft?o=L:(o=b,i=void 0);let f=o===b&&n[c+1].startsWith("/>")?" ":"";r+=o===L?a+zt:h>=0?(s.push(d),a.slice(0,h)+$t+a.slice(h)+y+f):a+y+(h===-2?c:f)}return[Ct(n,r+(n[e]||"<?>")+(t===2?"</svg>":"")),s]},N=class n{constructor({strings:t,_$litType$:e},s){let i;this.parts=[];let r=0,o=0,c=t.length-1,a=this.parts,[d,u]=Gt(t,e);if(this.el=n.createElement(d,s),S.currentNode=this.el.content,e===2){let h=this.el.content.firstChild;h.replaceWith(...h.childNodes)}for(;(i=S.nextNode())!==null&&a.length<c;){if(i.nodeType===1){if(i.hasAttributes())for(let h of i.getAttributeNames())if(h.endsWith($t)){let p=u[o++],f=i.getAttribute(h).split(y),D=/([.?@])?(.*)/.exec(p);a.push({type:1,index:r,name:D[2],strings:f,ctor:D[1]==="."?X:D[1]==="?"?tt:D[1]==="@"?et:w}),i.removeAttribute(h)}else h.startsWith(y)&&(a.push({type:6,index:r}),i.removeAttribute(h));if(bt.test(i.tagName)){let h=i.textContent.split(y),p=h.length-1;if(p>0){i.textContent=G?G.emptyScript:"";for(let f=0;f<p;f++)i.append(h[f],H()),S.nextNode(),a.push({type:2,index:++r});i.append(h[p],H())}}}else if(i.nodeType===8)if(i.data===At)a.push({type:2,index:r});else{let h=-1;for(;(h=i.data.indexOf(y,h+1))!==-1;)a.push({type:7,index:r}),h+=y.length-1}r++}}static createElement(t,e){let s=C.createElement("template");return s.innerHTML=t,s}};function x(n,t,e=n,s){if(t===g)return t;let i=s!==void 0?e._$Co?.[s]:e._$Cl,r=k(t)?void 0:t._$litDirective$;return i?.constructor!==r&&(i?._$AO?.(!1),r===void 0?i=void 0:(i=new r(n),i._$AT(n,e,s)),s!==void 0?(e._$Co??=[])[s]=i:e._$Cl=i),i!==void 0&&(t=x(n,i._$AS(n,t.values),i,s)),t}var Q=class{constructor(t,e){this._$AV=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(t){let{el:{content:e},parts:s}=this._$AD,i=(t?.creationScope??C).importNode(e,!0);S.currentNode=i;let r=S.nextNode(),o=0,c=0,a=s[0];for(;a!==void 0;){if(o===a.index){let d;a.type===2?d=new R(r,r.nextSibling,this,t):a.type===1?d=new a.ctor(r,a.name,a.strings,this,t):a.type===6&&(d=new st(r,this,t)),this._$AV.push(d),a=s[++c]}o!==a?.index&&(r=S.nextNode(),o++)}return S.currentNode=C,i}p(t){let e=0;for(let s of this._$AV)s!==void 0&&(s.strings!==void 0?(s._$AI(t,s,e),e+=s.strings.length-2):s._$AI(t[e])),e++}},R=class n{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(t,e,s,i){this.type=2,this._$AH=l,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=s,this.options=i,this._$Cv=i?.isConnected??!0}get parentNode(){let t=this._$AA.parentNode,e=this._$AM;return e!==void 0&&t?.nodeType===11&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){t=x(this,t,e),k(t)?t===l||t==null||t===""?(this._$AH!==l&&this._$AR(),this._$AH=l):t!==this._$AH&&t!==g&&this._(t):t._$litType$!==void 0?this.$(t):t.nodeType!==void 0?this.T(t):Kt(t)?this.k(t):this._(t)}S(t){return this._$AA.parentNode.insertBefore(t,this._$AB)}T(t){this._$AH!==t&&(this._$AR(),this._$AH=this.S(t))}_(t){this._$AH!==l&&k(this._$AH)?this._$AA.nextSibling.data=t:this.T(C.createTextNode(t)),this._$AH=t}$(t){let{values:e,_$litType$:s}=t,i=typeof s=="number"?this._$AC(t):(s.el===void 0&&(s.el=N.createElement(Ct(s.h,s.h[0]),this.options)),s);if(this._$AH?._$AD===i)this._$AH.p(e);else{let r=new Q(i,this),o=r.u(this.options);r.p(e),this.T(o),this._$AH=r}}_$AC(t){let e=_t.get(t.strings);return e===void 0&&_t.set(t.strings,e=new N(t)),e}k(t){Et(this._$AH)||(this._$AH=[],this._$AR());let e=this._$AH,s,i=0;for(let r of t)i===e.length?e.push(s=new n(this.S(H()),this.S(H()),this,this.options)):s=e[i],s._$AI(r),i++;i<e.length&&(this._$AR(s&&s._$AB.nextSibling,i),e.length=i)}_$AR(t=this._$AA.nextSibling,e){for(this._$AP?.(!1,!0,e);t&&t!==this._$AB;){let s=t.nextSibling;t.remove(),t=s}}setConnected(t){this._$AM===void 0&&(this._$Cv=t,this._$AP?.(t))}},w=class{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(t,e,s,i,r){this.type=1,this._$AH=l,this._$AN=void 0,this.element=t,this.name=e,this._$AM=i,this.options=r,s.length>2||s[0]!==""||s[1]!==""?(this._$AH=Array(s.length-1).fill(new String),this.strings=s):this._$AH=l}_$AI(t,e=this,s,i){let r=this.strings,o=!1;if(r===void 0)t=x(this,t,e,0),o=!k(t)||t!==this._$AH&&t!==g,o&&(this._$AH=t);else{let c=t,a,d;for(t=r[0],a=0;a<r.length-1;a++)d=x(this,c[s+a],e,a),d===g&&(d=this._$AH[a]),o||=!k(d)||d!==this._$AH[a],d===l?t=l:t!==l&&(t+=(d??"")+r[a+1]),this._$AH[a]=d}o&&!i&&this.j(t)}j(t){t===l?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,t??"")}},X=class extends w{constructor(){super(...arguments),this.type=3}j(t){this.element[this.name]=t===l?void 0:t}},tt=class extends w{constructor(){super(...arguments),this.type=4}j(t){this.element.toggleAttribute(this.name,!!t&&t!==l)}},et=class extends w{constructor(t,e,s,i,r){super(t,e,s,i,r),this.type=5}_$AI(t,e=this){if((t=x(this,t,e,0)??l)===g)return;let s=this._$AH,i=t===l&&s!==l||t.capture!==s.capture||t.once!==s.once||t.passive!==s.passive,r=t!==l&&(s===l||i);i&&this.element.removeEventListener(this.name,this,s),r&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){typeof this._$AH=="function"?this._$AH.call(this.options?.host??this.element,t):this._$AH.handleEvent(t)}},st=class{constructor(t,e,s){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=s}get _$AU(){return this._$AM._$AU}_$AI(t){x(this,t)}};var Wt=it.litHtmlPolyfillSupport;Wt?.(N,R),(it.litHtmlVersions??=[]).push("3.1.3");var xt=(n,t,e)=>{let s=e?.renderBefore??t,i=s._$litPart$;if(i===void 0){let r=e?.renderBefore??null;s._$litPart$=i=new R(t.insertBefore(H(),r),r,void 0,e??{})}return i._$AI(n),i};var v=class extends m{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){let t=super.createRenderRoot();return this.renderOptions.renderBefore??=t.firstChild,t}update(t){let e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Do=xt(e,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return g}};v._$litElement$=!0,v["finalized"]=!0,globalThis.litElementHydrateSupport?.({LitElement:v});var Ft=globalThis.litElementPolyfillSupport;Ft?.({LitElement:v});(globalThis.litElementVersions??=[]).push("4.0.5");var wt={ATTRIBUTE:1,CHILD:2,PROPERTY:3,BOOLEAN_ATTRIBUTE:4,EVENT:5,ELEMENT:6},Mt=n=>(...t)=>({_$litDirective$:n,values:t}),W=class{constructor(t){}get _$AU(){return this._$AM._$AU}_$AT(t,e,s){this._$Ct=t,this._$AM=e,this._$Ci=s}_$AS(t,e){return this.update(t,e)}update(t,e){return this.render(...e)}};var O=class extends W{constructor(t){if(super(t),this.it=l,t.type!==wt.CHILD)throw Error(this.constructor.directiveName+"() can only be used in child bindings")}render(t){if(t===l||t==null)return this._t=void 0,this.it=t;if(t===g)return t;if(typeof t!="string")throw Error(this.constructor.directiveName+"() called with a non-string value");if(t===this.it)return this._t;this.it=t;let e=[t];return e.raw=e,this._t={_$litType$:this.constructor.resultType,strings:e,values:[]}}};O.directiveName="unsafeHTML",O.resultType=1;var nt=Mt(O);var Jt={attribute:!0,type:String,converter:U,reflect:!1,hasChanged:K},Zt=(n=Jt,t,e)=>{let{kind:s,metadata:i}=e,r=globalThis.litPropertyMetadata.get(i);if(r===void 0&&globalThis.litPropertyMetadata.set(i,r=new Map),r.set(e.name,n),s==="accessor"){let{name:o}=e;return{set(c){let a=t.get.call(this);t.set.call(this,c),this.requestUpdate(o,a,n)},init(c){return c!==void 0&&this.P(o,void 0,n),c}}}if(s==="setter"){let{name:o}=e;return function(c){let a=this[o];t.call(this,c),this.requestUpdate(o,a,n)}}throw Error("Unsupported decorator location: "+s)};function _(n){return(t,e)=>typeof e=="object"?Zt(n,t,e):((s,i,r)=>{let o=i.hasOwnProperty(r);return i.constructor.createProperty(r,o?{...s,wrapped:!0}:s),o?Object.getOwnPropertyDescriptor(i,r):void 0})(n,t,e)}function rt(n,t){let e=document.createElement(n);for(let[s,i]of Object.entries(t))i!==null&&e.setAttribute(s,i);return e}var A=class extends v{createRenderRoot(){return this}};function Tt({headline:n="",message:t,status:e="warning"}){document.dispatchEvent(new CustomEvent("shiny:client-message",{detail:{headline:n,message:t,status:e}}))}var ot="shiny-chat-message",Ut="shiny-user-message",Lt="shiny-chat-messages",Ht="shiny-chat-input",Yt="shiny-chat-container",Pt={robot:'<svg fill="currentColor" class="bi bi-robot" viewBox="0 0 16 16" xmlns="http://www.w3.org/2000/svg"><path d="M6 12.5a.5.5 0 0 1 .5-.5h3a.5.5 0 0 1 0 1h-3a.5.5 0 0 1-.5-.5M3 8.062C3 6.76 4.235 5.765 5.53 5.886a26.6 26.6 0 0 0 4.94 0C11.765 5.765 13 6.76 13 8.062v1.157a.93.93 0 0 1-.765.935c-.845.147-2.34.346-4.235.346s-3.39-.2-4.235-.346A.93.93 0 0 1 3 9.219zm4.542-.827a.25.25 0 0 0-.217.068l-.92.9a25 25 0 0 1-1.871-.183.25.25 0 0 0-.068.495c.55.076 1.232.149 2.02.193a.25.25 0 0 0 .189-.071l.754-.736.847 1.71a.25.25 0 0 0 .404.062l.932-.97a25 25 0 0 0 1.922-.188.25.25 0 0 0-.068-.495c-.538.074-1.207.145-1.98.189a.25.25 0 0 0-.166.076l-.754.785-.842-1.7a.25.25 0 0 0-.182-.135"/><path d="M8.5 1.866a1 1 0 1 0-1 0V3h-2A4.5 4.5 0 0 0 1 7.5V8a1 1 0 0 0-1 1v2a1 1 0 0 0 1 1v1a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-1a1 1 0 0 0 1-1V9a1 1 0 0 0-1-1v-.5A4.5 4.5 0 0 0 10.5 3h-2zM14 7.5V13a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V7.5A3.5 3.5 0 0 1 5.5 4h5A3.5 3.5 0 0 1 14 7.5"/></svg>',dots_fade:'<svg width="24" height="24" fill="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><style>.spinner_S1WN{animation:spinner_MGfb .8s linear infinite;animation-delay:-.8s}.spinner_Km9P{animation-delay:-.65s}.spinner_JApP{animation-delay:-.5s}@keyframes spinner_MGfb{93.75%,100%{opacity:.2}}</style><circle class="spinner_S1WN" cx="4" cy="12" r="3"/><circle class="spinner_S1WN spinner_Km9P" cx="12" cy="12" r="3"/><circle class="spinner_S1WN spinner_JApP" cx="20" cy="12" r="3"/></svg>'},T=class extends A{constructor(){super(...arguments);this.content="...";this.content_type="markdown";this.streaming=!1}render(){let s=this.content.trim().length===0?Pt.dots_fade:Pt.robot;return M`
      <div class="message-icon">${nt(s)}</div>
      <shiny-markdown-stream
        content=${this.content}
        content-type=${this.content_type}
        ?streaming=${this.streaming}
        auto-scroll
        .onContentChange=${this.#e}
        .onStreamEnd=${this.#t}
      ></shiny-markdown-stream>
    `}#e(){this.streaming||this.#t()}#t(){this.querySelectorAll(".suggestion,[data-suggestion]").forEach(e=>{if(!(e instanceof HTMLElement)||e.hasAttribute("tabindex"))return;e.setAttribute("tabindex","0"),e.setAttribute("role","button");let s=e.dataset.suggestion||e.textContent;e.setAttribute("aria-label",`Use chat suggestion: ${s}`)})}};E([_()],T.prototype,"content",2),E([_()],T.prototype,"content_type",2),E([_({type:Boolean,reflect:!0})],T.prototype,"streaming",2);var J=class extends A{constructor(){super(...arguments);this.content="..."}render(){return M`
      <shiny-markdown-stream
        content=${this.content}
        content-type="semi-markdown"
      ></shiny-markdown-stream>
    `}};E([_()],J.prototype,"content",2);var at=class extends A{render(){return M``}},I=class extends A{constructor(){super(...arguments);this._disabled=!1;this.placeholder="Enter a message..."}get disabled(){return this._disabled}set disabled(e){let s=this._disabled;e!==s&&(this._disabled=e,e?this.setAttribute("disabled",""):this.removeAttribute("disabled"),this.requestUpdate("disabled",s),this.#t())}attributeChangedCallback(e,s,i){super.attributeChangedCallback(e,s,i),e==="disabled"&&(this.disabled=i!==null)}get textarea(){return this.querySelector("textarea")}get value(){return this.textarea.value}get valueIsEmpty(){return this.value.trim().length===0}get button(){return this.querySelector("button")}render(){let e='<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" class="bi bi-arrow-up-circle-fill" viewBox="0 0 16 16"><path d="M16 8A8 8 0 1 0 0 8a8 8 0 0 0 16 0m-7.5 3.5a.5.5 0 0 1-1 0V5.707L5.354 7.854a.5.5 0 1 1-.708-.708l3-3a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1-.708.708L8.5 5.707z"/></svg>';return M`
      <textarea
        id="${this.id}"
        class="form-control textarea-autoresize"
        rows="1"
        placeholder="${this.placeholder}"
        @keydown=${this.#e}
        @input=${this.#t}
        data-shiny-no-bind-input
      ></textarea>
      <button
        type="button"
        title="Send message"
        aria-label="Send message"
        @click=${this.#s}
      >
        ${nt(e)}
      </button>
    `}#e(e){e.code==="Enter"&&!e.shiftKey&&!this.valueIsEmpty&&(e.preventDefault(),this.#s())}#t(){this.button.disabled=this.disabled?!0:this.value.trim().length===0}firstUpdated(){this.#t()}#s(e=!0){if(this.valueIsEmpty||this.disabled)return;Shiny.setInputValue(this.id,this.value,{priority:"event"});let s=new CustomEvent("shiny-chat-input-sent",{detail:{content:this.value,role:"user"},bubbles:!0,composed:!0});this.dispatchEvent(s),this.setInputValue(""),this.disabled=!0,e&&this.textarea.focus()}setInputValue(e,{submit:s=!1,focus:i=!1}={}){let r=this.textarea.value;this.textarea.value=e;let o=new Event("input",{bubbles:!0,cancelable:!0});this.textarea.dispatchEvent(o),s&&(this.#s(!1),r&&this.setInputValue(r)),i&&this.textarea.focus()}};E([_()],I.prototype,"placeholder",2),E([_({type:Boolean})],I.prototype,"disabled",1);var ht=class extends A{get input(){return this.querySelector(Ht)}get messages(){return this.querySelector(Lt)}get lastMessage(){let t=this.messages.lastElementChild;return t||null}render(){return M``}firstUpdated(){this.messages&&(this.addEventListener("shiny-chat-input-sent",this.#e),this.addEventListener("shiny-chat-append-message",this.#t),this.addEventListener("shiny-chat-append-message-chunk",this.#o),this.addEventListener("shiny-chat-clear-messages",this.#a),this.addEventListener("shiny-chat-update-user-input",this.#h),this.addEventListener("shiny-chat-remove-loading-message",this.#u),this.addEventListener("click",this.#l),this.addEventListener("keydown",this.#c))}disconnectedCallback(){super.disconnectedCallback(),this.removeEventListener("shiny-chat-input-sent",this.#e),this.removeEventListener("shiny-chat-append-message",this.#t),this.removeEventListener("shiny-chat-append-message-chunk",this.#o),this.removeEventListener("shiny-chat-clear-messages",this.#a),this.removeEventListener("shiny-chat-update-user-input",this.#h),this.removeEventListener("shiny-chat-remove-loading-message",this.#u),this.removeEventListener("click",this.#l),this.removeEventListener("keydown",this.#c)}#e(t){this.#i(t.detail),this.#p()}#t(t){this.#i(t.detail)}#s(){this.#r(),this.input.disabled||(this.input.disabled=!0)}#i(t,e=!0){this.#s();let s=t.role==="user"?Ut:ot,i=rt(s,t);this.messages.appendChild(i),e&&this.#n()}#p(){let e=rt(ot,{content:"",role:"assistant"});this.messages.appendChild(e)}#r(){this.lastMessage?.content||this.lastMessage?.remove()}#o(t){this.#m(t.detail)}#m(t){t.chunk_type==="message_start"&&this.#i(t,!1);let e=this.lastMessage;if(!e)throw new Error("No messages found in the chat output");if(t.chunk_type==="message_start"){e.setAttribute("streaming","");return}let s=t.operation==="append"?e.getAttribute("content")+t.content:t.content;e.setAttribute("content",s),t.chunk_type==="message_end"&&(this.lastMessage?.removeAttribute("streaming"),this.#n())}#a(){this.messages.innerHTML=""}#h(t){let{value:e,placeholder:s,submit:i,focus:r}=t.detail;e!==void 0&&this.input.setInputValue(e,{submit:i,focus:r}),s!==void 0&&(this.input.placeholder=s)}#l(t){this.#d(t)}#c(t){(t.key==="Enter"||t.key===" ")&&this.#d(t)}#d(t){let{suggestion:e,submit:s}=this.#g(t.target);if(!e)return;t.preventDefault();let i=t.metaKey||t.ctrlKey?!0:t.altKey?!1:s;this.input.setInputValue(e,{submit:i,focus:!i})}#g(t){if(!(t instanceof HTMLElement))return{};let e=t.closest(".suggestion, [data-suggestion]");return e instanceof HTMLElement?e.classList.contains("suggestion")||e.dataset.suggestion!==void 0?{suggestion:e.dataset.suggestion||e.textContent||void 0,submit:e.classList.contains("submit")||e.dataset.suggestionSubmit===""||e.dataset.suggestionSubmit==="true"}:{}:{}}#u(){this.#r(),this.#n()}#n(){this.input.disabled=!1}};customElements.define(ot,T);customElements.define(Ut,J);customElements.define(Lt,at);customElements.define(Ht,I);customElements.define(Yt,ht);$(function(){Shiny.addCustomMessageHandler("shinyChatMessage",function(n){let t=new CustomEvent(n.handler,{detail:n.obj}),e=document.getElementById(n.id);if(!e){Tt({status:"error",message:`Unable to handle Chat() message since element with id
          ${n.id} wasn't found. Do you need to call .ui() (Express) or need a
          chat_ui('${n.id}') in the UI (Core)?
        `});return}e.dispatchEvent(t)})});
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
