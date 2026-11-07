"""Signed distance functions and soft masks for resolution-independent shapes."""

from __future__ import annotations

import numpy as np


def circle(x: np.ndarray, y: np.ndarray, cx: float, cy: float, r: float) -> np.ndarray:
    """Signed distance to a circle: negative inside."""
    return (np.hypot(x - cx, y - cy) - r).astype(np.float32)


def fill(sdf: np.ndarray, softness: float) -> np.ndarray:
    """Anti-aliased mask from an SDF: 1 inside, 0 outside, ``softness`` wide edge."""
    return np.clip(0.5 - sdf / max(softness, 1e-6), 0.0, 1.0).astype(np.float32)


def glow(sdf: np.ndarray, radius: float, power: float = 2.0) -> np.ndarray:
    """Falloff outside a shape, 1 at the edge fading to 0 at ``radius``."""
    d = np.maximum(sdf, 0.0) / max(radius, 1e-6)
    return (1.0 / (1.0 + d**power)).astype(np.float32)
