import { BuildOptions, build } from "esbuild";
import { sassPlugin } from "esbuild-sass-plugin";
import * as fs from "node:fs/promises";

const outDir = "../shiny/www/shared/py-shiny";

async function bundle_dataframe() {
  try {
    const options: BuildOptions = {
      entryPoints: { dataframe: "dataframe/index.tsx" },
      format: "esm",
      bundle: true,
      outdir: outDir + "/dataframe",
      minify: true,
      sourcemap: true,
      plugins: [sassPlugin({ type: "css-text", sourceMap: false })],
      metafile: true,
    };

    const result = await build(options);
    console.log("Building dataframe completed successfully!");
    // console.log("Output:", result);
    await fs.writeFile(
      "esbuild-metadata.json",
      JSON.stringify(result.metafile)
    );
  } catch (error) {
    console.error("Build failed:", error);
  }
}

async function bundle_textarea() {
  try {
    const options: BuildOptions = {
      entryPoints: {
        "textarea-autoresize": "text-area/textarea-autoresize.ts",
      },
      format: "esm",
      bundle: true,
      outdir: outDir + "/text-area",
      minify: false,
      sourcemap: false,
      metafile: false,
    };
    const result = await build(options);
    console.log("Building textarea-autoresize completed successfully!");
  } catch (error) {
    console.error("Build failed for textarea-autoresize:", error);
  }
}

// Run function to avoid top level await
async function main(): Promise<void> {
  await Promise.all([bundle_dataframe(), bundle_textarea()]);
}
main();
