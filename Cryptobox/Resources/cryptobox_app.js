/*
 AngularJS v1.0.6
 (c) 2010-2012 Google, Inc. http://angularjs.org
 License: MIT
*/
(function(N,Y,q){'use strict';function n(b,a,c){var d;if(b)if(H(b))for(d in b)d!="prototype"&&d!="length"&&d!="name"&&b.hasOwnProperty(d)&&a.call(c,b[d],d);else if(b.forEach&&b.forEach!==n)b.forEach(a,c);else if(!b||typeof b.length!=="number"?0:typeof b.hasOwnProperty!="function"&&typeof b.constructor!="function"||b instanceof K||ca&&b instanceof ca||xa.call(b)!=="[object Object]"||typeof b.callee==="function")for(d=0;d<b.length;d++)a.call(c,b[d],d);else for(d in b)b.hasOwnProperty(d)&&a.call(c,b[d],
d);return b}function nb(b){var a=[],c;for(c in b)b.hasOwnProperty(c)&&a.push(c);return a.sort()}function fc(b,a,c){for(var d=nb(b),e=0;e<d.length;e++)a.call(c,b[d[e]],d[e]);return d}function ob(b){return function(a,c){b(c,a)}}function ya(){for(var b=aa.length,a;b;){b--;a=aa[b].charCodeAt(0);if(a==57)return aa[b]="A",aa.join("");if(a==90)aa[b]="0";else return aa[b]=String.fromCharCode(a+1),aa.join("")}aa.unshift("0");return aa.join("")}function v(b){n(arguments,function(a){a!==b&&n(a,function(a,d){b[d]=
a})});return b}function G(b){return parseInt(b,10)}function za(b,a){return v(new (v(function(){},{prototype:b})),a)}function w(){}function na(b){return b}function I(b){return function(){return b}}function x(b){return typeof b=="undefined"}function y(b){return typeof b!="undefined"}function L(b){return b!=null&&typeof b=="object"}function B(b){return typeof b=="string"}function Ra(b){return typeof b=="number"}function oa(b){return xa.apply(b)=="[object Date]"}function E(b){return xa.apply(b)=="[object Array]"}
function H(b){return typeof b=="function"}function pa(b){return b&&b.document&&b.location&&b.alert&&b.setInterval}function O(b){return B(b)?b.replace(/^\s*/,"").replace(/\s*$/,""):b}function gc(b){return b&&(b.nodeName||b.bind&&b.find)}function Sa(b,a,c){var d=[];n(b,function(b,g,h){d.push(a.call(c,b,g,h))});return d}function Aa(b,a){if(b.indexOf)return b.indexOf(a);for(var c=0;c<b.length;c++)if(a===b[c])return c;return-1}function Ta(b,a){var c=Aa(b,a);c>=0&&b.splice(c,1);return a}function V(b,a){if(pa(b)||
b&&b.$evalAsync&&b.$watch)throw Error("Can't copy Window or Scope");if(a){if(b===a)throw Error("Can't copy equivalent objects or arrays");if(E(b))for(var c=a.length=0;c<b.length;c++)a.push(V(b[c]));else for(c in n(a,function(b,c){delete a[c]}),b)a[c]=V(b[c])}else(a=b)&&(E(b)?a=V(b,[]):oa(b)?a=new Date(b.getTime()):L(b)&&(a=V(b,{})));return a}function hc(b,a){var a=a||{},c;for(c in b)b.hasOwnProperty(c)&&c.substr(0,2)!=="$$"&&(a[c]=b[c]);return a}function ga(b,a){if(b===a)return!0;if(b===null||a===
null)return!1;if(b!==b&&a!==a)return!0;var c=typeof b,d;if(c==typeof a&&c=="object")if(E(b)){if((c=b.length)==a.length){for(d=0;d<c;d++)if(!ga(b[d],a[d]))return!1;return!0}}else if(oa(b))return oa(a)&&b.getTime()==a.getTime();else{if(b&&b.$evalAsync&&b.$watch||a&&a.$evalAsync&&a.$watch||pa(b)||pa(a))return!1;c={};for(d in b)if(!(d.charAt(0)==="$"||H(b[d]))){if(!ga(b[d],a[d]))return!1;c[d]=!0}for(d in a)if(!c[d]&&d.charAt(0)!=="$"&&a[d]!==q&&!H(a[d]))return!1;return!0}return!1}function Ua(b,a){var c=
arguments.length>2?ha.call(arguments,2):[];return H(a)&&!(a instanceof RegExp)?c.length?function(){return arguments.length?a.apply(b,c.concat(ha.call(arguments,0))):a.apply(b,c)}:function(){return arguments.length?a.apply(b,arguments):a.call(b)}:a}function ic(b,a){var c=a;/^\$+/.test(b)?c=q:pa(a)?c="$WINDOW":a&&Y===a?c="$DOCUMENT":a&&a.$evalAsync&&a.$watch&&(c="$SCOPE");return c}function da(b,a){return JSON.stringify(b,ic,a?"  ":null)}function pb(b){return B(b)?JSON.parse(b):b}function Va(b){b&&b.length!==
0?(b=A(""+b),b=!(b=="f"||b=="0"||b=="false"||b=="no"||b=="n"||b=="[]")):b=!1;return b}function qa(b){b=u(b).clone();try{b.html("")}catch(a){}var c=u("<div>").append(b).html();try{return b[0].nodeType===3?A(c):c.match(/^(<[^>]+>)/)[1].replace(/^<([\w\-]+)/,function(a,b){return"<"+A(b)})}catch(d){return A(c)}}function Wa(b){var a={},c,d;n((b||"").split("&"),function(b){b&&(c=b.split("="),d=decodeURIComponent(c[0]),a[d]=y(c[1])?decodeURIComponent(c[1]):!0)});return a}function qb(b){var a=[];n(b,function(b,
d){a.push(Xa(d,!0)+(b===!0?"":"="+Xa(b,!0)))});return a.length?a.join("&"):""}function Ya(b){return Xa(b,!0).replace(/%26/gi,"&").replace(/%3D/gi,"=").replace(/%2B/gi,"+")}function Xa(b,a){return encodeURIComponent(b).replace(/%40/gi,"@").replace(/%3A/gi,":").replace(/%24/g,"$").replace(/%2C/gi,",").replace(/%20/g,a?"%20":"+")}function jc(b,a){function c(a){a&&d.push(a)}var d=[b],e,g,h=["ng:app","ng-app","x-ng-app","data-ng-app"],f=/\sng[:\-]app(:\s*([\w\d_]+);?)?\s/;n(h,function(a){h[a]=!0;c(Y.getElementById(a));
a=a.replace(":","\\:");b.querySelectorAll&&(n(b.querySelectorAll("."+a),c),n(b.querySelectorAll("."+a+"\\:"),c),n(b.querySelectorAll("["+a+"]"),c))});n(d,function(a){if(!e){var b=f.exec(" "+a.className+" ");b?(e=a,g=(b[2]||"").replace(/\s+/g,",")):n(a.attributes,function(b){if(!e&&h[b.name])e=a,g=b.value})}});e&&a(e,g?[g]:[])}function rb(b,a){var c=function(){b=u(b);a=a||[];a.unshift(["$provide",function(a){a.value("$rootElement",b)}]);a.unshift("ng");var c=sb(a);c.invoke(["$rootScope","$rootElement",
"$compile","$injector",function(a,b,c,d){a.$apply(function(){b.data("$injector",d);c(b)(a)})}]);return c},d=/^NG_DEFER_BOOTSTRAP!/;if(N&&!d.test(N.name))return c();N.name=N.name.replace(d,"");Za.resumeBootstrap=function(b){n(b,function(b){a.push(b)});c()}}function $a(b,a){a=a||"_";return b.replace(kc,function(b,d){return(d?a:"")+b.toLowerCase()})}function ab(b,a,c){if(!b)throw Error("Argument '"+(a||"?")+"' is "+(c||"required"));return b}function ra(b,a,c){c&&E(b)&&(b=b[b.length-1]);ab(H(b),a,"not a function, got "+
(b&&typeof b=="object"?b.constructor.name||"Object":typeof b));return b}function lc(b){function a(a,b,e){return a[b]||(a[b]=e())}return a(a(b,"angular",Object),"module",function(){var b={};return function(d,e,g){e&&b.hasOwnProperty(d)&&(b[d]=null);return a(b,d,function(){function a(c,d,e){return function(){b[e||"push"]([c,d,arguments]);return k}}if(!e)throw Error("No module: "+d);var b=[],c=[],i=a("$injector","invoke"),k={_invokeQueue:b,_runBlocks:c,requires:e,name:d,provider:a("$provide","provider"),
factory:a("$provide","factory"),service:a("$provide","service"),value:a("$provide","value"),constant:a("$provide","constant","unshift"),filter:a("$filterProvider","register"),controller:a("$controllerProvider","register"),directive:a("$compileProvider","directive"),config:i,run:function(a){c.push(a);return this}};g&&i(g);return k})}})}function tb(b){return b.replace(mc,function(a,b,d,e){return e?d.toUpperCase():d}).replace(nc,"Moz$1")}function bb(b,a){function c(){var e;for(var b=[this],c=a,h,f,j,
i,k,m;b.length;){h=b.shift();f=0;for(j=h.length;f<j;f++){i=u(h[f]);c?i.triggerHandler("$destroy"):c=!c;k=0;for(e=(m=i.children()).length,i=e;k<i;k++)b.push(ca(m[k]))}}return d.apply(this,arguments)}var d=ca.fn[b],d=d.$original||d;c.$original=d;ca.fn[b]=c}function K(b){if(b instanceof K)return b;if(!(this instanceof K)){if(B(b)&&b.charAt(0)!="<")throw Error("selectors not implemented");return new K(b)}if(B(b)){var a=Y.createElement("div");a.innerHTML="<div>&#160;</div>"+b;a.removeChild(a.firstChild);
cb(this,a.childNodes);this.remove()}else cb(this,b)}function db(b){return b.cloneNode(!0)}function sa(b){ub(b);for(var a=0,b=b.childNodes||[];a<b.length;a++)sa(b[a])}function vb(b,a,c){var d=ba(b,"events");ba(b,"handle")&&(x(a)?n(d,function(a,c){eb(b,c,a);delete d[c]}):x(c)?(eb(b,a,d[a]),delete d[a]):Ta(d[a],c))}function ub(b){var a=b[Ba],c=Ca[a];c&&(c.handle&&(c.events.$destroy&&c.handle({},"$destroy"),vb(b)),delete Ca[a],b[Ba]=q)}function ba(b,a,c){var d=b[Ba],d=Ca[d||-1];if(y(c))d||(b[Ba]=d=++oc,
d=Ca[d]={}),d[a]=c;else return d&&d[a]}function wb(b,a,c){var d=ba(b,"data"),e=y(c),g=!e&&y(a),h=g&&!L(a);!d&&!h&&ba(b,"data",d={});if(e)d[a]=c;else if(g)if(h)return d&&d[a];else v(d,a);else return d}function Da(b,a){return(" "+b.className+" ").replace(/[\n\t]/g," ").indexOf(" "+a+" ")>-1}function xb(b,a){a&&n(a.split(" "),function(a){b.className=O((" "+b.className+" ").replace(/[\n\t]/g," ").replace(" "+O(a)+" "," "))})}function yb(b,a){a&&n(a.split(" "),function(a){if(!Da(b,a))b.className=O(b.className+
" "+O(a))})}function cb(b,a){if(a)for(var a=!a.nodeName&&y(a.length)&&!pa(a)?a:[a],c=0;c<a.length;c++)b.push(a[c])}function zb(b,a){return Ea(b,"$"+(a||"ngController")+"Controller")}function Ea(b,a,c){b=u(b);for(b[0].nodeType==9&&(b=b.find("html"));b.length;){if(c=b.data(a))return c;b=b.parent()}}function Ab(b,a){var c=Fa[a.toLowerCase()];return c&&Bb[b.nodeName]&&c}function pc(b,a){var c=function(c,e){if(!c.preventDefault)c.preventDefault=function(){c.returnValue=!1};if(!c.stopPropagation)c.stopPropagation=
function(){c.cancelBubble=!0};if(!c.target)c.target=c.srcElement||Y;if(x(c.defaultPrevented)){var g=c.preventDefault;c.preventDefault=function(){c.defaultPrevented=!0;g.call(c)};c.defaultPrevented=!1}c.isDefaultPrevented=function(){return c.defaultPrevented};n(a[e||c.type],function(a){a.call(b,c)});Z<=8?(c.preventDefault=null,c.stopPropagation=null,c.isDefaultPrevented=null):(delete c.preventDefault,delete c.stopPropagation,delete c.isDefaultPrevented)};c.elem=b;return c}function fa(b){var a=typeof b,
c;if(a=="object"&&b!==null)if(typeof(c=b.$$hashKey)=="function")c=b.$$hashKey();else{if(c===q)c=b.$$hashKey=ya()}else c=b;return a+":"+c}function Ga(b){n(b,this.put,this)}function fb(){}function Cb(b){var a,c;if(typeof b=="function"){if(!(a=b.$inject))a=[],c=b.toString().replace(qc,""),c=c.match(rc),n(c[1].split(sc),function(b){b.replace(tc,function(b,c,d){a.push(d)})}),b.$inject=a}else E(b)?(c=b.length-1,ra(b[c],"fn"),a=b.slice(0,c)):ra(b,"fn",!0);return a}function sb(b){function a(a){return function(b,
c){if(L(b))n(b,ob(a));else return a(b,c)}}function c(a,b){if(H(b)||E(b))b=m.instantiate(b);if(!b.$get)throw Error("Provider "+a+" must define $get factory method.");return k[a+f]=b}function d(a,b){return c(a,{$get:b})}function e(a){var b=[];n(a,function(a){if(!i.get(a))if(i.put(a,!0),B(a)){var c=ta(a);b=b.concat(e(c.requires)).concat(c._runBlocks);try{for(var d=c._invokeQueue,c=0,f=d.length;c<f;c++){var g=d[c],j=g[0]=="$injector"?m:m.get(g[0]);j[g[1]].apply(j,g[2])}}catch(h){throw h.message&&(h.message+=
" from "+a),h;}}else if(H(a))try{b.push(m.invoke(a))}catch(o){throw o.message&&(o.message+=" from "+a),o;}else if(E(a))try{b.push(m.invoke(a))}catch(k){throw k.message&&(k.message+=" from "+String(a[a.length-1])),k;}else ra(a,"module")});return b}function g(a,b){function c(d){if(typeof d!=="string")throw Error("Service name expected");if(a.hasOwnProperty(d)){if(a[d]===h)throw Error("Circular dependency: "+j.join(" <- "));return a[d]}else try{return j.unshift(d),a[d]=h,a[d]=b(d)}finally{j.shift()}}
function d(a,b,e){var f=[],i=Cb(a),g,h,j;h=0;for(g=i.length;h<g;h++)j=i[h],f.push(e&&e.hasOwnProperty(j)?e[j]:c(j));a.$inject||(a=a[g]);switch(b?-1:f.length){case 0:return a();case 1:return a(f[0]);case 2:return a(f[0],f[1]);case 3:return a(f[0],f[1],f[2]);case 4:return a(f[0],f[1],f[2],f[3]);case 5:return a(f[0],f[1],f[2],f[3],f[4]);case 6:return a(f[0],f[1],f[2],f[3],f[4],f[5]);case 7:return a(f[0],f[1],f[2],f[3],f[4],f[5],f[6]);case 8:return a(f[0],f[1],f[2],f[3],f[4],f[5],f[6],f[7]);case 9:return a(f[0],
f[1],f[2],f[3],f[4],f[5],f[6],f[7],f[8]);case 10:return a(f[0],f[1],f[2],f[3],f[4],f[5],f[6],f[7],f[8],f[9]);default:return a.apply(b,f)}}return{invoke:d,instantiate:function(a,b){var c=function(){},e;c.prototype=(E(a)?a[a.length-1]:a).prototype;c=new c;e=d(a,c,b);return L(e)?e:c},get:c,annotate:Cb}}var h={},f="Provider",j=[],i=new Ga,k={$provide:{provider:a(c),factory:a(d),service:a(function(a,b){return d(a,["$injector",function(a){return a.instantiate(b)}])}),value:a(function(a,b){return d(a,I(b))}),
constant:a(function(a,b){k[a]=b;l[a]=b}),decorator:function(a,b){var c=m.get(a+f),d=c.$get;c.$get=function(){var a=t.invoke(d,c);return t.invoke(b,null,{$delegate:a})}}}},m=g(k,function(){throw Error("Unknown provider: "+j.join(" <- "));}),l={},t=l.$injector=g(l,function(a){a=m.get(a+f);return t.invoke(a.$get,a)});n(e(b),function(a){t.invoke(a||w)});return t}function uc(){var b=!0;this.disableAutoScrolling=function(){b=!1};this.$get=["$window","$location","$rootScope",function(a,c,d){function e(a){var b=
null;n(a,function(a){!b&&A(a.nodeName)==="a"&&(b=a)});return b}function g(){var b=c.hash(),d;b?(d=h.getElementById(b))?d.scrollIntoView():(d=e(h.getElementsByName(b)))?d.scrollIntoView():b==="top"&&a.scrollTo(0,0):a.scrollTo(0,0)}var h=a.document;b&&d.$watch(function(){return c.hash()},function(){d.$evalAsync(g)});return g}]}function vc(b,a,c,d){function e(a){try{a.apply(null,ha.call(arguments,1))}finally{if(o--,o===0)for(;p.length;)try{p.pop()()}catch(b){c.error(b)}}}function g(a,b){(function S(){n(s,
function(a){a()});P=b(S,a)})()}function h(){C!=f.url()&&(C=f.url(),n(W,function(a){a(f.url())}))}var f=this,j=a[0],i=b.location,k=b.history,m=b.setTimeout,l=b.clearTimeout,t={};f.isMock=!1;var o=0,p=[];f.$$completeOutstandingRequest=e;f.$$incOutstandingRequestCount=function(){o++};f.notifyWhenNoOutstandingRequests=function(a){n(s,function(a){a()});o===0?a():p.push(a)};var s=[],P;f.addPollFn=function(a){x(P)&&g(100,m);s.push(a);return a};var C=i.href,z=a.find("base");f.url=function(a,b){if(a){if(C!=
a)return C=a,d.history?b?k.replaceState(null,"",a):(k.pushState(null,"",a),z.attr("href",z.attr("href"))):b?i.replace(a):i.href=a,f}else return i.href.replace(/%27/g,"'")};var W=[],J=!1;f.onUrlChange=function(a){J||(d.history&&u(b).bind("popstate",h),d.hashchange?u(b).bind("hashchange",h):f.addPollFn(h),J=!0);W.push(a);return a};f.baseHref=function(){var a=z.attr("href");return a?a.replace(/^https?\:\/\/[^\/]*/,""):""};var r={},$="",Q=f.baseHref();f.cookies=function(a,b){var d,e,f,i;if(a)if(b===q)j.cookie=
escape(a)+"=;path="+Q+";expires=Thu, 01 Jan 1970 00:00:00 GMT";else{if(B(b))d=(j.cookie=escape(a)+"="+escape(b)+";path="+Q).length+1,d>4096&&c.warn("Cookie '"+a+"' possibly not set or overflowed because it was too large ("+d+" > 4096 bytes)!")}else{if(j.cookie!==$){$=j.cookie;d=$.split("; ");r={};for(f=0;f<d.length;f++)e=d[f],i=e.indexOf("="),i>0&&(r[unescape(e.substring(0,i))]=unescape(e.substring(i+1)))}return r}};f.defer=function(a,b){var c;o++;c=m(function(){delete t[c];e(a)},b||0);t[c]=!0;return c};
f.defer.cancel=function(a){return t[a]?(delete t[a],l(a),e(w),!0):!1}}function wc(){this.$get=["$window","$log","$sniffer","$document",function(b,a,c,d){return new vc(b,d,a,c)}]}function xc(){this.$get=function(){function b(b,d){function e(a){if(a!=m){if(l){if(l==a)l=a.n}else l=a;g(a.n,a.p);g(a,m);m=a;m.n=null}}function g(a,b){if(a!=b){if(a)a.p=b;if(b)b.n=a}}if(b in a)throw Error("cacheId "+b+" taken");var h=0,f=v({},d,{id:b}),j={},i=d&&d.capacity||Number.MAX_VALUE,k={},m=null,l=null;return a[b]=
{put:function(a,b){var c=k[a]||(k[a]={key:a});e(c);x(b)||(a in j||h++,j[a]=b,h>i&&this.remove(l.key))},get:function(a){var b=k[a];if(b)return e(b),j[a]},remove:function(a){var b=k[a];if(b){if(b==m)m=b.p;if(b==l)l=b.n;g(b.n,b.p);delete k[a];delete j[a];h--}},removeAll:function(){j={};h=0;k={};m=l=null},destroy:function(){k=f=j=null;delete a[b]},info:function(){return v({},f,{size:h})}}}var a={};b.info=function(){var b={};n(a,function(a,e){b[e]=a.info()});return b};b.get=function(b){return a[b]};return b}}
function yc(){this.$get=["$cacheFactory",function(b){return b("templates")}]}function Db(b){var a={},c="Directive",d=/^\s*directive\:\s*([\d\w\-_]+)\s+(.*)$/,e=/(([\d\w\-_]+)(?:\:([^;]+))?;?)/,g="Template must have exactly one root element. was: ",h=/^\s*(https?|ftp|mailto|file):/;this.directive=function j(d,e){B(d)?(ab(e,"directive"),a.hasOwnProperty(d)||(a[d]=[],b.factory(d+c,["$injector","$exceptionHandler",function(b,c){var e=[];n(a[d],function(a){try{var g=b.invoke(a);if(H(g))g={compile:I(g)};
else if(!g.compile&&g.link)g.compile=I(g.link);g.priority=g.priority||0;g.name=g.name||d;g.require=g.require||g.controller&&g.name;g.restrict=g.restrict||"A";e.push(g)}catch(h){c(h)}});return e}])),a[d].push(e)):n(d,ob(j));return this};this.urlSanitizationWhitelist=function(a){return y(a)?(h=a,this):h};this.$get=["$injector","$interpolate","$exceptionHandler","$http","$templateCache","$parse","$controller","$rootScope","$document",function(b,i,k,m,l,t,o,p,s){function P(a,b,c){a instanceof u||(a=u(a));
n(a,function(b,c){b.nodeType==3&&b.nodeValue.match(/\S+/)&&(a[c]=u(b).wrap("<span></span>").parent()[0])});var d=z(a,b,a,c);return function(b,c){ab(b,"scope");for(var e=c?va.clone.call(a):a,g=0,i=e.length;g<i;g++){var h=e[g];(h.nodeType==1||h.nodeType==9)&&e.eq(g).data("$scope",b)}C(e,"ng-scope");c&&c(e,b);d&&d(b,e,e);return e}}function C(a,b){try{a.addClass(b)}catch(c){}}function z(a,b,c,d){function e(a,c,d,i){var h,j,k,o,l,m,t,s=[];l=0;for(m=c.length;l<m;l++)s.push(c[l]);t=l=0;for(m=g.length;l<
m;t++)j=s[t],c=g[l++],h=g[l++],c?(c.scope?(k=a.$new(L(c.scope)),u(j).data("$scope",k)):k=a,(o=c.transclude)||!i&&b?c(h,k,j,d,function(b){return function(c){var d=a.$new();d.$$transcluded=!0;return b(d,c).bind("$destroy",Ua(d,d.$destroy))}}(o||b)):c(h,k,j,q,i)):h&&h(a,j.childNodes,q,i)}for(var g=[],i,h,j,k=0;k<a.length;k++)h=new ia,i=W(a[k],[],h,d),h=(i=i.length?J(i,a[k],h,b,c):null)&&i.terminal||!a[k].childNodes||!a[k].childNodes.length?null:z(a[k].childNodes,i?i.transclude:b),g.push(i),g.push(h),
j=j||i||h;return j?e:null}function W(a,b,c,i){var g=c.$attr,h;switch(a.nodeType){case 1:r(b,ea(gb(a).toLowerCase()),"E",i);var j,k,l;h=a.attributes;for(var o=0,m=h&&h.length;o<m;o++)if(j=h[o],j.specified)k=j.name,l=ea(k.toLowerCase()),g[l]=k,c[l]=j=O(Z&&k=="href"?decodeURIComponent(a.getAttribute(k,2)):j.value),Ab(a,l)&&(c[l]=!0),S(a,b,j,l),r(b,l,"A",i);a=a.className;if(B(a)&&a!=="")for(;h=e.exec(a);)l=ea(h[2]),r(b,l,"C",i)&&(c[l]=O(h[3])),a=a.substr(h.index+h[0].length);break;case 3:y(b,a.nodeValue);
break;case 8:try{if(h=d.exec(a.nodeValue))l=ea(h[1]),r(b,l,"M",i)&&(c[l]=O(h[2]))}catch(t){}}b.sort(F);return b}function J(a,b,c,d,e){function i(a,b){if(a)a.require=r.require,m.push(a);if(b)b.require=r.require,s.push(b)}function h(a,b){var c,d="data",e=!1;if(B(a)){for(;(c=a.charAt(0))=="^"||c=="?";)a=a.substr(1),c=="^"&&(d="inheritedData"),e=e||c=="?";c=b[d]("$"+a+"Controller");if(!c&&!e)throw Error("No controller: "+a);}else E(a)&&(c=[],n(a,function(a){c.push(h(a,b))}));return c}function j(a,d,e,
i,g){var l,p,r,D,C;l=b===e?c:hc(c,new ia(u(e),c.$attr));p=l.$$element;if(J){var P=/^\s*([@=&])\s*(\w*)\s*$/,ja=d.$parent||d;n(J.scope,function(a,b){var c=a.match(P)||[],e=c[2]||b,c=c[1],i,g,h;d.$$isolateBindings[b]=c+e;switch(c){case "@":l.$observe(e,function(a){d[b]=a});l.$$observers[e].$$scope=ja;break;case "=":g=t(l[e]);h=g.assign||function(){i=d[b]=g(ja);throw Error(Eb+l[e]+" (directive: "+J.name+")");};i=d[b]=g(ja);d.$watch(function(){var a=g(ja);a!==d[b]&&(a!==i?i=d[b]=a:h(ja,a=i=d[b]));return a});
break;case "&":g=t(l[e]);d[b]=function(a){return g(ja,a)};break;default:throw Error("Invalid isolate scope definition for directive "+J.name+": "+a);}})}y&&n(y,function(a){var b={$scope:d,$element:p,$attrs:l,$transclude:g};C=a.controller;C=="@"&&(C=l[a.name]);p.data("$"+a.name+"Controller",o(C,b))});i=0;for(r=m.length;i<r;i++)try{D=m[i],D(d,p,l,D.require&&h(D.require,p))}catch(z){k(z,qa(p))}a&&a(d,e.childNodes,q,g);i=0;for(r=s.length;i<r;i++)try{D=s[i],D(d,p,l,D.require&&h(D.require,p))}catch(zc){k(zc,
qa(p))}}for(var l=-Number.MAX_VALUE,m=[],s=[],p=null,J=null,z=null,D=c.$$element=u(b),r,F,T,ka,S=d,y,x,X,v=0,A=a.length;v<A;v++){r=a[v];T=q;if(l>r.priority)break;if(X=r.scope)ua("isolated scope",J,r,D),L(X)&&(C(D,"ng-isolate-scope"),J=r),C(D,"ng-scope"),p=p||r;F=r.name;if(X=r.controller)y=y||{},ua("'"+F+"' controller",y[F],r,D),y[F]=r;if(X=r.transclude)ua("transclusion",ka,r,D),ka=r,l=r.priority,X=="element"?(T=u(b),D=c.$$element=u(Y.createComment(" "+F+": "+c[F]+" ")),b=D[0],w(e,u(T[0]),b),S=P(T,
d,l)):(T=u(db(b)).contents(),D.html(""),S=P(T,d));if(X=r.template)if(ua("template",z,r,D),z=r,X=Fb(X),r.replace){T=u("<div>"+O(X)+"</div>").contents();b=T[0];if(T.length!=1||b.nodeType!==1)throw Error(g+X);w(e,D,b);F={$attr:{}};a=a.concat(W(b,a.splice(v+1,a.length-(v+1)),F));$(c,F);A=a.length}else D.html(X);if(r.templateUrl)ua("template",z,r,D),z=r,j=Q(a.splice(v,a.length-v),j,D,c,e,r.replace,S),A=a.length;else if(r.compile)try{x=r.compile(D,c,S),H(x)?i(null,x):x&&i(x.pre,x.post)}catch(G){k(G,qa(D))}if(r.terminal)j.terminal=
!0,l=Math.max(l,r.priority)}j.scope=p&&p.scope;j.transclude=ka&&S;return j}function r(d,e,i,g){var h=!1;if(a.hasOwnProperty(e))for(var l,e=b.get(e+c),o=0,m=e.length;o<m;o++)try{if(l=e[o],(g===q||g>l.priority)&&l.restrict.indexOf(i)!=-1)d.push(l),h=!0}catch(t){k(t)}return h}function $(a,b){var c=b.$attr,d=a.$attr,e=a.$$element;n(a,function(d,e){e.charAt(0)!="$"&&(b[e]&&(d+=(e==="style"?";":" ")+b[e]),a.$set(e,d,!0,c[e]))});n(b,function(b,i){i=="class"?(C(e,b),a["class"]=(a["class"]?a["class"]+" ":
"")+b):i=="style"?e.attr("style",e.attr("style")+";"+b):i.charAt(0)!="$"&&!a.hasOwnProperty(i)&&(a[i]=b,d[i]=c[i])})}function Q(a,b,c,d,e,i,h){var j=[],k,o,t=c[0],s=a.shift(),p=v({},s,{controller:null,templateUrl:null,transclude:null,scope:null});c.html("");m.get(s.templateUrl,{cache:l}).success(function(l){var m,s,l=Fb(l);if(i){s=u("<div>"+O(l)+"</div>").contents();m=s[0];if(s.length!=1||m.nodeType!==1)throw Error(g+l);l={$attr:{}};w(e,c,m);W(m,a,l);$(d,l)}else m=t,c.html(l);a.unshift(p);k=J(a,m,
d,h);for(o=z(c[0].childNodes,h);j.length;){var ia=j.pop(),l=j.pop();s=j.pop();var r=j.pop(),D=m;s!==t&&(D=db(m),w(l,u(s),D));k(function(){b(o,r,D,e,ia)},r,D,e,ia)}j=null}).error(function(a,b,c,d){throw Error("Failed to load template: "+d.url);});return function(a,c,d,e,i){j?(j.push(c),j.push(d),j.push(e),j.push(i)):k(function(){b(o,c,d,e,i)},c,d,e,i)}}function F(a,b){return b.priority-a.priority}function ua(a,b,c,d){if(b)throw Error("Multiple directives ["+b.name+", "+c.name+"] asking for "+a+" on: "+
qa(d));}function y(a,b){var c=i(b,!0);c&&a.push({priority:0,compile:I(function(a,b){var d=b.parent(),e=d.data("$binding")||[];e.push(c);C(d.data("$binding",e),"ng-binding");a.$watch(c,function(a){b[0].nodeValue=a})})})}function S(a,b,c,d){var e=i(c,!0);e&&b.push({priority:100,compile:I(function(a,b,c){b=c.$$observers||(c.$$observers={});d==="class"&&(e=i(c[d],!0));c[d]=q;(b[d]||(b[d]=[])).$$inter=!0;(c.$$observers&&c.$$observers[d].$$scope||a).$watch(e,function(a){c.$set(d,a)})})})}function w(a,b,
c){var d=b[0],e=d.parentNode,i,g;if(a){i=0;for(g=a.length;i<g;i++)if(a[i]==d){a[i]=c;break}}e&&e.replaceChild(c,d);c[u.expando]=d[u.expando];b[0]=c}var ia=function(a,b){this.$$element=a;this.$attr=b||{}};ia.prototype={$normalize:ea,$set:function(a,b,c,d){var e=Ab(this.$$element[0],a),i=this.$$observers;e&&(this.$$element.prop(a,b),d=e);this[a]=b;d?this.$attr[a]=d:(d=this.$attr[a])||(this.$attr[a]=d=$a(a,"-"));if(gb(this.$$element[0])==="A"&&a==="href")D.setAttribute("href",b),e=D.href,e.match(h)||
(this[a]=b="unsafe:"+e);c!==!1&&(b===null||b===q?this.$$element.removeAttr(d):this.$$element.attr(d,b));i&&n(i[a],function(a){try{a(b)}catch(c){k(c)}})},$observe:function(a,b){var c=this,d=c.$$observers||(c.$$observers={}),e=d[a]||(d[a]=[]);e.push(b);p.$evalAsync(function(){e.$$inter||b(c[a])});return b}};var D=s[0].createElement("a"),T=i.startSymbol(),ka=i.endSymbol(),Fb=T=="{{"||ka=="}}"?na:function(a){return a.replace(/\{\{/g,T).replace(/}}/g,ka)};return P}]}function ea(b){return tb(b.replace(Ac,
""))}function Bc(){var b={};this.register=function(a,c){L(a)?v(b,a):b[a]=c};this.$get=["$injector","$window",function(a,c){return function(d,e){if(B(d)){var g=d,d=b.hasOwnProperty(g)?b[g]:hb(e.$scope,g,!0)||hb(c,g,!0);ra(d,g,!0)}return a.instantiate(d,e)}}]}function Cc(){this.$get=["$window",function(b){return u(b.document)}]}function Dc(){this.$get=["$log",function(b){return function(a,c){b.error.apply(b,arguments)}}]}function Ec(){var b="{{",a="}}";this.startSymbol=function(a){return a?(b=a,this):
b};this.endSymbol=function(b){return b?(a=b,this):a};this.$get=["$parse",function(c){function d(d,f){for(var j,i,k=0,m=[],l=d.length,t=!1,o=[];k<l;)(j=d.indexOf(b,k))!=-1&&(i=d.indexOf(a,j+e))!=-1?(k!=j&&m.push(d.substring(k,j)),m.push(k=c(t=d.substring(j+e,i))),k.exp=t,k=i+g,t=!0):(k!=l&&m.push(d.substring(k)),k=l);if(!(l=m.length))m.push(""),l=1;if(!f||t)return o.length=l,k=function(a){for(var b=0,c=l,d;b<c;b++){if(typeof(d=m[b])=="function")d=d(a),d==null||d==q?d="":typeof d!="string"&&(d=da(d));
o[b]=d}return o.join("")},k.exp=d,k.parts=m,k}var e=b.length,g=a.length;d.startSymbol=function(){return b};d.endSymbol=function(){return a};return d}]}function Gb(b){for(var b=b.split("/"),a=b.length;a--;)b[a]=Ya(b[a]);return b.join("/")}function wa(b,a){var c=Hb.exec(b),c={protocol:c[1],host:c[3],port:G(c[5])||Ib[c[1]]||null,path:c[6]||"/",search:c[8],hash:c[10]};if(a)a.$$protocol=c.protocol,a.$$host=c.host,a.$$port=c.port;return c}function la(b,a,c){return b+"://"+a+(c==Ib[b]?"":":"+c)}function Fc(b,
a,c){var d=wa(b);return decodeURIComponent(d.path)!=a||x(d.hash)||d.hash.indexOf(c)!==0?b:la(d.protocol,d.host,d.port)+a.substr(0,a.lastIndexOf("/"))+d.hash.substr(c.length)}function Gc(b,a,c){var d=wa(b);if(decodeURIComponent(d.path)==a&&!x(d.hash)&&d.hash.indexOf(c)===0)return b;else{var e=d.search&&"?"+d.search||"",g=d.hash&&"#"+d.hash||"",h=a.substr(0,a.lastIndexOf("/")),f=d.path.substr(h.length);if(d.path.indexOf(h)!==0)throw Error('Invalid url "'+b+'", missing path prefix "'+h+'" !');return la(d.protocol,
d.host,d.port)+a+"#"+c+f+e+g}}function ib(b,a,c){a=a||"";this.$$parse=function(b){var c=wa(b,this);if(c.path.indexOf(a)!==0)throw Error('Invalid url "'+b+'", missing path prefix "'+a+'" !');this.$$path=decodeURIComponent(c.path.substr(a.length));this.$$search=Wa(c.search);this.$$hash=c.hash&&decodeURIComponent(c.hash)||"";this.$$compose()};this.$$compose=function(){var b=qb(this.$$search),c=this.$$hash?"#"+Ya(this.$$hash):"";this.$$url=Gb(this.$$path)+(b?"?"+b:"")+c;this.$$absUrl=la(this.$$protocol,
this.$$host,this.$$port)+a+this.$$url};this.$$rewriteAppUrl=function(a){if(a.indexOf(c)==0)return a};this.$$parse(b)}function Ha(b,a,c){var d;this.$$parse=function(b){var c=wa(b,this);if(c.hash&&c.hash.indexOf(a)!==0)throw Error('Invalid url "'+b+'", missing hash prefix "'+a+'" !');d=c.path+(c.search?"?"+c.search:"");c=Hc.exec((c.hash||"").substr(a.length));this.$$path=c[1]?(c[1].charAt(0)=="/"?"":"/")+decodeURIComponent(c[1]):"";this.$$search=Wa(c[3]);this.$$hash=c[5]&&decodeURIComponent(c[5])||
"";this.$$compose()};this.$$compose=function(){var b=qb(this.$$search),c=this.$$hash?"#"+Ya(this.$$hash):"";this.$$url=Gb(this.$$path)+(b?"?"+b:"")+c;this.$$absUrl=la(this.$$protocol,this.$$host,this.$$port)+d+(this.$$url?"#"+a+this.$$url:"")};this.$$rewriteAppUrl=function(a){if(a.indexOf(c)==0)return a};this.$$parse(b)}function Jb(b,a,c,d){Ha.apply(this,arguments);this.$$rewriteAppUrl=function(b){if(b.indexOf(c)==0)return c+d+"#"+a+b.substr(c.length)}}function Ia(b){return function(){return this[b]}}
function Kb(b,a){return function(c){if(x(c))return this[b];this[b]=a(c);this.$$compose();return this}}function Ic(){var b="",a=!1;this.hashPrefix=function(a){return y(a)?(b=a,this):b};this.html5Mode=function(b){return y(b)?(a=b,this):a};this.$get=["$rootScope","$browser","$sniffer","$rootElement",function(c,d,e,g){function h(a){c.$broadcast("$locationChangeSuccess",f.absUrl(),a)}var f,j,i,k=d.url(),m=wa(k);a?(j=d.baseHref()||"/",i=j.substr(0,j.lastIndexOf("/")),m=la(m.protocol,m.host,m.port)+i+"/",
f=e.history?new ib(Fc(k,j,b),i,m):new Jb(Gc(k,j,b),b,m,j.substr(i.length+1))):(m=la(m.protocol,m.host,m.port)+(m.path||"")+(m.search?"?"+m.search:"")+"#"+b+"/",f=new Ha(k,b,m));g.bind("click",function(a){if(!a.ctrlKey&&!(a.metaKey||a.which==2)){for(var b=u(a.target);A(b[0].nodeName)!=="a";)if(b[0]===g[0]||!(b=b.parent())[0])return;var d=b.prop("href"),e=f.$$rewriteAppUrl(d);d&&!b.attr("target")&&e&&(f.$$parse(e),c.$apply(),a.preventDefault(),N.angular["ff-684208-preventDefault"]=!0)}});f.absUrl()!=
k&&d.url(f.absUrl(),!0);d.onUrlChange(function(a){f.absUrl()!=a&&(c.$evalAsync(function(){var b=f.absUrl();f.$$parse(a);h(b)}),c.$$phase||c.$digest())});var l=0;c.$watch(function(){var a=d.url(),b=f.$$replace;if(!l||a!=f.absUrl())l++,c.$evalAsync(function(){c.$broadcast("$locationChangeStart",f.absUrl(),a).defaultPrevented?f.$$parse(a):(d.url(f.absUrl(),b),h(a))});f.$$replace=!1;return l});return f}]}function Jc(){this.$get=["$window",function(b){function a(a){a instanceof Error&&(a.stack?a=a.message&&
a.stack.indexOf(a.message)===-1?"Error: "+a.message+"\n"+a.stack:a.stack:a.sourceURL&&(a=a.message+"\n"+a.sourceURL+":"+a.line));return a}function c(c){var e=b.console||{},g=e[c]||e.log||w;return g.apply?function(){var b=[];n(arguments,function(c){b.push(a(c))});return g.apply(e,b)}:function(a,b){g(a,b)}}return{log:c("log"),warn:c("warn"),info:c("info"),error:c("error")}}]}function Kc(b,a){function c(a){return a.indexOf(s)!=-1}function d(){return o+1<b.length?b.charAt(o+1):!1}function e(a){return"0"<=
a&&a<="9"}function g(a){return a==" "||a=="\r"||a=="\t"||a=="\n"||a=="\u000b"||a=="\u00a0"}function h(a){return"a"<=a&&a<="z"||"A"<=a&&a<="Z"||"_"==a||a=="$"}function f(a){return a=="-"||a=="+"||e(a)}function j(a,c,d){d=d||o;throw Error("Lexer Error: "+a+" at column"+(y(c)?"s "+c+"-"+o+" ["+b.substring(c,d)+"]":" "+d)+" in expression ["+b+"].");}function i(){for(var a="",c=o;o<b.length;){var i=A(b.charAt(o));if(i=="."||e(i))a+=i;else{var g=d();if(i=="e"&&f(g))a+=i;else if(f(i)&&g&&e(g)&&a.charAt(a.length-
1)=="e")a+=i;else if(f(i)&&(!g||!e(g))&&a.charAt(a.length-1)=="e")j("Invalid exponent");else break}o++}a*=1;l.push({index:c,text:a,json:!0,fn:function(){return a}})}function k(){for(var c="",d=o,f,i,j;o<b.length;){var k=b.charAt(o);if(k=="."||h(k)||e(k))k=="."&&(f=o),c+=k;else break;o++}if(f)for(i=o;i<b.length;){k=b.charAt(i);if(k=="("){j=c.substr(f-d+1);c=c.substr(0,f-d);o=i;break}if(g(k))i++;else break}d={index:d,text:c};if(Ja.hasOwnProperty(c))d.fn=d.json=Ja[c];else{var m=Lb(c,a);d.fn=v(function(a,
b){return m(a,b)},{assign:function(a,b){return Mb(a,c,b)}})}l.push(d);j&&(l.push({index:f,text:".",json:!1}),l.push({index:f+1,text:j,json:!1}))}function m(a){var c=o;o++;for(var d="",e=a,f=!1;o<b.length;){var i=b.charAt(o);e+=i;if(f)i=="u"?(i=b.substring(o+1,o+5),i.match(/[\da-f]{4}/i)||j("Invalid unicode escape [\\u"+i+"]"),o+=4,d+=String.fromCharCode(parseInt(i,16))):(f=Lc[i],d+=f?f:i),f=!1;else if(i=="\\")f=!0;else if(i==a){o++;l.push({index:c,text:e,string:d,json:!0,fn:function(){return d}});
return}else d+=i;o++}j("Unterminated quote",c)}for(var l=[],t,o=0,p=[],s,P=":";o<b.length;){s=b.charAt(o);if(c("\"'"))m(s);else if(e(s)||c(".")&&e(d()))i();else if(h(s)){if(k(),"{,".indexOf(P)!=-1&&p[0]=="{"&&(t=l[l.length-1]))t.json=t.text.indexOf(".")==-1}else if(c("(){}[].,;:"))l.push({index:o,text:s,json:":[,".indexOf(P)!=-1&&c("{[")||c("}]:,")}),c("{[")&&p.unshift(s),c("}]")&&p.shift(),o++;else if(g(s)){o++;continue}else{var n=s+d(),z=Ja[s],W=Ja[n];W?(l.push({index:o,text:n,fn:W}),o+=2):z?(l.push({index:o,
text:s,fn:z,json:"[,:".indexOf(P)!=-1&&c("+-")}),o+=1):j("Unexpected next character ",o,o+1)}P=s}return l}function Mc(b,a,c,d){function e(a,c){throw Error("Syntax Error: Token '"+c.text+"' "+a+" at column "+(c.index+1)+" of the expression ["+b+"] starting at ["+b.substring(c.index)+"].");}function g(){if(Q.length===0)throw Error("Unexpected end of expression: "+b);return Q[0]}function h(a,b,c,d){if(Q.length>0){var e=Q[0],f=e.text;if(f==a||f==b||f==c||f==d||!a&&!b&&!c&&!d)return e}return!1}function f(b,
c,d,f){return(b=h(b,c,d,f))?(a&&!b.json&&e("is not valid json",b),Q.shift(),b):!1}function j(a){f(a)||e("is unexpected, expecting ["+a+"]",h())}function i(a,b){return function(c,d){return a(c,d,b)}}function k(a,b,c){return function(d,e){return b(d,e,a,c)}}function m(){for(var a=[];;)if(Q.length>0&&!h("}",")",";","]")&&a.push(x()),!f(";"))return a.length==1?a[0]:function(b,c){for(var d,e=0;e<a.length;e++){var f=a[e];f&&(d=f(b,c))}return d}}function l(){for(var a=f(),b=c(a.text),d=[];;)if(a=f(":"))d.push(F());
else{var e=function(a,c,e){for(var e=[e],f=0;f<d.length;f++)e.push(d[f](a,c));return b.apply(a,e)};return function(){return e}}}function t(){for(var a=o(),b;;)if(b=f("||"))a=k(a,b.fn,o());else return a}function o(){var a=p(),b;if(b=f("&&"))a=k(a,b.fn,o());return a}function p(){var a=s(),b;if(b=f("==","!="))a=k(a,b.fn,p());return a}function s(){var a;a=n();for(var b;b=f("+","-");)a=k(a,b.fn,n());if(b=f("<",">","<=",">="))a=k(a,b.fn,s());return a}function n(){for(var a=C(),b;b=f("*","/","%");)a=k(a,
b.fn,C());return a}function C(){var a;return f("+")?z():(a=f("-"))?k(r,a.fn,C()):(a=f("!"))?i(a.fn,C()):z()}function z(){var a;if(f("("))a=x(),j(")");else if(f("["))a=W();else if(f("{"))a=J();else{var b=f();(a=b.fn)||e("not a primary expression",b)}for(var c;b=f("(","[",".");)b.text==="("?(a=y(a,c),c=null):b.text==="["?(c=a,a=S(a)):b.text==="."?(c=a,a=u(a)):e("IMPOSSIBLE");return a}function W(){var a=[];if(g().text!="]"){do a.push(F());while(f(","))}j("]");return function(b,c){for(var d=[],e=0;e<
a.length;e++)d.push(a[e](b,c));return d}}function J(){var a=[];if(g().text!="}"){do{var b=f(),b=b.string||b.text;j(":");var c=F();a.push({key:b,value:c})}while(f(","))}j("}");return function(b,c){for(var d={},e=0;e<a.length;e++){var f=a[e],i=f.value(b,c);d[f.key]=i}return d}}var r=I(0),$,Q=Kc(b,d),F=function(){var a=t(),c,d;return(d=f("="))?(a.assign||e("implies assignment but ["+b.substring(0,d.index)+"] can not be assigned to",d),c=t(),function(b,d){return a.assign(b,c(b,d),d)}):a},y=function(a,
b){var c=[];if(g().text!=")"){do c.push(F());while(f(","))}j(")");return function(d,e){for(var f=[],i=b?b(d,e):d,g=0;g<c.length;g++)f.push(c[g](d,e));g=a(d,e)||w;return g.apply?g.apply(i,f):g(f[0],f[1],f[2],f[3],f[4])}},u=function(a){var b=f().text,c=Lb(b,d);return v(function(b,d){return c(a(b,d),d)},{assign:function(c,d,e){return Mb(a(c,e),b,d)}})},S=function(a){var b=F();j("]");return v(function(c,d){var e=a(c,d),f=b(c,d),i;if(!e)return q;if((e=e[f])&&e.then){i=e;if(!("$$v"in e))i.$$v=q,i.then(function(a){i.$$v=
a});e=e.$$v}return e},{assign:function(c,d,e){return a(c,e)[b(c,e)]=d}})},x=function(){for(var a=F(),b;;)if(b=f("|"))a=k(a,b.fn,l());else return a};a?(F=t,y=u=S=x=function(){e("is not valid json",{text:b,index:0})},$=z()):$=m();Q.length!==0&&e("is an unexpected token",Q[0]);return $}function Mb(b,a,c){for(var a=a.split("."),d=0;a.length>1;d++){var e=a.shift(),g=b[e];g||(g={},b[e]=g);b=g}return b[a.shift()]=c}function hb(b,a,c){if(!a)return b;for(var a=a.split("."),d,e=b,g=a.length,h=0;h<g;h++)d=a[h],
b&&(b=(e=b)[d]);return!c&&H(b)?Ua(e,b):b}function Nb(b,a,c,d,e){return function(g,h){var f=h&&h.hasOwnProperty(b)?h:g,j;if(f===null||f===q)return f;if((f=f[b])&&f.then){if(!("$$v"in f))j=f,j.$$v=q,j.then(function(a){j.$$v=a});f=f.$$v}if(!a||f===null||f===q)return f;if((f=f[a])&&f.then){if(!("$$v"in f))j=f,j.$$v=q,j.then(function(a){j.$$v=a});f=f.$$v}if(!c||f===null||f===q)return f;if((f=f[c])&&f.then){if(!("$$v"in f))j=f,j.$$v=q,j.then(function(a){j.$$v=a});f=f.$$v}if(!d||f===null||f===q)return f;
if((f=f[d])&&f.then){if(!("$$v"in f))j=f,j.$$v=q,j.then(function(a){j.$$v=a});f=f.$$v}if(!e||f===null||f===q)return f;if((f=f[e])&&f.then){if(!("$$v"in f))j=f,j.$$v=q,j.then(function(a){j.$$v=a});f=f.$$v}return f}}function Lb(b,a){if(jb.hasOwnProperty(b))return jb[b];var c=b.split("."),d=c.length,e;if(a)e=d<6?Nb(c[0],c[1],c[2],c[3],c[4]):function(a,b){var e=0,i;do i=Nb(c[e++],c[e++],c[e++],c[e++],c[e++])(a,b),b=q,a=i;while(e<d);return i};else{var g="var l, fn, p;\n";n(c,function(a,b){g+="if(s === null || s === undefined) return s;\nl=s;\ns="+
(b?"s":'((k&&k.hasOwnProperty("'+a+'"))?k:s)')+'["'+a+'"];\nif (s && s.then) {\n if (!("$$v" in s)) {\n p=s;\n p.$$v = undefined;\n p.then(function(v) {p.$$v=v;});\n}\n s=s.$$v\n}\n'});g+="return s;";e=Function("s","k",g);e.toString=function(){return g}}return jb[b]=e}function Nc(){var b={};this.$get=["$filter","$sniffer",function(a,c){return function(d){switch(typeof d){case "string":return b.hasOwnProperty(d)?b[d]:b[d]=Mc(d,!1,a,c.csp);case "function":return d;default:return w}}}]}function Oc(){this.$get=
["$rootScope","$exceptionHandler",function(b,a){return Pc(function(a){b.$evalAsync(a)},a)}]}function Pc(b,a){function c(a){return a}function d(a){return h(a)}var e=function(){var f=[],j,i;return i={resolve:function(a){if(f){var c=f;f=q;j=g(a);c.length&&b(function(){for(var a,b=0,d=c.length;b<d;b++)a=c[b],j.then(a[0],a[1])})}},reject:function(a){i.resolve(h(a))},promise:{then:function(b,i){var g=e(),h=function(d){try{g.resolve((b||c)(d))}catch(e){a(e),g.reject(e)}},o=function(b){try{g.resolve((i||
d)(b))}catch(c){a(c),g.reject(c)}};f?f.push([h,o]):j.then(h,o);return g.promise}}}},g=function(a){return a&&a.then?a:{then:function(c){var d=e();b(function(){d.resolve(c(a))});return d.promise}}},h=function(a){return{then:function(c,i){var g=e();b(function(){g.resolve((i||d)(a))});return g.promise}}};return{defer:e,reject:h,when:function(f,j,i){var k=e(),m,l=function(b){try{return(j||c)(b)}catch(d){return a(d),h(d)}},t=function(b){try{return(i||d)(b)}catch(c){return a(c),h(c)}};b(function(){g(f).then(function(a){m||
(m=!0,k.resolve(g(a).then(l,t)))},function(a){m||(m=!0,k.resolve(t(a)))})});return k.promise},all:function(a){var b=e(),c=a.length,d=[];c?n(a,function(a,e){g(a).then(function(a){e in d||(d[e]=a,--c||b.resolve(d))},function(a){e in d||b.reject(a)})}):b.resolve(d);return b.promise}}}function Qc(){var b={};this.when=function(a,c){b[a]=v({reloadOnSearch:!0},c);if(a){var d=a[a.length-1]=="/"?a.substr(0,a.length-1):a+"/";b[d]={redirectTo:a}}return this};this.otherwise=function(a){this.when(null,a);return this};
this.$get=["$rootScope","$location","$routeParams","$q","$injector","$http","$templateCache",function(a,c,d,e,g,h,f){function j(a,b){for(var b="^"+b.replace(/[-\/\\^$*+?.()|[\]{}]/g,"\\$&")+"$",c="",d=[],e={},f=/:(\w+)/g,i,g=0;(i=f.exec(b))!==null;)c+=b.slice(g,i.index),c+="([^\\/]*)",d.push(i[1]),g=f.lastIndex;c+=b.substr(g);var h=a.match(RegExp(c));h&&n(d,function(a,b){e[a]=h[b+1]});return h?e:null}function i(){var b=k(),i=t.current;if(b&&i&&b.$$route===i.$$route&&ga(b.pathParams,i.pathParams)&&
!b.reloadOnSearch&&!l)i.params=b.params,V(i.params,d),a.$broadcast("$routeUpdate",i);else if(b||i)l=!1,a.$broadcast("$routeChangeStart",b,i),(t.current=b)&&b.redirectTo&&(B(b.redirectTo)?c.path(m(b.redirectTo,b.params)).search(b.params).replace():c.url(b.redirectTo(b.pathParams,c.path(),c.search())).replace()),e.when(b).then(function(){if(b){var a=[],c=[],d;n(b.resolve||{},function(b,d){a.push(d);c.push(B(b)?g.get(b):g.invoke(b))});if(!y(d=b.template))if(y(d=b.templateUrl))d=h.get(d,{cache:f}).then(function(a){return a.data});
y(d)&&(a.push("$template"),c.push(d));return e.all(c).then(function(b){var c={};n(b,function(b,d){c[a[d]]=b});return c})}}).then(function(c){if(b==t.current){if(b)b.locals=c,V(b.params,d);a.$broadcast("$routeChangeSuccess",b,i)}},function(c){b==t.current&&a.$broadcast("$routeChangeError",b,i,c)})}function k(){var a,d;n(b,function(b,e){if(!d&&(a=j(c.path(),e)))d=za(b,{params:v({},c.search(),a),pathParams:a}),d.$$route=b});return d||b[null]&&za(b[null],{params:{},pathParams:{}})}function m(a,b){var c=
[];n((a||"").split(":"),function(a,d){if(d==0)c.push(a);else{var e=a.match(/(\w+)(.*)/),f=e[1];c.push(b[f]);c.push(e[2]||"");delete b[f]}});return c.join("")}var l=!1,t={routes:b,reload:function(){l=!0;a.$evalAsync(i)}};a.$on("$locationChangeSuccess",i);return t}]}function Rc(){this.$get=I({})}function Sc(){var b=10;this.digestTtl=function(a){arguments.length&&(b=a);return b};this.$get=["$injector","$exceptionHandler","$parse",function(a,c,d){function e(){this.$id=ya();this.$$phase=this.$parent=this.$$watchers=
this.$$nextSibling=this.$$prevSibling=this.$$childHead=this.$$childTail=null;this["this"]=this.$root=this;this.$$destroyed=!1;this.$$asyncQueue=[];this.$$listeners={};this.$$isolateBindings={}}function g(a){if(j.$$phase)throw Error(j.$$phase+" already in progress");j.$$phase=a}function h(a,b){var c=d(a);ra(c,b);return c}function f(){}e.prototype={$new:function(a){if(H(a))throw Error("API-CHANGE: Use $controller to instantiate controllers.");a?(a=new e,a.$root=this.$root):(a=function(){},a.prototype=
this,a=new a,a.$id=ya());a["this"]=a;a.$$listeners={};a.$parent=this;a.$$asyncQueue=[];a.$$watchers=a.$$nextSibling=a.$$childHead=a.$$childTail=null;a.$$prevSibling=this.$$childTail;this.$$childHead?this.$$childTail=this.$$childTail.$$nextSibling=a:this.$$childHead=this.$$childTail=a;return a},$watch:function(a,b,c){var d=h(a,"watch"),e=this.$$watchers,g={fn:b,last:f,get:d,exp:a,eq:!!c};if(!H(b)){var j=h(b||w,"listener");g.fn=function(a,b,c){j(c)}}if(!e)e=this.$$watchers=[];e.unshift(g);return function(){Ta(e,
g)}},$digest:function(){var a,d,e,h,t,o,p,s=b,n,C=[],z,q;g("$digest");do{p=!1;n=this;do{for(t=n.$$asyncQueue;t.length;)try{n.$eval(t.shift())}catch(J){c(J)}if(h=n.$$watchers)for(o=h.length;o--;)try{if(a=h[o],(d=a.get(n))!==(e=a.last)&&!(a.eq?ga(d,e):typeof d=="number"&&typeof e=="number"&&isNaN(d)&&isNaN(e)))p=!0,a.last=a.eq?V(d):d,a.fn(d,e===f?d:e,n),s<5&&(z=4-s,C[z]||(C[z]=[]),q=H(a.exp)?"fn: "+(a.exp.name||a.exp.toString()):a.exp,q+="; newVal: "+da(d)+"; oldVal: "+da(e),C[z].push(q))}catch(r){c(r)}if(!(h=
n.$$childHead||n!==this&&n.$$nextSibling))for(;n!==this&&!(h=n.$$nextSibling);)n=n.$parent}while(n=h);if(p&&!s--)throw j.$$phase=null,Error(b+" $digest() iterations reached. Aborting!\nWatchers fired in the last 5 iterations: "+da(C));}while(p||t.length);j.$$phase=null},$destroy:function(){if(!(j==this||this.$$destroyed)){var a=this.$parent;this.$broadcast("$destroy");this.$$destroyed=!0;if(a.$$childHead==this)a.$$childHead=this.$$nextSibling;if(a.$$childTail==this)a.$$childTail=this.$$prevSibling;
if(this.$$prevSibling)this.$$prevSibling.$$nextSibling=this.$$nextSibling;if(this.$$nextSibling)this.$$nextSibling.$$prevSibling=this.$$prevSibling;this.$parent=this.$$nextSibling=this.$$prevSibling=this.$$childHead=this.$$childTail=null}},$eval:function(a,b){return d(a)(this,b)},$evalAsync:function(a){this.$$asyncQueue.push(a)},$apply:function(a){try{return g("$apply"),this.$eval(a)}catch(b){c(b)}finally{j.$$phase=null;try{j.$digest()}catch(d){throw c(d),d;}}},$on:function(a,b){var c=this.$$listeners[a];
c||(this.$$listeners[a]=c=[]);c.push(b);return function(){c[Aa(c,b)]=null}},$emit:function(a,b){var d=[],e,f=this,g=!1,h={name:a,targetScope:f,stopPropagation:function(){g=!0},preventDefault:function(){h.defaultPrevented=!0},defaultPrevented:!1},j=[h].concat(ha.call(arguments,1)),n,C;do{e=f.$$listeners[a]||d;h.currentScope=f;n=0;for(C=e.length;n<C;n++)if(e[n])try{if(e[n].apply(null,j),g)return h}catch(z){c(z)}else e.splice(n,1),n--,C--;f=f.$parent}while(f);return h},$broadcast:function(a,b){var d=
this,e=this,f={name:a,targetScope:this,preventDefault:function(){f.defaultPrevented=!0},defaultPrevented:!1},g=[f].concat(ha.call(arguments,1)),h,j;do{d=e;f.currentScope=d;e=d.$$listeners[a]||[];h=0;for(j=e.length;h<j;h++)if(e[h])try{e[h].apply(null,g)}catch(n){c(n)}else e.splice(h,1),h--,j--;if(!(e=d.$$childHead||d!==this&&d.$$nextSibling))for(;d!==this&&!(e=d.$$nextSibling);)d=d.$parent}while(d=e);return f}};var j=new e;return j}]}function Tc(){this.$get=["$window",function(b){var a={},c=G((/android (\d+)/.exec(A(b.navigator.userAgent))||
[])[1]);return{history:!(!b.history||!b.history.pushState||c<4),hashchange:"onhashchange"in b&&(!b.document.documentMode||b.document.documentMode>7),hasEvent:function(c){if(c=="input"&&Z==9)return!1;if(x(a[c])){var e=b.document.createElement("div");a[c]="on"+c in e}return a[c]},csp:!1}}]}function Uc(){this.$get=I(N)}function Ob(b){var a={},c,d,e;if(!b)return a;n(b.split("\n"),function(b){e=b.indexOf(":");c=A(O(b.substr(0,e)));d=O(b.substr(e+1));c&&(a[c]?a[c]+=", "+d:a[c]=d)});return a}function Pb(b){var a=
L(b)?b:q;return function(c){a||(a=Ob(b));return c?a[A(c)]||null:a}}function Qb(b,a,c){if(H(c))return c(b,a);n(c,function(c){b=c(b,a)});return b}function Vc(){var b=/^\s*(\[|\{[^\{])/,a=/[\}\]]\s*$/,c=/^\)\]\}',?\n/,d=this.defaults={transformResponse:[function(d){B(d)&&(d=d.replace(c,""),b.test(d)&&a.test(d)&&(d=pb(d,!0)));return d}],transformRequest:[function(a){return L(a)&&xa.apply(a)!=="[object File]"?da(a):a}],headers:{common:{Accept:"application/json, text/plain, */*","X-Requested-With":"XMLHttpRequest"},
post:{"Content-Type":"application/json;charset=utf-8"},put:{"Content-Type":"application/json;charset=utf-8"}}},e=this.responseInterceptors=[];this.$get=["$httpBackend","$browser","$cacheFactory","$rootScope","$q","$injector",function(a,b,c,j,i,k){function m(a){function c(a){var b=v({},a,{data:Qb(a.data,a.headers,f)});return 200<=a.status&&a.status<300?b:i.reject(b)}a.method=ma(a.method);var e=a.transformRequest||d.transformRequest,f=a.transformResponse||d.transformResponse,g=d.headers,g=v({"X-XSRF-TOKEN":b.cookies()["XSRF-TOKEN"]},
g.common,g[A(a.method)],a.headers),e=Qb(a.data,Pb(g),e),j;x(a.data)&&delete g["Content-Type"];j=l(a,e,g);j=j.then(c,c);n(p,function(a){j=a(j)});j.success=function(b){j.then(function(c){b(c.data,c.status,c.headers,a)});return j};j.error=function(b){j.then(null,function(c){b(c.data,c.status,c.headers,a)});return j};return j}function l(b,c,d){function e(a,b,c){n&&(200<=a&&a<300?n.put(q,[a,b,Ob(c)]):n.remove(q));f(b,a,c);j.$apply()}function f(a,c,d){c=Math.max(c,0);(200<=c&&c<300?k.resolve:k.reject)({data:a,
status:c,headers:Pb(d),config:b})}function h(){var a=Aa(m.pendingRequests,b);a!==-1&&m.pendingRequests.splice(a,1)}var k=i.defer(),l=k.promise,n,p,q=t(b.url,b.params);m.pendingRequests.push(b);l.then(h,h);b.cache&&b.method=="GET"&&(n=L(b.cache)?b.cache:o);if(n)if(p=n.get(q))if(p.then)return p.then(h,h),p;else E(p)?f(p[1],p[0],V(p[2])):f(p,200,{});else n.put(q,l);p||a(b.method,q,c,e,d,b.timeout,b.withCredentials);return l}function t(a,b){if(!b)return a;var c=[];fc(b,function(a,b){a==null||a==q||(L(a)&&
(a=da(a)),c.push(encodeURIComponent(b)+"="+encodeURIComponent(a)))});return a+(a.indexOf("?")==-1?"?":"&")+c.join("&")}var o=c("$http"),p=[];n(e,function(a){p.push(B(a)?k.get(a):k.invoke(a))});m.pendingRequests=[];(function(a){n(arguments,function(a){m[a]=function(b,c){return m(v(c||{},{method:a,url:b}))}})})("get","delete","head","jsonp");(function(a){n(arguments,function(a){m[a]=function(b,c,d){return m(v(d||{},{method:a,url:b,data:c}))}})})("post","put");m.defaults=d;return m}]}function Wc(){this.$get=
["$browser","$window","$document",function(b,a,c){return Xc(b,Yc,b.defer,a.angular.callbacks,c[0],a.location.protocol.replace(":",""))}]}function Xc(b,a,c,d,e,g){function h(a,b){var c=e.createElement("script"),d=function(){e.body.removeChild(c);b&&b()};c.type="text/javascript";c.src=a;Z?c.onreadystatechange=function(){/loaded|complete/.test(c.readyState)&&d()}:c.onload=c.onerror=d;e.body.appendChild(c)}return function(e,j,i,k,m,l,t){function o(a,c,d,e){c=(j.match(Hb)||["",g])[1]=="file"?d?200:404:
c;a(c==1223?204:c,d,e);b.$$completeOutstandingRequest(w)}b.$$incOutstandingRequestCount();j=j||b.url();if(A(e)=="jsonp"){var p="_"+(d.counter++).toString(36);d[p]=function(a){d[p].data=a};h(j.replace("JSON_CALLBACK","angular.callbacks."+p),function(){d[p].data?o(k,200,d[p].data):o(k,-2);delete d[p]})}else{var s=new a;s.open(e,j,!0);n(m,function(a,b){a&&s.setRequestHeader(b,a)});var q;s.onreadystatechange=function(){if(s.readyState==4){var a=s.getAllResponseHeaders(),b=["Cache-Control","Content-Language",
"Content-Type","Expires","Last-Modified","Pragma"];a||(a="",n(b,function(b){var c=s.getResponseHeader(b);c&&(a+=b+": "+c+"\n")}));o(k,q||s.status,s.responseText,a)}};if(t)s.withCredentials=!0;s.send(i||"");l>0&&c(function(){q=-1;s.abort()},l)}}}function Zc(){this.$get=function(){return{id:"en-us",NUMBER_FORMATS:{DECIMAL_SEP:".",GROUP_SEP:",",PATTERNS:[{minInt:1,minFrac:0,maxFrac:3,posPre:"",posSuf:"",negPre:"-",negSuf:"",gSize:3,lgSize:3},{minInt:1,minFrac:2,maxFrac:2,posPre:"\u00a4",posSuf:"",negPre:"(\u00a4",
negSuf:")",gSize:3,lgSize:3}],CURRENCY_SYM:"$"},DATETIME_FORMATS:{MONTH:"January,February,March,April,May,June,July,August,September,October,November,December".split(","),SHORTMONTH:"Jan,Feb,Mar,Apr,May,Jun,Jul,Aug,Sep,Oct,Nov,Dec".split(","),DAY:"Sunday,Monday,Tuesday,Wednesday,Thursday,Friday,Saturday".split(","),SHORTDAY:"Sun,Mon,Tue,Wed,Thu,Fri,Sat".split(","),AMPMS:["AM","PM"],medium:"MMM d, y h:mm:ss a","short":"M/d/yy h:mm a",fullDate:"EEEE, MMMM d, y",longDate:"MMMM d, y",mediumDate:"MMM d, y",
shortDate:"M/d/yy",mediumTime:"h:mm:ss a",shortTime:"h:mm a"},pluralCat:function(b){return b===1?"one":"other"}}}}function $c(){this.$get=["$rootScope","$browser","$q","$exceptionHandler",function(b,a,c,d){function e(e,f,j){var i=c.defer(),k=i.promise,m=y(j)&&!j,f=a.defer(function(){try{i.resolve(e())}catch(a){i.reject(a),d(a)}m||b.$apply()},f),j=function(){delete g[k.$$timeoutId]};k.$$timeoutId=f;g[f]=i;k.then(j,j);return k}var g={};e.cancel=function(b){return b&&b.$$timeoutId in g?(g[b.$$timeoutId].reject("canceled"),
a.defer.cancel(b.$$timeoutId)):!1};return e}]}function Rb(b){function a(a,e){return b.factory(a+c,e)}var c="Filter";this.register=a;this.$get=["$injector",function(a){return function(b){return a.get(b+c)}}];a("currency",Sb);a("date",Tb);a("filter",ad);a("json",bd);a("limitTo",cd);a("lowercase",dd);a("number",Ub);a("orderBy",Vb);a("uppercase",ed)}function ad(){return function(b,a){if(!E(b))return b;var c=[];c.check=function(a){for(var b=0;b<c.length;b++)if(!c[b](a))return!1;return!0};var d=function(a,
b){if(b.charAt(0)==="!")return!d(a,b.substr(1));switch(typeof a){case "boolean":case "number":case "string":return(""+a).toLowerCase().indexOf(b)>-1;case "object":for(var c in a)if(c.charAt(0)!=="$"&&d(a[c],b))return!0;return!1;case "array":for(c=0;c<a.length;c++)if(d(a[c],b))return!0;return!1;default:return!1}};switch(typeof a){case "boolean":case "number":case "string":a={$:a};case "object":for(var e in a)e=="$"?function(){var b=(""+a[e]).toLowerCase();b&&c.push(function(a){return d(a,b)})}():function(){var b=
e,f=(""+a[e]).toLowerCase();f&&c.push(function(a){return d(hb(a,b),f)})}();break;case "function":c.push(a);break;default:return b}for(var g=[],h=0;h<b.length;h++){var f=b[h];c.check(f)&&g.push(f)}return g}}function Sb(b){var a=b.NUMBER_FORMATS;return function(b,d){if(x(d))d=a.CURRENCY_SYM;return Wb(b,a.PATTERNS[1],a.GROUP_SEP,a.DECIMAL_SEP,2).replace(/\u00A4/g,d)}}function Ub(b){var a=b.NUMBER_FORMATS;return function(b,d){return Wb(b,a.PATTERNS[0],a.GROUP_SEP,a.DECIMAL_SEP,d)}}function Wb(b,a,c,d,
e){if(isNaN(b)||!isFinite(b))return"";var g=b<0,b=Math.abs(b),h=b+"",f="",j=[],i=!1;if(h.indexOf("e")!==-1){var k=h.match(/([\d\.]+)e(-?)(\d+)/);k&&k[2]=="-"&&k[3]>e+1?h="0":(f=h,i=!0)}if(!i){h=(h.split(Xb)[1]||"").length;x(e)&&(e=Math.min(Math.max(a.minFrac,h),a.maxFrac));var h=Math.pow(10,e),b=Math.round(b*h)/h,b=(""+b).split(Xb),h=b[0],b=b[1]||"",i=0,k=a.lgSize,m=a.gSize;if(h.length>=k+m)for(var i=h.length-k,l=0;l<i;l++)(i-l)%m===0&&l!==0&&(f+=c),f+=h.charAt(l);for(l=i;l<h.length;l++)(h.length-
l)%k===0&&l!==0&&(f+=c),f+=h.charAt(l);for(;b.length<e;)b+="0";e&&e!=="0"&&(f+=d+b.substr(0,e))}j.push(g?a.negPre:a.posPre);j.push(f);j.push(g?a.negSuf:a.posSuf);return j.join("")}function kb(b,a,c){var d="";b<0&&(d="-",b=-b);for(b=""+b;b.length<a;)b="0"+b;c&&(b=b.substr(b.length-a));return d+b}function M(b,a,c,d){return function(e){e=e["get"+b]();if(c>0||e>-c)e+=c;e===0&&c==-12&&(e=12);return kb(e,a,d)}}function Ka(b,a){return function(c,d){var e=c["get"+b](),g=ma(a?"SHORT"+b:b);return d[g][e]}}
function Tb(b){function a(a){var b;if(b=a.match(c)){var a=new Date(0),g=0,h=0;b[9]&&(g=G(b[9]+b[10]),h=G(b[9]+b[11]));a.setUTCFullYear(G(b[1]),G(b[2])-1,G(b[3]));a.setUTCHours(G(b[4]||0)-g,G(b[5]||0)-h,G(b[6]||0),G(b[7]||0))}return a}var c=/^(\d{4})-?(\d\d)-?(\d\d)(?:T(\d\d)(?::?(\d\d)(?::?(\d\d)(?:\.(\d+))?)?)?(Z|([+-])(\d\d):?(\d\d))?)?$/;return function(c,e){var g="",h=[],f,j,e=e||"mediumDate",e=b.DATETIME_FORMATS[e]||e;B(c)&&(c=fd.test(c)?G(c):a(c));Ra(c)&&(c=new Date(c));if(!oa(c))return c;for(;e;)(j=
gd.exec(e))?(h=h.concat(ha.call(j,1)),e=h.pop()):(h.push(e),e=null);n(h,function(a){f=hd[a];g+=f?f(c,b.DATETIME_FORMATS):a.replace(/(^'|'$)/g,"").replace(/''/g,"'")});return g}}function bd(){return function(b){return da(b,!0)}}function cd(){return function(b,a){if(!(b instanceof Array))return b;var a=G(a),c=[],d,e;if(!b||!(b instanceof Array))return c;a>b.length?a=b.length:a<-b.length&&(a=-b.length);a>0?(d=0,e=a):(d=b.length+a,e=b.length);for(;d<e;d++)c.push(b[d]);return c}}function Vb(b){return function(a,
c,d){function e(a,b){return Va(b)?function(b,c){return a(c,b)}:a}if(!E(a))return a;if(!c)return a;for(var c=E(c)?c:[c],c=Sa(c,function(a){var c=!1,d=a||na;if(B(a)){if(a.charAt(0)=="+"||a.charAt(0)=="-")c=a.charAt(0)=="-",a=a.substring(1);d=b(a)}return e(function(a,b){var c;c=d(a);var e=d(b),f=typeof c,g=typeof e;f==g?(f=="string"&&(c=c.toLowerCase()),f=="string"&&(e=e.toLowerCase()),c=c===e?0:c<e?-1:1):c=f<g?-1:1;return c},c)}),g=[],h=0;h<a.length;h++)g.push(a[h]);return g.sort(e(function(a,b){for(var d=
0;d<c.length;d++){var e=c[d](a,b);if(e!==0)return e}return 0},d))}}function R(b){H(b)&&(b={link:b});b.restrict=b.restrict||"AC";return I(b)}function Yb(b,a){function c(a,c){c=c?"-"+$a(c,"-"):"";b.removeClass((a?La:Ma)+c).addClass((a?Ma:La)+c)}var d=this,e=b.parent().controller("form")||Na,g=0,h=d.$error={};d.$name=a.name;d.$dirty=!1;d.$pristine=!0;d.$valid=!0;d.$invalid=!1;e.$addControl(d);b.addClass(Oa);c(!0);d.$addControl=function(a){a.$name&&!d.hasOwnProperty(a.$name)&&(d[a.$name]=a)};d.$removeControl=
function(a){a.$name&&d[a.$name]===a&&delete d[a.$name];n(h,function(b,c){d.$setValidity(c,!0,a)})};d.$setValidity=function(a,b,i){var k=h[a];if(b){if(k&&(Ta(k,i),!k.length)){g--;if(!g)c(b),d.$valid=!0,d.$invalid=!1;h[a]=!1;c(!0,a);e.$setValidity(a,!0,d)}}else{g||c(b);if(k){if(Aa(k,i)!=-1)return}else h[a]=k=[],g++,c(!1,a),e.$setValidity(a,!1,d);k.push(i);d.$valid=!1;d.$invalid=!0}};d.$setDirty=function(){b.removeClass(Oa).addClass(Zb);d.$dirty=!0;d.$pristine=!1;e.$setDirty()}}function U(b){return x(b)||
b===""||b===null||b!==b}function Pa(b,a,c,d,e,g){var h=function(){var c=O(a.val());d.$viewValue!==c&&b.$apply(function(){d.$setViewValue(c)})};if(e.hasEvent("input"))a.bind("input",h);else{var f;a.bind("keydown",function(a){a=a.keyCode;a===91||15<a&&a<19||37<=a&&a<=40||f||(f=g.defer(function(){h();f=null}))});a.bind("change",h)}d.$render=function(){a.val(U(d.$viewValue)?"":d.$viewValue)};var j=c.ngPattern,i=function(a,b){return U(b)||a.test(b)?(d.$setValidity("pattern",!0),b):(d.$setValidity("pattern",
!1),q)};j&&(j.match(/^\/(.*)\/$/)?(j=RegExp(j.substr(1,j.length-2)),e=function(a){return i(j,a)}):e=function(a){var c=b.$eval(j);if(!c||!c.test)throw Error("Expected "+j+" to be a RegExp but was "+c);return i(c,a)},d.$formatters.push(e),d.$parsers.push(e));if(c.ngMinlength){var k=G(c.ngMinlength),e=function(a){return!U(a)&&a.length<k?(d.$setValidity("minlength",!1),q):(d.$setValidity("minlength",!0),a)};d.$parsers.push(e);d.$formatters.push(e)}if(c.ngMaxlength){var m=G(c.ngMaxlength),c=function(a){return!U(a)&&
a.length>m?(d.$setValidity("maxlength",!1),q):(d.$setValidity("maxlength",!0),a)};d.$parsers.push(c);d.$formatters.push(c)}}function lb(b,a){b="ngClass"+b;return R(function(c,d,e){function g(b){if(a===!0||c.$index%2===a)j&&b!==j&&h(j),f(b);j=b}function h(a){L(a)&&!E(a)&&(a=Sa(a,function(a,b){if(a)return b}));d.removeClass(E(a)?a.join(" "):a)}function f(a){L(a)&&!E(a)&&(a=Sa(a,function(a,b){if(a)return b}));a&&d.addClass(E(a)?a.join(" "):a)}var j=q;c.$watch(e[b],g,!0);e.$observe("class",function(){var a=
c.$eval(e[b]);g(a,a)});b!=="ngClass"&&c.$watch("$index",function(d,g){var j=d%2;j!==g%2&&(j==a?f(c.$eval(e[b])):h(c.$eval(e[b])))})})}var A=function(b){return B(b)?b.toLowerCase():b},ma=function(b){return B(b)?b.toUpperCase():b},Z=G((/msie (\d+)/.exec(A(navigator.userAgent))||[])[1]),u,ca,ha=[].slice,Qa=[].push,xa=Object.prototype.toString,Za=N.angular||(N.angular={}),ta,gb,aa=["0","0","0"];w.$inject=[];na.$inject=[];gb=Z<9?function(b){b=b.nodeName?b:b[0];return b.scopeName&&b.scopeName!="HTML"?ma(b.scopeName+
":"+b.nodeName):b.nodeName}:function(b){return b.nodeName?b.nodeName:b[0].nodeName};var kc=/[A-Z]/g,id={full:"1.0.6",major:1,minor:0,dot:6,codeName:"universal-irreversibility"},Ca=K.cache={},Ba=K.expando="ng-"+(new Date).getTime(),oc=1,$b=N.document.addEventListener?function(b,a,c){b.addEventListener(a,c,!1)}:function(b,a,c){b.attachEvent("on"+a,c)},eb=N.document.removeEventListener?function(b,a,c){b.removeEventListener(a,c,!1)}:function(b,a,c){b.detachEvent("on"+a,c)},mc=/([\:\-\_]+(.))/g,nc=/^moz([A-Z])/,
va=K.prototype={ready:function(b){function a(){c||(c=!0,b())}var c=!1;this.bind("DOMContentLoaded",a);K(N).bind("load",a)},toString:function(){var b=[];n(this,function(a){b.push(""+a)});return"["+b.join(", ")+"]"},eq:function(b){return b>=0?u(this[b]):u(this[this.length+b])},length:0,push:Qa,sort:[].sort,splice:[].splice},Fa={};n("multiple,selected,checked,disabled,readOnly,required".split(","),function(b){Fa[A(b)]=b});var Bb={};n("input,select,option,textarea,button,form".split(","),function(b){Bb[ma(b)]=
!0});n({data:wb,inheritedData:Ea,scope:function(b){return Ea(b,"$scope")},controller:zb,injector:function(b){return Ea(b,"$injector")},removeAttr:function(b,a){b.removeAttribute(a)},hasClass:Da,css:function(b,a,c){a=tb(a);if(y(c))b.style[a]=c;else{var d;Z<=8&&(d=b.currentStyle&&b.currentStyle[a],d===""&&(d="auto"));d=d||b.style[a];Z<=8&&(d=d===""?q:d);return d}},attr:function(b,a,c){var d=A(a);if(Fa[d])if(y(c))c?(b[a]=!0,b.setAttribute(a,d)):(b[a]=!1,b.removeAttribute(d));else return b[a]||(b.attributes.getNamedItem(a)||
w).specified?d:q;else if(y(c))b.setAttribute(a,c);else if(b.getAttribute)return b=b.getAttribute(a,2),b===null?q:b},prop:function(b,a,c){if(y(c))b[a]=c;else return b[a]},text:v(Z<9?function(b,a){if(b.nodeType==1){if(x(a))return b.innerText;b.innerText=a}else{if(x(a))return b.nodeValue;b.nodeValue=a}}:function(b,a){if(x(a))return b.textContent;b.textContent=a},{$dv:""}),val:function(b,a){if(x(a))return b.value;b.value=a},html:function(b,a){if(x(a))return b.innerHTML;for(var c=0,d=b.childNodes;c<d.length;c++)sa(d[c]);
b.innerHTML=a}},function(b,a){K.prototype[a]=function(a,d){var e,g;if((b.length==2&&b!==Da&&b!==zb?a:d)===q)if(L(a)){for(e=0;e<this.length;e++)if(b===wb)b(this[e],a);else for(g in a)b(this[e],g,a[g]);return this}else{if(this.length)return b(this[0],a,d)}else{for(e=0;e<this.length;e++)b(this[e],a,d);return this}return b.$dv}});n({removeData:ub,dealoc:sa,bind:function a(c,d,e){var g=ba(c,"events"),h=ba(c,"handle");g||ba(c,"events",g={});h||ba(c,"handle",h=pc(c,g));n(d.split(" "),function(d){var j=g[d];
if(!j){if(d=="mouseenter"||d=="mouseleave"){var i=0;g.mouseenter=[];g.mouseleave=[];a(c,"mouseover",function(a){i++;i==1&&h(a,"mouseenter")});a(c,"mouseout",function(a){i--;i==0&&h(a,"mouseleave")})}else $b(c,d,h),g[d]=[];j=g[d]}j.push(e)})},unbind:vb,replaceWith:function(a,c){var d,e=a.parentNode;sa(a);n(new K(c),function(c){d?e.insertBefore(c,d.nextSibling):e.replaceChild(c,a);d=c})},children:function(a){var c=[];n(a.childNodes,function(a){a.nodeType===1&&c.push(a)});return c},contents:function(a){return a.childNodes||
[]},append:function(a,c){n(new K(c),function(c){a.nodeType===1&&a.appendChild(c)})},prepend:function(a,c){if(a.nodeType===1){var d=a.firstChild;n(new K(c),function(c){d?a.insertBefore(c,d):(a.appendChild(c),d=c)})}},wrap:function(a,c){var c=u(c)[0],d=a.parentNode;d&&d.replaceChild(c,a);c.appendChild(a)},remove:function(a){sa(a);var c=a.parentNode;c&&c.removeChild(a)},after:function(a,c){var d=a,e=a.parentNode;n(new K(c),function(a){e.insertBefore(a,d.nextSibling);d=a})},addClass:yb,removeClass:xb,
toggleClass:function(a,c,d){x(d)&&(d=!Da(a,c));(d?yb:xb)(a,c)},parent:function(a){return(a=a.parentNode)&&a.nodeType!==11?a:null},next:function(a){if(a.nextElementSibling)return a.nextElementSibling;for(a=a.nextSibling;a!=null&&a.nodeType!==1;)a=a.nextSibling;return a},find:function(a,c){return a.getElementsByTagName(c)},clone:db,triggerHandler:function(a,c){var d=(ba(a,"events")||{})[c];n(d,function(c){c.call(a,null)})}},function(a,c){K.prototype[c]=function(c,e){for(var g,h=0;h<this.length;h++)g==
q?(g=a(this[h],c,e),g!==q&&(g=u(g))):cb(g,a(this[h],c,e));return g==q?this:g}});Ga.prototype={put:function(a,c){this[fa(a)]=c},get:function(a){return this[fa(a)]},remove:function(a){var c=this[a=fa(a)];delete this[a];return c}};fb.prototype={push:function(a,c){var d=this[a=fa(a)];d?d.push(c):this[a]=[c]},shift:function(a){var c=this[a=fa(a)];if(c)return c.length==1?(delete this[a],c[0]):c.shift()},peek:function(a){if(a=this[fa(a)])return a[0]}};var rc=/^function\s*[^\(]*\(\s*([^\)]*)\)/m,sc=/,/,tc=
/^\s*(_?)(\S+?)\1\s*$/,qc=/((\/\/.*$)|(\/\*[\s\S]*?\*\/))/mg,Eb="Non-assignable model expression: ";Db.$inject=["$provide"];var Ac=/^(x[\:\-_]|data[\:\-_])/i,Hb=/^([^:]+):\/\/(\w+:{0,1}\w*@)?(\{?[\w\.-]*\}?)(:([0-9]+))?(\/[^\?#]*)?(\?([^#]*))?(#(.*))?$/,ac=/^([^\?#]*)?(\?([^#]*))?(#(.*))?$/,Hc=ac,Ib={http:80,https:443,ftp:21};ib.prototype={$$replace:!1,absUrl:Ia("$$absUrl"),url:function(a,c){if(x(a))return this.$$url;var d=ac.exec(a);d[1]&&this.path(decodeURIComponent(d[1]));if(d[2]||d[1])this.search(d[3]||
"");this.hash(d[5]||"",c);return this},protocol:Ia("$$protocol"),host:Ia("$$host"),port:Ia("$$port"),path:Kb("$$path",function(a){return a.charAt(0)=="/"?a:"/"+a}),search:function(a,c){if(x(a))return this.$$search;y(c)?c===null?delete this.$$search[a]:this.$$search[a]=c:this.$$search=B(a)?Wa(a):a;this.$$compose();return this},hash:Kb("$$hash",na),replace:function(){this.$$replace=!0;return this}};Ha.prototype=za(ib.prototype);Jb.prototype=za(Ha.prototype);var Ja={"null":function(){return null},"true":function(){return!0},
"false":function(){return!1},undefined:w,"+":function(a,c,d,e){d=d(a,c);e=e(a,c);return y(d)?y(e)?d+e:d:y(e)?e:q},"-":function(a,c,d,e){d=d(a,c);e=e(a,c);return(y(d)?d:0)-(y(e)?e:0)},"*":function(a,c,d,e){return d(a,c)*e(a,c)},"/":function(a,c,d,e){return d(a,c)/e(a,c)},"%":function(a,c,d,e){return d(a,c)%e(a,c)},"^":function(a,c,d,e){return d(a,c)^e(a,c)},"=":w,"==":function(a,c,d,e){return d(a,c)==e(a,c)},"!=":function(a,c,d,e){return d(a,c)!=e(a,c)},"<":function(a,c,d,e){return d(a,c)<e(a,c)},
">":function(a,c,d,e){return d(a,c)>e(a,c)},"<=":function(a,c,d,e){return d(a,c)<=e(a,c)},">=":function(a,c,d,e){return d(a,c)>=e(a,c)},"&&":function(a,c,d,e){return d(a,c)&&e(a,c)},"||":function(a,c,d,e){return d(a,c)||e(a,c)},"&":function(a,c,d,e){return d(a,c)&e(a,c)},"|":function(a,c,d,e){return e(a,c)(a,c,d(a,c))},"!":function(a,c,d){return!d(a,c)}},Lc={n:"\n",f:"\u000c",r:"\r",t:"\t",v:"\u000b","'":"'",'"':'"'},jb={},Yc=N.XMLHttpRequest||function(){try{return new ActiveXObject("Msxml2.XMLHTTP.6.0")}catch(a){}try{return new ActiveXObject("Msxml2.XMLHTTP.3.0")}catch(c){}try{return new ActiveXObject("Msxml2.XMLHTTP")}catch(d){}throw Error("This browser does not support XMLHttpRequest.");
};Rb.$inject=["$provide"];Sb.$inject=["$locale"];Ub.$inject=["$locale"];var Xb=".",hd={yyyy:M("FullYear",4),yy:M("FullYear",2,0,!0),y:M("FullYear",1),MMMM:Ka("Month"),MMM:Ka("Month",!0),MM:M("Month",2,1),M:M("Month",1,1),dd:M("Date",2),d:M("Date",1),HH:M("Hours",2),H:M("Hours",1),hh:M("Hours",2,-12),h:M("Hours",1,-12),mm:M("Minutes",2),m:M("Minutes",1),ss:M("Seconds",2),s:M("Seconds",1),EEEE:Ka("Day"),EEE:Ka("Day",!0),a:function(a,c){return a.getHours()<12?c.AMPMS[0]:c.AMPMS[1]},Z:function(a){var a=
-1*a.getTimezoneOffset(),c=a>=0?"+":"";c+=kb(Math[a>0?"floor":"ceil"](a/60),2)+kb(Math.abs(a%60),2);return c}},gd=/((?:[^yMdHhmsaZE']+)|(?:'(?:[^']|'')*')|(?:E+|y+|M+|d+|H+|h+|m+|s+|a|Z))(.*)/,fd=/^\d+$/;Tb.$inject=["$locale"];var dd=I(A),ed=I(ma);Vb.$inject=["$parse"];var jd=I({restrict:"E",compile:function(a,c){Z<=8&&(!c.href&&!c.name&&c.$set("href",""),a.append(Y.createComment("IE fix")));return function(a,c){c.bind("click",function(a){c.attr("href")||a.preventDefault()})}}}),mb={};n(Fa,function(a,
c){var d=ea("ng-"+c);mb[d]=function(){return{priority:100,compile:function(){return function(a,g,h){a.$watch(h[d],function(a){h.$set(c,!!a)})}}}}});n(["src","href"],function(a){var c=ea("ng-"+a);mb[c]=function(){return{priority:99,link:function(d,e,g){g.$observe(c,function(c){c&&(g.$set(a,c),Z&&e.prop(a,g[a]))})}}}});var Na={$addControl:w,$removeControl:w,$setValidity:w,$setDirty:w};Yb.$inject=["$element","$attrs","$scope"];var Qa=function(a){return["$timeout",function(c){var d={name:"form",restrict:"E",
controller:Yb,compile:function(){return{pre:function(a,d,h,f){if(!h.action){var j=function(a){a.preventDefault?a.preventDefault():a.returnValue=!1};$b(d[0],"submit",j);d.bind("$destroy",function(){c(function(){eb(d[0],"submit",j)},0,!1)})}var i=d.parent().controller("form"),k=h.name||h.ngForm;k&&(a[k]=f);i&&d.bind("$destroy",function(){i.$removeControl(f);k&&(a[k]=q);v(f,Na)})}}}};return a?v(V(d),{restrict:"EAC"}):d}]},kd=Qa(),ld=Qa(!0),md=/^(ftp|http|https):\/\/(\w+:{0,1}\w*@)?(\S+)(:[0-9]+)?(\/|\/([\w#!:.?+=&%@!\-\/]))?$/,
nd=/^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4}$/,od=/^\s*(\-|\+)?(\d+|(\d*(\.\d*)))\s*$/,bc={text:Pa,number:function(a,c,d,e,g,h){Pa(a,c,d,e,g,h);e.$parsers.push(function(a){var c=U(a);return c||od.test(a)?(e.$setValidity("number",!0),a===""?null:c?a:parseFloat(a)):(e.$setValidity("number",!1),q)});e.$formatters.push(function(a){return U(a)?"":""+a});if(d.min){var f=parseFloat(d.min),a=function(a){return!U(a)&&a<f?(e.$setValidity("min",!1),q):(e.$setValidity("min",!0),a)};e.$parsers.push(a);
e.$formatters.push(a)}if(d.max){var j=parseFloat(d.max),d=function(a){return!U(a)&&a>j?(e.$setValidity("max",!1),q):(e.$setValidity("max",!0),a)};e.$parsers.push(d);e.$formatters.push(d)}e.$formatters.push(function(a){return U(a)||Ra(a)?(e.$setValidity("number",!0),a):(e.$setValidity("number",!1),q)})},url:function(a,c,d,e,g,h){Pa(a,c,d,e,g,h);a=function(a){return U(a)||md.test(a)?(e.$setValidity("url",!0),a):(e.$setValidity("url",!1),q)};e.$formatters.push(a);e.$parsers.push(a)},email:function(a,
c,d,e,g,h){Pa(a,c,d,e,g,h);a=function(a){return U(a)||nd.test(a)?(e.$setValidity("email",!0),a):(e.$setValidity("email",!1),q)};e.$formatters.push(a);e.$parsers.push(a)},radio:function(a,c,d,e){x(d.name)&&c.attr("name",ya());c.bind("click",function(){c[0].checked&&a.$apply(function(){e.$setViewValue(d.value)})});e.$render=function(){c[0].checked=d.value==e.$viewValue};d.$observe("value",e.$render)},checkbox:function(a,c,d,e){var g=d.ngTrueValue,h=d.ngFalseValue;B(g)||(g=!0);B(h)||(h=!1);c.bind("click",
function(){a.$apply(function(){e.$setViewValue(c[0].checked)})});e.$render=function(){c[0].checked=e.$viewValue};e.$formatters.push(function(a){return a===g});e.$parsers.push(function(a){return a?g:h})},hidden:w,button:w,submit:w,reset:w},cc=["$browser","$sniffer",function(a,c){return{restrict:"E",require:"?ngModel",link:function(d,e,g,h){h&&(bc[A(g.type)]||bc.text)(d,e,g,h,c,a)}}}],Ma="ng-valid",La="ng-invalid",Oa="ng-pristine",Zb="ng-dirty",pd=["$scope","$exceptionHandler","$attrs","$element","$parse",
function(a,c,d,e,g){function h(a,c){c=c?"-"+$a(c,"-"):"";e.removeClass((a?La:Ma)+c).addClass((a?Ma:La)+c)}this.$modelValue=this.$viewValue=Number.NaN;this.$parsers=[];this.$formatters=[];this.$viewChangeListeners=[];this.$pristine=!0;this.$dirty=!1;this.$valid=!0;this.$invalid=!1;this.$name=d.name;var f=g(d.ngModel),j=f.assign;if(!j)throw Error(Eb+d.ngModel+" ("+qa(e)+")");this.$render=w;var i=e.inheritedData("$formController")||Na,k=0,m=this.$error={};e.addClass(Oa);h(!0);this.$setValidity=function(a,
c){if(m[a]!==!c){if(c){if(m[a]&&k--,!k)h(!0),this.$valid=!0,this.$invalid=!1}else h(!1),this.$invalid=!0,this.$valid=!1,k++;m[a]=!c;h(c,a);i.$setValidity(a,c,this)}};this.$setViewValue=function(d){this.$viewValue=d;if(this.$pristine)this.$dirty=!0,this.$pristine=!1,e.removeClass(Oa).addClass(Zb),i.$setDirty();n(this.$parsers,function(a){d=a(d)});if(this.$modelValue!==d)this.$modelValue=d,j(a,d),n(this.$viewChangeListeners,function(a){try{a()}catch(d){c(d)}})};var l=this;a.$watch(function(){var c=
f(a);if(l.$modelValue!==c){var d=l.$formatters,e=d.length;for(l.$modelValue=c;e--;)c=d[e](c);if(l.$viewValue!==c)l.$viewValue=c,l.$render()}})}],qd=function(){return{require:["ngModel","^?form"],controller:pd,link:function(a,c,d,e){var g=e[0],h=e[1]||Na;h.$addControl(g);c.bind("$destroy",function(){h.$removeControl(g)})}}},rd=I({require:"ngModel",link:function(a,c,d,e){e.$viewChangeListeners.push(function(){a.$eval(d.ngChange)})}}),dc=function(){return{require:"?ngModel",link:function(a,c,d,e){if(e){d.required=
!0;var g=function(a){if(d.required&&(U(a)||a===!1))e.$setValidity("required",!1);else return e.$setValidity("required",!0),a};e.$formatters.push(g);e.$parsers.unshift(g);d.$observe("required",function(){g(e.$viewValue)})}}}},sd=function(){return{require:"ngModel",link:function(a,c,d,e){var g=(a=/\/(.*)\//.exec(d.ngList))&&RegExp(a[1])||d.ngList||",";e.$parsers.push(function(a){var c=[];a&&n(a.split(g),function(a){a&&c.push(O(a))});return c});e.$formatters.push(function(a){return E(a)?a.join(", "):
q})}}},td=/^(true|false|\d+)$/,ud=function(){return{priority:100,compile:function(a,c){return td.test(c.ngValue)?function(a,c,g){g.$set("value",a.$eval(g.ngValue))}:function(a,c,g){a.$watch(g.ngValue,function(a){g.$set("value",a,!1)})}}}},vd=R(function(a,c,d){c.addClass("ng-binding").data("$binding",d.ngBind);a.$watch(d.ngBind,function(a){c.text(a==q?"":a)})}),wd=["$interpolate",function(a){return function(c,d,e){c=a(d.attr(e.$attr.ngBindTemplate));d.addClass("ng-binding").data("$binding",c);e.$observe("ngBindTemplate",
function(a){d.text(a)})}}],xd=[function(){return function(a,c,d){c.addClass("ng-binding").data("$binding",d.ngBindHtmlUnsafe);a.$watch(d.ngBindHtmlUnsafe,function(a){c.html(a||"")})}}],yd=lb("",!0),zd=lb("Odd",0),Ad=lb("Even",1),Bd=R({compile:function(a,c){c.$set("ngCloak",q);a.removeClass("ng-cloak")}}),Cd=[function(){return{scope:!0,controller:"@"}}],Dd=["$sniffer",function(a){return{priority:1E3,compile:function(){a.csp=!0}}}],ec={};n("click dblclick mousedown mouseup mouseover mouseout mousemove mouseenter mouseleave".split(" "),
function(a){var c=ea("ng-"+a);ec[c]=["$parse",function(d){return function(e,g,h){var f=d(h[c]);g.bind(A(a),function(a){e.$apply(function(){f(e,{$event:a})})})}}]});var Ed=R(function(a,c,d){c.bind("submit",function(){a.$apply(d.ngSubmit)})}),Fd=["$http","$templateCache","$anchorScroll","$compile",function(a,c,d,e){return{restrict:"ECA",terminal:!0,compile:function(g,h){var f=h.ngInclude||h.src,j=h.onload||"",i=h.autoscroll;return function(g,h){var l=0,n,o=function(){n&&(n.$destroy(),n=null);h.html("")};
g.$watch(f,function(f){var s=++l;f?a.get(f,{cache:c}).success(function(a){s===l&&(n&&n.$destroy(),n=g.$new(),h.html(a),e(h.contents())(n),y(i)&&(!i||g.$eval(i))&&d(),n.$emit("$includeContentLoaded"),g.$eval(j))}).error(function(){s===l&&o()}):o()})}}}}],Gd=R({compile:function(){return{pre:function(a,c,d){a.$eval(d.ngInit)}}}}),Hd=R({terminal:!0,priority:1E3}),Id=["$locale","$interpolate",function(a,c){var d=/{}/g;return{restrict:"EA",link:function(e,g,h){var f=h.count,j=g.attr(h.$attr.when),i=h.offset||
0,k=e.$eval(j),m={},l=c.startSymbol(),t=c.endSymbol();n(k,function(a,e){m[e]=c(a.replace(d,l+f+"-"+i+t))});e.$watch(function(){var c=parseFloat(e.$eval(f));return isNaN(c)?"":(k[c]||(c=a.pluralCat(c-i)),m[c](e,g,!0))},function(a){g.text(a)})}}}],Jd=R({transclude:"element",priority:1E3,terminal:!0,compile:function(a,c,d){return function(a,c,h){var f=h.ngRepeat,h=f.match(/^\s*(.+)\s+in\s+(.*)\s*$/),j,i,k;if(!h)throw Error("Expected ngRepeat in form of '_item_ in _collection_' but got '"+f+"'.");f=h[1];
j=h[2];h=f.match(/^(?:([\$\w]+)|\(([\$\w]+)\s*,\s*([\$\w]+)\))$/);if(!h)throw Error("'item' in 'item in collection' should be identifier or (key, value) but got '"+f+"'.");i=h[3]||h[1];k=h[2];var m=new fb;a.$watch(function(a){var e,f,h=a.$eval(j),n=c,q=new fb,y,z,u,x,r,v;if(E(h))r=h||[];else{r=[];for(u in h)h.hasOwnProperty(u)&&u.charAt(0)!="$"&&r.push(u);r.sort()}y=r.length-1;e=0;for(f=r.length;e<f;e++){u=h===r?e:r[e];x=h[u];if(v=m.shift(x)){z=v.scope;q.push(x,v);if(e!==v.index)v.index=e,n.after(v.element);
n=v.element}else z=a.$new();z[i]=x;k&&(z[k]=u);z.$index=e;z.$first=e===0;z.$last=e===y;z.$middle=!(z.$first||z.$last);v||d(z,function(a){n.after(a);v={scope:z,element:n=a,index:e};q.push(x,v)})}for(u in m)if(m.hasOwnProperty(u))for(r=m[u];r.length;)x=r.pop(),x.element.remove(),x.scope.$destroy();m=q})}}}),Kd=R(function(a,c,d){a.$watch(d.ngShow,function(a){c.css("display",Va(a)?"":"none")})}),Ld=R(function(a,c,d){a.$watch(d.ngHide,function(a){c.css("display",Va(a)?"none":"")})}),Md=R(function(a,c,
d){a.$watch(d.ngStyle,function(a,d){d&&a!==d&&n(d,function(a,d){c.css(d,"")});a&&c.css(a)},!0)}),Nd=I({restrict:"EA",require:"ngSwitch",controller:["$scope",function(){this.cases={}}],link:function(a,c,d,e){var g,h,f;a.$watch(d.ngSwitch||d.on,function(j){h&&(f.$destroy(),h.remove(),h=f=null);if(g=e.cases["!"+j]||e.cases["?"])a.$eval(d.change),f=a.$new(),g(f,function(a){h=a;c.append(a)})})}}),Od=R({transclude:"element",priority:500,require:"^ngSwitch",compile:function(a,c,d){return function(a,g,h,
f){f.cases["!"+c.ngSwitchWhen]=d}}}),Pd=R({transclude:"element",priority:500,require:"^ngSwitch",compile:function(a,c,d){return function(a,c,h,f){f.cases["?"]=d}}}),Qd=R({controller:["$transclude","$element",function(a,c){a(function(a){c.append(a)})}]}),Rd=["$http","$templateCache","$route","$anchorScroll","$compile","$controller",function(a,c,d,e,g,h){return{restrict:"ECA",terminal:!0,link:function(a,c,i){function k(){var i=d.current&&d.current.locals,k=i&&i.$template;if(k){c.html(k);m&&(m.$destroy(),
m=null);var k=g(c.contents()),n=d.current;m=n.scope=a.$new();if(n.controller)i.$scope=m,i=h(n.controller,i),c.children().data("$ngControllerController",i);k(m);m.$emit("$viewContentLoaded");m.$eval(l);e()}else c.html(""),m&&(m.$destroy(),m=null)}var m,l=i.onload||"";a.$on("$routeChangeSuccess",k);k()}}}],Sd=["$templateCache",function(a){return{restrict:"E",terminal:!0,compile:function(c,d){d.type=="text/ng-template"&&a.put(d.id,c[0].text)}}}],Td=I({terminal:!0}),Ud=["$compile","$parse",function(a,
c){var d=/^\s*(.*?)(?:\s+as\s+(.*?))?(?:\s+group\s+by\s+(.*))?\s+for\s+(?:([\$\w][\$\w\d]*)|(?:\(\s*([\$\w][\$\w\d]*)\s*,\s*([\$\w][\$\w\d]*)\s*\)))\s+in\s+(.*)$/,e={$setViewValue:w};return{restrict:"E",require:["select","?ngModel"],controller:["$element","$scope","$attrs",function(a,c,d){var j=this,i={},k=e,m;j.databound=d.ngModel;j.init=function(a,c,d){k=a;m=d};j.addOption=function(c){i[c]=!0;k.$viewValue==c&&(a.val(c),m.parent()&&m.remove())};j.removeOption=function(a){this.hasOption(a)&&(delete i[a],
k.$viewValue==a&&this.renderUnknownOption(a))};j.renderUnknownOption=function(c){c="? "+fa(c)+" ?";m.val(c);a.prepend(m);a.val(c);m.prop("selected",!0)};j.hasOption=function(a){return i.hasOwnProperty(a)};c.$on("$destroy",function(){j.renderUnknownOption=w})}],link:function(e,h,f,j){function i(a,c,d,e){d.$render=function(){var a=d.$viewValue;e.hasOption(a)?(w.parent()&&w.remove(),c.val(a),a===""&&v.prop("selected",!0)):x(a)&&v?c.val(""):e.renderUnknownOption(a)};c.bind("change",function(){a.$apply(function(){w.parent()&&
w.remove();d.$setViewValue(c.val())})})}function k(a,c,d){var e;d.$render=function(){var a=new Ga(d.$viewValue);n(c.find("option"),function(c){c.selected=y(a.get(c.value))})};a.$watch(function(){ga(e,d.$viewValue)||(e=V(d.$viewValue),d.$render())});c.bind("change",function(){a.$apply(function(){var a=[];n(c.find("option"),function(c){c.selected&&a.push(c.value)});d.$setViewValue(a)})})}function m(e,f,g){function h(){var a={"":[]},c=[""],d,i,p,u,v;p=g.$modelValue;u=t(e)||[];var x=l?nb(u):u,y,w,A;w=
{};v=!1;var B,E;if(o)v=new Ga(p);else if(p===null||s)a[""].push({selected:p===null,id:"",label:""}),v=!0;for(A=0;y=x.length,A<y;A++){w[k]=u[l?w[l]=x[A]:A];d=m(e,w)||"";if(!(i=a[d]))i=a[d]=[],c.push(d);o?d=v.remove(n(e,w))!=q:(d=p===n(e,w),v=v||d);B=j(e,w);B=B===q?"":B;i.push({id:l?x[A]:A,label:B,selected:d})}!o&&!v&&a[""].unshift({id:"?",label:"",selected:!0});w=0;for(x=c.length;w<x;w++){d=c[w];i=a[d];if(r.length<=w)p={element:z.clone().attr("label",d),label:i.label},u=[p],r.push(u),f.append(p.element);
else if(u=r[w],p=u[0],p.label!=d)p.element.attr("label",p.label=d);B=null;A=0;for(y=i.length;A<y;A++)if(d=i[A],v=u[A+1]){B=v.element;if(v.label!==d.label)B.text(v.label=d.label);if(v.id!==d.id)B.val(v.id=d.id);if(v.element.selected!==d.selected)B.prop("selected",v.selected=d.selected)}else d.id===""&&s?E=s:(E=C.clone()).val(d.id).attr("selected",d.selected).text(d.label),u.push({element:E,label:d.label,id:d.id,selected:d.selected}),B?B.after(E):p.element.append(E),B=E;for(A++;u.length>A;)u.pop().element.remove()}for(;r.length>
w;)r.pop()[0].element.remove()}var i;if(!(i=p.match(d)))throw Error("Expected ngOptions in form of '_select_ (as _label_)? for (_key_,)?_value_ in _collection_' but got '"+p+"'.");var j=c(i[2]||i[1]),k=i[4]||i[6],l=i[5],m=c(i[3]||""),n=c(i[2]?i[1]:k),t=c(i[7]),r=[[{element:f,label:""}]];s&&(a(s)(e),s.removeClass("ng-scope"),s.remove());f.html("");f.bind("change",function(){e.$apply(function(){var a,c=t(e)||[],d={},h,i,j,m,p,s;if(o){i=[];m=0;for(s=r.length;m<s;m++){a=r[m];j=1;for(p=a.length;j<p;j++)if((h=
a[j].element)[0].selected)h=h.val(),l&&(d[l]=h),d[k]=c[h],i.push(n(e,d))}}else h=f.val(),h=="?"?i=q:h==""?i=null:(d[k]=c[h],l&&(d[l]=h),i=n(e,d));g.$setViewValue(i)})});g.$render=h;e.$watch(h)}if(j[1]){for(var l=j[0],t=j[1],o=f.multiple,p=f.ngOptions,s=!1,v,C=u(Y.createElement("option")),z=u(Y.createElement("optgroup")),w=C.clone(),j=0,A=h.children(),r=A.length;j<r;j++)if(A[j].value==""){v=s=A.eq(j);break}l.init(t,s,w);if(o&&(f.required||f.ngRequired)){var B=function(a){t.$setValidity("required",
!f.required||a&&a.length);return a};t.$parsers.push(B);t.$formatters.unshift(B);f.$observe("required",function(){B(t.$viewValue)})}p?m(e,h,t):o?k(e,h,t):i(e,h,t,l)}}}}],Vd=["$interpolate",function(a){var c={addOption:w,removeOption:w};return{restrict:"E",priority:100,compile:function(d,e){if(x(e.value)){var g=a(d.text(),!0);g||e.$set("value",d.text())}return function(a,d,e){var i=d.parent(),k=i.data("$selectController")||i.parent().data("$selectController");k&&k.databound?d.prop("selected",!1):k=
c;g?a.$watch(g,function(a,c){e.$set("value",a);a!==c&&k.removeOption(c);k.addOption(a)}):k.addOption(e.value);d.bind("$destroy",function(){k.removeOption(e.value)})}}}}],Wd=I({restrict:"E",terminal:!0});(ca=N.jQuery)?(u=ca,v(ca.fn,{scope:va.scope,controller:va.controller,injector:va.injector,inheritedData:va.inheritedData}),bb("remove",!0),bb("empty"),bb("html")):u=K;Za.element=u;(function(a){v(a,{bootstrap:rb,copy:V,extend:v,equals:ga,element:u,forEach:n,injector:sb,noop:w,bind:Ua,toJson:da,fromJson:pb,
identity:na,isUndefined:x,isDefined:y,isString:B,isFunction:H,isObject:L,isNumber:Ra,isElement:gc,isArray:E,version:id,isDate:oa,lowercase:A,uppercase:ma,callbacks:{counter:0}});ta=lc(N);try{ta("ngLocale")}catch(c){ta("ngLocale",[]).provider("$locale",Zc)}ta("ng",["ngLocale"],["$provide",function(a){a.provider("$compile",Db).directive({a:jd,input:cc,textarea:cc,form:kd,script:Sd,select:Ud,style:Wd,option:Vd,ngBind:vd,ngBindHtmlUnsafe:xd,ngBindTemplate:wd,ngClass:yd,ngClassEven:Ad,ngClassOdd:zd,ngCsp:Dd,
ngCloak:Bd,ngController:Cd,ngForm:ld,ngHide:Ld,ngInclude:Fd,ngInit:Gd,ngNonBindable:Hd,ngPluralize:Id,ngRepeat:Jd,ngShow:Kd,ngSubmit:Ed,ngStyle:Md,ngSwitch:Nd,ngSwitchWhen:Od,ngSwitchDefault:Pd,ngOptions:Td,ngView:Rd,ngTransclude:Qd,ngModel:qd,ngList:sd,ngChange:rd,required:dc,ngRequired:dc,ngValue:ud}).directive(mb).directive(ec);a.provider({$anchorScroll:uc,$browser:wc,$cacheFactory:xc,$controller:Bc,$document:Cc,$exceptionHandler:Dc,$filter:Rb,$interpolate:Ec,$http:Vc,$httpBackend:Wc,$location:Ic,
$log:Jc,$parse:Nc,$route:Qc,$routeParams:Rc,$rootScope:Sc,$q:Oc,$sniffer:Tc,$templateCache:yc,$timeout:$c,$window:Uc})}])})(Za);u(Y).ready(function(){jc(Y,rb)})})(window,document);angular.element(document).find("head").append('<style type="text/css">@charset "UTF-8";[ng\\:cloak],[ng-cloak],[data-ng-cloak],[x-ng-cloak],.ng-cloak,.x-ng-cloak{display:none;}ng\\:form{display:block;}</style>');
// Generated by CoffeeScript 1.6.2
"use strict";
var BrowserDetect, GUID, asciistring, asciistring_lowercase, asciistring_lowercase_nospace, asciistring_no_specials, async_call, async_call_retries, b64_decode_mstyle, b64_encode_mstyle, b64_object_mstyle, b64_uri, b64mstyle, base64_decode, base64_encode, bool_parse, directive_check_slow_timeout, directive_check_timeout, exist, exist_string, exist_truth, g_format_file_size, g_http_error, g_running_local, get_local_time, ismobile, object_b64_mstyle, other_with, pass, pg, print, running_local, safe_b64, set_time_out, start_time, unique_number, uri_b64, warning,
  __slice = [].slice,
  __indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };

g_running_local = null;

directive_check_timeout = 100;

directive_check_slow_timeout = 500;

pg = function(v) {
  var print_key;

  if (exist(v)) {
    if (exist(window.globals[v])) {
      if (typeof console !== "undefined" && console !== null) {
        console.log(v, window.globals[v]);
      }
    } else {
      print_key = function(k) {
        if (String(k).indexOf(v) >= 0) {
          return typeof console !== "undefined" && console !== null ? console.log(v, "->", k, window.globals[k]) : void 0;
        }
      };
      _.each(_.keys(window.globals), print_key);
    }
  } else {
    print_key = function(k) {
      return typeof console !== "undefined" && console !== null ? console.log(k, window.globals[k]) : void 0;
    };
    _.each(_.keys(window.globals), print_key);
  }
  return "";
};

set_time_out = function(func, delay) {
  return setTimeout(func, delay);
};

async_call = function(func) {
  return setTimeout(func, directive_check_timeout);
};

if (window.btoa != null) {
  base64_encode = window.btoa;
} else {
  base64_encode = window.base64.encode;
}

if (window.atob != null) {
  base64_decode = window.atob;
} else {
  base64_decode = window.base64.decode;
}

if (!String.prototype.trim) {
  String.prototype.trim = function() {
    return this.replace(/^\s+|\s+$/g, "");
  };
}

String.prototype.startsWith = function(suffix) {
  return this.indexOf(suffix) === 0;
};

String.prototype.endsWith = function(suffix) {
  return this.indexOf(suffix, this.length - suffix.length) !== -1;
};

uri_b64 = function(s) {
  s = encodeURI(s);
  return base64_encode(s);
};

safe_b64 = function(s) {
  s = encodeURI(s);
  s = base64_encode(s);
  s = s.replace(/\=/g, "-");
  return s;
};

exist_string = function(value) {
  if (value != null) {
    switch (value) {
      case void 0:
      case null:
      case "null":
      case "undefined":
        return false;
      default:
        return true;
    }
  } else {
    return false;
  }
};

exist = function(value) {
  if (exist_string(value)) {
    if (value === "") {
      return false;
    }
    if (String(value) === "NaN") {
      return false;
    }
    if (String(value) === "undefined") {
      return false;
    }
    if (value.trim != null) {
      if (value.trim() === "") {
        return false;
      }
    }
    return true;
  } else {
    return false;
  }
};

exist_truth = function(value) {
  if (exist(value)) {
    switch (value) {
      case "0":
      case 0:
        return false;
      case "1":
      case 1:
        return true;
      case "false":
      case false:
        return false;
      case "true":
      case true:
        return true;
      default:
        warning("app_basic.cf:103", "exist_truth neither true or false", value);
        return false;
    }
  } else {
    return false;
  }
};

b64mstyle = "data:b64encode/mstyle,";

b64_encode_mstyle = function(s) {
  if (!exist(s)) {
    return s;
  }
  if (!exist(s.indexOf)) {
    return s;
  }
  if (s.indexOf(b64mstyle) === 0) {
    return s;
  }
  s = encodeURIComponent(s);
  s = base64_encode(s);
  s = s.replace(/\=/g, "-");
  return b64mstyle + s;
};

b64_decode_mstyle = function(s) {
  var error;

  if (!exist(s)) {
    return s;
  }
  if (!exist(s.indexOf)) {
    return s;
  }
  if (s.indexOf(b64mstyle) !== 0) {
    return s;
  }
  s = s.replace(b64mstyle, "");
  s = s.replace(/-/g, "=");
  s = base64_decode(s);
  try {
    s = decodeURIComponent(s);
  } catch (_error) {
    error = _error;
    s = "error decoding";
  }
  return s;
};

object_b64_mstyle = function(v) {
  var set_var;

  set_var = function(k) {
    return v[k] = object_b64_mstyle(v[k]);
  };
  if (_.isObject(v)) {
    _.each(_.keys(v), set_var);
    return v;
  } else {
    v = b64_encode_mstyle(v);
    return v;
  }
};

b64_object_mstyle = function(v) {
  var set_var;

  set_var = function(k) {
    return v[k] = b64_object_mstyle(v[k]);
  };
  if (_.isObject(v)) {
    _.each(_.keys(v), set_var);
    return v;
  } else {
    v = b64_decode_mstyle(v);
    return v;
  }
};

b64_uri = function(s) {
  s = base64_decode(s);
  return decodeURI(s);
};

pass = true;

asciistring = function(s) {
  var ns, testchar;

  ns = "";
  testchar = function(c) {
    var code;

    code = c.charCodeAt(0);
    switch (true) {
      case code >= 48 && code <= 57:
        return ns += c;
      case code >= 65 && code <= 90:
        return ns += c;
      case code >= 97 && code <= 122:
        return ns += c;
      case code === 32:
        return ns += c;
      case code === 45:
        return ns += c;
      case code === 38:
        return ns += c;
      case code === 47:
        return ns += c;
      case code === 43:
        return ns += c;
      default:
        return pass;
    }
  };
  _.each(s, testchar);
  return ns;
};

asciistring_no_specials = function(s) {
  var ns, testchar;

  ns = "";
  testchar = function(c) {
    var code;

    code = c.charCodeAt(0);
    switch (true) {
      case code >= 48 && code <= 57:
        return ns += c;
      case code >= 65 && code <= 90:
        return ns += c;
      case code >= 97 && code <= 122:
        return ns += c;
      case code === 32:
        return ns += c;
      case code === 45:
        return ns += c;
      case code === 38:
        return ns += c;
      case code === 43:
        return ns += c;
      case code === 214:
        return ns += "O";
      case code === 214:
        return ns += "O";
      case code === 246:
        return ns += "o";
      case code === 47:
        return ns += c;
      case code === 8364:
        return ns += "EUR ";
      default:
        return ns += "";
    }
  };
  _.each(s, testchar);
  if (ns != null) {
    return ns;
  } else {
    return "";
  }
};

asciistring_lowercase = function(s) {
  var ns;

  ns = "";
  s = s.toLowerCase();
  return asciistring(s);
};

asciistring_lowercase_nospace = function(s) {
  var ns, stripspace;

  s = asciistring_no_specials(s);
  ns = "";
  stripspace = function(i) {
    if (i !== ' ') {
      return ns += i;
    }
  };
  _.each(s, stripspace);
  return ns;
};

g_format_file_size = function(bytes) {
  if (bytes === 0) {
    return "-";
  }
  if (typeof bytes !== "number") {
    return "";
  }
  if (bytes >= (1024 * 1024 * 1024)) {
    return (bytes / (1024 * 1024 * 1024)).toFixed(2) + " gb";
  }
  if (bytes >= (1024 * 1024)) {
    return (bytes / (1024 * 1024)).toFixed(2) + " mb";
  }
  if (bytes >= 1024) {
    return (bytes / 1024).toFixed(2) + " kb";
  }
  return bytes.toFixed(0) + " b.";
};

GUID = function() {
  var S4;

  S4 = function() {
    return Math.floor(Math.random() * 0x10000).toString(16);
  };
  return S4() + S4() + "-" + S4() + "-" + S4() + "-" + S4() + "-" + S4() + S4() + S4();
};

get_local_time = function() {
  return new Date().getTime();
};

unique_number = function() {
  if (running_local) {
    return new Date().getTime();
  } else {
    return 7;
  }
};

window.cvar_show_debug_info = false;

other_with = {};

window.g_logfile = [];

start_time = get_local_time();

print = function() {
  var cnt, coffee2cf, create_print_string, found_object, loop_others, msg, num_objects, obj, others, others2, others_length, print_str, shortdate, spaces, _base, _base1;

  msg = arguments[0], others = 2 <= arguments.length ? __slice.call(arguments, 1) : [];
  if (exist(window.globals["g_browser"])) {
    if (window.globals["g_browser"].browser === 'Chrome') {
      switch (_.size(others)) {
        case 0:
          if (typeof console !== "undefined" && console !== null) {
            console.log("%c" + msg, 'color: crimson', others);
          }
          break;
        case 1:
          if (typeof console !== "undefined" && console !== null) {
            console.log("%c" + msg, 'color: crimson', others[0]);
          }
          break;
        case 2:
          if ((typeof (_base = others[0]).indexOf === "function" ? _base.indexOf(".cf") : void 0) > 0) {
            if (typeof console !== "undefined" && console !== null) {
              console.log("%c" + msg + " " + others[0], 'color: crimson', others[1]);
            }
          } else {
            if (typeof console !== "undefined" && console !== null) {
              console.log("%c" + msg, 'color: crimson', others[0], others[1]);
            }
          }
          break;
        case 3:
          if ((typeof (_base1 = others[0]).indexOf === "function" ? _base1.indexOf(".cf") : void 0) > 0) {
            if (typeof console !== "undefined" && console !== null) {
              console.log("%c" + msg + " " + others[0], 'color: crimson', others[1], others[2]);
            }
          } else {
            if (typeof console !== "undefined" && console !== null) {
              console.log("%c" + msg, 'color: crimson', others[0], others[1], others[2]);
            }
          }
          break;
        case 4:
          if (typeof console !== "undefined" && console !== null) {
            console.log("%c" + msg, 'color: crimson', others[0], others[1], others[2], others[3]);
          }
          break;
        default:
          if (typeof console !== "undefined" && console !== null) {
            console.log(others, msg);
          }
      }
    } else {
      switch (_.size(others)) {
        case 0:
          if (typeof console !== "undefined" && console !== null) {
            console.log(msg);
          }
          break;
        case 1:
          if (typeof console !== "undefined" && console !== null) {
            console.log(msg + " " + others[0]);
          }
          break;
        case 2:
          if (typeof console !== "undefined" && console !== null) {
            console.log(msg + " " + others[0] + " " + others[1]);
          }
          break;
        case 3:
          if (typeof console !== "undefined" && console !== null) {
            console.log(msg + " " + others[0] + " " + others[1] + " " + others[2]);
          }
          break;
        case 4:
          if (typeof console !== "undefined" && console !== null) {
            console.log(msg + " " + others[0] + " " + others[1] + " " + others[2] + " " + others[3]);
          }
          break;
        default:
          if (typeof console !== "undefined" && console !== null) {
            console.log(others, msg);
          }
      }
    }
  } else {
    if (typeof console !== "undefined" && console !== null) {
      console.log(msg, others);
    }
  }
  if (!exist_truth(window.cvar_show_debug_info)) {
    return;
  }
  if (msg.replace != null) {
    shortdate = "" + (get_local_time() - start_time) / 1000;
    while (shortdate.length < 6) {
      shortdate += " ";
    }
    shortdate += " ";
    while (msg.length < 22) {
      msg += " ";
    }
    msg = shortdate + msg;
    others2 = [];
    coffee2cf = function(obj) {
      if (obj != null) {
        if (obj.replace != null) {
          return obj.replace(".cf", ".cf");
        }
      }
      return obj;
    };
    others = (function() {
      var _i, _len, _results;

      _results = [];
      for (_i = 0, _len = others.length; _i < _len; _i++) {
        obj = others[_i];
        _results.push(coffee2cf(obj));
      }
      return _results;
    })();
    others_length = others.length;
    if (others != null) {
      cnt = 0;
      loop_others = function(i) {
        var l;

        if (exist(i)) {
          l = i.length;
        } else {
          l = "undefined".length;
        }
        if (other_with[cnt] != null) {
          if (other_with[cnt] < l) {
            other_with[cnt] = l + 2;
          }
        } else {
          other_with[cnt] = l + 2;
        }
        return cnt += 1;
      };
      _.each(others, loop_others);
      print_str = "";
      cnt = 0;
      spaces = function(n) {
        var c, s;

        c = 0;
        s = " ";
        while (c < n) {
          s += " ";
          c += 1;
        }
        return s;
      };
      found_object = -1;
      num_objects = 0;
      create_print_string = function(s) {
        if (_.isObject(s)) {
          found_object = cnt;
          num_objects += 1;
        } else {
          if (exist(s)) {
            print_str += s + spaces(other_with[cnt] - s.length);
          } else {
            print_str += s + " ";
          }
        }
        return cnt += 1;
      };
      _.each(others, create_print_string);
      if (found_object !== -1) {
        if (num_objects > 1) {
          window.g_logfile.push(msg);
        } else {
          window.g_logfile.push(msg + " " + print_str + " " + others[found_object]);
        }
      } else {
        window.g_logfile.push(msg + " " + print_str);
      }
    } else {
      window.g_logfile.push(msg + " " + String(others));
    }
    window.g_logfile = window.g_logfile.slice(_.size(window.g_logfile) - 150);
    return 1;
  }
};

warning = function() {
  var msg, others;

  msg = arguments[0], others = 2 <= arguments.length ? __slice.call(arguments, 1) : [];
  if (typeof console !== "undefined" && console !== null) {
    console.log('%c------ important ' + msg + ' ---------', 'color: red');
  }
  switch (_.size(others)) {
    case 0:
      if (typeof console !== "undefined" && console !== null) {
        console.log(others);
      }
      break;
    case 1:
      if (typeof console !== "undefined" && console !== null) {
        console.log(others[0], "\t\t");
      }
      break;
    case 2:
      if (typeof console !== "undefined" && console !== null) {
        console.log(others[0], others[1], "\t\t");
      }
      break;
    case 3:
      if (typeof console !== "undefined" && console !== null) {
        console.log(others[0], others[1], others[2], "\t\t");
      }
      break;
    case 4:
      if (typeof console !== "undefined" && console !== null) {
        console.log(others[0], others[1], others[2], others[3], "\t\t");
      }
      break;
    default:
      if (typeof console !== "undefined" && console !== null) {
        console.log(others);
      }
  }
  return typeof console !== "undefined" && console !== null ? console.log('%c------------------------------------------------', 'color: red') : void 0;
};

async_call_retries = function(msg, func, retries) {
  if (retries > 20) {
    print("app_basic.cf:451", msg, "async_call_retries slow");
    return setTimeout(func, directive_check_slow_timeout);
  } else {
    return setTimeout(func, directive_check_timeout);
  }
};

running_local = function() {
  var path_split;

  if (g_running_local != null) {
    return g_running_local;
  } else {
    path_split = document.location.hostname;
    if (path_split === "127.0.0.1" || path_split === "192.168.14.107") {
      print("app_basic.cf:464", "running local");
      return g_running_local = true;
    } else {
      return g_running_local = false;
    }
  }
};

g_http_error = function(data) {
  var traceback;

  if (data.indexOf == null) {
    if (data.data != null) {
      if (data.data.indexOf != null) {
        data = data.data;
      }
    }
  }
  if (data.indexOf != null) {
    traceback = data.slice(data.indexOf("Exception Type:"), data.indexOf("FILES:"));
    if (exist(traceback)) {
      warning("app_basic.cf:480", " **  django error  ** ", traceback);
      window.g_logfile.push(traceback);
    }
  } else {
    traceback = data;
    window.g_logfile.push(traceback);
    print("app_basic.cf:485", data);
  }
  return traceback;
};

ismobile = function() {
  if (navigator.userAgent.match(/Android/i) || navigator.userAgent.match(/webOS/i) || navigator.userAgent.match(/iPhone/i) || navigator.userAgent.match(/iPad/i) || navigator.userAgent.match(/iPod/i) || navigator.userAgent.match(/BlackBerry/i) || navigator.userAgent.match(/Windows Phone/i)) {
    return true;
  } else {
    return false;
  }
};

BrowserDetect = {
  init: function() {
    this.browser = this.searchString(this.dataBrowser) || "An unknown browser";
    this.version = this.searchVersion(navigator.userAgent) || this.searchVersion(navigator.appVersion) || "an unknown version";
    return this.OS = this.searchString(this.dataOS) || "an unknown OS";
  },
  searchString: function(data) {
    var dataProp, dataString, i;

    i = 0;
    while (i < data.length) {
      dataString = data[i].string;
      dataProp = data[i].prop;
      this.versionSearchString = data[i].versionSearch || data[i].identity;
      if (dataString) {
        if (dataString.indexOf(data[i].subString) !== -1) {
          return data[i].identity;
        }
      } else {
        if (dataProp) {
          return data[i].identity;
        }
      }
      i += 1;
    }
  },
  searchVersion: function(dataString) {
    var index;

    index = dataString.indexOf(this.versionSearchString);
    if (index === -1) {
      return;
    }
    return parseFloat(dataString.substring(index + this.versionSearchString.length + 1));
  },
  dataBrowser: [
    {
      string: navigator.userAgent,
      subString: "Chrome",
      identity: "Chrome"
    }, {
      string: navigator.userAgent,
      subString: "OmniWeb",
      versionSearch: "OmniWeb/",
      identity: "OmniWeb"
    }, {
      string: navigator.vendor,
      subString: "Apple",
      identity: "Safari",
      versionSearch: "Version"
    }, {
      prop: window.opera,
      identity: "Opera",
      versionSearch: "Version"
    }, {
      string: navigator.vendor,
      subString: "iCab",
      identity: "iCab"
    }, {
      string: navigator.vendor,
      subString: "KDE",
      identity: "Konqueror"
    }, {
      string: navigator.userAgent,
      subString: "Firefox",
      identity: "Firefox"
    }, {
      string: navigator.vendor,
      subString: "Camino",
      identity: "Camino"
    }, {
      string: navigator.userAgent,
      subString: "Netscape",
      identity: "Netscape"
    }, {
      string: navigator.userAgent,
      subString: "MSIE",
      identity: "Explorer",
      versionSearch: "MSIE"
    }, {
      string: navigator.userAgent,
      subString: "Gecko",
      identity: "Mozilla",
      versionSearch: "rv"
    }, {
      string: navigator.userAgent,
      subString: "Mozilla",
      identity: "Netscape",
      versionSearch: "Mozilla"
    }
  ],
  dataOS: [
    {
      string: navigator.platform,
      subString: "Win",
      identity: "Windows"
    }, {
      string: navigator.platform,
      subString: "Mac",
      identity: "Mac"
    }, {
      string: navigator.userAgent,
      subString: "iPhone",
      identity: "iPhone/iPod"
    }, {
      string: navigator.platform,
      subString: "Linux",
      identity: "Linux"
    }
  ]
};

bool_parse = function(bs) {
  if (bs === "true") {
    return true;
  } else if (bs === "false") {
    return false;
  } else {
    return bs;
  }
};

angular.module("cryptoboxApp.base", []).factory("memory", function($q) {
  var _set;

  window.globals = {};
  window.globals["g_first_tree_render"] = true;
  _set = function(key, value) {
    var error, kv;

    if (key.indexOf("cvar_") === 0) {
      key = key.replace("cvar_", "g_cvar_");
    }
    if (key.indexOf("c_") === 0) {
      key = key.replace("c_", "g_c_");
    }
    kv = key + ":" + value;
    if (key.indexOf("g_") === 0) {
      window.globals[key] = value;
      return;
    }
    error = "not g_" + key;
    print("app_basic.cf:630", error);
    return warning("app_basic.cf:631", error);
  };
  return {
    set: function(key, value) {
      if (!exist(key)) {
        warning("app_basic.cf:635", "no key given");
      }
      if (!exist(value)) {
        if (typeof console !== "undefined" && console !== null) {
          console.log("(no value) -> " + key);
        }
        value = "";
      }
      return _set(key, value);
    },
    set_if_higher: function(key, value) {
      var cv;

      cv = this.get(key);
      value = parseFloat(value);
      if (isNaN(value)) {
        throw "not a number";
      }
      if (exist(cv)) {
        if (cv < value) {
          return this.set(key, value);
        }
      } else {
        return this.set(key, value);
      }
    },
    critical_set: function(key, value) {
      if (!exist(key)) {
        warning("app_basic.cf:655", "no key given");
      }
      if (!exist(value)) {
        throw new Error("critical set undefined value for key " + key);
      }
      return _set(key, value);
    },
    set_no_warning: function(key, value) {
      return _set(key, value);
    },
    all_prefix: function(key_prefix) {
      var check, keys, result;

      keys = _.keys(window.globals);
      check = function(val) {
        var v;

        if (val.indexOf("g_cvar_") === 0) {
          v = val.replace("g_cvar_", "cvar_");
          if (v.indexOf(key_prefix) === 0) {
            return v;
          }
        }
        if (val.indexOf(key_prefix) === 0) {
          return val;
        }
      };
      result = _.filter(_.map(keys, check), function(val) {
        return val != null;
      });
      return result;
    },
    prefix: function(kp) {
      return this.all_prefix(kp);
    },
    del_prefix: function(kp) {
      var del_cache,
        _this = this;

      del_cache = function(key) {
        return _this.del(key);
      };
      return _.each(this.all_prefix(kp), del_cache);
    },
    exist: function(key) {
      if (!exist(key)) {
        return false;
      }
      if (!exist(this.get(key))) {
        return false;
      }
      return true;
    },
    has: function(key) {
      return this.exist(key);
    },
    get: function(key) {
      var error, value;

      if (!exist(key)) {
        warning("app_basic.cf:699", "no key given");
      }
      if (key.indexOf("cvar_") === 0) {
        key = key.replace("cvar_", "g_cvar_");
      }
      if (key.indexOf("c_") === 0) {
        key = key.replace("c_", "g_c_");
      }
      if (key.indexOf("g_") === 0) {
        value = window.globals[key];
        return bool_parse(value);
      }
      error = "globals should start with g_ ->" + key;
      print("app_basic.cf:709", error);
      return warning("app_basic.cf:710", error);
    },
    get_int: function(key) {
      var val;

      val = this.get(key);
      return parseInt(val, 10);
    },
    get_float: function(key) {
      var val;

      val = this.get(key);
      return parseFloat(val);
    },
    set_one_read_value: function(key) {
      _set(key, true);
      return true;
    },
    get_one_read_value: function(key) {
      var val;

      val = this.get(key);
      this.del(key);
      if (exist(val)) {
        return true;
      }
      return false;
    },
    get_promise: function(key) {
      var p, val;

      p = $q.defer();
      val = this.get(key);
      if (val != null) {
        p.resolve(val);
      } else {
        p.reject();
      }
      return p.promise;
    },
    del: function(key) {
      var error;

      if (key.indexOf("cvar_") === 0) {
        key = key.replace("cvar_", "g_cvar_");
      }
      if (key.indexOf("c_") === 0) {
        key = key.replace("c_", "g_c_");
      }
      if (key.indexOf("g_") === 0) {
        delete window.globals[key];
        return;
      }
      error = "globals should start with g_ (global) - " + key;
      print("app_basic.cf:751", key, "no g_ prefix");
      return warning("app_basic.cf:752", error);
    },
    reset: function() {
      var cookie_key, keep, key, _i, _len, _ref, _results;

      _ref = _.keys(window.globals);
      _results = [];
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        key = _ref[_i];
        keep = false;
        if (key.indexOf("g_service") === 0) {
          print("app_basic.cf:759", "stopping", key);
          clearInterval(window.globals[key]);
        }
        cookie_key = key;
        if (cookie_key.indexOf("g_c_") === 0) {
          cookie_key = cookie_key.replace("g_c_", "c_");
        }
        if (cookie_key.indexOf("c_") === 0) {
          if (cookie_key.indexOf("c_persist_") === 0) {
            keep = true;
          }
          if (cookie_key.indexOf("c_const_persist_") === 0) {
            keep = true;
          }
        }
        if (key.indexOf("g_persist_") === 0) {
          keep = true;
        }
        if (!keep) {
          _results.push(this.del(key));
        } else {
          _results.push(void 0);
        }
      }
      return _results;
    },
    bool_test: function(key) {
      var val;

      val = this.get(key);
      if (!exist(val)) {
        this.set(key, false);
        val = false;
      }
      if (String(val) !== "true" && String(val) !== "false") {
        throw new Error("not a boolean");
      }
      return exist_truth(val);
    },
    counter: function(key) {
      if (!exist(this.get("g_counter_" + key))) {
        return this.set("g_counter_" + key, 0);
      }
    },
    reset_counter: function(key) {
      return this.set("g_counter_" + key, 0);
    },
    get_counter: function(key) {
      return this.get("g_counter_" + key);
    },
    mod_counter: function(key, modulus) {
      var imod, ival, val;

      val = this.get("g_counter_" + key);
      ival = parseInt(val, 10);
      imod = parseInt(modulus, 10);
      return (ival % imod) === 0;
    },
    increment_counter: function(key) {
      var val;

      val = this.get("g_counter_" + key);
      if (!exist(val)) {
        val = 0;
      }
      val = parseInt(val, 10);
      val = val + 1;
      this.set("g_counter_" + key, val);
      return val;
    },
    decrement_counter: function(key) {
      var val;

      val = this.get("g_counter_" + key);
      val = parseInt(val, 10);
      val = val - 1;
      this.set("g_counter_" + key, val);
      return val;
    }
  };
}).factory("clientcookies", function(memory, utils) {
  var set_memory, _set;

  this.loaded = false;
  _set = function(key, value) {
    var error;

    if (key === "c_token") {
      warning("app_basic.cf:827", "c_token not allowed");
    }
    if (key === "c_username") {
      warning("app_basic.cf:829", "c_username not allowed");
    }
    if (key.indexOf("c_") === 0) {
      Store.set(key, value);
      return;
    }
    error = "cookies should start with c_";
    print("app_basic.cf:835", error);
    return warning("app_basic.cf:836", error);
  };
  set_memory = function(cookie) {
    if (cookie.key.indexOf("c_") === 0) {
      return memory.set(cookie.key, cookie.val);
    }
  };
  return {
    ensure_memory: function() {
      var cookie_data;

      if (!this.loaded) {
        cookie_data = Store.all();
        _.each(cookie_data, set_memory);
        return this.loaded = true;
      }
    },
    reset: function() {
      var check_delete,
        _this = this;

      check_delete = function(key) {
        var cookie_key, keep;

        keep = false;
        cookie_key = key;
        if (cookie_key.indexOf("g_c_") === 0) {
          cookie_key = cookie_key.replace("g_c_", "c_");
        }
        if (cookie_key.indexOf("c_") === 0) {
          if (cookie_key.indexOf("c_persist_") === 0) {
            keep = true;
          } else if (cookie_key.indexOf("c_const_persist_") === 0) {
            keep = true;
          }
        }
        if (!keep) {
          return _this.del(cookie_key);
        }
      };
      return _.each(_.keys(window.globals), check_delete);
    },
    del: function(key) {
      memory.del(key);
      return Store.del(key);
    },
    set: function(key, value) {
      if (key.indexOf("c_const_") === 0) {
        if (utils.exist(memory.get(key))) {
          print("app_basic.cf:872", key + "is const", value, "ignored");
          return;
        }
      }
      memory.set(key, value);
      return _set(key, value);
    },
    set_no_warning: function(key, value) {
      memory.set(key, value);
      return _set(key, value);
    },
    get: function(key) {
      var error, value;

      if (key === "c_token") {
        warning("app_basic.cf:883", "c_token not allowed");
      }
      if (key === "c_username") {
        warning("app_basic.cf:885", "c_username not allowed");
      }
      if (key.indexOf("c_") !== 0) {
        error = "cookies should start with c_";
        warning("app_basic.cf:888", error);
      }
      value = memory.get(key);
      value = bool_parse(value);
      if (value != null) {
        return value;
      }
      value = Store.get(key);
      if (utils.exist(value)) {
        value = bool_parse(value);
        memory.set(key, value);
        return value;
      }
      return null;
    },
    has: function(key) {
      var v;

      v = this.get(key);
      if (utils.exist(v)) {
        return true;
      }
      return false;
    }
  };
}).factory("utils", function(memory, dateFilter, $templateCache, $q, $http) {
  var init, m_browser, m_os, m_version;

  m_browser = null;
  m_os = null;
  m_version = null;
  init = function() {
    var browser;

    BrowserDetect.init();
    m_browser = BrowserDetect.browser;
    m_version = BrowserDetect.version;
    m_os = BrowserDetect.OS;
    browser = {};
    browser["browser"] = m_browser;
    browser["version"] = m_version;
    browser["os"] = m_os;
    return memory.set("g_browser", browser);
  };
  return {
    chrome: function() {
      if (m_browser === "Chrome") {
        return true;
      }
      return false;
    },
    ie8: function() {
      if (m_browser === "Explorer") {
        if (parseInt(m_version, 10) === 8) {
          return true;
        }
      }
      return false;
    },
    html5: function() {
      var v;

      v = memory.get("g_c_html5mode");
      return bool_parse(v);
    },
    split: function(str, splitter) {
      var s, sp;

      s = String(str);
      sp = s.split(splitter);
      return sp;
    },
    splitlast: function(str, splitter) {
      var s, sp;

      s = String(str);
      sp = s.split(splitter);
      return sp[_.size(sp) - 1];
    },
    bool_parse: function(v) {
      return bool_parse(v);
    },
    text_html: function(str) {
      str = str.trim();
      return String(str).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/\n/g, "<br/>");
    },
    percentage: function(current, range) {
      var perc;

      current = parseFloat(current);
      range = parseFloat(range);
      perc = current / (range / 100);
      if (range === 0) {
        return 0;
      }
      if (perc > 100) {
        perc = 100;
      }
      if (isNaN(perc)) {
        return 0;
      }
      return parseInt(perc, 10);
    },
    full: function(arr) {
      if (_.size(arr) > 0) {
        return true;
      }
      return false;
    },
    empty: function(arr) {
      if (_.size(arr) === 0) {
        return true;
      }
      return false;
    },
    exclude: function(source, exclude) {
      var check, new_array,
        _this = this;

      new_array = [];
      check = function(item) {
        var check2, found;

        found = false;
        check2 = function(item2) {
          var check_key;

          check_key = function(key) {
            if (!_.isObject(item[key])) {
              if (String(item[key]) === String(item2[key])) {
                return found = true;
              }
            }
          };
          return _.each(_.keys(item2), check_key);
        };
        _.each(exclude, check2);
        if (!found) {
          return new_array.push(item);
        }
      };
      _.each(source, check);
      return new_array;
    },
    exclude_key: function(source, exclude, key) {
      var check, new_array;

      new_array = [];
      check = function(item) {
        var check2, found;

        found = false;
        check2 = function(item2) {
          if (String(item[key]) === String(item2[key])) {
            return found = true;
          }
        };
        _.each(exclude, check2);
        if (!found) {
          return new_array.push(item);
        }
      };
      _.each(source, check);
      return new_array;
    },
    exclude_key_key: function(source, exclude, key, key2) {
      var check, new_array;

      new_array = [];
      check = function(item) {
        var check2, found;

        found = false;
        check2 = function(item2) {
          if (String(item[key]) === String(item2[key2])) {
            return found = true;
          }
        };
        _.each(exclude, check2);
        if (!found) {
          return new_array.push(item);
        }
      };
      _.each(source, check);
      return new_array;
    },
    exclude_key_value: function(source, key, value) {
      var check, new_array;

      new_array = [];
      check = function(item) {
        var found;

        found = false;
        if (String(item[key]) === String(value)) {
          found = true;
        }
        if (!found) {
          return new_array.push(item);
        }
      };
      _.each(source, check);
      return new_array;
    },
    filter_key_value: function(source, key, value) {
      var check, new_array,
        _this = this;

      new_array = [];
      check = function(item) {
        var found, tmp;

        found = false;
        if (_.isObject(item)) {
          tmp = _this.filter_key_value(item, key, value);
          if (_.size(tmp) > 0) {
            found = true;
          }
        }
        if (item != null) {
          if (String(item[key]) === String(value)) {
            found = true;
          }
        }
        if (found) {
          return new_array.push(item);
        }
      };
      _.each(source, check);
      return new_array;
    },
    map_to_values: function(source, key) {
      var check, new_array,
        _this = this;

      new_array = [];
      check = function(item) {
        var found;

        found = false;
        if (_.isObject(item[key])) {
          return print("app_basic.cf:1074", _this.map_to_values(item, key));
        } else {
          if (exist(item[[key]])) {
            return new_array.push(item[key]);
          }
        }
      };
      _.each(source, check);
      return new_array;
    },
    unique_object_list: function(source, key) {
      var make_unique, new_array,
        _this = this;

      new_array = [];
      make_unique = function(item) {
        var check, found;

        found = false;
        check = function(item2) {
          if (item2[key] === item[key]) {
            return found = true;
          }
        };
        _.each(new_array, check);
        if (!found) {
          return new_array.push(item);
        }
      };
      _.each(source, make_unique);
      return new_array;
    },
    unique_list: function(source) {
      var make_unique, new_array,
        _this = this;

      new_array = [];
      make_unique = function(item) {
        var check, found;

        found = false;
        check = function(item2) {
          if (item2 === item) {
            return found = true;
          }
        };
        _.each(new_array, check);
        if (!found) {
          return new_array.push(item);
        }
      };
      _.each(source, make_unique);
      return new_array;
    },
    slugify: function(text) {
      text = text.toLowerCase();
      text = text.replace(/[^-a-zA-Z0-9,&\s]+/g, "");
      text = text.replace(/-/g, "_");
      text = text.replace(/\s/g, "_");
      while (text.indexOf("__") > 0) {
        text = text.replace("__", "_");
      }
      return text;
    },
    obj2json: function(obj) {
      return JSON.stringify(obj);
    },
    json2obj: function(json) {
      return JSON.parse(json);
    },
    same_object: function(obj1, obj2) {
      var j1, j2;

      j1 = this.obj2json(obj1);
      j2 = this.obj2json(obj2);
      return j1 === j2;
    },
    b64_encode_mstyle: function(s) {
      return b64_encode_mstyle(s);
    },
    b64_decode_mstyle: function(s) {
      return b64_decode_mstyle(s);
    },
    object_b64_mstyle: function(v) {
      return object_b64_mstyle(v);
    },
    b64_object_mstyle: function(v) {
      return b64_object_mstyle(v);
    },
    b64_uri: function(s) {
      return b64_uri(s);
    },
    asciistring: function(s) {
      return asciistring(s);
    },
    asciistring_no_specials: function(s) {
      return asciistring_no_specials(s);
    },
    asciistring_lowercase: function(s) {
      return asciistring_lowercase(s);
    },
    format_file_size: function(bytes) {
      return g_format_file_size(bytes);
    },
    browser: function() {
      if (!this.exist(m_browser)) {
        init();
      }
      return m_browser;
    },
    is_phone: function() {
      if (memory.has("g_device_type")) {
        if (memory.get("g_device_type") === "phone") {
          return true;
        }
      }
      return false;
    },
    is_tablet: function() {
      if (memory.has("g_device_type")) {
        if (memory.get("g_device_type") === "tablet") {
          return true;
        }
      }
      return false;
    },
    is_desktop: function() {
      if (memory.has("g_device_type")) {
        if (memory.get("g_device_type") === "desktop") {
          return true;
        }
      }
      return false;
    },
    version: function() {
      if (!this.exist(m_version)) {
        init();
      }
      return m_version;
    },
    os: function() {
      if (!this.exist(m_os)) {
        init();
      }
      return m_os;
    },
    smooth_progress_update: function(hard_progress, smooth_progress) {
      var chance;

      if (this.ie8()) {
        return hard_progress;
      }
      if (hard_progress > 50) {
        if (smooth_progress < 20) {
          smooth_progress = 20;
        }
      }
      chance = 4;
      if (smooth_progress > 20) {
        chance = 500;
      }
      if (Math.round(chance * Math.random()) === 2) {
        smooth_progress += 1;
      }
      if (hard_progress > 98) {
        if (smooth_progress > 80) {
          if (hard_progress > 80) {
            smooth_progress += 20 * Math.random();
          } else {
            smooth_progress += 1;
          }
        } else if (smooth_progress > 60) {
          if (hard_progress > 60) {
            smooth_progress += 10 * Math.random();
          } else {
            smooth_progress += 2 * Math.random();
          }
        } else if (smooth_progress > 20) {
          if (hard_progress > 20) {
            smooth_progress += 10 * Math.random();
          } else {
            if (Math.round(chance * Math.random()) === 2) {
              smooth_progress += 10 * Math.random();
            } else {
              smooth_progress += 5 * Math.random();
            }
          }
        } else {
          smooth_progress += 2 * Math.random();
        }
      }
      if (smooth_progress > 100) {
        smooth_progress = 100;
      }
      if (hard_progress !== 100) {
        if (smooth_progress > 95) {
          smooth_progress = 95;
        }
      }
      return smooth_progress;
    },
    mail_admins: function(subject, message) {
      var command, data, p, url;

      p = $q.defer();
      data = {};
      data["subject"] = subject;
      data["message"] = message;
      command = "mailadmins";
      url = "/" + this.get_cryptobox_slug() + "/" + command + "/" + get_local_time();
      data = object_b64_mstyle(data);
      $http.post(url, data).then(function(succes) {
        return p.resolve();
      }, function(e) {
        print("app_basic.cf:1251", "error mailing admins");
        print("app_basic.cf:1252", e);
        return p.resolve();
      });
      return p.promise;
    },
    warning: function() {
      var add_error, add_errors, g_warnings, msg, others, spaces, warning_str, warnings;

      msg = arguments[0], others = 2 <= arguments.length ? __slice.call(arguments, 1) : [];
      warnings = [];
      warnings.push(msg);
      add_error = function(i) {
        return warnings.push(String(i));
      };
      _.each(others, add_error);
      warning("app_basic.cf:1264", msg, others);
      warning_str = "";
      spaces = "";
      add_errors = function(i) {
        warning_str += spaces + i + "\n";
        return spaces += "  ";
      };
      _.each(warnings, add_errors);
      this.mail_admins(this.get_cryptobox_slug() + " - javascript error", warning_str);
      return g_warnings = [];
    },
    digest: function() {
      return memory.critical_set("g_digest_requested", true);
    },
    force_digest: function(scope) {
      var digest,
        _this = this;

      digest = function() {
        if (!scope.$$phase) {
          return scope.$apply();
        }
      };
      return _.defer(digest);
    },
    sanitize_url: function(url) {
      url = "/" + url;
      while (url.indexOf("//") !== -1) {
        url = url.replace("//", "/");
      }
      return url;
    },
    trim_left: function(str, tv) {
      var subs;

      subs = str.substring(0, tv.length);
      if (subs === tv) {
        str = str.substring(tv.length, str.length);
      }
      return str;
    },
    strip_left: function(str, tv) {
      return this.trim_left(str, tv);
    },
    trim_right: function(str, tv) {
      var subs;

      subs = str.substring(str.length - tv.length);
      if (subs === tv) {
        str = str.substring(0, str.length - tv.length);
      }
      return str;
    },
    strip_right: function(str, tv) {
      return this.trim_right(str, tv);
    },
    capfirst: function(s) {
      return s.charAt(0).toUpperCase() + s.toLowerCase().substring(1);
    },
    numbers_only_string: function(v) {
      var i, s, _i, _len, _ref;

      if (!exist(v)) {
        v = "";
      }
      v = v.trim();
      if (v === "") {
        return v;
      }
      s = "";
      for (_i = 0, _len = v.length; _i < _len; _i++) {
        i = v[_i];
        if (_ref = parseInt(i, 10), __indexOf.call([0, 1, 2, 3, 4, 5, 6, 7, 8, 9], _ref) >= 0) {
          s += i;
        }
      }
      return s;
    },
    count: function(string, subString, allowOverlapping) {
      var n, pos, step;

      string += "";
      subString += "";
      if (subString.length <= 0) {
        return string.length + 1;
      }
      n = 0;
      pos = 0;
      step = (allowOverlapping ? 1. : subString.length);
      while (true) {
        pos = string.indexOf(subString, pos);
        if (pos >= 0) {
          n++;
          pos += step;
        } else {
          break;
        }
      }
      return n;
    },
    strip_file_extension: function(fname) {
      var cnt_points, extension, i, join_name, new_name, ret, split_name, _i, _ref;

      if (fname.indexOf(".") !== -1) {
        cnt_points = this.count(fname, ".");
        if (cnt_points > 1) {
          for (i = _i = 1, _ref = cnt_points - 1; 1 <= _ref ? _i <= _ref : _i >= _ref; i = 1 <= _ref ? ++_i : --_i) {
            fname = fname.replace(".", "±");
          }
        }
        split_name = fname.split(".");
        extension = split_name[split_name.length - 1];
        if (extension.indexOf(" ") !== -1) {
          return String(fname).trim();
        }
        split_name = split_name.slice(0, split_name.length - 1);
        new_name = "";
        join_name = function(i) {
          return new_name += i;
        };
        _.each(split_name, join_name);
        new_name = new_name.replace(/±/g, ".");
        ret = this.trim_right(new_name, ".");
        if (ret != null) {
          return ret;
        }
        return "";
      }
      return ret = this.trim_right(fname, " ");
    },
    file_extension: function(fname) {
      var cnt_points, extension, i, split_name, _i, _ref;

      if (fname.indexOf(".") !== -1) {
        cnt_points = this.count(fname, ".");
        if (cnt_points > 1) {
          for (i = _i = 1, _ref = cnt_points - 1; 1 <= _ref ? _i <= _ref : _i >= _ref; i = 1 <= _ref ? ++_i : --_i) {
            fname = fname.replace(".", "±");
          }
        }
        split_name = fname.split(".");
        extension = split_name[split_name.length - 1];
        if (extension.indexOf(" ") !== -1) {
          return fname;
        }
        if (_.size(extension) > 0) {
          return String(extension).trim();
        }
      }
      return String(fname).trim();
    },
    is_mobile: function() {
      return /Android|webOS|iPhone|iPad|iPod|BlackBerry/i.test(navigator.userAgent);
    },
    title: function(title) {
      return document.title = this.get_cryptobox_slug() + " | " + title.toLowerCase();
    },
    exist_string: function(value) {
      return exist_string(value);
    },
    exist: function(value) {
      return exist(value);
    },
    assert: function(key, value) {
      if (!this.exist(value)) {
        return warning("app_basic.cf:1408", "value named " + key + " does not exist");
      }
    },
    exist_truth: function(value) {
      return exist_truth(value);
    },
    stripTrailingSlash: function(str) {
      while (str.substr(-1) === "/") {
        str = str.substr(0, str.length - 1);
      }
      return str;
    },
    strEndsWith: function(str, suffix) {
      return str.indexOf(suffix, str.length - suffix.length) !== -1;
    },
    get_cryptobox_slug: function() {
      " parse out the toplevel url, this == the slug ";
      var cryptobox_slug, path_split;

      cryptobox_slug = memory.get("g_cryptobox_slug");
      if (cryptobox_slug) {
        return cryptobox_slug;
      } else {
        path_split = document.location.pathname.split("/");
        cryptobox_slug = path_split[1];
        memory.set("g_cryptobox_slug", cryptobox_slug);
        return cryptobox_slug;
      }
    },
    format_date: function(date) {
      return dateFilter(date, 'EEEE d MMMM y');
    },
    format_time: function(date) {
      return dateFilter(date, 'H:mm:ss');
    },
    format_datetime_medium: function(date) {
      return dateFilter(date, 'd MMM y H:mm');
    },
    format_datetime_long: function(date) {
      return dateFilter(date, 'EEEE d MMMM y H:mm:ss');
    },
    debug_mode: function() {
      var g_debugmode;

      g_debugmode = memory.get("g_debugmode");
      if (!this.exist(g_debugmode)) {
        memory.set("g_debugmode", running_local());
        g_debugmode = memory.get("g_debugmode");
      }
      return g_debugmode;
    },
    remove_cache: function() {
      if (this.debug_mode()) {
        return $templateCache.removeAll();
      }
    },
    sha3: function() {
      var append_data, data, hashdata;

      data = 1 <= arguments.length ? __slice.call(arguments, 0) : [];
      hashdata = "";
      append_data = function(d) {
        hashdata += String(d);
        return hashdata += "+";
      };
      _.each(data, append_data);
      hashdata = this.trim_right(hashdata, "+");
      return CryptoJS.SHA3(hashdata).toString();
    },
    http_get: function(url) {
      var p;

      print("app_basic.cf:1468", "http_get", url);
      p = $q.defer();
      $http.get(url).then(function(result) {
        return p.resolve(result.data);
      }, function(e) {
        return p.reject(g_http_error(e.data));
      });
      return p.promise;
    },
    http_get_cached: function(url) {
      var content, p, url_key;

      print("app_basic.cf:1481", "http_get_cached", url);
      url_key = asciistring_lowercase_nospace(url);
      p = $q.defer();
      content = memory.get("g_http_get_cached_" + url_key);
      if (exist(content)) {
        p.resolve(content);
      } else {
        $http.get(url).then(function(result) {
          memory.set("g_http_get_" + url_key, result.data);
          return p.resolve(result.data);
        }, function(e) {
          return p.reject(g_http_error(e.data));
        });
      }
      return p.promise;
    }
  };
}).factory("urls", function(utils, memory, clientcookies) {
  var _safe;

  _safe = function(parameter) {
    return safe_b64(parameter);
  };
  return {
    http_error: function(data) {
      return g_http_error(data);
    },
    make_route: function(path) {
      var cached_route, cryptobox_slug, new_path;

      cached_route = memory.get("g_" + path);
      if (cached_route != null) {
        return cached_route;
      }
      cryptobox_slug = utils.get_cryptobox_slug();
      if (clientcookies.get("c_html5mode")) {
        new_path = "/" + cryptobox_slug + "/" + path;
      } else {
        new_path = "/" + path;
      }
      new_path = new_path.replace(new RegExp("//", "g"), "/");
      memory.set("g_" + path, new_path);
      return new_path;
    },
    make_absolute_route: function(path) {
      var cached_route, cryptobox_slug, html5_mode, new_path;

      cached_route = memory.get("g_" + path);
      cryptobox_slug = utils.get_cryptobox_slug();
      if (memory.has("g_c_html5mode")) {
        html5_mode = memory.get("g_c_html5mode");
      } else {
        html5_mode = clientcookies.get("c_html5mode");
      }
      if (!html5_mode) {
        new_path = "/" + cryptobox_slug + "#/" + path;
      } else {
        new_path = "/" + cryptobox_slug + "/" + path;
      }
      new_path = new_path.replace(new RegExp("//", "g"), "/");
      memory.set("g_" + path, new_path);
      return new_path;
    },
    change_route: function($location, path, cvar) {
      var safe_path;

      path = utils.stripTrailingSlash(path);
      safe_path = this.make_route(path);
      if (cvar != null) {
        if (path.indexOf("docs/") > 0) {
          if (path.indexOf("add") === -1) {
            cvar.set("cvar_last_path", path);
          }
        }
      }
      if ($location.path() !== safe_path) {
        return $location.path(safe_path);
      }
    },
    change_document_location: function(path) {
      var cryptobox_slug_path, safe_path;

      path = utils.stripTrailingSlash(path);
      safe_path = this.make_route(path);
      cryptobox_slug_path = "/" + utils.get_cryptobox_slug();
      if (clientcookies.get("c_html5mode")) {
        return document.location = safe_path;
      } else {
        return document.location = cryptobox_slug_path + "#" + safe_path;
      }
    },
    safe: function(parameter) {
      return _safe(parameter);
    },
    command: function(msg, command) {
      " format a command url ";
      var url;

      url = "/" + utils.get_cryptobox_slug() + "/" + command + "/" + get_local_time();
      return url;
    },
    postcommand: function(msg, command, operation) {
      " format a command url ";
      var url;

      url = "/" + utils.get_cryptobox_slug() + "/" + command + "/" + get_local_time();
      return url;
    },
    key_value: function(command, key, value) {
      " format a command url ";
      var cryptobox_slug, url;

      get_local_time();
      cryptobox_slug = utils.get_cryptobox_slug();
      if ((cryptobox_slug == null) || cryptobox_slug === "undefined") {
        print("app_basic.cf:1586", "cryptobox slug == undefined");
      }
      url = "/" + cryptobox_slug + "/" + command + "/" + _safe(key) + "/" + _safe(value) + "/" + get_local_time();
      print("app_basic.cf:1589", "urls.key_value", url);
      return url;
    },
    logout: function(http) {
      var login_message, msg_log;

      print("app_basic.cf:1593", "logout");
      login_message = clientcookies.get("c_login_message");
      memory.reset();
      clientcookies.reset();
      if (utils.exist(login_message)) {
        clientcookies.set("c_login_message", login_message);
      }
      if (!running_local()) {
        return this.change_document_location("/logout");
      } else {
        msg_log = function() {
          warning("app_basic.cf:1603", "on the server you would be logged off now");
          if (String(document.location).indexOf("login") < 0) {
            return set_time_out(msg_log, 1000);
          }
        };
        return msg_log();
      }
    }
  };
});

