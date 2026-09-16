"""What it means to be a member of a discrete structure.

Elements are ordinary Python values. The only requirement the library places
on them is that they are hashable, so that they can live in sets and act as
dictionary keys. This module provides the normalization helpers and the
labelled wrapper used when a value needs a display name that differs from
its representation.
"""

from __future__ import annotations

from typing import Any, Dict, FrozenSet, Iterable, List, Tuple

from ..exceptions import ValidationError
from ..typing import Element

__all__ = [
    "normalize_element",
    "normalize_elements",
    "as_frozenset",
    "Labeled",
    "element_repr",
]


def normalize_element(value: Any, name: str = "element") -> Element:
    """Return ``value`` when it can be used as a member of a structure.

    Lists, sets, and dictionaries are converted to their immutable
    counterparts rather than rejected, because a caller who writes
    ``{{1, 2}, {3}}`` in mathematical notation means a set of sets.

    Args:
        value: The candidate member.
        name: Name used in the error message.

    Returns:
        A hashable value equal in meaning to the input.

    Raises:
        ValidationError: When the value cannot be made hashable.

    Example:
        >>> normalize_element([1, 2])
        (1, 2)
        >>> sorted(normalize_element({1, 2}))
        [1, 2]
    """
    if isinstance(value, list):
        return tuple(normalize_element(item, name) for item in value)
    if isinstance(value, (set, frozenset)):
        return frozenset(normalize_element(item, name) for item in value)
    if isinstance(value, dict):
        return tuple(
            sorted(
                ((key, normalize_element(item, name)) for key, item in value.items()),
                key=lambda pair: repr(pair[0]),
            )
        )
    try:
        hash(value)
    except TypeError as exc:
        raise ValidationError(f"{name} must be hashable, got {value!r}") from exc
    return value


def normalize_elements(values: Iterable[Any], name: str = "element") -> List[Element]:
    """Return the members of an iterable, each normalized and in order."""
    return [normalize_element(value, name) for value in values]


def as_frozenset(values: Iterable[Any], name: str = "element") -> FrozenSet[Element]:
    """Return a frozen set of normalized members.

    Example:
        >>> as_frozenset([1, 1, 2]) == frozenset({1, 2})
        True
    """
    return frozenset(normalize_elements(values, name))


class Labeled:
    """A hashable value carrying a display label.

    The wrapper is useful when a structure is built over opaque values that
    should print as human readable names, for example the vertices of a
    Cayley graph or the generators of a group.

    Args:
        value: The underlying member.
        label: Text used when the element is printed.

    Example:
        >>> r = Labeled((0, 1), "r")
        >>> str(r)
        'r'
        >>> r == Labeled((0, 1), "rotation")
        True
    """

    __slots__ = ("_value", "_label")

    def __init__(self, value: Any, label: str) -> None:
        self._value = normalize_element(value)
        self._label = str(label)

    @property
    def value(self) -> Element:
        """Return the underlying member."""
        return self._value

    @property
    def label(self) -> str:
        """Return the display label."""
        return self._label

    def relabel(self, label: str) -> "Labeled":
        """Return a copy of the element with a different label."""
        return Labeled(self._value, label)

    def to_dict(self) -> Dict[str, Any]:
        """Return a dictionary describing the element."""
        return {"value": self._value, "label": self._label}

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Labeled):
            return self._value == other._value
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self._value)

    def __str__(self) -> str:
        return self._label

    def __repr__(self) -> str:
        return f"Labeled({self._value!r}, {self._label!r})"


def element_repr(value: Any) -> str:
    """Return a short, stable rendering of an element.

    Frozen sets print in brace notation with their members sorted by their
    representation, so that equal sets always render identically.

    Example:
        >>> element_repr(frozenset({2, 1}))
        '{1, 2}'
        >>> element_repr((1, 2))
        '(1, 2)'
    """
    if isinstance(value, Labeled):
        return value.label
    if isinstance(value, (frozenset, set)):
        inner = ", ".join(sorted((element_repr(item) for item in value), key=_sort_key))
        return "{" + inner + "}"
    if isinstance(value, tuple):
        inner = ", ".join(element_repr(item) for item in value)
        return f"({inner})" if len(value) != 1 else f"({inner},)"
    return repr(value) if not isinstance(value, str) else value


def _sort_key(text: str) -> Tuple[int, str]:
    """Sort numeric looking strings before others, then lexicographically."""
    try:
        return (0, f"{float(text):020.6f}")
    except ValueError:
        return (1, text)
