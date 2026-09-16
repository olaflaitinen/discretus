# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Exception hierarchy for discretus.

Every error raised deliberately by the library derives from
:class:`DiscretusError`, so that a caller can catch all library failures as a
group without also catching unrelated built-in exceptions.

The hierarchy is::

    DiscretusError
        ValidationError
            DomainError
            DimensionError
        StructureError
            AxiomViolationError
            NotAFunctionError
        ParseError
        AlgorithmError
            ConvergenceError
            LimitExceededError
            InfeasibleError
        BackendError
            OptionalDependencyError
        SerializationError
"""

from __future__ import annotations

from typing import Any, Optional

__all__ = [
    "DiscretusError",
    "ValidationError",
    "DomainError",
    "DimensionError",
    "StructureError",
    "AxiomViolationError",
    "NotAFunctionError",
    "ParseError",
    "AlgorithmError",
    "ConvergenceError",
    "LimitExceededError",
    "InfeasibleError",
    "BackendError",
    "OptionalDependencyError",
    "SerializationError",
]


class DiscretusError(Exception):
    """Base class for every error raised by the library."""


class ValidationError(DiscretusError, ValueError):
    """An argument failed a documented precondition.

    The class also derives from :class:`ValueError` so that existing code
    which catches value errors keeps working.
    """


class DomainError(ValidationError):
    """A value lies outside the mathematical domain of a routine.

    Examples include a negative argument to a factorial, a modulus smaller
    than one, or an element that is not a member of the ground set.
    """


class DimensionError(ValidationError):
    """Two structures have incompatible shapes.

    Examples include adding matrices of different sizes and multiplying a
    matrix by a vector of the wrong length.
    """


class StructureError(DiscretusError):
    """A discrete structure is not in a state the routine requires."""


class AxiomViolationError(StructureError):
    """A candidate algebraic structure fails one of its defining axioms.

    Raised, for instance, when a proposed group operation is not associative
    or when an element has no inverse.
    """

    def __init__(self, axiom: str, detail: Optional[str] = None) -> None:
        message = f"axiom violated: {axiom}"
        if detail:
            message = f"{message} ({detail})"
        super().__init__(message)
        self.axiom = axiom
        self.detail = detail


class NotAFunctionError(StructureError):
    """A relation used as a function is not single valued or not total."""


class ParseError(DiscretusError):
    """Input text could not be parsed.

    The position, when known, is the zero based index of the offending
    character in the source text.
    """

    def __init__(
        self,
        message: str,
        source: Optional[str] = None,
        position: Optional[int] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.source = source
        self.position = position

    def __str__(self) -> str:
        if self.position is None:
            return self.message
        return f"{self.message} at position {self.position}"


class AlgorithmError(DiscretusError):
    """An algorithm could not produce a result."""


class ConvergenceError(AlgorithmError):
    """An iterative routine did not converge within its iteration budget."""


class LimitExceededError(AlgorithmError):
    """A configured enumeration or recursion limit was reached.

    The limit protects against accidentally materializing an astronomically
    large structure, such as the power set of a large ground set.
    """

    def __init__(self, limit: int, requested: Optional[Any] = None) -> None:
        message = f"configured limit of {limit} exceeded"
        if requested is not None:
            message = f"{message}; requested {requested}"
        super().__init__(message)
        self.limit = limit
        self.requested = requested


class InfeasibleError(AlgorithmError):
    """The requested object does not exist.

    Raised, for instance, when asking for a topological order of a graph that
    contains a cycle or for a perfect matching that a graph does not admit.
    """


class BackendError(DiscretusError):
    """A rendering or computation backend failed."""


class OptionalDependencyError(BackendError, ImportError):
    """An optional dependency is required for the requested feature."""

    def __init__(self, package: str, extra: Optional[str] = None) -> None:
        hint = (
            f'pip install "discretus[{extra}]"' if extra else f"pip install {package}"
        )
        super().__init__(
            f"the optional dependency {package!r} is required for this feature; "
            f"install it with: {hint}"
        )
        self.package = package
        self.extra = extra


class SerializationError(DiscretusError):
    """An object could not be written to, or read from, an interchange format."""
