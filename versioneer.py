# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Minimal version resolution helper for build and release tooling.

The single source of truth for the released version string is
``discretus/__about__.py``. When the working tree is a git checkout this
module can additionally describe the current commit, which the release
scripts use to label development builds. It deliberately implements only the
small surface the project needs instead of vendoring a general purpose
version management framework.
"""

from __future__ import annotations

import re
import subprocess  # nosec B404
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent
ABOUT = ROOT / "discretus" / "__about__.py"

_VERSION_RE = re.compile(r"^__version__\s*=\s*[\"']([^\"']+)[\"']", re.MULTILINE)


def get_version() -> str:
    """Return the declared release version of the package."""
    match = _VERSION_RE.search(ABOUT.read_text(encoding="utf-8"))
    if match is None:
        raise RuntimeError(f"no __version__ declaration found in {ABOUT}")
    return match.group(1)


def get_git_describe() -> Optional[str]:
    """Return ``git describe`` output, or ``None`` outside a git checkout."""
    try:
        completed = subprocess.run(  # nosec B603 B607
            ["git", "describe", "--tags", "--dirty", "--always"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return completed.stdout.strip() or None


def get_full_version() -> str:
    """Return the release version, annotated with the commit when available."""
    version = get_version()
    described = get_git_describe()
    if described is None or described.lstrip("v") == version:
        return version
    return f"{version}+{described}"


if __name__ == "__main__":
    print(get_full_version())
