"""Layer blending. ``base`` and ``layer`` are (H, W, 3) floats; ``alpha`` is scalar or (H, W)."""

from __future__ import annotations

from collections.abc import Callable

import numpy as np

BlendFn = Callable[[np.ndarray, np.ndarray], np.ndarray]


def _normal(b, top):
    return top


def _multiply(b, top):
    return b * top


def _screen(b, top):
    return 1.0 - (1.0 - b) * (1.0 - top)


def _add(b, top):
    return np.minimum(b + top, 1.0)


def _overlay(b, top):
    return np.where(b < 0.5, 2 * b * top, 1 - 2 * (1 - b) * (1 - top))


def _soft_light(b, top):
    return (1 - 2 * top) * b * b + 2 * top * b


def _difference(b, top):
    return np.abs(b - top)


MODES: dict[str, BlendFn] = {
    "normal": _normal,
    "multiply": _multiply,
    "screen": _screen,
    "add": _add,
    "overlay": _overlay,
    "soft_light": _soft_light,
    "difference": _difference,
}


def blend(
    base: np.ndarray, layer: np.ndarray, alpha: np.ndarray | float = 1.0, mode: str = "normal"
) -> np.ndarray:
    if mode not in MODES:
        raise KeyError(f"unknown blend mode {mode!r}; choose from {sorted(MODES)}")
    mixed = MODES[mode](base, layer)
    a = np.asarray(alpha, dtype=np.float32)
    if a.ndim == 2:
        a = a[..., None]
    return np.clip(base + (mixed - base) * a, 0.0, 1.0).astype(np.float32)
