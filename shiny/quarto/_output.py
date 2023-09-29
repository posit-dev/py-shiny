"""Shim for @output"""
from __future__ import annotations

__all__ = ("output_shim",)


def output_shim(x: object) -> object:
    return x
