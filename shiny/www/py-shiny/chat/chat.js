var Rt=Object.defineProperty;var Ot=Object.getOwnPropertyDescriptor;var m=(i,t,e,s)=>{for(var n=s>1?void 0:s?Ot(t,e):t,r=i.length-1,o;r>=0;r--)(o=i[r])&&(n=(s?o(t,e,n):o(n))||n);return s&&n&&Rt(t,e,n),n};var q=globalThis,j=q.ShadowRoot&&(q.ShadyCSS===void 0||q.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,dt=Symbol(),ct=new WeakMap,B=class{constructor(t,e,s){if(this._$cssResult$=!0,s!==dt)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t,this.t=e}get styleSheet(){let t=this.o,e=this.t;if(j&&t===void 0){let s=e!==void 0&&e.length===1;s&&(t=ct.get(e)),t===void 0&&((this.o=t=new CSSStyleSheet).replaceSync(this.cssText),s&&ct.set(e,t))}return t}toString(){return this.cssText}},ut=i=>new B(typeof i=="string"?i:i+"",void 0,dt);var X=(i,t)=>{if(j)i.adoptedStyleSheets=t.map(e=>e instanceof CSSStyleSheet?e:e.styleSheet);else for(let e of t){let s=document.createElement("style"),n=q.litNonce;n!==void 0&&s.setAttribute("nonce",n),s.textContent=e.cssText,i.appendChild(s)}},z=j?i=>i:i=>i instanceof CSSStyleSheet?(t=>{let e="";for(let s of t.cssRules)e+=s.cssText;return ut(e)})(i):i;var{is:It,defineProperty:Dt,getOwnPropertyDescriptor:Vt,getOwnPropertyNames:qt,getOwnPropertySymbols:Bt,getPrototypeOf:jt}=Object,G=globalThis,pt=G.trustedTypes,zt=pt?pt.emptyScript:"",Gt=G.reactiveElementPolyfillSupport,P=(i,t)=>i,L={toAttribute(i,t){switch(t){case Boolean:i=i?zt:null;break;case Object:case Array:i=i==null?i:JSON.stringify(i)}return i},fromAttribute(i,t){let e=i;switch(t){case Boolean:e=i!==null;break;case Number:e=i===null?null:Number(i);break;case Object:case Array:try{e=JSON.parse(i)}catch{e=null}}return e}},K=(i,t)=>!It(i,t),mt={attribute:!0,type:String,converter:L,reflect:!1,hasChanged:K};Symbol.metadata??=Symbol("metadata"),G.litPropertyMetadata??=new WeakMap;var f=class extends HTMLElement{static addInitializer(t){this._$Ei(),(this.l??=[]).push(t)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(t,e=mt){if(e.state&&(e.attribute=!1),this._$Ei(),this.elementProperties.set(t,e),!e.noAccessor){let s=Symbol(),n=this.getPropertyDescriptor(t,s,e);n!==void 0&&Dt(this.prototype,t,n)}}static getPropertyDescriptor(t,e,s){let{get:n,set:r}=Vt(this.prototype,t)??{get(){return this[e]},set(o){this[e]=o}};return{get(){return n?.call(this)},set(o){let c=n?.call(this);r.call(this,o),this.requestUpdate(t,c,s)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)??mt}static _$Ei(){if(this.hasOwnProperty(P("elementProperties")))return;let t=jt(this);t.finalize(),t.l!==void 0&&(this.l=[...t.l]),this.elementProperties=new Map(t.elementProperties)}static finalize(){if(this.hasOwnProperty(P("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(P("properties"))){let e=this.properties,s=[...qt(e),...Bt(e)];for(let n of s)this.createProperty(n,e[n])}let t=this[Symbol.metadata];if(t!==null){let e=litPropertyMetadata.get(t);if(e!==void 0)for(let[s,n]of e)this.elementProperties.set(s,n)}this._$Eh=new Map;for(let[e,s]of this.elementProperties){let n=this._$Eu(e,s);n!==void 0&&this._$Eh.set(n,e)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(t){let e=[];if(Array.isArray(t)){let s=new Set(t.flat(1/0).reverse());for(let n of s)e.unshift(z(n))}else t!==void 0&&e.push(z(t));return e}static _$Eu(t,e){let s=e.attribute;return s===!1?void 0:typeof s=="string"?s:typeof t=="string"?t.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(t=>this.enableUpdating=t),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(t=>t(this))}addController(t){(this._$EO??=new Set).add(t),this.renderRoot!==void 0&&this.isConnected&&t.hostConnected?.()}removeController(t){this._$EO?.delete(t)}_$E_(){let t=new Map,e=this.constructor.elementProperties;for(let s of e.keys())this.hasOwnProperty(s)&&(t.set(s,this[s]),delete this[s]);t.size>0&&(this._$Ep=t)}createRenderRoot(){let t=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return X(t,this.constructor.elementStyles),t}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(t=>t.hostConnected?.())}enableUpdating(t){}disconnectedCallback(){this._$EO?.forEach(t=>t.hostDisconnected?.())}attributeChangedCallback(t,e,s){this._$AK(t,s)}_$EC(t,e){let s=this.constructor.elementProperties.get(t),n=this.constructor._$Eu(t,s);if(n!==void 0&&s.reflect===!0){let r=(s.converter?.toAttribute!==void 0?s.converter:L).toAttribute(e,s.type);this._$Em=t,r==null?this.removeAttribute(n):this.setAttribute(n,r),this._$Em=null}}_$AK(t,e){let s=this.constructor,n=s._$Eh.get(t);if(n!==void 0&&this._$Em!==n){let r=s.getPropertyOptions(n),o=typeof r.converter=="function"?{fromAttribute:r.converter}:r.converter?.fromAttribute!==void 0?r.converter:L;this._$Em=n,this[n]=o.fromAttribute(e,r.type),this._$Em=null}}requestUpdate(t,e,s){if(t!==void 0){if(s??=this.constructor.getPropertyOptions(t),!(s.hasChanged??K)(this[t],e))return;this.P(t,e,s)}this.isUpdatePending===!1&&(this._$ES=this._$ET())}P(t,e,s){this._$AL.has(t)||this._$AL.set(t,e),s.reflect===!0&&this._$Em!==t&&(this._$Ej??=new Set).add(t)}async _$ET(){this.isUpdatePending=!0;try{await this._$ES}catch(e){Promise.reject(e)}let t=this.scheduleUpdate();return t!=null&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(let[n,r]of this._$Ep)this[n]=r;this._$Ep=void 0}let s=this.constructor.elementProperties;if(s.size>0)for(let[n,r]of s)r.wrapped!==!0||this._$AL.has(n)||this[n]===void 0||this.P(n,this[n],r)}let t=!1,e=this._$AL;try{t=this.shouldUpdate(e),t?(this.willUpdate(e),this._$EO?.forEach(s=>s.hostUpdate?.()),this.update(e)):this._$EU()}catch(s){throw t=!1,this._$EU(),s}t&&this._$AE(e)}willUpdate(t){}_$AE(t){this._$EO?.forEach(e=>e.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$EU(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(t){return!0}update(t){this._$Ej&&=this._$Ej.forEach(e=>this._$EC(e,this[e])),this._$EU()}updated(t){}firstUpdated(t){}};f.elementStyles=[],f.shadowRootOptions={mode:"open"},f[P("elementProperties")]=new Map,f[P("finalized")]=new Map,Gt?.({ReactiveElement:f}),(G.reactiveElementVersions??=[]).push("2.0.4");var ot=globalThis,W=ot.trustedTypes,gt=W?W.createPolicy("lit-html",{createHTML:i=>i}):void 0,At="$lit$",A=`lit$${Math.random().toFixed(9).slice(2)}$`,Et="?"+A,Kt=`<${Et}>`,C=document,k=()=>C.createComment(""),N=i=>i===null||typeof i!="object"&&typeof i!="function",bt=Array.isArray,Wt=i=>bt(i)||typeof i?.[Symbol.iterator]=="function",tt=`[ 	
\f\r]`,H=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,ft=/-->/g,yt=/>/g,b=RegExp(`>|${tt}(?:([^\\s"'>=/]+)(${tt}*=${tt}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`,"g"),vt=/'/g,_t=/"/g,St=/^(?:script|style|textarea|title)$/i,Ct=i=>(t,...e)=>({_$litType$:i,strings:t,values:e}),x=Ct(1),oe=Ct(2),y=Symbol.for("lit-noChange"),l=Symbol.for("lit-nothing"),$t=new WeakMap,S=C.createTreeWalker(C,129);function xt(i,t){if(!Array.isArray(i)||!i.hasOwnProperty("raw"))throw Error("invalid template strings array");return gt!==void 0?gt.createHTML(t):t}var Ft=(i,t)=>{let e=i.length-1,s=[],n,r=t===2?"<svg>":"",o=H;for(let c=0;c<e;c++){let a=i[c],d,u,h=-1,g=0;for(;g<a.length&&(o.lastIndex=g,u=o.exec(a),u!==null);)g=o.lastIndex,o===H?u[1]==="!--"?o=ft:u[1]!==void 0?o=yt:u[2]!==void 0?(St.test(u[2])&&(n=RegExp("</"+u[2],"g")),o=b):u[3]!==void 0&&(o=b):o===b?u[0]===">"?(o=n??H,h=-1):u[1]===void 0?h=-2:(h=o.lastIndex-u[2].length,d=u[1],o=u[3]===void 0?b:u[3]==='"'?_t:vt):o===_t||o===vt?o=b:o===ft||o===yt?o=H:(o=b,n=void 0);let _=o===b&&i[c+1].startsWith("/>")?" ":"";r+=o===H?a+Kt:h>=0?(s.push(d),a.slice(0,h)+At+a.slice(h)+A+_):a+A+(h===-2?c:_)}return[xt(i,r+(i[e]||"<?>")+(t===2?"</svg>":"")),s]},R=class i{constructor({strings:t,_$litType$:e},s){let n;this.parts=[];let r=0,o=0,c=t.length-1,a=this.parts,[d,u]=Ft(t,e);if(this.el=i.createElement(d,s),S.currentNode=this.el.content,e===2){let h=this.el.content.firstChild;h.replaceWith(...h.childNodes)}for(;(n=S.nextNode())!==null&&a.length<c;){if(n.nodeType===1){if(n.hasAttributes())for(let h of n.getAttributeNames())if(h.endsWith(At)){let g=u[o++],_=n.getAttribute(h).split(A),V=/([.?@])?(.*)/.exec(g);a.push({type:1,index:r,name:V[2],strings:_,ctor:V[1]==="."?st:V[1]==="?"?nt:V[1]==="@"?it:T}),n.removeAttribute(h)}else h.startsWith(A)&&(a.push({type:6,index:r}),n.removeAttribute(h));if(St.test(n.tagName)){let h=n.textContent.split(A),g=h.length-1;if(g>0){n.textContent=W?W.emptyScript:"";for(let _=0;_<g;_++)n.append(h[_],k()),S.nextNode(),a.push({type:2,index:++r});n.append(h[g],k())}}}else if(n.nodeType===8)if(n.data===Et)a.push({type:2,index:r});else{let h=-1;for(;(h=n.data.indexOf(A,h+1))!==-1;)a.push({type:7,index:r}),h+=A.length-1}r++}}static createElement(t,e){let s=C.createElement("template");return s.innerHTML=t,s}};function M(i,t,e=i,s){if(t===y)return t;let n=s!==void 0?e._$Co?.[s]:e._$Cl,r=N(t)?void 0:t._$litDirective$;return n?.constructor!==r&&(n?._$AO?.(!1),r===void 0?n=void 0:(n=new r(i),n._$AT(i,e,s)),s!==void 0?(e._$Co??=[])[s]=n:e._$Cl=n),n!==void 0&&(t=M(i,n._$AS(i,t.values),n,s)),t}var et=class{constructor(t,e){this._$AV=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(t){let{el:{content:e},parts:s}=this._$AD,n=(t?.creationScope??C).importNode(e,!0);S.currentNode=n;let r=S.nextNode(),o=0,c=0,a=s[0];for(;a!==void 0;){if(o===a.index){let d;a.type===2?d=new O(r,r.nextSibling,this,t):a.type===1?d=new a.ctor(r,a.name,a.strings,this,t):a.type===6&&(d=new rt(r,this,t)),this._$AV.push(d),a=s[++c]}o!==a?.index&&(r=S.nextNode(),o++)}return S.currentNode=C,n}p(t){let e=0;for(let s of this._$AV)s!==void 0&&(s.strings!==void 0?(s._$AI(t,s,e),e+=s.strings.length-2):s._$AI(t[e])),e++}},O=class i{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(t,e,s,n){this.type=2,this._$AH=l,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=s,this.options=n,this._$Cv=n?.isConnected??!0}get parentNode(){let t=this._$AA.parentNode,e=this._$AM;return e!==void 0&&t?.nodeType===11&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){t=M(this,t,e),N(t)?t===l||t==null||t===""?(this._$AH!==l&&this._$AR(),this._$AH=l):t!==this._$AH&&t!==y&&this._(t):t._$litType$!==void 0?this.$(t):t.nodeType!==void 0?this.T(t):Wt(t)?this.k(t):this._(t)}S(t){return this._$AA.parentNode.insertBefore(t,this._$AB)}T(t){this._$AH!==t&&(this._$AR(),this._$AH=this.S(t))}_(t){this._$AH!==l&&N(this._$AH)?this._$AA.nextSibling.data=t:this.T(C.createTextNode(t)),this._$AH=t}$(t){let{values:e,_$litType$:s}=t,n=typeof s=="number"?this._$AC(t):(s.el===void 0&&(s.el=R.createElement(xt(s.h,s.h[0]),this.options)),s);if(this._$AH?._$AD===n)this._$AH.p(e);else{let r=new et(n,this),o=r.u(this.options);r.p(e),this.T(o),this._$AH=r}}_$AC(t){let e=$t.get(t.strings);return e===void 0&&$t.set(t.strings,e=new R(t)),e}k(t){bt(this._$AH)||(this._$AH=[],this._$AR());let e=this._$AH,s,n=0;for(let r of t)n===e.length?e.push(s=new i(this.S(k()),this.S(k()),this,this.options)):s=e[n],s._$AI(r),n++;n<e.length&&(this._$AR(s&&s._$AB.nextSibling,n),e.length=n)}_$AR(t=this._$AA.nextSibling,e){for(this._$AP?.(!1,!0,e);t&&t!==this._$AB;){let s=t.nextSibling;t.remove(),t=s}}setConnected(t){this._$AM===void 0&&(this._$Cv=t,this._$AP?.(t))}},T=class{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(t,e,s,n,r){this.type=1,this._$AH=l,this._$AN=void 0,this.element=t,this.name=e,this._$AM=n,this.options=r,s.length>2||s[0]!==""||s[1]!==""?(this._$AH=Array(s.length-1).fill(new String),this.strings=s):this._$AH=l}_$AI(t,e=this,s,n){let r=this.strings,o=!1;if(r===void 0)t=M(this,t,e,0),o=!N(t)||t!==this._$AH&&t!==y,o&&(this._$AH=t);else{let c=t,a,d;for(t=r[0],a=0;a<r.length-1;a++)d=M(this,c[s+a],e,a),d===y&&(d=this._$AH[a]),o||=!N(d)||d!==this._$AH[a],d===l?t=l:t!==l&&(t+=(d??"")+r[a+1]),this._$AH[a]=d}o&&!n&&this.j(t)}j(t){t===l?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,t??"")}},st=class extends T{constructor(){super(...arguments),this.type=3}j(t){this.element[this.name]=t===l?void 0:t}},nt=class extends T{constructor(){super(...arguments),this.type=4}j(t){this.element.toggleAttribute(this.name,!!t&&t!==l)}},it=class extends T{constructor(t,e,s,n,r){super(t,e,s,n,r),this.type=5}_$AI(t,e=this){if((t=M(this,t,e,0)??l)===y)return;let s=this._$AH,n=t===l&&s!==l||t.capture!==s.capture||t.once!==s.once||t.passive!==s.passive,r=t!==l&&(s===l||n);n&&this.element.removeEventListener(this.name,this,s),r&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){typeof this._$AH=="function"?this._$AH.call(this.options?.host??this.element,t):this._$AH.handleEvent(t)}},rt=class{constructor(t,e,s){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=s}get _$AU(){return this._$AM._$AU}_$AI(t){M(this,t)}};var Jt=ot.litHtmlPolyfillSupport;Jt?.(R,O),(ot.litHtmlVersions??=[]).push("3.1.3");var wt=(i,t,e)=>{let s=e?.renderBefore??t,n=s._$litPart$;if(n===void 0){let r=e?.renderBefore??null;s._$litPart$=n=new O(t.insertBefore(k(),r),r,void 0,e??{})}return n._$AI(i),n};var E=class extends f{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){let t=super.createRenderRoot();return this.renderOptions.renderBefore??=t.firstChild,t}update(t){let e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Do=wt(e,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return y}};E._$litElement$=!0,E["finalized"]=!0,globalThis.litElementHydrateSupport?.({LitElement:E});var Zt=globalThis.litElementPolyfillSupport;Zt?.({LitElement:E});(globalThis.litElementVersions??=[]).push("4.0.5");var Mt={ATTRIBUTE:1,CHILD:2,PROPERTY:3,BOOLEAN_ATTRIBUTE:4,EVENT:5,ELEMENT:6},Tt=i=>(...t)=>({_$litDirective$:i,values:t}),F=class{constructor(t){}get _$AU(){return this._$AM._$AU}_$AT(t,e,s){this._$Ct=t,this._$AM=e,this._$Ci=s}_$AS(t,e){return this.update(t,e)}update(t,e){return this.render(...e)}};var I=class extends F{constructor(t){if(super(t),this.it=l,t.type!==Mt.CHILD)throw Error(this.constructor.directiveName+"() can only be used in child bindings")}render(t){if(t===l||t==null)return this._t=void 0,this.it=t;if(t===y)return t;if(typeof t!="string")throw Error(this.constructor.directiveName+"() called with a non-string value");if(t===this.it)return this._t;this.it=t;let e=[t];return e.raw=e,this._t={_$litType$:this.constructor.resultType,strings:e,values:[]}}};I.directiveName="unsafeHTML",I.resultType=1;var J=Tt(I);var Yt={attribute:!0,type:String,converter:L,reflect:!1,hasChanged:K},Qt=(i=Yt,t,e)=>{let{kind:s,metadata:n}=e,r=globalThis.litPropertyMetadata.get(n);if(r===void 0&&globalThis.litPropertyMetadata.set(n,r=new Map),r.set(e.name,i),s==="accessor"){let{name:o}=e;return{set(c){let a=t.get.call(this);t.set.call(this,c),this.requestUpdate(o,a,i)},init(c){return c!==void 0&&this.P(o,void 0,i),c}}}if(s==="setter"){let{name:o}=e;return function(c){let a=this[o];t.call(this,c),this.requestUpdate(o,a,i)}}throw Error("Unsupported decorator location: "+s)};function p(i){return(t,e)=>typeof e=="object"?Qt(i,t,e):((s,n,r)=>{let o=n.hasOwnProperty(r);return n.constructor.createProperty(r,o?{...s,wrapped:!0}:s),o?Object.getOwnPropertyDescriptor(n,r):void 0})(i,t,e)}function Y(i,t){let e=document.createElement(i);for(let[s,n]of Object.entries(t))n!==null&&e.setAttribute(s,n);return e}var v=class extends E{createRenderRoot(){return this}};function Ut({headline:i="",message:t,status:e="warning"}){document.dispatchEvent(new CustomEvent("shiny:client-message",{detail:{headline:i,message:t,status:e}}))}var at="shiny-chat-message",Lt="shiny-user-message",Ht="shiny-status-message",kt="shiny-chat-messages",Nt="shiny-chat-input",Xt="shiny-chat-container",Pt={robot:'<svg fill="currentColor" class="bi bi-robot" viewBox="0 0 16 16" xmlns="http://www.w3.org/2000/svg"><path d="M6 12.5a.5.5 0 0 1 .5-.5h3a.5.5 0 0 1 0 1h-3a.5.5 0 0 1-.5-.5M3 8.062C3 6.76 4.235 5.765 5.53 5.886a26.6 26.6 0 0 0 4.94 0C11.765 5.765 13 6.76 13 8.062v1.157a.93.93 0 0 1-.765.935c-.845.147-2.34.346-4.235.346s-3.39-.2-4.235-.346A.93.93 0 0 1 3 9.219zm4.542-.827a.25.25 0 0 0-.217.068l-.92.9a25 25 0 0 1-1.871-.183.25.25 0 0 0-.068.495c.55.076 1.232.149 2.02.193a.25.25 0 0 0 .189-.071l.754-.736.847 1.71a.25.25 0 0 0 .404.062l.932-.97a25 25 0 0 0 1.922-.188.25.25 0 0 0-.068-.495c-.538.074-1.207.145-1.98.189a.25.25 0 0 0-.166.076l-.754.785-.842-1.7a.25.25 0 0 0-.182-.135"/><path d="M8.5 1.866a1 1 0 1 0-1 0V3h-2A4.5 4.5 0 0 0 1 7.5V8a1 1 0 0 0-1 1v2a1 1 0 0 0 1 1v1a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-1a1 1 0 0 0 1-1V9a1 1 0 0 0-1-1v-.5A4.5 4.5 0 0 0 10.5 3h-2zM14 7.5V13a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V7.5A3.5 3.5 0 0 1 5.5 4h5A3.5 3.5 0 0 1 14 7.5"/></svg>',dots_fade:'<svg width="24" height="24" fill="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><style>.spinner_S1WN{animation:spinner_MGfb .8s linear infinite;animation-delay:-.8s}.spinner_Km9P{animation-delay:-.65s}.spinner_JApP{animation-delay:-.5s}@keyframes spinner_MGfb{93.75%,100%{opacity:.2}}</style><circle class="spinner_S1WN" cx="4" cy="12" r="3"/><circle class="spinner_S1WN spinner_Km9P" cx="12" cy="12" r="3"/><circle class="spinner_S1WN spinner_JApP" cx="20" cy="12" r="3"/></svg>'},U=class extends v{constructor(){super(...arguments);this.content="...";this.content_type="markdown";this.streaming=!1}render(){let s=this.content.trim().length===0?Pt.dots_fade:Pt.robot;return x`
      <div class="message-icon">${J(s)}</div>
      <shiny-markdown-stream
        content=${this.content}
        content-type=${this.content_type}
        ?streaming=${this.streaming}
        auto-scroll
        .onContentChange=${this.#e}
        .onStreamEnd=${this.#t}
      ></shiny-markdown-stream>
    `}#e(){this.streaming||this.#t()}#t(){this.querySelectorAll(".suggestion,[data-suggestion]").forEach(e=>{if(!(e instanceof HTMLElement)||e.hasAttribute("tabindex"))return;e.setAttribute("tabindex","0"),e.setAttribute("role","button");let s=e.dataset.suggestion||e.textContent;e.setAttribute("aria-label",`Use chat suggestion: ${s}`)})}};m([p()],U.prototype,"content",2),m([p()],U.prototype,"content_type",2),m([p({type:Boolean,reflect:!0})],U.prototype,"streaming",2);var Q=class extends v{constructor(){super(...arguments);this.content="..."}render(){return x`
      <shiny-markdown-stream
        content=${this.content}
        content-type="semi-markdown"
      ></shiny-markdown-stream>
    `}};m([p()],Q.prototype,"content",2);var w=class extends v{constructor(){super(...arguments);this.content="";this.content_type="text";this.type="static"}render(){let e=this.content_type==="html"?J(this.content):this.content;return x`${e}`}updated(e){super.updated(e),(e.has("content")||e.has("content_type"))&&this.#e()}#e(){this.scrollIntoView({behavior:"smooth",block:"end"})}};m([p()],w.prototype,"content",2),m([p()],w.prototype,"content_type",2),m([p()],w.prototype,"type",2);var ht=class extends v{render(){return x``}},D=class extends v{constructor(){super(...arguments);this._disabled=!1;this.placeholder="Enter a message..."}get disabled(){return this._disabled}set disabled(e){let s=this._disabled;e!==s&&(this._disabled=e,e?this.setAttribute("disabled",""):this.removeAttribute("disabled"),this.requestUpdate("disabled",s),this.#t())}attributeChangedCallback(e,s,n){super.attributeChangedCallback(e,s,n),e==="disabled"&&(this.disabled=n!==null)}get textarea(){return this.querySelector("textarea")}get value(){return this.textarea.value}get valueIsEmpty(){return this.value.trim().length===0}get button(){return this.querySelector("button")}render(){let e='<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" class="bi bi-arrow-up-circle-fill" viewBox="0 0 16 16"><path d="M16 8A8 8 0 1 0 0 8a8 8 0 0 0 16 0m-7.5 3.5a.5.5 0 0 1-1 0V5.707L5.354 7.854a.5.5 0 1 1-.708-.708l3-3a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1-.708.708L8.5 5.707z"/></svg>';return x`
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
        ${J(e)}
      </button>
    `}#e(e){e.code==="Enter"&&!e.shiftKey&&!this.valueIsEmpty&&(e.preventDefault(),this.#s())}#t(){this.button.disabled=this.disabled?!0:this.value.trim().length===0}firstUpdated(){this.#t()}#s(e=!0){if(this.valueIsEmpty||this.disabled)return;Shiny.setInputValue(this.id,this.value,{priority:"event"});let s=new CustomEvent("shiny-chat-input-sent",{detail:{content:this.value,role:"user"},bubbles:!0,composed:!0});this.dispatchEvent(s),this.setInputValue(""),this.disabled=!0,e&&this.textarea.focus()}setInputValue(e,{submit:s=!1,focus:n=!1}={}){let r=this.textarea.value;this.textarea.value=e;let o=new Event("input",{bubbles:!0,cancelable:!0});this.textarea.dispatchEvent(o),s&&(this.#s(!1),r&&this.setInputValue(r)),n&&this.textarea.focus()}};m([p()],D.prototype,"placeholder",2),m([p({type:Boolean})],D.prototype,"disabled",1);var lt=class extends v{get input(){return this.querySelector(Nt)}get messages(){return this.querySelector(kt)}get lastMessage(){let t=this.messages.querySelector("shiny-chat-message:last-child");return t||null}render(){return x``}firstUpdated(){this.messages&&(this.addEventListener("shiny-chat-input-sent",this.#e),this.addEventListener("shiny-chat-append-message",this.#t),this.addEventListener("shiny-chat-append-message-chunk",this.#o),this.addEventListener("shiny-chat-append-status-message",this.#a),this.addEventListener("shiny-chat-clear-messages",this.#h),this.addEventListener("shiny-chat-update-user-input",this.#l),this.addEventListener("shiny-chat-remove-loading-message",this.#p),this.addEventListener("click",this.#c),this.addEventListener("keydown",this.#d))}disconnectedCallback(){super.disconnectedCallback(),this.removeEventListener("shiny-chat-input-sent",this.#e),this.removeEventListener("shiny-chat-append-message",this.#t),this.removeEventListener("shiny-chat-append-message-chunk",this.#o),this.removeEventListener("shiny-chat-append-status-message",this.#a),this.removeEventListener("shiny-chat-clear-messages",this.#h),this.removeEventListener("shiny-chat-update-user-input",this.#l),this.removeEventListener("shiny-chat-remove-loading-message",this.#p),this.removeEventListener("click",this.#c),this.removeEventListener("keydown",this.#d)}#e(t){this.#n(t.detail),this.#m()}#t(t){this.#n(t.detail)}#s(){this.#r(),this.input.disabled||(this.input.disabled=!0)}#n(t,e=!0){this.#s();let s=t.role==="user"?Lt:at,n=Y(s,t);this.messages.appendChild(n),e&&this.#i()}#m(){let e=Y(at,{content:"",role:"assistant"});this.messages.appendChild(e)}#r(){this.lastMessage?.content||this.lastMessage?.remove()}#o(t){this.#g(t.detail)}#g(t){t.chunk_type==="message_start"&&this.#n(t,!1);let e=this.lastMessage;if(!e)throw new Error("No messages found in the chat output");if(t.chunk_type==="message_start"){e.setAttribute("streaming","");return}let s=t.operation==="append"?e.getAttribute("content")+t.content:t.content;e.setAttribute("content",s),t.chunk_type==="message_end"&&(this.lastMessage?.removeAttribute("streaming"),this.#i())}#a(t){if(this.messages.lastChild instanceof w&&this.messages.lastChild.type=="dynamic"){this.messages.lastChild.content=t.detail.content,this.messages.lastChild.content_type=t.detail.content_type;return}let e=Y(Ht,t.detail);this.messages.appendChild(e)}#h(){this.messages.innerHTML=""}#l(t){let{value:e,placeholder:s,submit:n,focus:r}=t.detail;e!==void 0&&this.input.setInputValue(e,{submit:n,focus:r}),s!==void 0&&(this.input.placeholder=s)}#c(t){this.#u(t)}#d(t){(t.key==="Enter"||t.key===" ")&&this.#u(t)}#u(t){let{suggestion:e,submit:s}=this.#f(t.target);if(!e)return;t.preventDefault();let n=t.metaKey||t.ctrlKey?!0:t.altKey?!1:s;this.input.setInputValue(e,{submit:n,focus:!n})}#f(t){if(!(t instanceof HTMLElement))return{};let e=t.closest(".suggestion, [data-suggestion]");return e instanceof HTMLElement?e.classList.contains("suggestion")||e.dataset.suggestion!==void 0?{suggestion:e.dataset.suggestion||e.textContent||void 0,submit:e.classList.contains("submit")||e.dataset.suggestionSubmit===""||e.dataset.suggestionSubmit==="true"}:{}:{}}#p(){this.#r(),this.#i()}#i(){this.input.disabled=!1}};customElements.define(at,U);customElements.define(Lt,Q);customElements.define(Ht,w);customElements.define(kt,ht);customElements.define(Nt,D);customElements.define(Xt,lt);$(function(){Shiny.addCustomMessageHandler("shinyChatMessage",function(i){let t=new CustomEvent(i.handler,{detail:i.obj}),e=document.getElementById(i.id);if(!e){Ut({status:"error",message:`Unable to handle Chat() message since element with id
          ${i.id} wasn't found. Do you need to call .ui() (Express) or need a
          chat_ui('${i.id}') in the UI (Core)?
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
