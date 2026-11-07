"""What a template produces: one or more artefacts, each one or more frames."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

import numpy as np

Format = Literal["png", "jpg", "gif"]


@dataclass
class Artefact:
    """A single output file.

    ``frames`` are float arrays shaped (H, W, 3) or (H, W, 4) with values in [0, 1].
    A still image has one frame; an animated GIF has many.

    ``options`` are passed to the exporter, for example:

    * jpg: ``quality`` (int), ``max_bytes`` (int, lowers quality until the file fits),
      ``min_quality`` (int, fail rather than go below this)
    * gif: ``duration_ms`` (int per frame), ``loop`` (int, 0 = forever)
    * png: ``compress_level`` (0-9)
    """

    name: str
    frames: list[np.ndarray]
    format: Format = "png"
    options: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def size(self) -> tuple[int, int]:
        h, w = self.frames[0].shape[:2]
        return w, h

    @classmethod
    def still(
        cls, name: str, image: np.ndarray, format: Format = "png", **options: Any
    ) -> Artefact:
        return cls(name=name, frames=[image], format=format, options=options)

    @classmethod
    def animation(
        cls,
        name: str,
        frames: list[np.ndarray],
        duration_ms: int = 80,
        loop: int = 0,
        **options: Any,
    ) -> Artefact:
        return cls(
            name=name,
            frames=frames,
            format="gif",
            options={"duration_ms": duration_ms, "loop": loop, **options},
        )
