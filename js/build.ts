import esbuild from "esbuild";
import { sassPlugin } from "esbuild-sass-plugin";
import * as fs from "node:fs";

// Set a boolean value of watch to true if the flag --watch is provided when the file is run from the command line.
// E.g. tsx scripts/build.ts --watch
const watch: boolean = process.argv.includes("--watch");
const minify: boolean = process.argv.includes("--minify");
const metafile: boolean = process.argv.includes("--metafile");

const rebuildLoggerPlugin = {
  name: "rebuild-logger",
  setup(build: esbuild.PluginBuild) {
    build.onStart(() => {
      console.log(`[${new Date().toISOString()}] Rebuilding JS files...`);
    });
  },
};

const metafilePlugin = {
  name: "metafile",
  setup(build: esbuild.PluginBuild) {
    build.onEnd((result) => {
      if (metafile) {
        fs.writeFileSync(
          "esbuild-metadata.json",
          JSON.stringify(result.metafile)
        );
      }
    });
  },
};

esbuild
  .context({
    entryPoints: {
      "dataframe/dataframe": "dataframe/index.tsx",
      "ml/ml": "ml/index.ts",
    },
    format: "esm",
    bundle: true,
    outdir: "../shiny/www/shared",
    minify: minify,
    sourcemap: true,
    metafile: true,
    plugins: [
      sassPlugin({ type: "css-text", sourceMap: false }),
      rebuildLoggerPlugin,
      metafilePlugin,
    ],
  })
  .then((context) => {
    if (watch) {
      context.watch();
    } else {
      context.rebuild();
      context.dispose();
    }
  })
  .catch(() => process.exit(1));
