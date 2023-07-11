#!/usr/bin/env python3

import importlib
import sys
from types import ModuleType
from typing import Union, cast

if sys.version_info < (3, 9):
    raise RuntimeError("This script requires Python 3.9 or later")


def gen_init_py(package_name: str) -> None:
    """
    Generate imports for __init__.py for a package or subpackage.
    """
    pkg = importlib.import_module(package_name)
    print("")
    print("=" * 80)
    print(pkg)
    print("=" * 80)

    all_imports: list[str] = []
    for name in dir(pkg):
        submodule = getattr(pkg, name)
        if isinstance(submodule, ModuleType):
            # print(submodule)
            all = getattr(submodule, "__all__", None)
            all = cast(Union[tuple[str], None], all)
            if all is not None:
                if not submodule.__name__.startswith(pkg.__name__ + "."):
                    continue
                    # print(
                    #     f"{name}: {submodule.__name__} does not appear to be a submodule of {pkg.__name__}"
                    # )

                all_imports.extend(all)

                submodule_relname = submodule.__name__.removeprefix(pkg.__name__)
                out = f"from {submodule_relname} import " + ", ".join(all)
                print(out)

    # print(f"__all__ = {tuple(all_imports)}")


gen_init_py("shiny")
gen_init_py("shiny.reactive")
gen_init_py("shiny.render")
gen_init_py("shiny.session")
gen_init_py("shiny.ui")
