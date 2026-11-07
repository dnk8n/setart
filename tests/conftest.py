from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
ALBUMS = ROOT / "albums"


@pytest.fixture
def albums_dir() -> Path:
    return ALBUMS
