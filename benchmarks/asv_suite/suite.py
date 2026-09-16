# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Bridge between the discretus benchmark harness and airspeed velocity.

The suite in the parent directory answers a question about the present: what
does this working tree cost right now. Airspeed velocity answers a question
about the past: how did that cost move across the history of the project. The
two questions want the same measurements, and there is no reason to declare
the measurements twice. This module is the adapter that lets the second tool
read the declarations written for the first.

Why an adapter is needed at all
===============================

Airspeed velocity discovers work to do by importing every module it finds
under its configured benchmark directory and then inspecting the module for
attributes whose name begins with one of its recognised prefixes, namely
``time_``, ``timeraw_``, ``mem_``, ``peakmem_``, and ``track_``. A class is
traversed for such methods, and the class name becomes part of the reported
benchmark identifier.

The harness in the parent package uses a different and deliberately more
explicit scheme. A benchmark is declared with a decorator that records the
routine, the sizes to measure it at, the complexity the reference documents
for it, the untimed setup that prepares an input, and the capability the
routine needs in order to run at all. None of that is expressible in a naming
convention, and none of it should be discarded in order to satisfy one.

So this module reads the harness registry and generates, for each declared
benchmark, one small class that airspeed velocity can discover. The generated
class carries the declared sizes as its parameter list, performs the declared
setup in its own untimed ``setup`` method, and exposes exactly one timed
method. Nothing is reimplemented: the routine, the inputs, the sizes, and the
skip condition all come from the single declaration in the ``bench_`` module.

Why the adapter lives in its own directory
==========================================

Airspeed velocity imports the modules under its benchmark directory as top
level modules, with that directory placed on the import path. The ``bench_``
modules cannot be imported that way, because they use relative imports to
reach the harness, and a relative import requires a parent package. Pointing
the configuration at the parent directory would therefore fail on every
module in it.

The adapter avoids the problem instead of working around it. It lives in a
directory of its own, so that directory is the only thing airspeed velocity
imports, and it reaches the harness through an ordinary absolute import after
putting the repository root on the import path. The ``bench_`` modules are
then imported as what they are, that is as submodules of the ``benchmarks``
package, by the harness discovery function.

What is measured, and what is not
=================================

Each generated class exposes a timed method and a peak memory method. The
timed method is the one that matters and the one the thresholds in the
configuration refer to. The memory method is reported alongside it because an
allocation regression in a pure Python library is usually the cause of a
timing regression rather than a separate event, and having both in the same
report saves a second run.

Airspeed velocity performs its own statistics, and its defaults are tuned for
benchmarks that take microseconds and can be repeated thousands of times. The
routines here are coarse by comparison, so the generated classes set the
iteration count to one and let the declared repetition count from the harness
decide how many samples are taken. The warm up is performed in the untimed
setup rather than left to the tool, which keeps the first timed sample
comparable to the rest.

Running it
==========

Airspeed velocity is an optional development tool. It is installed through
the pip section of environment.yml and is imported by nothing in the library.

    asv run ALL --config benchmarks/asv.conf.json
    asv run v1.0.0..main --config benchmarks/asv.conf.json
    asv continuous main HEAD --config benchmarks/asv.conf.json
    asv compare v1.0.0 main --config benchmarks/asv.conf.json
    asv publish --config benchmarks/asv.conf.json
    asv preview --config benchmarks/asv.conf.json

A single benchmark, which is the useful form while investigating one routine,
is selected by the identifier the report shows:

    asv run --bench suite.union_integers --config benchmarks/asv.conf.json

The module is also runnable on its own, which is how a contributor checks
that the generation worked without waiting for a historical run:

    python benchmarks/asv_suite/suite.py

