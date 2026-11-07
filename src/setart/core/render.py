"""The one function that ties a template, a seed and an output folder together."""

from __future__ import annotations

import platform
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

import numpy as np
import PIL

from . import export
from .artefact import Artefact
from .template import RenderContext, Template


def _setart_version() -> str:
    try:
        return version("setart")
    except PackageNotFoundError:
        return "unknown"


def render(
    template_cls: type[Template],
    seed: int,
    overrides: dict[str, str] | None = None,
    scale: float = 1.0,
) -> tuple[list[Artefact], dict]:
    params = template_cls.make_params(overrides)
    ctx = RenderContext(seed=seed, params=params, scale=scale)
    artefacts = template_cls().render(ctx)
    if not artefacts:
        raise RuntimeError(f"{template_cls.name} produced no artefacts")
    names = [f"{a.name}.{a.format}" for a in artefacts]
    if len(set(names)) != len(names):
        raise RuntimeError(f"{template_cls.name} produced duplicate artefact names: {names}")
    manifest = {
        "template": template_cls.name,
        "template_version": template_cls.version,
        "seed": seed,
        "scale": scale,
        "params": params,
        "environment": {
            "setart": _setart_version(),
            "numpy": np.__version__,
            "pillow": PIL.__version__,
            "python": platform.python_version(),
            "machine": platform.machine(),
        },
    }
    return artefacts, manifest


def render_to_dir(
    template_cls: type[Template],
    seed: int,
    out_dir: Path,
    overrides: dict[str, str] | None = None,
    scale: float = 1.0,
) -> list[Path]:
    artefacts, manifest = render(template_cls, seed, overrides, scale)
    return export.write(artefacts, out_dir, manifest)
