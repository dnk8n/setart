"""Colours of Kosi Bay at dusk: estuary teal, lake blue, mangrove shadow, sunset heat."""

from setart.blocks.color import Palette, hex_rgb

# Cyclic ramp used for the psychedelic marbling. Order matters: neighbouring stops blend.
DUSK = Palette.from_hex(
    "kosi-dusk",
    "#140b34",  # night over the lakes
    "#4b1d6e",  # violet
    "#b0157a",  # magenta
    "#ff5e5b",  # coral
    "#ff9f1c",  # dusk orange
    "#ffd46b",  # sand gold
    "#2ec4b6",  # estuary teal
    "#0e5a8a",  # lake blue
)

# Warm-only ramp for the sun's concentric rings.
SUN = Palette.from_hex("kosi-sun", "#fff1b8", "#ffd46b", "#ff9f1c", "#ff5e5b", "#e0306f")

LAKE = hex_rgb("#06324a")
MANGROVE = hex_rgb("#071a1f")
RIM = hex_rgb("#2ec4b6")
FIRE = (hex_rgb("#ffd46b"), hex_rgb("#ff9f1c"), hex_rgb("#ff5e5b"))
