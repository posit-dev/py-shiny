import * as esbuild from "esbuild";
import * as React from "react";
import * as ReactDOM from "react-dom";

function namedExports(module) {
  return Object.keys(module).filter((x) => x !== "default");
}

import { globalExternals } from "@fal-works/esbuild-plugin-global-externals";

/** Mapping from module paths to global variables */
const globals = {
  react: {
    varName: "React",
    namedExports: namedExports(React),
    defaultExport: true,
  },
  "react-dom": {
    varName: "ReactDOM",
    namedExports: namedExports(ReactDOM),
    defaultExport: true,
  },
};

await esbuild.build({
  entryPoints: ["index.tsx"],
  bundle: true,
  outdir: "dist",
  minify: true,
  sourcemap: true,
  plugins: [globalExternals(globals)],
});
