"""setart: deterministic, code-only generative album art.

Public API for template authors::

    from setart import Artefact, RenderContext, Template, blocks
"""

from . import blocks
from .core import TARGETS, Artefact, RenderContext, Seeds, Target, Template, render, render_to_dir

__all__ = [
    "TARGETS",
    "Artefact",
    "RenderContext",
    "Seeds",
    "Target",
    "Template",
    "blocks",
    "render",
    "render_to_dir",
]
