"""Deterministic randomness.

Every random decision in setart flows from one integer seed. Code never calls
``random``, ``np.random.<func>`` or anything time based. Instead it asks a
:class:`Seeds` object for a named stream::

    rng = seeds.rng("stars")        # numpy Generator, always the same for this seed + name
    sub = seeds.child("sky")        # an independent namespace for a sub-component

Naming streams (rather than drawing from one shared generator) means adding a
new random element to a template does not shift every other element: the
"stars" stream is unaffected when you add a "clouds" stream.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field

import numpy as np


def _name_key(name: str) -> tuple[int, ...]:
    """Stable integer key for a stream name (Python's ``hash`` is salted per process)."""
    digest = hashlib.sha256(name.encode("utf-8")).digest()
    return tuple(int.from_bytes(digest[i : i + 4], "little") for i in range(0, 16, 4))


@dataclass(frozen=True)
class Seeds:
    """A namespace of reproducible random streams derived from one seed."""

    seed: int
    path: tuple[str, ...] = field(default=())

    def child(self, name: str) -> Seeds:
        """An independent namespace, e.g. one per layer or component."""
        return Seeds(self.seed, (*self.path, name))

    def sequence(self, name: str) -> np.random.SeedSequence:
        key: tuple[int, ...] = ()
        for part in (*self.path, name):
            key += _name_key(part)
        return np.random.SeedSequence(entropy=self.seed, spawn_key=key)

    def rng(self, name: str) -> np.random.Generator:
        """A fresh numpy Generator for ``name``. Calling twice gives two identical streams."""
        return np.random.Generator(np.random.PCG64(self.sequence(name)))

    def integer(self, name: str, bits: int = 32) -> int:
        """A single derived integer, handy for seeding external tools."""
        return int(self.sequence(name).generate_state(1, dtype=np.uint64)[0] >> (64 - bits))
