"""Writing artefacts to disk, byte-for-byte reproducibly.

Exporters strip anything that varies between runs (timestamps, encoder metadata) so
the same seed always yields the same file hash on the same platform and library versions.
"""

from __future__ import annotations

import hashlib
import io
import json
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

from .artefact import Artefact

EXTENSIONS = {"png": "png", "jpg": "jpg", "gif": "gif"}


def to_uint8(frame: np.ndarray) -> np.ndarray:
    """Float [0, 1] -> uint8 with explicit rounding (no platform-dependent truncation)."""
    if frame.dtype == np.uint8:
        return frame
    return np.clip(np.rint(np.asarray(frame, dtype=np.float64) * 255.0), 0, 255).astype(np.uint8)


def to_pil(frame: np.ndarray) -> Image.Image:
    arr = to_uint8(frame)
    if arr.ndim == 2:
        return Image.fromarray(arr, mode="L")
    return Image.fromarray(arr, mode="RGBA" if arr.shape[2] == 4 else "RGB")


def encode(artefact: Artefact) -> bytes:
    fmt = artefact.format
    opts = artefact.options
    if fmt == "png":
        buf = io.BytesIO()
        to_pil(artefact.frames[0]).save(
            buf, format="PNG", compress_level=opts.get("compress_level", 6)
        )
        return buf.getvalue()
    if fmt == "jpg":
        return _encode_jpeg(artefact.frames[0], opts)
    if fmt == "gif":
        frames = [to_pil(f).convert("RGB") for f in artefact.frames]
        colors = opts.get("colors", 256)
        # Build one palette from the first frame so colours stay stable across the loop.
        palette_src = frames[0].quantize(colors=colors, method=Image.Quantize.MEDIANCUT, dither=0)
        quantized = [f.quantize(palette=palette_src, dither=Image.Dither.NONE) for f in frames]
        buf = io.BytesIO()
        quantized[0].save(
            buf,
            format="GIF",
            save_all=len(quantized) > 1,
            append_images=quantized[1:],
            duration=opts.get("duration_ms", 80),
            loop=opts.get("loop", 0),
            optimize=False,
            disposal=2,
        )
        return buf.getvalue()
    raise ValueError(f"unsupported format: {fmt}")


def _jpeg_bytes(img: Image.Image, quality: int) -> bytes:
    # Full-resolution colour at high quality; standard 4:2:0 chroma below that.
    kwargs = {"quality": quality, "subsampling": 0 if quality >= 90 else 2, "progressive": False}
    buf = io.BytesIO()
    try:
        img.save(buf, format="JPEG", optimize=True, **kwargs)
    except OSError:
        # libjpeg's optimiser can fail on extremely noisy images; fall back to standard tables.
        buf = io.BytesIO()
        img.save(buf, format="JPEG", optimize=False, **kwargs)
    return buf.getvalue()


def _encode_jpeg(frame: np.ndarray, opts: dict[str, Any]) -> bytes:
    img = to_pil(frame).convert("RGB")
    quality = int(opts.get("quality", 92))
    min_quality = int(opts.get("min_quality", 70))
    max_bytes = opts.get("max_bytes")
    while True:
        data = _jpeg_bytes(img, quality)
        if not max_bytes or len(data) <= max_bytes:
            return data
        if quality <= min_quality:
            raise ValueError(
                f"JPEG is {len(data)} bytes at quality {quality}, over max_bytes={max_bytes}. "
                "Lower min_quality, reduce the size, or reduce fine detail such as grain."
            )
        quality = max(min_quality, quality - 2)


def _jsonable(value: Any) -> Any:
    if is_dataclass(value) and not isinstance(value, type):
        return asdict(value)
    if isinstance(value, (tuple, list)):
        return [_jsonable(v) for v in value]
    if isinstance(value, dict):
        return {k: _jsonable(v) for k, v in value.items()}
    if isinstance(value, (np.integer, np.floating)):
        return value.item()
    return value


def write(
    artefacts: list[Artefact], out_dir: Path, manifest: dict[str, Any] | None = None
) -> list[Path]:
    """Write artefacts plus a ``manifest.json`` recording how to reproduce them."""
    out_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    entries = []
    for art in artefacts:
        data = encode(art)
        path = out_dir / f"{art.name}.{EXTENSIONS[art.format]}"
        path.write_bytes(data)
        paths.append(path)
        entries.append(
            {
                "file": path.name,
                "format": art.format,
                "size": list(art.size),
                "frames": len(art.frames),
                "bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
                "metadata": _jsonable(art.metadata),
            }
        )
    doc = {**_jsonable(manifest or {}), "artefacts": entries}
    (out_dir / "manifest.json").write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
    return paths
