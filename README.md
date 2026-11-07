# setart

Deterministic, code-only generative album art.

Every image is drawn by Python code from a seed. There are no static assets: no photos,
no stock textures, no fonts pulled from disk. The same album, seed and parameters always
produce the same file, so a cover can be reproduced, tweaked and versioned like code.

## Quick start

```bash
uv sync                                            # install (Python 3.11+)
uv run setart list                                 # see the albums
uv run setart render kosi-bay-friends --seed 2     # full-size cover into out/
uv run setart render kosi-bay-friends --seed 2 --scale 0.25   # fast preview
```

Output lands in `out/<album>/seed-<n>/` with a `manifest.json` that records the template
version, seed, parameters, library versions and a SHA-256 of every file.

Try seeds until one feels right, then tune it:

```bash
uv run setart info kosi-bay-friends                # list tunable parameters
uv run setart render kosi-bay-friends --seed 2 --set color_cycles=2 --set friends=40
uv run setart render kosi-bay-friends --seed 2 --set gif_frames=24   # also an animated loop
```

## Start a new album

```bash
uv run setart new summer-haze      # creates albums/summer_haze/ with a working starter
uv run setart render summer-haze --scale 0.25
```

Then edit `albums/summer_haze/__init__.py`, and write down what the brief means visually
in `albums/summer_haze/brief.md`.

## How it is organised

```
src/setart/
  core/        contracts: Template, RenderContext, Seeds, Artefact, exporters, loader
  blocks/      reusable building blocks: noise, colour, compositing, shapes, post effects
  cli.py       setart list | info | new | render
albums/
  kosi_bay_friends/   one folder per album: bespoke code, palette and brief
tests/         every album is automatically checked for determinism
docs/          CONTRIBUTING.md: how humans and AI extend the framework
```

* **Core** is small and stable. It defines what a template is and how output is written.
* **Blocks** are generic tools any album can use. Code moves here once two albums need it.
* **Albums** hold everything specific to one cover.

A template returns a list of artefacts. Each artefact is PNG, JPG or GIF, still or
animated, at any size; how many and which is up to the template.

## Determinism

* All randomness comes from `ctx.seeds.rng("<name>")`, named streams derived from the seed.
* Exporters write no timestamps or variable metadata.
* Tests render every album twice, in two processes, and compare file hashes.

Renders are byte-identical on the same platform and library versions. Across different
CPUs or numpy/Pillow versions, floating point can differ in the last bits, so the
manifest records the environment alongside each hash.

## Albums

| Album | Description |
| --- | --- |
| [kosi_bay_friends](albums/kosi_bay_friends/brief.md) | Psychedelic abstract dusk over Kosi Bay; four city sound waves. SoundCloud cover. |

## License

MIT