/*
//@ sourceMappingURL=app_basic.map
*/
// Generated by CoffeeScript 1.6.2
var add_menu, add_tray, cryptobox_ctrl, f_exit;

f_exit = function() {
  return Ti.App.exit();
};

add_menu = function() {
  var fileItem, menu;

  menu = Ti.UI.createMenu();
  fileItem = Ti.UI.createMenuItem("File");
  fileItem.addItem("Exit", f_exit);
  menu.appendItem(fileItem);
  return Ti.UI.setMenu(menu);
};

add_tray = function() {
  var programTray, tmenu;

  programTray = Ti.UI.addTray("tray_icon.png");
  tmenu = Ti.UI.createMenu();
  tmenu.addItem("Exit", f_exit);
  return programTray.setMenu(tmenu);
};

add_menu();

add_tray();

angular.module("cryptoboxApp", ["cryptoboxApp.base"]);

cryptobox_ctrl = function($scope, $q) {
  var get_version, run_command;

  run_command = function(cmd_name) {
    var cmd, cmd_output, cmd_process, on_exit, on_failure, p, stdout;

    p = $q.defer();
    cmd = Ti.API.getApplication().getResourcesPath() + "/" + cmd_name;
    cmd_output = Ti.Filesystem.createTempFile();
    cmd_process = Ti.Process.createProcess([cmd], stdout = cmd_output);
    on_exit = function(command) {
      console.log('exiting', command.getTarget().toString().replace(Ti.API.getApplication().getResourcesPath(), ""));
      return p.resolve("succes");
    };
    on_failure = function() {
      return p.reject("timeout occurred");
    };
    set_time_out(on_failure, 5000);
    cmd_process.setOnExit(on_exit);
    cmd_process.launch();
    return p.promise;
  };
  get_version = function() {
    run_command("pyversion").then(function(success) {
      return console.log(success);
    }, function(error) {
      return console.log(error);
    });
    return "version";
  };
  $scope.python_version = get_version();
  $scope.handle_change = function() {
    return $scope.yourName = handle($scope.yourName);
  };
  $scope.file_input_change = function() {
    return py_file_input_change($scope.file_input);
  };
  return $scope.open_dialog = function() {
    var cv_open_save_dialog;

    console.log(get_version());
    return;
    cv_open_save_dialog = function(e) {
      return console.log(e.toString());
    };
    return console.log(Ti.UI.openFolderChooserDialog(cv_open_save_dialog, {
      "title": "Selecteer datamap Cryptobox",
      "path": Ti.Filesystem.getDocumentsDirectory().toString(),
      "default": "Cryptobox"
    }));
  };
};
