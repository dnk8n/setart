import io

import numpy as np
import pytest
from PIL import Image

from setart import Artefact
from setart.core import export


def _img(seed=0, size=64):
    return np.random.default_rng(seed).random((size, size, 3)).astype(np.float32)


def test_png_bytes_are_reproducible():
    a = export.encode(Artefact.still("a", _img()))
    b = export.encode(Artefact.still("a", _img()))
    assert a == b


def test_jpeg_respects_max_bytes():
    smooth = np.linspace(0, 1, 256 * 256 * 3, dtype=np.float32).reshape(256, 256, 3)
    data = export.encode(Artefact.still("a", smooth, "jpg", quality=95, max_bytes=20_000))
    assert len(data) <= 20_000


def test_jpeg_refuses_to_degrade_below_min_quality():
    with pytest.raises(ValueError):
        export.encode(Artefact.still("a", _img(size=256), "jpg", max_bytes=1000, min_quality=90))


def test_gif_animation_has_all_frames():
    frames = [_img(i, 32) for i in range(5)]
    data = export.encode(Artefact.animation("loop", frames))
    gif = Image.open(io.BytesIO(data))
    assert gif.n_frames == 5


def test_write_creates_manifest(tmp_path):
    paths = export.write([Artefact.still("x", _img())], tmp_path, {"seed": 1})
    assert paths[0].name == "x.png"
    assert (tmp_path / "manifest.json").is_file()
