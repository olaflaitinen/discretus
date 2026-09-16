"""Seeded randomness.

Every randomized routine in the library takes a seed and routes its
randomness through this module, so that a result computed on one machine can
be reproduced exactly on another. When the caller supplies no seed the
library falls back to :attr:`~discretus.config.Config.default_seed`, and
only when that is also unset does the routine become nondeterministic.
"""

from __future__ import annotations

import random
from typing import Any, Iterable, List, Optional, Sequence, TypeVar

from ..config import get_config
from ..exceptions import DomainError
from ..typing import Seed
from ..validation import require_seed

__all__ = ["rng", "SeededRandom", "deterministic_sample", "deterministic_shuffle"]

T = TypeVar("T")


def rng(seed: Seed = None) -> random.Random:
    """Return a generator seeded by ``seed`` or by the configured default.

    Args:
        seed: Explicit seed, or ``None`` to consult the configuration.

    Returns:
        An independent :class:`random.Random` instance. The library never
        touches the global random state, so a caller's own random stream is
        unaffected.

    Example:
        >>> rng(7).random() == rng(7).random()
        True
    """
    require_seed(seed)
    effective = seed if seed is not None else get_config().default_seed
    return random.Random(effective)  # nosec B311


class SeededRandom:
    """A small, explicit interface over a seeded generator.

    Only the operations the library needs are exposed, which keeps the
    randomized routines easy to audit for reproducibility.

    Args:
        seed: Explicit seed, or ``None`` to consult the configuration.

    Example:
        >>> source = SeededRandom(2024)
        >>> source.integer(0, 10) == SeededRandom(2024).integer(0, 10)
        True
    """

    def __init__(self, seed: Seed = None) -> None:
        self._seed = seed
        self._random = rng(seed)

    @property
    def seed(self) -> Optional[int]:
        """Return the seed this instance was created with."""
        return self._seed

    def integer(self, low: int, high: int) -> int:
        """Return a uniform integer in the inclusive range ``[low, high]``."""
        if low > high:
            raise DomainError(f"empty range [{low}, {high}]")
        return self._random.randint(low, high)

    def unit(self) -> float:
        """Return a uniform float in the half open interval ``[0, 1)``."""
        return self._random.random()

    def bernoulli(self, probability: float) -> bool:
        """Return ``True`` with the given probability."""
        if not 0.0 <= probability <= 1.0:
            raise DomainError(f"probability must lie in [0, 1], got {probability}")
        return self._random.random() < probability

    def choice(self, population: Sequence[T]) -> T:
        """Return one item chosen uniformly at random."""
        if not population:
            raise DomainError("cannot choose from an empty population")
        return population[self._random.randrange(len(population))]

    def sample(self, population: Sequence[T], size: int) -> List[T]:
        """Return ``size`` distinct items chosen uniformly at random."""
        if size < 0 or size > len(population):
            raise DomainError(f"cannot sample {size} of {len(population)} items")
        return self._random.sample(list(population), size)

    def shuffled(self, population: Iterable[T]) -> List[T]:
        """Return a shuffled copy of the items."""
        items = list(population)
        self._random.shuffle(items)
        return items

    def permutation(self, size: int) -> List[int]:
        """Return a uniformly random permutation of ``range(size)``."""
        if size < 0:
            raise DomainError(f"size must be non negative, got {size}")
        return self.shuffled(range(size))

    def __repr__(self) -> str:
        return f"SeededRandom(seed={self._seed!r})"


def deterministic_sample(
    population: Sequence[T],
    size: int,
    seed: Seed = None,
) -> List[T]:
    """Return a reproducible sample of distinct items.

    Example:
        >>> sample = deterministic_sample(list(range(100)), 3, seed=1)
        >>> sample == deterministic_sample(list(range(100)), 3, seed=1)
        True
        >>> len(set(sample))
        3
    """
    return SeededRandom(seed).sample(population, size)


def deterministic_shuffle(population: Iterable[Any], seed: Seed = None) -> List[Any]:
    """Return a reproducible shuffle of the items.

    Example:
        >>> deterministic_shuffle([1, 2, 3, 4], seed=5) == deterministic_shuffle([1, 2, 3, 4], seed=5)
        True
    """
    return SeededRandom(seed).shuffled(population)
