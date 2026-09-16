# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Project metadata for discretus.

This module is the single source of truth for the distribution metadata that
is exposed at runtime. It imports nothing from the rest of the library so
that build tooling can read it without importing the package.
"""

from __future__ import annotations

__all__ = [
    "__title__",
    "__summary__",
    "__version__",
    "__version_info__",
    "__author__",
    "__author_email__",
    "__maintainer__",
    "__license__",
    "__copyright__",
    "__url__",
    "__documentation__",
    "__position__",
    "__affiliation__",
    "__orcid__",
]

__title__ = "discretus"
__summary__ = (
    "A rigorous, production-grade library for Discrete Mathematics in pure Python."
)
__version__ = "1.0.0"
__version_info__ = (1, 0, 0)

__author__ = "Olaf Yunus Laitinen Imanov"
__author_email__ = "yimanov@student.uef.fi"
__maintainer__ = __author__
__position__ = "Student Researcher"
__affiliation__ = (
    "Department of Physics and Mathematics, Faculty of Science, Forestry and "
    "Technology, University of Eastern Finland, Joensuu, Finland"
)
__orcid__ = "0009-0006-5184-0810"

__license__ = "MPL-2.0"
__copyright__ = "Copyright (c) 2026 Olaf Yunus Laitinen Imanov"
__url__ = "https://github.com/olaflaitinen/discretus"
__documentation__ = "https://discretus.readthedocs.io"
