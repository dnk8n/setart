"""Colour: parsing, palettes and gradient ramps. All colours are float RGB in [0, 1]."""

from __future__ import annotations

import colorsys
from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np

RGB = tuple[float, float, float]


def hex_rgb(code: str) -> RGB:
    code = code.lstrip("#")
    if len(code) == 3:
        code = "".join(c * 2 for c in code)
    return tuple(int(code[i : i + 2], 16) / 255.0 for i in (0, 2, 4))  # type: ignore[return-value]


def hsv(h: float, s: float, v: float) -> RGB:
    return colorsys.hsv_to_rgb(h % 1.0, s, v)


def solid(width: int, height: int, rgb: Sequence[float]) -> np.ndarray:
    return np.broadcast_to(np.asarray(rgb, dtype=np.float32), (height, width, 3)).copy()


def mix(a: np.ndarray, b: np.ndarray, t: np.ndarray | float) -> np.ndarray:
    t = np.asarray(t, dtype=np.float32)
    if t.ndim == 2:
        t = t[..., None]
    return (a + (b - a) * t).astype(np.float32)


@dataclass(frozen=True)
class Palette:
    """An ordered list of colour stops that can be sampled as a smooth ramp."""

    name: str
    colors: tuple[RGB, ...]

    @classmethod
    def from_hex(cls, name: str, *codes: str) -> Palette:
        return cls(name, tuple(hex_rgb(c) for c in codes))

    def array(self) -> np.ndarray:
        return np.asarray(self.colors, dtype=np.float32)

    def ramp(self, t: np.ndarray, cyclic: bool = False) -> np.ndarray:
        """Map a field ``t`` to colours. Cyclic ramps wrap (t=1 meets t=0) for banding."""
        stops = self.array()
        if cyclic:
            stops = np.concatenate([stops, stops[:1]], axis=0)
            t = np.mod(t, 1.0)
        else:
            t = np.clip(t, 0.0, 1.0)
        pos = t.astype(np.float32) * (len(stops) - 1)
        i0 = np.clip(np.floor(pos).astype(np.int64), 0, len(stops) - 2)
        f = (pos - i0)[..., None]
        # Smooth the interpolation between stops so bands blend without hard kinks.
        f = f * f * (3.0 - 2.0 * f)
        return (stops[i0] + (stops[i0 + 1] - stops[i0]) * f).astype(np.float32)


def cosine(t: np.ndarray, a: RGB, b: RGB, c: RGB, d: RGB) -> np.ndarray:
    """Procedural cosine palette: ``a + b * cos(2pi(c*t + d))`` (after Inigo Quilez)."""
    t = np.asarray(t, dtype=np.float32)[..., None]
    a_, b_, c_, d_ = (np.asarray(v, dtype=np.float32) for v in (a, b, c, d))
    return np.clip(a_ + b_ * np.cos(2 * np.pi * (c_ * t + d_)), 0.0, 1.0).astype(np.float32)


def adjust_saturation(image: np.ndarray, amount: float) -> np.ndarray:
    luma = (image @ np.asarray([0.2126, 0.7152, 0.0722], dtype=np.float32))[..., None]
    return np.clip(luma + (image - luma) * amount, 0.0, 1.0).astype(np.float32)
