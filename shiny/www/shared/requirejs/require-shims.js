// Since HTMLDependency()s are designed to be loaded via a <script> tag,
// we need to avoid anonymous define() calls (which will error out in a script tag)
// https://requirejs.org/docs/errors.html#mismatch
//
// One way to approach this is to lean on the data-requiremodule attribute,
// which requirejs happens to set when it loads scripts in the browser
// https://github.com/requirejs/requirejs/blob/898ff9/require.js#L1897-L1902
const oldDefine = window.define;
window.define = function define(name, deps, callback) {
    if (typeof name !== 'string') {
        callback = deps;
        deps = name;
        name = document.currentScript.getAttribute('data-requiremodule')
    }
    return oldDefine.apply(this, [name, deps, callback]);
}
for(var prop in oldDefine) {
  if (oldDefine.hasOwnProperty(prop)) {
    window.define[prop] = oldDefine[prop];
  }
}
