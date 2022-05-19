// Make Shiny's global dependencies require()-able. A non-trivial amount of Shiny's
// legacy JS code depends on these globals, but it seems reasonable to think other
// downstream code want to require('jquery') (panel_absolute() does that via
// require('jquery-ui')).
define('jquery', [], function() { return jQuery });
define('bootstrap', [], function() { return bootstrap });

// Since HTMLDependency()s are designed to be loaded via a <script> tag, we do our best
// to avoid anonymous define() calls (which will error out in a script tag)
// https://requirejs.org/docs/errors.html#mismatch
//
// One way to approach this is to lean on the data-requiremodule attribute, which
// requirejs happens to set when it loads scripts in the browser
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

// Users can still encounter this anonymous define() error, and we've actually
// encountered this in shiny-server-client.js because we were inlining an internal
// dependency that contained an anonymous define()
// https://github.com/rstudio/shiny-server-client/blob/5ee5aac/dist/shiny-server-client.js#L4271-L4272).
// In this case, it doesn't seem like there is anything we can do to help the situation
// other than to add some more context to the error.
window.requirejs.onError = function(err) {
  if (err.message.includes('Mismatched anonymous define()')) {
    err.message = err.message + '\n\nConsider either adding a data-requiremodule attribute (with the module name) to the <script> tag containing the anonymous define() or removing the anonymous define() altogether.';
  }
  throw err;
}
