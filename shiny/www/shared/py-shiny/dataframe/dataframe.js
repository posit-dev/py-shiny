<<<<<<< Updated upstream
var $e,h,sn,go,ge,nn,an,dt,un,Ge={},dn=[],po=/acit|ex(?:s|g|n|p|$)|rph|grid|ows|mnc|ntw|ine[ch]|zoo|^ord|itera/i,Ke=Array.isArray;function ie(e,n){for(var t in n)e[t]=n[t];return e}function cn(e){var n=e.parentNode;n&&n.removeChild(e)}function k(e,n,t){var r,o,i,l={};for(i in n)i=="key"?r=n[i]:i=="ref"?o=n[i]:l[i]=n[i];if(arguments.length>2&&(l.children=arguments.length>3?$e.call(arguments,2):t),typeof e=="function"&&e.defaultProps!=null)for(i in e.defaultProps)l[i]===void 0&&(l[i]=e.defaultProps[i]);return Me(e,l,r,o,null)}function Me(e,n,t,r,o){var i={type:e,props:n,key:t,ref:r,__k:null,__:null,__b:0,__e:null,__d:void 0,__c:null,__h:null,constructor:void 0,__v:o??++sn};return o==null&&h.vnode!=null&&h.vnode(i),i}function ft(){return{current:null}}function Z(e){return e.children}function j(e,n){this.props=e,this.context=n}function Fe(e,n){if(n==null)return e.__?Fe(e.__,e.__.__k.indexOf(e)+1):null;for(var t;n<e.__k.length;n++)if((t=e.__k[n])!=null&&t.__e!=null)return t.__e;return typeof e.type=="function"?Fe(e):null}function fn(e){var n,t;if((e=e.__)!=null&&e.__c!=null){for(e.__e=e.__c.base=null,n=0;n<e.__k.length;n++)if((t=e.__k[n])!=null&&t.__e!=null){e.__e=e.__c.base=t.__e;break}return fn(e)}}function ct(e){(!e.__d&&(e.__d=!0)&&ge.push(e)&&!Be.__r++||nn!==h.debounceRendering)&&((nn=h.debounceRendering)||an)(Be)}function Be(){var e,n,t,r,o,i,l,u;for(ge.sort(dt);e=ge.shift();)e.__d&&(n=ge.length,r=void 0,o=void 0,l=(i=(t=e).__v).__e,(u=t.__P)&&(r=[],(o=ie({},i)).__v=i.__v+1,gt(u,i,o,t.__n,u.ownerSVGElement!==void 0,i.__h!=null?[l]:null,r,l??Fe(i),i.__h),hn(r,i),i.__e!=l&&fn(i)),ge.length>n&&ge.sort(dt));Be.__r=0}function gn(e,n,t,r,o,i,l,u,a,d){var s,g,f,c,p,m,_,v=r&&r.__k||dn,w=v.length;for(t.__k=[],s=0;s<n.length;s++)if((c=t.__k[s]=(c=n[s])==null||typeof c=="boolean"||typeof c=="function"?null:typeof c=="string"||typeof c=="number"||typeof c=="bigint"?Me(null,c,null,null,c):Ke(c)?Me(Z,{children:c},null,null,null):c.__b>0?Me(c.type,c.props,c.key,c.ref?c.ref:null,c.__v):c)!=null){if(c.__=t,c.__b=t.__b+1,(f=v[s])===null||f&&c.key==f.key&&c.type===f.type)v[s]=void 0;else for(g=0;g<w;g++){if((f=v[g])&&c.key==f.key&&c.type===f.type){v[g]=void 0;break}f=null}gt(e,c,f=f||Ge,o,i,l,u,a,d),p=c.__e,(g=c.ref)&&f.ref!=g&&(_||(_=[]),f.ref&&_.push(f.ref,null,c),_.push(g,c.__c||p,c)),p!=null?(m==null&&(m=p),typeof c.type=="function"&&c.__k===f.__k?c.__d=a=pn(c,a,e):a=mn(e,c,f,v,p,a),typeof t.type=="function"&&(t.__d=a)):a&&f.__e==a&&a.parentNode!=e&&(a=Fe(f))}for(t.__e=m,s=w;s--;)v[s]!=null&&(typeof t.type=="function"&&v[s].__e!=null&&v[s].__e==t.__d&&(t.__d=_n(r).nextSibling),yn(v[s],v[s]));if(_)for(s=0;s<_.length;s++)vn(_[s],_[++s],_[++s])}function pn(e,n,t){for(var r,o=e.__k,i=0;o&&i<o.length;i++)(r=o[i])&&(r.__=e,n=typeof r.type=="function"?pn(r,n,t):mn(t,r,r,o,r.__e,n));return n}function ee(e,n){return n=n||[],e==null||typeof e=="boolean"||(Ke(e)?e.some(function(t){ee(t,n)}):n.push(e)),n}function mn(e,n,t,r,o,i){var l,u,a;if(n.__d!==void 0)l=n.__d,n.__d=void 0;else if(t==null||o!=i||o.parentNode==null)e:if(i==null||i.parentNode!==e)e.appendChild(o),l=null;else{for(u=i,a=0;(u=u.nextSibling)&&a<r.length;a+=1)if(u==o)break e;e.insertBefore(o,i),l=i}return l!==void 0?l:o.nextSibling}function _n(e){var n,t,r;if(e.type==null||typeof e.type=="string")return e.__e;if(e.__k){for(n=e.__k.length-1;n>=0;n--)if((t=e.__k[n])&&(r=_n(t)))return r}return null}function mo(e,n,t,r,o){var i;for(i in t)i==="children"||i==="key"||i in n||Ue(e,i,null,t[i],r);for(i in n)o&&typeof n[i]!="function"||i==="children"||i==="key"||i==="value"||i==="checked"||t[i]===n[i]||Ue(e,i,n[i],t[i],r)}function rn(e,n,t){n[0]==="-"?e.setProperty(n,t??""):e[n]=t==null?"":typeof t!="number"||po.test(n)?t:t+"px"}function Ue(e,n,t,r,o){var i;e:if(n==="style")if(typeof t=="string")e.style.cssText=t;else{if(typeof r=="string"&&(e.style.cssText=r=""),r)for(n in r)t&&n in t||rn(e.style,n,"");if(t)for(n in t)r&&t[n]===r[n]||rn(e.style,n,t[n])}else if(n[0]==="o"&&n[1]==="n")i=n!==(n=n.replace(/Capture$/,"")),n=n.toLowerCase()in e?n.toLowerCase().slice(2):n.slice(2),e.l||(e.l={}),e.l[n+i]=t,t?r||e.addEventListener(n,i?ln:on,i):e.removeEventListener(n,i?ln:on,i);else if(n!=="dangerouslySetInnerHTML"){if(o)n=n.replace(/xlink(H|:h)/,"h").replace(/sName$/,"s");else if(n!=="width"&&n!=="height"&&n!=="href"&&n!=="list"&&n!=="form"&&n!=="tabIndex"&&n!=="download"&&n!=="rowSpan"&&n!=="colSpan"&&n in e)try{e[n]=t??"";break e}catch{}typeof t=="function"||(t==null||t===!1&&n[4]!=="-"?e.removeAttribute(n):e.setAttribute(n,t))}}function on(e){return this.l[e.type+!1](h.event?h.event(e):e)}function ln(e){return this.l[e.type+!0](h.event?h.event(e):e)}function gt(e,n,t,r,o,i,l,u,a){var d,s,g,f,c,p,m,_,v,w,E,V,D,G,re,I=n.type;if(n.constructor!==void 0)return null;t.__h!=null&&(a=t.__h,u=n.__e=t.__e,n.__h=null,i=[u]),(d=h.__b)&&d(n);try{e:if(typeof I=="function"){if(_=n.props,v=(d=I.contextType)&&r[d.__c],w=d?v?v.props.value:d.__:r,t.__c?m=(s=n.__c=t.__c).__=s.__E:("prototype"in I&&I.prototype.render?n.__c=s=new I(_,w):(n.__c=s=new j(_,w),s.constructor=I,s.render=ho),v&&v.sub(s),s.props=_,s.state||(s.state={}),s.context=w,s.__n=r,g=s.__d=!0,s.__h=[],s._sb=[]),s.__s==null&&(s.__s=s.state),I.getDerivedStateFromProps!=null&&(s.__s==s.state&&(s.__s=ie({},s.__s)),ie(s.__s,I.getDerivedStateFromProps(_,s.__s))),f=s.props,c=s.state,s.__v=n,g)I.getDerivedStateFromProps==null&&s.componentWillMount!=null&&s.componentWillMount(),s.componentDidMount!=null&&s.__h.push(s.componentDidMount);else{if(I.getDerivedStateFromProps==null&&_!==f&&s.componentWillReceiveProps!=null&&s.componentWillReceiveProps(_,w),!s.__e&&s.shouldComponentUpdate!=null&&s.shouldComponentUpdate(_,s.__s,w)===!1||n.__v===t.__v){for(n.__v!==t.__v&&(s.props=_,s.state=s.__s,s.__d=!1),s.__e=!1,n.__e=t.__e,n.__k=t.__k,n.__k.forEach(function(N){N&&(N.__=n)}),E=0;E<s._sb.length;E++)s.__h.push(s._sb[E]);s._sb=[],s.__h.length&&l.push(s);break e}s.componentWillUpdate!=null&&s.componentWillUpdate(_,s.__s,w),s.componentDidUpdate!=null&&s.__h.push(function(){s.componentDidUpdate(f,c,p)})}if(s.context=w,s.props=_,s.__P=e,V=h.__r,D=0,"prototype"in I&&I.prototype.render){for(s.state=s.__s,s.__d=!1,V&&V(n),d=s.render(s.props,s.state,s.context),G=0;G<s._sb.length;G++)s.__h.push(s._sb[G]);s._sb=[]}else do s.__d=!1,V&&V(n),d=s.render(s.props,s.state,s.context),s.state=s.__s;while(s.__d&&++D<25);s.state=s.__s,s.getChildContext!=null&&(r=ie(ie({},r),s.getChildContext())),g||s.getSnapshotBeforeUpdate==null||(p=s.getSnapshotBeforeUpdate(f,c)),gn(e,Ke(re=d!=null&&d.type===Z&&d.key==null?d.props.children:d)?re:[re],n,t,r,o,i,l,u,a),s.base=n.__e,n.__h=null,s.__h.length&&l.push(s),m&&(s.__E=s.__=null),s.__e=!1}else i==null&&n.__v===t.__v?(n.__k=t.__k,n.__e=t.__e):n.__e=_o(t.__e,n,t,r,o,i,l,a);(d=h.diffed)&&d(n)}catch(N){n.__v=null,(a||i!=null)&&(n.__e=u,n.__h=!!a,i[i.indexOf(u)]=null),h.__e(N,n,t)}}function hn(e,n){h.__c&&h.__c(n,e),e.some(function(t){try{e=t.__h,t.__h=[],e.some(function(r){r.call(t)})}catch(r){h.__e(r,t.__v)}})}function _o(e,n,t,r,o,i,l,u){var a,d,s,g=t.props,f=n.props,c=n.type,p=0;if(c==="svg"&&(o=!0),i!=null){for(;p<i.length;p++)if((a=i[p])&&"setAttribute"in a==!!c&&(c?a.localName===c:a.nodeType===3)){e=a,i[p]=null;break}}if(e==null){if(c===null)return document.createTextNode(f);e=o?document.createElementNS("http://www.w3.org/2000/svg",c):document.createElement(c,f.is&&f),i=null,u=!1}if(c===null)g===f||u&&e.data===f||(e.data=f);else{if(i=i&&$e.call(e.childNodes),d=(g=t.props||Ge).dangerouslySetInnerHTML,s=f.dangerouslySetInnerHTML,!u){if(i!=null)for(g={},p=0;p<e.attributes.length;p++)g[e.attributes[p].name]=e.attributes[p].value;(s||d)&&(s&&(d&&s.__html==d.__html||s.__html===e.innerHTML)||(e.innerHTML=s&&s.__html||""))}if(mo(e,f,g,o,u),s)n.__k=[];else if(gn(e,Ke(p=n.props.children)?p:[p],n,t,r,o&&c!=="foreignObject",i,l,i?i[0]:t.__k&&Fe(t,0),u),i!=null)for(p=i.length;p--;)i[p]!=null&&cn(i[p]);u||("value"in f&&(p=f.value)!==void 0&&(p!==e.value||c==="progress"&&!p||c==="option"&&p!==g.value)&&Ue(e,"value",p,g.value,!1),"checked"in f&&(p=f.checked)!==void 0&&p!==e.checked&&Ue(e,"checked",p,g.checked,!1))}return e}function vn(e,n,t){try{typeof e=="function"?e(n):e.current=n}catch(r){h.__e(r,t)}}function yn(e,n,t){var r,o;if(h.unmount&&h.unmount(e),(r=e.ref)&&(r.current&&r.current!==e.__e||vn(r,null,n)),(r=e.__c)!=null){if(r.componentWillUnmount)try{r.componentWillUnmount()}catch(i){h.__e(i,n)}r.base=r.__P=null,e.__c=void 0}if(r=e.__k)for(o=0;o<r.length;o++)r[o]&&yn(r[o],n,t||typeof e.type!="function");t||e.__e==null||cn(e.__e),e.__=e.__e=e.__d=void 0}function ho(e,n,t){return this.constructor(e,t)}function ve(e,n,t){var r,o,i;h.__&&h.__(e,n),o=(r=typeof t=="function")?null:t&&t.__k||n.__k,i=[],gt(n,e=(!r&&t||n).__k=k(Z,null,[e]),o||Ge,Ge,n.ownerSVGElement!==void 0,!r&&t?[t]:o?null:n.firstChild?$e.call(n.childNodes):null,i,!r&&t?t:o?o.__e:n.firstChild,r),hn(i,e)}function pt(e,n){ve(e,n,pt)}function bn(e,n,t){var r,o,i,l,u=ie({},e.props);for(i in e.type&&e.type.defaultProps&&(l=e.type.defaultProps),n)i=="key"?r=n[i]:i=="ref"?o=n[i]:u[i]=n[i]===void 0&&l!==void 0?l[i]:n[i];return arguments.length>2&&(u.children=arguments.length>3?$e.call(arguments,2):t),Me(e.type,u,r||e.key,o||e.ref,null)}function mt(e,n){var t={__c:n="__cC"+un++,__:e,Consumer:function(r,o){return r.children(o)},Provider:function(r){var o,i;return this.getChildContext||(o=[],(i={})[n]=this,this.getChildContext=function(){return i},this.shouldComponentUpdate=function(l){this.props.value!==l.value&&o.some(function(u){u.__e=!0,ct(u)})},this.sub=function(l){o.push(l);var u=l.componentWillUnmount;l.componentWillUnmount=function(){o.splice(o.indexOf(l),1),u&&u.call(l)}}),r.children}};return t.Provider.__=t.Consumer.contextType=t}$e=dn.slice,h={__e:function(e,n,t,r){for(var o,i,l;n=n.__;)if((o=n.__c)&&!o.__)try{if((i=o.constructor)&&i.getDerivedStateFromError!=null&&(o.setState(i.getDerivedStateFromError(e)),l=o.__d),o.componentDidCatch!=null&&(o.componentDidCatch(e,r||{}),l=o.__d),l)return o.__E=o}catch(u){e=u}throw e}},sn=0,go=function(e){return e!=null&&e.constructor===void 0},j.prototype.setState=function(e,n){var t;t=this.__s!=null&&this.__s!==this.state?this.__s:this.__s=ie({},this.state),typeof e=="function"&&(e=e(ie({},t),this.props)),e&&ie(t,e),e!=null&&this.__v&&(n&&this._sb.push(n),ct(this))},j.prototype.forceUpdate=function(e){this.__v&&(this.__e=!0,e&&this.__h.push(e),ct(this))},j.prototype.render=Z,ge=[],an=typeof Promise=="function"?Promise.prototype.then.bind(Promise.resolve()):setTimeout,dt=function(e,n){return e.__v.__b-n.__v.__b},Be.__r=0,un=0;var de,F,_t,Sn,ye=0,Fn=[],je=[],wn=h.__b,Cn=h.__r,En=h.diffed,Rn=h.__c,xn=h.unmount;function be(e,n){h.__h&&h.__h(F,e,ye||n),ye=0;var t=F.__H||(F.__H={__:[],__h:[]});return e>=t.__.length&&t.__.push({__V:je}),t.__[e]}function A(e){return ye=1,Se(Dn,e)}function Se(e,n,t){var r=be(de++,2);if(r.t=e,!r.__c&&(r.__=[t?t(n):Dn(void 0,n),function(u){var a=r.__N?r.__N[0]:r.__[0],d=r.t(a,u);a!==d&&(r.__N=[d,r.__[1]],r.__c.setState({}))}],r.__c=F,!F.u)){var o=function(u,a,d){if(!r.__c.__H)return!0;var s=r.__c.__H.__.filter(function(f){return f.__c});if(s.every(function(f){return!f.__N}))return!i||i.call(this,u,a,d);var g=!1;return s.forEach(function(f){if(f.__N){var c=f.__[0];f.__=f.__N,f.__N=void 0,c!==f.__[0]&&(g=!0)}}),!(!g&&r.__c.props===u)&&(!i||i.call(this,u,a,d))};F.u=!0;var i=F.shouldComponentUpdate,l=F.componentWillUpdate;F.componentWillUpdate=function(u,a,d){if(this.__e){var s=i;i=void 0,o(u,a,d),i=s}l&&l.call(this,u,a,d)},F.shouldComponentUpdate=o}return r.__N||r.__}function L(e,n){var t=be(de++,3);!h.__s&&vt(t.__H,n)&&(t.__=e,t.i=n,F.__H.__h.push(t))}function te(e,n){var t=be(de++,4);!h.__s&&vt(t.__H,n)&&(t.__=e,t.i=n,F.__h.push(t))}function q(e){return ye=5,ne(function(){return{current:e}},[])}function $n(e,n,t){ye=6,te(function(){return typeof e=="function"?(e(n()),function(){return e(null)}):e?(e.current=n(),function(){return e.current=null}):void 0},t==null?t:t.concat(e))}function ne(e,n){var t=be(de++,7);return vt(t.__H,n)?(t.__V=e(),t.i=n,t.__h=e,t.__V):t.__}function le(e,n){return ye=8,ne(function(){return e},n)}function In(e){var n=F.context[e.__c],t=be(de++,9);return t.c=e,n?(t.__==null&&(t.__=!0,n.sub(F)),n.props.value):e.__}function Vn(e,n){h.useDebugValue&&h.useDebugValue(n?n(e):e)}function Tn(){var e=be(de++,11);if(!e.__){for(var n=F.__v;n!==null&&!n.__m&&n.__!==null;)n=n.__;var t=n.__m||(n.__m=[0,0]);e.__="P"+t[0]+"-"+t[1]++}return e.__}function vo(){for(var e;e=Fn.shift();)if(e.__P&&e.__H)try{e.__H.__h.forEach(qe),e.__H.__h.forEach(ht),e.__H.__h=[]}catch(n){e.__H.__h=[],h.__e(n,e.__v)}}h.__b=function(e){F=null,wn&&wn(e)},h.__r=function(e){Cn&&Cn(e),de=0;var n=(F=e.__c).__H;n&&(_t===F?(n.__h=[],F.__h=[],n.__.forEach(function(t){t.__N&&(t.__=t.__N),t.__V=je,t.__N=t.i=void 0})):(n.__h.forEach(qe),n.__h.forEach(ht),n.__h=[],de=0)),_t=F},h.diffed=function(e){En&&En(e);var n=e.__c;n&&n.__H&&(n.__H.__h.length&&(Fn.push(n)!==1&&Sn===h.requestAnimationFrame||((Sn=h.requestAnimationFrame)||yo)(vo)),n.__H.__.forEach(function(t){t.i&&(t.__H=t.i),t.__V!==je&&(t.__=t.__V),t.i=void 0,t.__V=je})),_t=F=null},h.__c=function(e,n){n.some(function(t){try{t.__h.forEach(qe),t.__h=t.__h.filter(function(r){return!r.__||ht(r)})}catch(r){n.some(function(o){o.__h&&(o.__h=[])}),n=[],h.__e(r,t.__v)}}),Rn&&Rn(e,n)},h.unmount=function(e){xn&&xn(e);var n,t=e.__c;t&&t.__H&&(t.__H.__.forEach(function(r){try{qe(r)}catch(o){n=o}}),t.__H=void 0,n&&h.__e(n,t.__v))};var Mn=typeof requestAnimationFrame=="function";function yo(e){var n,t=function(){clearTimeout(r),Mn&&cancelAnimationFrame(n),setTimeout(e)},r=setTimeout(t,100);Mn&&(n=requestAnimationFrame(t))}function qe(e){var n=F,t=e.__c;typeof t=="function"&&(e.__c=void 0,t()),F=n}function ht(e){var n=F;e.__c=e.__(),F=n}function vt(e,n){return!e||e.length!==n.length||n.some(function(t,r){return t!==e[r]})}function Dn(e,n){return typeof n=="function"?n(e):n}function Gn(e,n){for(var t in n)e[t]=n[t];return e}function bt(e,n){for(var t in e)if(t!=="__source"&&!(t in n))return!0;for(var r in n)if(r!=="__source"&&e[r]!==n[r])return!0;return!1}function yt(e,n){return e===n&&(e!==0||1/e==1/n)||e!=e&&n!=n}function St(e){this.props=e}function bo(e,n){function t(o){var i=this.props.ref,l=i==o.ref;return!l&&i&&(i.call?i(null):i.current=null),n?!n(this.props,o)||!l:bt(this.props,o)}function r(o){return this.shouldComponentUpdate=t,k(e,o)}return r.displayName="Memo("+(e.displayName||e.name)+")",r.prototype.isReactComponent=!0,r.__f=!0,r}(St.prototype=new j).isPureReactComponent=!0,St.prototype.shouldComponentUpdate=function(e,n){return bt(this.props,e)||bt(this.state,n)};var On=h.__b;h.__b=function(e){e.type&&e.type.__f&&e.ref&&(e.props.ref=e.ref,e.ref=null),On&&On(e)};var So=typeof Symbol<"u"&&Symbol.for&&Symbol.for("react.forward_ref")||3911;function wo(e){function n(t){var r=Gn({},t);return delete r.ref,e(r,t.ref||null)}return n.$$typeof=So,n.render=n,n.prototype.isReactComponent=n.__f=!0,n.displayName="ForwardRef("+(e.displayName||e.name)+")",n}var An=function(e,n){return e==null?null:ee(ee(e).map(n))},Co={map:An,forEach:An,count:function(e){return e?ee(e).length:0},only:function(e){var n=ee(e);if(n.length!==1)throw"Children.only";return n[0]},toArray:ee},Eo=h.__e;h.__e=function(e,n,t,r){if(e.then){for(var o,i=n;i=i.__;)if((o=i.__c)&&o.__c)return n.__e==null&&(n.__e=t.__e,n.__k=t.__k),o.__c(e,n)}Eo(e,n,t,r)};var Nn=h.unmount;function Bn(e,n,t){return e&&(e.__c&&e.__c.__H&&(e.__c.__H.__.forEach(function(r){typeof r.__c=="function"&&r.__c()}),e.__c.__H=null),(e=Gn({},e)).__c!=null&&(e.__c.__P===t&&(e.__c.__P=n),e.__c=null),e.__k=e.__k&&e.__k.map(function(r){return Bn(r,n,t)})),e}function Un(e,n,t){return e&&(e.__v=null,e.__k=e.__k&&e.__k.map(function(r){return Un(r,n,t)}),e.__c&&e.__c.__P===n&&(e.__e&&t.insertBefore(e.__e,e.__d),e.__c.__e=!0,e.__c.__P=t)),e}function We(){this.__u=0,this.t=null,this.__b=null}function Kn(e){var n=e.__.__c;return n&&n.__a&&n.__a(e)}function Ro(e){var n,t,r;function o(i){if(n||(n=e()).then(function(l){t=l.default||l},function(l){r=l}),r)throw r;if(!t)throw n;return k(t,i)}return o.displayName="Lazy",o.__f=!0,o}function Ie(){this.u=null,this.o=null}h.unmount=function(e){var n=e.__c;n&&n.__R&&n.__R(),n&&e.__h===!0&&(e.type=null),Nn&&Nn(e)},(We.prototype=new j).__c=function(e,n){var t=n.__c,r=this;r.t==null&&(r.t=[]),r.t.push(t);var o=Kn(r.__v),i=!1,l=function(){i||(i=!0,t.__R=null,o?o(u):u())};t.__R=l;var u=function(){if(!--r.__u){if(r.state.__a){var d=r.state.__a;r.__v.__k[0]=Un(d,d.__c.__P,d.__c.__O)}var s;for(r.setState({__a:r.__b=null});s=r.t.pop();)s.forceUpdate()}},a=n.__h===!0;r.__u++||a||r.setState({__a:r.__b=r.__v.__k[0]}),e.then(l,l)},We.prototype.componentWillUnmount=function(){this.t=[]},We.prototype.render=function(e,n){if(this.__b){if(this.__v.__k){var t=document.createElement("div"),r=this.__v.__k[0].__c;this.__v.__k[0]=Bn(this.__b,t,r.__O=r.__P)}this.__b=null}var o=n.__a&&k(Z,null,e.fallback);return o&&(o.__h=null),[k(Z,null,n.__a?null:e.children),o]};var Pn=function(e,n,t){if(++t[1]===t[0]&&e.o.delete(n),e.props.revealOrder&&(e.props.revealOrder[0]!=="t"||!e.o.size))for(t=e.u;t;){for(;t.length>3;)t.pop()();if(t[1]<t[0])break;e.u=t=t[2]}};function xo(e){return this.getChildContext=function(){return e.context},e.children}function Mo(e){var n=this,t=e.i;n.componentWillUnmount=function(){ve(null,n.l),n.l=null,n.i=null},n.i&&n.i!==t&&n.componentWillUnmount(),e.__v?(n.l||(n.i=t,n.l={nodeType:1,parentNode:t,childNodes:[],appendChild:function(r){this.childNodes.push(r),n.i.appendChild(r)},insertBefore:function(r,o){this.childNodes.push(r),n.i.appendChild(r)},removeChild:function(r){this.childNodes.splice(this.childNodes.indexOf(r)>>>1,1),n.i.removeChild(r)}}),ve(k(xo,{context:n.context},e.__v),n.l)):n.l&&n.componentWillUnmount()}function Fo(e,n){var t=k(Mo,{__v:e,i:n});return t.containerInfo=n,t}(Ie.prototype=new j).__a=function(e){var n=this,t=Kn(n.__v),r=n.o.get(e);return r[0]++,function(o){var i=function(){n.props.revealOrder?(r.push(o),Pn(n,e,r)):o()};t?t(i):i()}},Ie.prototype.render=function(e){this.u=null,this.o=new Map;var n=ee(e.children);e.revealOrder&&e.revealOrder[0]==="b"&&n.reverse();for(var t=n.length;t--;)this.o.set(n[t],this.u=[1,0,this.u]);return e.children},Ie.prototype.componentDidUpdate=Ie.prototype.componentDidMount=function(){var e=this;this.o.forEach(function(n,t){Pn(e,t,n)})};var jn=typeof Symbol<"u"&&Symbol.for&&Symbol.for("react.element")||60103,$o=/^(?:accent|alignment|arabic|baseline|cap|clip(?!PathU)|color|dominant|fill|flood|font|glyph(?!R)|horiz|image(!S)|letter|lighting|marker(?!H|W|U)|overline|paint|pointer|shape|stop|strikethrough|stroke|text(?!L)|transform|underline|unicode|units|v|vector|vert|word|writing|x(?!C))[A-Z]/,Io=/^on(Ani|Tra|Tou|BeforeInp|Compo)/,Vo=/[A-Z0-9]/g,To=typeof document<"u",Do=function(e){return(typeof Symbol<"u"&&typeof Symbol()=="symbol"?/fil|che|rad/:/fil|che|ra/).test(e)};function wt(e,n,t){return n.__k==null&&(n.textContent=""),ve(e,n),typeof t=="function"&&t(),e?e.__c:null}function qn(e,n,t){return pt(e,n),typeof t=="function"&&t(),e?e.__c:null}j.prototype.isReactComponent={},["componentWillMount","componentWillReceiveProps","componentWillUpdate"].forEach(function(e){Object.defineProperty(j.prototype,e,{configurable:!0,get:function(){return this["UNSAFE_"+e]},set:function(n){Object.defineProperty(this,e,{configurable:!0,writable:!0,value:n})}})});var kn=h.event;function Oo(){}function Ao(){return this.cancelBubble}function No(){return this.defaultPrevented}h.event=function(e){return kn&&(e=kn(e)),e.persist=Oo,e.isPropagationStopped=Ao,e.isDefaultPrevented=No,e.nativeEvent=e};var Ct,Po={enumerable:!1,configurable:!0,get:function(){return this.class}},Ln=h.vnode;h.vnode=function(e){typeof e.type=="string"&&function(n){var t=n.props,r=n.type,o={};for(var i in t){var l=t[i];if(!(i==="value"&&"defaultValue"in t&&l==null||To&&i==="children"&&r==="noscript"||i==="class"||i==="className")){var u=i.toLowerCase();i==="defaultValue"&&"value"in t&&t.value==null?i="value":i==="download"&&l===!0?l="":u==="ondoubleclick"?i="ondblclick":u!=="onchange"||r!=="input"&&r!=="textarea"||Do(t.type)?u==="onfocus"?i="onfocusin":u==="onblur"?i="onfocusout":Io.test(i)?i=u:r.indexOf("-")===-1&&$o.test(i)?i=i.replace(Vo,"-$&").toLowerCase():l===null&&(l=void 0):u=i="oninput",u==="oninput"&&o[i=u]&&(i="oninputCapture"),o[i]=l}}r=="select"&&o.multiple&&Array.isArray(o.value)&&(o.value=ee(t.children).forEach(function(a){a.props.selected=o.value.indexOf(a.props.value)!=-1})),r=="select"&&o.defaultValue!=null&&(o.value=ee(t.children).forEach(function(a){a.props.selected=o.multiple?o.defaultValue.indexOf(a.props.value)!=-1:o.defaultValue==a.props.value})),t.class&&!t.className?(o.class=t.class,Object.defineProperty(o,"className",Po)):(t.className&&!t.class||t.class&&t.className)&&(o.class=o.className=t.className),n.props=o}(e),e.$$typeof=jn,Ln&&Ln(e)};var Hn=h.__r;h.__r=function(e){Hn&&Hn(e),Ct=e.__c};var zn=h.diffed;h.diffed=function(e){zn&&zn(e);var n=e.props,t=e.__e;t!=null&&e.type==="textarea"&&"value"in n&&n.value!==t.value&&(t.value=n.value==null?"":n.value),Ct=null};var ko={ReactCurrentDispatcher:{current:{readContext:function(e){return Ct.__n[e.__c].props.value}}}};function Lo(e){return k.bind(null,e)}function Wn(e){return!!e&&e.$$typeof===jn}function Ho(e){return Wn(e)?bn.apply(null,arguments):e}function Et(e){return!!e.__k&&(ve(null,e),!0)}function zo(e){return e&&(e.base||e.nodeType===1&&e)||null}var Go=function(e,n){return e(n)},Bo=function(e,n){return e(n)},Rt=Z;function Xn(e){e()}function Uo(e){return e}function Ko(){return[!1,Xn]}var jo=te;function qo(e,n){var t=n(),r=A({h:{__:t,v:n}}),o=r[0].h,i=r[1];return te(function(){o.__=t,o.v=n,yt(o.__,n())||i({h:o})},[e,t,n]),L(function(){return yt(o.__,o.v())||i({h:o}),e(function(){yt(o.__,o.v())||i({h:o})})},[e]),t}var b={useState:A,useId:Tn,useReducer:Se,useEffect:L,useLayoutEffect:te,useInsertionEffect:jo,useTransition:Ko,useDeferredValue:Uo,useSyncExternalStore:qo,startTransition:Xn,useRef:q,useImperativeHandle:$n,useMemo:ne,useCallback:le,useContext:In,useDebugValue:Vn,version:"17.0.2",Children:Co,render:wt,hydrate:qn,unmountComponentAtNode:Et,createPortal:Fo,createElement:k,createContext:mt,createFactory:Lo,cloneElement:Ho,createRef:ft,Fragment:Z,isValidElement:Wn,findDOMNode:zo,Component:j,PureComponent:St,memo:bo,forwardRef:wo,flushSync:Bo,unstable_batchedUpdates:Go,StrictMode:Rt,Suspense:We,SuspenseList:Ie,lazy:Ro,__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED:ko};function ce(e,n){return typeof e=="function"?e(n):e}function W(e,n){return t=>{n.setState(r=>({...r,[e]:ce(t,r[e])}))}}function Qe(e){return e instanceof Function}function Wo(e){return Array.isArray(e)&&e.every(n=>typeof n=="number")}function Xo(e,n){let t=[],r=o=>{o.forEach(i=>{t.push(i);let l=n(i);l!=null&&l.length&&r(l)})};return r(e),t}function y(e,n,t){let r=[],o;return()=>{let i;t.key&&t.debug&&(i=Date.now());let l=e();if(!(l.length!==r.length||l.some((d,s)=>r[s]!==d)))return o;r=l;let a;if(t.key&&t.debug&&(a=Date.now()),o=n(...l),t==null||t.onChange==null||t.onChange(o),t.key&&t.debug&&t!=null&&t.debug()){let d=Math.round((Date.now()-i)*100)/100,s=Math.round((Date.now()-a)*100)/100,g=s/16,f=(c,p)=>{for(c=String(c);c.length<p;)c=" "+c;return c};console.info(`%c\u23F1 ${f(s,5)} /${f(d,5)} ms`,`
            font-size: .6rem;
            font-weight: bold;
            color: hsl(${Math.max(0,Math.min(120-120*g,120))}deg 100% 31%);`,t?.key)}return o}}function Yo(e,n,t,r){var o,i;let u={...e._getDefaultColumnDef(),...n},a=u.accessorKey,d=(o=(i=u.id)!=null?i:a?a.replace(".","_"):void 0)!=null?o:typeof u.header=="string"?u.header:void 0,s;if(u.accessorFn?s=u.accessorFn:a&&(a.includes(".")?s=f=>{let c=f;for(let m of a.split(".")){var p;c=(p=c)==null?void 0:p[m]}return c}:s=f=>f[u.accessorKey]),!d)throw new Error;let g={id:`${String(d)}`,accessorFn:s,parent:r,depth:t,columnDef:u,columns:[],getFlatColumns:y(()=>[!0],()=>{var f;return[g,...(f=g.columns)==null?void 0:f.flatMap(c=>c.getFlatColumns())]},{key:"column.getFlatColumns",debug:()=>{var f;return(f=e.options.debugAll)!=null?f:e.options.debugColumns}}),getLeafColumns:y(()=>[e._getOrderColumnsFn()],f=>{var c;if((c=g.columns)!=null&&c.length){let p=g.columns.flatMap(m=>m.getLeafColumns());return f(p)}return[g]},{key:"column.getLeafColumns",debug:()=>{var f;return(f=e.options.debugAll)!=null?f:e.options.debugColumns}})};return g=e._features.reduce((f,c)=>Object.assign(f,c.createColumn==null?void 0:c.createColumn(g,e)),g),g}function Jn(e,n,t){var r;let i={id:(r=t.id)!=null?r:n.id,column:n,index:t.index,isPlaceholder:!!t.isPlaceholder,placeholderId:t.placeholderId,depth:t.depth,subHeaders:[],colSpan:0,rowSpan:0,headerGroup:null,getLeafHeaders:()=>{let l=[],u=a=>{a.subHeaders&&a.subHeaders.length&&a.subHeaders.map(u),l.push(a)};return u(i),l},getContext:()=>({table:e,header:i,column:n})};return e._features.forEach(l=>{Object.assign(i,l.createHeader==null?void 0:l.createHeader(i,e))}),i}var Jo={createTable:e=>({getHeaderGroups:y(()=>[e.getAllColumns(),e.getVisibleLeafColumns(),e.getState().columnPinning.left,e.getState().columnPinning.right],(n,t,r,o)=>{var i,l;let u=(i=r?.map(g=>t.find(f=>f.id===g)).filter(Boolean))!=null?i:[],a=(l=o?.map(g=>t.find(f=>f.id===g)).filter(Boolean))!=null?l:[],d=t.filter(g=>!(r!=null&&r.includes(g.id))&&!(o!=null&&o.includes(g.id)));return Xe(n,[...u,...d,...a],e)},{key:!1,debug:()=>{var n;return(n=e.options.debugAll)!=null?n:e.options.debugHeaders}}),getCenterHeaderGroups:y(()=>[e.getAllColumns(),e.getVisibleLeafColumns(),e.getState().columnPinning.left,e.getState().columnPinning.right],(n,t,r,o)=>(t=t.filter(i=>!(r!=null&&r.includes(i.id))&&!(o!=null&&o.includes(i.id))),Xe(n,t,e,"center")),{key:!1,debug:()=>{var n;return(n=e.options.debugAll)!=null?n:e.options.debugHeaders}}),getLeftHeaderGroups:y(()=>[e.getAllColumns(),e.getVisibleLeafColumns(),e.getState().columnPinning.left],(n,t,r)=>{var o;let i=(o=r?.map(l=>t.find(u=>u.id===l)).filter(Boolean))!=null?o:[];return Xe(n,i,e,"left")},{key:!1,debug:()=>{var n;return(n=e.options.debugAll)!=null?n:e.options.debugHeaders}}),getRightHeaderGroups:y(()=>[e.getAllColumns(),e.getVisibleLeafColumns(),e.getState().columnPinning.right],(n,t,r)=>{var o;let i=(o=r?.map(l=>t.find(u=>u.id===l)).filter(Boolean))!=null?o:[];return Xe(n,i,e,"right")},{key:!1,debug:()=>{var n;return(n=e.options.debugAll)!=null?n:e.options.debugHeaders}}),getFooterGroups:y(()=>[e.getHeaderGroups()],n=>[...n].reverse(),{key:!1,debug:()=>{var n;return(n=e.options.debugAll)!=null?n:e.options.debugHeaders}}),getLeftFooterGroups:y(()=>[e.getLeftHeaderGroups()],n=>[...n].reverse(),{key:!1,debug:()=>{var n;return(n=e.options.debugAll)!=null?n:e.options.debugHeaders}}),getCenterFooterGroups:y(()=>[e.getCenterHeaderGroups()],n=>[...n].reverse(),{key:!1,debug:()=>{var n;return(n=e.options.debugAll)!=null?n:e.options.debugHeaders}}),getRightFooterGroups:y(()=>[e.getRightHeaderGroups()],n=>[...n].reverse(),{key:!1,debug:()=>{var n;return(n=e.options.debugAll)!=null?n:e.options.debugHeaders}}),getFlatHeaders:y(()=>[e.getHeaderGroups()],n=>n.map(t=>t.headers).flat(),{key:!1,debug:()=>{var n;return(n=e.options.debugAll)!=null?n:e.options.debugHeaders}}),getLeftFlatHeaders:y(()=>[e.getLeftHeaderGroups()],n=>n.map(t=>t.headers).flat(),{key:!1,debug:()=>{var n;return(n=e.options.debugAll)!=null?n:e.options.debugHeaders}}),getCenterFlatHeaders:y(()=>[e.getCenterHeaderGroups()],n=>n.map(t=>t.headers).flat(),{key:!1,debug:()=>{var n;return(n=e.options.debugAll)!=null?n:e.options.debugHeaders}}),getRightFlatHeaders:y(()=>[e.getRightHeaderGroups()],n=>n.map(t=>t.headers).flat(),{key:!1,debug:()=>{var n;return(n=e.options.debugAll)!=null?n:e.options.debugHeaders}}),getCenterLeafHeaders:y(()=>[e.getCenterFlatHeaders()],n=>n.filter(t=>{var r;return!((r=t.subHeaders)!=null&&r.length)}),{key:!1,debug:()=>{var n;return(n=e.options.debugAll)!=null?n:e.options.debugHeaders}}),getLeftLeafHeaders:y(()=>[e.getLeftFlatHeaders()],n=>n.filter(t=>{var r;return!((r=t.subHeaders)!=null&&r.length)}),{key:!1,debug:()=>{var n;return(n=e.options.debugAll)!=null?n:e.options.debugHeaders}}),getRightLeafHeaders:y(()=>[e.getRightFlatHeaders()],n=>n.filter(t=>{var r;return!((r=t.subHeaders)!=null&&r.length)}),{key:!1,debug:()=>{var n;return(n=e.options.debugAll)!=null?n:e.options.debugHeaders}}),getLeafHeaders:y(()=>[e.getLeftHeaderGroups(),e.getCenterHeaderGroups(),e.getRightHeaderGroups()],(n,t,r)=>{var o,i,l,u,a,d;return[...(o=(i=n[0])==null?void 0:i.headers)!=null?o:[],...(l=(u=t[0])==null?void 0:u.headers)!=null?l:[],...(a=(d=r[0])==null?void 0:d.headers)!=null?a:[]].map(s=>s.getLeafHeaders()).flat()},{key:!1,debug:()=>{var n;return(n=e.options.debugAll)!=null?n:e.options.debugHeaders}})})};function Xe(e,n,t,r){var o,i;let l=0,u=function(f,c){c===void 0&&(c=1),l=Math.max(l,c),f.filter(p=>p.getIsVisible()).forEach(p=>{var m;(m=p.columns)!=null&&m.length&&u(p.columns,c+1)},0)};u(e);let a=[],d=(f,c)=>{let p={depth:c,id:[r,`${c}`].filter(Boolean).join("_"),headers:[]},m=[];f.forEach(_=>{let v=[...m].reverse()[0],w=_.column.depth===p.depth,E,V=!1;if(w&&_.column.parent?E=_.column.parent:(E=_.column,V=!0),v&&v?.column===E)v.subHeaders.push(_);else{let D=Jn(t,E,{id:[r,c,E.id,_?.id].filter(Boolean).join("_"),isPlaceholder:V,placeholderId:V?`${m.filter(G=>G.column===E).length}`:void 0,depth:c,index:m.length});D.subHeaders.push(_),m.push(D)}p.headers.push(_),_.headerGroup=p}),a.push(p),c>0&&d(m,c-1)},s=n.map((f,c)=>Jn(t,f,{depth:l,index:c}));d(s,l-1),a.reverse();let g=f=>f.filter(p=>p.column.getIsVisible()).map(p=>{let m=0,_=0,v=[0];p.subHeaders&&p.subHeaders.length?(v=[],g(p.subHeaders).forEach(E=>{let{colSpan:V,rowSpan:D}=E;m+=V,v.push(D)})):m=1;let w=Math.min(...v);return _=_+w,p.colSpan=m,p.rowSpan=_,{colSpan:m,rowSpan:_}});return g((o=(i=a[0])==null?void 0:i.headers)!=null?o:[]),a}var Ye={size:150,minSize:20,maxSize:Number.MAX_SAFE_INTEGER},xt=()=>({startOffset:null,startSize:null,deltaOffset:null,deltaPercentage:null,isResizingColumn:!1,columnSizingStart:[]}),Qo={getDefaultColumnDef:()=>Ye,getInitialState:e=>({columnSizing:{},columnSizingInfo:xt(),...e}),getDefaultOptions:e=>({columnResizeMode:"onEnd",onColumnSizingChange:W("columnSizing",e),onColumnSizingInfoChange:W("columnSizingInfo",e)}),createColumn:(e,n)=>({getSize:()=>{var t,r,o;let i=n.getState().columnSizing[e.id];return Math.min(Math.max((t=e.columnDef.minSize)!=null?t:Ye.minSize,(r=i??e.columnDef.size)!=null?r:Ye.size),(o=e.columnDef.maxSize)!=null?o:Ye.maxSize)},getStart:t=>{let r=t?t==="left"?n.getLeftVisibleLeafColumns():n.getRightVisibleLeafColumns():n.getVisibleLeafColumns(),o=r.findIndex(i=>i.id===e.id);if(o>0){let i=r[o-1];return i.getStart(t)+i.getSize()}return 0},resetSize:()=>{n.setColumnSizing(t=>{let{[e.id]:r,...o}=t;return o})},getCanResize:()=>{var t,r;return((t=e.columnDef.enableResizing)!=null?t:!0)&&((r=n.options.enableColumnResizing)!=null?r:!0)},getIsResizing:()=>n.getState().columnSizingInfo.isResizingColumn===e.id}),createHeader:(e,n)=>({getSize:()=>{let t=0,r=o=>{if(o.subHeaders.length)o.subHeaders.forEach(r);else{var i;t+=(i=o.column.getSize())!=null?i:0}};return r(e),t},getStart:()=>{if(e.index>0){let t=e.headerGroup.headers[e.index-1];return t.getStart()+t.getSize()}return 0},getResizeHandler:()=>{let t=n.getColumn(e.column.id),r=t?.getCanResize();return o=>{if(!t||!r||(o.persist==null||o.persist(),Mt(o)&&o.touches&&o.touches.length>1))return;let i=e.getSize(),l=e?e.getLeafHeaders().map(m=>[m.column.id,m.column.getSize()]):[[t.id,t.getSize()]],u=Mt(o)?Math.round(o.touches[0].clientX):o.clientX,a={},d=(m,_)=>{typeof _=="number"&&(n.setColumnSizingInfo(v=>{var w,E;let V=_-((w=v?.startOffset)!=null?w:0),D=Math.max(V/((E=v?.startSize)!=null?E:0),-.999999);return v.columnSizingStart.forEach(G=>{let[re,I]=G;a[re]=Math.round(Math.max(I+I*D,0)*100)/100}),{...v,deltaOffset:V,deltaPercentage:D}}),(n.options.columnResizeMode==="onChange"||m==="end")&&n.setColumnSizing(v=>({...v,...a})))},s=m=>d("move",m),g=m=>{d("end",m),n.setColumnSizingInfo(_=>({..._,isResizingColumn:!1,startOffset:null,startSize:null,deltaOffset:null,deltaPercentage:null,columnSizingStart:[]}))},f={moveHandler:m=>s(m.clientX),upHandler:m=>{document.removeEventListener("mousemove",f.moveHandler),document.removeEventListener("mouseup",f.upHandler),g(m.clientX)}},c={moveHandler:m=>(m.cancelable&&(m.preventDefault(),m.stopPropagation()),s(m.touches[0].clientX),!1),upHandler:m=>{var _;document.removeEventListener("touchmove",c.moveHandler),document.removeEventListener("touchend",c.upHandler),m.cancelable&&(m.preventDefault(),m.stopPropagation()),g((_=m.touches[0])==null?void 0:_.clientX)}},p=Zo()?{passive:!1}:!1;Mt(o)?(document.addEventListener("touchmove",c.moveHandler,p),document.addEventListener("touchend",c.upHandler,p)):(document.addEventListener("mousemove",f.moveHandler,p),document.addEventListener("mouseup",f.upHandler,p)),n.setColumnSizingInfo(m=>({...m,startOffset:u,startSize:i,deltaOffset:0,deltaPercentage:0,columnSizingStart:l,isResizingColumn:t.id}))}}}),createTable:e=>({setColumnSizing:n=>e.options.onColumnSizingChange==null?void 0:e.options.onColumnSizingChange(n),setColumnSizingInfo:n=>e.options.onColumnSizingInfoChange==null?void 0:e.options.onColumnSizingInfoChange(n),resetColumnSizing:n=>{var t;e.setColumnSizing(n?{}:(t=e.initialState.columnSizing)!=null?t:{})},resetHeaderSizeInfo:n=>{var t;e.setColumnSizingInfo(n?xt():(t=e.initialState.columnSizingInfo)!=null?t:xt())},getTotalSize:()=>{var n,t;return(n=(t=e.getHeaderGroups()[0])==null?void 0:t.headers.reduce((r,o)=>r+o.getSize(),0))!=null?n:0},getLeftTotalSize:()=>{var n,t;return(n=(t=e.getLeftHeaderGroups()[0])==null?void 0:t.headers.reduce((r,o)=>r+o.getSize(),0))!=null?n:0},getCenterTotalSize:()=>{var n,t;return(n=(t=e.getCenterHeaderGroups()[0])==null?void 0:t.headers.reduce((r,o)=>r+o.getSize(),0))!=null?n:0},getRightTotalSize:()=>{var n,t;return(n=(t=e.getRightHeaderGroups()[0])==null?void 0:t.headers.reduce((r,o)=>r+o.getSize(),0))!=null?n:0}})},Je=null;function Zo(){if(typeof Je=="boolean")return Je;let e=!1;try{let n={get passive(){return e=!0,!1}},t=()=>{};window.addEventListener("test",t,n),window.removeEventListener("test",t)}catch{e=!1}return Je=e,Je}function Mt(e){return e.type==="touchstart"}var ei={getInitialState:e=>({expanded:{},...e}),getDefaultOptions:e=>({onExpandedChange:W("expanded",e),paginateExpandedRows:!0}),createTable:e=>{let n=!1,t=!1;return{_autoResetExpanded:()=>{var r,o;if(!n){e._queue(()=>{n=!0});return}if((r=(o=e.options.autoResetAll)!=null?o:e.options.autoResetExpanded)!=null?r:!e.options.manualExpanding){if(t)return;t=!0,e._queue(()=>{e.resetExpanded(),t=!1})}},setExpanded:r=>e.options.onExpandedChange==null?void 0:e.options.onExpandedChange(r),toggleAllRowsExpanded:r=>{r??!e.getIsAllRowsExpanded()?e.setExpanded(!0):e.setExpanded({})},resetExpanded:r=>{var o,i;e.setExpanded(r?{}:(o=(i=e.initialState)==null?void 0:i.expanded)!=null?o:{})},getCanSomeRowsExpand:()=>e.getPrePaginationRowModel().flatRows.some(r=>r.getCanExpand()),getToggleAllRowsExpandedHandler:()=>r=>{r.persist==null||r.persist(),e.toggleAllRowsExpanded()},getIsSomeRowsExpanded:()=>{let r=e.getState().expanded;return r===!0||Object.values(r).some(Boolean)},getIsAllRowsExpanded:()=>{let r=e.getState().expanded;return typeof r=="boolean"?r===!0:!(!Object.keys(r).length||e.getRowModel().flatRows.some(o=>!o.getIsExpanded()))},getExpandedDepth:()=>{let r=0;return(e.getState().expanded===!0?Object.keys(e.getRowModel().rowsById):Object.keys(e.getState().expanded)).forEach(i=>{let l=i.split(".");r=Math.max(r,l.length)}),r},getPreExpandedRowModel:()=>e.getSortedRowModel(),getExpandedRowModel:()=>(!e._getExpandedRowModel&&e.options.getExpandedRowModel&&(e._getExpandedRowModel=e.options.getExpandedRowModel(e)),e.options.manualExpanding||!e._getExpandedRowModel?e.getPreExpandedRowModel():e._getExpandedRowModel())}},createRow:(e,n)=>({toggleExpanded:t=>{n.setExpanded(r=>{var o;let i=r===!0?!0:!!(r!=null&&r[e.id]),l={};if(r===!0?Object.keys(n.getRowModel().rowsById).forEach(u=>{l[u]=!0}):l=r,t=(o=t)!=null?o:!i,!i&&t)return{...l,[e.id]:!0};if(i&&!t){let{[e.id]:u,...a}=l;return a}return r})},getIsExpanded:()=>{var t;let r=n.getState().expanded;return!!((t=n.options.getIsRowExpanded==null?void 0:n.options.getIsRowExpanded(e))!=null?t:r===!0||r?.[e.id])},getCanExpand:()=>{var t,r,o;return(t=n.options.getRowCanExpand==null?void 0:n.options.getRowCanExpand(e))!=null?t:((r=n.options.enableExpanding)!=null?r:!0)&&!!((o=e.subRows)!=null&&o.length)},getToggleExpandedHandler:()=>{let t=e.getCanExpand();return()=>{t&&e.toggleExpanded()}}})},tr=(e,n,t)=>{var r,o,i;let l=t.toLowerCase();return!!(!((r=e.getValue(n))==null||(o=r.toString())==null||(i=o.toLowerCase())==null)&&i.includes(l))};tr.autoRemove=e=>J(e);var nr=(e,n,t)=>{var r,o;return!!(!((r=e.getValue(n))==null||(o=r.toString())==null)&&o.includes(t))};nr.autoRemove=e=>J(e);var rr=(e,n,t)=>{var r,o;return((r=e.getValue(n))==null||(o=r.toString())==null?void 0:o.toLowerCase())===t?.toLowerCase()};rr.autoRemove=e=>J(e);var or=(e,n,t)=>{var r;return(r=e.getValue(n))==null?void 0:r.includes(t)};or.autoRemove=e=>J(e)||!(e!=null&&e.length);var ir=(e,n,t)=>!t.some(r=>{var o;return!((o=e.getValue(n))!=null&&o.includes(r))});ir.autoRemove=e=>J(e)||!(e!=null&&e.length);var lr=(e,n,t)=>t.some(r=>{var o;return(o=e.getValue(n))==null?void 0:o.includes(r)});lr.autoRemove=e=>J(e)||!(e!=null&&e.length);var sr=(e,n,t)=>e.getValue(n)===t;sr.autoRemove=e=>J(e);var ar=(e,n,t)=>e.getValue(n)==t;ar.autoRemove=e=>J(e);var Nt=(e,n,t)=>{let[r,o]=t,i=e.getValue(n);return i>=r&&i<=o};Nt.resolveFilterValue=e=>{let[n,t]=e,r=typeof n!="number"?parseFloat(n):n,o=typeof t!="number"?parseFloat(t):t,i=n===null||Number.isNaN(r)?-1/0:r,l=t===null||Number.isNaN(o)?1/0:o;if(i>l){let u=i;i=l,l=u}return[i,l]};Nt.autoRemove=e=>J(e)||J(e[0])&&J(e[1]);var se={includesString:tr,includesStringSensitive:nr,equalsString:rr,arrIncludes:or,arrIncludesAll:ir,arrIncludesSome:lr,equals:sr,weakEquals:ar,inNumberRange:Nt};function J(e){return e==null||e===""}var ti={getDefaultColumnDef:()=>({filterFn:"auto"}),getInitialState:e=>({columnFilters:[],globalFilter:void 0,...e}),getDefaultOptions:e=>({onColumnFiltersChange:W("columnFilters",e),onGlobalFilterChange:W("globalFilter",e),filterFromLeafRows:!1,maxLeafRowFilterDepth:100,globalFilterFn:"auto",getColumnCanGlobalFilter:n=>{var t,r;let o=(t=e.getCoreRowModel().flatRows[0])==null||(r=t._getAllCellsByColumnId()[n.id])==null?void 0:r.getValue();return typeof o=="string"||typeof o=="number"}}),createColumn:(e,n)=>({getAutoFilterFn:()=>{let t=n.getCoreRowModel().flatRows[0],r=t?.getValue(e.id);return typeof r=="string"?se.includesString:typeof r=="number"?se.inNumberRange:typeof r=="boolean"||r!==null&&typeof r=="object"?se.equals:Array.isArray(r)?se.arrIncludes:se.weakEquals},getFilterFn:()=>{var t,r;return Qe(e.columnDef.filterFn)?e.columnDef.filterFn:e.columnDef.filterFn==="auto"?e.getAutoFilterFn():(t=(r=n.options.filterFns)==null?void 0:r[e.columnDef.filterFn])!=null?t:se[e.columnDef.filterFn]},getCanFilter:()=>{var t,r,o;return((t=e.columnDef.enableColumnFilter)!=null?t:!0)&&((r=n.options.enableColumnFilters)!=null?r:!0)&&((o=n.options.enableFilters)!=null?o:!0)&&!!e.accessorFn},getCanGlobalFilter:()=>{var t,r,o,i;return((t=e.columnDef.enableGlobalFilter)!=null?t:!0)&&((r=n.options.enableGlobalFilter)!=null?r:!0)&&((o=n.options.enableFilters)!=null?o:!0)&&((i=n.options.getColumnCanGlobalFilter==null?void 0:n.options.getColumnCanGlobalFilter(e))!=null?i:!0)&&!!e.accessorFn},getIsFiltered:()=>e.getFilterIndex()>-1,getFilterValue:()=>{var t,r;return(t=n.getState().columnFilters)==null||(r=t.find(o=>o.id===e.id))==null?void 0:r.value},getFilterIndex:()=>{var t,r;return(t=(r=n.getState().columnFilters)==null?void 0:r.findIndex(o=>o.id===e.id))!=null?t:-1},setFilterValue:t=>{n.setColumnFilters(r=>{let o=e.getFilterFn(),i=r?.find(s=>s.id===e.id),l=ce(t,i?i.value:void 0);if(Qn(o,l,e)){var u;return(u=r?.filter(s=>s.id!==e.id))!=null?u:[]}let a={id:e.id,value:l};if(i){var d;return(d=r?.map(s=>s.id===e.id?a:s))!=null?d:[]}return r!=null&&r.length?[...r,a]:[a]})},_getFacetedRowModel:n.options.getFacetedRowModel&&n.options.getFacetedRowModel(n,e.id),getFacetedRowModel:()=>e._getFacetedRowModel?e._getFacetedRowModel():n.getPreFilteredRowModel(),_getFacetedUniqueValues:n.options.getFacetedUniqueValues&&n.options.getFacetedUniqueValues(n,e.id),getFacetedUniqueValues:()=>e._getFacetedUniqueValues?e._getFacetedUniqueValues():new Map,_getFacetedMinMaxValues:n.options.getFacetedMinMaxValues&&n.options.getFacetedMinMaxValues(n,e.id),getFacetedMinMaxValues:()=>{if(e._getFacetedMinMaxValues)return e._getFacetedMinMaxValues()}}),createRow:(e,n)=>({columnFilters:{},columnFiltersMeta:{}}),createTable:e=>({getGlobalAutoFilterFn:()=>se.includesString,getGlobalFilterFn:()=>{var n,t;let{globalFilterFn:r}=e.options;return Qe(r)?r:r==="auto"?e.getGlobalAutoFilterFn():(n=(t=e.options.filterFns)==null?void 0:t[r])!=null?n:se[r]},setColumnFilters:n=>{let t=e.getAllLeafColumns(),r=o=>{var i;return(i=ce(n,o))==null?void 0:i.filter(l=>{let u=t.find(a=>a.id===l.id);if(u){let a=u.getFilterFn();if(Qn(a,l.value,u))return!1}return!0})};e.options.onColumnFiltersChange==null||e.options.onColumnFiltersChange(r)},setGlobalFilter:n=>{e.options.onGlobalFilterChange==null||e.options.onGlobalFilterChange(n)},resetGlobalFilter:n=>{e.setGlobalFilter(n?void 0:e.initialState.globalFilter)},resetColumnFilters:n=>{var t,r;e.setColumnFilters(n?[]:(t=(r=e.initialState)==null?void 0:r.columnFilters)!=null?t:[])},getPreFilteredRowModel:()=>e.getCoreRowModel(),getFilteredRowModel:()=>(!e._getFilteredRowModel&&e.options.getFilteredRowModel&&(e._getFilteredRowModel=e.options.getFilteredRowModel(e)),e.options.manualFiltering||!e._getFilteredRowModel?e.getPreFilteredRowModel():e._getFilteredRowModel()),_getGlobalFacetedRowModel:e.options.getFacetedRowModel&&e.options.getFacetedRowModel(e,"__global__"),getGlobalFacetedRowModel:()=>e.options.manualFiltering||!e._getGlobalFacetedRowModel?e.getPreFilteredRowModel():e._getGlobalFacetedRowModel(),_getGlobalFacetedUniqueValues:e.options.getFacetedUniqueValues&&e.options.getFacetedUniqueValues(e,"__global__"),getGlobalFacetedUniqueValues:()=>e._getGlobalFacetedUniqueValues?e._getGlobalFacetedUniqueValues():new Map,_getGlobalFacetedMinMaxValues:e.options.getFacetedMinMaxValues&&e.options.getFacetedMinMaxValues(e,"__global__"),getGlobalFacetedMinMaxValues:()=>{if(e._getGlobalFacetedMinMaxValues)return e._getGlobalFacetedMinMaxValues()}})};function Qn(e,n,t){return(e&&e.autoRemove?e.autoRemove(n,t):!1)||typeof n>"u"||typeof n=="string"&&!n}var ni=(e,n,t)=>t.reduce((r,o)=>{let i=o.getValue(e);return r+(typeof i=="number"?i:0)},0),ri=(e,n,t)=>{let r;return t.forEach(o=>{let i=o.getValue(e);i!=null&&(r>i||r===void 0&&i>=i)&&(r=i)}),r},oi=(e,n,t)=>{let r;return t.forEach(o=>{let i=o.getValue(e);i!=null&&(r<i||r===void 0&&i>=i)&&(r=i)}),r},ii=(e,n,t)=>{let r,o;return t.forEach(i=>{let l=i.getValue(e);l!=null&&(r===void 0?l>=l&&(r=o=l):(r>l&&(r=l),o<l&&(o=l)))}),[r,o]},li=(e,n)=>{let t=0,r=0;if(n.forEach(o=>{let i=o.getValue(e);i!=null&&(i=+i)>=i&&(++t,r+=i)}),t)return r/t},si=(e,n)=>{if(!n.length)return;let t=n.map(i=>i.getValue(e));if(!Wo(t))return;if(t.length===1)return t[0];let r=Math.floor(t.length/2),o=t.sort((i,l)=>i-l);return t.length%2!==0?o[r]:(o[r-1]+o[r])/2},ai=(e,n)=>Array.from(new Set(n.map(t=>t.getValue(e))).values()),ui=(e,n)=>new Set(n.map(t=>t.getValue(e))).size,di=(e,n)=>n.length,Ft={sum:ni,min:ri,max:oi,extent:ii,mean:li,median:si,unique:ai,uniqueCount:ui,count:di},ci={getDefaultColumnDef:()=>({aggregatedCell:e=>{var n,t;return(n=(t=e.getValue())==null||t.toString==null?void 0:t.toString())!=null?n:null},aggregationFn:"auto"}),getInitialState:e=>({grouping:[],...e}),getDefaultOptions:e=>({onGroupingChange:W("grouping",e),groupedColumnMode:"reorder"}),createColumn:(e,n)=>({toggleGrouping:()=>{n.setGrouping(t=>t!=null&&t.includes(e.id)?t.filter(r=>r!==e.id):[...t??[],e.id])},getCanGroup:()=>{var t,r,o,i;return(t=(r=(o=(i=e.columnDef.enableGrouping)!=null?i:!0)!=null?o:n.options.enableGrouping)!=null?r:!0)!=null?t:!!e.accessorFn},getIsGrouped:()=>{var t;return(t=n.getState().grouping)==null?void 0:t.includes(e.id)},getGroupedIndex:()=>{var t;return(t=n.getState().grouping)==null?void 0:t.indexOf(e.id)},getToggleGroupingHandler:()=>{let t=e.getCanGroup();return()=>{t&&e.toggleGrouping()}},getAutoAggregationFn:()=>{let t=n.getCoreRowModel().flatRows[0],r=t?.getValue(e.id);if(typeof r=="number")return Ft.sum;if(Object.prototype.toString.call(r)==="[object Date]")return Ft.extent},getAggregationFn:()=>{var t,r;if(!e)throw new Error;return Qe(e.columnDef.aggregationFn)?e.columnDef.aggregationFn:e.columnDef.aggregationFn==="auto"?e.getAutoAggregationFn():(t=(r=n.options.aggregationFns)==null?void 0:r[e.columnDef.aggregationFn])!=null?t:Ft[e.columnDef.aggregationFn]}}),createTable:e=>({setGrouping:n=>e.options.onGroupingChange==null?void 0:e.options.onGroupingChange(n),resetGrouping:n=>{var t,r;e.setGrouping(n?[]:(t=(r=e.initialState)==null?void 0:r.grouping)!=null?t:[])},getPreGroupedRowModel:()=>e.getFilteredRowModel(),getGroupedRowModel:()=>(!e._getGroupedRowModel&&e.options.getGroupedRowModel&&(e._getGroupedRowModel=e.options.getGroupedRowModel(e)),e.options.manualGrouping||!e._getGroupedRowModel?e.getPreGroupedRowModel():e._getGroupedRowModel())}),createRow:(e,n)=>({getIsGrouped:()=>!!e.groupingColumnId,getGroupingValue:t=>{if(e._groupingValuesCache.hasOwnProperty(t))return e._groupingValuesCache[t];let r=n.getColumn(t);return r!=null&&r.columnDef.getGroupingValue?(e._groupingValuesCache[t]=r.columnDef.getGroupingValue(e.original),e._groupingValuesCache[t]):e.getValue(t)},_groupingValuesCache:{}}),createCell:(e,n,t,r)=>({getIsGrouped:()=>n.getIsGrouped()&&n.id===t.groupingColumnId,getIsPlaceholder:()=>!e.getIsGrouped()&&n.getIsGrouped(),getIsAggregated:()=>{var o;return!e.getIsGrouped()&&!e.getIsPlaceholder()&&!!((o=t.subRows)!=null&&o.length)}})};function fi(e,n,t){if(!(n!=null&&n.length)||!t)return e;let r=e.filter(i=>!n.includes(i.id));return t==="remove"?r:[...n.map(i=>e.find(l=>l.id===i)).filter(Boolean),...r]}var gi={getInitialState:e=>({columnOrder:[],...e}),getDefaultOptions:e=>({onColumnOrderChange:W("columnOrder",e)}),createTable:e=>({setColumnOrder:n=>e.options.onColumnOrderChange==null?void 0:e.options.onColumnOrderChange(n),resetColumnOrder:n=>{var t;e.setColumnOrder(n?[]:(t=e.initialState.columnOrder)!=null?t:[])},_getOrderColumnsFn:y(()=>[e.getState().columnOrder,e.getState().grouping,e.options.groupedColumnMode],(n,t,r)=>o=>{let i=[];if(!(n!=null&&n.length))i=o;else{let l=[...n],u=[...o];for(;u.length&&l.length;){let a=l.shift(),d=u.findIndex(s=>s.id===a);d>-1&&i.push(u.splice(d,1)[0])}i=[...i,...u]}return fi(i,t,r)},{key:!1})})},Tt=0,Dt=10,$t=()=>({pageIndex:Tt,pageSize:Dt}),pi={getInitialState:e=>({...e,pagination:{...$t(),...e?.pagination}}),getDefaultOptions:e=>({onPaginationChange:W("pagination",e)}),createTable:e=>{let n=!1,t=!1;return{_autoResetPageIndex:()=>{var r,o;if(!n){e._queue(()=>{n=!0});return}if((r=(o=e.options.autoResetAll)!=null?o:e.options.autoResetPageIndex)!=null?r:!e.options.manualPagination){if(t)return;t=!0,e._queue(()=>{e.resetPageIndex(),t=!1})}},setPagination:r=>{let o=i=>ce(r,i);return e.options.onPaginationChange==null?void 0:e.options.onPaginationChange(o)},resetPagination:r=>{var o;e.setPagination(r?$t():(o=e.initialState.pagination)!=null?o:$t())},setPageIndex:r=>{e.setPagination(o=>{let i=ce(r,o.pageIndex),l=typeof e.options.pageCount>"u"||e.options.pageCount===-1?Number.MAX_SAFE_INTEGER:e.options.pageCount-1;return i=Math.max(0,Math.min(i,l)),{...o,pageIndex:i}})},resetPageIndex:r=>{var o,i,l;e.setPageIndex(r?Tt:(o=(i=e.initialState)==null||(l=i.pagination)==null?void 0:l.pageIndex)!=null?o:Tt)},resetPageSize:r=>{var o,i,l;e.setPageSize(r?Dt:(o=(i=e.initialState)==null||(l=i.pagination)==null?void 0:l.pageSize)!=null?o:Dt)},setPageSize:r=>{e.setPagination(o=>{let i=Math.max(1,ce(r,o.pageSize)),l=o.pageSize*o.pageIndex,u=Math.floor(l/i);return{...o,pageIndex:u,pageSize:i}})},setPageCount:r=>e.setPagination(o=>{var i;let l=ce(r,(i=e.options.pageCount)!=null?i:-1);return typeof l=="number"&&(l=Math.max(-1,l)),{...o,pageCount:l}}),getPageOptions:y(()=>[e.getPageCount()],r=>{let o=[];return r&&r>0&&(o=[...new Array(r)].fill(null).map((i,l)=>l)),o},{key:!1,debug:()=>{var r;return(r=e.options.debugAll)!=null?r:e.options.debugTable}}),getCanPreviousPage:()=>e.getState().pagination.pageIndex>0,getCanNextPage:()=>{let{pageIndex:r}=e.getState().pagination,o=e.getPageCount();return o===-1?!0:o===0?!1:r<o-1},previousPage:()=>e.setPageIndex(r=>r-1),nextPage:()=>e.setPageIndex(r=>r+1),getPrePaginationRowModel:()=>e.getExpandedRowModel(),getPaginationRowModel:()=>(!e._getPaginationRowModel&&e.options.getPaginationRowModel&&(e._getPaginationRowModel=e.options.getPaginationRowModel(e)),e.options.manualPagination||!e._getPaginationRowModel?e.getPrePaginationRowModel():e._getPaginationRowModel()),getPageCount:()=>{var r;return(r=e.options.pageCount)!=null?r:Math.ceil(e.getPrePaginationRowModel().rows.length/e.getState().pagination.pageSize)}}}},It=()=>({left:[],right:[]}),mi={getInitialState:e=>({columnPinning:It(),...e}),getDefaultOptions:e=>({onColumnPinningChange:W("columnPinning",e)}),createColumn:(e,n)=>({pin:t=>{let r=e.getLeafColumns().map(o=>o.id).filter(Boolean);n.setColumnPinning(o=>{var i,l;if(t==="right"){var u,a;return{left:((u=o?.left)!=null?u:[]).filter(g=>!(r!=null&&r.includes(g))),right:[...((a=o?.right)!=null?a:[]).filter(g=>!(r!=null&&r.includes(g))),...r]}}if(t==="left"){var d,s;return{left:[...((d=o?.left)!=null?d:[]).filter(g=>!(r!=null&&r.includes(g))),...r],right:((s=o?.right)!=null?s:[]).filter(g=>!(r!=null&&r.includes(g)))}}return{left:((i=o?.left)!=null?i:[]).filter(g=>!(r!=null&&r.includes(g))),right:((l=o?.right)!=null?l:[]).filter(g=>!(r!=null&&r.includes(g)))}})},getCanPin:()=>e.getLeafColumns().some(r=>{var o,i;return((o=r.columnDef.enablePinning)!=null?o:!0)&&((i=n.options.enablePinning)!=null?i:!0)}),getIsPinned:()=>{let t=e.getLeafColumns().map(u=>u.id),{left:r,right:o}=n.getState().columnPinning,i=t.some(u=>r?.includes(u)),l=t.some(u=>o?.includes(u));return i?"left":l?"right":!1},getPinnedIndex:()=>{var t,r,o;let i=e.getIsPinned();return i?(t=(r=n.getState().columnPinning)==null||(o=r[i])==null?void 0:o.indexOf(e.id))!=null?t:-1:0}}),createRow:(e,n)=>({getCenterVisibleCells:y(()=>[e._getAllVisibleCells(),n.getState().columnPinning.left,n.getState().columnPinning.right],(t,r,o)=>{let i=[...r??[],...o??[]];return t.filter(l=>!i.includes(l.column.id))},{key:"row.getCenterVisibleCells",debug:()=>{var t;return(t=n.options.debugAll)!=null?t:n.options.debugRows}}),getLeftVisibleCells:y(()=>[e._getAllVisibleCells(),n.getState().columnPinning.left,,],(t,r)=>(r??[]).map(i=>t.find(l=>l.column.id===i)).filter(Boolean).map(i=>({...i,position:"left"})),{key:"row.getLeftVisibleCells",debug:()=>{var t;return(t=n.options.debugAll)!=null?t:n.options.debugRows}}),getRightVisibleCells:y(()=>[e._getAllVisibleCells(),n.getState().columnPinning.right],(t,r)=>(r??[]).map(i=>t.find(l=>l.column.id===i)).filter(Boolean).map(i=>({...i,position:"right"})),{key:"row.getRightVisibleCells",debug:()=>{var t;return(t=n.options.debugAll)!=null?t:n.options.debugRows}})}),createTable:e=>({setColumnPinning:n=>e.options.onColumnPinningChange==null?void 0:e.options.onColumnPinningChange(n),resetColumnPinning:n=>{var t,r;return e.setColumnPinning(n?It():(t=(r=e.initialState)==null?void 0:r.columnPinning)!=null?t:It())},getIsSomeColumnsPinned:n=>{var t;let r=e.getState().columnPinning;if(!n){var o,i;return!!((o=r.left)!=null&&o.length||(i=r.right)!=null&&i.length)}return!!((t=r[n])!=null&&t.length)},getLeftLeafColumns:y(()=>[e.getAllLeafColumns(),e.getState().columnPinning.left],(n,t)=>(t??[]).map(r=>n.find(o=>o.id===r)).filter(Boolean),{key:!1,debug:()=>{var n;return(n=e.options.debugAll)!=null?n:e.options.debugColumns}}),getRightLeafColumns:y(()=>[e.getAllLeafColumns(),e.getState().columnPinning.right],(n,t)=>(t??[]).map(r=>n.find(o=>o.id===r)).filter(Boolean),{key:!1,debug:()=>{var n;return(n=e.options.debugAll)!=null?n:e.options.debugColumns}}),getCenterLeafColumns:y(()=>[e.getAllLeafColumns(),e.getState().columnPinning.left,e.getState().columnPinning.right],(n,t,r)=>{let o=[...t??[],...r??[]];return n.filter(i=>!o.includes(i.id))},{key:!1,debug:()=>{var n;return(n=e.options.debugAll)!=null?n:e.options.debugColumns}})})},_i={getInitialState:e=>({rowSelection:{},...e}),getDefaultOptions:e=>({onRowSelectionChange:W("rowSelection",e),enableRowSelection:!0,enableMultiRowSelection:!0,enableSubRowSelection:!0}),createTable:e=>({setRowSelection:n=>e.options.onRowSelectionChange==null?void 0:e.options.onRowSelectionChange(n),resetRowSelection:n=>{var t;return e.setRowSelection(n?{}:(t=e.initialState.rowSelection)!=null?t:{})},toggleAllRowsSelected:n=>{e.setRowSelection(t=>{n=typeof n<"u"?n:!e.getIsAllRowsSelected();let r={...t},o=e.getPreGroupedRowModel().flatRows;return n?o.forEach(i=>{i.getCanSelect()&&(r[i.id]=!0)}):o.forEach(i=>{delete r[i.id]}),r})},toggleAllPageRowsSelected:n=>e.setRowSelection(t=>{let r=typeof n<"u"?n:!e.getIsAllPageRowsSelected(),o={...t};return e.getRowModel().rows.forEach(i=>{Ot(o,i.id,r,e)}),o}),getPreSelectedRowModel:()=>e.getCoreRowModel(),getSelectedRowModel:y(()=>[e.getState().rowSelection,e.getCoreRowModel()],(n,t)=>Object.keys(n).length?Vt(e,t):{rows:[],flatRows:[],rowsById:{}},{key:!1,debug:()=>{var n;return(n=e.options.debugAll)!=null?n:e.options.debugTable}}),getFilteredSelectedRowModel:y(()=>[e.getState().rowSelection,e.getFilteredRowModel()],(n,t)=>Object.keys(n).length?Vt(e,t):{rows:[],flatRows:[],rowsById:{}},{key:"getFilteredSelectedRowModel",debug:()=>{var n;return(n=e.options.debugAll)!=null?n:e.options.debugTable}}),getGroupedSelectedRowModel:y(()=>[e.getState().rowSelection,e.getSortedRowModel()],(n,t)=>Object.keys(n).length?Vt(e,t):{rows:[],flatRows:[],rowsById:{}},{key:"getGroupedSelectedRowModel",debug:()=>{var n;return(n=e.options.debugAll)!=null?n:e.options.debugTable}}),getIsAllRowsSelected:()=>{let n=e.getFilteredRowModel().flatRows,{rowSelection:t}=e.getState(),r=!!(n.length&&Object.keys(t).length);return r&&n.some(o=>o.getCanSelect()&&!t[o.id])&&(r=!1),r},getIsAllPageRowsSelected:()=>{let n=e.getPaginationRowModel().flatRows.filter(o=>o.getCanSelect()),{rowSelection:t}=e.getState(),r=!!n.length;return r&&n.some(o=>!t[o.id])&&(r=!1),r},getIsSomeRowsSelected:()=>{var n;let t=Object.keys((n=e.getState().rowSelection)!=null?n:{}).length;return t>0&&t<e.getFilteredRowModel().flatRows.length},getIsSomePageRowsSelected:()=>{let n=e.getPaginationRowModel().flatRows;return e.getIsAllPageRowsSelected()?!1:n.filter(t=>t.getCanSelect()).some(t=>t.getIsSelected()||t.getIsSomeSelected())},getToggleAllRowsSelectedHandler:()=>n=>{e.toggleAllRowsSelected(n.target.checked)},getToggleAllPageRowsSelectedHandler:()=>n=>{e.toggleAllPageRowsSelected(n.target.checked)}}),createRow:(e,n)=>({toggleSelected:t=>{let r=e.getIsSelected();n.setRowSelection(o=>{if(t=typeof t<"u"?t:!r,r===t)return o;let i={...o};return Ot(i,e.id,t,n),i})},getIsSelected:()=>{let{rowSelection:t}=n.getState();return Pt(e,t)},getIsSomeSelected:()=>{let{rowSelection:t}=n.getState();return Zn(e,t)==="some"},getIsAllSubRowsSelected:()=>{let{rowSelection:t}=n.getState();return Zn(e,t)==="all"},getCanSelect:()=>{var t;return typeof n.options.enableRowSelection=="function"?n.options.enableRowSelection(e):(t=n.options.enableRowSelection)!=null?t:!0},getCanSelectSubRows:()=>{var t;return typeof n.options.enableSubRowSelection=="function"?n.options.enableSubRowSelection(e):(t=n.options.enableSubRowSelection)!=null?t:!0},getCanMultiSelect:()=>{var t;return typeof n.options.enableMultiRowSelection=="function"?n.options.enableMultiRowSelection(e):(t=n.options.enableMultiRowSelection)!=null?t:!0},getToggleSelectedHandler:()=>{let t=e.getCanSelect();return r=>{var o;t&&e.toggleSelected((o=r.target)==null?void 0:o.checked)}}})},Ot=(e,n,t,r)=>{var o;let i=r.getRow(n);t?(i.getCanMultiSelect()||Object.keys(e).forEach(l=>delete e[l]),i.getCanSelect()&&(e[n]=!0)):delete e[n],(o=i.subRows)!=null&&o.length&&i.getCanSelectSubRows()&&i.subRows.forEach(l=>Ot(e,l.id,t,r))};function Vt(e,n){let t=e.getState().rowSelection,r=[],o={},i=function(l,u){return l.map(a=>{var d;let s=Pt(a,t);if(s&&(r.push(a),o[a.id]=a),(d=a.subRows)!=null&&d.length&&(a={...a,subRows:i(a.subRows)}),s)return a}).filter(Boolean)};return{rows:i(n.rows),flatRows:r,rowsById:o}}function Pt(e,n){var t;return(t=n[e.id])!=null?t:!1}function Zn(e,n,t){if(e.subRows&&e.subRows.length){let r=!0,o=!1;return e.subRows.forEach(i=>{o&&!r||(Pt(i,n)?o=!0:r=!1)}),r?"all":o?"some":!1}return!1}var At=/([0-9]+)/gm,hi=(e,n,t)=>ur(fe(e.getValue(t)).toLowerCase(),fe(n.getValue(t)).toLowerCase()),vi=(e,n,t)=>ur(fe(e.getValue(t)),fe(n.getValue(t))),yi=(e,n,t)=>kt(fe(e.getValue(t)).toLowerCase(),fe(n.getValue(t)).toLowerCase()),bi=(e,n,t)=>kt(fe(e.getValue(t)),fe(n.getValue(t))),Si=(e,n,t)=>{let r=e.getValue(t),o=n.getValue(t);return r>o?1:r<o?-1:0},wi=(e,n,t)=>kt(e.getValue(t),n.getValue(t));function kt(e,n){return e===n?0:e>n?1:-1}function fe(e){return typeof e=="number"?isNaN(e)||e===1/0||e===-1/0?"":String(e):typeof e=="string"?e:""}function ur(e,n){let t=e.split(At).filter(Boolean),r=n.split(At).filter(Boolean);for(;t.length&&r.length;){let o=t.shift(),i=r.shift(),l=parseInt(o,10),u=parseInt(i,10),a=[l,u].sort();if(isNaN(a[0])){if(o>i)return 1;if(i>o)return-1;continue}if(isNaN(a[1]))return isNaN(l)?-1:1;if(l>u)return 1;if(u>l)return-1}return t.length-r.length}var Ve={alphanumeric:hi,alphanumericCaseSensitive:vi,text:yi,textCaseSensitive:bi,datetime:Si,basic:wi},Ci={getInitialState:e=>({sorting:[],...e}),getDefaultColumnDef:()=>({sortingFn:"auto",sortUndefined:1}),getDefaultOptions:e=>({onSortingChange:W("sorting",e),isMultiSortEvent:n=>n.shiftKey}),createColumn:(e,n)=>({getAutoSortingFn:()=>{let t=n.getFilteredRowModel().flatRows.slice(10),r=!1;for(let o of t){let i=o?.getValue(e.id);if(Object.prototype.toString.call(i)==="[object Date]")return Ve.datetime;if(typeof i=="string"&&(r=!0,i.split(At).length>1))return Ve.alphanumeric}return r?Ve.text:Ve.basic},getAutoSortDir:()=>{let t=n.getFilteredRowModel().flatRows[0];return typeof t?.getValue(e.id)=="string"?"asc":"desc"},getSortingFn:()=>{var t,r;if(!e)throw new Error;return Qe(e.columnDef.sortingFn)?e.columnDef.sortingFn:e.columnDef.sortingFn==="auto"?e.getAutoSortingFn():(t=(r=n.options.sortingFns)==null?void 0:r[e.columnDef.sortingFn])!=null?t:Ve[e.columnDef.sortingFn]},toggleSorting:(t,r)=>{let o=e.getNextSortingOrder(),i=typeof t<"u"&&t!==null;n.setSorting(l=>{let u=l?.find(c=>c.id===e.id),a=l?.findIndex(c=>c.id===e.id),d=[],s,g=i?t:o==="desc";if(l!=null&&l.length&&e.getCanMultiSort()&&r?u?s="toggle":s="add":l!=null&&l.length&&a!==l.length-1?s="replace":u?s="toggle":s="replace",s==="toggle"&&(i||o||(s="remove")),s==="add"){var f;d=[...l,{id:e.id,desc:g}],d.splice(0,d.length-((f=n.options.maxMultiSortColCount)!=null?f:Number.MAX_SAFE_INTEGER))}else s==="toggle"?d=l.map(c=>c.id===e.id?{...c,desc:g}:c):s==="remove"?d=l.filter(c=>c.id!==e.id):d=[{id:e.id,desc:g}];return d})},getFirstSortDir:()=>{var t,r;return((t=(r=e.columnDef.sortDescFirst)!=null?r:n.options.sortDescFirst)!=null?t:e.getAutoSortDir()==="desc")?"desc":"asc"},getNextSortingOrder:t=>{var r,o;let i=e.getFirstSortDir(),l=e.getIsSorted();return l?l!==i&&((r=n.options.enableSortingRemoval)==null||r)&&(!(t&&(o=n.options.enableMultiRemove)!=null)||o)?!1:l==="desc"?"asc":"desc":i},getCanSort:()=>{var t,r;return((t=e.columnDef.enableSorting)!=null?t:!0)&&((r=n.options.enableSorting)!=null?r:!0)&&!!e.accessorFn},getCanMultiSort:()=>{var t,r;return(t=(r=e.columnDef.enableMultiSort)!=null?r:n.options.enableMultiSort)!=null?t:!!e.accessorFn},getIsSorted:()=>{var t;let r=(t=n.getState().sorting)==null?void 0:t.find(o=>o.id===e.id);return r?r.desc?"desc":"asc":!1},getSortIndex:()=>{var t,r;return(t=(r=n.getState().sorting)==null?void 0:r.findIndex(o=>o.id===e.id))!=null?t:-1},clearSorting:()=>{n.setSorting(t=>t!=null&&t.length?t.filter(r=>r.id!==e.id):[])},getToggleSortingHandler:()=>{let t=e.getCanSort();return r=>{t&&(r.persist==null||r.persist(),e.toggleSorting==null||e.toggleSorting(void 0,e.getCanMultiSort()?n.options.isMultiSortEvent==null?void 0:n.options.isMultiSortEvent(r):!1))}}}),createTable:e=>({setSorting:n=>e.options.onSortingChange==null?void 0:e.options.onSortingChange(n),resetSorting:n=>{var t,r;e.setSorting(n?[]:(t=(r=e.initialState)==null?void 0:r.sorting)!=null?t:[])},getPreSortedRowModel:()=>e.getGroupedRowModel(),getSortedRowModel:()=>(!e._getSortedRowModel&&e.options.getSortedRowModel&&(e._getSortedRowModel=e.options.getSortedRowModel(e)),e.options.manualSorting||!e._getSortedRowModel?e.getPreSortedRowModel():e._getSortedRowModel())})},Ei={getInitialState:e=>({columnVisibility:{},...e}),getDefaultOptions:e=>({onColumnVisibilityChange:W("columnVisibility",e)}),createColumn:(e,n)=>({toggleVisibility:t=>{e.getCanHide()&&n.setColumnVisibility(r=>({...r,[e.id]:t??!e.getIsVisible()}))},getIsVisible:()=>{var t,r;return(t=(r=n.getState().columnVisibility)==null?void 0:r[e.id])!=null?t:!0},getCanHide:()=>{var t,r;return((t=e.columnDef.enableHiding)!=null?t:!0)&&((r=n.options.enableHiding)!=null?r:!0)},getToggleVisibilityHandler:()=>t=>{e.toggleVisibility==null||e.toggleVisibility(t.target.checked)}}),createRow:(e,n)=>({_getAllVisibleCells:y(()=>[e.getAllCells(),n.getState().columnVisibility],t=>t.filter(r=>r.column.getIsVisible()),{key:"row._getAllVisibleCells",debug:()=>{var t;return(t=n.options.debugAll)!=null?t:n.options.debugRows}}),getVisibleCells:y(()=>[e.getLeftVisibleCells(),e.getCenterVisibleCells(),e.getRightVisibleCells()],(t,r,o)=>[...t,...r,...o],{key:!1,debug:()=>{var t;return(t=n.options.debugAll)!=null?t:n.options.debugRows}})}),createTable:e=>{let n=(t,r)=>y(()=>[r(),r().filter(o=>o.getIsVisible()).map(o=>o.id).join("_")],o=>o.filter(i=>i.getIsVisible==null?void 0:i.getIsVisible()),{key:t,debug:()=>{var o;return(o=e.options.debugAll)!=null?o:e.options.debugColumns}});return{getVisibleFlatColumns:n("getVisibleFlatColumns",()=>e.getAllFlatColumns()),getVisibleLeafColumns:n("getVisibleLeafColumns",()=>e.getAllLeafColumns()),getLeftVisibleLeafColumns:n("getLeftVisibleLeafColumns",()=>e.getLeftLeafColumns()),getRightVisibleLeafColumns:n("getRightVisibleLeafColumns",()=>e.getRightLeafColumns()),getCenterVisibleLeafColumns:n("getCenterVisibleLeafColumns",()=>e.getCenterLeafColumns()),setColumnVisibility:t=>e.options.onColumnVisibilityChange==null?void 0:e.options.onColumnVisibilityChange(t),resetColumnVisibility:t=>{var r;e.setColumnVisibility(t?{}:(r=e.initialState.columnVisibility)!=null?r:{})},toggleAllColumnsVisible:t=>{var r;t=(r=t)!=null?r:!e.getIsAllColumnsVisible(),e.setColumnVisibility(e.getAllLeafColumns().reduce((o,i)=>({...o,[i.id]:t||!(i.getCanHide!=null&&i.getCanHide())}),{}))},getIsAllColumnsVisible:()=>!e.getAllLeafColumns().some(t=>!(t.getIsVisible!=null&&t.getIsVisible())),getIsSomeColumnsVisible:()=>e.getAllLeafColumns().some(t=>t.getIsVisible==null?void 0:t.getIsVisible()),getToggleAllColumnsVisibilityHandler:()=>t=>{var r;e.toggleAllColumnsVisible((r=t.target)==null?void 0:r.checked)}}}},er=[Jo,Ei,gi,mi,ti,Ci,ci,ei,pi,_i,Qo];function dr(e){var n;(e.debugAll||e.debugTable)&&console.info("Creating Table Instance...");let t={_features:er},r=t._features.reduce((s,g)=>Object.assign(s,g.getDefaultOptions==null?void 0:g.getDefaultOptions(t)),{}),o=s=>t.options.mergeOptions?t.options.mergeOptions(r,s):{...r,...s},l={...{},...(n=e.initialState)!=null?n:{}};t._features.forEach(s=>{var g;l=(g=s.getInitialState==null?void 0:s.getInitialState(l))!=null?g:l});let u=[],a=!1,d={_features:er,options:{...r,...e},initialState:l,_queue:s=>{u.push(s),a||(a=!0,Promise.resolve().then(()=>{for(;u.length;)u.shift()();a=!1}).catch(g=>setTimeout(()=>{throw g})))},reset:()=>{t.setState(t.initialState)},setOptions:s=>{let g=ce(s,t.options);t.options=o(g)},getState:()=>t.options.state,setState:s=>{t.options.onStateChange==null||t.options.onStateChange(s)},_getRowId:(s,g,f)=>{var c;return(c=t.options.getRowId==null?void 0:t.options.getRowId(s,g,f))!=null?c:`${f?[f.id,g].join("."):g}`},getCoreRowModel:()=>(t._getCoreRowModel||(t._getCoreRowModel=t.options.getCoreRowModel(t)),t._getCoreRowModel()),getRowModel:()=>t.getPaginationRowModel(),getRow:s=>{let g=t.getRowModel().rowsById[s];if(!g)throw new Error;return g},_getDefaultColumnDef:y(()=>[t.options.defaultColumn],s=>{var g;return s=(g=s)!=null?g:{},{header:f=>{let c=f.header.column.columnDef;return c.accessorKey?c.accessorKey:c.accessorFn?c.id:null},cell:f=>{var c,p;return(c=(p=f.renderValue())==null||p.toString==null?void 0:p.toString())!=null?c:null},...t._features.reduce((f,c)=>Object.assign(f,c.getDefaultColumnDef==null?void 0:c.getDefaultColumnDef()),{}),...s}},{debug:()=>{var s;return(s=t.options.debugAll)!=null?s:t.options.debugColumns},key:!1}),_getColumnDefs:()=>t.options.columns,getAllColumns:y(()=>[t._getColumnDefs()],s=>{let g=function(f,c,p){return p===void 0&&(p=0),f.map(m=>{let _=Yo(t,m,p,c),v=m;return _.columns=v.columns?g(v.columns,_,p+1):[],_})};return g(s)},{key:!1,debug:()=>{var s;return(s=t.options.debugAll)!=null?s:t.options.debugColumns}}),getAllFlatColumns:y(()=>[t.getAllColumns()],s=>s.flatMap(g=>g.getFlatColumns()),{key:!1,debug:()=>{var s;return(s=t.options.debugAll)!=null?s:t.options.debugColumns}}),_getAllFlatColumnsById:y(()=>[t.getAllFlatColumns()],s=>s.reduce((g,f)=>(g[f.id]=f,g),{}),{key:!1,debug:()=>{var s;return(s=t.options.debugAll)!=null?s:t.options.debugColumns}}),getAllLeafColumns:y(()=>[t.getAllColumns(),t._getOrderColumnsFn()],(s,g)=>{let f=s.flatMap(c=>c.getLeafColumns());return g(f)},{key:!1,debug:()=>{var s;return(s=t.options.debugAll)!=null?s:t.options.debugColumns}}),getColumn:s=>t._getAllFlatColumnsById()[s]};return Object.assign(t,d),t._features.forEach(s=>Object.assign(t,s.createTable==null?void 0:s.createTable(t))),t}function Ri(e,n,t,r){let o=()=>{var l;return(l=i.getValue())!=null?l:e.options.renderFallbackValue},i={id:`${n.id}_${t.id}`,row:n,column:t,getValue:()=>n.getValue(r),renderValue:o,getContext:y(()=>[e,t,n,i],(l,u,a,d)=>({table:l,column:u,row:a,cell:d,getValue:d.getValue,renderValue:d.renderValue}),{key:!1,debug:()=>e.options.debugAll})};return e._features.forEach(l=>{Object.assign(i,l.createCell==null?void 0:l.createCell(i,t,n,e))},{}),i}var Lt=(e,n,t,r,o,i,l)=>{let u={id:n,index:r,original:t,depth:o,parentId:l,_valuesCache:{},_uniqueValuesCache:{},getValue:a=>{if(u._valuesCache.hasOwnProperty(a))return u._valuesCache[a];let d=e.getColumn(a);if(d!=null&&d.accessorFn)return u._valuesCache[a]=d.accessorFn(u.original,r),u._valuesCache[a]},getUniqueValues:a=>{if(u._uniqueValuesCache.hasOwnProperty(a))return u._uniqueValuesCache[a];let d=e.getColumn(a);if(d!=null&&d.accessorFn)return d.columnDef.getUniqueValues?(u._uniqueValuesCache[a]=d.columnDef.getUniqueValues(u.original,r),u._uniqueValuesCache[a]):(u._uniqueValuesCache[a]=[u.getValue(a)],u._uniqueValuesCache[a])},renderValue:a=>{var d;return(d=u.getValue(a))!=null?d:e.options.renderFallbackValue},subRows:i??[],getLeafRows:()=>Xo(u.subRows,a=>a.subRows),getParentRow:()=>u.parentId?e.getRow(u.parentId):void 0,getParentRows:()=>{let a=[],d=u;for(;;){let s=d.getParentRow();if(!s)break;a.push(s),d=s}return a.reverse()},getAllCells:y(()=>[e.getAllLeafColumns()],a=>a.map(d=>Ri(e,u,d,d.id)),{key:!1,debug:()=>{var a;return(a=e.options.debugAll)!=null?a:e.options.debugRows}}),_getAllCellsByColumnId:y(()=>[u.getAllCells()],a=>a.reduce((d,s)=>(d[s.column.id]=s,d),{}),{key:"row.getAllCellsByColumnId",debug:()=>{var a;return(a=e.options.debugAll)!=null?a:e.options.debugRows}})};for(let a=0;a<e._features.length;a++){let d=e._features[a];Object.assign(u,d==null||d.createRow==null?void 0:d.createRow(u,e))}return u};function cr(){return e=>y(()=>[e.options.data],n=>{let t={rows:[],flatRows:[],rowsById:{}},r=function(o,i,l){i===void 0&&(i=0);let u=[];for(let d=0;d<o.length;d++){let s=Lt(e,e._getRowId(o[d],d,l),o[d],d,i,void 0,l?.id);if(t.flatRows.push(s),t.rowsById[s.id]=s,u.push(s),e.options.getSubRows){var a;s.originalSubRows=e.options.getSubRows(o[d],d),(a=s.originalSubRows)!=null&&a.length&&(s.subRows=r(s.originalSubRows,i+1,s))}}return u};return t.rows=r(n),t},{key:!1,debug:()=>{var n;return(n=e.options.debugAll)!=null?n:e.options.debugTable},onChange:()=>{e._autoResetPageIndex()}})}function fr(e,n,t){return t.options.filterFromLeafRows?xi(e,n,t):Mi(e,n,t)}function xi(e,n,t){var r;let o=[],i={},l=(r=t.options.maxLeafRowFilterDepth)!=null?r:100,u=function(a,d){d===void 0&&(d=0);let s=[];for(let f=0;f<a.length;f++){var g;let c=a[f],p=Lt(t,c.id,c.original,c.index,c.depth,void 0,c.parentId);if(p.columnFilters=c.columnFilters,(g=c.subRows)!=null&&g.length&&d<l){if(p.subRows=u(c.subRows,d+1),c=p,n(c)&&!p.subRows.length){s.push(c),i[c.id]=c,i[f]=c;continue}if(n(c)||p.subRows.length){s.push(c),i[c.id]=c,i[f]=c;continue}}else c=p,n(c)&&(s.push(c),i[c.id]=c,i[f]=c)}return s};return{rows:u(e),flatRows:o,rowsById:i}}function Mi(e,n,t){var r;let o=[],i={},l=(r=t.options.maxLeafRowFilterDepth)!=null?r:100,u=function(a,d){d===void 0&&(d=0);let s=[];for(let f=0;f<a.length;f++){let c=a[f];if(n(c)){var g;if((g=c.subRows)!=null&&g.length&&d<l){let m=Lt(t,c.id,c.original,c.index,c.depth,void 0,c.parentId);m.subRows=u(c.subRows,d+1),c=m}s.push(c),o.push(c),i[c.id]=c}}return s};return{rows:u(e),flatRows:o,rowsById:i}}function gr(){return e=>y(()=>[e.getPreFilteredRowModel(),e.getState().columnFilters,e.getState().globalFilter],(n,t,r)=>{if(!n.rows.length||!(t!=null&&t.length)&&!r){for(let f=0;f<n.flatRows.length;f++)n.flatRows[f].columnFilters={},n.flatRows[f].columnFiltersMeta={};return n}let o=[],i=[];(t??[]).forEach(f=>{var c;let p=e.getColumn(f.id);if(!p)return;let m=p.getFilterFn();m&&o.push({id:f.id,filterFn:m,resolvedValue:(c=m.resolveFilterValue==null?void 0:m.resolveFilterValue(f.value))!=null?c:f.value})});let l=t.map(f=>f.id),u=e.getGlobalFilterFn(),a=e.getAllLeafColumns().filter(f=>f.getCanGlobalFilter());r&&u&&a.length&&(l.push("__global__"),a.forEach(f=>{var c;i.push({id:f.id,filterFn:u,resolvedValue:(c=u.resolveFilterValue==null?void 0:u.resolveFilterValue(r))!=null?c:r})}));let d,s;for(let f=0;f<n.flatRows.length;f++){let c=n.flatRows[f];if(c.columnFilters={},o.length)for(let p=0;p<o.length;p++){d=o[p];let m=d.id;c.columnFilters[m]=d.filterFn(c,m,d.resolvedValue,_=>{c.columnFiltersMeta[m]=_})}if(i.length){for(let p=0;p<i.length;p++){s=i[p];let m=s.id;if(s.filterFn(c,m,s.resolvedValue,_=>{c.columnFiltersMeta[m]=_})){c.columnFilters.__global__=!0;break}}c.columnFilters.__global__!==!0&&(c.columnFilters.__global__=!1)}}let g=f=>{for(let c=0;c<l.length;c++)if(f.columnFilters[l[c]]===!1)return!1;return!0};return fr(n.rows,g,e)},{key:!1,debug:()=>{var n;return(n=e.options.debugAll)!=null?n:e.options.debugTable},onChange:()=>{e._autoResetPageIndex()}})}function pr(){return(e,n)=>y(()=>[e.getPreFilteredRowModel(),e.getState().columnFilters,e.getState().globalFilter,e.getFilteredRowModel()],(t,r,o)=>{if(!t.rows.length||!(r!=null&&r.length)&&!o)return t;let i=[...r.map(u=>u.id).filter(u=>u!==n),o?"__global__":void 0].filter(Boolean),l=u=>{for(let a=0;a<i.length;a++)if(u.columnFilters[i[a]]===!1)return!1;return!0};return fr(t.rows,l,e)},{key:!1,debug:()=>{var t;return(t=e.options.debugAll)!=null?t:e.options.debugTable},onChange:()=>{}})}function mr(){return(e,n)=>y(()=>{var t;return[(t=e.getColumn(n))==null?void 0:t.getFacetedRowModel()]},t=>{if(!t)return new Map;let r=new Map;for(let i=0;i<t.flatRows.length;i++){let l=t.flatRows[i].getUniqueValues(n);for(let u=0;u<l.length;u++){let a=l[u];if(r.has(a)){var o;r.set(a,((o=r.get(a))!=null?o:0)+1)}else r.set(a,1)}}return r},{key:!1,debug:()=>{var t;return(t=e.options.debugAll)!=null?t:e.options.debugTable},onChange:()=>{}})}function _r(){return(e,n)=>y(()=>{var t;return[(t=e.getColumn(n))==null?void 0:t.getFacetedRowModel()]},t=>{var r;if(!t)return;let o=(r=t.flatRows[0])==null?void 0:r.getUniqueValues(n);if(typeof o>"u")return;let i=[o,o];for(let l=0;l<t.flatRows.length;l++){let u=t.flatRows[l].getUniqueValues(n);for(let a=0;a<u.length;a++){let d=u[a];d<i[0]?i[0]=d:d>i[1]&&(i[1]=d)}}return i},{key:!1,debug:()=>{var t;return(t=e.options.debugAll)!=null?t:e.options.debugTable},onChange:()=>{}})}function hr(){return e=>y(()=>[e.getState().sorting,e.getPreSortedRowModel()],(n,t)=>{if(!t.rows.length||!(n!=null&&n.length))return t;let r=e.getState().sorting,o=[],i=r.filter(a=>{var d;return(d=e.getColumn(a.id))==null?void 0:d.getCanSort()}),l={};i.forEach(a=>{let d=e.getColumn(a.id);d&&(l[a.id]={sortUndefined:d.columnDef.sortUndefined,invertSorting:d.columnDef.invertSorting,sortingFn:d.getSortingFn()})});let u=a=>{let d=[...a];return d.sort((s,g)=>{for(let c=0;c<i.length;c+=1){var f;let p=i[c],m=l[p.id],_=(f=p?.desc)!=null?f:!1,v=0;if(m.sortUndefined){let w=s.getValue(p.id),E=g.getValue(p.id),V=w===void 0,D=E===void 0;(V||D)&&(v=V&&D?0:V?m.sortUndefined:-m.sortUndefined)}if(v===0&&(v=m.sortingFn(s,g,p.id)),v!==0)return _&&(v*=-1),m.invertSorting&&(v*=-1),v}return s.index-g.index}),d.forEach(s=>{var g;o.push(s),(g=s.subRows)!=null&&g.length&&(s.subRows=u(s.subRows))}),d};return{rows:u(t.rows),flatRows:o,rowsById:t.rowsById}},{key:!1,debug:()=>{var n;return(n=e.options.debugAll)!=null?n:e.options.debugTable},onChange:()=>{e._autoResetPageIndex()}})}function Ze(e,n){return e?Fi(e)?k(e,n):e:null}function Fi(e){return $i(e)||typeof e=="function"||Ii(e)}function $i(e){return typeof e=="function"&&(()=>{let n=Object.getPrototypeOf(e);return n.prototype&&n.prototype.isReactComponent})()}function Ii(e){return typeof e=="object"&&typeof e.$$typeof=="symbol"&&["react.memo","react.forward_ref"].includes(e.$$typeof.description)}function vr(e){let n={state:{},onStateChange:()=>{},renderFallbackValue:null,...e},[t]=A(()=>({current:dr(n)})),[r,o]=A(()=>t.current.initialState);return t.current.setOptions(i=>({...i,...e,state:{...r,...e.state},onStateChange:l=>{o(l),e.onStateChange==null||e.onStateChange(l)}})),t.current}function Te(){return Te=Object.assign?Object.assign.bind():function(e){for(var n=1;n<arguments.length;n++){var t=arguments[n];for(var r in t)Object.prototype.hasOwnProperty.call(t,r)&&(e[r]=t[r])}return e},Te.apply(this,arguments)}function De(){return De=Object.assign?Object.assign.bind():function(e){for(var n=1;n<arguments.length;n++){var t=arguments[n];for(var r in t)Object.prototype.hasOwnProperty.call(t,r)&&(e[r]=t[r])}return e},De.apply(this,arguments)}function pe(e,n,t){var r,o=(r=t.initialDeps)!=null?r:[],i;return function(){var l;t.key&&t.debug!=null&&t.debug()&&(l=Date.now());var u=e(),a=u.length!==o.length||u.some(function(p,m){return o[m]!==p});if(!a)return i;o=u;var d;if(t.key&&t.debug!=null&&t.debug()&&(d=Date.now()),i=n.apply(void 0,u),t.key&&t.debug!=null&&t.debug()){var s=Math.round((Date.now()-l)*100)/100,g=Math.round((Date.now()-d)*100)/100,f=g/16,c=function(m,_){for(m=String(m);m.length<_;)m=" "+m;return m};console.info("%c\u23F1 "+c(g,5)+" /"+c(s,5)+" ms",`
            font-size: .6rem;
            font-weight: bold;
            color: hsl(`+Math.max(0,Math.min(120-120*f,120))+"deg 100% 31%);",t?.key)}return t==null||t.onChange==null||t.onChange(i),i}}function et(e,n){if(e===void 0)throw new Error("Unexpected undefined"+(n?": "+n:""));return e}var yr=function(n,t){return Math.abs(n-t)<1};var Vi=function(n){return n},Ti=function(n){for(var t=Math.max(n.startIndex-n.overscan,0),r=Math.min(n.endIndex+n.overscan,n.count-1),o=[],i=t;i<=r;i++)o.push(i);return o},br=function(n,t){var r=n.scrollElement;if(r){var o=function(u){var a=u.width,d=u.height;t({width:Math.round(a),height:Math.round(d)})};o(r.getBoundingClientRect());var i=new ResizeObserver(function(l){var u=l[0];if(u!=null&&u.borderBoxSize){var a=u.borderBoxSize[0];if(a){o({width:a.inlineSize,height:a.blockSize});return}}o(r.getBoundingClientRect())});return i.observe(r,{box:"border-box"}),function(){i.unobserve(r)}}};var Sr=function(n,t){var r=n.scrollElement;if(r){var o=function(){t(r[n.options.horizontal?"scrollLeft":"scrollTop"])};return o(),r.addEventListener("scroll",o,{passive:!0}),function(){r.removeEventListener("scroll",o)}}};var Di=function(n,t,r){if(t!=null&&t.borderBoxSize){var o=t.borderBoxSize[0];if(o){var i=Math.round(o[r.options.horizontal?"inlineSize":"blockSize"]);return i}}return Math.round(n.getBoundingClientRect()[r.options.horizontal?"width":"height"])};var wr=function(n,t,r){var o,i,l=t.adjustments,u=l===void 0?0:l,a=t.behavior,d=n+u;(o=r.scrollElement)==null||o.scrollTo==null||o.scrollTo((i={},i[r.options.horizontal?"left":"top"]=d,i.behavior=a,i))},Cr=function(n){var t=this;this.unsubs=[],this.scrollElement=null,this.isScrolling=!1,this.isScrollingTimeoutId=null,this.scrollToIndexTimeoutId=null,this.measurementsCache=[],this.itemSizeCache=new Map,this.pendingMeasuredCacheIndexes=[],this.scrollDirection=null,this.scrollAdjustments=0,this.measureElementCache=new Map,this.observer=function(){var r=null,o=function(){return r||(typeof ResizeObserver<"u"?r=new ResizeObserver(function(l){l.forEach(function(u){t._measureElement(u.target,u)})}):null)};return{disconnect:function(){var l;return(l=o())==null?void 0:l.disconnect()},observe:function(l){var u;return(u=o())==null?void 0:u.observe(l,{box:"border-box"})},unobserve:function(l){var u;return(u=o())==null?void 0:u.unobserve(l)}}}(),this.range={startIndex:0,endIndex:0},this.setOptions=function(r){Object.entries(r).forEach(function(o){var i=o[0],l=o[1];typeof l>"u"&&delete r[i]}),t.options=De({debug:!1,initialOffset:0,overscan:1,paddingStart:0,paddingEnd:0,scrollPaddingStart:0,scrollPaddingEnd:0,horizontal:!1,getItemKey:Vi,rangeExtractor:Ti,onChange:function(){},measureElement:Di,initialRect:{width:0,height:0},scrollMargin:0,scrollingDelay:150,indexAttribute:"data-index",initialMeasurementsCache:[],lanes:1},r)},this.notify=function(){t.options.onChange==null||t.options.onChange(t)},this.cleanup=function(){t.unsubs.filter(Boolean).forEach(function(r){return r()}),t.unsubs=[],t.scrollElement=null},this._didMount=function(){return t.measureElementCache.forEach(t.observer.observe),function(){t.observer.disconnect(),t.cleanup()}},this._willUpdate=function(){var r=t.options.getScrollElement();t.scrollElement!==r&&(t.cleanup(),t.scrollElement=r,t._scrollToOffset(t.scrollOffset,{adjustments:void 0,behavior:void 0}),t.unsubs.push(t.options.observeElementRect(t,function(o){var i=t.scrollRect;t.scrollRect=o,(t.options.horizontal?o.width!==i.width:o.height!==i.height)&&t.maybeNotify()})),t.unsubs.push(t.options.observeElementOffset(t,function(o){t.scrollAdjustments=0,t.scrollOffset!==o&&(t.isScrollingTimeoutId!==null&&(clearTimeout(t.isScrollingTimeoutId),t.isScrollingTimeoutId=null),t.isScrolling=!0,t.scrollDirection=t.scrollOffset<o?"forward":"backward",t.scrollOffset=o,t.maybeNotify(),t.isScrollingTimeoutId=setTimeout(function(){t.isScrollingTimeoutId=null,t.isScrolling=!1,t.scrollDirection=null,t.maybeNotify()},t.options.scrollingDelay))})))},this.getSize=function(){return t.scrollRect[t.options.horizontal?"width":"height"]},this.memoOptions=pe(function(){return[t.options.count,t.options.paddingStart,t.options.scrollMargin,t.options.getItemKey]},function(r,o,i,l){return t.pendingMeasuredCacheIndexes=[],{count:r,paddingStart:o,scrollMargin:i,getItemKey:l}},{key:!1}),this.getFurthestMeasurement=function(r,o){for(var i=new Map,l=new Map,u=o-1;u>=0;u--){var a=r[u];if(!i.has(a.lane)){var d=l.get(a.lane);if(d==null||a.end>d.end?l.set(a.lane,a):a.end<d.end&&i.set(a.lane,!0),i.size===t.options.lanes)break}}return l.size===t.options.lanes?Array.from(l.values()).sort(function(s,g){return s.end-g.end})[0]:void 0},this.getMeasurements=pe(function(){return[t.memoOptions(),t.itemSizeCache]},function(r,o){var i=r.count,l=r.paddingStart,u=r.scrollMargin,a=r.getItemKey,d=t.pendingMeasuredCacheIndexes.length>0?Math.min.apply(Math,t.pendingMeasuredCacheIndexes):0;t.pendingMeasuredCacheIndexes=[];for(var s=t.measurementsCache.slice(0,d),g=d;g<i;g++){var f=a(g),c=t.options.lanes===1?s[g-1]:t.getFurthestMeasurement(s,g),p=c?c.end:l+u,m=o.get(f),_=typeof m=="number"?m:t.options.estimateSize(g),v=p+_,w=c?c.lane:g%t.options.lanes;s[g]={index:g,start:p,size:_,end:v,key:f,lane:w}}return t.measurementsCache=s,s},{key:!1,debug:function(){return t.options.debug}}),this.calculateRange=pe(function(){return[t.getMeasurements(),t.getSize(),t.scrollOffset]},function(r,o,i){return t.range=Oi({measurements:r,outerSize:o,scrollOffset:i})},{key:!1,debug:function(){return t.options.debug}}),this.maybeNotify=pe(function(){var r=t.calculateRange();return[r.startIndex,r.endIndex,t.isScrolling]},function(){t.notify()},{key:!1,debug:function(){return t.options.debug},initialDeps:[this.range.startIndex,this.range.endIndex,this.isScrolling]}),this.getIndexes=pe(function(){return[t.options.rangeExtractor,t.calculateRange(),t.options.overscan,t.options.count]},function(r,o,i,l){return r(De({},o,{overscan:i,count:l}))},{key:!1,debug:function(){return t.options.debug}}),this.indexFromElement=function(r){var o=t.options.indexAttribute,i=r.getAttribute(o);return i?parseInt(i,10):(console.warn("Missing attribute name '"+o+"={index}' on measured element."),-1)},this._measureElement=function(r,o){var i,l=t.indexFromElement(r),u=t.measurementsCache[l];if(u){var a=t.measureElementCache.get(u.key);if(!r.isConnected){t.observer.unobserve(r),r===a&&t.measureElementCache.delete(u.key);return}a!==r&&(a&&t.observer.unobserve(a),t.observer.observe(r),t.measureElementCache.set(u.key,r));var d=t.options.measureElement(r,o,t),s=(i=t.itemSizeCache.get(u.key))!=null?i:u.size,g=d-s;g!==0&&(u.start<t.scrollOffset&&t._scrollToOffset(t.scrollOffset,{adjustments:t.scrollAdjustments+=g,behavior:void 0}),t.pendingMeasuredCacheIndexes.push(l),t.itemSizeCache=new Map(t.itemSizeCache.set(u.key,d)),t.notify())}},this.measureElement=function(r){r&&t._measureElement(r,void 0)},this.getVirtualItems=pe(function(){return[t.getIndexes(),t.getMeasurements()]},function(r,o){for(var i=[],l=0,u=r.length;l<u;l++){var a=r[l],d=o[a];i.push(d)}return i},{key:!1,debug:function(){return t.options.debug}}),this.getVirtualItemForOffset=function(r){var o=t.getMeasurements();return et(o[Er(0,o.length-1,function(i){return et(o[i]).start},r)])},this.getOffsetForAlignment=function(r,o){var i=t.getSize();o==="auto"&&(r<=t.scrollOffset?o="start":r>=t.scrollOffset+i?o="end":o="start"),o==="start"?r=r:o==="end"?r=r-i:o==="center"&&(r=r-i/2);var l=t.options.horizontal?"scrollWidth":"scrollHeight",u=t.scrollElement?"document"in t.scrollElement?t.scrollElement.document.documentElement[l]:t.scrollElement[l]:0,a=u-t.getSize();return Math.max(Math.min(a,r),0)},this.getOffsetForIndex=function(r,o){o===void 0&&(o="auto"),r=Math.max(0,Math.min(r,t.options.count-1));var i=et(t.getMeasurements()[r]);if(o==="auto")if(i.end>=t.scrollOffset+t.getSize()-t.options.scrollPaddingEnd)o="end";else if(i.start<=t.scrollOffset+t.options.scrollPaddingStart)o="start";else return[t.scrollOffset,o];var l=o==="end"?i.end+t.options.scrollPaddingEnd:i.start-t.options.scrollPaddingStart;return[t.getOffsetForAlignment(l,o),o]},this.isDynamicMode=function(){return t.measureElementCache.size>0},this.cancelScrollToIndex=function(){t.scrollToIndexTimeoutId!==null&&(clearTimeout(t.scrollToIndexTimeoutId),t.scrollToIndexTimeoutId=null)},this.scrollToOffset=function(r,o){var i=o===void 0?{}:o,l=i.align,u=l===void 0?"start":l,a=i.behavior;t.cancelScrollToIndex(),a==="smooth"&&t.isDynamicMode()&&console.warn("The `smooth` scroll behavior is not fully supported with dynamic size."),t._scrollToOffset(t.getOffsetForAlignment(r,u),{adjustments:void 0,behavior:a})},this.scrollToIndex=function(r,o){var i=o===void 0?{}:o,l=i.align,u=l===void 0?"auto":l,a=i.behavior;r=Math.max(0,Math.min(r,t.options.count-1)),t.cancelScrollToIndex(),a==="smooth"&&t.isDynamicMode()&&console.warn("The `smooth` scroll behavior is not fully supported with dynamic size.");var d=t.getOffsetForIndex(r,u),s=d[0],g=d[1];t._scrollToOffset(s,{adjustments:void 0,behavior:a}),a!=="smooth"&&t.isDynamicMode()&&(t.scrollToIndexTimeoutId=setTimeout(function(){t.scrollToIndexTimeoutId=null;var f=t.measureElementCache.has(t.options.getItemKey(r));if(f){var c=t.getOffsetForIndex(r,g),p=c[0];yr(p,t.scrollOffset)||t.scrollToIndex(r,{align:g,behavior:a})}else t.scrollToIndex(r,{align:g,behavior:a})}))},this.scrollBy=function(r,o){var i=o===void 0?{}:o,l=i.behavior;t.cancelScrollToIndex(),l==="smooth"&&t.isDynamicMode()&&console.warn("The `smooth` scroll behavior is not fully supported with dynamic size."),t._scrollToOffset(t.scrollOffset+r,{adjustments:void 0,behavior:l})},this.getTotalSize=function(){var r;return(((r=t.getMeasurements()[t.options.count-1])==null?void 0:r.end)||t.options.paddingStart)-t.options.scrollMargin+t.options.paddingEnd},this._scrollToOffset=function(r,o){var i=o.adjustments,l=o.behavior;t.options.scrollToFn(r,{behavior:l,adjustments:i},t)},this.measure=function(){t.itemSizeCache=new Map,t.notify()},this.setOptions(n),this.scrollRect=this.options.initialRect,this.scrollOffset=this.options.initialOffset,this.measurementsCache=this.options.initialMeasurementsCache,this.measurementsCache.forEach(function(r){t.itemSizeCache.set(r.key,r.size)}),this.maybeNotify()},Er=function(n,t,r,o){for(;n<=t;){var i=(n+t)/2|0,l=r(i);if(l<o)n=i+1;else if(l>o)t=i-1;else return i}return n>0?n-1:0};function Oi(e){for(var n=e.measurements,t=e.outerSize,r=e.scrollOffset,o=n.length-1,i=function(d){return n[d].start},l=Er(0,o,i,r),u=l;u<o&&n[u].end<r+t;)u++;return{startIndex:l,endIndex:u}}var Ai=typeof document<"u"?te:L;function Ni(e){var n=Se(function(){return{}},{})[1],t=Te({},e,{onChange:function(l){n(),e.onChange==null||e.onChange(l)}}),r=A(function(){return new Cr(t)}),o=r[0];return o.setOptions(t),L(function(){return o._didMount()},[]),Ai(function(){return o._willUpdate()}),o}function Rr(e){return Ni(Te({observeElementRect:br,observeElementOffset:Sr,scrollToFn:wr},e))}function xr(e){return{render(n){wt(n,e)},unmount(){Et(e)}}}var Tr=Symbol.for("immer-nothing"),Mr=Symbol.for("immer-draftable"),C=Symbol.for("immer-state");function X(e,...n){throw new Error(`[Immer] minified error nr: ${e}. Full error at: https://bit.ly/3cXEKWf`)}var we=Object.getPrototypeOf;function Ce(e){return!!e&&!!e[C]}function ue(e){return e?Dr(e)||Array.isArray(e)||!!e[Mr]||!!e.constructor?.[Mr]||it(e)||lt(e):!1}var Pi=Object.prototype.constructor.toString();function Dr(e){if(!e||typeof e!="object")return!1;let n=we(e);if(n===null)return!0;let t=Object.hasOwnProperty.call(n,"constructor")&&n.constructor;return t===Object?!0:typeof t=="function"&&Function.toString.call(t)===Pi}function Ee(e,n){ot(e)===0?Object.entries(e).forEach(([t,r])=>{n(t,r,e)}):e.forEach((t,r)=>n(r,t,e))}function ot(e){let n=e[C];return n?n.type_:Array.isArray(e)?1:it(e)?2:lt(e)?3:0}function Gt(e,n){return ot(e)===2?e.has(n):Object.prototype.hasOwnProperty.call(e,n)}function Or(e,n,t){let r=ot(e);r===2?e.set(n,t):r===3?e.add(t):e[n]=t}function ki(e,n){return e===n?e!==0||1/e===1/n:e!==e&&n!==n}function it(e){return e instanceof Map}function lt(e){return e instanceof Set}function O(e){return e.copy_||e.base_}function Bt(e,n){if(it(e))return new Map(e);if(lt(e))return new Set(e);if(Array.isArray(e))return Array.prototype.slice.call(e);if(!n&&Dr(e))return we(e)?{...e}:Object.assign(Object.create(null),e);let t=Object.getOwnPropertyDescriptors(e);delete t[C];let r=Reflect.ownKeys(t);for(let o=0;o<r.length;o++){let i=r[o],l=t[i];l.writable===!1&&(l.writable=!0,l.configurable=!0),(l.get||l.set)&&(t[i]={configurable:!0,writable:!0,enumerable:l.enumerable,value:e[i]})}return Object.create(we(e),t)}function Re(e,n=!1){return st(e)||Ce(e)||!ue(e)||(ot(e)>1&&(e.set=e.add=e.clear=e.delete=Li),Object.freeze(e),n&&Ee(e,(t,r)=>Re(r,!0),!0)),e}function Li(){X(2)}function st(e){return Object.isFrozen(e)}var Ut={};function me(e){let n=Ut[e];return n||X(0,e),n}function Hi(e,n){Ut[e]||(Ut[e]=n)}var Oe;function tt(){return Oe}function zi(e,n){return{drafts_:[],parent_:e,immer_:n,canAutoFreeze_:!0,unfinalizedDrafts_:0}}function Fr(e,n){n&&(me("Patches"),e.patches_=[],e.inversePatches_=[],e.patchListener_=n)}function Kt(e){jt(e),e.drafts_.forEach(Gi),e.drafts_=null}function jt(e){e===Oe&&(Oe=e.parent_)}function $r(e){return Oe=zi(Oe,e)}function Gi(e){let n=e[C];n.type_===0||n.type_===1?n.revoke_():n.revoked_=!0}function Ir(e,n){n.unfinalizedDrafts_=n.drafts_.length;let t=n.drafts_[0];return e!==void 0&&e!==t?(t[C].modified_&&(Kt(n),X(4)),ue(e)&&(e=nt(n,e),n.parent_||rt(n,e)),n.patches_&&me("Patches").generateReplacementPatches_(t[C].base_,e,n.patches_,n.inversePatches_)):e=nt(n,t,[]),Kt(n),n.patches_&&n.patchListener_(n.patches_,n.inversePatches_),e!==Tr?e:void 0}function nt(e,n,t){if(st(n))return n;let r=n[C];if(!r)return Ee(n,(o,i)=>Vr(e,r,n,o,i,t),!0),n;if(r.scope_!==e)return n;if(!r.modified_)return rt(e,r.base_,!0),r.base_;if(!r.finalized_){r.finalized_=!0,r.scope_.unfinalizedDrafts_--;let o=r.copy_,i=o,l=!1;r.type_===3&&(i=new Set(o),o.clear(),l=!0),Ee(i,(u,a)=>Vr(e,r,o,u,a,t,l)),rt(e,o,!1),t&&e.patches_&&me("Patches").generatePatches_(r,t,e.patches_,e.inversePatches_)}return r.copy_}function Vr(e,n,t,r,o,i,l){if(Ce(o)){let u=i&&n&&n.type_!==3&&!Gt(n.assigned_,r)?i.concat(r):void 0,a=nt(e,o,u);if(Or(t,r,a),Ce(a))e.canAutoFreeze_=!1;else return}else l&&t.add(o);if(ue(o)&&!st(o)){if(!e.immer_.autoFreeze_&&e.unfinalizedDrafts_<1)return;nt(e,o),(!n||!n.scope_.parent_)&&rt(e,o)}}function rt(e,n,t=!1){!e.parent_&&e.immer_.autoFreeze_&&e.canAutoFreeze_&&Re(n,t)}function Bi(e,n){let t=Array.isArray(e),r={type_:t?1:0,scope_:n?n.scope_:tt(),modified_:!1,finalized_:!1,assigned_:{},parent_:n,base_:e,draft_:null,copy_:null,revoke_:null,isManual_:!1},o=r,i=qt;t&&(o=[r],i=Ae);let{revoke:l,proxy:u}=Proxy.revocable(o,i);return r.draft_=u,r.revoke_=l,u}var qt={get(e,n){if(n===C)return e;let t=O(e);if(!Gt(t,n))return Ui(e,t,n);let r=t[n];return e.finalized_||!ue(r)?r:r===Ht(e.base_,n)?(zt(e),e.copy_[n]=Ne(r,e)):r},has(e,n){return n in O(e)},ownKeys(e){return Reflect.ownKeys(O(e))},set(e,n,t){let r=Ar(O(e),n);if(r?.set)return r.set.call(e.draft_,t),!0;if(!e.modified_){let o=Ht(O(e),n),i=o?.[C];if(i&&i.base_===t)return e.copy_[n]=t,e.assigned_[n]=!1,!0;if(ki(t,o)&&(t!==void 0||Gt(e.base_,n)))return!0;zt(e),ae(e)}return e.copy_[n]===t&&(t!==void 0||n in e.copy_)||Number.isNaN(t)&&Number.isNaN(e.copy_[n])||(e.copy_[n]=t,e.assigned_[n]=!0),!0},deleteProperty(e,n){return Ht(e.base_,n)!==void 0||n in e.base_?(e.assigned_[n]=!1,zt(e),ae(e)):delete e.assigned_[n],e.copy_&&delete e.copy_[n],!0},getOwnPropertyDescriptor(e,n){let t=O(e),r=Reflect.getOwnPropertyDescriptor(t,n);return r&&{writable:!0,configurable:e.type_!==1||n!=="length",enumerable:r.enumerable,value:t[n]}},defineProperty(){X(11)},getPrototypeOf(e){return we(e.base_)},setPrototypeOf(){X(12)}},Ae={};Ee(qt,(e,n)=>{Ae[e]=function(){return arguments[0]=arguments[0][0],n.apply(this,arguments)}});Ae.deleteProperty=function(e,n){return Ae.set.call(this,e,n,void 0)};Ae.set=function(e,n,t){return qt.set.call(this,e[0],n,t,e[0])};function Ht(e,n){let t=e[C];return(t?O(t):e)[n]}function Ui(e,n,t){let r=Ar(n,t);return r?"value"in r?r.value:r.get?.call(e.draft_):void 0}function Ar(e,n){if(!(n in e))return;let t=we(e);for(;t;){let r=Object.getOwnPropertyDescriptor(t,n);if(r)return r;t=we(t)}}function ae(e){e.modified_||(e.modified_=!0,e.parent_&&ae(e.parent_))}function zt(e){e.copy_||(e.copy_=Bt(e.base_,e.scope_.immer_.useStrictShallowCopy_))}var Ki=class{constructor(e){this.autoFreeze_=!0,this.useStrictShallowCopy_=!1,this.produce=(n,t,r)=>{if(typeof n=="function"&&typeof t!="function"){let i=t;t=n;let l=this;return function(a=i,...d){return l.produce(a,s=>t.call(this,s,...d))}}typeof t!="function"&&X(6),r!==void 0&&typeof r!="function"&&X(7);let o;if(ue(n)){let i=$r(this),l=Ne(n,void 0),u=!0;try{o=t(l),u=!1}finally{u?Kt(i):jt(i)}return Fr(i,r),Ir(o,i)}else if(!n||typeof n!="object"){if(o=t(n),o===void 0&&(o=n),o===Tr&&(o=void 0),this.autoFreeze_&&Re(o,!0),r){let i=[],l=[];me("Patches").generateReplacementPatches_(n,o,i,l),r(i,l)}return o}else X(1,n)},this.produceWithPatches=(n,t)=>{if(typeof n=="function")return(l,...u)=>this.produceWithPatches(l,a=>n(a,...u));let r,o;return[this.produce(n,t,(l,u)=>{r=l,o=u}),r,o]},typeof e?.autoFreeze=="boolean"&&this.setAutoFreeze(e.autoFreeze),typeof e?.useStrictShallowCopy=="boolean"&&this.setUseStrictShallowCopy(e.useStrictShallowCopy)}createDraft(e){ue(e)||X(8),Ce(e)&&(e=ji(e));let n=$r(this),t=Ne(e,void 0);return t[C].isManual_=!0,jt(n),t}finishDraft(e,n){let t=e&&e[C];(!t||!t.isManual_)&&X(9);let{scope_:r}=t;return Fr(r,n),Ir(void 0,r)}setAutoFreeze(e){this.autoFreeze_=e}setUseStrictShallowCopy(e){this.useStrictShallowCopy_=e}applyPatches(e,n){let t;for(t=n.length-1;t>=0;t--){let o=n[t];if(o.path.length===0&&o.op==="replace"){e=o.value;break}}t>-1&&(n=n.slice(t+1));let r=me("Patches").applyPatches_;return Ce(e)?r(e,n):this.produce(e,o=>r(o,n))}};function Ne(e,n){let t=it(e)?me("MapSet").proxyMap_(e,n):lt(e)?me("MapSet").proxySet_(e,n):Bi(e,n);return(n?n.scope_:tt()).drafts_.push(t),t}function ji(e){return Ce(e)||X(10,e),Nr(e)}function Nr(e){if(!ue(e)||st(e))return e;let n=e[C],t;if(n){if(!n.modified_)return n.base_;n.finalized_=!0,t=Bt(e,n.scope_.immer_.useStrictShallowCopy_)}else t=Bt(e,!0);return Ee(t,(r,o)=>{Or(t,r,Nr(o))}),n&&(n.finalized_=!1),t}function Pr(){class e extends Map{constructor(a,d){super(),this[C]={type_:2,parent_:d,scope_:d?d.scope_:tt(),modified_:!1,finalized_:!1,copy_:void 0,assigned_:void 0,base_:a,draft_:this,isManual_:!1,revoked_:!1}}get size(){return O(this[C]).size}has(a){return O(this[C]).has(a)}set(a,d){let s=this[C];return l(s),(!O(s).has(a)||O(s).get(a)!==d)&&(t(s),ae(s),s.assigned_.set(a,!0),s.copy_.set(a,d),s.assigned_.set(a,!0)),this}delete(a){if(!this.has(a))return!1;let d=this[C];return l(d),t(d),ae(d),d.base_.has(a)?d.assigned_.set(a,!1):d.assigned_.delete(a),d.copy_.delete(a),!0}clear(){let a=this[C];l(a),O(a).size&&(t(a),ae(a),a.assigned_=new Map,Ee(a.base_,d=>{a.assigned_.set(d,!1)}),a.copy_.clear())}forEach(a,d){let s=this[C];O(s).forEach((g,f,c)=>{a.call(d,this.get(f),f,this)})}get(a){let d=this[C];l(d);let s=O(d).get(a);if(d.finalized_||!ue(s)||s!==d.base_.get(a))return s;let g=Ne(s,d);return t(d),d.copy_.set(a,g),g}keys(){return O(this[C]).keys()}values(){let a=this.keys();return{[Symbol.iterator]:()=>this.values(),next:()=>{let d=a.next();return d.done?d:{done:!1,value:this.get(d.value)}}}}entries(){let a=this.keys();return{[Symbol.iterator]:()=>this.entries(),next:()=>{let d=a.next();if(d.done)return d;let s=this.get(d.value);return{done:!1,value:[d.value,s]}}}}[Symbol.iterator](){return this.entries()}}function n(u,a){return new e(u,a)}function t(u){u.copy_||(u.assigned_=new Map,u.copy_=new Map(u.base_))}class r extends Set{constructor(a,d){super(),this[C]={type_:3,parent_:d,scope_:d?d.scope_:tt(),modified_:!1,finalized_:!1,copy_:void 0,base_:a,draft_:this,drafts_:new Map,revoked_:!1,isManual_:!1}}get size(){return O(this[C]).size}has(a){let d=this[C];return l(d),d.copy_?!!(d.copy_.has(a)||d.drafts_.has(a)&&d.copy_.has(d.drafts_.get(a))):d.base_.has(a)}add(a){let d=this[C];return l(d),this.has(a)||(i(d),ae(d),d.copy_.add(a)),this}delete(a){if(!this.has(a))return!1;let d=this[C];return l(d),i(d),ae(d),d.copy_.delete(a)||(d.drafts_.has(a)?d.copy_.delete(d.drafts_.get(a)):!1)}clear(){let a=this[C];l(a),O(a).size&&(i(a),ae(a),a.copy_.clear())}values(){let a=this[C];return l(a),i(a),a.copy_.values()}entries(){let a=this[C];return l(a),i(a),a.copy_.entries()}keys(){return this.values()}[Symbol.iterator](){return this.values()}forEach(a,d){let s=this.values(),g=s.next();for(;!g.done;)a.call(d,g.value,g.value,this),g=s.next()}}function o(u,a){return new r(u,a)}function i(u){u.copy_||(u.copy_=new Set,u.base_.forEach(a=>{if(ue(a)){let d=Ne(a,u);u.drafts_.set(a,d),u.copy_.add(d)}else u.copy_.add(a)}))}function l(u){u.revoked_&&X(3,JSON.stringify(O(u)))}Hi("MapSet",{proxyMap_:n,proxySet_:o})}var H=new Ki,kr=H.produce,kl=H.produceWithPatches.bind(H),Ll=H.setAutoFreeze.bind(H),Hl=H.setUseStrictShallowCopy.bind(H),zl=H.applyPatches.bind(H),Gl=H.createDraft.bind(H),Bl=H.finishDraft.bind(H);function at(e){var n=A(function(){return Re(typeof e=="function"?e():e,!0)}),t=n[1];return[n[0],le(function(r){t(typeof r=="function"?kr(r):Re(r))},[])]}function qi(e,n,t,r,o){window.Shiny.shinyapp.makeRequest(e,n,t,r,o)}function Lr({method:e,args:n,blobs:t}){return new Promise((r,o)=>{qi(e,n,i=>{r(i)},i=>{o(i)},t)})}function Hr({patchInfo:e,patches:n,onSuccess:t,onError:r,columns:o,setData:i,setCellEditMapAtLoc:l}){let u=n.map(a=>({row_index:a.rowIndex,column_index:a.columnIndex,value:a.value}));Lr({method:e.key,args:[u]}).then(a=>{if(!Array.isArray(a))throw new Error("Expected a response of a list of patches");for(let s of a)if(!("row_index"in s&&"column_index"in s&&"value"in s))throw new Error("Expected list of patches containing `row_index`, `column_index`, and `value`");a=a;let d=a.map(s=>({rowIndex:s.row_index,columnIndex:s.column_index,value:s.value}));i(s=>{d.forEach(({rowIndex:g,columnIndex:f,value:c})=>{s[g][f]=c})}),d.forEach(({rowIndex:s,columnIndex:g,value:f})=>{l(s,g,c=>{c.value=f,c.state=_e.EditSuccess,c.errorTitle=void 0})}),t(d)}).catch(a=>{n.forEach(({rowIndex:d,columnIndex:s,value:g})=>{l(d,s,f=>{f.value=String(g),f.state=_e.EditFailure,f.errorTitle=String(a)})}),r(a)})}var _e={EditSaving:"EditSaving",EditSuccess:"EditSuccess",EditFailure:"EditFailure",Editing:"Editing",Ready:"Ready"},Wi={EditSaving:"cell-edit-saving",EditSuccess:"cell-edit-success",EditFailure:"cell-edit-failure",Editing:"cell-edit-editing",Ready:void 0},zr=({containerRef:e,rowId:n,cell:t,patchInfo:r,columns:o,rowIndex:i,columnIndex:l,editCellsIsAllowed:u,getSortedRowModel:a,cellEditInfo:d,setData:s,setCellEditMapAtLoc:g})=>{let f=t.getValue(),c=d?.value??f,p=d?.state??_e.Ready,m=d?.errorTitle,_=d?.isEditing??!1,v=d?.editValue??f,w=q(null),E=le(({resetIsEditing:S=!1,resetEditValue:P=!1}={resetIsEditing:!0,resetEditValue:!0})=>{g(i,l,B=>{S&&(B.isEditing=!1),P&&(B.editValue=void 0)})},[i,l,g]),V=S=>{S.key==="Escape"&&(S.preventDefault(),E())},D=S=>{if(S.key!=="Tab")return;S.preventDefault();let P=S.shiftKey,B=l+(P?-1:1);I(),!(B<0||B>=o.length)&&g(i,B,U=>{U.isEditing=!0})},G=S=>{if(S.key!=="Enter")return;S.preventDefault();let P=S.shiftKey,B=a(),U=B.rows.findIndex(K=>K.id===n);if(U<0)return;let xe=U+(P?-1:1);if(I(),xe<0||xe>=B.rows.length)return;let ut=B.rows[xe].index;g(ut,l,K=>{K.isEditing=!0})},re=S=>{[V,G,D].forEach(P=>P(S))},I=le(()=>{if(g(i,l,S=>{S.errorTitle=void 0}),`${f}`==`${v}`){E(),g(i,l,S=>{S.state=p});return}E({resetIsEditing:!0}),g(i,l,S=>{S.state=_e.EditSaving}),Hr({patchInfo:r,patches:[{rowIndex:i,columnIndex:l,value:v}],onSuccess:S=>{E({resetEditValue:!0})},onError:S=>{},columns:o,setData:s,setCellEditMapAtLoc:g})},[g,i,l,f,v,E,r,o,s,p]);L(()=>{_&&w.current&&(w.current.focus(),w.current.select())},[_]),L(()=>{if(!_||!w.current)return;let S=P=>{P.target!==w.current&&(I(),E())};return document.body.addEventListener("click",S),()=>{document.body.removeEventListener("click",S)}},[p,I,i,l,_,E]);function N(S){_&&S.target.select()}function oe(S){g(i,l,P=>{P.editValue=S.target.value})}let Pe,Y,ke=m,Le=Wi[_?_e.Editing:p],He=null;return p===_e.EditSaving?Y=b.createElement("em",null,v):(_?He=b.createElement("textarea",{value:v,onChange:oe,onFocus:N,onKeyDown:re,ref:w}):u&&(Pe=S=>{g(i,l,P=>{P.isEditing=!0,P.editValue=c})}),Y=Ze(t.column.columnDef.cell,t.getContext())),b.createElement("td",{id:t.id,onClick:Pe,title:ke,className:Le},He,Y)};var Gr=()=>{let[e,n]=at(new Map);return Pr(),{cellEditMap:e,setCellEditMap:n,setCellEditMapAtLoc:(r,o,i)=>{n(l=>{let u=Br(r,o),a=l.get(u)??{};i(a),l.set(u,a)})}}},Br=(e,n)=>`[${e}, ${n}]`;var Ur=(e,n,t)=>{let r=Br(n,t);return[e.get(r)??{},r]};function Kr(e,n,t){let r=Object.assign({top:0,right:0,bottom:0,left:0},t),o=e,i=o.scrollTop+r.top,l=o.scrollLeft+r.left,u=i+o.clientHeight-r.top-r.bottom,a=l+o.clientWidth-r.left-r.right;for(let d=0;d<n.length;d++){let s=n[d],g=s.offsetTop,f=s.offsetLeft;if(g>=i&&g<=u&&f>=l&&f<=a)return s}return null}function Wt(e,n){return document?.defaultView?.getComputedStyle(e,null)?.getPropertyValue(n)}var Wr=e=>{let[n,t]=A(!1),{range:r,from:o,to:i,onRangeChange:l}=e;return b.createElement(Xi,{range:r,value:[o,i],editing:n,onValueChange:u=>l(...u),onFocus:()=>t(!0),onBlur:()=>t(!1)})};var Xi=e=>{let[n,t]=e.value,{editing:r,onFocus:o}=e,i=q(null),l=q(null);return b.createElement("div",{onBlur:u=>{if(!u.currentTarget.contains(u.relatedTarget))return e.onBlur()},onFocus:()=>o(),style:{display:"flex",gap:"0.5rem"}},b.createElement("input",{ref:i,className:`form-control form-control-sm ${i.current?.checkValidity()?"":"is-invalid"}`,style:{flex:"1 1 0",width:"0"},type:"number",placeholder:jr(r,"Min",e.range()[0]),defaultValue:n,step:"any",onChange:u=>{let a=qr(u.target.value);i.current.classList.toggle("is-invalid",!u.target.checkValidity()),e.onValueChange([a,t])}}),b.createElement("input",{ref:l,className:`form-control form-control-sm ${l.current?.checkValidity()?"":"is-invalid"}`,style:{flex:"1 1 0",width:"0"},type:"number",placeholder:jr(r,"Max",e.range()[1]),defaultValue:t,step:"any",onChange:u=>{let a=qr(u.target.value);l.current.classList.toggle("is-invalid",!u.target.checkValidity()),e.onValueChange([n,a])}}))};function jr(e,n,t){return e?typeof t>"u"?n:`${n} (${t})`:null}function qr(e){if(e!=="")return+e}function Xr(e){return e?{getFilteredRowModel:gr(),getFacetedRowModel:pr(),getFacetedUniqueValues:mr(),getFacetedMinMaxValues:_r(),filterFns:{substring:(n,t,r,o)=>n.getValue(t).toString().includes(r)}}:{}}var Yr=({header:e,className:n,...t})=>{if((e.column.columnDef.meta?.typeHint).type==="numeric"){let[o,i]=e.column.getFilterValue()??[void 0,void 0];return Wr({from:o,to:i,range:()=>e.column.getFacetedMinMaxValues()??[void 0,void 0],onRangeChange:(u,a)=>e.column.setFilterValue([u,a])})}return b.createElement("input",{...t,className:`form-control form-control-sm ${n}`,type:"text",onChange:o=>e.column.setFilterValue(o.target.value)})};var z=class e{_set;static _empty=new e(new Set);constructor(n){this._set=n}static empty(){return this._empty}static just(...n){return this.empty().add(...n)}has(n){return this._set.has(n)}add(...n){let t=new Set(this._set.keys());for(let r of n)t.add(r);return new e(t)}toggle(n){return this.has(n)?this.delete(n):this.add(n)}delete(n){let t=new Set(this._set.keys());return t.delete(n),new e(t)}clear(){return e.empty()}[Symbol.iterator](){return this._set[Symbol.iterator]()}toList(){return[...this._set.keys()]}};var Q=class e{static _NONE="none";static _ROW_SINGLE="single";static _ROW_MULTIPLE="multiple";static _COL_SINGLE="single";static _col_multiple="multiple";static _RECT_REGION="region";static _RECT_CELL="cell";static _rowEnum={NONE:e._NONE,SINGLE:e._ROW_SINGLE,MULTIPLE:e._ROW_MULTIPLE};static _colEnum={NONE:e._NONE,SINGLE:e._COL_SINGLE,MULTIPLE:e._col_multiple};static _rectEnum={NONE:e._NONE,REGION:e._RECT_REGION,CELL:e._RECT_CELL};row;col;rect;constructor({row:n,col:t,rect:r}){if(!Object.values(e._rowEnum).includes(n))throw new Error(`Invalid row selection mode: ${n}`);if(!Object.values(e._colEnum).includes(t))throw new Error(`Invalid col selection mode: ${t}`);if(!Object.values(e._rectEnum).includes(r))throw new Error(`Invalid rect selection mode: ${r}`);this.row=n,this.col=t,this.rect=r}is_none(){return this.row===e._rowEnum.NONE&&this.col===e._colEnum.NONE&&this.rect===e._rectEnum.NONE}};function Qr(e){return e||(e={row:"multi-native",col:"none",rect:"none"}),new Q({row:e.row,col:e.col,rect:e.rect})}function Zr(e,n,t,r){let[o,i]=A(z.empty()),[l,u]=A(null),a=s=>{if(e.is_none())return;let g=s.currentTarget,f=n(g),c=Yi(e,r,o,s,f,l);c&&(i(c.selection),c.anchor&&(u(f),g.focus()),s.preventDefault())},d=s=>{if(e.is_none())return;let g=s.currentTarget,f=n(g),c=o.has(f);if(e.row===Q._rowEnum.SINGLE){if(s.key===" "||s.key==="Enter")o.has(f)?i(z.empty()):i(z.just(f)),s.preventDefault();else if(s.key==="ArrowUp"||s.key==="ArrowDown"){let p=t(f,s.key==="ArrowUp"?-1:1);p&&(s.preventDefault(),c&&i(z.just(p)))}}else e.row===Q._rowEnum.MULTIPLE&&(s.key===" "||s.key==="Enter"?(i(o.toggle(f)),s.preventDefault()):(s.key==="ArrowUp"||s.key==="ArrowDown")&&t(f,s.key==="ArrowUp"?-1:1)&&s.preventDefault())};return{has(s){return o.has(s)},set(s,g){i(g?o.add(s):o.delete(s))},setMultiple(s){i(z.just(...s))},clear(){i(o.clear())},keys(){return o},itemHandlers(){return{onMouseDown:a,onKeyDown:d}}}}var Jr=/^mac/i.test(window.navigator.userAgentData?.platform??window.navigator.platform);function Yi(e,n,t,r,o,i){let{shiftKey:l,altKey:u}=r,a=Jr?r.metaKey:r.ctrlKey;if((Jr?r.ctrlKey:r.metaKey)||u||e.row===Q._rowEnum.NONE)return null;if(e.row===Q._rowEnum.SINGLE)return a&&!l?t.has(o)?{selection:z.empty(),anchor:!0}:{selection:z.just(o),anchor:!0}:{selection:z.just(o),anchor:!0};if(e.row===Q._rowEnum.MULTIPLE)if(l&&a){if(i!==null&&n){let s=n(i,o);return{selection:t.add(...s)}}}else{if(a)return{selection:t.toggle(o),anchor:!0};if(l){if(i!==null&&n){let s=n(i,o);return{selection:z.just(...s)}}}else return{selection:z.just(o),anchor:!0}}else throw new Error(`Unsupported row selection mode: ${e.row}`);return null}var eo={className:"sort-arrow",viewBox:[-1,-1,2,2].map(e=>e*1.4).join(" "),width:"100%",height:"100%",style:{paddingLeft:"3px"}},to={stroke:"#333333",strokeWidth:"0.6",fill:"transparent"},Ji=b.createElement("svg",{xmlns:"http://www.w3.org/2000/svg",...eo},b.createElement("path",{d:"M -1 0.5 L 0 -0.5 L 1 0.5",...to,strokeLinecap:"round"})),Qi=b.createElement("svg",{xmlns:"http://www.w3.org/2000/svg",...eo},b.createElement("path",{d:"M -1 -0.5 L 0 0.5 L 1 -0.5",...to,strokeLinecap:"round"})),no=({direction:e})=>{if(!e)return null;if(e==="asc")return Ji;if(e==="desc")return Qi;throw new Error(`Unexpected sort direction: '${e}'`)};var ro=`
=======
// node_modules/preact/dist/preact.module.js
var n;
var l;
var u;
var i;
var t;
var o;
var r;
var f;
var e;
var c = {};
var s = [];
var a = /acit|ex(?:s|g|n|p|$)|rph|grid|ows|mnc|ntw|ine[ch]|zoo|^ord|itera/i;
var v = Array.isArray;
function h(n2, l3) {
  for (var u3 in l3)
    n2[u3] = l3[u3];
  return n2;
}
function p(n2) {
  var l3 = n2.parentNode;
  l3 && l3.removeChild(n2);
}
function y(l3, u3, i4) {
  var t3, o3, r3, f3 = {};
  for (r3 in u3)
    "key" == r3 ? t3 = u3[r3] : "ref" == r3 ? o3 = u3[r3] : f3[r3] = u3[r3];
  if (arguments.length > 2 && (f3.children = arguments.length > 3 ? n.call(arguments, 2) : i4), "function" == typeof l3 && null != l3.defaultProps)
    for (r3 in l3.defaultProps)
      void 0 === f3[r3] && (f3[r3] = l3.defaultProps[r3]);
  return d(l3, f3, t3, o3, null);
}
function d(n2, i4, t3, o3, r3) {
  var f3 = { type: n2, props: i4, key: t3, ref: o3, __k: null, __: null, __b: 0, __e: null, __d: void 0, __c: null, __h: null, constructor: void 0, __v: null == r3 ? ++u : r3 };
  return null == r3 && null != l.vnode && l.vnode(f3), f3;
}
function _() {
  return { current: null };
}
function k(n2) {
  return n2.children;
}
function b(n2, l3) {
  this.props = n2, this.context = l3;
}
function g(n2, l3) {
  if (null == l3)
    return n2.__ ? g(n2.__, n2.__.__k.indexOf(n2) + 1) : null;
  for (var u3; l3 < n2.__k.length; l3++)
    if (null != (u3 = n2.__k[l3]) && null != u3.__e)
      return u3.__e;
  return "function" == typeof n2.type ? g(n2) : null;
}
function m(n2) {
  var l3, u3;
  if (null != (n2 = n2.__) && null != n2.__c) {
    for (n2.__e = n2.__c.base = null, l3 = 0; l3 < n2.__k.length; l3++)
      if (null != (u3 = n2.__k[l3]) && null != u3.__e) {
        n2.__e = n2.__c.base = u3.__e;
        break;
      }
    return m(n2);
  }
}
function w(n2) {
  (!n2.__d && (n2.__d = true) && t.push(n2) && !x.__r++ || o !== l.debounceRendering) && ((o = l.debounceRendering) || r)(x);
}
function x() {
  var n2, l3, u3, i4, o3, r3, e3, c3;
  for (t.sort(f); n2 = t.shift(); )
    n2.__d && (l3 = t.length, i4 = void 0, o3 = void 0, e3 = (r3 = (u3 = n2).__v).__e, (c3 = u3.__P) && (i4 = [], (o3 = h({}, r3)).__v = r3.__v + 1, L(c3, r3, o3, u3.__n, void 0 !== c3.ownerSVGElement, null != r3.__h ? [e3] : null, i4, null == e3 ? g(r3) : e3, r3.__h), M(i4, r3), r3.__e != e3 && m(r3)), t.length > l3 && t.sort(f));
  x.__r = 0;
}
function P(n2, l3, u3, i4, t3, o3, r3, f3, e3, a3) {
  var h3, p3, y3, _3, b3, m3, w4, x4 = i4 && i4.__k || s, P3 = x4.length;
  for (u3.__k = [], h3 = 0; h3 < l3.length; h3++)
    if (null != (_3 = u3.__k[h3] = null == (_3 = l3[h3]) || "boolean" == typeof _3 || "function" == typeof _3 ? null : "string" == typeof _3 || "number" == typeof _3 || "bigint" == typeof _3 ? d(null, _3, null, null, _3) : v(_3) ? d(k, { children: _3 }, null, null, null) : _3.__b > 0 ? d(_3.type, _3.props, _3.key, _3.ref ? _3.ref : null, _3.__v) : _3)) {
      if (_3.__ = u3, _3.__b = u3.__b + 1, null === (y3 = x4[h3]) || y3 && _3.key == y3.key && _3.type === y3.type)
        x4[h3] = void 0;
      else
        for (p3 = 0; p3 < P3; p3++) {
          if ((y3 = x4[p3]) && _3.key == y3.key && _3.type === y3.type) {
            x4[p3] = void 0;
            break;
          }
          y3 = null;
        }
      L(n2, _3, y3 = y3 || c, t3, o3, r3, f3, e3, a3), b3 = _3.__e, (p3 = _3.ref) && y3.ref != p3 && (w4 || (w4 = []), y3.ref && w4.push(y3.ref, null, _3), w4.push(p3, _3.__c || b3, _3)), null != b3 ? (null == m3 && (m3 = b3), "function" == typeof _3.type && _3.__k === y3.__k ? _3.__d = e3 = C(_3, e3, n2) : e3 = $2(n2, _3, y3, x4, b3, e3), "function" == typeof u3.type && (u3.__d = e3)) : e3 && y3.__e == e3 && e3.parentNode != n2 && (e3 = g(y3));
    }
  for (u3.__e = m3, h3 = P3; h3--; )
    null != x4[h3] && ("function" == typeof u3.type && null != x4[h3].__e && x4[h3].__e == u3.__d && (u3.__d = A(i4).nextSibling), q(x4[h3], x4[h3]));
  if (w4)
    for (h3 = 0; h3 < w4.length; h3++)
      O(w4[h3], w4[++h3], w4[++h3]);
}
function C(n2, l3, u3) {
  for (var i4, t3 = n2.__k, o3 = 0; t3 && o3 < t3.length; o3++)
    (i4 = t3[o3]) && (i4.__ = n2, l3 = "function" == typeof i4.type ? C(i4, l3, u3) : $2(u3, i4, i4, t3, i4.__e, l3));
  return l3;
}
function S(n2, l3) {
  return l3 = l3 || [], null == n2 || "boolean" == typeof n2 || (v(n2) ? n2.some(function(n3) {
    S(n3, l3);
  }) : l3.push(n2)), l3;
}
function $2(n2, l3, u3, i4, t3, o3) {
  var r3, f3, e3;
  if (void 0 !== l3.__d)
    r3 = l3.__d, l3.__d = void 0;
  else if (null == u3 || t3 != o3 || null == t3.parentNode)
    n:
      if (null == o3 || o3.parentNode !== n2)
        n2.appendChild(t3), r3 = null;
      else {
        for (f3 = o3, e3 = 0; (f3 = f3.nextSibling) && e3 < i4.length; e3 += 1)
          if (f3 == t3)
            break n;
        n2.insertBefore(t3, o3), r3 = o3;
      }
  return void 0 !== r3 ? r3 : t3.nextSibling;
}
function A(n2) {
  var l3, u3, i4;
  if (null == n2.type || "string" == typeof n2.type)
    return n2.__e;
  if (n2.__k) {
    for (l3 = n2.__k.length - 1; l3 >= 0; l3--)
      if ((u3 = n2.__k[l3]) && (i4 = A(u3)))
        return i4;
  }
  return null;
}
function H(n2, l3, u3, i4, t3) {
  var o3;
  for (o3 in u3)
    "children" === o3 || "key" === o3 || o3 in l3 || T(n2, o3, null, u3[o3], i4);
  for (o3 in l3)
    t3 && "function" != typeof l3[o3] || "children" === o3 || "key" === o3 || "value" === o3 || "checked" === o3 || u3[o3] === l3[o3] || T(n2, o3, l3[o3], u3[o3], i4);
}
function I(n2, l3, u3) {
  "-" === l3[0] ? n2.setProperty(l3, null == u3 ? "" : u3) : n2[l3] = null == u3 ? "" : "number" != typeof u3 || a.test(l3) ? u3 : u3 + "px";
}
function T(n2, l3, u3, i4, t3) {
  var o3;
  n:
    if ("style" === l3)
      if ("string" == typeof u3)
        n2.style.cssText = u3;
      else {
        if ("string" == typeof i4 && (n2.style.cssText = i4 = ""), i4)
          for (l3 in i4)
            u3 && l3 in u3 || I(n2.style, l3, "");
        if (u3)
          for (l3 in u3)
            i4 && u3[l3] === i4[l3] || I(n2.style, l3, u3[l3]);
      }
    else if ("o" === l3[0] && "n" === l3[1])
      o3 = l3 !== (l3 = l3.replace(/Capture$/, "")), l3 = l3.toLowerCase() in n2 ? l3.toLowerCase().slice(2) : l3.slice(2), n2.l || (n2.l = {}), n2.l[l3 + o3] = u3, u3 ? i4 || n2.addEventListener(l3, o3 ? z : j, o3) : n2.removeEventListener(l3, o3 ? z : j, o3);
    else if ("dangerouslySetInnerHTML" !== l3) {
      if (t3)
        l3 = l3.replace(/xlink(H|:h)/, "h").replace(/sName$/, "s");
      else if ("width" !== l3 && "height" !== l3 && "href" !== l3 && "list" !== l3 && "form" !== l3 && "tabIndex" !== l3 && "download" !== l3 && "rowSpan" !== l3 && "colSpan" !== l3 && l3 in n2)
        try {
          n2[l3] = null == u3 ? "" : u3;
          break n;
        } catch (n3) {
        }
      "function" == typeof u3 || (null == u3 || false === u3 && "-" !== l3[4] ? n2.removeAttribute(l3) : n2.setAttribute(l3, u3));
    }
}
function j(n2) {
  return this.l[n2.type + false](l.event ? l.event(n2) : n2);
}
function z(n2) {
  return this.l[n2.type + true](l.event ? l.event(n2) : n2);
}
function L(n2, u3, i4, t3, o3, r3, f3, e3, c3) {
  var s3, a3, p3, y3, d3, _3, g4, m3, w4, x4, C3, S2, $4, A4, H3, I3 = u3.type;
  if (void 0 !== u3.constructor)
    return null;
  null != i4.__h && (c3 = i4.__h, e3 = u3.__e = i4.__e, u3.__h = null, r3 = [e3]), (s3 = l.__b) && s3(u3);
  try {
    n:
      if ("function" == typeof I3) {
        if (m3 = u3.props, w4 = (s3 = I3.contextType) && t3[s3.__c], x4 = s3 ? w4 ? w4.props.value : s3.__ : t3, i4.__c ? g4 = (a3 = u3.__c = i4.__c).__ = a3.__E : ("prototype" in I3 && I3.prototype.render ? u3.__c = a3 = new I3(m3, x4) : (u3.__c = a3 = new b(m3, x4), a3.constructor = I3, a3.render = B), w4 && w4.sub(a3), a3.props = m3, a3.state || (a3.state = {}), a3.context = x4, a3.__n = t3, p3 = a3.__d = true, a3.__h = [], a3._sb = []), null == a3.__s && (a3.__s = a3.state), null != I3.getDerivedStateFromProps && (a3.__s == a3.state && (a3.__s = h({}, a3.__s)), h(a3.__s, I3.getDerivedStateFromProps(m3, a3.__s))), y3 = a3.props, d3 = a3.state, a3.__v = u3, p3)
          null == I3.getDerivedStateFromProps && null != a3.componentWillMount && a3.componentWillMount(), null != a3.componentDidMount && a3.__h.push(a3.componentDidMount);
        else {
          if (null == I3.getDerivedStateFromProps && m3 !== y3 && null != a3.componentWillReceiveProps && a3.componentWillReceiveProps(m3, x4), !a3.__e && null != a3.shouldComponentUpdate && false === a3.shouldComponentUpdate(m3, a3.__s, x4) || u3.__v === i4.__v) {
            for (u3.__v !== i4.__v && (a3.props = m3, a3.state = a3.__s, a3.__d = false), a3.__e = false, u3.__e = i4.__e, u3.__k = i4.__k, u3.__k.forEach(function(n3) {
              n3 && (n3.__ = u3);
            }), C3 = 0; C3 < a3._sb.length; C3++)
              a3.__h.push(a3._sb[C3]);
            a3._sb = [], a3.__h.length && f3.push(a3);
            break n;
          }
          null != a3.componentWillUpdate && a3.componentWillUpdate(m3, a3.__s, x4), null != a3.componentDidUpdate && a3.__h.push(function() {
            a3.componentDidUpdate(y3, d3, _3);
          });
        }
        if (a3.context = x4, a3.props = m3, a3.__P = n2, S2 = l.__r, $4 = 0, "prototype" in I3 && I3.prototype.render) {
          for (a3.state = a3.__s, a3.__d = false, S2 && S2(u3), s3 = a3.render(a3.props, a3.state, a3.context), A4 = 0; A4 < a3._sb.length; A4++)
            a3.__h.push(a3._sb[A4]);
          a3._sb = [];
        } else
          do {
            a3.__d = false, S2 && S2(u3), s3 = a3.render(a3.props, a3.state, a3.context), a3.state = a3.__s;
          } while (a3.__d && ++$4 < 25);
        a3.state = a3.__s, null != a3.getChildContext && (t3 = h(h({}, t3), a3.getChildContext())), p3 || null == a3.getSnapshotBeforeUpdate || (_3 = a3.getSnapshotBeforeUpdate(y3, d3)), P(n2, v(H3 = null != s3 && s3.type === k && null == s3.key ? s3.props.children : s3) ? H3 : [H3], u3, i4, t3, o3, r3, f3, e3, c3), a3.base = u3.__e, u3.__h = null, a3.__h.length && f3.push(a3), g4 && (a3.__E = a3.__ = null), a3.__e = false;
      } else
        null == r3 && u3.__v === i4.__v ? (u3.__k = i4.__k, u3.__e = i4.__e) : u3.__e = N(i4.__e, u3, i4, t3, o3, r3, f3, c3);
    (s3 = l.diffed) && s3(u3);
  } catch (n3) {
    u3.__v = null, (c3 || null != r3) && (u3.__e = e3, u3.__h = !!c3, r3[r3.indexOf(e3)] = null), l.__e(n3, u3, i4);
  }
}
function M(n2, u3) {
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
function N(l3, u3, i4, t3, o3, r3, f3, e3) {
  var s3, a3, h3, y3 = i4.props, d3 = u3.props, _3 = u3.type, k4 = 0;
  if ("svg" === _3 && (o3 = true), null != r3) {
    for (; k4 < r3.length; k4++)
      if ((s3 = r3[k4]) && "setAttribute" in s3 == !!_3 && (_3 ? s3.localName === _3 : 3 === s3.nodeType)) {
        l3 = s3, r3[k4] = null;
        break;
      }
  }
  if (null == l3) {
    if (null === _3)
      return document.createTextNode(d3);
    l3 = o3 ? document.createElementNS("http://www.w3.org/2000/svg", _3) : document.createElement(_3, d3.is && d3), r3 = null, e3 = false;
  }
  if (null === _3)
    y3 === d3 || e3 && l3.data === d3 || (l3.data = d3);
  else {
    if (r3 = r3 && n.call(l3.childNodes), a3 = (y3 = i4.props || c).dangerouslySetInnerHTML, h3 = d3.dangerouslySetInnerHTML, !e3) {
      if (null != r3)
        for (y3 = {}, k4 = 0; k4 < l3.attributes.length; k4++)
          y3[l3.attributes[k4].name] = l3.attributes[k4].value;
      (h3 || a3) && (h3 && (a3 && h3.__html == a3.__html || h3.__html === l3.innerHTML) || (l3.innerHTML = h3 && h3.__html || ""));
    }
    if (H(l3, d3, y3, o3, e3), h3)
      u3.__k = [];
    else if (P(l3, v(k4 = u3.props.children) ? k4 : [k4], u3, i4, t3, o3 && "foreignObject" !== _3, r3, f3, r3 ? r3[0] : i4.__k && g(i4, 0), e3), null != r3)
      for (k4 = r3.length; k4--; )
        null != r3[k4] && p(r3[k4]);
    e3 || ("value" in d3 && void 0 !== (k4 = d3.value) && (k4 !== l3.value || "progress" === _3 && !k4 || "option" === _3 && k4 !== y3.value) && T(l3, "value", k4, y3.value, false), "checked" in d3 && void 0 !== (k4 = d3.checked) && k4 !== l3.checked && T(l3, "checked", k4, y3.checked, false));
  }
  return l3;
}
function O(n2, u3, i4) {
  try {
    "function" == typeof n2 ? n2(u3) : n2.current = u3;
  } catch (n3) {
    l.__e(n3, i4);
  }
}
function q(n2, u3, i4) {
  var t3, o3;
  if (l.unmount && l.unmount(n2), (t3 = n2.ref) && (t3.current && t3.current !== n2.__e || O(t3, null, u3)), null != (t3 = n2.__c)) {
    if (t3.componentWillUnmount)
      try {
        t3.componentWillUnmount();
      } catch (n3) {
        l.__e(n3, u3);
      }
    t3.base = t3.__P = null, n2.__c = void 0;
  }
  if (t3 = n2.__k)
    for (o3 = 0; o3 < t3.length; o3++)
      t3[o3] && q(t3[o3], u3, i4 || "function" != typeof n2.type);
  i4 || null == n2.__e || p(n2.__e), n2.__ = n2.__e = n2.__d = void 0;
}
function B(n2, l3, u3) {
  return this.constructor(n2, u3);
}
function D(u3, i4, t3) {
  var o3, r3, f3;
  l.__ && l.__(u3, i4), r3 = (o3 = "function" == typeof t3) ? null : t3 && t3.__k || i4.__k, f3 = [], L(i4, u3 = (!o3 && t3 || i4).__k = y(k, null, [u3]), r3 || c, c, void 0 !== i4.ownerSVGElement, !o3 && t3 ? [t3] : r3 ? null : i4.firstChild ? n.call(i4.childNodes) : null, f3, !o3 && t3 ? t3 : r3 ? r3.__e : i4.firstChild, o3), M(f3, u3);
}
function E(n2, l3) {
  D(n2, l3, E);
}
function F(l3, u3, i4) {
  var t3, o3, r3, f3, e3 = h({}, l3.props);
  for (r3 in l3.type && l3.type.defaultProps && (f3 = l3.type.defaultProps), u3)
    "key" == r3 ? t3 = u3[r3] : "ref" == r3 ? o3 = u3[r3] : e3[r3] = void 0 === u3[r3] && void 0 !== f3 ? f3[r3] : u3[r3];
  return arguments.length > 2 && (e3.children = arguments.length > 3 ? n.call(arguments, 2) : i4), d(l3.type, e3, t3 || l3.key, o3 || l3.ref, null);
}
function G(n2, l3) {
  var u3 = { __c: l3 = "__cC" + e++, __: n2, Consumer: function(n3, l4) {
    return n3.children(l4);
  }, Provider: function(n3) {
    var u4, i4;
    return this.getChildContext || (u4 = [], (i4 = {})[l3] = this, this.getChildContext = function() {
      return i4;
    }, this.shouldComponentUpdate = function(n4) {
      this.props.value !== n4.value && u4.some(function(n5) {
        n5.__e = true, w(n5);
      });
    }, this.sub = function(n4) {
      u4.push(n4);
      var l4 = n4.componentWillUnmount;
      n4.componentWillUnmount = function() {
        u4.splice(u4.indexOf(n4), 1), l4 && l4.call(n4);
      };
    }), n3.children;
  } };
  return u3.Provider.__ = u3.Consumer.contextType = u3;
}
n = s.slice, l = { __e: function(n2, l3, u3, i4) {
  for (var t3, o3, r3; l3 = l3.__; )
    if ((t3 = l3.__c) && !t3.__)
      try {
        if ((o3 = t3.constructor) && null != o3.getDerivedStateFromError && (t3.setState(o3.getDerivedStateFromError(n2)), r3 = t3.__d), null != t3.componentDidCatch && (t3.componentDidCatch(n2, i4 || {}), r3 = t3.__d), r3)
          return t3.__E = t3;
      } catch (l4) {
        n2 = l4;
      }
  throw n2;
} }, u = 0, i = function(n2) {
  return null != n2 && void 0 === n2.constructor;
}, b.prototype.setState = function(n2, l3) {
  var u3;
  u3 = null != this.__s && this.__s !== this.state ? this.__s : this.__s = h({}, this.state), "function" == typeof n2 && (n2 = n2(h({}, u3), this.props)), n2 && h(u3, n2), null != n2 && this.__v && (l3 && this._sb.push(l3), w(this));
}, b.prototype.forceUpdate = function(n2) {
  this.__v && (this.__e = true, n2 && this.__h.push(n2), w(this));
}, b.prototype.render = k, t = [], r = "function" == typeof Promise ? Promise.prototype.then.bind(Promise.resolve()) : setTimeout, f = function(n2, l3) {
  return n2.__v.__b - l3.__v.__b;
}, x.__r = 0, e = 0;

// node_modules/preact/hooks/dist/hooks.module.js
var t2;
var r2;
var u2;
var i2;
var o2 = 0;
var f2 = [];
var c2 = [];
var e2 = l.__b;
var a2 = l.__r;
var v2 = l.diffed;
var l2 = l.__c;
var m2 = l.unmount;
function d2(t3, u3) {
  l.__h && l.__h(r2, t3, o2 || u3), o2 = 0;
  var i4 = r2.__H || (r2.__H = { __: [], __h: [] });
  return t3 >= i4.__.length && i4.__.push({ __V: c2 }), i4.__[t3];
}
function h2(n2) {
  return o2 = 1, s2(B2, n2);
}
function s2(n2, u3, i4) {
  var o3 = d2(t2++, 2);
  if (o3.t = n2, !o3.__c && (o3.__ = [i4 ? i4(u3) : B2(void 0, u3), function(n3) {
    var t3 = o3.__N ? o3.__N[0] : o3.__[0], r3 = o3.t(t3, n3);
    t3 !== r3 && (o3.__N = [r3, o3.__[1]], o3.__c.setState({}));
  }], o3.__c = r2, !r2.u)) {
    var f3 = function(n3, t3, r3) {
      if (!o3.__c.__H)
        return true;
      var u4 = o3.__c.__H.__.filter(function(n4) {
        return n4.__c;
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
function p2(u3, i4) {
  var o3 = d2(t2++, 3);
  !l.__s && z2(o3.__H, i4) && (o3.__ = u3, o3.i = i4, r2.__H.__h.push(o3));
}
function y2(u3, i4) {
  var o3 = d2(t2++, 4);
  !l.__s && z2(o3.__H, i4) && (o3.__ = u3, o3.i = i4, r2.__h.push(o3));
}
function _2(n2) {
  return o2 = 5, F2(function() {
    return { current: n2 };
  }, []);
}
function A2(n2, t3, r3) {
  o2 = 6, y2(function() {
    return "function" == typeof n2 ? (n2(t3()), function() {
      return n2(null);
    }) : n2 ? (n2.current = t3(), function() {
      return n2.current = null;
    }) : void 0;
  }, null == r3 ? r3 : r3.concat(n2));
}
function F2(n2, r3) {
  var u3 = d2(t2++, 7);
  return z2(u3.__H, r3) ? (u3.__V = n2(), u3.i = r3, u3.__h = n2, u3.__V) : u3.__;
}
function T2(n2, t3) {
  return o2 = 8, F2(function() {
    return n2;
  }, t3);
}
function q2(n2) {
  var u3 = r2.context[n2.__c], i4 = d2(t2++, 9);
  return i4.c = n2, u3 ? (null == i4.__ && (i4.__ = true, u3.sub(r2)), u3.props.value) : n2.__;
}
function x2(t3, r3) {
  l.useDebugValue && l.useDebugValue(r3 ? r3(t3) : t3);
}
function V() {
  var n2 = d2(t2++, 11);
  if (!n2.__) {
    for (var u3 = r2.__v; null !== u3 && !u3.__m && null !== u3.__; )
      u3 = u3.__;
    var i4 = u3.__m || (u3.__m = [0, 0]);
    n2.__ = "P" + i4[0] + "-" + i4[1]++;
  }
  return n2.__;
}
function b2() {
  for (var t3; t3 = f2.shift(); )
    if (t3.__P && t3.__H)
      try {
        t3.__H.__h.forEach(k2), t3.__H.__h.forEach(w2), t3.__H.__h = [];
      } catch (r3) {
        t3.__H.__h = [], l.__e(r3, t3.__v);
      }
}
l.__b = function(n2) {
  r2 = null, e2 && e2(n2);
}, l.__r = function(n2) {
  a2 && a2(n2), t2 = 0;
  var i4 = (r2 = n2.__c).__H;
  i4 && (u2 === r2 ? (i4.__h = [], r2.__h = [], i4.__.forEach(function(n3) {
    n3.__N && (n3.__ = n3.__N), n3.__V = c2, n3.__N = n3.i = void 0;
  })) : (i4.__h.forEach(k2), i4.__h.forEach(w2), i4.__h = [], t2 = 0)), u2 = r2;
}, l.diffed = function(t3) {
  v2 && v2(t3);
  var o3 = t3.__c;
  o3 && o3.__H && (o3.__H.__h.length && (1 !== f2.push(o3) && i2 === l.requestAnimationFrame || ((i2 = l.requestAnimationFrame) || j2)(b2)), o3.__H.__.forEach(function(n2) {
    n2.i && (n2.__H = n2.i), n2.__V !== c2 && (n2.__ = n2.__V), n2.i = void 0, n2.__V = c2;
  })), u2 = r2 = null;
}, l.__c = function(t3, r3) {
  r3.some(function(t4) {
    try {
      t4.__h.forEach(k2), t4.__h = t4.__h.filter(function(n2) {
        return !n2.__ || w2(n2);
      });
    } catch (u3) {
      r3.some(function(n2) {
        n2.__h && (n2.__h = []);
      }), r3 = [], l.__e(u3, t4.__v);
    }
  }), l2 && l2(t3, r3);
}, l.unmount = function(t3) {
  m2 && m2(t3);
  var r3, u3 = t3.__c;
  u3 && u3.__H && (u3.__H.__.forEach(function(n2) {
    try {
      k2(n2);
    } catch (n3) {
      r3 = n3;
    }
  }), u3.__H = void 0, r3 && l.__e(r3, u3.__v));
};
var g2 = "function" == typeof requestAnimationFrame;
function j2(n2) {
  var t3, r3 = function() {
    clearTimeout(u3), g2 && cancelAnimationFrame(t3), setTimeout(n2);
  }, u3 = setTimeout(r3, 100);
  g2 && (t3 = requestAnimationFrame(r3));
}
function k2(n2) {
  var t3 = r2, u3 = n2.__c;
  "function" == typeof u3 && (n2.__c = void 0, u3()), r2 = t3;
}
function w2(n2) {
  var t3 = r2;
  n2.__c = n2.__(), r2 = t3;
}
function z2(n2, t3) {
  return !n2 || n2.length !== t3.length || t3.some(function(t4, r3) {
    return t4 !== n2[r3];
  });
}
function B2(n2, t3) {
  return "function" == typeof t3 ? t3(n2) : t3;
}

// node_modules/preact/compat/dist/compat.module.js
function g3(n2, t3) {
  for (var e3 in t3)
    n2[e3] = t3[e3];
  return n2;
}
function C2(n2, t3) {
  for (var e3 in n2)
    if ("__source" !== e3 && !(e3 in t3))
      return true;
  for (var r3 in t3)
    if ("__source" !== r3 && n2[r3] !== t3[r3])
      return true;
  return false;
}
function E2(n2, t3) {
  return n2 === t3 && (0 !== n2 || 1 / n2 == 1 / t3) || n2 != n2 && t3 != t3;
}
function w3(n2) {
  this.props = n2;
}
function x3(n2, e3) {
  function r3(n3) {
    var t3 = this.props.ref, r4 = t3 == n3.ref;
    return !r4 && t3 && (t3.call ? t3(null) : t3.current = null), e3 ? !e3(this.props, n3) || !r4 : C2(this.props, n3);
  }
  function u3(e4) {
    return this.shouldComponentUpdate = r3, y(n2, e4);
  }
  return u3.displayName = "Memo(" + (n2.displayName || n2.name) + ")", u3.prototype.isReactComponent = true, u3.__f = true, u3;
}
(w3.prototype = new b()).isPureReactComponent = true, w3.prototype.shouldComponentUpdate = function(n2, t3) {
  return C2(this.props, n2) || C2(this.state, t3);
};
var R = l.__b;
l.__b = function(n2) {
  n2.type && n2.type.__f && n2.ref && (n2.props.ref = n2.ref, n2.ref = null), R && R(n2);
};
var N2 = "undefined" != typeof Symbol && Symbol.for && Symbol.for("react.forward_ref") || 3911;
function k3(n2) {
  function t3(t4) {
    var e3 = g3({}, t4);
    return delete e3.ref, n2(e3, t4.ref || null);
  }
  return t3.$$typeof = N2, t3.render = t3, t3.prototype.isReactComponent = t3.__f = true, t3.displayName = "ForwardRef(" + (n2.displayName || n2.name) + ")", t3;
}
var A3 = function(n2, t3) {
  return null == n2 ? null : S(S(n2).map(t3));
};
var O2 = { map: A3, forEach: A3, count: function(n2) {
  return n2 ? S(n2).length : 0;
}, only: function(n2) {
  var t3 = S(n2);
  if (1 !== t3.length)
    throw "Children.only";
  return t3[0];
}, toArray: S };
var T3 = l.__e;
l.__e = function(n2, t3, e3, r3) {
  if (n2.then) {
    for (var u3, o3 = t3; o3 = o3.__; )
      if ((u3 = o3.__c) && u3.__c)
        return null == t3.__e && (t3.__e = e3.__e, t3.__k = e3.__k), u3.__c(n2, t3);
  }
  T3(n2, t3, e3, r3);
};
var I2 = l.unmount;
function L2(n2, t3, e3) {
  return n2 && (n2.__c && n2.__c.__H && (n2.__c.__H.__.forEach(function(n3) {
    "function" == typeof n3.__c && n3.__c();
  }), n2.__c.__H = null), null != (n2 = g3({}, n2)).__c && (n2.__c.__P === e3 && (n2.__c.__P = t3), n2.__c = null), n2.__k = n2.__k && n2.__k.map(function(n3) {
    return L2(n3, t3, e3);
  })), n2;
}
function U(n2, t3, e3) {
  return n2 && (n2.__v = null, n2.__k = n2.__k && n2.__k.map(function(n3) {
    return U(n3, t3, e3);
  }), n2.__c && n2.__c.__P === t3 && (n2.__e && e3.insertBefore(n2.__e, n2.__d), n2.__c.__e = true, n2.__c.__P = e3)), n2;
}
function D2() {
  this.__u = 0, this.t = null, this.__b = null;
}
function F3(n2) {
  var t3 = n2.__.__c;
  return t3 && t3.__a && t3.__a(n2);
}
function M2(n2) {
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
    return y(r3, o4);
  }
  return o3.displayName = "Lazy", o3.__f = true, o3;
}
function V2() {
  this.u = null, this.o = null;
}
l.unmount = function(n2) {
  var t3 = n2.__c;
  t3 && t3.__R && t3.__R(), t3 && true === n2.__h && (n2.type = null), I2 && I2(n2);
}, (D2.prototype = new b()).__c = function(n2, t3) {
  var e3 = t3.__c, r3 = this;
  null == r3.t && (r3.t = []), r3.t.push(e3);
  var u3 = F3(r3.__v), o3 = false, i4 = function() {
    o3 || (o3 = true, e3.__R = null, u3 ? u3(l3) : l3());
  };
  e3.__R = i4;
  var l3 = function() {
    if (!--r3.__u) {
      if (r3.state.__a) {
        var n3 = r3.state.__a;
        r3.__v.__k[0] = U(n3, n3.__c.__P, n3.__c.__O);
      }
      var t4;
      for (r3.setState({ __a: r3.__b = null }); t4 = r3.t.pop(); )
        t4.forceUpdate();
    }
  }, c3 = true === t3.__h;
  r3.__u++ || c3 || r3.setState({ __a: r3.__b = r3.__v.__k[0] }), n2.then(i4, i4);
}, D2.prototype.componentWillUnmount = function() {
  this.t = [];
}, D2.prototype.render = function(n2, e3) {
  if (this.__b) {
    if (this.__v.__k) {
      var r3 = document.createElement("div"), o3 = this.__v.__k[0].__c;
      this.__v.__k[0] = L2(this.__b, r3, o3.__O = o3.__P);
    }
    this.__b = null;
  }
  var i4 = e3.__a && y(k, null, n2.fallback);
  return i4 && (i4.__h = null), [y(k, null, e3.__a ? null : n2.children), i4];
};
var W = function(n2, t3, e3) {
  if (++e3[1] === e3[0] && n2.o.delete(t3), n2.props.revealOrder && ("t" !== n2.props.revealOrder[0] || !n2.o.size))
    for (e3 = n2.u; e3; ) {
      for (; e3.length > 3; )
        e3.pop()();
      if (e3[1] < e3[0])
        break;
      n2.u = e3 = e3[2];
    }
};
function P2(n2) {
  return this.getChildContext = function() {
    return n2.context;
  }, n2.children;
}
function j3(n2) {
  var e3 = this, r3 = n2.i;
  e3.componentWillUnmount = function() {
    D(null, e3.l), e3.l = null, e3.i = null;
  }, e3.i && e3.i !== r3 && e3.componentWillUnmount(), n2.__v ? (e3.l || (e3.i = r3, e3.l = { nodeType: 1, parentNode: r3, childNodes: [], appendChild: function(n3) {
    this.childNodes.push(n3), e3.i.appendChild(n3);
  }, insertBefore: function(n3, t3) {
    this.childNodes.push(n3), e3.i.appendChild(n3);
  }, removeChild: function(n3) {
    this.childNodes.splice(this.childNodes.indexOf(n3) >>> 1, 1), e3.i.removeChild(n3);
  } }), D(y(P2, { context: e3.context }, n2.__v), e3.l)) : e3.l && e3.componentWillUnmount();
}
function z3(n2, e3) {
  var r3 = y(j3, { __v: n2, i: e3 });
  return r3.containerInfo = e3, r3;
}
(V2.prototype = new b()).__a = function(n2) {
  var t3 = this, e3 = F3(t3.__v), r3 = t3.o.get(n2);
  return r3[0]++, function(u3) {
    var o3 = function() {
      t3.props.revealOrder ? (r3.push(u3), W(t3, n2, r3)) : u3();
    };
    e3 ? e3(o3) : o3();
  };
}, V2.prototype.render = function(n2) {
  this.u = null, this.o = /* @__PURE__ */ new Map();
  var t3 = S(n2.children);
  n2.revealOrder && "b" === n2.revealOrder[0] && t3.reverse();
  for (var e3 = t3.length; e3--; )
    this.o.set(t3[e3], this.u = [1, 0, this.u]);
  return n2.children;
}, V2.prototype.componentDidUpdate = V2.prototype.componentDidMount = function() {
  var n2 = this;
  this.o.forEach(function(t3, e3) {
    W(n2, e3, t3);
  });
};
var B3 = "undefined" != typeof Symbol && Symbol.for && Symbol.for("react.element") || 60103;
var H2 = /^(?:accent|alignment|arabic|baseline|cap|clip(?!PathU)|color|dominant|fill|flood|font|glyph(?!R)|horiz|image(!S)|letter|lighting|marker(?!H|W|U)|overline|paint|pointer|shape|stop|strikethrough|stroke|text(?!L)|transform|underline|unicode|units|v|vector|vert|word|writing|x(?!C))[A-Z]/;
var Z = /^on(Ani|Tra|Tou|BeforeInp|Compo)/;
var Y = /[A-Z0-9]/g;
var $3 = "undefined" != typeof document;
var q3 = function(n2) {
  return ("undefined" != typeof Symbol && "symbol" == typeof Symbol() ? /fil|che|rad/ : /fil|che|ra/).test(n2);
};
function G2(n2, t3, e3) {
  return null == t3.__k && (t3.textContent = ""), D(n2, t3), "function" == typeof e3 && e3(), n2 ? n2.__c : null;
}
function J(n2, t3, e3) {
  return E(n2, t3), "function" == typeof e3 && e3(), n2 ? n2.__c : null;
}
b.prototype.isReactComponent = {}, ["componentWillMount", "componentWillReceiveProps", "componentWillUpdate"].forEach(function(t3) {
  Object.defineProperty(b.prototype, t3, { configurable: true, get: function() {
    return this["UNSAFE_" + t3];
  }, set: function(n2) {
    Object.defineProperty(this, t3, { configurable: true, writable: true, value: n2 });
  } });
});
var K = l.event;
function Q() {
}
function X() {
  return this.cancelBubble;
}
function nn() {
  return this.defaultPrevented;
}
l.event = function(n2) {
  return K && (n2 = K(n2)), n2.persist = Q, n2.isPropagationStopped = X, n2.isDefaultPrevented = nn, n2.nativeEvent = n2;
};
var tn;
var en = { enumerable: false, configurable: true, get: function() {
  return this.class;
} };
var rn = l.vnode;
l.vnode = function(n2) {
  "string" == typeof n2.type && function(n3) {
    var t3 = n3.props, e3 = n3.type, u3 = {};
    for (var o3 in t3) {
      var i4 = t3[o3];
      if (!("value" === o3 && "defaultValue" in t3 && null == i4 || $3 && "children" === o3 && "noscript" === e3 || "class" === o3 || "className" === o3)) {
        var l3 = o3.toLowerCase();
        "defaultValue" === o3 && "value" in t3 && null == t3.value ? o3 = "value" : "download" === o3 && true === i4 ? i4 = "" : "ondoubleclick" === l3 ? o3 = "ondblclick" : "onchange" !== l3 || "input" !== e3 && "textarea" !== e3 || q3(t3.type) ? "onfocus" === l3 ? o3 = "onfocusin" : "onblur" === l3 ? o3 = "onfocusout" : Z.test(o3) ? o3 = l3 : -1 === e3.indexOf("-") && H2.test(o3) ? o3 = o3.replace(Y, "-$&").toLowerCase() : null === i4 && (i4 = void 0) : l3 = o3 = "oninput", "oninput" === l3 && u3[o3 = l3] && (o3 = "oninputCapture"), u3[o3] = i4;
      }
    }
    "select" == e3 && u3.multiple && Array.isArray(u3.value) && (u3.value = S(t3.children).forEach(function(n4) {
      n4.props.selected = -1 != u3.value.indexOf(n4.props.value);
    })), "select" == e3 && null != u3.defaultValue && (u3.value = S(t3.children).forEach(function(n4) {
      n4.props.selected = u3.multiple ? -1 != u3.defaultValue.indexOf(n4.props.value) : u3.defaultValue == n4.props.value;
    })), t3.class && !t3.className ? (u3.class = t3.class, Object.defineProperty(u3, "className", en)) : (t3.className && !t3.class || t3.class && t3.className) && (u3.class = u3.className = t3.className), n3.props = u3;
  }(n2), n2.$$typeof = B3, rn && rn(n2);
};
var un = l.__r;
l.__r = function(n2) {
  un && un(n2), tn = n2.__c;
};
var on = l.diffed;
l.diffed = function(n2) {
  on && on(n2);
  var t3 = n2.props, e3 = n2.__e;
  null != e3 && "textarea" === n2.type && "value" in t3 && t3.value !== e3.value && (e3.value = null == t3.value ? "" : t3.value), tn = null;
};
var ln = { ReactCurrentDispatcher: { current: { readContext: function(n2) {
  return tn.__n[n2.__c].props.value;
} } } };
function fn(n2) {
  return y.bind(null, n2);
}
function an(n2) {
  return !!n2 && n2.$$typeof === B3;
}
function sn(n2) {
  return an(n2) ? F.apply(null, arguments) : n2;
}
function hn(n2) {
  return !!n2.__k && (D(null, n2), true);
}
function vn(n2) {
  return n2 && (n2.base || 1 === n2.nodeType && n2) || null;
}
var dn = function(n2, t3) {
  return n2(t3);
};
var pn = function(n2, t3) {
  return n2(t3);
};
var mn = k;
function yn(n2) {
  n2();
}
function _n(n2) {
  return n2;
}
function bn() {
  return [false, yn];
}
var Sn = y2;
function gn(n2, t3) {
  var e3 = t3(), r3 = h2({ h: { __: e3, v: t3 } }), u3 = r3[0].h, o3 = r3[1];
  return y2(function() {
    u3.__ = e3, u3.v = t3, E2(u3.__, t3()) || o3({ h: u3 });
  }, [n2, e3, t3]), p2(function() {
    return E2(u3.__, u3.v()) || o3({ h: u3 }), n2(function() {
      E2(u3.__, u3.v()) || o3({ h: u3 });
    });
  }, [n2]), e3;
}
var Cn = { useState: h2, useId: V, useReducer: s2, useEffect: p2, useLayoutEffect: y2, useInsertionEffect: Sn, useTransition: bn, useDeferredValue: _n, useSyncExternalStore: gn, startTransition: yn, useRef: _2, useImperativeHandle: A2, useMemo: F2, useCallback: T2, useContext: q2, useDebugValue: x2, version: "17.0.2", Children: O2, render: G2, hydrate: J, unmountComponentAtNode: hn, createPortal: z3, createElement: y, createContext: G, createFactory: fn, cloneElement: sn, createRef: _, Fragment: k, isValidElement: an, findDOMNode: vn, Component: b, PureComponent: w3, memo: x3, forwardRef: k3, flushSync: pn, unstable_batchedUpdates: dn, StrictMode: mn, Suspense: D2, SuspenseList: V2, lazy: M2, __SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED: ln };

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
  return () => {
    let depTime;
    if (opts.key && opts.debug)
      depTime = Date.now();
    const newDeps = getDeps();
    const depsChanged = newDeps.length !== deps.length || newDeps.some((dep, index) => deps[index] !== dep);
    if (!depsChanged) {
      return result;
    }
    deps = newDeps;
    let resultTime;
    if (opts.key && opts.debug)
      resultTime = Date.now();
    result = fn2(...newDeps);
    opts == null ? void 0 : opts.onChange == null ? void 0 : opts.onChange(result);
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
    }, {
      key: false,
      debug: () => {
        var _table$options$debugA;
        return (_table$options$debugA = table.options.debugAll) != null ? _table$options$debugA : table.options.debugColumns;
      }
    }),
    getLeafColumns: memo(() => [table._getOrderColumnsFn()], (orderColumns2) => {
      var _column$columns2;
      if ((_column$columns2 = column.columns) != null && _column$columns2.length) {
        let leafColumns = column.columns.flatMap((column2) => column2.getLeafColumns());
        return orderColumns2(leafColumns);
      }
      return [column];
    }, {
      key: false,
      debug: () => {
        var _table$options$debugA2;
        return (_table$options$debugA2 = table.options.debugAll) != null ? _table$options$debugA2 : table.options.debugColumns;
      }
    })
  };
  column = table._features.reduce((obj, feature) => {
    return Object.assign(obj, feature.createColumn == null ? void 0 : feature.createColumn(column, table));
  }, column);
  return column;
}
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
    Object.assign(header, feature.createHeader == null ? void 0 : feature.createHeader(header, table));
  });
  return header;
}
var Headers = {
  createTable: (table) => {
    return {
      // Header Groups
      getHeaderGroups: memo(() => [table.getAllColumns(), table.getVisibleLeafColumns(), table.getState().columnPinning.left, table.getState().columnPinning.right], (allColumns, leafColumns, left, right) => {
        var _left$map$filter, _right$map$filter;
        const leftColumns = (_left$map$filter = left == null ? void 0 : left.map((columnId) => leafColumns.find((d3) => d3.id === columnId)).filter(Boolean)) != null ? _left$map$filter : [];
        const rightColumns = (_right$map$filter = right == null ? void 0 : right.map((columnId) => leafColumns.find((d3) => d3.id === columnId)).filter(Boolean)) != null ? _right$map$filter : [];
        const centerColumns = leafColumns.filter((column) => !(left != null && left.includes(column.id)) && !(right != null && right.includes(column.id)));
        const headerGroups = buildHeaderGroups(allColumns, [...leftColumns, ...centerColumns, ...rightColumns], table);
        return headerGroups;
      }, {
        key: "getHeaderGroups",
        debug: () => {
          var _table$options$debugA;
          return (_table$options$debugA = table.options.debugAll) != null ? _table$options$debugA : table.options.debugHeaders;
        }
      }),
      getCenterHeaderGroups: memo(() => [table.getAllColumns(), table.getVisibleLeafColumns(), table.getState().columnPinning.left, table.getState().columnPinning.right], (allColumns, leafColumns, left, right) => {
        leafColumns = leafColumns.filter((column) => !(left != null && left.includes(column.id)) && !(right != null && right.includes(column.id)));
        return buildHeaderGroups(allColumns, leafColumns, table, "center");
      }, {
        key: "getCenterHeaderGroups",
        debug: () => {
          var _table$options$debugA2;
          return (_table$options$debugA2 = table.options.debugAll) != null ? _table$options$debugA2 : table.options.debugHeaders;
        }
      }),
      getLeftHeaderGroups: memo(() => [table.getAllColumns(), table.getVisibleLeafColumns(), table.getState().columnPinning.left], (allColumns, leafColumns, left) => {
        var _left$map$filter2;
        const orderedLeafColumns = (_left$map$filter2 = left == null ? void 0 : left.map((columnId) => leafColumns.find((d3) => d3.id === columnId)).filter(Boolean)) != null ? _left$map$filter2 : [];
        return buildHeaderGroups(allColumns, orderedLeafColumns, table, "left");
      }, {
        key: "getLeftHeaderGroups",
        debug: () => {
          var _table$options$debugA3;
          return (_table$options$debugA3 = table.options.debugAll) != null ? _table$options$debugA3 : table.options.debugHeaders;
        }
      }),
      getRightHeaderGroups: memo(() => [table.getAllColumns(), table.getVisibleLeafColumns(), table.getState().columnPinning.right], (allColumns, leafColumns, right) => {
        var _right$map$filter2;
        const orderedLeafColumns = (_right$map$filter2 = right == null ? void 0 : right.map((columnId) => leafColumns.find((d3) => d3.id === columnId)).filter(Boolean)) != null ? _right$map$filter2 : [];
        return buildHeaderGroups(allColumns, orderedLeafColumns, table, "right");
      }, {
        key: "getRightHeaderGroups",
        debug: () => {
          var _table$options$debugA4;
          return (_table$options$debugA4 = table.options.debugAll) != null ? _table$options$debugA4 : table.options.debugHeaders;
        }
      }),
      // Footer Groups
      getFooterGroups: memo(() => [table.getHeaderGroups()], (headerGroups) => {
        return [...headerGroups].reverse();
      }, {
        key: "getFooterGroups",
        debug: () => {
          var _table$options$debugA5;
          return (_table$options$debugA5 = table.options.debugAll) != null ? _table$options$debugA5 : table.options.debugHeaders;
        }
      }),
      getLeftFooterGroups: memo(() => [table.getLeftHeaderGroups()], (headerGroups) => {
        return [...headerGroups].reverse();
      }, {
        key: "getLeftFooterGroups",
        debug: () => {
          var _table$options$debugA6;
          return (_table$options$debugA6 = table.options.debugAll) != null ? _table$options$debugA6 : table.options.debugHeaders;
        }
      }),
      getCenterFooterGroups: memo(() => [table.getCenterHeaderGroups()], (headerGroups) => {
        return [...headerGroups].reverse();
      }, {
        key: "getCenterFooterGroups",
        debug: () => {
          var _table$options$debugA7;
          return (_table$options$debugA7 = table.options.debugAll) != null ? _table$options$debugA7 : table.options.debugHeaders;
        }
      }),
      getRightFooterGroups: memo(() => [table.getRightHeaderGroups()], (headerGroups) => {
        return [...headerGroups].reverse();
      }, {
        key: "getRightFooterGroups",
        debug: () => {
          var _table$options$debugA8;
          return (_table$options$debugA8 = table.options.debugAll) != null ? _table$options$debugA8 : table.options.debugHeaders;
        }
      }),
      // Flat Headers
      getFlatHeaders: memo(() => [table.getHeaderGroups()], (headerGroups) => {
        return headerGroups.map((headerGroup) => {
          return headerGroup.headers;
        }).flat();
      }, {
        key: "getFlatHeaders",
        debug: () => {
          var _table$options$debugA9;
          return (_table$options$debugA9 = table.options.debugAll) != null ? _table$options$debugA9 : table.options.debugHeaders;
        }
      }),
      getLeftFlatHeaders: memo(() => [table.getLeftHeaderGroups()], (left) => {
        return left.map((headerGroup) => {
          return headerGroup.headers;
        }).flat();
      }, {
        key: "getLeftFlatHeaders",
        debug: () => {
          var _table$options$debugA10;
          return (_table$options$debugA10 = table.options.debugAll) != null ? _table$options$debugA10 : table.options.debugHeaders;
        }
      }),
      getCenterFlatHeaders: memo(() => [table.getCenterHeaderGroups()], (left) => {
        return left.map((headerGroup) => {
          return headerGroup.headers;
        }).flat();
      }, {
        key: "getCenterFlatHeaders",
        debug: () => {
          var _table$options$debugA11;
          return (_table$options$debugA11 = table.options.debugAll) != null ? _table$options$debugA11 : table.options.debugHeaders;
        }
      }),
      getRightFlatHeaders: memo(() => [table.getRightHeaderGroups()], (left) => {
        return left.map((headerGroup) => {
          return headerGroup.headers;
        }).flat();
      }, {
        key: "getRightFlatHeaders",
        debug: () => {
          var _table$options$debugA12;
          return (_table$options$debugA12 = table.options.debugAll) != null ? _table$options$debugA12 : table.options.debugHeaders;
        }
      }),
      // Leaf Headers
      getCenterLeafHeaders: memo(() => [table.getCenterFlatHeaders()], (flatHeaders) => {
        return flatHeaders.filter((header) => {
          var _header$subHeaders;
          return !((_header$subHeaders = header.subHeaders) != null && _header$subHeaders.length);
        });
      }, {
        key: "getCenterLeafHeaders",
        debug: () => {
          var _table$options$debugA13;
          return (_table$options$debugA13 = table.options.debugAll) != null ? _table$options$debugA13 : table.options.debugHeaders;
        }
      }),
      getLeftLeafHeaders: memo(() => [table.getLeftFlatHeaders()], (flatHeaders) => {
        return flatHeaders.filter((header) => {
          var _header$subHeaders2;
          return !((_header$subHeaders2 = header.subHeaders) != null && _header$subHeaders2.length);
        });
      }, {
        key: "getLeftLeafHeaders",
        debug: () => {
          var _table$options$debugA14;
          return (_table$options$debugA14 = table.options.debugAll) != null ? _table$options$debugA14 : table.options.debugHeaders;
        }
      }),
      getRightLeafHeaders: memo(() => [table.getRightFlatHeaders()], (flatHeaders) => {
        return flatHeaders.filter((header) => {
          var _header$subHeaders3;
          return !((_header$subHeaders3 = header.subHeaders) != null && _header$subHeaders3.length);
        });
      }, {
        key: "getRightLeafHeaders",
        debug: () => {
          var _table$options$debugA15;
          return (_table$options$debugA15 = table.options.debugAll) != null ? _table$options$debugA15 : table.options.debugHeaders;
        }
      }),
      getLeafHeaders: memo(() => [table.getLeftHeaderGroups(), table.getCenterHeaderGroups(), table.getRightHeaderGroups()], (left, center, right) => {
        var _left$0$headers, _left$, _center$0$headers, _center$, _right$0$headers, _right$;
        return [...(_left$0$headers = (_left$ = left[0]) == null ? void 0 : _left$.headers) != null ? _left$0$headers : [], ...(_center$0$headers = (_center$ = center[0]) == null ? void 0 : _center$.headers) != null ? _center$0$headers : [], ...(_right$0$headers = (_right$ = right[0]) == null ? void 0 : _right$.headers) != null ? _right$0$headers : []].map((header) => {
          return header.getLeafHeaders();
        }).flat();
      }, {
        key: "getLeafHeaders",
        debug: () => {
          var _table$options$debugA16;
          return (_table$options$debugA16 = table.options.debugAll) != null ? _table$options$debugA16 : table.options.debugHeaders;
        }
      })
    };
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
      onColumnSizingChange: makeStateUpdater("columnSizing", table),
      onColumnSizingInfoChange: makeStateUpdater("columnSizingInfo", table)
    };
  },
  createColumn: (column, table) => {
    return {
      getSize: () => {
        var _column$columnDef$min, _ref, _column$columnDef$max;
        const columnSize = table.getState().columnSizing[column.id];
        return Math.min(Math.max((_column$columnDef$min = column.columnDef.minSize) != null ? _column$columnDef$min : defaultColumnSizing.minSize, (_ref = columnSize != null ? columnSize : column.columnDef.size) != null ? _ref : defaultColumnSizing.size), (_column$columnDef$max = column.columnDef.maxSize) != null ? _column$columnDef$max : defaultColumnSizing.maxSize);
      },
      getStart: (position) => {
        const columns = !position ? table.getVisibleLeafColumns() : position === "left" ? table.getLeftVisibleLeafColumns() : table.getRightVisibleLeafColumns();
        const index = columns.findIndex((d3) => d3.id === column.id);
        if (index > 0) {
          const prevSiblingColumn = columns[index - 1];
          return prevSiblingColumn.getStart(position) + prevSiblingColumn.getSize();
        }
        return 0;
      },
      resetSize: () => {
        table.setColumnSizing((_ref2) => {
          let {
            [column.id]: _3,
            ...rest
          } = _ref2;
          return rest;
        });
      },
      getCanResize: () => {
        var _column$columnDef$ena, _table$options$enable;
        return ((_column$columnDef$ena = column.columnDef.enableResizing) != null ? _column$columnDef$ena : true) && ((_table$options$enable = table.options.enableColumnResizing) != null ? _table$options$enable : true);
      },
      getIsResizing: () => {
        return table.getState().columnSizingInfo.isResizingColumn === column.id;
      }
    };
  },
  createHeader: (header, table) => {
    return {
      getSize: () => {
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
      },
      getStart: () => {
        if (header.index > 0) {
          const prevSiblingHeader = header.headerGroup.headers[header.index - 1];
          return prevSiblingHeader.getStart() + prevSiblingHeader.getSize();
        }
        return 0;
      },
      getResizeHandler: () => {
        const column = table.getColumn(header.column.id);
        const canResize = column == null ? void 0 : column.getCanResize();
        return (e3) => {
          if (!column || !canResize) {
            return;
          }
          e3.persist == null ? void 0 : e3.persist();
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
              const deltaOffset = clientXPos - ((_old$startOffset = old == null ? void 0 : old.startOffset) != null ? _old$startOffset : 0);
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
          const mouseEvents = {
            moveHandler: (e4) => onMove(e4.clientX),
            upHandler: (e4) => {
              document.removeEventListener("mousemove", mouseEvents.moveHandler);
              document.removeEventListener("mouseup", mouseEvents.upHandler);
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
              document.removeEventListener("touchmove", touchEvents.moveHandler);
              document.removeEventListener("touchend", touchEvents.upHandler);
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
            document.addEventListener("touchmove", touchEvents.moveHandler, passiveIfSupported);
            document.addEventListener("touchend", touchEvents.upHandler, passiveIfSupported);
          } else {
            document.addEventListener("mousemove", mouseEvents.moveHandler, passiveIfSupported);
            document.addEventListener("mouseup", mouseEvents.upHandler, passiveIfSupported);
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
      }
    };
  },
  createTable: (table) => {
    return {
      setColumnSizing: (updater) => table.options.onColumnSizingChange == null ? void 0 : table.options.onColumnSizingChange(updater),
      setColumnSizingInfo: (updater) => table.options.onColumnSizingInfoChange == null ? void 0 : table.options.onColumnSizingInfoChange(updater),
      resetColumnSizing: (defaultState) => {
        var _table$initialState$c;
        table.setColumnSizing(defaultState ? {} : (_table$initialState$c = table.initialState.columnSizing) != null ? _table$initialState$c : {});
      },
      resetHeaderSizeInfo: (defaultState) => {
        var _table$initialState$c2;
        table.setColumnSizingInfo(defaultState ? getDefaultColumnSizingInfoState() : (_table$initialState$c2 = table.initialState.columnSizingInfo) != null ? _table$initialState$c2 : getDefaultColumnSizingInfoState());
      },
      getTotalSize: () => {
        var _table$getHeaderGroup, _table$getHeaderGroup2;
        return (_table$getHeaderGroup = (_table$getHeaderGroup2 = table.getHeaderGroups()[0]) == null ? void 0 : _table$getHeaderGroup2.headers.reduce((sum2, header) => {
          return sum2 + header.getSize();
        }, 0)) != null ? _table$getHeaderGroup : 0;
      },
      getLeftTotalSize: () => {
        var _table$getLeftHeaderG, _table$getLeftHeaderG2;
        return (_table$getLeftHeaderG = (_table$getLeftHeaderG2 = table.getLeftHeaderGroups()[0]) == null ? void 0 : _table$getLeftHeaderG2.headers.reduce((sum2, header) => {
          return sum2 + header.getSize();
        }, 0)) != null ? _table$getLeftHeaderG : 0;
      },
      getCenterTotalSize: () => {
        var _table$getCenterHeade, _table$getCenterHeade2;
        return (_table$getCenterHeade = (_table$getCenterHeade2 = table.getCenterHeaderGroups()[0]) == null ? void 0 : _table$getCenterHeade2.headers.reduce((sum2, header) => {
          return sum2 + header.getSize();
        }, 0)) != null ? _table$getCenterHeade : 0;
      },
      getRightTotalSize: () => {
        var _table$getRightHeader, _table$getRightHeader2;
        return (_table$getRightHeader = (_table$getRightHeader2 = table.getRightHeaderGroups()[0]) == null ? void 0 : _table$getRightHeader2.headers.reduce((sum2, header) => {
          return sum2 + header.getSize();
        }, 0)) != null ? _table$getRightHeader : 0;
      }
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
var Expanding = {
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
    return {
      _autoResetExpanded: () => {
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
      },
      setExpanded: (updater) => table.options.onExpandedChange == null ? void 0 : table.options.onExpandedChange(updater),
      toggleAllRowsExpanded: (expanded) => {
        if (expanded != null ? expanded : !table.getIsAllRowsExpanded()) {
          table.setExpanded(true);
        } else {
          table.setExpanded({});
        }
      },
      resetExpanded: (defaultState) => {
        var _table$initialState$e, _table$initialState;
        table.setExpanded(defaultState ? {} : (_table$initialState$e = (_table$initialState = table.initialState) == null ? void 0 : _table$initialState.expanded) != null ? _table$initialState$e : {});
      },
      getCanSomeRowsExpand: () => {
        return table.getPrePaginationRowModel().flatRows.some((row) => row.getCanExpand());
      },
      getToggleAllRowsExpandedHandler: () => {
        return (e3) => {
          e3.persist == null ? void 0 : e3.persist();
          table.toggleAllRowsExpanded();
        };
      },
      getIsSomeRowsExpanded: () => {
        const expanded = table.getState().expanded;
        return expanded === true || Object.values(expanded).some(Boolean);
      },
      getIsAllRowsExpanded: () => {
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
      },
      getExpandedDepth: () => {
        let maxDepth = 0;
        const rowIds = table.getState().expanded === true ? Object.keys(table.getRowModel().rowsById) : Object.keys(table.getState().expanded);
        rowIds.forEach((id) => {
          const splitId = id.split(".");
          maxDepth = Math.max(maxDepth, splitId.length);
        });
        return maxDepth;
      },
      getPreExpandedRowModel: () => table.getSortedRowModel(),
      getExpandedRowModel: () => {
        if (!table._getExpandedRowModel && table.options.getExpandedRowModel) {
          table._getExpandedRowModel = table.options.getExpandedRowModel(table);
        }
        if (table.options.manualExpanding || !table._getExpandedRowModel) {
          return table.getPreExpandedRowModel();
        }
        return table._getExpandedRowModel();
      }
    };
  },
  createRow: (row, table) => {
    return {
      toggleExpanded: (expanded) => {
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
      },
      getIsExpanded: () => {
        var _table$options$getIsR;
        const expanded = table.getState().expanded;
        return !!((_table$options$getIsR = table.options.getIsRowExpanded == null ? void 0 : table.options.getIsRowExpanded(row)) != null ? _table$options$getIsR : expanded === true || (expanded == null ? void 0 : expanded[row.id]));
      },
      getCanExpand: () => {
        var _table$options$getRow, _table$options$enable, _row$subRows;
        return (_table$options$getRow = table.options.getRowCanExpand == null ? void 0 : table.options.getRowCanExpand(row)) != null ? _table$options$getRow : ((_table$options$enable = table.options.enableExpanding) != null ? _table$options$enable : true) && !!((_row$subRows = row.subRows) != null && _row$subRows.length);
      },
      getToggleExpandedHandler: () => {
        const canExpand = row.getCanExpand();
        return () => {
          if (!canExpand)
            return;
          row.toggleExpanded();
        };
      }
    };
  }
};
var includesString = (row, columnId, filterValue) => {
  var _row$getValue, _row$getValue$toStrin, _row$getValue$toStrin2;
  const search = filterValue.toLowerCase();
  return Boolean((_row$getValue = row.getValue(columnId)) == null ? void 0 : (_row$getValue$toStrin = _row$getValue.toString()) == null ? void 0 : (_row$getValue$toStrin2 = _row$getValue$toStrin.toLowerCase()) == null ? void 0 : _row$getValue$toStrin2.includes(search));
};
includesString.autoRemove = (val) => testFalsey(val);
var includesStringSensitive = (row, columnId, filterValue) => {
  var _row$getValue2, _row$getValue2$toStri;
  return Boolean((_row$getValue2 = row.getValue(columnId)) == null ? void 0 : (_row$getValue2$toStri = _row$getValue2.toString()) == null ? void 0 : _row$getValue2$toStri.includes(filterValue));
};
includesStringSensitive.autoRemove = (val) => testFalsey(val);
var equalsString = (row, columnId, filterValue) => {
  var _row$getValue3, _row$getValue3$toStri;
  return ((_row$getValue3 = row.getValue(columnId)) == null ? void 0 : (_row$getValue3$toStri = _row$getValue3.toString()) == null ? void 0 : _row$getValue3$toStri.toLowerCase()) === (filterValue == null ? void 0 : filterValue.toLowerCase());
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
var Filters = {
  getDefaultColumnDef: () => {
    return {
      filterFn: "auto"
    };
  },
  getInitialState: (state) => {
    return {
      columnFilters: [],
      globalFilter: void 0,
      // filtersProgress: 1,
      // facetProgress: {},
      ...state
    };
  },
  getDefaultOptions: (table) => {
    return {
      onColumnFiltersChange: makeStateUpdater("columnFilters", table),
      onGlobalFilterChange: makeStateUpdater("globalFilter", table),
      filterFromLeafRows: false,
      maxLeafRowFilterDepth: 100,
      globalFilterFn: "auto",
      getColumnCanGlobalFilter: (column) => {
        var _table$getCoreRowMode, _table$getCoreRowMode2;
        const value = (_table$getCoreRowMode = table.getCoreRowModel().flatRows[0]) == null ? void 0 : (_table$getCoreRowMode2 = _table$getCoreRowMode._getAllCellsByColumnId()[column.id]) == null ? void 0 : _table$getCoreRowMode2.getValue();
        return typeof value === "string" || typeof value === "number";
      }
    };
  },
  createColumn: (column, table) => {
    return {
      getAutoFilterFn: () => {
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
      },
      getFilterFn: () => {
        var _table$options$filter, _table$options$filter2;
        return isFunction(column.columnDef.filterFn) ? column.columnDef.filterFn : column.columnDef.filterFn === "auto" ? column.getAutoFilterFn() : (_table$options$filter = (_table$options$filter2 = table.options.filterFns) == null ? void 0 : _table$options$filter2[column.columnDef.filterFn]) != null ? _table$options$filter : filterFns[column.columnDef.filterFn];
      },
      getCanFilter: () => {
        var _column$columnDef$ena, _table$options$enable, _table$options$enable2;
        return ((_column$columnDef$ena = column.columnDef.enableColumnFilter) != null ? _column$columnDef$ena : true) && ((_table$options$enable = table.options.enableColumnFilters) != null ? _table$options$enable : true) && ((_table$options$enable2 = table.options.enableFilters) != null ? _table$options$enable2 : true) && !!column.accessorFn;
      },
      getCanGlobalFilter: () => {
        var _column$columnDef$ena2, _table$options$enable3, _table$options$enable4, _table$options$getCol;
        return ((_column$columnDef$ena2 = column.columnDef.enableGlobalFilter) != null ? _column$columnDef$ena2 : true) && ((_table$options$enable3 = table.options.enableGlobalFilter) != null ? _table$options$enable3 : true) && ((_table$options$enable4 = table.options.enableFilters) != null ? _table$options$enable4 : true) && ((_table$options$getCol = table.options.getColumnCanGlobalFilter == null ? void 0 : table.options.getColumnCanGlobalFilter(column)) != null ? _table$options$getCol : true) && !!column.accessorFn;
      },
      getIsFiltered: () => column.getFilterIndex() > -1,
      getFilterValue: () => {
        var _table$getState$colum, _table$getState$colum2;
        return (_table$getState$colum = table.getState().columnFilters) == null ? void 0 : (_table$getState$colum2 = _table$getState$colum.find((d3) => d3.id === column.id)) == null ? void 0 : _table$getState$colum2.value;
      },
      getFilterIndex: () => {
        var _table$getState$colum3, _table$getState$colum4;
        return (_table$getState$colum3 = (_table$getState$colum4 = table.getState().columnFilters) == null ? void 0 : _table$getState$colum4.findIndex((d3) => d3.id === column.id)) != null ? _table$getState$colum3 : -1;
      },
      setFilterValue: (value) => {
        table.setColumnFilters((old) => {
          const filterFn = column.getFilterFn();
          const previousfilter = old == null ? void 0 : old.find((d3) => d3.id === column.id);
          const newFilter = functionalUpdate(value, previousfilter ? previousfilter.value : void 0);
          if (shouldAutoRemoveFilter(filterFn, newFilter, column)) {
            var _old$filter;
            return (_old$filter = old == null ? void 0 : old.filter((d3) => d3.id !== column.id)) != null ? _old$filter : [];
          }
          const newFilterObj = {
            id: column.id,
            value: newFilter
          };
          if (previousfilter) {
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
      },
      _getFacetedRowModel: table.options.getFacetedRowModel && table.options.getFacetedRowModel(table, column.id),
      getFacetedRowModel: () => {
        if (!column._getFacetedRowModel) {
          return table.getPreFilteredRowModel();
        }
        return column._getFacetedRowModel();
      },
      _getFacetedUniqueValues: table.options.getFacetedUniqueValues && table.options.getFacetedUniqueValues(table, column.id),
      getFacetedUniqueValues: () => {
        if (!column._getFacetedUniqueValues) {
          return /* @__PURE__ */ new Map();
        }
        return column._getFacetedUniqueValues();
      },
      _getFacetedMinMaxValues: table.options.getFacetedMinMaxValues && table.options.getFacetedMinMaxValues(table, column.id),
      getFacetedMinMaxValues: () => {
        if (!column._getFacetedMinMaxValues) {
          return void 0;
        }
        return column._getFacetedMinMaxValues();
      }
      // () => [column.getFacetedRowModel()],
      // facetedRowModel => getRowModelMinMaxValues(facetedRowModel, column.id),
    };
  },
  createRow: (row, table) => {
    return {
      columnFilters: {},
      columnFiltersMeta: {}
    };
  },
  createTable: (table) => {
    return {
      getGlobalAutoFilterFn: () => {
        return filterFns.includesString;
      },
      getGlobalFilterFn: () => {
        var _table$options$filter3, _table$options$filter4;
        const {
          globalFilterFn
        } = table.options;
        return isFunction(globalFilterFn) ? globalFilterFn : globalFilterFn === "auto" ? table.getGlobalAutoFilterFn() : (_table$options$filter3 = (_table$options$filter4 = table.options.filterFns) == null ? void 0 : _table$options$filter4[globalFilterFn]) != null ? _table$options$filter3 : filterFns[globalFilterFn];
      },
      setColumnFilters: (updater) => {
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
        table.options.onColumnFiltersChange == null ? void 0 : table.options.onColumnFiltersChange(updateFn);
      },
      setGlobalFilter: (updater) => {
        table.options.onGlobalFilterChange == null ? void 0 : table.options.onGlobalFilterChange(updater);
      },
      resetGlobalFilter: (defaultState) => {
        table.setGlobalFilter(defaultState ? void 0 : table.initialState.globalFilter);
      },
      resetColumnFilters: (defaultState) => {
        var _table$initialState$c, _table$initialState;
        table.setColumnFilters(defaultState ? [] : (_table$initialState$c = (_table$initialState = table.initialState) == null ? void 0 : _table$initialState.columnFilters) != null ? _table$initialState$c : []);
      },
      getPreFilteredRowModel: () => table.getCoreRowModel(),
      getFilteredRowModel: () => {
        if (!table._getFilteredRowModel && table.options.getFilteredRowModel) {
          table._getFilteredRowModel = table.options.getFilteredRowModel(table);
        }
        if (table.options.manualFiltering || !table._getFilteredRowModel) {
          return table.getPreFilteredRowModel();
        }
        return table._getFilteredRowModel();
      },
      _getGlobalFacetedRowModel: table.options.getFacetedRowModel && table.options.getFacetedRowModel(table, "__global__"),
      getGlobalFacetedRowModel: () => {
        if (table.options.manualFiltering || !table._getGlobalFacetedRowModel) {
          return table.getPreFilteredRowModel();
        }
        return table._getGlobalFacetedRowModel();
      },
      _getGlobalFacetedUniqueValues: table.options.getFacetedUniqueValues && table.options.getFacetedUniqueValues(table, "__global__"),
      getGlobalFacetedUniqueValues: () => {
        if (!table._getGlobalFacetedUniqueValues) {
          return /* @__PURE__ */ new Map();
        }
        return table._getGlobalFacetedUniqueValues();
      },
      _getGlobalFacetedMinMaxValues: table.options.getFacetedMinMaxValues && table.options.getFacetedMinMaxValues(table, "__global__"),
      getGlobalFacetedMinMaxValues: () => {
        if (!table._getGlobalFacetedMinMaxValues) {
          return;
        }
        return table._getGlobalFacetedMinMaxValues();
      }
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
  const nums = values.sort((a3, b3) => a3 - b3);
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
var Grouping = {
  getDefaultColumnDef: () => {
    return {
      aggregatedCell: (props) => {
        var _toString, _props$getValue;
        return (_toString = (_props$getValue = props.getValue()) == null ? void 0 : _props$getValue.toString == null ? void 0 : _props$getValue.toString()) != null ? _toString : null;
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
    return {
      toggleGrouping: () => {
        table.setGrouping((old) => {
          if (old != null && old.includes(column.id)) {
            return old.filter((d3) => d3 !== column.id);
          }
          return [...old != null ? old : [], column.id];
        });
      },
      getCanGroup: () => {
        var _ref, _ref2, _ref3, _column$columnDef$ena;
        return (_ref = (_ref2 = (_ref3 = (_column$columnDef$ena = column.columnDef.enableGrouping) != null ? _column$columnDef$ena : true) != null ? _ref3 : table.options.enableGrouping) != null ? _ref2 : true) != null ? _ref : !!column.accessorFn;
      },
      getIsGrouped: () => {
        var _table$getState$group;
        return (_table$getState$group = table.getState().grouping) == null ? void 0 : _table$getState$group.includes(column.id);
      },
      getGroupedIndex: () => {
        var _table$getState$group2;
        return (_table$getState$group2 = table.getState().grouping) == null ? void 0 : _table$getState$group2.indexOf(column.id);
      },
      getToggleGroupingHandler: () => {
        const canGroup = column.getCanGroup();
        return () => {
          if (!canGroup)
            return;
          column.toggleGrouping();
        };
      },
      getAutoAggregationFn: () => {
        const firstRow = table.getCoreRowModel().flatRows[0];
        const value = firstRow == null ? void 0 : firstRow.getValue(column.id);
        if (typeof value === "number") {
          return aggregationFns.sum;
        }
        if (Object.prototype.toString.call(value) === "[object Date]") {
          return aggregationFns.extent;
        }
      },
      getAggregationFn: () => {
        var _table$options$aggreg, _table$options$aggreg2;
        if (!column) {
          throw new Error();
        }
        return isFunction(column.columnDef.aggregationFn) ? column.columnDef.aggregationFn : column.columnDef.aggregationFn === "auto" ? column.getAutoAggregationFn() : (_table$options$aggreg = (_table$options$aggreg2 = table.options.aggregationFns) == null ? void 0 : _table$options$aggreg2[column.columnDef.aggregationFn]) != null ? _table$options$aggreg : aggregationFns[column.columnDef.aggregationFn];
      }
    };
  },
  createTable: (table) => {
    return {
      setGrouping: (updater) => table.options.onGroupingChange == null ? void 0 : table.options.onGroupingChange(updater),
      resetGrouping: (defaultState) => {
        var _table$initialState$g, _table$initialState;
        table.setGrouping(defaultState ? [] : (_table$initialState$g = (_table$initialState = table.initialState) == null ? void 0 : _table$initialState.grouping) != null ? _table$initialState$g : []);
      },
      getPreGroupedRowModel: () => table.getFilteredRowModel(),
      getGroupedRowModel: () => {
        if (!table._getGroupedRowModel && table.options.getGroupedRowModel) {
          table._getGroupedRowModel = table.options.getGroupedRowModel(table);
        }
        if (table.options.manualGrouping || !table._getGroupedRowModel) {
          return table.getPreGroupedRowModel();
        }
        return table._getGroupedRowModel();
      }
    };
  },
  createRow: (row, table) => {
    return {
      getIsGrouped: () => !!row.groupingColumnId,
      getGroupingValue: (columnId) => {
        if (row._groupingValuesCache.hasOwnProperty(columnId)) {
          return row._groupingValuesCache[columnId];
        }
        const column = table.getColumn(columnId);
        if (!(column != null && column.columnDef.getGroupingValue)) {
          return row.getValue(columnId);
        }
        row._groupingValuesCache[columnId] = column.columnDef.getGroupingValue(row.original);
        return row._groupingValuesCache[columnId];
      },
      _groupingValuesCache: {}
    };
  },
  createCell: (cell, column, row, table) => {
    return {
      getIsGrouped: () => column.getIsGrouped() && column.id === row.groupingColumnId,
      getIsPlaceholder: () => !cell.getIsGrouped() && column.getIsGrouped(),
      getIsAggregated: () => {
        var _row$subRows;
        return !cell.getIsGrouped() && !cell.getIsPlaceholder() && !!((_row$subRows = row.subRows) != null && _row$subRows.length);
      }
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
var Ordering = {
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
  createTable: (table) => {
    return {
      setColumnOrder: (updater) => table.options.onColumnOrderChange == null ? void 0 : table.options.onColumnOrderChange(updater),
      resetColumnOrder: (defaultState) => {
        var _table$initialState$c;
        table.setColumnOrder(defaultState ? [] : (_table$initialState$c = table.initialState.columnOrder) != null ? _table$initialState$c : []);
      },
      _getOrderColumnsFn: memo(() => [table.getState().columnOrder, table.getState().grouping, table.options.groupedColumnMode], (columnOrder, grouping, groupedColumnMode) => (columns) => {
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
      }, {
        key: "getOrderColumnsFn"
        // debug: () => table.options.debugAll ?? table.options.debugTable,
      })
    };
  }
};
var defaultPageIndex = 0;
var defaultPageSize = 10;
var getDefaultPaginationState = () => ({
  pageIndex: defaultPageIndex,
  pageSize: defaultPageSize
});
var Pagination = {
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
    return {
      _autoResetPageIndex: () => {
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
      },
      setPagination: (updater) => {
        const safeUpdater = (old) => {
          let newState = functionalUpdate(updater, old);
          return newState;
        };
        return table.options.onPaginationChange == null ? void 0 : table.options.onPaginationChange(safeUpdater);
      },
      resetPagination: (defaultState) => {
        var _table$initialState$p;
        table.setPagination(defaultState ? getDefaultPaginationState() : (_table$initialState$p = table.initialState.pagination) != null ? _table$initialState$p : getDefaultPaginationState());
      },
      setPageIndex: (updater) => {
        table.setPagination((old) => {
          let pageIndex = functionalUpdate(updater, old.pageIndex);
          const maxPageIndex = typeof table.options.pageCount === "undefined" || table.options.pageCount === -1 ? Number.MAX_SAFE_INTEGER : table.options.pageCount - 1;
          pageIndex = Math.max(0, Math.min(pageIndex, maxPageIndex));
          return {
            ...old,
            pageIndex
          };
        });
      },
      resetPageIndex: (defaultState) => {
        var _table$initialState$p2, _table$initialState, _table$initialState$p3;
        table.setPageIndex(defaultState ? defaultPageIndex : (_table$initialState$p2 = (_table$initialState = table.initialState) == null ? void 0 : (_table$initialState$p3 = _table$initialState.pagination) == null ? void 0 : _table$initialState$p3.pageIndex) != null ? _table$initialState$p2 : defaultPageIndex);
      },
      resetPageSize: (defaultState) => {
        var _table$initialState$p4, _table$initialState2, _table$initialState2$;
        table.setPageSize(defaultState ? defaultPageSize : (_table$initialState$p4 = (_table$initialState2 = table.initialState) == null ? void 0 : (_table$initialState2$ = _table$initialState2.pagination) == null ? void 0 : _table$initialState2$.pageSize) != null ? _table$initialState$p4 : defaultPageSize);
      },
      setPageSize: (updater) => {
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
      },
      setPageCount: (updater) => table.setPagination((old) => {
        var _table$options$pageCo;
        let newPageCount = functionalUpdate(updater, (_table$options$pageCo = table.options.pageCount) != null ? _table$options$pageCo : -1);
        if (typeof newPageCount === "number") {
          newPageCount = Math.max(-1, newPageCount);
        }
        return {
          ...old,
          pageCount: newPageCount
        };
      }),
      getPageOptions: memo(() => [table.getPageCount()], (pageCount) => {
        let pageOptions = [];
        if (pageCount && pageCount > 0) {
          pageOptions = [...new Array(pageCount)].fill(null).map((_3, i4) => i4);
        }
        return pageOptions;
      }, {
        key: "getPageOptions",
        debug: () => {
          var _table$options$debugA;
          return (_table$options$debugA = table.options.debugAll) != null ? _table$options$debugA : table.options.debugTable;
        }
      }),
      getCanPreviousPage: () => table.getState().pagination.pageIndex > 0,
      getCanNextPage: () => {
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
      },
      previousPage: () => {
        return table.setPageIndex((old) => old - 1);
      },
      nextPage: () => {
        return table.setPageIndex((old) => {
          return old + 1;
        });
      },
      getPrePaginationRowModel: () => table.getExpandedRowModel(),
      getPaginationRowModel: () => {
        if (!table._getPaginationRowModel && table.options.getPaginationRowModel) {
          table._getPaginationRowModel = table.options.getPaginationRowModel(table);
        }
        if (table.options.manualPagination || !table._getPaginationRowModel) {
          return table.getPrePaginationRowModel();
        }
        return table._getPaginationRowModel();
      },
      getPageCount: () => {
        var _table$options$pageCo2;
        return (_table$options$pageCo2 = table.options.pageCount) != null ? _table$options$pageCo2 : Math.ceil(table.getPrePaginationRowModel().rows.length / table.getState().pagination.pageSize);
      }
    };
  }
};
var getDefaultPinningState = () => ({
  left: [],
  right: []
});
var Pinning = {
  getInitialState: (state) => {
    return {
      columnPinning: getDefaultPinningState(),
      ...state
    };
  },
  getDefaultOptions: (table) => {
    return {
      onColumnPinningChange: makeStateUpdater("columnPinning", table)
    };
  },
  createColumn: (column, table) => {
    return {
      pin: (position) => {
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
      },
      getCanPin: () => {
        const leafColumns = column.getLeafColumns();
        return leafColumns.some((d3) => {
          var _d$columnDef$enablePi, _table$options$enable;
          return ((_d$columnDef$enablePi = d3.columnDef.enablePinning) != null ? _d$columnDef$enablePi : true) && ((_table$options$enable = table.options.enablePinning) != null ? _table$options$enable : true);
        });
      },
      getIsPinned: () => {
        const leafColumnIds = column.getLeafColumns().map((d3) => d3.id);
        const {
          left,
          right
        } = table.getState().columnPinning;
        const isLeft = leafColumnIds.some((d3) => left == null ? void 0 : left.includes(d3));
        const isRight = leafColumnIds.some((d3) => right == null ? void 0 : right.includes(d3));
        return isLeft ? "left" : isRight ? "right" : false;
      },
      getPinnedIndex: () => {
        var _table$getState$colum, _table$getState$colum2, _table$getState$colum3;
        const position = column.getIsPinned();
        return position ? (_table$getState$colum = (_table$getState$colum2 = table.getState().columnPinning) == null ? void 0 : (_table$getState$colum3 = _table$getState$colum2[position]) == null ? void 0 : _table$getState$colum3.indexOf(column.id)) != null ? _table$getState$colum : -1 : 0;
      }
    };
  },
  createRow: (row, table) => {
    return {
      getCenterVisibleCells: memo(() => [row._getAllVisibleCells(), table.getState().columnPinning.left, table.getState().columnPinning.right], (allCells, left, right) => {
        const leftAndRight = [...left != null ? left : [], ...right != null ? right : []];
        return allCells.filter((d3) => !leftAndRight.includes(d3.column.id));
      }, {
        key: false,
        debug: () => {
          var _table$options$debugA;
          return (_table$options$debugA = table.options.debugAll) != null ? _table$options$debugA : table.options.debugRows;
        }
      }),
      getLeftVisibleCells: memo(() => [row._getAllVisibleCells(), table.getState().columnPinning.left, ,], (allCells, left) => {
        const cells = (left != null ? left : []).map((columnId) => allCells.find((cell) => cell.column.id === columnId)).filter(Boolean).map((d3) => ({
          ...d3,
          position: "left"
        }));
        return cells;
      }, {
        key: false,
        debug: () => {
          var _table$options$debugA2;
          return (_table$options$debugA2 = table.options.debugAll) != null ? _table$options$debugA2 : table.options.debugRows;
        }
      }),
      getRightVisibleCells: memo(() => [row._getAllVisibleCells(), table.getState().columnPinning.right], (allCells, right) => {
        const cells = (right != null ? right : []).map((columnId) => allCells.find((cell) => cell.column.id === columnId)).filter(Boolean).map((d3) => ({
          ...d3,
          position: "right"
        }));
        return cells;
      }, {
        key: false,
        debug: () => {
          var _table$options$debugA3;
          return (_table$options$debugA3 = table.options.debugAll) != null ? _table$options$debugA3 : table.options.debugRows;
        }
      })
    };
  },
  createTable: (table) => {
    return {
      setColumnPinning: (updater) => table.options.onColumnPinningChange == null ? void 0 : table.options.onColumnPinningChange(updater),
      resetColumnPinning: (defaultState) => {
        var _table$initialState$c, _table$initialState;
        return table.setColumnPinning(defaultState ? getDefaultPinningState() : (_table$initialState$c = (_table$initialState = table.initialState) == null ? void 0 : _table$initialState.columnPinning) != null ? _table$initialState$c : getDefaultPinningState());
      },
      getIsSomeColumnsPinned: (position) => {
        var _pinningState$positio;
        const pinningState = table.getState().columnPinning;
        if (!position) {
          var _pinningState$left, _pinningState$right;
          return Boolean(((_pinningState$left = pinningState.left) == null ? void 0 : _pinningState$left.length) || ((_pinningState$right = pinningState.right) == null ? void 0 : _pinningState$right.length));
        }
        return Boolean((_pinningState$positio = pinningState[position]) == null ? void 0 : _pinningState$positio.length);
      },
      getLeftLeafColumns: memo(() => [table.getAllLeafColumns(), table.getState().columnPinning.left], (allColumns, left) => {
        return (left != null ? left : []).map((columnId) => allColumns.find((column) => column.id === columnId)).filter(Boolean);
      }, {
        key: "getLeftLeafColumns",
        debug: () => {
          var _table$options$debugA4;
          return (_table$options$debugA4 = table.options.debugAll) != null ? _table$options$debugA4 : table.options.debugColumns;
        }
      }),
      getRightLeafColumns: memo(() => [table.getAllLeafColumns(), table.getState().columnPinning.right], (allColumns, right) => {
        return (right != null ? right : []).map((columnId) => allColumns.find((column) => column.id === columnId)).filter(Boolean);
      }, {
        key: "getRightLeafColumns",
        debug: () => {
          var _table$options$debugA5;
          return (_table$options$debugA5 = table.options.debugAll) != null ? _table$options$debugA5 : table.options.debugColumns;
        }
      }),
      getCenterLeafColumns: memo(() => [table.getAllLeafColumns(), table.getState().columnPinning.left, table.getState().columnPinning.right], (allColumns, left, right) => {
        const leftAndRight = [...left != null ? left : [], ...right != null ? right : []];
        return allColumns.filter((d3) => !leftAndRight.includes(d3.id));
      }, {
        key: "getCenterLeafColumns",
        debug: () => {
          var _table$options$debugA6;
          return (_table$options$debugA6 = table.options.debugAll) != null ? _table$options$debugA6 : table.options.debugColumns;
        }
      })
    };
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
    return {
      setRowSelection: (updater) => table.options.onRowSelectionChange == null ? void 0 : table.options.onRowSelectionChange(updater),
      resetRowSelection: (defaultState) => {
        var _table$initialState$r;
        return table.setRowSelection(defaultState ? {} : (_table$initialState$r = table.initialState.rowSelection) != null ? _table$initialState$r : {});
      },
      toggleAllRowsSelected: (value) => {
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
      },
      toggleAllPageRowsSelected: (value) => table.setRowSelection((old) => {
        const resolvedValue = typeof value !== "undefined" ? value : !table.getIsAllPageRowsSelected();
        const rowSelection = {
          ...old
        };
        table.getRowModel().rows.forEach((row) => {
          mutateRowIsSelected(rowSelection, row.id, resolvedValue, table);
        });
        return rowSelection;
      }),
      // addRowSelectionRange: rowId => {
      //   const {
      //     rows,
      //     rowsById,
      //     options: { selectGroupingRows, selectSubRows },
      //   } = table
      //   const findSelectedRow = (rows: Row[]) => {
      //     let found
      //     rows.find(d => {
      //       if (d.getIsSelected()) {
      //         found = d
      //         return true
      //       }
      //       const subFound = findSelectedRow(d.subRows || [])
      //       if (subFound) {
      //         found = subFound
      //         return true
      //       }
      //       return false
      //     })
      //     return found
      //   }
      //   const firstRow = findSelectedRow(rows) || rows[0]
      //   const lastRow = rowsById[rowId]
      //   let include = false
      //   const selectedRowIds = {}
      //   const addRow = (row: Row) => {
      //     mutateRowIsSelected(selectedRowIds, row.id, true, {
      //       rowsById,
      //       selectGroupingRows: selectGroupingRows!,
      //       selectSubRows: selectSubRows!,
      //     })
      //   }
      //   table.rows.forEach(row => {
      //     const isFirstRow = row.id === firstRow.id
      //     const isLastRow = row.id === lastRow.id
      //     if (isFirstRow || isLastRow) {
      //       if (!include) {
      //         include = true
      //       } else if (include) {
      //         addRow(row)
      //         include = false
      //       }
      //     }
      //     if (include) {
      //       addRow(row)
      //     }
      //   })
      //   table.setRowSelection(selectedRowIds)
      // },
      getPreSelectedRowModel: () => table.getCoreRowModel(),
      getSelectedRowModel: memo(() => [table.getState().rowSelection, table.getCoreRowModel()], (rowSelection, rowModel) => {
        if (!Object.keys(rowSelection).length) {
          return {
            rows: [],
            flatRows: [],
            rowsById: {}
          };
        }
        return selectRowsFn(table, rowModel);
      }, {
        key: "getSelectedRowModel",
        debug: () => {
          var _table$options$debugA;
          return (_table$options$debugA = table.options.debugAll) != null ? _table$options$debugA : table.options.debugTable;
        }
      }),
      getFilteredSelectedRowModel: memo(() => [table.getState().rowSelection, table.getFilteredRowModel()], (rowSelection, rowModel) => {
        if (!Object.keys(rowSelection).length) {
          return {
            rows: [],
            flatRows: [],
            rowsById: {}
          };
        }
        return selectRowsFn(table, rowModel);
      }, {
        key: false,
        debug: () => {
          var _table$options$debugA2;
          return (_table$options$debugA2 = table.options.debugAll) != null ? _table$options$debugA2 : table.options.debugTable;
        }
      }),
      getGroupedSelectedRowModel: memo(() => [table.getState().rowSelection, table.getSortedRowModel()], (rowSelection, rowModel) => {
        if (!Object.keys(rowSelection).length) {
          return {
            rows: [],
            flatRows: [],
            rowsById: {}
          };
        }
        return selectRowsFn(table, rowModel);
      }, {
        key: false,
        debug: () => {
          var _table$options$debugA3;
          return (_table$options$debugA3 = table.options.debugAll) != null ? _table$options$debugA3 : table.options.debugTable;
        }
      }),
      ///
      // getGroupingRowCanSelect: rowId => {
      //   const row = table.getRow(rowId)
      //   if (!row) {
      //     throw new Error()
      //   }
      //   if (typeof table.options.enableGroupingRowSelection === 'function') {
      //     return table.options.enableGroupingRowSelection(row)
      //   }
      //   return table.options.enableGroupingRowSelection ?? false
      // },
      getIsAllRowsSelected: () => {
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
      },
      getIsAllPageRowsSelected: () => {
        const paginationFlatRows = table.getPaginationRowModel().flatRows.filter((row) => row.getCanSelect());
        const {
          rowSelection
        } = table.getState();
        let isAllPageRowsSelected = !!paginationFlatRows.length;
        if (isAllPageRowsSelected && paginationFlatRows.some((row) => !rowSelection[row.id])) {
          isAllPageRowsSelected = false;
        }
        return isAllPageRowsSelected;
      },
      getIsSomeRowsSelected: () => {
        var _table$getState$rowSe;
        const totalSelected = Object.keys((_table$getState$rowSe = table.getState().rowSelection) != null ? _table$getState$rowSe : {}).length;
        return totalSelected > 0 && totalSelected < table.getFilteredRowModel().flatRows.length;
      },
      getIsSomePageRowsSelected: () => {
        const paginationFlatRows = table.getPaginationRowModel().flatRows;
        return table.getIsAllPageRowsSelected() ? false : paginationFlatRows.filter((row) => row.getCanSelect()).some((d3) => d3.getIsSelected() || d3.getIsSomeSelected());
      },
      getToggleAllRowsSelectedHandler: () => {
        return (e3) => {
          table.toggleAllRowsSelected(e3.target.checked);
        };
      },
      getToggleAllPageRowsSelectedHandler: () => {
        return (e3) => {
          table.toggleAllPageRowsSelected(e3.target.checked);
        };
      }
    };
  },
  createRow: (row, table) => {
    return {
      toggleSelected: (value) => {
        const isSelected = row.getIsSelected();
        table.setRowSelection((old) => {
          value = typeof value !== "undefined" ? value : !isSelected;
          if (isSelected === value) {
            return old;
          }
          const selectedRowIds = {
            ...old
          };
          mutateRowIsSelected(selectedRowIds, row.id, value, table);
          return selectedRowIds;
        });
      },
      getIsSelected: () => {
        const {
          rowSelection
        } = table.getState();
        return isRowSelected(row, rowSelection);
      },
      getIsSomeSelected: () => {
        const {
          rowSelection
        } = table.getState();
        return isSubRowSelected(row, rowSelection) === "some";
      },
      getIsAllSubRowsSelected: () => {
        const {
          rowSelection
        } = table.getState();
        return isSubRowSelected(row, rowSelection) === "all";
      },
      getCanSelect: () => {
        var _table$options$enable;
        if (typeof table.options.enableRowSelection === "function") {
          return table.options.enableRowSelection(row);
        }
        return (_table$options$enable = table.options.enableRowSelection) != null ? _table$options$enable : true;
      },
      getCanSelectSubRows: () => {
        var _table$options$enable2;
        if (typeof table.options.enableSubRowSelection === "function") {
          return table.options.enableSubRowSelection(row);
        }
        return (_table$options$enable2 = table.options.enableSubRowSelection) != null ? _table$options$enable2 : true;
      },
      getCanMultiSelect: () => {
        var _table$options$enable3;
        if (typeof table.options.enableMultiRowSelection === "function") {
          return table.options.enableMultiRowSelection(row);
        }
        return (_table$options$enable3 = table.options.enableMultiRowSelection) != null ? _table$options$enable3 : true;
      },
      getToggleSelectedHandler: () => {
        const canSelect = row.getCanSelect();
        return (e3) => {
          var _target;
          if (!canSelect)
            return;
          row.toggleSelected((_target = e3.target) == null ? void 0 : _target.checked);
        };
      }
    };
  }
};
var mutateRowIsSelected = (selectedRowIds, id, value, table) => {
  var _row$subRows;
  const row = table.getRow(id);
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
  if ((_row$subRows = row.subRows) != null && _row$subRows.length && row.getCanSelectSubRows()) {
    row.subRows.forEach((row2) => mutateRowIsSelected(selectedRowIds, row2.id, value, table));
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
  if (row.subRows && row.subRows.length) {
    let allChildrenSelected = true;
    let someSelected = false;
    row.subRows.forEach((subRow) => {
      if (someSelected && !allChildrenSelected) {
        return;
      }
      if (isRowSelected(subRow, selection)) {
        someSelected = true;
      } else {
        allChildrenSelected = false;
      }
    });
    return allChildrenSelected ? "all" : someSelected ? "some" : false;
  }
  return false;
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
  const b3 = rowB.getValue(columnId);
  return a3 > b3 ? 1 : a3 < b3 ? -1 : 0;
};
var basic = (rowA, rowB, columnId) => {
  return compareBasic(rowA.getValue(columnId), rowB.getValue(columnId));
};
function compareBasic(a3, b3) {
  return a3 === b3 ? 0 : a3 > b3 ? 1 : -1;
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
  const b3 = bStr.split(reSplitAlphaNumeric).filter(Boolean);
  while (a3.length && b3.length) {
    const aa = a3.shift();
    const bb = b3.shift();
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
  return a3.length - b3.length;
}
var sortingFns = {
  alphanumeric,
  alphanumericCaseSensitive,
  text,
  textCaseSensitive,
  datetime,
  basic
};
var Sorting = {
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
    return {
      getAutoSortingFn: () => {
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
      },
      getAutoSortDir: () => {
        const firstRow = table.getFilteredRowModel().flatRows[0];
        const value = firstRow == null ? void 0 : firstRow.getValue(column.id);
        if (typeof value === "string") {
          return "asc";
        }
        return "desc";
      },
      getSortingFn: () => {
        var _table$options$sortin, _table$options$sortin2;
        if (!column) {
          throw new Error();
        }
        return isFunction(column.columnDef.sortingFn) ? column.columnDef.sortingFn : column.columnDef.sortingFn === "auto" ? column.getAutoSortingFn() : (_table$options$sortin = (_table$options$sortin2 = table.options.sortingFns) == null ? void 0 : _table$options$sortin2[column.columnDef.sortingFn]) != null ? _table$options$sortin : sortingFns[column.columnDef.sortingFn];
      },
      toggleSorting: (desc, multi) => {
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
      },
      getFirstSortDir: () => {
        var _ref, _column$columnDef$sor;
        const sortDescFirst = (_ref = (_column$columnDef$sor = column.columnDef.sortDescFirst) != null ? _column$columnDef$sor : table.options.sortDescFirst) != null ? _ref : column.getAutoSortDir() === "desc";
        return sortDescFirst ? "desc" : "asc";
      },
      getNextSortingOrder: (multi) => {
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
      },
      getCanSort: () => {
        var _column$columnDef$ena, _table$options$enable3;
        return ((_column$columnDef$ena = column.columnDef.enableSorting) != null ? _column$columnDef$ena : true) && ((_table$options$enable3 = table.options.enableSorting) != null ? _table$options$enable3 : true) && !!column.accessorFn;
      },
      getCanMultiSort: () => {
        var _ref2, _column$columnDef$ena2;
        return (_ref2 = (_column$columnDef$ena2 = column.columnDef.enableMultiSort) != null ? _column$columnDef$ena2 : table.options.enableMultiSort) != null ? _ref2 : !!column.accessorFn;
      },
      getIsSorted: () => {
        var _table$getState$sorti;
        const columnSort = (_table$getState$sorti = table.getState().sorting) == null ? void 0 : _table$getState$sorti.find((d3) => d3.id === column.id);
        return !columnSort ? false : columnSort.desc ? "desc" : "asc";
      },
      getSortIndex: () => {
        var _table$getState$sorti2, _table$getState$sorti3;
        return (_table$getState$sorti2 = (_table$getState$sorti3 = table.getState().sorting) == null ? void 0 : _table$getState$sorti3.findIndex((d3) => d3.id === column.id)) != null ? _table$getState$sorti2 : -1;
      },
      clearSorting: () => {
        table.setSorting((old) => old != null && old.length ? old.filter((d3) => d3.id !== column.id) : []);
      },
      getToggleSortingHandler: () => {
        const canSort = column.getCanSort();
        return (e3) => {
          if (!canSort)
            return;
          e3.persist == null ? void 0 : e3.persist();
          column.toggleSorting == null ? void 0 : column.toggleSorting(void 0, column.getCanMultiSort() ? table.options.isMultiSortEvent == null ? void 0 : table.options.isMultiSortEvent(e3) : false);
        };
      }
    };
  },
  createTable: (table) => {
    return {
      setSorting: (updater) => table.options.onSortingChange == null ? void 0 : table.options.onSortingChange(updater),
      resetSorting: (defaultState) => {
        var _table$initialState$s, _table$initialState;
        table.setSorting(defaultState ? [] : (_table$initialState$s = (_table$initialState = table.initialState) == null ? void 0 : _table$initialState.sorting) != null ? _table$initialState$s : []);
      },
      getPreSortedRowModel: () => table.getGroupedRowModel(),
      getSortedRowModel: () => {
        if (!table._getSortedRowModel && table.options.getSortedRowModel) {
          table._getSortedRowModel = table.options.getSortedRowModel(table);
        }
        if (table.options.manualSorting || !table._getSortedRowModel) {
          return table.getPreSortedRowModel();
        }
        return table._getSortedRowModel();
      }
    };
  }
};
var Visibility = {
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
    return {
      toggleVisibility: (value) => {
        if (column.getCanHide()) {
          table.setColumnVisibility((old) => ({
            ...old,
            [column.id]: value != null ? value : !column.getIsVisible()
          }));
        }
      },
      getIsVisible: () => {
        var _table$getState$colum, _table$getState$colum2;
        return (_table$getState$colum = (_table$getState$colum2 = table.getState().columnVisibility) == null ? void 0 : _table$getState$colum2[column.id]) != null ? _table$getState$colum : true;
      },
      getCanHide: () => {
        var _column$columnDef$ena, _table$options$enable;
        return ((_column$columnDef$ena = column.columnDef.enableHiding) != null ? _column$columnDef$ena : true) && ((_table$options$enable = table.options.enableHiding) != null ? _table$options$enable : true);
      },
      getToggleVisibilityHandler: () => {
        return (e3) => {
          column.toggleVisibility == null ? void 0 : column.toggleVisibility(e3.target.checked);
        };
      }
    };
  },
  createRow: (row, table) => {
    return {
      _getAllVisibleCells: memo(() => [row.getAllCells(), table.getState().columnVisibility], (cells) => {
        return cells.filter((cell) => cell.column.getIsVisible());
      }, {
        key: false,
        debug: () => {
          var _table$options$debugA;
          return (_table$options$debugA = table.options.debugAll) != null ? _table$options$debugA : table.options.debugRows;
        }
      }),
      getVisibleCells: memo(() => [row.getLeftVisibleCells(), row.getCenterVisibleCells(), row.getRightVisibleCells()], (left, center, right) => [...left, ...center, ...right], {
        key: "row.getVisibleCells",
        debug: () => {
          var _table$options$debugA2;
          return (_table$options$debugA2 = table.options.debugAll) != null ? _table$options$debugA2 : table.options.debugRows;
        }
      })
    };
  },
  createTable: (table) => {
    const makeVisibleColumnsMethod = (key, getColumns) => {
      return memo(() => [getColumns(), getColumns().filter((d3) => d3.getIsVisible()).map((d3) => d3.id).join("_")], (columns) => {
        return columns.filter((d3) => d3.getIsVisible == null ? void 0 : d3.getIsVisible());
      }, {
        key,
        debug: () => {
          var _table$options$debugA3;
          return (_table$options$debugA3 = table.options.debugAll) != null ? _table$options$debugA3 : table.options.debugColumns;
        }
      });
    };
    return {
      getVisibleFlatColumns: makeVisibleColumnsMethod("getVisibleFlatColumns", () => table.getAllFlatColumns()),
      getVisibleLeafColumns: makeVisibleColumnsMethod("getVisibleLeafColumns", () => table.getAllLeafColumns()),
      getLeftVisibleLeafColumns: makeVisibleColumnsMethod("getLeftVisibleLeafColumns", () => table.getLeftLeafColumns()),
      getRightVisibleLeafColumns: makeVisibleColumnsMethod("getRightVisibleLeafColumns", () => table.getRightLeafColumns()),
      getCenterVisibleLeafColumns: makeVisibleColumnsMethod("getCenterVisibleLeafColumns", () => table.getCenterLeafColumns()),
      setColumnVisibility: (updater) => table.options.onColumnVisibilityChange == null ? void 0 : table.options.onColumnVisibilityChange(updater),
      resetColumnVisibility: (defaultState) => {
        var _table$initialState$c;
        table.setColumnVisibility(defaultState ? {} : (_table$initialState$c = table.initialState.columnVisibility) != null ? _table$initialState$c : {});
      },
      toggleAllColumnsVisible: (value) => {
        var _value;
        value = (_value = value) != null ? _value : !table.getIsAllColumnsVisible();
        table.setColumnVisibility(table.getAllLeafColumns().reduce((obj, column) => ({
          ...obj,
          [column.id]: !value ? !(column.getCanHide != null && column.getCanHide()) : value
        }), {}));
      },
      getIsAllColumnsVisible: () => !table.getAllLeafColumns().some((column) => !(column.getIsVisible != null && column.getIsVisible())),
      getIsSomeColumnsVisible: () => table.getAllLeafColumns().some((column) => column.getIsVisible == null ? void 0 : column.getIsVisible()),
      getToggleAllColumnsVisibilityHandler: () => {
        return (e3) => {
          var _target;
          table.toggleAllColumnsVisible((_target = e3.target) == null ? void 0 : _target.checked);
        };
      }
    };
  }
};
var features = [Headers, Visibility, Ordering, Pinning, Filters, Sorting, Grouping, Expanding, Pagination, RowSelection, ColumnSizing];
function createTable(options) {
  var _options$initialState;
  if (options.debugAll || options.debugTable) {
    console.info("Creating Table Instance...");
  }
  let table = {
    _features: features
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
    _features: features,
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
      table.options.onStateChange == null ? void 0 : table.options.onStateChange(updater);
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
    getRow: (id) => {
      const row = table.getRowModel().rowsById[id];
      if (!row) {
        if (true) {
          throw new Error(`getRow expected an ID, but got ${id}`);
        }
        throw new Error();
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
          return (_props$renderValue$to = (_props$renderValue = props.renderValue()) == null ? void 0 : _props$renderValue.toString == null ? void 0 : _props$renderValue.toString()) != null ? _props$renderValue$to : null;
        },
        ...table._features.reduce((obj, feature) => {
          return Object.assign(obj, feature.getDefaultColumnDef == null ? void 0 : feature.getDefaultColumnDef());
        }, {}),
        ...defaultColumn
      };
    }, {
      debug: () => {
        var _table$options$debugA;
        return (_table$options$debugA = table.options.debugAll) != null ? _table$options$debugA : table.options.debugColumns;
      },
      key: "getDefaultColumnDef"
    }),
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
    }, {
      key: "getAllColumns",
      debug: () => {
        var _table$options$debugA2;
        return (_table$options$debugA2 = table.options.debugAll) != null ? _table$options$debugA2 : table.options.debugColumns;
      }
    }),
    getAllFlatColumns: memo(() => [table.getAllColumns()], (allColumns) => {
      return allColumns.flatMap((column) => {
        return column.getFlatColumns();
      });
    }, {
      key: "getAllFlatColumns",
      debug: () => {
        var _table$options$debugA3;
        return (_table$options$debugA3 = table.options.debugAll) != null ? _table$options$debugA3 : table.options.debugColumns;
      }
    }),
    _getAllFlatColumnsById: memo(() => [table.getAllFlatColumns()], (flatColumns) => {
      return flatColumns.reduce((acc, column) => {
        acc[column.id] = column;
        return acc;
      }, {});
    }, {
      key: "getAllFlatColumnsById",
      debug: () => {
        var _table$options$debugA4;
        return (_table$options$debugA4 = table.options.debugAll) != null ? _table$options$debugA4 : table.options.debugColumns;
      }
    }),
    getAllLeafColumns: memo(() => [table.getAllColumns(), table._getOrderColumnsFn()], (allColumns, orderColumns2) => {
      let leafColumns = allColumns.flatMap((column) => column.getLeafColumns());
      return orderColumns2(leafColumns);
    }, {
      key: "getAllLeafColumns",
      debug: () => {
        var _table$options$debugA5;
        return (_table$options$debugA5 = table.options.debugAll) != null ? _table$options$debugA5 : table.options.debugColumns;
      }
    }),
    getColumn: (columnId) => {
      const column = table._getAllFlatColumnsById()[columnId];
      if (!column) {
        console.error(`[Table] Column with id '${columnId}' does not exist.`);
      }
      return column;
    }
  };
  Object.assign(table, coreInstance);
  table._features.forEach((feature) => {
    return Object.assign(table, feature.createTable == null ? void 0 : feature.createTable(table));
  });
  return table;
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
    }), {
      key: "cell.getContext",
      debug: () => table.options.debugAll
    })
  };
  table._features.forEach((feature) => {
    Object.assign(cell, feature.createCell == null ? void 0 : feature.createCell(cell, column, row, table));
  }, {});
  return cell;
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
    getParentRow: () => row.parentId ? table.getRow(row.parentId) : void 0,
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
    }, {
      key: "row.getAllCells",
      debug: () => {
        var _table$options$debugA;
        return (_table$options$debugA = table.options.debugAll) != null ? _table$options$debugA : table.options.debugRows;
      }
    }),
    _getAllCellsByColumnId: memo(() => [row.getAllCells()], (allCells) => {
      return allCells.reduce((acc, cell) => {
        acc[cell.column.id] = cell;
        return acc;
      }, {});
    }, {
      key: false,
      debug: () => {
        var _table$options$debugA2;
        return (_table$options$debugA2 = table.options.debugAll) != null ? _table$options$debugA2 : table.options.debugRows;
      }
    })
  };
  for (let i4 = 0; i4 < table._features.length; i4++) {
    const feature = table._features[i4];
    Object.assign(row, feature == null ? void 0 : feature.createRow == null ? void 0 : feature.createRow(row, table));
  }
  return row;
};
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
  }, {
    key: "getRowModel",
    debug: () => {
      var _table$options$debugA;
      return (_table$options$debugA = table.options.debugAll) != null ? _table$options$debugA : table.options.debugTable;
    },
    onChange: () => {
      table._autoResetPageIndex();
    }
  });
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
          newFilteredRowsById[i4] = row;
          continue;
        }
        if (filterRow(row) || newRow.subRows.length) {
          rows.push(row);
          newFilteredRowsById[row.id] = row;
          newFilteredRowsById[i4] = row;
          continue;
        }
      } else {
        row = newRow;
        if (filterRow(row)) {
          rows.push(row);
          newFilteredRowsById[row.id] = row;
          newFilteredRowsById[i4] = row;
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
    const filterableIds = columnFilters.map((d3) => d3.id);
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
  }, {
    key: "getFilteredRowModel",
    debug: () => {
      var _table$options$debugA;
      return (_table$options$debugA = table.options.debugAll) != null ? _table$options$debugA : table.options.debugTable;
    },
    onChange: () => {
      table._autoResetPageIndex();
    }
  });
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
  }, {
    key: "getFacetedRowModel_" + columnId,
    debug: () => {
      var _table$options$debugA;
      return (_table$options$debugA = table.options.debugAll) != null ? _table$options$debugA : table.options.debugTable;
    },
    onChange: () => {
    }
  });
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
  }, {
    key: "getFacetedUniqueValues_" + columnId,
    debug: () => {
      var _table$options$debugA;
      return (_table$options$debugA = table.options.debugAll) != null ? _table$options$debugA : table.options.debugTable;
    },
    onChange: () => {
    }
  });
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
  }, {
    key: "getFacetedMinMaxValues_" + columnId,
    debug: () => {
      var _table$options$debugA;
      return (_table$options$debugA = table.options.debugAll) != null ? _table$options$debugA : table.options.debugTable;
    },
    onChange: () => {
    }
  });
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
      const sortedData = [...rows];
      sortedData.sort((rowA, rowB) => {
        for (let i4 = 0; i4 < availableSorting.length; i4 += 1) {
          var _sortEntry$desc;
          const sortEntry = availableSorting[i4];
          const columnInfo = columnInfoById[sortEntry.id];
          const isDesc = (_sortEntry$desc = sortEntry == null ? void 0 : sortEntry.desc) != null ? _sortEntry$desc : false;
          let sortInt = 0;
          if (columnInfo.sortUndefined) {
            const aValue = rowA.getValue(sortEntry.id);
            const bValue = rowB.getValue(sortEntry.id);
            const aUndefined = aValue === void 0;
            const bUndefined = bValue === void 0;
            if (aUndefined || bUndefined) {
              sortInt = aUndefined && bUndefined ? 0 : aUndefined ? columnInfo.sortUndefined : -columnInfo.sortUndefined;
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
  }, {
    key: "getSortedRowModel",
    debug: () => {
      var _table$options$debugA;
      return (_table$options$debugA = table.options.debugAll) != null ? _table$options$debugA : table.options.debugTable;
    },
    onChange: () => {
      table._autoResetPageIndex();
    }
  });
}

// node_modules/@tanstack/react-table/build/lib/index.mjs
function flexRender(Comp, props) {
  return !Comp ? null : isReactComponent(Comp) ? /* @__PURE__ */ y(Comp, props) : Comp;
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
      options.onStateChange == null ? void 0 : options.onStateChange(updater);
    }
  }));
  return tableRef.current;
}

// node_modules/@tanstack/react-virtual/build/lib/_virtual/_rollupPluginBabelHelpers.mjs
function _extends() {
  _extends = Object.assign ? Object.assign.bind() : function(target) {
    for (var i4 = 1; i4 < arguments.length; i4++) {
      var source = arguments[i4];
      for (var key in source) {
        if (Object.prototype.hasOwnProperty.call(source, key)) {
          target[key] = source[key];
        }
      }
    }
    return target;
  };
  return _extends.apply(this, arguments);
}

// node_modules/@tanstack/virtual-core/build/lib/_virtual/_rollupPluginBabelHelpers.mjs
function _extends2() {
  _extends2 = Object.assign ? Object.assign.bind() : function(target) {
    for (var i4 = 1; i4 < arguments.length; i4++) {
      var source = arguments[i4];
      for (var key in source) {
        if (Object.prototype.hasOwnProperty.call(source, key)) {
          target[key] = source[key];
        }
      }
    }
    return target;
  };
  return _extends2.apply(this, arguments);
}

// node_modules/@tanstack/virtual-core/build/lib/utils.mjs
function memo2(getDeps, fn2, opts) {
  var _opts$initialDeps;
  var deps = (_opts$initialDeps = opts.initialDeps) != null ? _opts$initialDeps : [];
  var result;
  return function() {
    var depTime;
    if (opts.key && opts.debug != null && opts.debug())
      depTime = Date.now();
    var newDeps = getDeps();
    var depsChanged = newDeps.length !== deps.length || newDeps.some(function(dep, index) {
      return deps[index] !== dep;
    });
    if (!depsChanged) {
      return result;
    }
    deps = newDeps;
    var resultTime;
    if (opts.key && opts.debug != null && opts.debug())
      resultTime = Date.now();
    result = fn2.apply(void 0, newDeps);
    if (opts.key && opts.debug != null && opts.debug()) {
      var depEndTime = Math.round((Date.now() - depTime) * 100) / 100;
      var resultEndTime = Math.round((Date.now() - resultTime) * 100) / 100;
      var resultFpsPercentage = resultEndTime / 16;
      var pad = function pad2(str, num) {
        str = String(str);
        while (str.length < num) {
          str = " " + str;
        }
        return str;
      };
      console.info("%c\u23F1 " + pad(resultEndTime, 5) + " /" + pad(depEndTime, 5) + " ms", "\n            font-size: .6rem;\n            font-weight: bold;\n            color: hsl(" + Math.max(0, Math.min(120 - 120 * resultFpsPercentage, 120)) + "deg 100% 31%);", opts == null ? void 0 : opts.key);
    }
    opts == null ? void 0 : opts.onChange == null ? void 0 : opts.onChange(result);
    return result;
  };
}
function notUndefined(value, msg) {
  if (value === void 0) {
    throw new Error("Unexpected undefined" + (msg ? ": " + msg : ""));
  } else {
    return value;
  }
}
var approxEqual = function approxEqual2(a3, b3) {
  return Math.abs(a3 - b3) < 1;
};

// node_modules/@tanstack/virtual-core/build/lib/index.mjs
var defaultKeyExtractor = function defaultKeyExtractor2(index) {
  return index;
};
var defaultRangeExtractor = function defaultRangeExtractor2(range) {
  var start = Math.max(range.startIndex - range.overscan, 0);
  var end = Math.min(range.endIndex + range.overscan, range.count - 1);
  var arr = [];
  for (var _i = start; _i <= end; _i++) {
    arr.push(_i);
  }
  return arr;
};
var observeElementRect = function observeElementRect2(instance, cb) {
  var element = instance.scrollElement;
  if (!element) {
    return;
  }
  var handler = function handler2(rect) {
    var width = rect.width, height = rect.height;
    cb({
      width: Math.round(width),
      height: Math.round(height)
    });
  };
  handler(element.getBoundingClientRect());
  var observer = new ResizeObserver(function(entries) {
    var entry = entries[0];
    if (entry != null && entry.borderBoxSize) {
      var box = entry.borderBoxSize[0];
      if (box) {
        handler({
          width: box.inlineSize,
          height: box.blockSize
        });
        return;
      }
    }
    handler(element.getBoundingClientRect());
  });
  observer.observe(element, {
    box: "border-box"
  });
  return function() {
    observer.unobserve(element);
  };
};
var observeElementOffset = function observeElementOffset2(instance, cb) {
  var element = instance.scrollElement;
  if (!element) {
    return;
  }
  var handler = function handler2() {
    cb(element[instance.options.horizontal ? "scrollLeft" : "scrollTop"]);
  };
  handler();
  element.addEventListener("scroll", handler, {
    passive: true
  });
  return function() {
    element.removeEventListener("scroll", handler);
  };
};
var measureElement = function measureElement2(element, entry, instance) {
  if (entry != null && entry.borderBoxSize) {
    var box = entry.borderBoxSize[0];
    if (box) {
      var size = Math.round(box[instance.options.horizontal ? "inlineSize" : "blockSize"]);
      return size;
    }
  }
  return Math.round(element.getBoundingClientRect()[instance.options.horizontal ? "width" : "height"]);
};
var elementScroll = function elementScroll2(offset, _ref2, instance) {
  var _instance$scrollEleme3, _instance$scrollEleme4;
  var _ref2$adjustments = _ref2.adjustments, adjustments = _ref2$adjustments === void 0 ? 0 : _ref2$adjustments, behavior = _ref2.behavior;
  var toOffset = offset + adjustments;
  (_instance$scrollEleme3 = instance.scrollElement) == null ? void 0 : _instance$scrollEleme3.scrollTo == null ? void 0 : _instance$scrollEleme3.scrollTo((_instance$scrollEleme4 = {}, _instance$scrollEleme4[instance.options.horizontal ? "left" : "top"] = toOffset, _instance$scrollEleme4.behavior = behavior, _instance$scrollEleme4));
};
var Virtualizer = function Virtualizer2(_opts) {
  var _this = this;
  this.unsubs = [];
  this.scrollElement = null;
  this.isScrolling = false;
  this.isScrollingTimeoutId = null;
  this.scrollToIndexTimeoutId = null;
  this.measurementsCache = [];
  this.itemSizeCache = /* @__PURE__ */ new Map();
  this.pendingMeasuredCacheIndexes = [];
  this.scrollDirection = null;
  this.scrollAdjustments = 0;
  this.measureElementCache = /* @__PURE__ */ new Map();
  this.observer = function() {
    var _ro = null;
    var get = function get2() {
      if (_ro) {
        return _ro;
      } else if (typeof ResizeObserver !== "undefined") {
        return _ro = new ResizeObserver(function(entries) {
          entries.forEach(function(entry) {
            _this._measureElement(entry.target, entry);
          });
        });
      } else {
        return null;
      }
    };
    return {
      disconnect: function disconnect() {
        var _get;
        return (_get = get()) == null ? void 0 : _get.disconnect();
      },
      observe: function observe(target) {
        var _get2;
        return (_get2 = get()) == null ? void 0 : _get2.observe(target, {
          box: "border-box"
        });
      },
      unobserve: function unobserve(target) {
        var _get3;
        return (_get3 = get()) == null ? void 0 : _get3.unobserve(target);
      }
    };
  }();
  this.range = {
    startIndex: 0,
    endIndex: 0
  };
  this.setOptions = function(opts) {
    Object.entries(opts).forEach(function(_ref3) {
      var key = _ref3[0], value = _ref3[1];
      if (typeof value === "undefined")
        delete opts[key];
    });
    _this.options = _extends2({
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
      onChange: function onChange() {
      },
      measureElement,
      initialRect: {
        width: 0,
        height: 0
      },
      scrollMargin: 0,
      scrollingDelay: 150,
      indexAttribute: "data-index",
      initialMeasurementsCache: [],
      lanes: 1
    }, opts);
  };
  this.notify = function() {
    _this.options.onChange == null ? void 0 : _this.options.onChange(_this);
  };
  this.cleanup = function() {
    _this.unsubs.filter(Boolean).forEach(function(d3) {
      return d3();
    });
    _this.unsubs = [];
    _this.scrollElement = null;
  };
  this._didMount = function() {
    _this.measureElementCache.forEach(_this.observer.observe);
    return function() {
      _this.observer.disconnect();
      _this.cleanup();
    };
  };
  this._willUpdate = function() {
    var scrollElement = _this.options.getScrollElement();
    if (_this.scrollElement !== scrollElement) {
      _this.cleanup();
      _this.scrollElement = scrollElement;
      _this._scrollToOffset(_this.scrollOffset, {
        adjustments: void 0,
        behavior: void 0
      });
      _this.unsubs.push(_this.options.observeElementRect(_this, function(rect) {
        var prev = _this.scrollRect;
        _this.scrollRect = rect;
        if (_this.options.horizontal ? rect.width !== prev.width : rect.height !== prev.height) {
          _this.maybeNotify();
        }
      }));
      _this.unsubs.push(_this.options.observeElementOffset(_this, function(offset) {
        _this.scrollAdjustments = 0;
        if (_this.scrollOffset === offset) {
          return;
        }
        if (_this.isScrollingTimeoutId !== null) {
          clearTimeout(_this.isScrollingTimeoutId);
          _this.isScrollingTimeoutId = null;
        }
        _this.isScrolling = true;
        _this.scrollDirection = _this.scrollOffset < offset ? "forward" : "backward";
        _this.scrollOffset = offset;
        _this.maybeNotify();
        _this.isScrollingTimeoutId = setTimeout(function() {
          _this.isScrollingTimeoutId = null;
          _this.isScrolling = false;
          _this.scrollDirection = null;
          _this.maybeNotify();
        }, _this.options.scrollingDelay);
      }));
    }
  };
  this.getSize = function() {
    return _this.scrollRect[_this.options.horizontal ? "width" : "height"];
  };
  this.memoOptions = memo2(function() {
    return [_this.options.count, _this.options.paddingStart, _this.options.scrollMargin, _this.options.getItemKey];
  }, function(count2, paddingStart, scrollMargin, getItemKey) {
    _this.pendingMeasuredCacheIndexes = [];
    return {
      count: count2,
      paddingStart,
      scrollMargin,
      getItemKey
    };
  }, {
    key: false
  });
  this.getFurthestMeasurement = function(measurements, index) {
    var furthestMeasurementsFound = /* @__PURE__ */ new Map();
    var furthestMeasurements = /* @__PURE__ */ new Map();
    for (var m3 = index - 1; m3 >= 0; m3--) {
      var measurement = measurements[m3];
      if (furthestMeasurementsFound.has(measurement.lane)) {
        continue;
      }
      var previousFurthestMeasurement = furthestMeasurements.get(measurement.lane);
      if (previousFurthestMeasurement == null || measurement.end > previousFurthestMeasurement.end) {
        furthestMeasurements.set(measurement.lane, measurement);
      } else if (measurement.end < previousFurthestMeasurement.end) {
        furthestMeasurementsFound.set(measurement.lane, true);
      }
      if (furthestMeasurementsFound.size === _this.options.lanes) {
        break;
      }
    }
    return furthestMeasurements.size === _this.options.lanes ? Array.from(furthestMeasurements.values()).sort(function(a3, b3) {
      return a3.end - b3.end;
    })[0] : void 0;
  };
  this.getMeasurements = memo2(function() {
    return [_this.memoOptions(), _this.itemSizeCache];
  }, function(_ref4, itemSizeCache) {
    var count2 = _ref4.count, paddingStart = _ref4.paddingStart, scrollMargin = _ref4.scrollMargin, getItemKey = _ref4.getItemKey;
    var min2 = _this.pendingMeasuredCacheIndexes.length > 0 ? Math.min.apply(Math, _this.pendingMeasuredCacheIndexes) : 0;
    _this.pendingMeasuredCacheIndexes = [];
    var measurements = _this.measurementsCache.slice(0, min2);
    for (var _i2 = min2; _i2 < count2; _i2++) {
      var key = getItemKey(_i2);
      var furthestMeasurement = _this.options.lanes === 1 ? measurements[_i2 - 1] : _this.getFurthestMeasurement(measurements, _i2);
      var start = furthestMeasurement ? furthestMeasurement.end : paddingStart + scrollMargin;
      var measuredSize = itemSizeCache.get(key);
      var size = typeof measuredSize === "number" ? measuredSize : _this.options.estimateSize(_i2);
      var end = start + size;
      var lane = furthestMeasurement ? furthestMeasurement.lane : _i2 % _this.options.lanes;
      measurements[_i2] = {
        index: _i2,
        start,
        size,
        end,
        key,
        lane
      };
    }
    _this.measurementsCache = measurements;
    return measurements;
  }, {
    key: "getMeasurements",
    debug: function debug() {
      return _this.options.debug;
    }
  });
  this.calculateRange = memo2(function() {
    return [_this.getMeasurements(), _this.getSize(), _this.scrollOffset];
  }, function(measurements, outerSize, scrollOffset) {
    return _this.range = calculateRange({
      measurements,
      outerSize,
      scrollOffset
    });
  }, {
    key: "calculateRange",
    debug: function debug() {
      return _this.options.debug;
    }
  });
  this.maybeNotify = memo2(function() {
    var range = _this.calculateRange();
    return [range.startIndex, range.endIndex, _this.isScrolling];
  }, function() {
    _this.notify();
  }, {
    key: "maybeNotify",
    debug: function debug() {
      return _this.options.debug;
    },
    initialDeps: [this.range.startIndex, this.range.endIndex, this.isScrolling]
  });
  this.getIndexes = memo2(function() {
    return [_this.options.rangeExtractor, _this.calculateRange(), _this.options.overscan, _this.options.count];
  }, function(rangeExtractor, range, overscan, count2) {
    return rangeExtractor(_extends2({}, range, {
      overscan,
      count: count2
    }));
  }, {
    key: "getIndexes",
    debug: function debug() {
      return _this.options.debug;
    }
  });
  this.indexFromElement = function(node) {
    var attributeName = _this.options.indexAttribute;
    var indexStr = node.getAttribute(attributeName);
    if (!indexStr) {
      console.warn("Missing attribute name '" + attributeName + "={index}' on measured element.");
      return -1;
    }
    return parseInt(indexStr, 10);
  };
  this._measureElement = function(node, entry) {
    var _this$itemSizeCache$g;
    var index = _this.indexFromElement(node);
    var item = _this.measurementsCache[index];
    if (!item) {
      return;
    }
    var prevNode = _this.measureElementCache.get(item.key);
    if (!node.isConnected) {
      _this.observer.unobserve(node);
      if (node === prevNode) {
        _this.measureElementCache["delete"](item.key);
      }
      return;
    }
    if (prevNode !== node) {
      if (prevNode) {
        _this.observer.unobserve(prevNode);
      }
      _this.observer.observe(node);
      _this.measureElementCache.set(item.key, node);
    }
    var measuredItemSize = _this.options.measureElement(node, entry, _this);
    var itemSize = (_this$itemSizeCache$g = _this.itemSizeCache.get(item.key)) != null ? _this$itemSizeCache$g : item.size;
    var delta = measuredItemSize - itemSize;
    if (delta !== 0) {
      if (item.start < _this.scrollOffset) {
        if (_this.options.debug) {
          console.info("correction", delta);
        }
        _this._scrollToOffset(_this.scrollOffset, {
          adjustments: _this.scrollAdjustments += delta,
          behavior: void 0
        });
      }
      _this.pendingMeasuredCacheIndexes.push(index);
      _this.itemSizeCache = new Map(_this.itemSizeCache.set(item.key, measuredItemSize));
      _this.notify();
    }
  };
  this.measureElement = function(node) {
    if (!node) {
      return;
    }
    _this._measureElement(node, void 0);
  };
  this.getVirtualItems = memo2(function() {
    return [_this.getIndexes(), _this.getMeasurements()];
  }, function(indexes, measurements) {
    var virtualItems = [];
    for (var k4 = 0, len = indexes.length; k4 < len; k4++) {
      var _i3 = indexes[k4];
      var measurement = measurements[_i3];
      virtualItems.push(measurement);
    }
    return virtualItems;
  }, {
    key: "getIndexes",
    debug: function debug() {
      return _this.options.debug;
    }
  });
  this.getVirtualItemForOffset = function(offset) {
    var measurements = _this.getMeasurements();
    return notUndefined(measurements[findNearestBinarySearch(0, measurements.length - 1, function(index) {
      return notUndefined(measurements[index]).start;
    }, offset)]);
  };
  this.getOffsetForAlignment = function(toOffset, align) {
    var size = _this.getSize();
    if (align === "auto") {
      if (toOffset <= _this.scrollOffset) {
        align = "start";
      } else if (toOffset >= _this.scrollOffset + size) {
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
    var scrollSizeProp = _this.options.horizontal ? "scrollWidth" : "scrollHeight";
    var scrollSize = _this.scrollElement ? "document" in _this.scrollElement ? _this.scrollElement.document.documentElement[scrollSizeProp] : _this.scrollElement[scrollSizeProp] : 0;
    var maxOffset = scrollSize - _this.getSize();
    return Math.max(Math.min(maxOffset, toOffset), 0);
  };
  this.getOffsetForIndex = function(index, align) {
    if (align === void 0) {
      align = "auto";
    }
    index = Math.max(0, Math.min(index, _this.options.count - 1));
    var measurement = notUndefined(_this.getMeasurements()[index]);
    if (align === "auto") {
      if (measurement.end >= _this.scrollOffset + _this.getSize() - _this.options.scrollPaddingEnd) {
        align = "end";
      } else if (measurement.start <= _this.scrollOffset + _this.options.scrollPaddingStart) {
        align = "start";
      } else {
        return [_this.scrollOffset, align];
      }
    }
    var toOffset = align === "end" ? measurement.end + _this.options.scrollPaddingEnd : measurement.start - _this.options.scrollPaddingStart;
    return [_this.getOffsetForAlignment(toOffset, align), align];
  };
  this.isDynamicMode = function() {
    return _this.measureElementCache.size > 0;
  };
  this.cancelScrollToIndex = function() {
    if (_this.scrollToIndexTimeoutId !== null) {
      clearTimeout(_this.scrollToIndexTimeoutId);
      _this.scrollToIndexTimeoutId = null;
    }
  };
  this.scrollToOffset = function(toOffset, _temp) {
    var _ref5 = _temp === void 0 ? {} : _temp, _ref5$align = _ref5.align, align = _ref5$align === void 0 ? "start" : _ref5$align, behavior = _ref5.behavior;
    _this.cancelScrollToIndex();
    if (behavior === "smooth" && _this.isDynamicMode()) {
      console.warn("The `smooth` scroll behavior is not fully supported with dynamic size.");
    }
    _this._scrollToOffset(_this.getOffsetForAlignment(toOffset, align), {
      adjustments: void 0,
      behavior
    });
  };
  this.scrollToIndex = function(index, _temp2) {
    var _ref6 = _temp2 === void 0 ? {} : _temp2, _ref6$align = _ref6.align, initialAlign = _ref6$align === void 0 ? "auto" : _ref6$align, behavior = _ref6.behavior;
    index = Math.max(0, Math.min(index, _this.options.count - 1));
    _this.cancelScrollToIndex();
    if (behavior === "smooth" && _this.isDynamicMode()) {
      console.warn("The `smooth` scroll behavior is not fully supported with dynamic size.");
    }
    var _this$getOffsetForInd = _this.getOffsetForIndex(index, initialAlign), toOffset = _this$getOffsetForInd[0], align = _this$getOffsetForInd[1];
    _this._scrollToOffset(toOffset, {
      adjustments: void 0,
      behavior
    });
    if (behavior !== "smooth" && _this.isDynamicMode()) {
      _this.scrollToIndexTimeoutId = setTimeout(function() {
        _this.scrollToIndexTimeoutId = null;
        var elementInDOM = _this.measureElementCache.has(_this.options.getItemKey(index));
        if (elementInDOM) {
          var _this$getOffsetForInd2 = _this.getOffsetForIndex(index, align), _toOffset = _this$getOffsetForInd2[0];
          if (!approxEqual(_toOffset, _this.scrollOffset)) {
            _this.scrollToIndex(index, {
              align,
              behavior
            });
          }
        } else {
          _this.scrollToIndex(index, {
            align,
            behavior
          });
        }
      });
    }
  };
  this.scrollBy = function(delta, _temp3) {
    var _ref7 = _temp3 === void 0 ? {} : _temp3, behavior = _ref7.behavior;
    _this.cancelScrollToIndex();
    if (behavior === "smooth" && _this.isDynamicMode()) {
      console.warn("The `smooth` scroll behavior is not fully supported with dynamic size.");
    }
    _this._scrollToOffset(_this.scrollOffset + delta, {
      adjustments: void 0,
      behavior
    });
  };
  this.getTotalSize = function() {
    var _this$getMeasurements;
    return (((_this$getMeasurements = _this.getMeasurements()[_this.options.count - 1]) == null ? void 0 : _this$getMeasurements.end) || _this.options.paddingStart) - _this.options.scrollMargin + _this.options.paddingEnd;
  };
  this._scrollToOffset = function(offset, _ref8) {
    var adjustments = _ref8.adjustments, behavior = _ref8.behavior;
    _this.options.scrollToFn(offset, {
      behavior,
      adjustments
    }, _this);
  };
  this.measure = function() {
    _this.itemSizeCache = /* @__PURE__ */ new Map();
    _this.notify();
  };
  this.setOptions(_opts);
  this.scrollRect = this.options.initialRect;
  this.scrollOffset = this.options.initialOffset;
  this.measurementsCache = this.options.initialMeasurementsCache;
  this.measurementsCache.forEach(function(item) {
    _this.itemSizeCache.set(item.key, item.size);
  });
  this.maybeNotify();
};
var findNearestBinarySearch = function findNearestBinarySearch2(low, high, getCurrentValue, value) {
  while (low <= high) {
    var middle = (low + high) / 2 | 0;
    var currentValue = getCurrentValue(middle);
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
function calculateRange(_ref9) {
  var measurements = _ref9.measurements, outerSize = _ref9.outerSize, scrollOffset = _ref9.scrollOffset;
  var count2 = measurements.length - 1;
  var getOffset = function getOffset2(index) {
    return measurements[index].start;
  };
  var startIndex = findNearestBinarySearch(0, count2, getOffset, scrollOffset);
  var endIndex = startIndex;
  while (endIndex < count2 && measurements[endIndex].end < scrollOffset + outerSize) {
    endIndex++;
  }
  return {
    startIndex,
    endIndex
  };
}

// node_modules/@tanstack/react-virtual/build/lib/index.mjs
var useIsomorphicLayoutEffect = typeof document !== "undefined" ? y2 : p2;
function useVirtualizerBase(options) {
  var rerender = s2(function() {
    return {};
  }, {})[1];
  var resolvedOptions = _extends({}, options, {
    onChange: function onChange(instance2) {
      rerender();
      options.onChange == null ? void 0 : options.onChange(instance2);
    }
  });
  var _React$useState = h2(function() {
    return new Virtualizer(resolvedOptions);
  }), instance = _React$useState[0];
  instance.setOptions(resolvedOptions);
  p2(function() {
    return instance._didMount();
  }, []);
  useIsomorphicLayoutEffect(function() {
    return instance._willUpdate();
  });
  return instance;
}
function useVirtualizer(options) {
  return useVirtualizerBase(_extends({
    observeElementRect,
    observeElementOffset,
    scrollToFn: elementScroll
  }, options));
}

// node_modules/preact/compat/client.mjs
function createRoot(container) {
  return {
    render(children) {
      G2(children, container);
    },
    unmount() {
      hn(container);
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

// node_modules/use-immer/dist/use-immer.module.js
function i3(f3) {
  var u3 = h2(function() {
    return freeze("function" == typeof f3 ? f3() : f3, true);
  }), i4 = u3[1];
  return [u3[0], T2(function(t3) {
    i4("function" == typeof t3 ? produce(t3) : freeze(t3));
  }, [])];
}

// dataframe/request.ts
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

// dataframe/data-update.tsx
function updateCellsData({
  id,
  patchInfo,
  patches,
  onSuccess,
  onError,
  columns,
  setData,
  setCellEditMapAtLoc
}) {
  const patchesPy = patches.map((patch) => {
    return {
      row_index: patch.rowIndex,
      column_index: patch.columnIndex,
      value: patch.value
      // prev: patch.prev,
    };
  });
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
    const newPatches = newPatchesPy.map((patch) => {
      return {
        rowIndex: patch.row_index,
        columnIndex: patch.column_index,
        value: patch.value
      };
    });
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

// dataframe/cell.tsx
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
var TableBodyCell = ({
  id,
  containerRef,
  cell,
  patchInfo,
  columns,
  rowIndex,
  columnIndex,
  editCellsIsAllowed,
  virtualRows,
  cellEditInfo,
  setData,
  setCellEditMapAtLoc,
  maxRowSize
}) => {
  const initialValue = cell.getValue();
  const cellValue = cellEditInfo?.value ?? initialValue;
  const cellState = cellEditInfo?.state ?? CellStateEnum.Ready;
  const errorTitle = cellEditInfo?.errorTitle;
  const isEditing = cellEditInfo?.isEditing ?? false;
  const editValue = cellEditInfo?.editValue ?? initialValue;
  const inputRef = _2(null);
  const resetEditing = T2(
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
    resetEditing();
  };
  const handleTab = (e3) => {
    if (e3.key !== "Tab")
      return;
    e3.preventDefault();
    const hasShift = e3.shiftKey;
    const newColumnIndex = columnIndex + (hasShift ? -1 : 1);
    if (newColumnIndex < 0 || newColumnIndex >= columns.length) {
      return;
    }
    attemptUpdate();
    setCellEditMapAtLoc(rowIndex, newColumnIndex, (obj_draft) => {
      obj_draft.isEditing = true;
    });
  };
  const handleEnter = (e3) => {
    if (e3.key !== "Enter")
      return;
    e3.preventDefault();
    const hasShift = e3.shiftKey;
    const newRowIndex = rowIndex + (hasShift ? -1 : 1);
    if (newRowIndex < 0 || newRowIndex >= maxRowSize) {
      return;
    }
    attemptUpdate();
    setCellEditMapAtLoc(newRowIndex, columnIndex, (obj_draft) => {
      obj_draft.isEditing = true;
    });
  };
  const onInputKeyDown = (e3) => {
    [handleEsc, handleEnter, handleTab].forEach((fn2) => fn2(e3));
  };
  const attemptUpdate = T2(() => {
    setCellEditMapAtLoc(rowIndex, columnIndex, (obj_draft) => {
      obj_draft.errorTitle = void 0;
    });
    if (`${initialValue}` === `${editValue}`) {
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
      id,
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
    initialValue,
    editValue,
    resetEditing,
    id,
    patchInfo,
    columns,
    setData,
    cellState
  ]);
  p2(() => {
    if (!isEditing)
      return;
    if (!inputRef.current)
      return;
    inputRef.current.focus();
    inputRef.current.select();
  }, [isEditing]);
  p2(() => {
    if (!isEditing)
      return;
    if (!inputRef.current)
      return;
    const onBodyClick = (e3) => {
      if (e3.target === inputRef.current)
        return;
      attemptUpdate();
      resetEditing();
    };
    document.body.addEventListener("click", onBodyClick);
    return () => {
      document.body.removeEventListener("click", onBodyClick);
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
  let onClick = void 0;
  let content = void 0;
  const cellTitle = errorTitle;
  const tableCellClass = CellStateClassEnum[isEditing ? CellStateEnum.Editing : cellState];
  let editContent = null;
  if (cellState === CellStateEnum.EditSaving) {
    content = /* @__PURE__ */ Cn.createElement("em", null, editValue);
  } else {
    if (isEditing) {
      editContent = /* @__PURE__ */ Cn.createElement(
        "textarea",
        {
          value: editValue,
          onChange,
          onFocus,
          onKeyDown: onInputKeyDown,
          ref: inputRef
        }
      );
    } else {
      if (editCellsIsAllowed) {
        onClick = (e3) => {
          setCellEditMapAtLoc(rowIndex, columnIndex, (obj_draft) => {
            obj_draft.isEditing = true;
            obj_draft.editValue = cellValue;
          });
        };
      }
    }
    content = flexRender(cell.column.columnDef.cell, cell.getContext());
  }
  return /* @__PURE__ */ Cn.createElement(
    "td",
    {
      key: cell.id,
      onClick,
      title: cellTitle,
      className: tableCellClass
    },
    editContent,
    content
  );
};

// dataframe/cell-edit-map.tsx
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
  return { cellEditMap, setCellEditMap, setCellEditMapAtLoc };
};
var makeCellEditMapKey = (rowIndex, columnIndex) => {
  return `[${rowIndex}, ${columnIndex}]`;
};
var getCellEditMapObj = (x4, rowIndex, columnIndex) => {
  const key = makeCellEditMapKey(rowIndex, columnIndex);
  return [x4.get(key) ?? {}, key];
};

// dataframe/dom-utils.tsx
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

// dataframe/filter-numeric.tsx
var FilterNumeric = (props) => {
  const [editing, setEditing] = h2(false);
  const { range, from, to, onRangeChange } = props;
  return /* @__PURE__ */ Cn.createElement(
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
  const minInputRef = _2(null);
  const maxInputRef = _2(null);
  return /* @__PURE__ */ Cn.createElement(
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
    /* @__PURE__ */ Cn.createElement(
      "input",
      {
        ref: minInputRef,
        className: `form-control form-control-sm ${minInputRef.current?.checkValidity() ? "" : "is-invalid"}`,
        style: { flex: "1 1 0", width: "0" },
        type: "number",
        placeholder: createPlaceholder(editing, "Min", props.range()[0]),
        defaultValue: min2,
        step: "any",
        onChange: (e3) => {
          const value = coerceToNum(e3.target.value);
          minInputRef.current.classList.toggle(
            "is-invalid",
            !e3.target.checkValidity()
          );
          props.onValueChange([value, max2]);
        }
      }
    ),
    /* @__PURE__ */ Cn.createElement(
      "input",
      {
        ref: maxInputRef,
        className: `form-control form-control-sm ${maxInputRef.current?.checkValidity() ? "" : "is-invalid"}`,
        style: { flex: "1 1 0", width: "0" },
        type: "number",
        placeholder: createPlaceholder(editing, "Max", props.range()[1]),
        defaultValue: max2,
        step: "any",
        onChange: (e3) => {
          const value = coerceToNum(e3.target.value);
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
    return null;
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

// dataframe/filter.tsx
function useFilter(enabled) {
  if (enabled) {
    return {
      getFilteredRowModel: getFilteredRowModel(),
      getFacetedRowModel: getFacetedRowModel(),
      getFacetedUniqueValues: getFacetedUniqueValues(),
      getFacetedMinMaxValues: getFacetedMinMaxValues(),
      filterFns: {
        substring: (row, columnId, value, addMeta) => {
          return row.getValue(columnId).toString().includes(value);
        }
      }
    };
  } else {
    return {};
  }
}
var Filter = ({ header, className, ...props }) => {
  const typeHint = header.column.columnDef.meta?.typeHint;
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
  return /* @__PURE__ */ Cn.createElement(
    "input",
    {
      ...props,
      className: `form-control form-control-sm ${className}`,
      type: "text",
      onChange: (e3) => header.column.setFilterValue(e3.target.value)
    }
  );
};

// dataframe/immutable-set.tsx
var ImmutableSet = class _ImmutableSet {
  _set;
  static _empty = new _ImmutableSet(/* @__PURE__ */ new Set());
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

// dataframe/selection.tsx
var SelectionModes = class _SelectionModes {
  static _NONE = "none";
  static _ROW_SINGLE = "single";
  static _ROW_MULTIPLE = "multiple";
  static _ROW_MULTI_NATIVE = "multi-native";
  static _COL_SINGLE = "single";
  static _col_multiple = "multiple";
  static _RECT_REGION = "region";
  static _RECT_CELL = "cell";
  static _rowEnum = {
    NONE: _SelectionModes._NONE,
    SINGLE: _SelectionModes._ROW_SINGLE,
    MULTIPLE: _SelectionModes._ROW_MULTIPLE,
    // TODO-barret; Make it the new definition of rows!
    MULTI_NATIVE: _SelectionModes._ROW_MULTI_NATIVE
  };
  static _colEnum = {
    NONE: _SelectionModes._NONE,
    SINGLE: _SelectionModes._COL_SINGLE,
    MULTIPLE: _SelectionModes._col_multiple
  };
  static _rectEnum = {
    NONE: _SelectionModes._NONE,
    REGION: _SelectionModes._RECT_REGION,
    CELL: _SelectionModes._RECT_CELL
  };
  static _types;
  row;
  col;
  rect;
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
  canSelect() {
    return !this.isNone();
  }
  isNone() {
    return this.row === _SelectionModes._rowEnum.NONE && this.col === _SelectionModes._colEnum.NONE && this.rect === _SelectionModes._rectEnum.NONE;
  }
};
function initSelectionModes(selectionModesOption) {
  if (!selectionModesOption) {
    selectionModesOption = { row: "multi-native", col: "none", rect: "none" };
  }
  return new SelectionModes({
    row: selectionModesOption.row,
    col: selectionModesOption.col,
    rect: selectionModesOption.rect
  });
}
function useRowSelection({
  selectionModes,
  keyAccessor,
  focusOffset,
  between
}) {
  const [selectedKeys, setSelectedKeys] = h2(
    ImmutableSet.empty()
  );
  const [anchor, setAnchor] = h2(null);
  const onMouseDown = (event) => {
    if (selectionModes.row === SelectionModes._rowEnum.NONE)
      return;
    const el = event.currentTarget;
    const key = keyAccessor(el);
    const result = performRowMouseDownAction({
      selectionModes,
      between,
      selectedKeys,
      event,
      key,
      anchor
    });
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
    if (selectionModes.row === SelectionModes._rowEnum.NONE)
      return;
    const el = event.currentTarget;
    const key = keyAccessor(el);
    const selected = selectedKeys.has(key);
    if (selectionModes.row === SelectionModes._rowEnum.SINGLE) {
      if (event.key === " " || event.key === "Enter") {
        if (selectedKeys.has(key)) {
          setSelectedKeys(ImmutableSet.empty());
        } else {
          setSelectedKeys(ImmutableSet.just(key));
        }
        event.preventDefault();
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
        setSelectedKeys(selectedKeys.toggle(key));
        event.preventDefault();
      } else if (event.key === "ArrowUp" || event.key === "ArrowDown") {
        if (focusOffset(key, event.key === "ArrowUp" ? -1 : 1)) {
          event.preventDefault();
        }
      }
    } else {
      throw new Error(
        "Unimplemented row selection key action: " + selectionModes.row
      );
    }
  };
  return {
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
    setMultiple(key_arr) {
      setSelectedKeys(ImmutableSet.just(...key_arr));
    },
    clear() {
      setSelectedKeys(selectedKeys.clear());
    },
    keys() {
      return selectedKeys;
    },
    itemHandlers() {
      return { onMouseDown, onKeyDown };
    }
  };
}
var isMac = /^mac/i.test(
  window.navigator.userAgentData?.platform ?? window.navigator.platform
);
function performRowMouseDownAction({
  selectionModes,
  between,
  selectedKeys,
  event,
  key,
  anchor
}) {
  const { shiftKey, altKey } = event;
  const ctrlKey = isMac ? event.metaKey : event.ctrlKey;
  const metaKey = isMac ? event.ctrlKey : event.metaKey;
  if (metaKey || altKey) {
    return null;
  }
  if (selectionModes.row === SelectionModes._rowEnum.NONE)
    return null;
  if (selectionModes.row === SelectionModes._rowEnum.SINGLE) {
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
    return { selection: selectedKeys.toggle(key), anchor: true };
  } else if (selectionModes.row === SelectionModes._rowEnum.MULTI_NATIVE) {
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
    throw new Error(
      "Unimplemented row selection click action: " + selectionModes.row
    );
  }
  return null;
}

// dataframe/sort-arrows.tsx
var sortCommonProps = {
  className: "sort-arrow",
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
var sortArrowUp = /* @__PURE__ */ Cn.createElement("svg", { xmlns: "http://www.w3.org/2000/svg", ...sortCommonProps }, /* @__PURE__ */ Cn.createElement(
  "path",
  {
    d: "M -1 0.5 L 0 -0.5 L 1 0.5",
    ...sortPathCommonProps,
    strokeLinecap: "round"
  }
));
var sortArrowDown = /* @__PURE__ */ Cn.createElement("svg", { xmlns: "http://www.w3.org/2000/svg", ...sortCommonProps }, /* @__PURE__ */ Cn.createElement(
  "path",
  {
    d: "M -1 -0.5 L 0 0.5 L 1 -0.5",
    ...sortPathCommonProps,
    strokeLinecap: "round"
  }
));
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

// dataframe/styles.scss
var styles_default = `
>>>>>>> Stashed changes
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
  --shiny-datagrid-table-cell-edit-success-border-color: color-mix(in srgb, var(--bs-success) 20%, transparent);
  --shiny-datagrid-table-cell-edit-success-border-style: var(--shiny-datagrid-grid-gridlines-style);
  --shiny-datagrid-table-cell-edit-success-bgcolor: color-mix(in srgb, var(--bs-success) 10%, transparent);
  --shiny-datagrid-table-cell-edit-failure-border-color: color-mix(in srgb, var(--bs-danger) 40%, transparent);
  --shiny-datagrid-table-cell-edit-failure-border-style: var(--shiny-datagrid-grid-gridlines-style);
  --shiny-datagrid-table-cell-edit-failure-bgcolor: color-mix(in srgb, var(--bs-danger) 10%, transparent);
  --shiny-datagrid-table-cell-edit-saving-color: var(--bs-gray-500);
  --shiny-datagrid-table-cell-edit-saving-font-style: italic;
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
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border: none;
  background-color: inherit;
  resize: none;
}

shiny-data-frame .shiny-data-grid > table > tbody > tr > td.cell-edit-saving {
  color: var(--shiny-datagrid-table-cell-edit-saving-color);
  font-style: var(--shiny-datagrid-table-cell-edit-saving-font-style);
}
shiny-data-frame .shiny-data-grid > table > tbody > tr > td.cell-edit-failure {
  outline: 2px var(--shiny-datagrid-table-cell-edit-failure-border-style) var(--shiny-datagrid-table-cell-edit-failure-border-color);
  background-color: var(--shiny-datagrid-table-cell-edit-failure-bgcolor);
<<<<<<< Updated upstream
}`;function oo(e,n,t){let[r,o]=A(0),i=b.useCallback(u=>{o(-1),u.target===u.currentTarget&&Kr(e,n(),t)?.focus()},[e,n,t]),l=b.useCallback(u=>{o(0)},[]);return{containerTabIndex:r,containerHandlers:{onFocus:i,onBlur:l}}}function io(e,n,t,r,o){return ne(()=>{let i=e??!0;if(!i)return null;let l=typeof i=="string"?i:"Viewing rows {start} through {end} of {total}";if(!n||t.length===0||!r)return null;let u=n.scrollTop+r.clientHeight,a=n.scrollTop+n.clientHeight,[d,s]=Zi(u,a,t,(p,m)=>p.start+p.size/2);if(d===null||s===null)return null;let g=t[d],f=t[s];if(g.index===0&&f.index===o-1)return null;let c=el(l,g.index+1,f.index+1,o);return b.createElement("div",{className:"shiny-data-grid-summary"},c)},[e,n,t,r,o])}function Zi(e,n,t,r){let o=null,i=null;for(let l=0;l<t.length;l++){let u=t[l];if(o===null)r(u,!0)>=e&&(o=l,i=l);else if(r(u,!1)<=n)i=l;else break}return[o,i]}function el(e,n,t,r){return e.replace(/\{(start|end|total)\}/g,(o,i)=>i==="start"?n+"":i==="end"?t+"":i==="total"?r+"":o)}var tl=({id:e,gridInfo:{payload:n,patchInfo:t,selectionModes:r},bgcolor:o})=>{let{columns:i,typeHints:l,data:u,options:a}=n,{width:d,height:s,fill:g,filters:f}=a,c=q(null),p=q(null),m=q(null),{cellEditMap:_,setCellEditMapAtLoc:v}=Gr(),w=a.editable===!0,E=ne(()=>i.map((M,x)=>{let R=l?.[x];return{accessorFn:(T,he)=>T[x],filterFn:R?.type==="numeric"?"inNumberRange":"includesString",header:M,meta:{colIndex:x,typeHint:R},cell:({getValue:T})=>T()}}),[i,l]),V=ne(()=>u,[u]),[D,G]=at(u),re=Xr(f),I={data:D,columns:E,getCoreRowModel:cr(),getSortedRowModel:hr(),...re},N=vr(I),oe=Rr({count:N.getFilteredRowModel().rows.length,getScrollElement:()=>c.current,estimateSize:()=>31,paddingStart:p.current?.clientHeight??0,scrollingDelay:10});te(()=>{oe.scrollToOffset(0)},[n,oe]);let Pe=oe.getTotalSize(),Y=oe.getVirtualItems(),ke=(Y.length>0&&Y?.[0]?.start||0)-(p.current?.clientHeight??0),Le=Y.length>0?Pe-(Y?.[Y.length-1]?.end||0):0,He=io(a.summary,c?.current,Y,p.current,oe.options.count),S=a.style??"grid",P=S==="grid"?"shiny-data-grid-grid":"shiny-data-grid-table",B=S==="table"?"table table-sm":null,U=Qr(r),xe=!U.is_none(),ut=U.row!==Q._rowEnum.NONE,K=Zr(U,M=>M.dataset.key,(M,x)=>{let R=N.getSortedRowModel(),T=R.rows.findIndex(ze=>ze.id===M);if(T<0||(T+=x,T<0||T>=R.rows.length))return null;let he=R.rows[T].id;return oe.scrollToIndex(T),setTimeout(()=>{c.current?.querySelector(`[data-key='${he}']`)?.focus()},0),he},(M,x)=>nl(N.getSortedRowModel(),M,x));L(()=>{let M=R=>{let T=R.detail.cellSelection;if(T.type==="none"){K.clear();return}else if(T.type==="row"){K.setMultiple(T.rows.map(String));return}else console.error("Unhandled cell selection update:",T)};if(!e)return;let x=document.getElementById(e);if(x)return x.addEventListener("updateCellSelection",M),()=>{x.removeEventListener("updateCellSelection",M)}},[e,K,u]),L(()=>{if(!e)return;let M=`${e}_cell_selection`,x=null;U.is_none()?x=null:U.row!==Q._rowEnum.NONE?x={type:"row",rows:K.keys().toList().map(T=>parseInt(T)).sort()}:console.error("Unhandled row selection mode:",U),Shiny.setInputValue(M,x)},[e,U,[...K.keys()]]),w&&xe&&console.error("Should not have editable and row selection at the same time");let ao=b.useCallback(()=>m.current.querySelectorAll("[tabindex='-1']"),[m.current]),Jt=oo(c.current,ao,{top:p.current?.clientHeight??0});L(()=>()=>{N.resetSorting(),K.clear()},[n]);let uo=N.getHeaderGroups().length,Qt=u.length>0?"scrolling":"",Zt=c.current?.scrollHeight,en=c.current?.clientHeight;Zt&&en&&Zt<=en&&(Qt="");let co=M=>x=>{(x.key===" "||x.key==="Enter")&&M.toggleSorting(void 0,x.shiftKey)},fo=rl(oe),tn=`shiny-data-grid ${P} ${Qt}`;return g&&(tn+=" html-fill-item"),b.createElement(b.Fragment,null,b.createElement("div",{className:tn,ref:c,style:{width:d,height:s,overflow:"auto"}},b.createElement("table",{className:B+(f?" filtering":""),"aria-rowcount":D.length,"aria-multiselectable":ut,style:{width:d===null||d==="auto"?void 0:"100%"}},b.createElement("thead",{ref:p,style:{backgroundColor:o}},N.getHeaderGroups().map((M,x)=>b.createElement("tr",{key:M.id,"aria-rowindex":x+1},M.headers.map(R=>b.createElement("th",{key:R.id,colSpan:R.colSpan,style:{width:R.getSize()},scope:"col",tabIndex:0,onClick:R.column.getToggleSortingHandler(),onKeyDown:co(R.column)},R.isPlaceholder?null:b.createElement("div",{style:{cursor:R.column.getCanSort()?"pointer":void 0,userSelect:R.column.getCanSort()?"none":void 0}},Ze(R.column.columnDef.header,R.getContext()),b.createElement(no,{direction:R.column.getIsSorted()})))))),f&&b.createElement("tr",{className:"filters"},N.getFlatHeaders().map(M=>b.createElement("th",{key:`filter-${M.id}`},b.createElement(Yr,{header:M}))))),b.createElement("tbody",{ref:m,tabIndex:Jt.containerTabIndex,...Jt.containerHandlers},ke>0&&b.createElement("tr",{style:{height:`${ke}px`}}),Y.map(M=>{let x=N.getRowModel().rows[M.index];return x&&b.createElement("tr",{key:M.key,"data-index":M.index,"aria-rowindex":M.index+uo,"data-key":x.id,ref:fo,"aria-selected":K.has(x.id),tabIndex:-1,...K.itemHandlers()},x.getVisibleCells().map(R=>{let T=R.row.index,he=R.column.columnDef.meta.colIndex,[ze,ol]=Ur(_,T,he);return b.createElement(zr,{key:R.id,rowId:R.row.id,containerRef:c,cell:R,patchInfo:t,editCellsIsAllowed:w,columns:i,rowIndex:T,columnIndex:he,getSortedRowModel:N.getSortedRowModel,cellEditInfo:ze,setData:G,setCellEditMapAtLoc:v})}))}),Le>0&&b.createElement("tr",{style:{height:`${Le}px`}})))),He)};function nl(e,n,t){let r=e.rows.findIndex(l=>l.id===n),o=e.rows.findIndex(l=>l.id===t);if(r<0||o<0)return[];r>o&&([r,o]=[o,r]);let i=[];for(let l=r;l<=o;l++)i.push(e.rows[l].id);return i}function rl(e){let n=q([]),t=le(r=>{r&&(r.isConnected?e.measureElement(r):n.current.push(r))},[e]);return te(()=>{n.current.length>0&&n.current.splice(0).forEach(e.measureElement)}),t}var Xt=class extends Shiny.OutputBinding{find(n){return $(n).find("shiny-data-frame")}renderValue(n,t){n.renderValue(t)}renderError(n,t){n.classList.add("shiny-output-error"),n.renderError(t)}clearError(n){n.classList.remove("shiny-output-error"),n.clearError()}};Shiny.outputBindings.register(new Xt,"shinyDataFrame");function lo(e){if(!e)return;let n=Wt(e,"background-color");if(!n)return n;let t=n.match(/^rgba\(\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)\s*\)$/);if(n==="transparent"||t&&parseFloat(t[4])===0){let r=Wt(e,"background-image");return r&&r!=="none"?void 0:lo(e.parentElement)}return n}var so=document.createElement("template");so.innerHTML=`<style>${ro}</style>`;var Yt=class extends HTMLElement{reactRoot;errorRoot;connectedCallback(){let[n]=[this];n.appendChild(so.content.cloneNode(!0)),this.errorRoot=document.createElement("span"),n.appendChild(this.errorRoot);let t=document.createElement("div");t.classList.add("html-fill-container","html-fill-item"),n.appendChild(t),this.reactRoot=xr(t);let r=this.querySelector("script.data");if(r){let o=JSON.parse(r.innerText);this.renderValue(o)}}renderValue(n){if(this.clearError(),!n){this.reactRoot.render(null);return}this.reactRoot.render(b.createElement(Rt,null,b.createElement(tl,{id:this.id,gridInfo:n,bgcolor:lo(this)})))}renderError(n){this.reactRoot.render(null),this.errorRoot.innerText=n.message}clearError(){this.reactRoot.render(null),this.errorRoot.innerText=""}};customElements.define("shiny-data-frame",Yt);$(function(){Shiny.addCustomMessageHandler("shinyDataFrameMessage",function(e){let n=new CustomEvent(e.handler,{detail:e.obj});document.getElementById(e.id)?.dispatchEvent(n)})});export{Yt as ShinyDataFrameOutput};
=======
}`;

// dataframe/tabindex-group.ts
function useTabindexGroup(container, focusableItems, extraPadding) {
  const [tabIndex, setTabIndex] = h2(0);
  const onFocus = Cn.useCallback(
    (event) => {
      setTabIndex(-1);
      if (event.target !== event.currentTarget) {
        return;
      }
      findFirstItemInView(container, focusableItems(), extraPadding)?.focus();
    },
    [container, focusableItems, extraPadding]
  );
  const onBlur = Cn.useCallback(
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

// dataframe/table-summary.tsx
function useSummary(summaryTemplate, scrollContainer, virtualRows, thead, nrows) {
  return F2(() => {
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
    if (firstRow.index === 0 && lastRow.index === nrows - 1) {
      return null;
    }
    const summaryMessage = formatSummary(
      template,
      firstRow.index + 1,
      lastRow.index + 1,
      nrows
    );
    return /* @__PURE__ */ Cn.createElement("div", { className: "shiny-data-grid-summary" }, summaryMessage);
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

// dataframe/index.tsx
var ShinyDataGrid = ({
  id,
  gridInfo: { payload, patchInfo, selectionModes: selectionModesProp },
  bgcolor
}) => {
  const {
    columns,
    typeHints,
    data: rowData,
    options: payload_options
  } = payload;
  const { width, height, fill, filters: withFilters } = payload_options;
  const containerRef = _2(null);
  const theadRef = _2(null);
  const tbodyRef = _2(null);
  const { cellEditMap, setCellEditMapAtLoc } = useCellEditMap();
  const editCellsIsAllowed = payload_options["editable"] === true;
  const coldefs = F2(
    () => columns.map((colname, i4) => {
      const typeHint = typeHints?.[i4];
      return {
        accessorFn: (row, index) => {
          return row[i4];
        },
        // TODO: delegate this decision to something in filter.tsx
        filterFn: typeHint?.type === "numeric" ? "inNumberRange" : "includesString",
        header: colname,
        meta: {
          colIndex: i4,
          typeHint
        },
        cell: ({ getValue }) => {
          return getValue();
        }
      };
    }),
    [columns, typeHints]
  );
  const dataOriginal = F2(() => rowData, [rowData]);
  const [dataState, setData] = i3(rowData);
  const filterOpts = useFilter(withFilters);
  const options = {
    data: dataState,
    columns: coldefs,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    ...filterOpts
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
    paddingStart: theadRef.current?.clientHeight ?? 0,
    // In response to https://github.com/posit-dev/py-shiny/pull/538/files#r1228352446
    // (the default scrollingDelay is 150)
    scrollingDelay: 10
  });
  y2(() => {
    rowVirtualizer.scrollToOffset(0);
  }, [payload, rowVirtualizer]);
  const totalSize = rowVirtualizer.getTotalSize();
  const virtualRows = rowVirtualizer.getVirtualItems();
  const paddingTop = (virtualRows.length > 0 ? virtualRows?.[0]?.start || 0 : 0) - (theadRef.current?.clientHeight ?? 0);
  const paddingBottom = virtualRows.length > 0 ? totalSize - (virtualRows?.[virtualRows.length - 1]?.end || 0) : 0;
  const summary = useSummary(
    payload_options["summary"],
    containerRef?.current,
    virtualRows,
    theadRef.current,
    rowVirtualizer.options.count
  );
  const tableStyle = payload_options["style"] ?? "grid";
  const containerClass = tableStyle === "grid" ? "shiny-data-grid-grid" : "shiny-data-grid-table";
  const tableClass = tableStyle === "table" ? "table table-sm" : null;
  const selectionModes = initSelectionModes(selectionModesProp);
  const canMultiRowSelect = selectionModes.row === SelectionModes._rowEnum.MULTIPLE;
  const rectSelection = useRectSelection({
    selectionModes,
    keysAccessor: (el) => {
      const rowKey = el.parentElement?.dataset.key;
      const colKey = el.dataset.key;
      return [rowKey, colKey];
    },
    focusOffset: (keys, offset) => {
      const rowModel = table.getSortedRowModel();
      let index = rowModel.rows.findIndex((row) => row.id === keys[0]);
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
    }
  });
  const rowSelection = useRowSelection({
    selectionModes,
    // TODO-barret; Use keyAccessor in Cell Traversal to get the cell key
    keyAccessor: (el) => el.dataset.key,
    // TODO-barret; Use focusOffset in Cell Traversal to get the next cell key, not position!
    focusOffset: (key, offset) => {
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
    between: (fromKey, toKey) => findKeysBetween(table.getSortedRowModel(), fromKey, toKey)
  });
  p2(() => {
    const handleMessage = (event) => {
      const cellSelection = event.detail.cellSelection;
      if (cellSelection.type === "none") {
        rowSelection.clear();
        return;
      } else if (cellSelection.type === "row") {
        rowSelection.setMultiple(cellSelection.rows.map(String));
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
      handleMessage
    );
    return () => {
      element.removeEventListener(
        "updateCellSelection",
        handleMessage
      );
    };
  }, [id, rowSelection, rowData]);
  p2(() => {
    if (!id)
      return;
    const shinyId = `${id}_cell_selection`;
    let shinyValue = null;
    if (selectionModes.isNone()) {
      shinyValue = null;
    } else if (selectionModes.row !== SelectionModes._rowEnum.NONE) {
      const rowSelectionKeys = rowSelection.keys().toList();
      shinyValue = {
        type: "row",
        rows: rowSelectionKeys.map((key) => parseInt(key)).sort()
      };
    } else if (selectionModes.rect !== SelectionModes._rectEnum.NONE) {
      if (selectionModes.rect === SelectionModes._rectEnum.REGION) {
        throw new Error("Region selection not yet supported");
      }
      shinyValue = {
        type: "rect",
        rows: [],
        cols: []
      };
    } else {
      console.error("Unhandled row selection mode:", selectionModes);
    }
    Shiny.setInputValue(shinyId, shinyValue);
  }, [id, selectionModes, [...rowSelection.keys()]]);
  if (editCellsIsAllowed && selectionModes.canSelect()) {
    console.error(
      "Should not have editable and row selection at the same time"
    );
  }
  const tbodyTabItems = Cn.useCallback(
    () => tbodyRef.current.querySelectorAll("[tabindex='-1']"),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [tbodyRef.current]
  );
  const tbodyTabGroup = useTabindexGroup(containerRef.current, tbodyTabItems, {
    top: theadRef.current?.clientHeight ?? 0
  });
  p2(() => {
    return () => {
      table.resetSorting();
      rowSelection.clear();
    };
  }, [payload]);
  const headerRowCount = table.getHeaderGroups().length;
  let scrollingClass = rowData.length > 0 ? "scrolling" : "";
  const scrollHeight = containerRef.current?.scrollHeight;
  const clientHeight = containerRef.current?.clientHeight;
  if (scrollHeight && clientHeight && scrollHeight <= clientHeight) {
    scrollingClass = "";
  }
  const makeHeaderKeyDown = (column) => (event) => {
    if (event.key === " " || event.key === "Enter") {
      column.toggleSorting(void 0, event.shiftKey);
    }
  };
  const measureEl = useVirtualizerMeasureWorkaround(rowVirtualizer);
  let className = `shiny-data-grid ${containerClass} ${scrollingClass}`;
  if (fill) {
    className += " html-fill-item";
  }
  const maxRowSize = table.getSortedRowModel().rows.length;
  return /* @__PURE__ */ Cn.createElement(Cn.Fragment, null, /* @__PURE__ */ Cn.createElement(
    "div",
    {
      className,
      ref: containerRef,
      style: { width, height, overflow: "auto" }
    },
    /* @__PURE__ */ Cn.createElement(
      "table",
      {
        className: tableClass + (withFilters ? " filtering" : ""),
        "aria-rowcount": dataState.length,
        "aria-multiselectable": canMultiRowSelect,
        style: {
          width: width === null || width === "auto" ? void 0 : "100%"
        }
      },
      /* @__PURE__ */ Cn.createElement("thead", { ref: theadRef, style: { backgroundColor: bgcolor } }, table.getHeaderGroups().map((headerGroup, i4) => /* @__PURE__ */ Cn.createElement("tr", { key: headerGroup.id, "aria-rowindex": i4 + 1 }, headerGroup.headers.map((header) => {
        return /* @__PURE__ */ Cn.createElement(
          "th",
          {
            key: header.id,
            colSpan: header.colSpan,
            style: { width: header.getSize() },
            scope: "col",
            tabIndex: 0,
            onClick: header.column.getToggleSortingHandler(),
            onKeyDown: makeHeaderKeyDown(header.column)
          },
          header.isPlaceholder ? null : /* @__PURE__ */ Cn.createElement(
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
            /* @__PURE__ */ Cn.createElement(SortArrow, { direction: header.column.getIsSorted() })
          )
        );
      }))), withFilters && /* @__PURE__ */ Cn.createElement("tr", { className: "filters" }, table.getFlatHeaders().map((header) => {
        return /* @__PURE__ */ Cn.createElement("th", { key: `filter-${header.id}` }, /* @__PURE__ */ Cn.createElement(Filter, { header }));
      }))),
      /* @__PURE__ */ Cn.createElement(
        "tbody",
        {
          ref: tbodyRef,
          tabIndex: tbodyTabGroup.containerTabIndex,
          ...tbodyTabGroup.containerHandlers
        },
        paddingTop > 0 && /* @__PURE__ */ Cn.createElement("tr", { style: { height: `${paddingTop}px` } }),
        virtualRows.map((virtualRow) => {
          const row = table.getRowModel().rows[virtualRow.index];
          return row && /* @__PURE__ */ Cn.createElement(
            "tr",
            {
              key: virtualRow.key,
              "data-index": virtualRow.index,
              "aria-rowindex": virtualRow.index + headerRowCount,
              "data-key": row.id,
              ref: measureEl,
              "aria-selected": rowSelection.has(row.id),
              tabIndex: -1,
              ...rowSelection.itemHandlers()
            },
            row.getVisibleCells().map((cell) => {
              const rowIndex = cell.row.index;
              const columnIndex = cell.column.columnDef.meta.colIndex;
              const [cellEditInfo, _key] = getCellEditMapObj(
                cellEditMap,
                rowIndex,
                columnIndex
              );
              return /* @__PURE__ */ Cn.createElement(
                TableBodyCell,
                {
                  id,
                  containerRef,
                  key: cell.id,
                  cell,
                  patchInfo,
                  editCellsIsAllowed,
                  columns,
                  rowIndex,
                  columnIndex,
                  virtualRows,
                  cellEditInfo,
                  maxRowSize,
                  setData,
                  setCellEditMapAtLoc
                }
              );
            })
          );
        }),
        paddingBottom > 0 && /* @__PURE__ */ Cn.createElement("tr", { style: { height: `${paddingBottom}px` } })
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
  const measureTodoQueue = _2([]);
  const measureElementWithRetry = T2(
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
  y2(() => {
    if (measureTodoQueue.current.length > 0) {
      const todo = measureTodoQueue.current.splice(0);
      todo.forEach(rowVirtualizer.measureElement);
    }
  });
  return measureElementWithRetry;
}
var ShinyDataFrameOutputBinding = class extends Shiny.OutputBinding {
  find(scope) {
    return $(scope).find("shiny-data-frame");
  }
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
Shiny.outputBindings.register(
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
  reactRoot;
  errorRoot;
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
      /* @__PURE__ */ Cn.createElement(mn, null, /* @__PURE__ */ Cn.createElement(
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
$(function() {
  Shiny.addCustomMessageHandler("shinyDataFrameMessage", function(message) {
    const evt = new CustomEvent(message.handler, {
      detail: message.obj
    });
    const el = document.getElementById(message.id);
    el?.dispatchEvent(evt);
  });
});
export {
  ShinyDataFrameOutput
};
>>>>>>> Stashed changes
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

@tanstack/react-virtual/build/lib/_virtual/_rollupPluginBabelHelpers.mjs:
  (**
   * react-virtual
   *
   * Copyright (c) TanStack
   *
   * This source code is licensed under the MIT license found in the
   * LICENSE.md file in the root directory of this source tree.
   *
   * @license MIT
   *)

@tanstack/virtual-core/build/lib/_virtual/_rollupPluginBabelHelpers.mjs:
  (**
   * virtual-core
   *
   * Copyright (c) TanStack
   *
   * This source code is licensed under the MIT license found in the
   * LICENSE.md file in the root directory of this source tree.
   *
   * @license MIT
   *)

@tanstack/virtual-core/build/lib/utils.mjs:
  (**
   * virtual-core
   *
   * Copyright (c) TanStack
   *
   * This source code is licensed under the MIT license found in the
   * LICENSE.md file in the root directory of this source tree.
   *
   * @license MIT
   *)

@tanstack/virtual-core/build/lib/index.mjs:
  (**
   * virtual-core
   *
   * Copyright (c) TanStack
   *
   * This source code is licensed under the MIT license found in the
   * LICENSE.md file in the root directory of this source tree.
   *
   * @license MIT
   *)

@tanstack/react-virtual/build/lib/index.mjs:
  (**
   * react-virtual
   *
   * Copyright (c) TanStack
   *
   * This source code is licensed under the MIT license found in the
   * LICENSE.md file in the root directory of this source tree.
   *
   * @license MIT
   *)
*/
//# sourceMappingURL=dataframe.js.map
