"""Layers of the Kosi Bay cover. Each function is one idea from brief.md.

Coordinates are centred and normalised (see ``setart.blocks.grid.centered``): the image
spans [-1, 1] on both axes, y grows downwards, and the horizon sits at ``params.horizon``.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from setart import Seeds
from setart.blocks import color, composite, field, grid, noise, shapes

from . import palette


@dataclass(frozen=True)
class City:
    name: str
    scene: str
    bpm: float


# Typical tempos of each city's signature sound set the spacing of its wave rings.
CITIES = (
    City("Detroit", "techno", 130.0),
    City("Jersey", "garage house", 122.0),
    City("New York", "garage", 118.0),
    City("London", "UK garage", 132.0),
)


@dataclass
class Fields:
    """Expensive, resolution-dependent fields computed once and reused across frames."""

    x: np.ndarray
    y: np.ndarray
    marble: np.ndarray
    flow: np.ndarray
    sources: list[tuple[float, float, float, float]]  # (sx, sy, freq, phase)


def sky_field(seeds: Seeds, w: int, h: int, params) -> Fields:
    x, y = grid.centered(w, h)

    # Domain warping is smooth, so compute it at reduced resolution and upsample.
    fw, fh = (
        max(64, round(w * params.field_resolution)),
        max(64, round(h * params.field_resolution)),
    )
    lx, ly = grid.centered(fw, fh)
    value, (wx, wy) = noise.domain_warp(
        seeds.rng("marble"),
        lx,
        ly,
        scale=params.warp_scale,
        strength=params.warp_strength,
        iterations=2,
        octaves=4,
    )
    marble = field.resize(value, w, h)
    flow = field.resize(np.hypot(wx, wy), w, h)

    rng = seeds.rng("cities")
    sun_x, sun_y = 0.0, params.horizon
    base_angle = rng.uniform(0, 2 * np.pi)
    sources = []
    for i, city in enumerate(CITIES):
        angle = base_angle + i * (np.pi / 2) + rng.uniform(-0.25, 0.25)
        dist = 1.4 + rng.uniform(0, 0.5)
        freq = params.wave_rings * city.bpm / 125.0
        phase = i * params.swing * np.pi
        sources.append((sun_x + dist * np.cos(angle), sun_y + dist * np.sin(angle), freq, phase))
    return Fields(x=x, y=y, marble=marble, flow=flow, sources=sources)


def waves(f: Fields, t: float) -> np.ndarray:
    """Interference of the four city waves; ``t`` in [0, 1) animates one seamless loop."""
    total = np.zeros_like(f.x)
    for k, (sx, sy, freq, phase) in enumerate(f.sources):
        d = np.hypot(f.x - sx, f.y - sy)
        # Integer cycles per loop keep the animation seamless.
        total += np.sin(2 * np.pi * (freq * d - (k + 1) * t) + phase)
    return total / len(f.sources)


def sky(f: Fields, params, t: float) -> np.ndarray:
    sun_d = np.hypot(f.x, f.y - params.horizon)
    wv = waves(f, t)
    tone = 0.8 * f.marble + params.wave_amount * wv + 0.35 * sun_d + 0.15 * f.flow
    img = palette.DUSK.ramp(tone * params.color_cycles, cyclic=True)
    # Shade by flow speed so the marbling reads as depth, not flat colour.
    shade = 0.78 + 0.32 * field.normalize(f.flow)
    img = img * shade[..., None]
    # Where the four cities' waves line up, a bright crest appears.
    crest = field.smoothstep(0.6, 0.9, wv) * params.wave_lines
    img = composite.blend(
        np.clip(img, 0, 1),
        palette.DUSK.ramp(tone * params.color_cycles + 0.5, cyclic=True),
        crest,
        mode="screen",
    )
    # Minimal: the sky calms into night away from the sun, leaving negative space.
    calm = field.smoothstep(0.3, 1.25, sun_d) * params.night
    night = color.solid(img.shape[1], img.shape[0], palette.DUSK.colors[0])
    return color.mix(np.clip(img, 0, 1), night, calm)


def sun(img: np.ndarray, f: Fields, params) -> np.ndarray:
    r = params.sun_radius
    cy = params.horizon - r * 0.15
    sdf = shapes.circle(f.x, f.y, 0.0, cy, r)
    d = np.hypot(f.x, f.y - cy) / r
    # Concentric bands that wobble with the marbling and the city waves.
    bands = d * 0.85 + 0.06 * f.marble + 0.04 * np.sin(2 * np.pi * (d * 6.0 + 0.5 * f.marble))
    rings = palette.SUN.ramp(bands, cyclic=False)
    img = composite.blend(img, rings, shapes.fill(sdf, 0.004))
    halo = shapes.glow(sdf, r * 0.9, power=1.6) * (1 - shapes.fill(sdf, 0.004))
    return composite.blend(
        img,
        color.solid(img.shape[1], img.shape[0], palette.SUN.colors[1]),
        halo * params.sun_glow,
        mode="screen",
    )


def ridge_line(seeds: Seeds, x: np.ndarray, params) -> np.ndarray:
    """Height of the mangrove ridge above the horizon for each x."""
    f = noise.FBM(seeds.rng("ridge"), octaves=4)
    row = x[0]
    height = 0.012 + 0.03 * field.normalize(f(row * 2.5, np.zeros_like(row)))
    return np.broadcast_to(params.horizon - height, x.shape)


def ridge(img: np.ndarray, f: Fields, top: np.ndarray, params) -> np.ndarray:
    land = shapes.fill(top - f.y, 0.003) * shapes.fill(f.y - params.horizon, 0.003)
    rim = shapes.glow(np.abs(f.y - top), 0.004, power=2.0) * shapes.fill(
        f.y - params.horizon, 0.002
    )
    w, h = img.shape[1], img.shape[0]
    img = composite.blend(img, color.solid(w, h, palette.RIM), rim * 0.6, mode="screen")
    return composite.blend(img, color.solid(w, h, palette.MANGROVE), land)


def fires(img: np.ndarray, seeds: Seeds, f: Fields, top: np.ndarray, params) -> np.ndarray:
    """Friends gathered along the shore: small fires and lanterns with soft glows."""
    rng = seeds.rng("friends")
    w, h = img.shape[1], img.shape[0]
    row = f.x[0]
    for _ in range(params.friends):
        # Friends gather along the dark shore, loosely clustered towards the middle.
        fx = float(np.clip(rng.normal(0.0, 0.5), -0.94, 0.94))
        col = int(np.clip(np.searchsorted(row, fx), 0, w - 1))
        fy = float(rng.uniform(top[0, col] + 0.004, params.horizon - 0.003))
        rad = rng.uniform(0.0025, 0.0055)
        tint = palette.FIRE[int(rng.integers(len(palette.FIRE)))]
        # Only evaluate a window around each light; full-frame SDFs would be wasteful.
        x0, x1 = max(0, col - w // 12), min(w, col + w // 12)
        rowc = int(np.clip(np.searchsorted(f.y[:, 0], fy), 0, h - 1))
        y0, y1 = max(0, rowc - h // 12), min(h, rowc + h // 12)
        sx, sy = f.x[y0:y1, x0:x1], f.y[y0:y1, x0:x1]
        sdf = shapes.circle(sx, sy, fx, fy, rad)
        alpha = np.maximum(shapes.fill(sdf, 0.002), shapes.glow(sdf, rad * 3, power=1.8) * 0.9)
        patch = img[y0:y1, x0:x1]
        img[y0:y1, x0:x1] = composite.blend(
            patch, color.solid(x1 - x0, y1 - y0, tint), alpha, mode="screen"
        )
    return img


def reflect(img: np.ndarray, seeds: Seeds, f: Fields, params, t: float) -> np.ndarray:
    """Mirror everything above the horizon into the lake, with ripples and depth."""
    w, h = img.shape[1], img.shape[0]
    below = f.y > params.horizon
    depth = np.where(below, f.y - params.horizon, 0.0).astype(np.float32)
    ripple = noise.FBM(seeds.rng("ripple"), octaves=3)
    phase = 2 * np.pi * t
    wobble = ripple(f.x * 3.0 + 0.4 * np.cos(phase), depth * 60.0 + 0.4 * np.sin(phase))
    mx = f.x + wobble * (0.004 + 0.05 * depth)
    my = 2 * params.horizon - f.y
    px, py = grid.centered_to_pixels(mx, my, w, h)
    mirrored = field.sample(img, px, py)
    deep = field.smoothstep(0.0, 1.0 - params.horizon, depth) * params.lake_depth
    lake = color.mix(mirrored * 0.82, color.solid(w, h, palette.LAKE), 0.25 + 0.6 * deep)
    # Thin horizontal glints, denser near the shore.
    glint = field.smoothstep(0.55, 0.9, np.abs(np.sin(depth * 900.0 + wobble * 6))) * 0.08
    lake = composite.blend(lake, mirrored, glint * (1 - deep), mode="screen")
    return np.where(below[..., None], lake, img).astype(np.float32)
