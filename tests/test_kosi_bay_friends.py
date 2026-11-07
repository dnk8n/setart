from setart.core import loader
from setart.core.render import render

from .conftest import ALBUMS


def test_cover_outputs_and_optional_gif():
    t = loader.load("kosi_bay_friends", ALBUMS)
    arts, _ = render(t, 1, scale=0.04)
    assert sorted(f"{a.name}.{a.format}" for a in arts) == ["cover.jpg", "cover.png"]
    assert arts[0].size == (120, 120)

    arts, _ = render(t, 1, {"gif_frames": "3", "gif_size": "200"}, scale=0.2)
    gif = [a for a in arts if a.format == "gif"][0]
    assert len(gif.frames) == 3 and gif.size == (40, 40)
