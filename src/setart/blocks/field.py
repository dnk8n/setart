"""Scalar field utilities: remapping, shaping and resampling."""

from __future__ import annotations

import numpy as np
from PIL import Image


def normalize(f: np.ndarray, lo: float | None = None, hi: float | None = None) -> np.ndarray:
    lo = float(f.min()) if lo is None else lo
    hi = float(f.max()) if hi is None else hi
    return ((f - lo) / max(hi - lo, 1e-12)).astype(np.float32)


def smoothstep(edge0: float, edge1: float, x: np.ndarray) -> np.ndarray:
    t = np.clip((x - edge0) / (edge1 - edge0), 0.0, 1.0)
    return (t * t * (3.0 - 2.0 * t)).astype(np.float32)


def resize(f: np.ndarray, width: int, height: int) -> np.ndarray:
    """Bicubic resize of a float field (lets expensive smooth fields be computed at low res)."""
    if f.shape == (height, width):
        return f
    img = Image.fromarray(np.ascontiguousarray(f, dtype=np.float32), mode="F")
    return np.asarray(img.resize((width, height), Image.Resampling.BICUBIC), dtype=np.float32)


def sample(image: np.ndarray, x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Bilinear sample ``image`` at pixel coordinates (x, y), clamping at the edges."""
    h, w = image.shape[:2]
    x = np.clip(x, 0, w - 1.001)
    y = np.clip(y, 0, h - 1.001)
    x0 = np.floor(x).astype(np.int64)
    y0 = np.floor(y).astype(np.int64)
    fx = (x - x0).astype(np.float32)
    fy = (y - y0).astype(np.float32)
    if image.ndim == 3:
        fx = fx[..., None]
        fy = fy[..., None]
    a = image[y0, x0]
    b = image[y0, x0 + 1]
    c = image[y0 + 1, x0]
    d = image[y0 + 1, x0 + 1]
    top = a + (b - a) * fx
    bottom = c + (d - c) * fx
    return (top + (bottom - top) * fy).astype(np.float32)


def box_blur(image: np.ndarray, radius: int, passes: int = 3) -> np.ndarray:
    """Separable box blur via cumulative sums; three passes approximate a Gaussian."""
    if radius < 1:
        return image
    out = image.astype(np.float32)
    for _ in range(passes):
        for axis in (0, 1):
            pad = [(0, 0)] * out.ndim
            pad[axis] = (radius + 1, radius)
            padded = np.pad(out, pad, mode="edge")
            c = np.cumsum(padded, axis=axis, dtype=np.float64)
            n = out.shape[axis]
            hi = np.take(c, np.arange(2 * radius + 1, 2 * radius + 1 + n), axis=axis)
            lo = np.take(c, np.arange(0, n), axis=axis)
            out = ((hi - lo) / (2 * radius + 1)).astype(np.float32)
    return out
