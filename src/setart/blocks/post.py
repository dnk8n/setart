"""Finishing passes applied to whole images."""

from __future__ import annotations

import numpy as np

from . import field, grid


def vignette(image: np.ndarray, strength: float = 0.4, radius: float = 1.1) -> np.ndarray:
    h, w = image.shape[:2]
    x, y = grid.centered(w, h)
    r = np.hypot(x, y) / radius
    mask = 1.0 - strength * field.smoothstep(0.4, 1.4, r)
    return (image * mask[..., None]).astype(np.float32)


def grain(image: np.ndarray, rng: np.random.Generator, amount: float = 0.03) -> np.ndarray:
    h, w = image.shape[:2]
    noise = rng.standard_normal((h, w), dtype=np.float32) * amount
    return np.clip(image + noise[..., None], 0.0, 1.0).astype(np.float32)


def chromatic_aberration(image: np.ndarray, amount: float = 0.004) -> np.ndarray:
    """Push red outward and blue inward from the centre, like a cheap lens."""
    h, w = image.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    cx, cy = (w - 1) / 2, (h - 1) / 2
    out = image.copy()
    for channel, k in ((0, 1.0 - amount), (2, 1.0 + amount)):
        out[..., channel] = field.sample(
            image[..., channel], cx + (xx - cx) * k, cy + (yy - cy) * k
        )
    return out


def bloom(
    image: np.ndarray, threshold: float = 0.7, radius_frac: float = 0.01, strength: float = 0.6
) -> np.ndarray:
    """Blur the bright parts and screen them back on top."""
    h, w = image.shape[:2]
    bright = np.clip((image - threshold) / max(1 - threshold, 1e-6), 0, 1)
    blurred = field.box_blur(bright, max(1, round(radius_frac * min(w, h))))
    return np.clip(1 - (1 - image) * (1 - blurred * strength), 0, 1).astype(np.float32)
