# Copyright (c) 2024 databackend contributors (MIT License)
#
# See https://github.com/machow/databackend

# pyright: reportMissingTypeArgument=false
# pyright: reportUnknownArgumentType=false
# pyright: reportUnknownMemberType=false
# pyright: reportUnknownParameterType=false
# pyright: reportUnknownVariableType=false

import importlib
import sys
from abc import ABCMeta


def _load_class(mod_name: str, cls_name: str):
    mod = importlib.import_module(mod_name)
    return getattr(mod, cls_name)


class _AbstractBackendMeta(ABCMeta):
    def register_backend(cls, mod_name: str, cls_name: str):
        cls._backends.append(  # pyright: ignore[reportGeneralTypeIssues, reportAttributeAccessIssue]
            (mod_name, cls_name)
        )

        # """Clear the caches (for debugging or testing)"""
        cls._abc_caches_clear()  # pyright: ignore[reportGeneralTypeIssues,reportAttributeAccessIssue]


class AbstractBackend(metaclass=_AbstractBackendMeta):
    @classmethod
    def __init_subclass__(cls):
        if not hasattr(cls, "_backends"):
            cls._backends = []

    @classmethod
    def __subclasshook__(cls, subclass: type):
        for mod_name, cls_name in cls._backends:
            if mod_name not in sys.modules:
                # module isn't loaded, so it can't be the subclass
                # we don't want to import the module to explicitly run the check
                # so skip here.
                continue
            else:
                parent_candidate = _load_class(mod_name, cls_name)
                if issubclass(subclass, parent_candidate):
                    return True

        return NotImplemented
