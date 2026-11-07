# Contributing: humans and AI

This guide is written for anyone extending setart, including an AI agent that has been
handed a brief. Read it fully before writing code.

## The rules

1. **No static assets.** Never add image, texture, font or data files that end up in the
   picture. Everything visible must come from code. Calling out to C or another binary is
   fine if it is deterministic and documented.
2. **Deterministic.** Rendering must be a pure function of `(template version, params, seed)`.
   * Get randomness only from `ctx.seeds.rng("name")` or `ctx.seeds.child("name")`.
   * Never use `random`, `np.random.<function>`, `hash()`, time, the network, or
     environment variables while rendering.
   * Give each random element its own named stream, so adding one does not shift others.
3. **Resolution independent.** Work in normalised coordinates (`blocks.grid.centered` or
   `blocks.grid.uv`) and get the pixel size from `ctx.size(...)`, so `--scale 0.25`
   previews the same composition.
4. **Bump `version`** on a template when a change alters existing output for a seed.

## Where code goes

| You are writing... | Put it in |
| --- | --- |
| Something only this cover needs (its palette, motifs, composition) | `albums/<album>/` |
| A generic technique a second album could reuse (a noise type, a blend mode, an SDF) | `src/setart/blocks/` |
| A change to what a template is, how output is written, or the CLI | `src/setart/core/` or `cli.py` (rare, keep it small) |
| A named output size or platform constraint | `src/setart/core/targets.py` |

When unsure, start in the album. Promote code to `blocks/` when a second album wants it,
with a test in `tests/test_blocks.py`. Blocks must be pure functions on numpy arrays (or
small classes seeded with an explicit `np.random.Generator`).

Conventions: images are `(H, W, 3)` `float32` in `[0, 1]`; scalar fields are `(H, W)`.

## Turning a brief into an album

1. `uv run setart new <album-name>` to create a working starter.
2. Paste the brief into `brief.md`, then fill in the interpretation table: one row per
   tag or idea, saying what it looks like and which function or parameter implements it.
   This table is what lets the next person change one idea without breaking others.
3. Build the image as a stack of layers, one function per idea, in a `scene.py`.
   See `albums/kosi_bay_friends/` for the pattern.
4. Expose the knobs a person would want to tune as fields on `Params`, with defaults.
5. Preview with `--scale 0.25` across a few seeds; make sure seeds give variety, not noise.
6. Render full size and check the platform constraints (e.g. SoundCloud: 2MB JPEG).
7. Run `uv run pytest` and `uv run ruff check .`. New albums are tested automatically.

## Checklist before opening a pull request

- [ ] `uv run pytest -q` passes, including the cross-process determinism test.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] No binary or asset files added; `out/` is not committed.
- [ ] `brief.md` explains how each idea in the brief maps to code.
- [ ] Generic code added to `blocks/` has a test.
