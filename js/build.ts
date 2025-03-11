import { BuildOptions, build, type Metafile } from "esbuild";
import { sassPlugin } from "esbuild-sass-plugin";
import * as fs from "node:fs/promises";

let minify = true;
let metafile = true;
process.argv.forEach((val, index) => {
  if (val === "--minify=false") {
    console.log("Disabling minification");
    minify = false;
  }
  if (val === "--metafile=false") {
    console.log("Disabling metafile generation");
    metafile = false;
  }
});

const outDir = "../shiny/www/py-shiny";

const allEsbuildMetadata: Array<Metafile> = [];

function mergeMetadatas(metadatas: Array<Metafile>): Metafile {
  // Merge all the metafile objects together
  const mergedMetadata: Metafile = {
    inputs: {},
    outputs: {},
  };

  metadatas.forEach((metafile) => {
    Object.entries(metafile.inputs).forEach(([key, value]) => {
      if (
        mergedMetadata.inputs[key] &&
        JSON.stringify(mergedMetadata.inputs[key]) !== JSON.stringify(value)
      ) {
        // It's very possible for multiple MetaFile objects to refer to the same input.
        // But if that input has different values in the different Metafile objects,
        // that could cause inaccuracies when we merge them. I think it's possible they
        // could have different values if tree-shaking is enabled -- this will detect
        // those cases and warn the user, and if it happens we can figure out how to
        // handle it.
        console.warn(
          `Different values found for key in metadata: ${key}. Overwriting.`
        );
      }
      mergedMetadata.inputs[key] = value;
    });
    Object.entries(metafile.outputs).forEach(([key, value]) => {
      if (mergedMetadata.outputs[key]) {
        console.warn(`Duplicate key found in metadata: ${key}. Overwriting.`);
      }
      mergedMetadata.outputs[key] = value;
    });
  });

  return mergedMetadata;
}
async function bundle_helper(
  options: BuildOptions
): Promise<ReturnType<typeof build> | undefined> {
  try {
    const result = await build({
      format: "esm",
      bundle: true,
      minify: minify,
      sourcemap: minify,
      metafile: metafile,
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

    if (result.metafile) {
      allEsbuildMetadata.push(result.metafile);
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
  },
  {
    entryPoints: {
      "text-area/textarea-autoresize": "text-area/textarea-autoresize.ts",
    },
  },
  {
    entryPoints: {
      "page-output/page-output": "page-output/page-output.ts",
    },
  },
  {
    entryPoints: { "spin/spin": "spin/spin.scss" },
    plugins: [sassPlugin({ type: "css", sourceMap: false })],
  },
  {
    entryPoints: {
      "markdown-stream/markdown-stream": "markdown-stream/markdown-stream.ts",
    },
  },
  {
    entryPoints: {
      "markdown-stream/markdown-stream": "markdown-stream/markdown-stream.scss",
    },
    plugins: [sassPlugin({ type: "css", sourceMap: false })],
  },
  {
    entryPoints: {
      "chat/chat": "chat/chat.ts",
    },
  },
  {
    entryPoints: { "chat/chat": "chat/chat.scss" },
    plugins: [sassPlugin({ type: "css", sourceMap: false })],
  },
];

(async () => {
  await Promise.all(opts.map(bundle_helper));

  if (metafile) {
    const mergedMetadata = mergeMetadatas(allEsbuildMetadata);
    await fs.writeFile("esbuild-metadata.json", JSON.stringify(mergedMetadata));
    console.log("Metadata file written to esbuild-metadata.json");
  }
})();
