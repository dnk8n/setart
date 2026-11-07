"""Kosi Bay festival of friends: psychedelic, abstract SoundCloud cover. See brief.md."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from setart import Artefact, RenderContext, Template
from setart.blocks import post
from setart.core.targets import SOUNDCLOUD

from . import scene


@dataclass
class Params:
    horizon: float = 0.22  # y of the horizon in centred coords (0 = middle)
    warp_scale: float = 0.9  # size of the marbling (lower = bigger shapes)
    warp_strength: float = 0.75  # how much the marbling folds on itself
    field_resolution: float = 0.5  # marbling computed at this fraction of output size
    color_cycles: float = 1.2  # times the palette repeats across the tone range
    wave_rings: float = 7.0  # ring density of the city waves (techno / minimal)
    wave_amount: float = 0.22  # how strongly the waves bend the colour bands
    swing: float = 0.33  # phase offset between city waves (garage swing)
    wave_lines: float = 0.35  # bright crests where the city waves align
    sun_radius: float = 0.34
    night: float = 0.85  # how much the upper sky fades to night (minimal)
    sun_glow: float = 0.55  # soulful warmth
    lake_depth: float = 0.8  # deep: how dark and blue the lake gets
    friends: int = 23  # fires and lanterns on the shore
    grain: float = 0.018
    gif_frames: int = 0  # >0 also renders an animated loop.gif
    gif_size: int = 600


class KosiBayFriends(Template):
    name = "kosi-bay-friends"
    version = "1"
    description = "Psychedelic abstract dusk over Kosi Bay with four city sound waves."
    Params = Params

    def frame(self, ctx: RenderContext, w: int, h: int, t: float, fields=None) -> np.ndarray:
        p, seeds = ctx.params, ctx.seeds
        f = fields or scene.sky_field(seeds, w, h, p)
        img = scene.sky(f, p, t)
        img = scene.sun(img, f, p)
        top = scene.ridge_line(seeds, f.x, p)
        img = scene.ridge(img, f, top, p)
        img = scene.fires(img, seeds, f, top, p)
        img = scene.reflect(img, seeds, f, p, t)
        img = post.bloom(img, threshold=0.8, radius_frac=0.008, strength=0.35)
        img = post.chromatic_aberration(img, 0.0025)
        img = post.vignette(img, strength=0.45)
        return post.grain(img, seeds.rng(f"grain-{t:.6f}"), p.grain)

    def render(self, ctx: RenderContext) -> list[Artefact]:
        w, h = ctx.size(SOUNDCLOUD.width, SOUNDCLOUD.height)
        cover = self.frame(ctx, w, h, t=0.0)
        out = [
            Artefact.still("cover", cover, format="jpg", **SOUNDCLOUD.options),
            Artefact.still("cover", cover, format="png"),
        ]
        if ctx.params.gif_frames > 0:
            gw, gh = ctx.size(ctx.params.gif_size, ctx.params.gif_size)
            fields = scene.sky_field(ctx.seeds, gw, gh, ctx.params)
            n = ctx.params.gif_frames
            frames = [self.frame(ctx, gw, gh, i / n, fields) for i in range(n)]
            out.append(Artefact.animation("loop", frames, duration_ms=90))
        return out


TEMPLATE = KosiBayFriends
