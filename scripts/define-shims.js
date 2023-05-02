// Since HTMLDependency()s are designed to be loaded via a <script> tag, we do our best
// to avoid anonymous define() calls (which will error out in a script tag)
// https://requirejs.org/docs/errors.html#mismatch
const oldDefine = window.define;
window.define = function define(name, deps, callback) {
  if (typeof name !== "string") {
    callback = deps;
    deps = name;
    const script = document.currentScript;
    if (script) {
      name = script.getAttribute("data-requiremodule");
      if (name) {
        console.info(
          `Changing an anonymous define() call to named define() using '${name}'`
        );
      }
    }
  }
  return oldDefine.apply(this, [name, deps, callback]);
};
for (var prop in oldDefine) {
  if (oldDefine.hasOwnProperty(prop)) {
    window.define[prop] = oldDefine[prop];
  }
}

// By default, we want UMD loaders to attach themselves to the window. This seems like
// better/safer default behavior since, the alternative is to have any UMD loader to
// fail if loaded via a <script> tag. If dependencies actually do want to be
// define()/require(), they can opt
window.define.amd = false;

// In case someone want to restore the old define() function
window.define.noConflict = function() {
  window.define = oldDefine;
  return this;
};

// Users can still encounter this anonymous define() error, and we've actually
// encountered this in shiny-server-client.js because we were inlining an internal
// dependency that contained an anonymous define()
// https://github.com/rstudio/shiny-server-client/blob/5ee5aac/dist/shiny-server-client.js#L4271-L4272).
// In this case, it doesn't seem like there is anything we can do to help the situation
// other than to add some more context to the error.
const oldOnError = window.requirejs.onError;
window.requirejs.onError = function(err) {
  if (err.message.includes('Mismatched anonymous define()')) {
    err.message = err.message + '\n\nTo avoid this error, consider either: (1) adding a data-requiremodule attribute (with the module name) to the <script> tag containing the anonymous define(), (2) setting define.amd=false, or (3) removing the anonymous define() altogether.';
  }

  return oldOnError.apply(this, [err]);
}
