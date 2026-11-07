"""Reusable, generic building blocks.

Everything here is a pure function (or a small class seeded explicitly) operating on
numpy float arrays in [0, 1]. Images are (H, W, 3) float32; scalar fields are (H, W).

Put code here when it is useful to more than one album. Album-specific ideas live in
the album's own folder until a second album wants them.
"""

from . import color, composite, field, grid, noise, post, shapes

__all__ = ["color", "composite", "field", "grid", "noise", "post", "shapes"]
