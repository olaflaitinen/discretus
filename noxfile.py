# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Nox sessions for testing, linting, typing, and documentation builds."""

from __future__ import annotations

import nox

nox.options.sessions = ["tests", "lint", "typecheck"]
nox.options.reuse_existing_virtualenvs = True

PYTHON_VERSIONS = ["3.9", "3.10", "3.11", "3.12", "3.13"]
SOURCES = ["discretus", "tests", "examples", "benchmarks"]


@nox.session(python=PYTHON_VERSIONS)
def tests(session: nox.Session) -> None:
    """Run the test suite on every supported interpreter."""
    session.install("-e", ".")
    session.install("pytest>=7.4", "pytest-cov>=4.1", "hypothesis>=6.90")
    session.run("pytest", "--cov=discretus", "--cov-report=term-missing", "tests")


@nox.session
def lint(session: nox.Session) -> None:
    """Check formatting and static lint rules."""
    session.install("black>=24.1", "isort>=5.13", "ruff>=0.3")
    session.run("black", "--check", *SOURCES)
    session.run("isort", "--check-only", *SOURCES)
    session.run("ruff", "check", *SOURCES)


@nox.session
def format_code(session: nox.Session) -> None:
    """Apply the project code style in place."""
    session.install("black>=24.1", "isort>=5.13")
    session.run("black", *SOURCES)
    session.run("isort", *SOURCES)


@nox.session
def typecheck(session: nox.Session) -> None:
    """Run the mypy type checker over the library."""
    session.install("-e", ".")
    session.install("mypy>=1.8")
    session.run("mypy", "discretus")


@nox.session
def security(session: nox.Session) -> None:
    """Run the bandit security scanner over the library."""
    session.install("bandit>=1.7")
    session.run("bandit", "-c", ".bandit", "-r", "discretus")


@nox.session
def docs(session: nox.Session) -> None:
    """Build the HTML documentation."""
    session.install("-e", ".")
    session.install("-r", "requirements-docs.txt")
    session.run("sphinx-build", "-b", "html", "docs", "docs/_build/html")


@nox.session
def benchmarks(session: nox.Session) -> None:
    """Run the benchmark suite."""
    session.install("-e", ".")
    session.run("python", "-m", "benchmarks")
