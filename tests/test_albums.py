"""Every album must load and render deterministically. New albums are picked up automatically."""

import hashlib
import subprocess
import sys

import pytest

from setart.core import export, loader
from setart.core.render import render

from .conftest import ALBUMS, ROOT

ALBUM_DIRS = loader.album_dirs(ALBUMS)
SCALE = 0.04  # tiny renders keep the suite fast


def _hashes(template, seed):
    arts, _ = render(template, seed, scale=SCALE)
    return [hashlib.sha256(export.encode(a)).hexdigest() for a in arts]


def test_there_is_at_least_one_album():
    assert ALBUM_DIRS


@pytest.mark.parametrize("album", ALBUM_DIRS, ids=lambda p: p.name)
def test_album_is_deterministic(album):
    template = loader.load(album, ALBUMS)
    assert template.name and template.description
    assert _hashes(template, 1) == _hashes(template, 1)
    assert _hashes(template, 1) != _hashes(template, 2)


@pytest.mark.parametrize("album", ALBUM_DIRS, ids=lambda p: p.name)
def test_album_is_deterministic_across_processes(album):
    """Catches hidden per-process state such as Python's salted ``hash``."""
    code = (
        "import hashlib,sys;from setart.core import export,loader;"
        "from setart.core.render import render;"
        f"t=loader.load({str(album)!r});a,_=render(t,1,scale={SCALE});"
        "print(','.join(hashlib.sha256(export.encode(x)).hexdigest() for x in a))"
    )
    out = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, check=True, cwd=ROOT
    ).stdout.strip()
    assert out.split(",") == _hashes(loader.load(album, ALBUMS), 1)
