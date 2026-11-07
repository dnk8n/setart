# Brief: Kosi Bay festival of friends

> Make me a psychedelic album art cover that is suitable for SoundCloud upload.
> Music styles: Detroit, Jersey, New York, London; garage, techno, deep, soulful, minimal.
> Theme: festival of friends in rural Kosi Bay, South Africa. Style: abstract.
> Keep it abstract, no text.

## Interpretation

How each tag maps to code, so the next person (or AI) can change one idea without
breaking the others.

| Tag | Visual idea | Where |
| --- | --- | --- |
| psychedelic | Iterated domain-warped noise mapped through a cyclic palette, so colour bands melt into each other. | `scene.sky_field`, `palette.DUSK` |
| Detroit, Jersey, New York, London | Four sound-wave sources ripple across the sky and interfere. Each city's ring spacing comes from a typical tempo of its scene. | `CITIES` in `scene.py` |
| techno, minimal | Tight, regular wave rings; a calm, low horizon leaves negative space in the lake. | `Params.wave_rings`, `Params.horizon` |
| garage | Swing: each city's wave starts at a slightly shifted phase. | `Params.swing` |
| deep | The lake darkens and turns blue with depth. | `Params.lake_depth` |
| soulful | A warm, glowing half-set sun at the centre. | `scene.sun` |
| festival of friends | Small fires and lanterns gathered along the shore, reflected in the water. | `scene.fires`, `Params.friends` |
| rural Kosi Bay | Palette from the estuary, lakes and dusk; a low mangrove ridge on the horizon; the lake mirrors the sky. | `palette.py`, `scene.ridge`, `scene.reflect` |

## Outputs

* `cover.jpg`: 3000 x 3000 JPEG for SoundCloud (meets the 3000 px release artwork minimum).
* `cover.png`: lossless master.
* `loop.gif`: optional animated loop of the waves, enable with `--set gif_frames=24`.

## Rendering

```bash
uv run setart render kosi-bay-friends --seed 2
```

Seed 2 was the first pick. Full size takes about 30 seconds and the JPEG lands just under
SoundCloud's 2MB upload limit.
