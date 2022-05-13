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

// Define a custom loader to get a hook into when requirejs loads a script
// https://requirejs.org/docs/plugins.html#apiload
function shinyRequireLoader(name, req, onload, config) {
    req([name], function(value) {
        onload(value);

        // fire an event to indicate that the module has been loaded
        // this is used by the Shiny server to determine when to
        // send the module to the client
        var event = new CustomEvent('require-module-loaded', {detail: {name: name}});
        window.dispatchEvent(event);
    });
}

define("shinyRequireLoader", {load: shinyRequireLoader});

// Use the custom loader on every async require() call
const oldRequire = window.require;
window.require = function require(deps, callback, errback, optional) {
    if (Array.isArray(deps)) {
        deps = deps.map(x => { return "shinyRequireLoader!" + x });
    }
    return oldRequire.apply(this, [deps, callback, errback, optional]);
}
for(var prop in oldRequire) {
    if (oldRequire.hasOwnProperty(prop)) {
        window.require[prop] = oldRequire[prop];
    }
}

// Listen for require-module-loaded events, and when they are received,
// load the module into the DOM
window.addEventListener('require-module-loaded', function(event) {
    console.log('require-module-loaded', event.detail.name);
    if (Shiny) Shiny.bindAll(document);
});
