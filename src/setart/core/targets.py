"""Named output targets: common platform sizes and constraints.

Templates may use these or define their own; nothing in core depends on them.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .artefact import Format


@dataclass(frozen=True)
class Target:
    name: str
    width: int
    height: int
    format: Format
    options: dict[str, Any] = field(default_factory=dict)
    notes: str = ""


SOUNDCLOUD = Target(
    name="soundcloud",
    width=3000,
    height=3000,
    format="jpg",
    # SoundCloud uploads must be 2MB or less and display best at 800x800 or larger.
    # 3000x3000 also meets SoundCloud's distribution minimum for release artwork.
    options={"quality": 95, "min_quality": 75, "max_bytes": 2 * 1000 * 1000},
    notes="Square cover art, 3000x3000 JPEG under 2MB.",
)

SQUARE_PREVIEW = Target(name="preview", width=800, height=800, format="png")

TARGETS: dict[str, Target] = {t.name: t for t in (SOUNDCLOUD, SQUARE_PREVIEW)}
