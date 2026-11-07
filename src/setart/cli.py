"""Command line interface: ``setart list``, ``setart info <album>``, ``setart render <album>``."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from .core import loader
from .core.render import render_to_dir


def _parse_sets(pairs: list[str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for pair in pairs:
        if "=" not in pair:
            raise SystemExit(f"--set expects key=value, got {pair!r}")
        key, value = pair.split("=", 1)
        out[key.strip()] = value.strip()
    return out


def cmd_list(args: argparse.Namespace) -> int:
    root = Path(args.albums)
    dirs = loader.album_dirs(root)
    if not dirs:
        print(f"no albums found in {root}")
        return 1
    for path in dirs:
        tpl = loader.load(path, root)
        print(f"{path.name:<28} {tpl.name} v{tpl.version}  {tpl.description}")
    return 0


def cmd_info(args: argparse.Namespace) -> int:
    tpl = loader.load(args.album, Path(args.albums))
    print(f"{tpl.name} v{tpl.version}\n{tpl.description}\n\nparameters:")
    for name, typ, default in tpl.describe_params():
        print(f"  {name:<24} {typ:<10} default={default!r}")
    return 0


def cmd_render(args: argparse.Namespace) -> int:
    root = Path(args.albums)
    path = loader.resolve(args.album, root)
    tpl = loader.load(path, root)
    out = Path(args.out) / path.name / f"seed-{args.seed}"
    if args.scale != 1.0:
        out = out.with_name(out.name + f"-x{args.scale:g}")
    start = time.perf_counter()
    paths = render_to_dir(tpl, args.seed, out, _parse_sets(args.set), args.scale)
    elapsed = time.perf_counter() - start
    for p in paths:
        print(p)
    print(f"rendered {len(paths)} artefact(s) in {elapsed:.1f}s -> {out}", file=sys.stderr)
    return 0


ALBUM_SKELETON = '''"""{title}. See brief.md."""

from __future__ import annotations

from dataclasses import dataclass

from setart import Artefact, RenderContext, Template
from setart.blocks import color, grid, noise, post
from setart.core.targets import SOUNDCLOUD


@dataclass
class Params:
    scale: float = 2.0
    grain: float = 0.015


class {cls}(Template):
    name = "{slug}"
    version = "1"
    description = "TODO: one line describing this cover."
    Params = Params

    def render(self, ctx: RenderContext) -> list[Artefact]:
        p, seeds = ctx.params, ctx.seeds
        w, h = ctx.size(SOUNDCLOUD.width, SOUNDCLOUD.height)
        x, y = grid.centered(w, h)
        value, _ = noise.domain_warp(seeds.rng("field"), x, y, scale=p.scale)
        palette = color.Palette.from_hex("todo", "#101030", "#e04070", "#ffd060")
        img = palette.ramp(value * 0.5 + 0.5)
        img = post.grain(img, seeds.rng("grain"), p.grain)
        return [Artefact.still("cover", img, format="jpg", **SOUNDCLOUD.options)]


TEMPLATE = {cls}
'''

BRIEF_SKELETON = """# Brief: {title}

> Paste the original brief here.

## Interpretation

| Tag | Visual idea | Where |
| --- | --- | --- |
| | | |
"""


def cmd_new(args: argparse.Namespace) -> int:
    slug = args.name.strip().lower().replace("_", "-")
    if not slug.replace("-", "").isalnum():
        raise SystemExit("album names use letters, digits and dashes, e.g. 'summer-haze'")
    path = Path(args.albums) / slug.replace("-", "_")
    if path.exists():
        raise SystemExit(f"{path} already exists")
    path.mkdir(parents=True)
    title = slug.replace("-", " ").capitalize()
    cls = "".join(part.capitalize() for part in slug.split("-"))
    (path / "__init__.py").write_text(ALBUM_SKELETON.format(title=title, cls=cls, slug=slug))
    (path / "brief.md").write_text(BRIEF_SKELETON.format(title=title))
    print(f"created {path}. Try: setart render {slug} --scale 0.25")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="setart", description=__doc__)
    parser.add_argument(
        "--albums",
        default=str(loader.DEFAULT_ALBUMS_DIR),
        help="albums directory (default: ./albums or $SETART_ALBUMS)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="list albums").set_defaults(func=cmd_list)

    info = sub.add_parser("info", help="show an album's parameters")
    info.add_argument("album")
    info.set_defaults(func=cmd_info)

    new = sub.add_parser("new", help="create a new album from a starter template")
    new.add_argument("name", help="kebab-case album name")
    new.set_defaults(func=cmd_new)

    render = sub.add_parser("render", help="render an album")
    render.add_argument("album", help="album folder name or path")
    render.add_argument("--seed", type=int, default=0)
    render.add_argument("--out", default="out")
    render.add_argument(
        "--scale",
        type=float,
        default=1.0,
        help="resolution multiplier for quick previews, e.g. 0.25",
    )
    render.add_argument(
        "--set",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="override a template parameter (repeatable)",
    )
    render.set_defaults(func=cmd_render)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
