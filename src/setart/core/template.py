"""The Template contract.

A template is a Python class that turns ``(params, seed)`` into artefacts. It must be a
pure function of those inputs: no clock, no network, no files read at render time, no
global random state. That is what makes every render reproducible.

Minimal example::

    @dataclass
    class Params:
        hue: float = 0.6

    class MyCover(Template):
        name = "my-cover"
        version = "1"
        Params = Params

        def render(self, ctx: RenderContext) -> list[Artefact]:
            w, h = ctx.size(3000, 3000)
            img = blocks.color.solid(w, h, blocks.color.hsv(ctx.params.hue, 0.8, 0.9))
            return [Artefact.still("cover", img, format="jpg")]
"""

from __future__ import annotations

import dataclasses
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, ClassVar

from .artefact import Artefact
from .seed import Seeds


@dataclass
class NoParams:
    pass


@dataclass(frozen=True)
class RenderContext:
    """Everything a template may depend on while rendering."""

    seed: int
    params: Any
    scale: float = 1.0

    @property
    def seeds(self) -> Seeds:
        return Seeds(self.seed)

    def size(self, width: int, height: int) -> tuple[int, int]:
        """Nominal output size, multiplied by ``scale`` for quick previews.

        Templates should work in normalised coordinates (see ``blocks.grid``) so a
        preview is the same composition at a lower resolution.
        """
        return max(1, round(width * self.scale)), max(1, round(height * self.scale))


class Template(ABC):
    """Base class for every album template."""

    #: Short, unique, kebab-case identifier.
    name: ClassVar[str] = ""
    #: Bump when a change alters output for an existing seed.
    version: ClassVar[str] = "1"
    #: One-line human description.
    description: ClassVar[str] = ""
    #: Dataclass of tunable parameters. Every field needs a default.
    Params: ClassVar[type] = NoParams

    @abstractmethod
    def render(self, ctx: RenderContext) -> list[Artefact]:
        """Produce artefacts. Must be deterministic in ``ctx``."""

    # -- helpers ---------------------------------------------------------

    @classmethod
    def make_params(cls, overrides: dict[str, str] | None = None) -> Any:
        """Build a Params instance, coercing string overrides (from the CLI) to field types."""
        params = cls.Params()
        if not overrides:
            return params
        fields = {f.name: f for f in dataclasses.fields(params)}
        changes: dict[str, Any] = {}
        for key, raw in overrides.items():
            if key not in fields:
                known = ", ".join(sorted(fields)) or "(none)"
                raise KeyError(f"{cls.name} has no parameter {key!r}. Known: {known}")
            current = getattr(params, key)
            changes[key] = _coerce(raw, current)
        return dataclasses.replace(params, **changes)

    @classmethod
    def describe_params(cls) -> list[tuple[str, str, Any]]:
        return [
            (f.name, getattr(f.type, "__name__", str(f.type)), getattr(cls.Params(), f.name))
            for f in dataclasses.fields(cls.Params())
        ]


def _coerce(raw: str, current: Any) -> Any:
    if isinstance(current, bool):
        if raw.lower() in {"1", "true", "yes", "on"}:
            return True
        if raw.lower() in {"0", "false", "no", "off"}:
            return False
        raise ValueError(f"not a boolean: {raw!r}")
    if isinstance(current, int):
        return int(raw)
    if isinstance(current, float):
        return float(raw)
    if isinstance(current, (tuple, list)):
        parts = [p.strip() for p in raw.split(",") if p.strip()]
        sample = current[0] if current else ""
        return type(current)(_coerce(p, sample) for p in parts)
    return raw
