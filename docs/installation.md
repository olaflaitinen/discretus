# Installation

discretus is a pure Python library with no mandatory third party
dependencies. In the ordinary case installation is a single command that
needs no compiler, no system library, and no network access beyond the
package index itself.

```bash
pip install discretus
```

This page covers that case in one line and then covers everything else: the
optional extras and what each one is for, conda, installing from source,
verifying an installation, offline and restricted environments, containers,
notebooks, continuous integration, upgrading, uninstalling, and the problems
that do occasionally occur, with their causes.

## Requirements

| Requirement | Value |
| --- | --- |
| Python | 3.9 or later |
| Implementation | CPython or PyPy |
| Operating system | Linux, macOS, Windows |
| Architecture | Any architecture the interpreter runs on |
| Compiler | Not required |
| Runtime dependencies | None |
| Disk space | Under two megabytes for the library |

The library is distributed as a universal wheel, which means one artifact
serves every platform and every supported interpreter version. There is no
source build step, so an installation cannot fail for the reasons that
compiled packages fail: no missing header, no mismatched toolchain, no
architecture specific wheel to hunt for.

The floor of 3.9 exists because the library uses typing constructs that
earlier versions do not support. The ceiling is whatever the newest released
interpreter is; the test matrix runs 3.9 through 3.13 on Linux, macOS, and
Windows before every release.

## Installing from the package index

The recommended installation into a virtual environment is:

```bash
python -m venv .venv
source .venv/bin/activate        # on Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install discretus
```

Installing into a virtual environment rather than into the interpreter that
the operating system provides is worth the extra two commands. It keeps the
system interpreter untouched, makes the dependency set of each project
independent, and makes removal a matter of deleting a directory.

To install a specific version, which is what a reproducible analysis or a
graded assignment should do:

```bash
pip install "discretus==1.0.0"
```

To allow patch updates but not minor ones, which is the usual choice for an
application that depends on the library:

```bash
pip install "discretus~=1.0.0"
```

## Optional extras

The core installs with nothing extra. Three extras add capability, and each
is genuinely optional: the library imports an extra dependency only inside
the function that needs it, and raises `OptionalDependencyError` with the
name of the extra when it is absent, so a missing extra produces an
actionable message rather than an import error at startup.

```bash
pip install "discretus[viz]"          # rendering backends
pip install "discretus[docs]"         # documentation toolchain
pip install "discretus[dev]"          # tests, linters, type checker
pip install "discretus[viz,dev]"      # several at once
```

### The viz extra

The `viz` extra installs `matplotlib` and the Python bindings for Graphviz.
It is what you need in order to draw a graph, a Hasse diagram, a lattice, a
tree, a truth table, a Karnaugh map, a matrix heat map, or a Venn diagram to
a raster or vector image.

Two backends need nothing at all and are always available: the ASCII backend,
which renders into a terminal or into a docstring, and the SVG backend,
which writes markup directly. If your use of the library is textual, you do
not need this extra.

