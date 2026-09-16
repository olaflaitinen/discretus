# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Global configuration for discretus.

The library is usable without touching this module. The settings exist so
that an application can tighten validation, raise or lower the guard rails
that protect against accidental combinatorial explosion, choose a default
rendering backend, and make randomized routines reproducible process wide.

Every setting can also be supplied through an environment variable whose
name is the upper case field name prefixed with ``DISCRETUS_``, which makes
the library configurable inside continuous integration runners and grading
sandboxes without editing code.

Example:
    >>> from discretus.config import config_scope, get_config
    >>> with config_scope(max_enumeration=8):
    ...     get_config().max_enumeration
    8
    >>> get_config().max_enumeration
    1000000
"""

from __future__ import annotations

import os
from contextlib import contextmanager
from dataclasses import dataclass, fields, replace
from typing import Any, Dict, Iterator, Optional

from .exceptions import ValidationError

__all__ = [
    "Config",
    "get_config",
    "set_config",
    "reset_config",
    "config_scope",
    "config_from_environment",
]

_ENV_PREFIX = "DISCRETUS_"


@dataclass(frozen=True)
class Config:
    """An immutable snapshot of the library settings.

    Attributes:
        strict_validation: When true, routines verify their preconditions
            even when the check is asymptotically as expensive as the
            computation itself. Turning it off trades safety for speed.
        max_enumeration: Upper bound on the number of objects a routine
            will materialize before raising
            :class:`~discretus.exceptions.LimitExceededError`. Lazy
            generators are unaffected.
        max_recursion_depth: Depth at which the recursive reference
            implementations switch to their iterative variants.
        explain: When true, routines that support step recording collect
            their derivation by default.
        latex_style: Either ``"inline"`` or ``"display"``, controlling how
            the LaTeX mixin wraps its output.
        notation: Either ``"ascii"`` or ``"unicode"``, controlling how
            formulas are printed.
        default_seed: Seed used by randomized routines when the caller does
            not supply one. ``None`` leaves them nondeterministic.
        tolerance: Absolute tolerance for comparisons that cannot be made
            exactly because a floating point value is involved.
        viz_backend: Preferred visualization backend, or ``"auto"`` to pick
            the first backend whose dependencies are installed.
    """

    strict_validation: bool = True
    max_enumeration: int = 1_000_000
    max_recursion_depth: int = 900
    explain: bool = False
    latex_style: str = "inline"
    notation: str = "ascii"
    default_seed: Optional[int] = None
    tolerance: float = 1e-12
    viz_backend: str = "auto"

    def __post_init__(self) -> None:
        if self.max_enumeration < 1:
            raise ValidationError("max_enumeration must be at least 1")
        if self.max_recursion_depth < 1:
            raise ValidationError("max_recursion_depth must be at least 1")
        if self.latex_style not in {"inline", "display"}:
            raise ValidationError("latex_style must be 'inline' or 'display'")
        if self.notation not in {"ascii", "unicode"}:
            raise ValidationError("notation must be 'ascii' or 'unicode'")
        if self.tolerance <= 0:
            raise ValidationError("tolerance must be positive")

    def to_dict(self) -> Dict[str, Any]:
        """Return the settings as a plain dictionary."""
        return {field.name: getattr(self, field.name) for field in fields(self)}


def _coerce(name: str, raw: str) -> Any:
    """Convert an environment string to the type declared on :class:`Config`."""
    declared = {field.name: field.type for field in fields(Config)}[name]
    text = raw.strip()
    if declared == "bool":
        lowered = text.lower()
        if lowered in {"1", "true", "yes", "on"}:
            return True
        if lowered in {"0", "false", "no", "off"}:
            return False
        raise ValidationError(f"cannot read {name!r} as a boolean: {raw!r}")
    if declared == "int":
        return int(text)
    if declared == "float":
        return float(text)
    if declared == "Optional[int]":
        return None if text.lower() in {"", "none"} else int(text)
    return text


def config_from_environment(base: Optional[Config] = None) -> Config:
    """Return a configuration with environment variable overrides applied.

    Args:
        base: Configuration to start from. Defaults to library defaults.

    Returns:
        A new :class:`Config` where every ``DISCRETUS_`` variable that names
        a known setting has replaced the corresponding field.

    Raises:
        ValidationError: When a variable cannot be read as its field type.
    """
    current = base if base is not None else Config()
    overrides: Dict[str, Any] = {}
    for field in fields(Config):
        raw = os.environ.get(_ENV_PREFIX + field.name.upper())
        if raw is not None:
            overrides[field.name] = _coerce(field.name, raw)
    return replace(current, **overrides) if overrides else current


_active: Config = config_from_environment()


def get_config() -> Config:
    """Return the configuration currently in effect."""
    return _active


def set_config(**overrides: Any) -> Config:
    """Replace one or more settings process wide.

    Args:
        **overrides: Field names and their new values.

    Returns:
        The new active configuration.

    Raises:
        ValidationError: When a name is not a known setting or a value is
            outside its valid range.
    """
    global _active
    known = {field.name for field in fields(Config)}
    unknown = sorted(set(overrides) - known)
    if unknown:
        raise ValidationError(f"unknown configuration keys: {', '.join(unknown)}")
    _active = replace(_active, **overrides)
    return _active


def reset_config() -> Config:
    """Restore the defaults, including environment variable overrides."""
    global _active
    _active = config_from_environment()
    return _active


@contextmanager
def config_scope(**overrides: Any) -> Iterator[Config]:
    """Apply settings for the duration of a ``with`` block.

    The previous configuration is restored on exit, including when the block
    raises.

    Args:
        **overrides: Field names and their temporary values.

    Yields:
        The configuration in effect inside the block.
    """
    global _active
    previous = _active
    try:
        yield set_config(**overrides)
    finally:
        _active = previous
