"""Discovering and loading album templates.

An album is a directory (under ``albums/`` by default) that is a Python package whose
``__init__.py`` exposes ``TEMPLATE``, a :class:`~setart.core.template.Template` subclass.
Being a package lets an album split bespoke code across modules with relative imports.
"""

from __future__ import annotations

import importlib.util
import os
import sys
import types
from pathlib import Path

from .template import Template

DEFAULT_ALBUMS_DIR = Path(os.environ.get("SETART_ALBUMS", "albums"))


def album_dirs(root: Path = DEFAULT_ALBUMS_DIR) -> list[Path]:
    if not root.is_dir():
        return []
    return sorted(p for p in root.iterdir() if (p / "__init__.py").is_file())


def resolve(album: str, root: Path = DEFAULT_ALBUMS_DIR) -> Path:
    """Accept a path or an album folder name (dashes and underscores are interchangeable)."""
    direct = Path(album)
    if (direct / "__init__.py").is_file():
        return direct
    for candidate in (album, album.replace("-", "_")):
        path = root / candidate
        if (path / "__init__.py").is_file():
            return path
    known = ", ".join(p.name for p in album_dirs(root)) or "(none)"
    raise FileNotFoundError(f"album {album!r} not found in {root}. Known: {known}")


def load(album: str | Path, root: Path = DEFAULT_ALBUMS_DIR) -> type[Template]:
    path = resolve(str(album), root).resolve()
    # Albums are imported as sub-packages of a synthetic ``setart_albums`` package so that
    # relative imports inside an album (``from . import scene``) work.
    if "setart_albums" not in sys.modules:
        parent = types.ModuleType("setart_albums")
        parent.__path__ = []
        sys.modules["setart_albums"] = parent
    module_name = f"setart_albums.{path.name}"
    if module_name in sys.modules:
        module = sys.modules[module_name]
    else:
        spec = importlib.util.spec_from_file_location(
            module_name, path / "__init__.py", submodule_search_locations=[str(path)]
        )
        if spec is None or spec.loader is None:
            raise ImportError(f"cannot import album at {path}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
    template = getattr(module, "TEMPLATE", None)
    if not (isinstance(template, type) and issubclass(template, Template)):
        raise TypeError(f"{path}/__init__.py must define TEMPLATE = <Template subclass>")
    return template