That prints the number of generated classes, the number whose requirement is
satisfied in the current build, and the identifier of each one, which is
exactly what the configuration thresholds have to be written against.
"""

from __future__ import annotations

import pathlib
import sys
from typing import Any, Callable, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Import path
# ---------------------------------------------------------------------------

#: The repository root, which is two levels above this file. The path is
#: derived from the file rather than from the working directory, because
#: airspeed velocity runs with the working directory set to a build tree
#: whose location is an implementation detail of the tool.
REPOSITORY_ROOT = pathlib.Path(__file__).resolve().parents[2]

if str(REPOSITORY_ROOT) not in sys.path:
    # Inserted at the front rather than appended, so that the harness in this
    # checkout is the one measured. An installed copy of the same name, if one
    # ever existed, would otherwise shadow it and the measurement would
    # silently describe the wrong code.
    sys.path.insert(0, str(REPOSITORY_ROOT))

from benchmarks import (  # noqa: E402 - the path has to be set up first
    BASE_SEED,
    REGISTRY,
    Benchmark,
    discover,
    group_names,
)

# ---------------------------------------------------------------------------
# Tool configuration shared by every generated class
# ---------------------------------------------------------------------------

#: Seconds allowed for one benchmark before airspeed velocity abandons it.
#: The value matches the default timeout in the configuration file, and is
#: repeated here because a generated class does not inherit it.
TIMEOUT = 120.0

#: Iterations per sample. One, because the routines measured here take
#: milliseconds or more, so the timer resolution is not the limiting factor
#: and a larger count would only make a single sample slower to obtain.
NUMBER = 1

#: Seconds of automatic warm up. Zero, because the warm up is performed in
#: the untimed setup instead, using the repetition count the benchmark itself
#: declared. Leaving it to the tool would warm up for a fixed duration
#: regardless of what the routine actually needs.
WARMUP_TIME = 0.0

#: Minimum number of samples airspeed velocity insists on collecting. One,
#: for the same reason as the iteration count: the tool must not decide to
#: repeat an expensive enumeration in order to satisfy a statistical default.
MIN_RUN_COUNT = 1

#: Processes to run each benchmark in. Two, so that a result that depends on
#: a warm interpreter rather than on the routine shows up as a disagreement
#: between processes instead of being reported as a clean number.
PROCESSES = 2

#: The seed every generated benchmark inherits, recorded here so that the
#: value appears in the report metadata and a reader can reproduce an input.
SEED = BASE_SEED


# ---------------------------------------------------------------------------
# Registry access
# ---------------------------------------------------------------------------


def load_registry() -> List[Benchmark]:
    """Import every benchmark module and return the declared benchmarks.

    The harness registry is populated as a side effect of importing the
    ``bench_`` modules, so discovery has to happen before the registry is
    read. Discovery is idempotent, because a module that is already imported
    is not imported again, so calling this more than once is harmless.

    Returns:
        Every declared benchmark, in declaration order. The order matters
        only for readability of the generated listing; airspeed velocity
        sorts the report by identifier regardless.
    """
    discover()
    return list(REGISTRY)


def benchmarks_by_name() -> Dict[str, Benchmark]:
    """Return the declared benchmarks keyed by their name.

    Names are unique across the whole suite, which is what makes a flat
    identifier space possible. A duplicate would silently shadow an earlier
    declaration here, so it is reported rather than tolerated.

    Returns:
        A mapping from benchmark name to benchmark.

    Raises:
        RuntimeError: If two benchmarks share a name.
    """
    mapping: Dict[str, Benchmark] = {}
    for item in load_registry():
        if item.name in mapping:
            raise RuntimeError(
                "two benchmarks are named "
                f"{item.name!r}: {mapping[item.name].group} "
                f"and {item.group}"
            )
        mapping[item.name] = item
    return mapping


def domain_names() -> List[str]:
    """Return the top level domains, without their subgroup suffixes.

    A benchmark declares a group such as ``graphs.shortest_path``, and the
    part before the first dot is the package it belongs to. The availability
    tracking below reports one number per package rather than one per
    subgroup, because the question it answers is which parts of the library
    are built at a given commit.

    Returns:
        The distinct top level domains, in declaration order.
    """
    seen: List[str] = []
    for group in group_names():
        domain = group.split(".", 1)[0]
        if domain not in seen:
            seen.append(domain)
    return seen


# ---------------------------------------------------------------------------
# Preparation
# ---------------------------------------------------------------------------


def prepare(item: Benchmark, size: Any) -> Callable[[], Any]:
    """Return a callable that performs the benchmark once, untimed setup done.

    This mirrors the calling convention of the harness exactly, because a
    measurement taken through this adapter has to be comparable to one taken
    through ``python -m benchmarks``. The convention has three cases:

    When the benchmark declares a setup, the setup is called with the size,
    its return value is the payload, and the payload is passed to the
    function. This is the usual case, and it is what keeps input construction
    out of the measurement.

    When the benchmark declares no setup, the size itself is the payload and
    is passed to the function. This suits a routine whose input is a single
    number, such as a factorisation or a sieve.

    When the payload is ``None``, the function is called with no arguments at
    all. This suits a benchmark that does not vary with size and constructs
    whatever it needs internally.

    Args:
        item: The benchmark to prepare.
        size: The size to prepare for.

    Returns:
        A callable of no arguments that performs one repetition of the work.
    """
    payload = item.setup(size) if item.setup is not None else size
    if payload is None:
        return item.function
    return lambda: item.function(payload)


# ---------------------------------------------------------------------------
# The generated benchmark classes
# ---------------------------------------------------------------------------


class BenchmarkAdapter:
    """Base class for the generated per benchmark adapters.

    A subclass is generated for every declared benchmark. The subclass sets
    three attributes and inherits everything else:

    ``item``
        The declaration this adapter measures.

    ``params``
        A list of one list, holding the sizes the benchmark declared. One
        list means one parameter, which is what ``param_names`` names.

    ``pretty_name``
        The qualified name, that is the group and the benchmark name joined
        by a dot, so that the report groups related routines together even
        though the identifier space is flat.

    The class is not itself discovered by airspeed velocity, because it
    declares no sizes and its ``item`` is ``None``. Its timed methods are
    inherited by the subclasses, and a subclass identifier is what the report
    and the regression thresholds refer to.
    """

    #: The declaration being measured. ``None`` on the base class, which is
    #: what makes the base class inert rather than a benchmark of nothing.
    item: Optional[Benchmark] = None

    #: The parameter names airspeed velocity shows in the report.
    param_names = ["size"]

    #: The sizes to measure at. Overridden by every generated subclass.
    params: Tuple[List[Any], ...] = ([],)

    timeout = TIMEOUT
    number = NUMBER
    warmup_time = WARMUP_TIME
    min_run_count = MIN_RUN_COUNT
    processes = PROCESSES

    def setup(self, size: Any) -> None:
        """Prepare the input for one size, without timing the preparation.

        Three outcomes are possible, and each is deliberate.

        When the routine is not available in the build being measured, this
        raises ``NotImplementedError``, which is how airspeed velocity is
        told to record the combination as skipped rather than as a failure.
        That is the same treatment the harness gives an unavailable routine,
        and it is what allows the suite to run against a commit from before
        the routine existed. A historical run spans the whole development of
        the library, so most commits are missing most routines, and a suite
        that failed on them would produce no usable record at all.

        When the preparation itself fails, the exception propagates and
        airspeed velocity records a failure. A setup that raises is a bug in
        the benchmark or in the library, not a missing capability, and hiding
        it would turn a real defect into a silent gap in the report.

        Otherwise the prepared callable is stored on the instance and the
        declared warm up repetitions are performed. The warm up is not timed,
        and it exists so that the first timed sample is not the one that pays
        for a first touch of a page, a lazily imported submodule, or an
        interned constant.

        Args:
            size: The size to prepare for, taken from the parameter list.

        Raises:
            NotImplementedError: If the routine is not available here.
        """
        item = type(self).item
        if item is None or item.requires is None:
            raise NotImplementedError("the routine is not available in this build")
        self.call = prepare(item, size)
        for _ in range(item.warmup):
            self.call()

    def teardown(self, size: Any) -> None:
        """Release the prepared input.

        Airspeed velocity keeps the instance alive between samples, and some
        of the inputs here are large, a graph on a million edges among them.
        Dropping the reference means the next parameter combination starts
        from a comparable memory state rather than from whichever combination
        happened to run before it.

        Args:
            size: The size that was prepared, unused but part of the calling
                convention airspeed velocity uses for a parametrised
                benchmark.
        """
        self.call = None

    def time_run(self, size: Any) -> None:
        """Perform the work once, which is the measurement.

        The method body is deliberately nothing but the call. Anything else
        here, an assertion or a size check for instance, would be inside the
        measured region and would be attributed to the routine.

        Args:
            size: The size being measured, unused because the prepared
                callable already closed over its input.
        """
        self.call()

    def peakmem_run(self, size: Any) -> None:
        """Perform the work once while airspeed velocity watches memory.

        Peak memory is reported for the whole process, so the figure includes
        the interpreter and the prepared input as well as the routine. That
        makes the absolute number uninteresting and the trend across history
        informative, which is the same way the timing figures should be read.

        Args:
            size: The size being measured, unused for the same reason as in
                the timed method.
        """
        self.call()


# ---------------------------------------------------------------------------
# Generation
# ---------------------------------------------------------------------------

#: Attribute names that already exist in this module and therefore cannot be
#: used for a generated class. A benchmark whose name collided with one of
#: these would replace the module attribute and break the generation, so the
#: collision is reported instead of resolved by mangling the name: a report
#: identifier that differs from the name in the source would be worse than a
#: build error, because it would only be noticed while reading a report.
RESERVED_NAMES = frozenset(
    {
        "BASE_SEED",
        "Benchmark",
        "BenchmarkAdapter",
        "MIN_RUN_COUNT",
        "NUMBER",
        "PROCESSES",
        "REGISTRY",
        "REPOSITORY_ROOT",
        "RESERVED_NAMES",
        "SEED",
        "TIMEOUT",
        "WARMUP_TIME",
        "benchmarks_by_name",
        "build_adapter",
        "discover",
        "domain_names",
        "generate",
        "group_names",
        "load_registry",
        "pathlib",
        "prepare",
        "sys",
    }
)


def build_adapter(item: Benchmark) -> type:
    """Return a class airspeed velocity can discover for one benchmark.

    The generated class is a subclass of :class:`BenchmarkAdapter` carrying
    the declaration, the declared sizes as its single parameter list, and the
    declared repetition count as the number of samples to collect. Its name
    is the benchmark name unchanged, so the identifier in a published report
    is the identifier a contributor would pass to the harness on the command
    line, and a regression threshold written against one is readable against
    the other.

    The docstring of the generated class is assembled from the declaration,
    because airspeed velocity shows it in the report. Putting the documented
    complexity there means a reader looking at a curve sees what the curve
    was supposed to be without leaving the page.

    Args:
        item: The benchmark to generate an adapter for.

    Returns:
        The generated class.

    Raises:
        ValueError: If the benchmark name is not usable as a class name.
    """
    if not item.name.isidentifier():
        raise ValueError(f"benchmark name {item.name!r} is not a valid identifier")
    if item.name in RESERVED_NAMES:
        raise ValueError(
            f"benchmark name {item.name!r} collides with a module attribute"
        )

    lines = [f"Measure {item.qualified_name}."]
    if item.complexity:
        lines.append("")
        lines.append(f"Documented complexity: {item.complexity}.")
    if item.note:
        lines.append("")
        lines.append(item.note)

    namespace: Dict[str, Any] = {
        "__doc__": "\n".join(lines),
        "item": item,
        "params": [list(item.sizes)],
        "param_names": ["size"],
        "pretty_name": item.qualified_name,
        "repeat": item.repeats,
    }
    return type(item.name, (BenchmarkAdapter,), namespace)


def generate() -> Dict[str, type]:
    """Generate one adapter class for every declared benchmark.

    Returns:
        A mapping from class name to generated class. The caller injects the
        mapping into the module namespace, which is where airspeed velocity
        looks for it. Returning it rather than injecting it directly keeps
        the function testable, and keeps the one mutation of module state in
        a single visible place below.
    """
    return {name: build_adapter(item) for name, item in benchmarks_by_name().items()}


#: The generated classes, kept in a mapping as well as in the module
#: namespace so that the self check below can count them without inspecting
#: the namespace and guessing which attributes are benchmarks.
ADAPTERS = generate()

globals().update(ADAPTERS)


# ---------------------------------------------------------------------------
# Availability tracking
# ---------------------------------------------------------------------------


class Availability:
    """Record how much of the library is measurable at each commit.

    This is not a timing benchmark. It is a tracked quantity, which airspeed
    velocity records and plots exactly like a timing but without running
    anything, and it exists because a historical timing report has a gap
    wherever a routine did not yet exist. Reading such a report without
    knowing when each package was built invites the wrong conclusion, namely
    that a measurement disappeared when in fact it had not yet appeared.

    The recorded number is how many of the declared benchmarks for a domain
    find their routine present in the build being measured. It rises as the
    library is built out, and a fall in it is a genuine signal worth
    investigating: a routine that was measurable and is no longer measurable
    has either been renamed or removed.
    """

    params = [domain_names()]
    param_names = ["domain"]
    timeout = TIMEOUT

    def track_available(self, domain: str) -> int:
        """Return the number of measurable benchmarks in one domain.

        Args:
            domain: The top level domain, such as ``graphs``.

        Returns:
            The count of declared benchmarks in that domain whose routine is
            available here.
        """
        return sum(
            1
            for item in load_registry()
            if item.group.split(".", 1)[0] == domain and item.requires is not None
        )

    def track_declared(self, domain: str) -> int:
        """Return the number of declared benchmarks in one domain.

        Args:
            domain: The top level domain, such as ``graphs``.

        Returns:
            The count of declarations, available or not. Together with the
            available count this gives the ratio a reader needs, and keeping
            them as two tracked numbers rather than one ratio means each can
            be read on its own axis.
        """
        return sum(
            1 for item in load_registry() if item.group.split(".", 1)[0] == domain
        )


Availability.track_available.unit = "benchmarks"
Availability.track_declared.unit = "benchmarks"


__all__ = [
    "ADAPTERS",
    "Availability",
    "BenchmarkAdapter",
    "MIN_RUN_COUNT",
    "NUMBER",
    "PROCESSES",
    "REPOSITORY_ROOT",
    "RESERVED_NAMES",
    "SEED",
    "TIMEOUT",
    "WARMUP_TIME",
    "benchmarks_by_name",
    "build_adapter",
    "domain_names",
    "generate",
    "load_registry",
    "prepare",
] + sorted(ADAPTERS)


# ---------------------------------------------------------------------------
# Self check
# ---------------------------------------------------------------------------


def _self_check() -> int:
    """Print what was generated, which is what the configuration refers to.

    Returns:
        A process exit status: zero when at least one adapter was generated,
        and one when none were, because an empty suite means the generation
        silently failed and a historical run would produce nothing.
    """
    items = benchmarks_by_name()
    available = sum(1 for item in items.values() if item.requires is not None)
    print(f"generated {len(ADAPTERS)} adapters from {len(items)} declarations")
    print(f"{available} of {len(items)} are available in this build")
    print(f"domains: {', '.join(domain_names())}")
    print(f"seed: {SEED}")
    print()
    width = max((len(name) for name in ADAPTERS), default=0)
    for name in sorted(ADAPTERS):
        item = items[name]
        state = "available" if item.requires is not None else "unavailable"
        sizes = ", ".join(str(size) for size in item.sizes)
        print(f"suite.{name.ljust(width)}  {state:<11}  sizes: {sizes}")
    return 0 if ADAPTERS else 1


if __name__ == "__main__":
    raise SystemExit(_self_check())


# Notes on reading these results
# ==============================
#
# A historical report is read differently from a single run, and the
# difference is worth stating because the same numbers support different
# conclusions.
#
# A step in a curve is the interesting shape. It means one commit changed the
# cost, and the commit is named in the report, so the question becomes
# whether that change was intended. A gradual drift across many commits is
# almost always the machine rather than the library: a historical run can
# span days of wall clock time and several runner generations.
#
# A curve that starts partway along the history has not regressed from
# nothing. It started when the routine was first implemented, which the
# availability tracking above makes explicit.
#
# A change of slope between two sizes of the same benchmark matters more than
# a change of absolute value at one size. The reference documents an
# asymptotic bound, and an asymptotic bound is a statement about slope. The
# growth report of the harness in the parent package states the implied
# exponent directly, and is the better tool for that question; airspeed
# velocity is the better tool for the question of when the slope changed.
#
# The peak memory figures are process wide and include the prepared input, so
# a large input dominates them. They are useful for spotting the commit at
# which a routine began materialising a structure it used to stream, and they
# are not useful as an estimate of what a routine costs in isolation.
