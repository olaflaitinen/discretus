# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""discretus: a rigorous library for discrete mathematics in pure Python.

The package spans seven domains, namely set theory, mathematical logic,
combinatorics, graph theory, number theory, recurrence relations, and
abstract algebra, and exposes them through one coherent interface with
consistent naming, predictable data structures, and uniform error handling.

Domain packages are imported on first use rather than at import time, so
that a program which only needs number theory does not pay for the graph
and logic packages. The attribute access that triggers the import is
transparent to the caller::

    import discretus

    discretus.number_theory.primes.is_prime(97)

Direct imports work as usual and are the recommended style::

    from discretus.sets import FiniteSet
    from discretus.graphs.shortest_path import dijkstra

Attributes:
    __version__: The released version string.
    __author__: The author of the library.
"""

from __future__ import annotations

import importlib
from typing import TYPE_CHECKING, Any, List

from .__about__ import (
    __author__,
    __author_email__,
    __copyright__,
    __documentation__,
    __license__,
    __summary__,
    __title__,
    __url__,
    __version__,
    __version_info__,
)
from .config import Config, config_scope, get_config, reset_config, set_config
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

if TYPE_CHECKING:  # pragma: no cover
    # Each name is imported under itself, which is the convention that marks
    # an import as a deliberate re export rather than an unused one. Without
    # it a linter reports eleven unused imports, and a type checker does not
    # treat the names as part of this module's interface, which is the whole
    # reason the block exists: the subpackages are loaded lazily at runtime,
    # so this is the only place a checker can learn that they exist.
    from . import algebra as algebra
    from . import combinatorics as combinatorics
    from . import core as core
    from . import graphs as graphs
    from . import io as io
    from . import logic as logic
    from . import number_theory as number_theory
    from . import recurrences as recurrences
    from . import sets as sets
    from . import utils as utils
    from . import viz as viz

#: Subpackages that are imported on first attribute access.
_LAZY_SUBMODULES = (
    "algebra",
    "cli",
    "combinatorics",
    "core",
    "graphs",
    "io",
    "logic",
    "number_theory",
    "recurrences",
    "sets",
    "utils",
    "viz",
)

__all__ = [
    # Metadata.
    "__version__",
    "__version_info__",
    "__author__",
    "__author_email__",
    "__license__",
    "__copyright__",
    "__summary__",
    "__title__",
    "__url__",
    "__documentation__",
    # Configuration.
    "Config",
    "get_config",
    "set_config",
    "reset_config",
    "config_scope",
    # Exceptions.
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
    # Domain packages, imported lazily.
    *_LAZY_SUBMODULES,
]


def __getattr__(name: str) -> Any:
    """Import a domain subpackage the first time it is requested.

    Args:
        name: Attribute being looked up on the package.

    Returns:
        The imported submodule.

    Raises:
        AttributeError: When the name is not a known attribute.
    """
    if name in _LAZY_SUBMODULES:
        module = importlib.import_module(f".{name}", __name__)
        globals()[name] = module
        return module
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> List[str]:
    """Return the public names, including the lazily imported subpackages."""
    return sorted(set(__all__) | set(globals()))
