# PyShiny API reference

## Build locally

To build the PyShiny API reference locally, do:

```sh
make clean && make html
```

Note that `make clean` won't remove `source/reference` files, so you may periodically want to `rm -r source/reference` to truly have a clean build.

## Preview locally

Serve the contents of `build/html`

```sh
cd build/html
python3 -m http.server
```

(Then open your browser to <http://localhost:8000>)

## Development

It's recommended to use VSCode's [reStructuredText extension](https://marketplace.visualstudio.com/items?itemName=lextudio.restructuredtext) (as well as it's recommended extensions) when contributing to these docs. **Just make sure you open VSCode from the docs folder**:

```sh
code prism/docs
```
