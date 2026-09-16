# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Logging helpers for the library.

The library never configures logging on import. It attaches a null handler to
its root logger, which keeps quiet in applications that do not configure
logging while still letting an application opt in with a single call to
:func:`configure_logging`.
"""

from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Any, Iterator, Optional, Union

__all__ = [
    "ROOT_LOGGER_NAME",
    "get_logger",
    "configure_logging",
    "log_level_scope",
    "log_algorithm_step",
]

ROOT_LOGGER_NAME = "discretus"

_root = logging.getLogger(ROOT_LOGGER_NAME)
_root.addHandler(logging.NullHandler())

DEFAULT_FORMAT = "%(asctime)s %(levelname)-8s %(name)s: %(message)s"


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Return a logger below the library root.

    Args:
        name: Dotted suffix, normally ``__name__``. A name that already
            starts with the library root is used unchanged.

    Returns:
        The logger for the requested name.

    Example:
        >>> get_logger("discretus.graphs.dijkstra").name
        'discretus.graphs.dijkstra'
    """
    if name is None:
        return _root
    if name == ROOT_LOGGER_NAME or name.startswith(ROOT_LOGGER_NAME + "."):
        return logging.getLogger(name)
    return logging.getLogger(f"{ROOT_LOGGER_NAME}.{name}")


def configure_logging(
    level: Union[int, str] = logging.INFO,
    stream: Optional[Any] = None,
    fmt: str = DEFAULT_FORMAT,
) -> logging.Logger:
    """Attach a stream handler to the library logger.

    Calling the function twice replaces the handler rather than adding a
    second one, so repeated calls do not duplicate output.

    Args:
        level: Threshold as a level number or a level name.
        stream: Destination stream. Defaults to standard error.
        fmt: Format string for the handler.

    Returns:
        The configured library root logger.
    """
    for handler in list(_root.handlers):
        if not isinstance(handler, logging.NullHandler):
            _root.removeHandler(handler)
    handler = logging.StreamHandler(stream)
    handler.setFormatter(logging.Formatter(fmt))
    _root.addHandler(handler)
    _root.setLevel(level)
    return _root


@contextmanager
def log_level_scope(level: Union[int, str]) -> Iterator[logging.Logger]:
    """Set the library log level for the duration of a ``with`` block."""
    previous = _root.level
    _root.setLevel(level)
    try:
        yield _root
    finally:
        _root.setLevel(previous)


def log_algorithm_step(
    logger: logging.Logger,
    algorithm: str,
    message: str,
    **context: Any,
) -> None:
    """Record one step of an algorithm at debug level.

    The context is rendered as ``key=value`` pairs in a stable order, which
    keeps the output diffable when a run is captured in a test.

    Args:
        logger: Logger to write to.
        algorithm: Name of the algorithm producing the step.
        message: Short description of the step.
        **context: Additional values to include.
    """
    if not logger.isEnabledFor(logging.DEBUG):
        return
    if context:
        rendered = " ".join(f"{key}={context[key]!r}" for key in sorted(context))
        logger.debug("%s: %s (%s)", algorithm, message, rendered)
    else:
        logger.debug("%s: %s", algorithm, message)
