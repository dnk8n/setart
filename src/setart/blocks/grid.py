"""Coordinate grids. Work in normalised coordinates so compositions are resolution independent."""

from __future__ import annotations

import numpy as np


def uv(width: int, height: int) -> tuple[np.ndarray, np.ndarray]:
    """Pixel-centre coordinates with u in [0, 1] left->right and v in [0, 1] top->bottom."""
    u = (np.arange(width, dtype=np.float32) + 0.5) / width
    v = (np.arange(height, dtype=np.float32) + 0.5) / height
    return np.meshgrid(u, v)


def centered(width: int, height: int) -> tuple[np.ndarray, np.ndarray]:
    """Coordinates centred on the image with the shorter side spanning [-1, 1]."""
    u, v = uv(width, height)
    s = min(width, height)
    return (u - 0.5) * 2 * width / s, (v - 0.5) * 2 * height / s


def polar(x: np.ndarray, y: np.ndarray, cx: float = 0.0, cy: float = 0.0):
    """(radius, angle) about a centre."""
    dx, dy = x - cx, y - cy
    return np.hypot(dx, dy), np.arctan2(dy, dx)


def centered_to_pixels(x, y, width: int, height: int):
    """Inverse of :func:`centered`: centred coordinates back to pixel coordinates."""
    s = min(width, height)
    px = (x * s / (2 * width) + 0.5) * width - 0.5
    py = (y * s / (2 * height) + 0.5) * height - 0.5
    return px, py
