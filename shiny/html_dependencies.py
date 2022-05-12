from htmltools import HTMLDependency


def shiny_deps() -> HTMLDependency:
    return HTMLDependency(
        name="shiny",
        version="0.0.1",
        source={"package": "shiny", "subdir": "www/shared/"},
        script={"src": "shiny.js"},
        stylesheet={"href": "shiny.min.css"},
    )


def jquery_deps() -> HTMLDependency:
    return HTMLDependency(
        name="jquery",
        version="3.6.0",
        source={"package": "shiny", "subdir": "www/shared/jquery/"},
        script={"src": "jquery-3.6.0.min.js"},
    )


def require_deps() -> HTMLDependency:
    return HTMLDependency(
        name="requirejs",
        version="2.3.6",
        source={"package": "shiny", "subdir": "www/shared/requirejs/"},
        script={"src": "require.min.js"},
        # Since HTMLDependency()s are designed to be loaded via a <script> tag,
        # we need to avoid anonymous define() calls (which will error out in a script tag)
        # https://requirejs.org/docs/errors.html#mismatch
        #
        # The current way we approach this is to leverage a data-requiremodule attribute,
        # which requirejs happends to set when it loads scripts in the browser
        # https://github.com/requirejs/requirejs/blob/898ff9/require.js#L1897-L1902
        head="""
        <script type="text/javascript">
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
        </script>
        """,
    )
