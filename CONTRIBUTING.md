# Contributing to discretus

Thank you for considering a contribution. This document is long on purpose.
It records everything a contributor needs in one place, so that you never
have to guess what the project expects, and so that a review can be about
the mathematics rather than about conventions.

Read the first three sections before your first pull request. The rest is
reference material you can return to when it becomes relevant.

## Table of contents

1. [Code of conduct](#code-of-conduct)
2. [Ways to contribute](#ways-to-contribute)
3. [Development setup](#development-setup)
4. [Everyday commands](#everyday-commands)
5. [Repository layout](#repository-layout)
6. [The quality gate](#the-quality-gate)
7. [Code style](#code-style)
8. [Documenting a routine](#documenting-a-routine)
9. [Mathematical conventions](#mathematical-conventions)
10. [Error handling](#error-handling)
11. [Testing](#testing)
12. [Performance work](#performance-work)
13. [Adding a new algorithm](#adding-a-new-algorithm)
14. [Adding an optional dependency](#adding-an-optional-dependency)
15. [Documentation](#documentation)
16. [Commit messages](#commit-messages)
17. [Pull requests](#pull-requests)
18. [Review expectations](#review-expectations)
19. [Deprecation policy](#deprecation-policy)
20. [Releasing](#releasing)
21. [Getting help](#getting-help)

## Code of conduct

Participation in this project is governed by `CODE_OF_CONDUCT.md`. By taking
part you agree to uphold a respectful, inclusive, and harassment free
environment in every project space, which includes the issue tracker, pull
request reviews, discussions, and any correspondence that arises from them.

Reports go to yimanov@student.uef.fi. They are handled privately and the
reporter is never identified without their agreement.

## Ways to contribute

Contributions of every size are welcome, and the list below is ordered from
the least to the most involved rather than from the least to the most
valuable. A precise defect report is worth more to the project than a large
feature that nobody asked for.

- Report a defect. The most useful report contains the version, the
  interpreter, a minimal program that shows the problem, the result you
  expected, the reason you expected it, and the result you observed.
- Correct the documentation. A docstring that states the wrong complexity, a
  tutorial step that no longer works, or a theorem stated with a swapped
  quantifier is a genuine defect, and fixing it helps every later reader.
- Add a missing test. Coverage is high but not complete, and a test that
  pins an edge case, an empty structure, a singleton, a disconnected graph,
  a modulus of one, is always welcome.
- Improve an error message. The library aims to explain what went wrong in
  terms of the mathematics rather than in terms of the implementation.
- Improve performance without changing documented behavior.
- Add an algorithm inside the documented scope. Open an issue first so that
  the interface can be agreed before you write it.
- Add a structure or a subpackage. This is a design change; discuss it in an
  issue and expect the discussion to take longer than the implementation.

For anything beyond a small fix, open an issue first. A design discussion
before the code exists costs an exchange of messages. The same discussion
after the code exists costs a rewrite, and it is discouraging for everybody
involved.

## Development setup

The library has no mandatory third party dependencies, so the environment is
small and fast to create.

```bash
git clone https://github.com/olaflaitinen/discretus.git
cd discretus
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,docs,viz]"
pre-commit install
pre-commit install --hook-type commit-msg
git config commit.template .gitmessage
```

If you prefer conda, `environment.yml` describes the same environment and
additionally installs the Graphviz system binaries, which pip cannot
provide.

```bash
conda env create --file environment.yml
conda activate discretus-dev
```

If you prefer not to install anything locally, the repository carries a
`.gitpod.yml` that opens a prepared workspace in a browser, and a two stage
`Dockerfile` whose development target runs the suite inside a container.

```bash
docker compose run --rm tests
```

Confirm the installation before you start work.

```bash
python -c "import discretus; print(discretus.__version__)"
make test
```

The visualization extra is optional even for contributors. If you install
without it, the tests that need a rendering backend are skipped rather than
failed, and the marker `optional` identifies them.

## Everyday commands

The `Makefile` is the entry point for routine tasks. Every target is a thin
wrapper, so you can always run the underlying tool directly when you need a
flag the target does not pass.

| Command | Effect |
| --- | --- |
| `make test` | Run the test suite |
| `make test-all` | Run every test stage the pipeline runs |
| `make test-cov` | Run the suite with coverage and a missing line report |
| `make lint` | Check formatting and static lint rules without changing files |
| `make gate` | Run every check the pipeline runs, in its order |
| `make format` | Apply black and isort in place |
| `make type` | Run mypy over the library |
| `make security` | Run bandit over the library |
| `make docs` | Build the HTML documentation |
| `make docs-strict` | Build it with warnings treated as errors |
| `make stubs` | Generate type stubs and audit the annotations |
| `make bench` | Run the benchmark suite |
| `make build` | Build the source distribution and the wheel |
| `make clean` | Remove build artifacts and tool caches |
| `make precommit` | Run every pre-commit hook over every file |

### The scripts behind the targets

Each of the composite targets above is one script, and every script takes
options that the target does not pass. Run any of them with `--help` for the
full list. They are the same scripts the pipeline runs, so a check that
passes here passes there.

| Script | What it is for |
| --- | --- |
| `scripts/lint.sh` | Fifteen checks, cheapest first: the formatter, three linters, the type checker, the security scanner, the docstring examples, and six checks of the repository's own conventions. `--fix` applies what can be applied, `--fast` leaves out the slow three, and `--only` and `--skip` select by name. |
| `scripts/run_tests.sh` | Six test stages: the suite, the docstring examples, the property based tests with the seed pinned, the tests marked slow, the ones needing an optional dependency, and the measured run against the coverage floor. `--matrix` repeats the selection on every installed interpreter. |
| `scripts/build_docs.sh` | The documentation stages: the plain build, the strict build, the page inventory, the documentation examples, the reference coverage, the link check, and the printable form. `--serve` serves the result locally. |
| `scripts/bump_version.py` | Raises the version in every file that declares it, rewrites the version tuple, and moves the changelog section. `--dry-run` prints the plan. It never pushes. |
| `scripts/generate_stubs.py` | Generates type stubs from the source for tooling that cannot read inline annotations, and reports any public signature whose annotations are incomplete. `--check` audits without writing. |
| `scripts/release.sh` | Everything that has to pass before a release tag is pushed, in the order the release workflow uses. It never publishes: publishing happens in the workflow, on a pushed tag, through trusted publishing. |

The convention checks of the first script also run as pre-commit hooks, so a
long dash, a missing license notice, a version that disagrees between two
files, an undocumented public name, and a configuration file that does not
parse are all caught before a commit is recorded rather than in the pipeline.

Two task runners manage the interpreter matrix. Use either.

```bash
nox --session tests          # every supported interpreter
nox --session tests-3.11     # one interpreter
tox -e py312,lint,type
```

While working on one package, run only its tests. The suite mirrors the
package layout, so the path is predictable.

```bash
python -m pytest tests/graphs -q
python -m pytest tests/graphs/test_shortest_path.py::test_dijkstra_matches_bellman_ford -q
```

## Repository layout

```text
discretus/
  discretus/        the importable library
    core/           shared abstractions and exact arithmetic
    sets/           sets, relations, orders, functions
    logic/          propositional and predicate logic, satisfiability
    combinatorics/  counting, sequences, generation, designs
    graphs/         structures and graph algorithms
    number_theory/  integers, primes, modular arithmetic, crypto
    recurrences/    recurrences, the Master Theorem, asymptotics
    algebra/        groups, rings, fields, polynomials, linear algebra
    viz/            pluggable rendering backends
    io/             interchange formats
    utils/          cross cutting helpers
  tests/            the suite, mirroring the package layout
  docs/             documentation sources
  examples/         runnable demonstrations
  benchmarks/       performance measurements
  scripts/          maintenance and release helpers
```

The dependency direction is strict. A domain package may import from
`discretus.core` and from `discretus.utils`, and it may not import from
another domain package. Interoperability between domains is provided through
explicit conversion functions that live in the package which produces the
target type. If you find yourself wanting to import the graph package from
the algebra package, add a conversion instead, for example a method that
emits the Cayley graph as plain vertex and edge data that the graph package
can consume.

The reason for the rule is not purity. It keeps the import graph acyclic,
keeps startup fast, makes it possible to reason about what a program
actually exercises, and prevents a defect in one domain from being reachable
from every other.

## The quality gate

A change is mergeable when all of the following hold. Continuous integration
checks each of them, and `make lint type test` plus the pre-commit hooks
reproduce the checks locally.

1. The suite passes on every supported interpreter version, that is 3.9
   through 3.13, on Linux, macOS, and Windows.
2. Coverage does not decrease. The project sits above ninety percent, the
   core layer above ninety five, and new or changed lines are held to ninety
   five percent.
3. `black`, `isort`, `ruff`, and `pylint` report nothing.
4. `mypy` reports nothing, and every new public function is annotated.
5. `bandit` reports no new finding.
6. `codespell`, `yamllint`, and the Markdown linter report nothing.
7. The prose check passes, which means no long dash character and no emoji
   anywhere in the repository.
8. Every new public routine has a docstring in the project format, including
   its asymptotic complexity.
9. A new algorithm is validated against an independent or naive
   implementation on randomized inputs.
10. The changelog entry under `Unreleased` describes the change.

Do not disable a check in order to pass it. If a rule is wrong for a
specific line, silence it on that line with a comment that says why, and if
a rule is wrong for the project, propose changing the configuration in its
own pull request.

## Code style

The mechanical part of the style is enforced by tools, so it is not worth
discussing in review. The judgement part is listed here.

- Format with `black` at the configured line length and sort imports with
  `isort` using the black profile. Do not hand format around the formatter.
- Begin every module with the three line Mozilla Public License 2.0 notice,
  because the license applies per file, then the module docstring.
- Put `from __future__ import annotations` at the top of every module. It
  keeps annotations cheap and lets the sources use modern syntax while
  still running on the oldest supported interpreter.
- Annotate every public function, method, and attribute. Internal helpers
  should be annotated too, and `mypy` is configured to require it.
- Declare `__all__` in every module, listing the public names in the order a
  reader would expect to meet them rather than alphabetically.
- Name routines after the mathematics they encode. `transitive_closure` is
  right; `tc` and `compute_closure_of_relation` are not.
- Keep argument order consistent with the surrounding module. Where a
  routine takes a structure and a parameter, the structure comes first.
- Do not mutate arguments, and do not mutate a structure in place. Return a
  new object. Every value type in the library is immutable, and the
  `FrozenMixin` in `discretus.core.frozen` enforces that for new types.
- Raise the project exceptions from `discretus.exceptions`, never a bare
  built-in, so that a caller can catch library failures as a group.
- Accept any iterable where a collection is meaningful, and return a
  concrete list, tuple, or frozen set rather than an iterator, unless the
  routine is documented as lazy. When it is lazy, say so in the summary
  line and return a generator.
- Make randomized routines take a seed and be deterministic once it is
  supplied. Route the randomness through `discretus.core.random_base` rather
  than touching the global random state.
- Sort anything user visible through `discretus.core.comparators`, which
  provides a total order over mixed element types. Never let output order
  depend on hash values, because that would make results differ between
  processes.
- Prefer exact arithmetic. Use `int` and `fractions.Fraction`, and introduce
  a float only where the mathematics is genuinely approximate, in which case
  document the tolerance.
- Write prose in docstrings and documentation with plain punctuation. Do not
  use the long dash character and do not use emoji anywhere.

## Documenting a routine

Every public routine carries a docstring in the following shape. The
sections are Google style, which the documentation build renders through the
Napoleon extension.

```python
def modular_inverse(value: int, modulus: int) -> int:
    """Return the multiplicative inverse of a residue.

    The inverse exists precisely when the value and the modulus are
    coprime, which the extended Euclidean algorithm decides while it
    computes the Bezout coefficients.

    Args:
        value: Any integer. It is reduced modulo the modulus first.
        modulus: A modulus of at least one.

    Returns:
        The unique residue in the interval from zero to the modulus whose
        product with the value is one.

    Raises:
        DomainError: When the modulus is smaller than one.
        InfeasibleError: When the value and the modulus are not coprime.

    Complexity:
        O(log modulus) division steps.

    Example:
        >>> modular_inverse(3, 11)
        4
    """
```

Rules for each section.

- The summary is one line, in the imperative, and it states what the routine
  returns rather than what it does internally.
- The body explains the mathematics when the summary is not enough. State
  the definition or theorem the routine implements. Name the algorithm. If
  the routine is a transparent reference implementation with a tuned
  counterpart elsewhere, say so and point at the counterpart.
- `Args` documents the meaning and the valid range of every parameter, not
  its type, which the annotation already gives.
- `Raises` lists every exception the routine raises deliberately, with the
  condition that triggers it.
- `Complexity` is required for anything that is not constant time. State it
  in terms of the input quantities you name, for instance the number of
  vertices and edges rather than a bare `n`. Include space when it is not
  constant.
- `Example` is a doctest. It must run, because the documentation job
  executes every docstring example. Keep it small enough that a reader can
  verify it by hand.

## Mathematical conventions

The library is consistent about the following choices, and a contribution
should follow them rather than introduce a second convention.

- The natural numbers include zero.
- The empty product is one and the empty sum is zero, so a routine over an
  empty collection returns the unit of its operation rather than raising.
- The empty set is a subset of every set, the power set of the empty set has
  one member, and the empty relation is vacuously transitive, symmetric, and
  antisymmetric. Tests should pin these cases.
- The zero polynomial has degree minus one.
- A graph is simple unless its type says otherwise. Self loops and parallel
  edges belong to the multigraph type.
- Vertices and set members may be any hashable value. Do not assume they are
  integers, and do not assume they are comparable with one another.
- Indices in ranking and unranking are zero based, and the order is the one
  the module documents, normally lexicographic.
- A permutation is one line notation over zero based positions unless the
  routine says cycle notation.
- Degrees, orders, and cardinalities are plain integers. Sizes that could
  exceed machine precision, for instance the number of subsets of a large
  set, are still exact because Python integers are unbounded.

## Error handling

The exception hierarchy lives in `discretus.exceptions` and is described in
its module docstring. Choose the most specific class that fits.

| Situation | Exception |
| --- | --- |
| An argument has the wrong type or shape | `ValidationError` |
| A value is outside the mathematical domain | `DomainError` |
| Two structures have incompatible shapes | `DimensionError` |
| A candidate structure fails an axiom | `AxiomViolationError` |
| A relation used as a function is not single valued | `NotAFunctionError` |
| Input text cannot be parsed | `ParseError` |
| An iterative routine did not converge | `ConvergenceError` |
| A configured enumeration limit was reached | `LimitExceededError` |
| The requested object does not exist | `InfeasibleError` |
| An optional dependency is missing | `OptionalDependencyError` |
| An interchange format could not be read or written | `SerializationError` |

Two distinctions are worth stating, because they are easy to get wrong.

`InfeasibleError` means the mathematics has no answer, for instance a
topological order of a cyclic graph or a perfect matching that a graph does
not admit. It is not a validation failure, because the input was
well formed. Returning `None` is acceptable instead when absence is an
ordinary outcome that a caller will branch on, for instance searching for an
identity element, and the docstring must then say that `None` is possible.

`LimitExceededError` protects the caller from materializing a structure so
large that the process would die. It is raised by the guard in
`discretus.validation.check_enumeration_limit`, and the limit is
configurable. A routine that can iterate lazily should do so rather than
raise, and should document that the limit does not apply to it.

Use the helpers in `discretus.validation` rather than writing checks by
hand, so that messages stay uniform.

```python
from .validation import require_positive, require_modulus

def routine(n: int, modulus: int) -> int:
    require_positive(n, "n")
    require_modulus(modulus)
    ...
```

## Testing

Tests live under `tests/` and mirror the package layout, so
`discretus/graphs/spanning/kruskal.py` is tested by
`tests/graphs/test_spanning.py`. Shared fixtures live in
`tests/conftest.py`.

The suite has four kinds of test, and a substantial contribution normally
adds at least two of them.

**Example based tests.** A small, deterministic case whose expected value a
reader can verify by hand or look up in a table. Prefer a textbook value,
and cite it in a comment when it is not obvious.

```python
def test_catalan_matches_the_classical_table():
    assert [catalan(n) for n in range(7)] == [1, 1, 2, 5, 14, 42, 132]
```

**Property based tests.** Assert the algebraic laws the documentation
claims, using Hypothesis to generate inputs. Mark them with `property`.

```python
@pytest.mark.property
@given(sets(), sets(), sets())
def test_intersection_distributes_over_union(a, b, c):
    assert intersection(a, union(b, c)) == union(intersection(a, b), intersection(a, c))
```

**Cross validation tests.** When two routines must agree, assert it on
randomized inputs. This is how a tuned implementation is kept honest
against its naive reference, and it is required for any new algorithm that
duplicates an existing result.

```python
@pytest.mark.property
@given(weighted_graphs())
def test_kruskal_and_prim_agree_on_total_weight(graph):
    assert total_weight(kruskal(graph)) == total_weight(prim(graph))
```

**Regression tests.** When you fix a defect, add the failing case in the
same commit as the fix, with a comment naming the issue. A fix without a
regression test invites the defect back.

Further expectations.

- Every test is deterministic. Seed anything random, either through the
  routine's own seed parameter or through a fixture.
- Test the degenerate cases explicitly: the empty structure, a singleton, a
  disconnected graph, a modulus of one, a zero exponent, an empty formula.
- Do not test private helpers through the public interface by accident. If a
  helper deserves a test, it probably deserves to be public.
- Keep a single test focused. A test that asserts six unrelated facts tells
  you little when it fails.
- Mark a slow test with `slow`, and keep the default run comfortable. The
  marker `optional` is for tests that need an optional dependency.

## Performance work

Performance matters, and it comes second to correctness. The project ships
both a transparent reference implementation and a tuned one where the
distinction is instructive, and the tuned one is validated against the
reference rather than trusted.

Before optimizing, measure. The benchmark suite under `benchmarks/` is the
right place for a measurement that should persist.

```bash
make bench
python -m benchmarks --json results.json
```

A performance pull request should state the measurement, the machine, the
interpreter, and the input sizes, and it should show that the result did not
change. A speedup that alters output order, loses exactness, or makes a
routine nondeterministic is not a speedup, because those properties are part
of the documented behavior.

Memoization is welcome where it is safe, which means the cached value cannot
be invalidated by anything the caller does. Use the helpers in
`discretus.core.lazy` and `discretus.utils.memoize` rather than a bare
dictionary, so that the cache can be inspected and cleared in tests. Do not
introduce a cache that grows without bound across calls on behalf of a lazy
generator, because that defeats the laziness the module promises.

## Adding a new algorithm

The following sequence keeps a new algorithm from stalling in review.

1. Open an issue. State the definition or theorem, the proposed name, the
   proposed signature, the complexity, and a reference. Wait for agreement
   on the interface.
2. Place the module where the subject is taught. A shortest path algorithm
   belongs in `discretus/graphs/shortest_path/`, one file per algorithm,
   named after it.
3. Implement the transparent version first, in the shape the theorem
   suggests. Make it correct and readable before making it fast.
4. Export it from the subpackage `__init__.py`, keeping the list in the same
   order as the module names.
5. Write the docstring, including the complexity and a doctest.
6. Write the tests: a textbook case, the degenerate cases, and cross
   validation against whatever independent routine can confirm the result.
7. Add a benchmark if the routine is performance relevant.
8. Add it to the API reference page for its package and, if it is
   pedagogically interesting, to a tutorial.
9. Add a changelog entry under `Unreleased`.
10. Run `make lint type test` and open the pull request.

## Adding an optional dependency

The core must keep installing with no third party package. If your
contribution needs one, it belongs behind an extra.

- Add it to the appropriate extra in `pyproject.toml`, and mirror it in
  `requirements-dev.txt` or `requirements-docs.txt` and in
  `environment.yml`.
- Import it inside the function that needs it, not at module import time.
- Raise `OptionalDependencyError` with the extra name when the import fails,
  so that the message tells the user exactly what to install.
- Mark the tests that need it with `optional` and skip them when it is
  absent.
- Register a rendering backend or an interchange format through
  `discretus.registry` rather than by importing it eagerly.

```python
def render(self) -> bytes:
    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise OptionalDependencyError("matplotlib", extra="viz") from exc
    ...
```

## Documentation

The documentation sources live under `docs/` and are written in Markdown,
which the build renders through MyST. There are three kinds of page and they
have different jobs.

- The API reference under `docs/api/` describes what exists, in the order
  the package presents it. Keep it complete and terse.
- The tutorials under `docs/tutorials/` teach a subject by working through
  it. Keep them narrative, and make every code block runnable from top to
  bottom.
- The top level pages, namely the index, the installation guide, and the
  quick start, orient a new reader. Keep them short and link onward.

Build and review locally before pushing prose.

```bash
make docs
python -m http.server --directory docs/_build/html
```

Every code block in the documentation must run. The documentation job
executes the docstring examples and every script under `examples/`, so a
broken snippet fails the build rather than reaching a reader.

## Commit messages

The project uses Conventional Commits. The template in `.gitmessage`
contains the full vocabulary and one worked example for each type; enable it
with `git config commit.template .gitmessage`.

The shape is:

```text
<type>(<scope>): <subject in the imperative, at most 72 characters>

<body wrapped at 72 characters, explaining what changed and why>

<footer with issue references and breaking change notes>
```

The type is one of `feat`, `fix`, `perf`, `refactor`, `docs`, `test`,
`build`, `ci`, `chore`, or `revert`. The scope names the package.

```text
feat(graphs): add Boruvka minimum spanning tree

Implement the Boruvka algorithm with union find component merging, which
contracts every component in a round and therefore runs in O(|E| log |V|)
time. The result is cross validated against Kruskal on randomized
weighted graphs, since both must return the same total weight even when
the trees themselves differ.

Closes #42
```

Write one commit per logical change. A pull request that adds an algorithm,
its tests, and its documentation may be one commit or three, but it should
not be fifteen commits that each fix a typo in the previous one. Rebase and
tidy before requesting review.

## Pull requests

- Keep the pull request focused on one change. Two unrelated fixes are two
  pull requests, and both will be reviewed faster than one combined one.
- Fill in the template. The mathematical notes section is not optional for a
  change that touches mathematics: state the definition, the theorem, or the
  algorithm, and cite the reference you followed.
- Rebase onto the latest `main` before requesting review, and rebase rather
  than merge when updating, so that the history stays linear.
- Make sure continuous integration is green. A red pipeline is the
  contributor's to resolve, and a reviewer will usually wait for it.
- Mark it as a draft while you are still working, so that a reviewer does
  not spend time on a moving target.
- Expect to be asked for a test. It is the most common review request, and
  anticipating it saves a round trip.

## Review expectations

A review is a technical conversation about a change, not a judgement of the
person who wrote it. Both sides can rely on the following.

As a reviewer: respond within a few days, review the change that was
submitted rather than the change you would have written, distinguish clearly
between what must change and what you would merely prefer, explain the
reason for a request so that it teaches rather than merely instructs, and
approve when the change is good enough rather than when it is perfect.

As a contributor: assume that a question is a question and not an
accusation, answer it in the thread rather than in a force push, push a
fixup commit so that the reviewer can see what changed and squash before
merge, and say so plainly when you disagree, with your reasoning. A
disagreement about mathematics is resolved by a reference or a
counterexample, which is one of the pleasures of working in this domain.

The maintainer merges. Merging is squash and merge by default, with the
pull request title as the subject, which is why the title must follow the
commit message convention.

## Deprecation policy

The public interface follows semantic versioning. Within a major version it
stays backward compatible, and anything not documented as public is internal
and may change without notice.

When a public name has to change:

1. Add the new name, fully documented and tested.
2. Keep the old name working as a thin wrapper that emits a
   `DeprecationWarning` naming the replacement.
3. Record the deprecation in the changelog under `Deprecated`, with the
   release in which the name will be removed.
4. Remove it no earlier than the next minor release, and note the removal in
   the changelog under `Removed`, with a migration note.

```python
def old_name(*args: Any, **kwargs: Any) -> Any:
    """Deprecated alias of :func:`new_name`."""
    warnings.warn(
        "old_name is deprecated and will be removed in 1.2.0; use new_name",
        DeprecationWarning,
        stacklevel=2,
    )
    return new_name(*args, **kwargs)
```

The test configuration turns deprecation warnings into errors, so the suite
itself must call the new name while a test that exercises the alias asserts
the warning.

## Releasing

Releases are cut by a maintainer. The sequence is recorded here so that it
is reproducible and so that a contributor can see what happens to their
change after it merges.

1. Confirm that `main` is green on every interpreter and platform.
2. Move the `Unreleased` section of `CHANGELOG.md` under the new version
   heading, with the date, and add the comparison link.
3. Run `scripts/bump_version.py <part>`, which updates every file listed in
   `.bumpversion.cfg`, rewrites the `__version_info__` tuple, and creates
   the commit and the signed tag `vX.Y.Z`.
4. Push the commit, then push the tag. The release workflow verifies that
   the tag matches the declared version, runs the suite, builds and checks
   the distribution, publishes it through trusted publishing, and drafts the
   release notes.
5. Confirm that the documentation built and that the package installs from
   the index in a clean environment.

## Getting help

- For a usage question, open a discussion rather than an issue.
- For a defect, open an issue with the bug report template.
- For a design proposal, open an issue with the feature request template.
- For anything sensitive, including a security report, write to
  yimanov@student.uef.fi. Do not open a public issue for a vulnerability;
  `SECURITY.md` describes the process.

If you are looking for a first contribution, the issues labelled
`good first issue` are chosen to be self contained, and the ones labelled
`documentation` need no deep familiarity with the internals.
