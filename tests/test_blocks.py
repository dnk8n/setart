import numpy as np

from setart import Seeds
from setart.blocks import color, composite, field, grid, noise


def test_perlin_deterministic_and_bounded():
    x, y = grid.uv(64, 64)
    a = noise.Perlin(Seeds(3).rng("n"))(x * 8, y * 8)
    b = noise.Perlin(Seeds(3).rng("n"))(x * 8, y * 8)
    assert np.array_equal(a, b)
    assert np.abs(a).max() < 1.0


def test_domain_warp_shape():
    x, y = grid.centered(32, 48)
    value, (wx, wy) = noise.domain_warp(Seeds(1).rng("w"), x, y)
    assert value.shape == wx.shape == wy.shape == (48, 32)


def test_palette_ramp_endpoints_and_cycle():
    p = color.Palette.from_hex("bw", "#000000", "#ffffff")
    out = p.ramp(np.array([[0.0, 1.0]]))
    assert np.allclose(out[0, 0], 0) and np.allclose(out[0, 1], 1)
    cyc = p.ramp(np.array([[0.0, 1.0]]), cyclic=True)
    assert np.allclose(cyc[0, 0], cyc[0, 1])


def test_blend_modes_stay_in_range():
    base = np.random.default_rng(0).random((4, 4, 3)).astype(np.float32)
    layer = np.random.default_rng(1).random((4, 4, 3)).astype(np.float32)
    for mode in composite.MODES:
        out = composite.blend(base, layer, 0.5, mode)
        assert out.min() >= 0 and out.max() <= 1


def test_box_blur_preserves_constant():
    img = np.full((20, 30, 3), 0.25, dtype=np.float32)
    assert np.allclose(field.box_blur(img, 3), 0.25, atol=1e-5)
