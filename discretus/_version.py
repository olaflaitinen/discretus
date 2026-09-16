"""Version resolution for discretus.

The released version string is declared in :mod:`discretus.__about__`. When
the package runs from a git checkout the commit description is appended so
that development builds are distinguishable from releases.
"""

from __future__ import annotations

import subprocess  # nosec B404
from pathlib import Path
from typing import Optional, Tuple

from .__about__ import __version__ as _declared
from .__about__ import __version_info__ as _declared_info

__all__ = ["version", "version_info", "git_revision", "full_version"]

_REPO_ROOT = Path(__file__).resolve().parent.parent


def version() -> str:
    """Return the declared release version, for example ``"1.0.0"``."""
    return _declared


def version_info() -> Tuple[int, int, int]:
    """Return the release version as a ``(major, minor, patch)`` tuple."""
    return _declared_info


def git_revision() -> Optional[str]:
    """Return the abbreviated git commit hash, or ``None`` if unavailable.

    The function returns ``None`` for an installed package, because a wheel
    carries no git metadata. It never raises.
    """
    if not (_REPO_ROOT / ".git").exists():
        return None
    try:
        completed = subprocess.run(  # nosec B603 B607
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=str(_REPO_ROOT),
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return completed.stdout.strip() or None


def full_version() -> str:
    """Return the version annotated with the git revision when available."""
    revision = git_revision()
    if revision is None:
        return _declared
    return f"{_declared}+g{revision}"
