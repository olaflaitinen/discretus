"""Compatibility shim.

All project metadata lives in ``pyproject.toml``. This file exists only so
that legacy tooling that still invokes ``python setup.py`` keeps working.
"""

from setuptools import setup

if __name__ == "__main__":
    setup()