The Graphviz backend additionally requires the Graphviz system binaries,
which are a native program rather than a Python package and therefore cannot
be installed by pip. See [Installing Graphviz](#installing-graphviz) below.

### The docs extra

The `docs` extra installs Sphinx, the MyST Markdown parser, the Furo theme,
and the copy button extension. You need it only to build this documentation
locally, which is described in the contributing guide.

### The dev extra

The `dev` extra installs the full quality gate: `pytest` and `pytest-cov`
for the suite, `hypothesis` for the property based tests, `black` and
`isort` for formatting, `ruff` and `pylint` for lint, `mypy` for type
checking, `bandit` for security analysis, `pre-commit` for running all of it
before a commit, and `nox` for the interpreter matrix.

## Installing with conda

A conda package is available from conda-forge for users who prefer that
ecosystem.

```bash
conda install --channel conda-forge discretus
```

For development, the repository ships an environment file that creates the
whole toolchain, including the Graphviz system binaries that pip cannot
provide.

```bash
git clone https://github.com/olaflaitinen/discretus.git
cd discretus
conda env create --file environment.yml
conda activate discretus-dev
```

Update it after the file changes, removing packages that were dropped:

```bash
conda env update --file environment.yml --prune
```

Mixing conda and pip in one environment works but should be done
deliberately: install everything that conda-forge provides with conda first,
and only then install the remainder with pip, so that conda's solver sees
the full picture.

## Installing from source

Install from source when you want to contribute, when you need a fix that is
merged but not released, or when your policy requires building from a
reviewed tree.

```bash
git clone https://github.com/olaflaitinen/discretus.git
cd discretus
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,docs,viz]"
pre-commit install
```

The `-e` flag installs in editable mode, so an edit to a source file is
visible to the next interpreter start without reinstalling. That is what you
want while developing and not what you want in production, where a plain
`pip install .` produces an immutable installation.

To build the distribution artifacts the way the release workflow builds
them:

```bash
python -m pip install build twine
python -m build
python -m twine check dist/*
```

The result is a source distribution and a wheel under `dist/`, and the check
verifies that the metadata and the long description are well formed before
they reach an index.

To install a specific commit or tag directly, without a working tree:

```bash
pip install "git+https://github.com/olaflaitinen/discretus.git@v1.0.0"
pip install "git+https://github.com/olaflaitinen/discretus.git@main"
```

## Verifying the installation

Start with the version, which confirms that the package imports and tells
you what you have.

```bash
python -c "import discretus; print(discretus.__version__)"
```

A slightly fuller check exercises four domains and therefore confirms that
the lazy subpackage imports work:

```bash
python - <<'PY'
from discretus.sets import FiniteSet
from discretus.sets.operations import union
from discretus.logic.propositional import parse, is_tautology
from discretus.graphs import Graph
from discretus.graphs.shortest_path import dijkstra
from discretus.number_theory.primes import is_prime

print(union(FiniteSet({1, 2}), FiniteSet({2, 3})))
print(is_tautology(parse("p | ~p")))

g = Graph()
g.add_edges_from([("A", "B", 4), ("A", "C", 1), ("C", "B", 2)])
print(dijkstra(g, "A")[0]["B"])

print(is_prime(2_147_483_647))
PY
```

The command line interface is installed as a console script and as a
runnable module, and either is a quick end to end check:

```bash
discretus prime 2147483647
python -m discretus factor 600851475143
python -m discretus cnf "p -> (q -> r)"
```

To check the optional rendering stack, ask the visualization package which
backends it can see. The ASCII and SVG backends are always present; the
others appear when their dependencies are installed.

```python
from discretus.registry import VIZ_BACKENDS

print(VIZ_BACKENDS.names())
```

If you installed from source, run the suite. It should pass in full on a
supported interpreter, and the tests that need an optional dependency are
skipped rather than failed when that dependency is absent.

```bash
python -m pytest -q
```

## Installing Graphviz

Only the Graphviz rendering backend needs the system binaries. Every other
part of the library, including the ASCII, SVG, and matplotlib backends, works
without them.

| Platform | Command |
| --- | --- |
| Debian or Ubuntu | `sudo apt install graphviz` |
| Fedora | `sudo dnf install graphviz` |
| Arch | `sudo pacman -S graphviz` |
| macOS with Homebrew | `brew install graphviz` |
| macOS with MacPorts | `sudo port install graphviz` |
| Windows with winget | `winget install Graphviz.Graphviz` |
| Windows with Chocolatey | `choco install graphviz` |
| conda, any platform | `conda install -c conda-forge graphviz` |

Verify that the binaries are on the path, which is the part that most often
goes wrong on Windows, where the installer does not always add them:

```bash
dot -V
```

If that command is not found, the Python bindings will raise when the
backend is used, and the error message says so. Adding the Graphviz `bin`
directory to the path fixes it; a shell restart is usually required
afterwards.

## Offline and restricted environments

The library is a good citizen in an environment with no network access,
which is one of the reasons the core has no dependencies. Download once, on
a connected machine, then install from the local directory.

```bash
# On a connected machine, for the target platform and interpreter:
pip download discretus --dest ./wheels --only-binary :all:

# Transfer ./wheels, then on the target machine:
pip install --no-index --find-links ./wheels discretus
```

Because the wheel is universal, one download serves every platform, so the
usual complication of matching wheels to platforms does not arise.

For a fully pinned installation, which is what a grading sandbox or a
reproducible analysis should use, combine a requirements file with the
constraints file the repository ships:

```bash
pip install --constraint constraints.txt --requirement requirements-dev.txt
```

To disable network access explicitly while installing from a local
directory, which catches an accidental dependency on the index:

```bash
pip install --no-index --find-links ./wheels "discretus[viz]"
```

## Using a container

The repository provides a two stage image. The base stage installs the
library alone, and the development stage adds the test and documentation
toolchain.

```bash
# Build and run the library image.
docker build --target base --tag discretus:1.0.0 .
docker run --rm discretus:1.0.0

# Run the suite in the development image.
docker compose run --rm tests

# Build the documentation in the development image.
docker compose run --rm docs
```

The image declares the standard open container annotations, so a running
container can be traced back to the version and the source it was built
from:

```bash
docker inspect --format '{{ "{{" }} index .Config.Labels "org.opencontainers.image.version" {{ "}}" }}' discretus:1.0.0
```

## Using discretus in a notebook

The library needs nothing special in a notebook, and two of its features are
particularly suited to one.

Objects that can render themselves to LaTeX implement the rich display
protocol, so a truth table, a matrix, a polynomial, or a Hasse diagram
displays as typeset mathematics rather than as a repr when it is the value
of the last expression in a cell.

```bash
pip install "discretus[viz]" jupyterlab
jupyter lab
```

Step recording is the second. Turning it on for a cell, or for a whole
notebook, makes the routines that support it report their intermediate
reasoning, which is what makes a notebook a teaching artifact rather than a
calculator.

```python
from discretus.config import config_scope

with config_scope(explain=True):
    ...
```

## Continuous integration

An installation in continuous integration should be pinned, fast, and free
of the extras it does not need. For a project that depends on the library:

```yaml
- uses: actions/setup-python@v5
  with:
    python-version: "3.12"
    cache: pip

- run: python -m pip install --upgrade pip
- run: python -m pip install "discretus==1.0.0"
```

For a workflow that also renders figures, add the extra and the system
binaries:

```yaml
- run: sudo apt-get update && sudo apt-get install --yes graphviz
- run: python -m pip install "discretus[viz]==1.0.0"
```

The library's own pipeline additionally runs a job that installs the package
with no extras at all and exercises the command line interface, which is how
the promise that the core needs nothing is kept true rather than merely
stated.

## Configuration after installation

The library works with no configuration. Where it matters, the behaviour can
be set in code or through the environment, and `.env.example` in the
repository documents every variable with its default and accepted values.

```python
from discretus.config import set_config

set_config(
    max_enumeration=10_000,     # bound on materialized objects
    strict_validation=True,     # check preconditions even when costly
    notation="unicode",         # print formulas with mathematical symbols
    default_seed=20260115,      # make randomized routines reproducible
)
```

```bash
export DISCRETUS_MAX_ENUMERATION=10000
export DISCRETUS_NOTATION=unicode
```

A service that accepts user supplied formulas or graphs should lower
`max_enumeration` deliberately, because the default is chosen for
interactive use. The security policy in the repository discusses the
reasoning.

## Upgrading

```bash
pip install --upgrade discretus
```

Read the changelog before a minor or major upgrade. Within a major version
the public interface is backward compatible and an upgrade is safe; a major
version may remove interface that was deprecated at least one minor release
earlier, and each removal carries a migration note.

To see what a deprecation warns about before it becomes a removal, run your
own suite with warnings visible:

```bash
python -W error::DeprecationWarning -m pytest
```

## Uninstalling

```bash
pip uninstall discretus
```

The library writes no files outside its installation directory, creates no
cache in the home directory, and stores no state between processes, so
removing the package removes it completely. If you installed into a virtual
environment, deleting the environment directory is equivalent.

## Troubleshooting

**`ModuleNotFoundError: No module named 'discretus'` immediately after a
successful install.** The install and the interpreter are not the same
environment. Check which interpreter you are running and install with that
interpreter explicitly:

```bash
which python
python -m pip install discretus
python -c "import discretus, sys; print(sys.executable, discretus.__version__)"
```

**`OptionalDependencyError` naming a package and an extra.** Exactly what it
says: a feature needs an extra you did not install. The message contains the
command to run, for instance `pip install "discretus[viz]"`.

**A Graphviz backend raises even though the Python package is installed.**
The system binaries are missing or not on the path. Run `dot -V`, and see
[Installing Graphviz](#installing-graphviz).

**`LimitExceededError` from a routine that used to work.** The configured
enumeration limit was reached. Either the input grew, for instance a power
set whose ground set gained a few members and therefore doubled several
times, or the limit was lowered. Raise the limit deliberately, or use the
lazy generator, which the limit does not apply to.

**A result differs between two machines.** This should not happen for an
exact routine, and it is worth a defect report if it does. Check first
whether a randomized routine is involved without a seed, and whether a
float entered the computation through an input.

**`pip` selects an old version.** The index is being mirrored or cached.
Check what is available and ask for a specific version:

```bash
pip index versions discretus
pip install --upgrade --no-cache-dir "discretus==1.0.0"
```

**An installation into a system managed interpreter is refused.** Recent
distributions mark their interpreter as externally managed, which is
correct. Use a virtual environment rather than overriding the protection.

**The suite fails on a fresh source checkout.** Confirm that the install was
editable and included the dev extra, and that the interpreter is supported:

```bash
pip install -e ".[dev]"
python -m pytest -q
```

If a failure remains, it is worth a report. Include the interpreter version,
the platform, the installed extras, and the full output.

## Platform notes

**Linux.** Nothing to note beyond the choice of a virtual environment over
the distribution interpreter. On a minimal container image, confirm that the
interpreter was built with the standard library modules the package uses,
which every official image is.

**macOS.** The interpreter that ships with the operating system is older
than the supported floor on some releases. Install a current interpreter
from python.org, from Homebrew, or from conda, and create the virtual
environment with that one. On Apple silicon the universal wheel installs
unchanged, since there is nothing compiled to match.

**Windows.** Use `py -m venv .venv` and `.venv\Scripts\activate`. Two
things differ from the other platforms. Console output of the mathematical
symbols needs a terminal in a UTF-8 code page, which recent Windows Terminal
provides by default and the legacy console does not; if you see replacement
characters, set the notation to ASCII with
`set_config(notation="ascii")` or run `chcp 65001`. And the Graphviz
installer does not always add its `bin` directory to the path, which is the
single most common cause of a rendering failure on this platform.

**PyPy.** The library runs on PyPy and benefits from it, because the hot
paths are pure Python loops over integers. Expect the graph algorithms and
the satisfiability solver to be several times faster, and expect the exact
rational arithmetic to be closer to parity, since it is dominated by
unbounded integer work that CPython already implements in C.

**Browser and WebAssembly runtimes.** Because the package is a universal
wheel with no dependencies, it installs in Pyodide and similar runtimes with
`micropip`, which makes it usable in a browser based teaching environment.
The visualization extras are not available there, and the ASCII and SVG
backends are, which is usually what such an environment wants anyway.

## Installing with other package managers

The library declares standard metadata, so every manager that reads it works
without special handling.

```bash
# Poetry
poetry add discretus
poetry add "discretus[viz]"

# PDM
pdm add discretus

# uv
uv pip install discretus
uv add discretus

# Pipenv
pipenv install discretus

# Hatch, in pyproject.toml
# dependencies = ["discretus~=1.0"]
```

For a project that pins its dependencies in a lock file, pin the library the
same way you pin everything else. There is no transitive dependency tree to
resolve, so a lock entry for discretus is a single line and an upgrade can
never pull in an unrelated package.

## Installing for a teaching laboratory

A shared machine used by a class has requirements that a personal
installation does not, and the library is designed to meet them.

Install into a read only shared location and let each student use it without
being able to modify it. The library stores no state, writes nothing outside
its installation directory, and creates no cache in the home directory, so a
shared read only installation behaves exactly like a private one.

```bash
sudo python -m venv /opt/discretus
sudo /opt/discretus/bin/pip install "discretus==1.0.0"
# Students add /opt/discretus/bin to their path, or use the interpreter path.
```

Pin the version for the whole term, so that an exercise that worked in week
three still works in week eleven, and record the pin in the course
materials. Set the enumeration limit through the environment rather than
asking students to remember it, which turns an accidental request for a huge
power set into a clear error instead of a machine that stops responding.

```bash
# In the shared profile
export DISCRETUS_MAX_ENUMERATION=200000
```

For automated grading, add a seed so that any randomized exercise is
identical for every submission, and prefer the exact routines so that a
student's answer and the reference answer are compared as numbers rather
than as approximations.

```bash
export DISCRETUS_DEFAULT_SEED=20260115
```

## Verifying what you installed

For an environment where provenance matters, verify the artifact rather than
trusting the transfer. Ask pip to require hashes, which refuses to install
anything whose hash is not listed:

```bash
pip install --require-hashes --requirement pinned-requirements.txt
```

Inspect the installed metadata, which reports the version, the license, and
the declared dependencies, and should report no runtime dependency at all:

```bash
pip show --files discretus
python -c "import importlib.metadata as m; print(m.metadata('discretus')['License'])"
python -c "import importlib.metadata as m; print(m.requires('discretus'))"
```

The last command prints only the optional extras, each marked with the
environment marker that gates it. If it ever prints an unconditional
requirement, that is a defect in the packaging and is worth reporting.

## Dependency policy

Two commitments shape the dependency set and are worth stating, because they
determine what an upgrade can do to you.

The computational core will not gain a mandatory third party dependency
within a major version. That is what makes the library installable in a
locked down environment, and it is a design constraint rather than a
preference.

An optional dependency stays optional. A feature behind an extra is never
promoted into the core, and the import of an extra dependency happens inside
the function that needs it, so importing the library never imports a
plotting stack, and a missing extra never turns into a startup failure.
