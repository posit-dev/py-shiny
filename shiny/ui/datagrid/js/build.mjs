import * as fs from "fs/promises";
import * as esbuild from "esbuild";
import * as React from "react";
import * as ReactDOM from "react-dom";
import { sassPlugin } from "esbuild-sass-plugin";
import { globalExternals } from "@fal-works/esbuild-plugin-global-externals";

function namedExports(module) {
  return Object.keys(module).filter((x) => x !== "default");
}

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

await fs.copyFile(
  "node_modules/react/umd/react.production.min.js",
  "dist/react.production.min.js"
);
await fs.copyFile(
  "node_modules/react-dom/umd/react-dom.production.min.js",
  "dist/react-dom.production.min.js"
);

await fs.copyFile(
  "node_modules/react/umd/react.development.js",
  "dist/react.development.js"
);
await fs.copyFile(
  "node_modules/react-dom/umd/react-dom.development.js",
  "dist/react-dom.development.js"
);

await fs.copyFile(
  "node_modules/react/umd/react.profiling.min.js",
  "dist/react.profiling.min.js"
);
await fs.copyFile(
  "node_modules/react-dom/umd/react-dom.profiling.min.js",
  "dist/react-dom.profiling.min.js"
);

await esbuild.build({
  entryPoints: ["index.tsx"],
  bundle: true,
  outdir: "dist",
  minify: true,
  sourcemap: true,
  plugins: [globalExternals(globals), sassPlugin()],
  target: ["safari12"],
});
