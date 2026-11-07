from dataclasses import dataclass

import pytest

from setart import Artefact, RenderContext, Template, render
from setart.blocks import color


@dataclass
class P:
    hue: float = 0.5
    count: int = 3
    flag: bool = False
    sizes: tuple = (1, 2)


class Solid(Template):
    name = "solid"
    Params = P

    def render(self, ctx: RenderContext):
        w, h = ctx.size(40, 20)
        return [Artefact.still("img", color.solid(w, h, color.hsv(ctx.params.hue, 1, 1)))]


def test_param_coercion():
    p = Solid.make_params({"hue": "0.25", "count": "7", "flag": "yes", "sizes": "3,4,5"})
    assert (p.hue, p.count, p.flag, p.sizes) == (0.25, 7, True, (3, 4, 5))


def test_unknown_param_is_an_error():
    with pytest.raises(KeyError):
        Solid.make_params({"nope": "1"})


def test_scale_changes_resolution_only():
    arts, manifest = render(Solid, seed=0, scale=0.5)
    assert arts[0].size == (20, 10)
    assert manifest["template"] == "solid"


def test_cli_new_creates_a_renderable_album(tmp_path):
    from setart.cli import main
    from setart.core import loader

    assert main(["--albums", str(tmp_path), "new", "summer-haze"]) == 0
    template = loader.load("summer-haze", tmp_path)
    arts, _ = render(template, seed=3, scale=0.02)
    assert arts[0].format == "jpg"
