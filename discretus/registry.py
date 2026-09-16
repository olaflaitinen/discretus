# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""A small named registry used for pluggable backends and formats.

The visualization package registers its rendering backends here and the
input and output package registers its interchange formats. Keeping the
mechanism in one place means the lookup, the error messages, and the
deterministic ordering behave identically everywhere.

Example:
    >>> registry = Registry("demo")
    >>> @registry.register("upper")
    ... def shout(text: str) -> str:
    ...     return text.upper()
    >>> registry.get("upper")("abc")
    'ABC'
    >>> registry.names()
    ['upper']
"""

from __future__ import annotations

from typing import Callable, Dict, Generic, Iterator, List, Optional, TypeVar

from .exceptions import ValidationError

__all__ = ["Registry", "VIZ_BACKENDS", "IO_FORMATS", "ALGORITHM_VARIANTS"]

T = TypeVar("T")


class Registry(Generic[T]):
    """A mapping from lower case names to registered objects.

    Args:
        kind: Human readable description used in error messages.
    """

    def __init__(self, kind: str) -> None:
        self._kind = kind
        self._items: Dict[str, T] = {}
        self._aliases: Dict[str, str] = {}

    @property
    def kind(self) -> str:
        """Return the description of what this registry holds."""
        return self._kind

    def register(
        self,
        name: str,
        *aliases: str,
        overwrite: bool = False,
    ) -> Callable[[T], T]:
        """Return a decorator that registers its argument under ``name``.

        Args:
            name: Canonical registration name, compared case insensitively.
            *aliases: Additional names that resolve to the same object.
            overwrite: Whether replacing an existing entry is allowed.

        Raises:
            ValidationError: When the name is already taken and ``overwrite``
                is false.
        """

        def decorator(item: T) -> T:
            self.add(name, item, *aliases, overwrite=overwrite)
            return item

        return decorator

    def add(
        self,
        name: str,
        item: T,
        *aliases: str,
        overwrite: bool = False,
    ) -> T:
        """Register ``item`` under ``name`` and return it."""
        key = name.strip().lower()
        if not key:
            raise ValidationError(f"a {self._kind} name must not be empty")
        if key in self._items and not overwrite:
            raise ValidationError(f"{self._kind} {name!r} is already registered")
        self._items[key] = item
        for alias in aliases:
            alias_key = alias.strip().lower()
            if alias_key in self._aliases and not overwrite:
                raise ValidationError(f"alias {alias!r} is already registered")
            self._aliases[alias_key] = key
        return item

    def get(self, name: str) -> T:
        """Return the object registered under ``name`` or one of its aliases.

        Raises:
            ValidationError: When nothing is registered under the name.
        """
        key = name.strip().lower()
        key = self._aliases.get(key, key)
        if key not in self._items:
            available = ", ".join(self.names()) or "nothing"
            raise ValidationError(
                f"unknown {self._kind} {name!r}; registered: {available}"
            )
        return self._items[key]

    def get_optional(self, name: str) -> Optional[T]:
        """Return the registered object, or ``None`` when it is absent."""
        try:
            return self.get(name)
        except ValidationError:
            return None

    def names(self) -> List[str]:
        """Return the canonical names in sorted order."""
        return sorted(self._items)

    def aliases(self) -> Dict[str, str]:
        """Return a copy of the alias table."""
        return dict(self._aliases)

    def unregister(self, name: str) -> None:
        """Remove an entry and every alias pointing at it.

        Raises:
            ValidationError: When nothing is registered under the name.
        """
        key = name.strip().lower()
        key = self._aliases.get(key, key)
        if key not in self._items:
            raise ValidationError(f"unknown {self._kind} {name!r}")
        del self._items[key]
        for alias, target in list(self._aliases.items()):
            if target == key:
                del self._aliases[alias]

    def clear(self) -> None:
        """Remove every entry. Intended for tests."""
        self._items.clear()
        self._aliases.clear()

    def __contains__(self, name: object) -> bool:
        if not isinstance(name, str):
            return False
        key = name.strip().lower()
        return self._aliases.get(key, key) in self._items

    def __iter__(self) -> Iterator[str]:
        return iter(self.names())

    def __len__(self) -> int:
        return len(self._items)

    def __repr__(self) -> str:
        return f"Registry({self._kind!r}, entries={self.names()!r})"


#: Rendering backends registered by :mod:`discretus.viz`.
VIZ_BACKENDS: Registry = Registry("visualization backend")

#: Interchange formats registered by :mod:`discretus.io`.
IO_FORMATS: Registry = Registry("interchange format")

#: Alternative implementations of the same routine, used by the benchmarks
#: and by the cross validation tests.
ALGORITHM_VARIANTS: Registry = Registry("algorithm variant")
