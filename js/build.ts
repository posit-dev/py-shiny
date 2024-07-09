import { BuildOptions, build } from "esbuild";
import { sassPlugin } from "esbuild-sass-plugin";
import * as fs from "node:fs/promises";

let minify = true;
process.argv.forEach((val, index) => {
  if (val === "--minify=false") {
    console.log("Disabling minification");
    minify = false;
  }
});

const outDir = "../shiny/www/py-shiny";

async function bundle_helper(
  options: BuildOptions
): Promise<ReturnType<typeof build> | undefined> {
  try {
    const result = await build({
      format: "esm",
      bundle: true,
      minify: minify,
      sourcemap: true,
      metafile: false,
      outdir: outDir,
      ...options,
    });

    Object.entries(options.entryPoints as Record<string, string>).forEach(
      ([output_file_stub, input_path]) => {
        console.log(
          "Building " + output_file_stub + ".js completed successfully!"
        );
      }
    );

    if (options.metafile) {
      // Save metafile
      const data_frame_results = result;
      await fs.writeFile(
        "esbuild-metadata.json",
        JSON.stringify(data_frame_results.metafile)
      );
      console.log("Metadata file written to esbuild-metadata.json");
    }
    return result;
  } catch (error) {
    console.error("Build failed:", error);
  }
}

const opts: Array<BuildOptions> = [
  {
    entryPoints: { "data-frame/data-frame": "data-frame/index.tsx" },
    plugins: [sassPlugin({ type: "css-text", sourceMap: false })],
    metafile: true,
  },
  {
    entryPoints: {
      "text-area/textarea-autoresize": "text-area/textarea-autoresize.ts",
    },
    minify: false,
    sourcemap: false,
  },
  {
    entryPoints: {
      "page-output/page-output": "page-output/page-output.ts",
    },
    minify: false,
    sourcemap: false,
  },
  {
    entryPoints: { "spin/spin": "spin/spin.scss" },
    plugins: [sassPlugin({ type: "css", sourceMap: false })],
    metafile: true,
  },
  {
    entryPoints: {
      "chat/chat": "chat/chat.ts",
    },
    minify: true,
    sourcemap: true,
  },
  {
    entryPoints: { "chat/chat": "chat/chat.scss" },
    plugins: [sassPlugin({ type: "css", sourceMap: false })],
    metafile: true,
  },
];

// Run function to avoid top level await
async function main(): Promise<void> {
  await Promise.all(opts.map(bundle_helper));
}
main();
