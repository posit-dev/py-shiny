import { BuildOptions, build } from "esbuild";
import { sassPlugin } from "esbuild-sass-plugin";
import * as fs from "node:fs";

async function bundle() {
  try {
    const options: BuildOptions = {
      entryPoints: { dataframe: "dataframe/index.tsx" },
      format: "esm",
      bundle: true,
      outdir: "../shiny/www/shared/dataframe",
      minify: true,
      sourcemap: true,
      plugins: [sassPlugin({ type: "css-text", sourceMap: false })],
      metafile: true,
    };

    const result = await build(options);
    console.log("Build completed successfully!");
    // console.log("Output:", result);
    fs.writeFileSync("esbuild-metadata.json", JSON.stringify(result.metafile));
  } catch (error) {
    console.error("Build failed:", error);
  }
}

bundle();
