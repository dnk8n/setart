"""Framework core: the contracts every template relies on. Keep this small and stable."""

from .artefact import Artefact
from .render import render, render_to_dir
from .seed import Seeds
from .targets import TARGETS, Target
from .template import RenderContext, Template

__all__ = [
    "Artefact",
    "RenderContext",
    "Seeds",
    "TARGETS",
    "Target",
    "Template",
    "render",
    "render_to_dir",
]
