# Contributing to discretus

Thank you for considering a contribution. This document explains how to set
up a development environment, what the quality gate expects, and how to get a
change reviewed and merged quickly.

## Code of conduct

Participation in this project is governed by `CODE_OF_CONDUCT.md`. By taking
part you agree to uphold a respectful, inclusive, and harassment free
environment in every project space.

## Ways to contribute

- Report a defect with a minimal reproduction.
- Propose a new algorithm or structure that fits the mathematical scope.
- Improve a docstring, a tutorial, or an example.
- Add a missing test, especially a property based one.
- Improve performance without changing documented behavior.

For anything substantial, please open an issue first so that the design can
be discussed before you invest time in an implementation.

## Development setup

```bash
git clone https://github.com/olaflaitinen/discretus.git
cd discretus
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,docs,viz]"
pre-commit install
```

## Everyday commands

```bash
make test        # run the test suite
make test-cov    # run the suite with coverage reporting
make lint        # black, isort, and ruff in check mode
make format      # apply black and isort
make type        # run mypy over the library
make security    # run bandit over the library
make docs        # build the HTML documentation
```

## Quality gate

A change is mergeable when all of the following hold.

1. The full test suite passes on every supported interpreter version.
2. Coverage does not decrease.
3. `black`, `isort`, `ruff`, and `pylint` report no findings.
4. `mypy` reports no errors, and every new public function is annotated.
5. `bandit` reports no new findings.
6. Every new public routine has a docstring that states its parameters, its
   return value, the exceptions it raises, and its asymptotic complexity.
7. New mathematical routines are validated against an independent reference
   or a naive implementation on randomized inputs.

## Code style

- Every source file starts with the three line Mozilla Public License 2.0
  notice, because the license applies per file.
- Format with `black` at the configured line length and sort imports with
  `isort` using the black profile.
- Annotate every public function and method.
- Use `from __future__ import annotations` at the top of every module.
- Name routines after the mathematics they encode, and keep argument order
  consistent with the surrounding module.
- Raise the project exceptions from `discretus.exceptions` rather than bare
  built-in exceptions, so that callers can catch library errors as a group.
- Do not mutate arguments. Return new objects instead.
- Randomized routines must accept an explicit seed and be deterministic once
  it is supplied.
- Prose in documentation and docstrings uses plain punctuation. Do not use
  the long dash character and do not use emoji anywhere in the repository.

## Docstring template

```python
def routine(argument: int) -> int:
    """Summarize the routine in one line.

    Explain the mathematics in a short paragraph when the summary is not
    sufficient.

    Args:
        argument: What the argument means and which values are valid.

    Returns:
        What the caller receives.

    Raises:
        ValidationError: When the argument is outside the valid range.

    Complexity:
        O(log n) time and O(1) space.

    Example:
        >>> routine(8)
        3
    """
```

## Tests

- Tests mirror the package layout, so `discretus/graphs/spanning/kruskal.py`
  is tested by `tests/graphs/test_spanning.py`.
- Prefer small deterministic examples that a reader can verify by hand, then
  add property based tests for the algebraic laws.
- When you fix a defect, add the failing case as a regression test in the
  same commit as the fix.

## Commit messages

Use Conventional Commits. The type is one of `feat`, `fix`, `docs`, `test`,
`refactor`, `perf`, `build`, `ci`, or `chore`, followed by an optional scope
that names the package.

```text
feat(graphs): add Boruvka minimum spanning tree

Implement the Boruvka algorithm with union find component merging and
validate it against Kruskal on randomized weighted graphs.
```

## Pull requests

Keep pull requests small and focused, fill in the template, describe the
mathematical behavior you changed, and link the issue the change addresses.
Rebase onto the latest `main` before requesting review, and make sure the
continuous integration pipeline is green.

## Releasing

Releases are cut by a maintainer. The version is bumped with
`scripts/bump_version.py`, the changelog entry is finalized, a signed tag
`vX.Y.Z` is pushed, and the release workflow publishes the artifacts.
