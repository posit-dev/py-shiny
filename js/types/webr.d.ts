// This tells TypeScript that the URL has the same stuff as the local webr
// package. This is needed because the URL is not a local package
declare module "https://webr.r-wasm.org/latest/webr.mjs" {
  export * from "webr";
}
