# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Compatibility shim.

All project metadata lives in ``pyproject.toml``. This file exists only so
that legacy tooling that still invokes ``python setup.py`` keeps working.
"""

from setuptools import setup

if __name__ == "__main__":
    setup()
