"""Precondition helpers shared by every package.

The helpers raise the library exceptions from :mod:`discretus.exceptions`
rather than bare built-in exceptions, so that a caller can catch all
validation failures as a group. Each helper returns the validated value,
which lets it be used inline::

    n = require_non_negative(n, "n")

Checks that cost as much as the computation they guard consult
:attr:`~discretus.config.Config.strict_validation` and become no-ops when
the caller has opted out.
"""

from __future__ import annotations

from typing import Any, Collection, Iterable, List, Optional, Sized, Tuple, TypeVar

from .config import get_config
from .exceptions import DomainError, LimitExceededError, ValidationError

__all__ = [
    "require_integer",
    "require_non_negative",
    "require_positive",
    "require_in_range",
    "require_modulus",
    "require_probability",
    "require_hashable",
    "require_not_empty",
    "require_same_length",
    "require_member",
    "require_subset",
    "require_choice",
    "require_seed",
    "check_enumeration_limit",
    "strict",
]

T = TypeVar("T")


def strict() -> bool:
    """Return whether expensive precondition checks are enabled."""
    return get_config().strict_validation


def require_integer(value: Any, name: str = "value") -> int:
    """Return ``value`` when it is an integer.

    Booleans are rejected, because ``True`` acting as ``1`` hides defects in
    numeric code.

    Raises:
        ValidationError: When the value is not an integer.
    """
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValidationError(f"{name} must be an integer, got {type(value).__name__}")
    return value


def require_non_negative(value: int, name: str = "value") -> int:
    """Return ``value`` when it is an integer greater than or equal to zero.

    Raises:
        DomainError: When the value is negative.
    """
    require_integer(value, name)
    if value < 0:
        raise DomainError(f"{name} must be non negative, got {value}")
    return value


def require_positive(value: int, name: str = "value") -> int:
    """Return ``value`` when it is a positive integer.

    Raises:
        DomainError: When the value is zero or negative.
    """
    require_integer(value, name)
    if value <= 0:
        raise DomainError(f"{name} must be positive, got {value}")
    return value


def require_in_range(
    value: int,
    low: int,
    high: int,
    name: str = "value",
    inclusive: bool = True,
) -> int:
    """Return ``value`` when it lies between ``low`` and ``high``.

    Args:
        value: The candidate value.
        low: Lower bound.
        high: Upper bound.
        name: Name used in the error message.
        inclusive: Whether the upper bound is part of the range.

    Raises:
        DomainError: When the value is outside the range.
    """
    require_integer(value, name)
    upper_ok = value <= high if inclusive else value < high
    if value < low or not upper_ok:
        closing = "]" if inclusive else ")"
        raise DomainError(f"{name} must lie in [{low}, {high}{closing}, got {value}")
    return value


def require_modulus(modulus: int, name: str = "modulus") -> int:
    """Return ``modulus`` when it is a valid modulus, that is at least one.

    Raises:
        DomainError: When the modulus is zero or negative.
    """
    require_integer(modulus, name)
    if modulus < 1:
        raise DomainError(f"{name} must be at least 1, got {modulus}")
    return modulus


def require_probability(value: float, name: str = "probability") -> float:
    """Return ``value`` when it lies in the closed unit interval.

    Raises:
        DomainError: When the value is outside ``[0, 1]``.
    """
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ValidationError(f"{name} must be a real number")
    if not 0.0 <= float(value) <= 1.0:
        raise DomainError(f"{name} must lie in [0, 1], got {value}")
    return float(value)


def require_hashable(value: Any, name: str = "element") -> Any:
    """Return ``value`` when it can be used as a set member.

    Raises:
        ValidationError: When the value is unhashable.
    """
    try:
        hash(value)
    except TypeError as exc:
        raise ValidationError(f"{name} must be hashable, got {value!r}") from exc
    return value


def require_not_empty(collection: Sized, name: str = "collection") -> Sized:
    """Return ``collection`` when it contains at least one item.

    Raises:
        DomainError: When the collection is empty.
    """
    if len(collection) == 0:
        raise DomainError(f"{name} must not be empty")
    return collection


def require_same_length(
    first: Sized,
    second: Sized,
    first_name: str = "first",
    second_name: str = "second",
) -> Tuple[Sized, Sized]:
    """Return both collections when they have the same length.

    Raises:
        ValidationError: When the lengths differ.
    """
    if len(first) != len(second):
        raise ValidationError(
            f"{first_name} and {second_name} must have the same length, "
            f"got {len(first)} and {len(second)}"
        )
    return first, second


def require_member(value: Any, ground: Collection[Any], name: str = "element") -> Any:
    """Return ``value`` when it belongs to the ground set.

    Raises:
        DomainError: When the value is not a member.
    """
    if value not in ground:
        raise DomainError(f"{name} {value!r} is not a member of the ground set")
    return value


def require_subset(
    candidate: Iterable[Any],
    ground: Collection[Any],
    name: str = "subset",
) -> List[Any]:
    """Return the candidate as a list when every item belongs to ``ground``.

    Raises:
        DomainError: When an item is not a member of the ground set.
    """
    items = list(candidate)
    if strict():
        missing = [item for item in items if item not in ground]
        if missing:
            raise DomainError(f"{name} contains non members: {missing!r}")
    return items


def require_choice(value: T, options: Collection[T], name: str = "option") -> T:
    """Return ``value`` when it is one of the permitted options.

    Raises:
        ValidationError: When the value is not permitted.
    """
    if value not in options:
        allowed = ", ".join(repr(option) for option in sorted(options, key=repr))
        raise ValidationError(f"{name} must be one of {allowed}, got {value!r}")
    return value


def require_seed(seed: Optional[int], name: str = "seed") -> Optional[int]:
    """Return ``seed`` when it is ``None`` or a non negative integer.

    Raises:
        DomainError: When the seed is negative.
    """
    if seed is None:
        return None
    return require_non_negative(seed, name)


def check_enumeration_limit(requested: int, what: str = "objects") -> int:
    """Return ``requested`` when it fits within the configured limit.

    The guard protects against accidentally materializing an astronomically
    large structure, such as the power set of a large ground set.

    Args:
        requested: Number of objects the caller is about to materialize.
        what: Noun used in the error message.

    Raises:
        LimitExceededError: When the request exceeds
            :attr:`~discretus.config.Config.max_enumeration`.
    """
    limit = get_config().max_enumeration
    if requested > limit:
        raise LimitExceededError(limit, f"{requested} {what}")
    return requested
