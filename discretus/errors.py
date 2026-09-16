"""Compatibility alias for :mod:`discretus.exceptions`.

The exception hierarchy is defined once in :mod:`discretus.exceptions`. This
module re-exports it under the ``errors`` name, which some callers prefer,
and it will be kept in place for the lifetime of the major version.
"""

from __future__ import annotations

from .exceptions import (
    AlgorithmError,
    AxiomViolationError,
    BackendError,
    ConvergenceError,
    DimensionError,
    DiscretusError,
    DomainError,
    InfeasibleError,
    LimitExceededError,
    NotAFunctionError,
    OptionalDependencyError,
    ParseError,
    SerializationError,
    StructureError,
    ValidationError,
)

__all__ = [
    "AlgorithmError",
    "AxiomViolationError",
    "BackendError",
    "ConvergenceError",
    "DimensionError",
    "DiscretusError",
    "DomainError",
    "InfeasibleError",
    "LimitExceededError",
    "NotAFunctionError",
    "OptionalDependencyError",
    "ParseError",
    "SerializationError",
    "StructureError",
    "ValidationError",
]
