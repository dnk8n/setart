"""Seeded, vectorised coherent noise (pure numpy, no global state).

``Perlin`` is classic 2D gradient noise; :func:`fbm` layers octaves; :func:`domain_warp`
feeds noise into its own coordinates, the core trick behind fluid, psychedelic marbling.
"""

from __future__ import annotations

import numpy as np


def _fade(t: np.ndarray) -> np.ndarray:
    return t * t * t * (t * (t * 6.0 - 15.0) + 10.0)


class Perlin:
    """2D gradient noise. Output is roughly in [-0.7, 0.7]."""

    def __init__(self, rng: np.random.Generator, table_size: int = 256):
        self.n = table_size
        perm = rng.permutation(table_size).astype(np.int32)
        self.perm = np.concatenate([perm, perm])
        angles = rng.uniform(0.0, 2.0 * np.pi, table_size)
        self.gx = np.cos(angles).astype(np.float32)
        self.gy = np.sin(angles).astype(np.float32)

    def __call__(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        x = np.asarray(x, dtype=np.float32)
        y = np.asarray(y, dtype=np.float32)
        x0 = np.floor(x)
        y0 = np.floor(y)
        fx = x - x0
        fy = y - y0
        mask = self.n - 1
        xi = x0.astype(np.int64) & mask
        yi = y0.astype(np.int64) & mask
        p = self.perm
        a = p[xi]
        b = p[xi + 1]
        h00 = p[a + yi]
        h01 = p[a + yi + 1]
        h10 = p[b + yi]
        h11 = p[b + yi + 1]

        def dot(h, dx, dy):
            return self.gx[h] * dx + self.gy[h] * dy

        n00 = dot(h00, fx, fy)
        n10 = dot(h10, fx - 1, fy)
        n01 = dot(h01, fx, fy - 1)
        n11 = dot(h11, fx - 1, fy - 1)
        u = _fade(fx)
        v = _fade(fy)
        nx0 = n00 + u * (n10 - n00)
        nx1 = n01 + u * (n11 - n01)
        return (nx0 + v * (nx1 - nx0)).astype(np.float32)


class FBM:
    """Fractional Brownian motion: summed octaves of Perlin noise, normalised to about [-1, 1]."""

    def __init__(
        self,
        rng: np.random.Generator,
        octaves: int = 5,
        lacunarity: float = 2.0,
        gain: float = 0.5,
    ):
        self.octaves = octaves
        self.lacunarity = lacunarity
        self.gain = gain
        self.layers = [Perlin(rng) for _ in range(octaves)]
        self.offsets = rng.uniform(0, 256, size=(octaves, 2)).astype(np.float32)
        self.norm = sum(gain**i for i in range(octaves)) * 0.7

    def __call__(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        total = np.zeros(np.broadcast(x, y).shape, dtype=np.float32)
        freq, amp = 1.0, 1.0
        for i, layer in enumerate(self.layers):
            ox, oy = self.offsets[i]
            total += amp * layer(x * freq + ox, y * freq + oy)
            freq *= self.lacunarity
            amp *= self.gain
        return total / self.norm


def domain_warp(
    rng: np.random.Generator,
    x: np.ndarray,
    y: np.ndarray,
    scale: float = 2.0,
    strength: float = 1.0,
    iterations: int = 2,
    octaves: int = 5,
) -> tuple[np.ndarray, tuple[np.ndarray, np.ndarray]]:
    """Iterated domain warping (after Inigo Quilez).

    Returns ``(value, (wx, wy))``: the final scalar field in about [-1, 1] and the last
    warp vector, which is useful for colouring by flow direction.
    """
    fields = [(FBM(rng, octaves), FBM(rng, octaves)) for _ in range(iterations)]
    final = FBM(rng, octaves)
    px, py = x * scale, y * scale
    wx = np.zeros_like(px)
    wy = np.zeros_like(py)
    for fx, fy in fields:
        qx = px + strength * 4.0 * wx
        qy = py + strength * 4.0 * wy
        wx, wy = fx(qx, qy), fy(qx, qy)
    value = final(px + strength * 4.0 * wx, py + strength * 4.0 * wy)
    return value, (wx, wy)
