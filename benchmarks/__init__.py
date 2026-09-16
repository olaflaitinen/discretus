# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Benchmark harness for discretus.

The library documents the asymptotic complexity of every nontrivial routine.
A documented bound is only credible if it is measured, and this package is
where the measuring happens. It is deliberately small and dependency free, so
that it runs in the same restricted environments the library itself installs
in, and so that a measurement never depends on a benchmarking framework whose
own overhead has to be reasoned about.

What this harness is for:

    Detecting a change of asymptotic behaviour. A routine documented as
    linear that becomes quadratic shows up immediately in the growth ratios,
    and a growth rate survives a noisy machine.

    Detecting a large constant factor change, roughly a factor of two or
    more, which is the resolution a shared continuous integration runner can
    actually deliver.

    Recording what the library costs, so that the complexity statements in
    the reference can be checked against reality rather than trusted.

What it is not for:

    Resolving a few percent. The timer is honest, and the machine is not:
    a shared runner varies its processor model between jobs, and a laptop
    varies its clock with its temperature. A difference inside that margin is
    not evidence either way, and the reporting deliberately refuses to
    highlight one.

    Comparing against another library. That comparison is worth making and
    belongs in a document with its methodology stated, not in a suite whose
    inputs were chosen to exercise this library's own code paths.

Design decisions, each of which has an alternative that was rejected:

    Time is measured with the monotonic performance counter, and the
    reported figure is the minimum of several repetitions rather than the
    mean. For a deterministic computation the variation between repetitions
    is noise from the machine, so the minimum is the closest available
    estimate of the true cost. The mean, the median, and the standard
    deviation are also recorded, because a large spread is itself
    information: it usually means the benchmark is dominated by allocation
    or by the garbage collector rather than by the routine.

    The garbage collector is disabled during a measurement and re enabled
    afterwards. A collection that happens to fall inside one repetition and
    not another is the single largest source of spurious variation in a
    Python microbenchmark.

    Every input is generated from an explicit seed, so a measurement can be
    repeated exactly. A benchmark whose input changes between runs cannot
    detect a regression, because a difference could always be the input.

    A benchmark whose routine is not available is skipped rather than
    failing. The library is built out package by package, and a suite that
    fails on a package that does not exist yet would have to be edited on
    every merge.

    Nothing here imports a third party package. The standard library
    provides the timer, the statistics, and the JSON writer.

Usage:

    python -m benchmarks                        # run everything
    python -m benchmarks --group graphs         # one domain
    python -m benchmarks --filter dijkstra      # one routine
    python -m benchmarks --quick                # the small sizes only
    python -m benchmarks --json results.json    # machine readable output
    python -m benchmarks --compare old.json     # against an earlier run
    python -m benchmarks --list                 # what would run

Writing a benchmark:

    from benchmarks import benchmark, require

    module = require("discretus.number_theory.primes")


    @benchmark(group="number_theory", sizes=[10_000, 100_000, 1_000_000],
               complexity="O(n log log n)", requires=module)
    def sieve(size):
        module.primes_up_to(size)

The decorated function receives one size and performs the work once. The
harness handles the warm up, the repetitions, the timing, and the reporting.
"""

from __future__ import annotations

import gc
import json
import math
import platform
import random
import statistics
import sys
import time
from dataclasses import asdict, dataclass, field
from importlib import import_module
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Optional,
    Sequence,
    Tuple,
)

__all__ = [
    "DEFAULT_REPEATS",
    "DEFAULT_WARMUP",
    "QUICK_SIZE_LIMIT",
    "Benchmark",
    "BenchmarkResult",
    "REGISTRY",
    "benchmark",
    "require",
    "requires_all",
    "seeded",
    "random_integers",
    "random_pairs",
    "random_words",
    "discover",
    "run_all",
    "run_one",
    "group_names",
    "format_results",
    "format_growth",
    "format_comparison",
    "results_to_json",
    "results_from_json",
    "compare_results",
    "environment",
]

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------

#: Number of timed repetitions per measurement. Five is enough for the
#: minimum to be stable on a quiet machine and cheap enough that the whole
#: suite finishes in a few minutes.
DEFAULT_REPEATS = 5

#: Number of untimed repetitions before the timed ones. The first call warms
#: the import, the memoization caches, and the interpreter's own caches, and
#: including it would measure the warm up rather than the routine.
DEFAULT_WARMUP = 1

#: In quick mode, sizes above this value are skipped. Quick mode exists for a
#: pull request, where the question is whether anything changed by a large
#: factor rather than what the growth rate is.
QUICK_SIZE_LIMIT = 100_000

#: A measurement shorter than this is reported with a warning, because at
#: that scale the timer resolution and the loop overhead are a material part
#: of the number.
MINIMUM_RELIABLE_SECONDS = 1e-5

#: The seed every input generator derives from, so that the whole suite is
#: reproducible and two runs differ only in the machine.
BASE_SEED = 20260115


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Benchmark:
    """One measurable routine, at one or more input sizes.

    Attributes:
        name: Unique identifier, normally the routine being measured.
        group: The domain it belongs to, used for filtering and reporting.
        function: Callable that performs the work once for a given size.
        sizes: The input sizes to measure. A single entry means the
            benchmark does not vary with size, in which case the growth
            report omits it.
        complexity: The complexity the reference documents, recorded so that
            the growth report can state what was expected.
        repeats: Timed repetitions, overriding the default.
        warmup: Untimed repetitions, overriding the default.
        setup: Optional callable that prepares an input for a size and
            returns it. When present, the prepared value is passed to the
            function instead of the size, and the preparation is not timed.
        requires: The module the benchmark needs, or ``None`` when the
            requirement is unavailable, in which case the benchmark is
            skipped.
        note: Free text shown in the detailed report.
    """

    name: str
    group: str
    function: Callable[..., Any]
    sizes: Tuple[Any, ...] = (None,)
    complexity: str = ""
    repeats: int = DEFAULT_REPEATS
    warmup: int = DEFAULT_WARMUP
    setup: Optional[Callable[[Any], Any]] = None
    requires: Optional[Any] = None
    note: str = ""

    @property
    def qualified_name(self) -> str:
        """Return the name prefixed by its group."""
        return f"{self.group}.{self.name}"

    @property
    def varies_with_size(self) -> bool:
        """Return whether the benchmark was declared with several sizes."""
        return len(self.sizes) > 1


@dataclass
class BenchmarkResult:
    """The outcome of measuring one benchmark at one size.

    A result is always produced, even when the measurement did not happen,
    so that a report distinguishes a benchmark that was skipped from one that
    was never declared.
    """

    name: str
    group: str
    size: Any
    status: str = "ok"
    times: List[float] = field(default_factory=list)
    complexity: str = ""
    note: str = ""
    message: str = ""

    @property
    def best(self) -> float:
        """Return the fastest repetition, which is the reported figure."""
        return min(self.times) if self.times else float("nan")

    @property
    def worst(self) -> float:
        """Return the slowest repetition."""
        return max(self.times) if self.times else float("nan")

    @property
    def mean(self) -> float:
        """Return the arithmetic mean of the repetitions."""
        return statistics.fmean(self.times) if self.times else float("nan")

    @property
    def median(self) -> float:
        """Return the median of the repetitions."""
        return statistics.median(self.times) if self.times else float("nan")

    @property
    def spread(self) -> float:
        """Return the relative spread, that is the range over the minimum.

        A spread above roughly one half usually means the measurement is
        dominated by something other than the routine, most often allocation.
        """
        if len(self.times) < 2 or self.best == 0:
            return float("nan")
        return (self.worst - self.best) / self.best

    @property
    def reliable(self) -> bool:
        """Return whether the measurement is long enough to be meaningful."""
        return bool(self.times) and self.best >= MINIMUM_RELIABLE_SECONDS

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON compatible dictionary describing the result."""
        payload = asdict(self)
        payload.update(
            {
                "best": self.best,
                "worst": self.worst,
                "mean": self.mean,
                "median": self.median,
                "spread": self.spread,
                "reliable": self.reliable,
            }
        )
        return payload

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "BenchmarkResult":
        """Rebuild a result from the output of :meth:`to_dict`."""
        return cls(
            name=payload["name"],
            group=payload["group"],
            size=payload.get("size"),
            status=payload.get("status", "ok"),
            times=list(payload.get("times", [])),
            complexity=payload.get("complexity", ""),
            note=payload.get("note", ""),
            message=payload.get("message", ""),
        )


#: Every declared benchmark, in declaration order, which is the order the
#: report uses so that a run reads like the source.
REGISTRY: List[Benchmark] = []


# ---------------------------------------------------------------------------
# Declaration
# ---------------------------------------------------------------------------


def benchmark(
    group: str,
    sizes: Optional[Sequence[Any]] = None,
    complexity: str = "",
    repeats: int = DEFAULT_REPEATS,
    warmup: int = DEFAULT_WARMUP,
    setup: Optional[Callable[[Any], Any]] = None,
    requires: Optional[Any] = None,
    name: Optional[str] = None,
    note: str = "",
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Register the decorated function as a benchmark.

    Args:
        group: The domain the benchmark belongs to.
        sizes: Input sizes to measure. Defaults to a single unnamed size.
        complexity: The complexity the reference documents.
        repeats: Timed repetitions.
        warmup: Untimed repetitions.
        setup: Optional preparation, not timed, whose result is passed to the
            function instead of the size.
        requires: The module the benchmark needs. ``None`` marks it as
            unavailable, which skips it rather than failing.
        name: Overrides the function name.
        note: Free text for the detailed report.

    Returns:
        The function unchanged, so that it remains directly callable.
    """

    def decorator(function: Callable[..., Any]) -> Callable[..., Any]:
        REGISTRY.append(
            Benchmark(
                name=name or function.__name__,
                group=group,
                function=function,
                sizes=tuple(sizes) if sizes else (None,),
                complexity=complexity,
                repeats=repeats,
                warmup=warmup,
                setup=setup,
                requires=requires,
                note=note,
            )
        )
        return function

    return decorator


def require(path: str, *names: str) -> Optional[Any]:
    """Import a module, returning ``None`` when it cannot be used.

    The library is built out package by package, so a benchmark file may
    reference a module that does not exist yet, or one that exists as an
    empty placeholder and therefore imports without providing anything.
    Both cases must report as unavailable rather than as an error, because a
    suite that failed on a package still being written would have to be
    edited on every merge.

    Importability alone is not enough to decide that, because an empty
    module imports successfully. The names a benchmark actually calls are
    therefore passed in and checked, which makes the requirement a statement
    about capability rather than about the module's existence.

    Args:
        path: The dotted module path.
        *names: Attributes the benchmarks in this file will use. When any of
            them is absent, the module counts as unavailable.

    Returns:
        The imported module, or ``None``.

    Example:
        >>> require("json", "loads", "dumps") is not None
        True
        >>> require("json", "no_such_function") is None
        True
        >>> require("no.such.module") is None
        True
    """
    try:
        module = import_module(path)
    except Exception:  # noqa: BLE001 - any import failure means unavailable
        return None
    for name in names:
        if not hasattr(module, name):
            return None
    return module


def requires_all(*modules: Optional[Any]) -> Optional[Any]:
    """Return the first module when every argument is available.

    Several benchmarks need two or three modules at once, for instance a
    graph type and an algorithm over it. This helper keeps the declaration
    readable.

    Args:
        *modules: The results of :func:`require`.

    Returns:
        The first module, or ``None`` when any argument is ``None``.
    """
    if not modules or any(module is None for module in modules):
        return None
    return modules[0]


# ---------------------------------------------------------------------------
# Deterministic input generation
# ---------------------------------------------------------------------------


def seeded(label: str) -> random.Random:
    """Return a generator seeded deterministically from a label.

    Deriving the seed from a label means every benchmark has its own
    reproducible stream without anybody maintaining a table of numbers, and a
    renamed benchmark gets a fresh stream rather than silently sharing one.

    Args:
        label: Any string, normally the benchmark name.

    Returns:
        An independent :class:`random.Random`.
    """
    digest = 0
    for character in label:
        digest = (digest * 131 + ord(character)) & 0xFFFFFFFF
    return random.Random(BASE_SEED ^ digest)  # nosec B311


def random_integers(
    count: int,
    low: int = 1,
    high: int = 10**9,
    label: str = "integers",
) -> List[int]:
    """Return a reproducible list of integers in a range."""
    source = seeded(label)
    return [source.randint(low, high) for _ in range(count)]


def random_pairs(
    count: int,
    vertices: int,
    label: str = "pairs",
) -> List[Tuple[int, int]]:
    """Return reproducible distinct unordered pairs over a vertex range.

    Used by the graph benchmarks to build an input without depending on the
    graph generators, so that a benchmark of a generator is not measured
    against itself.
    """
    source = seeded(label)
    seen = set()
    pairs: List[Tuple[int, int]] = []
    attempts = 0
    limit = count * 20 + 100
    while len(pairs) < count and attempts < limit:
        attempts += 1
        left = source.randrange(vertices)
        right = source.randrange(vertices)
        if left == right:
            continue
        edge = (min(left, right), max(left, right))
        if edge in seen:
            continue
        seen.add(edge)
        pairs.append(edge)
    return pairs


def random_words(
    count: int,
    length: int = 8,
    label: str = "words",
) -> List[str]:
    """Return a reproducible list of lower case words.

    Several benchmarks use string members rather than integers, because the
    library allows any hashable value and a routine that is fast for integers
    and slow for strings is worth detecting.
    """
    source = seeded(label)
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    return [
        "".join(source.choice(alphabet) for _ in range(length))
        for _ in range(count)
    ]


# ---------------------------------------------------------------------------
# Measurement
# ---------------------------------------------------------------------------


def _time_once(call: Callable[[], Any]) -> float:
    """Return the elapsed time of one call, in seconds."""
    start = time.perf_counter()
    call()
    return time.perf_counter() - start


def run_one(item: Benchmark, size: Any, quick: bool = False) -> BenchmarkResult:
    """Measure one benchmark at one size.

    The sequence is: skip when the requirement is missing, skip when quick
    mode excludes the size, prepare the input without timing it, perform the
    warm up repetitions, disable the garbage collector, time the repetitions,
    and re enable the collector.

    Args:
        item: The benchmark to measure.
        size: The size to measure at.
        quick: Whether to skip the larger sizes.

    Returns:
        A result, which reports a status of ``ok``, ``skipped``, or ``error``.
    """
    result = BenchmarkResult(
        name=item.name,
        group=item.group,
        size=size,
        complexity=item.complexity,
        note=item.note,
    )

    if item.requires is None:
        result.status = "skipped"
        result.message = "the routine is not available in this build"
        return result

    if quick and isinstance(size, int) and size > QUICK_SIZE_LIMIT:
        result.status = "skipped"
        result.message = f"size {size} is above the quick mode limit"
        return result

    try:
        payload = item.setup(size) if item.setup is not None else size
    except Exception as error:  # noqa: BLE001 - report rather than abort
        result.status = "error"
        result.message = f"setup failed: {type(error).__name__}: {error}"
        return result

    if payload is None:
        call: Callable[[], Any] = item.function
    else:
        call = lambda: item.function(payload)  # noqa: E731 - a timed thunk

    try:
        for _ in range(item.warmup):
            call()
    except Exception as error:  # noqa: BLE001
        result.status = "error"
        result.message = f"warm up failed: {type(error).__name__}: {error}"
        return result

    collecting = gc.isenabled()
    gc.collect()
    gc.disable()
    try:
        for _ in range(item.repeats):
            result.times.append(_time_once(call))
    except Exception as error:  # noqa: BLE001
        result.status = "error"
        result.message = f"{type(error).__name__}: {error}"
    finally:
        if collecting:
            gc.enable()

    return result


def run_all(
    groups: Optional[Iterable[str]] = None,
    pattern: Optional[str] = None,
    quick: bool = False,
    progress: bool = True,
) -> List[BenchmarkResult]:
    """Measure every registered benchmark that matches the filters.

    Args:
        groups: Only these groups, or every group when ``None``.
        pattern: Only benchmarks whose qualified name contains this text.
        quick: Whether to skip the larger sizes.
        progress: Whether to report each benchmark as it runs, on standard
            error so that a redirected report stays clean.

    Returns:
        Every result, in declaration order.
    """
    wanted = set(groups) if groups else None
    results: List[BenchmarkResult] = []

    for item in REGISTRY:
        if wanted is not None and item.group not in wanted:
            continue
        if pattern and pattern.lower() not in item.qualified_name.lower():
            continue
        for size in item.sizes:
            if progress:
                label = item.qualified_name
                suffix = "" if size is None else f" at {size}"
                print(f"running {label}{suffix}", file=sys.stderr, flush=True)
            results.append(run_one(item, size, quick=quick))

    return results


def group_names() -> List[str]:
    """Return the declared groups, in declaration order without duplicates."""
    seen: List[str] = []
    for item in REGISTRY:
        if item.group not in seen:
            seen.append(item.group)
    return seen


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------


def _format_seconds(value: float) -> str:
    """Return a duration in the unit that keeps three significant digits."""
    if value != value:  # not a number
        return "-"
    if value >= 1:
        return f"{value:.3f} s"
    if value >= 1e-3:
        return f"{value * 1e3:.3f} ms"
    if value >= 1e-6:
        return f"{value * 1e6:.3f} us"
    return f"{value * 1e9:.1f} ns"


def _format_size(size: Any) -> str:
    """Return a size rendered for the report."""
    if size is None:
        return ""
    if isinstance(size, int):
        return f"{size:,}"
    return str(size)


def format_results(results: Sequence[BenchmarkResult]) -> str:
    """Return a table of every result, grouped by domain.

    The columns are the benchmark, the size, the best repetition, the median,
    the relative spread, and the documented complexity. A skipped or failed
    benchmark keeps its row so that the report is a complete inventory.
    """
    if not results:
        return "no benchmarks matched the filters"

    lines: List[str] = []
    name_width = max(len(r.name) for r in results) + 2
    size_width = max((len(_format_size(r.size)) for r in results), default=4) + 2

    for group in dict.fromkeys(r.group for r in results):
        rows = [r for r in results if r.group == group]
        lines.append("")
        lines.append(group)
        lines.append("-" * len(group))
        header = (
            "benchmark".ljust(name_width)
            + "size".rjust(size_width)
            + "best".rjust(12)
            + "median".rjust(12)
            + "spread".rjust(9)
            + "  complexity"
        )
        lines.append(header)
        for row in rows:
            if row.status != "ok":
                lines.append(
                    row.name.ljust(name_width)
                    + _format_size(row.size).rjust(size_width)
                    + f"  {row.status}: {row.message}"
                )
                continue
            spread = "-" if row.spread != row.spread else f"{row.spread:7.1%}"
            warning = "" if row.reliable else "  (below the reliable minimum)"
            lines.append(
                row.name.ljust(name_width)
                + _format_size(row.size).rjust(size_width)
                + _format_seconds(row.best).rjust(12)
                + _format_seconds(row.median).rjust(12)
                + spread.rjust(9)
                + "  "
                + row.complexity
                + warning
            )
    return "\n".join(lines)


def format_growth(results: Sequence[BenchmarkResult]) -> str:
    """Return the growth ratios for every benchmark with several sizes.

    This is the most useful part of the report. The ratio of consecutive
    measurements tells you the growth rate, and a growth rate survives a
    noisy machine in a way an absolute time does not. A routine documented as
    linear should roughly double when its input doubles; one documented as
    logarithmic should barely move.
    """
    by_name: Dict[Tuple[str, str], List[BenchmarkResult]] = {}
    for row in results:
        if row.status != "ok" or row.size is None:
            continue
        by_name.setdefault((row.group, row.name), []).append(row)

    interesting = {key: rows for key, rows in by_name.items() if len(rows) > 1}
    if not interesting:
        return "no benchmark produced more than one size"

    lines = ["", "growth", "------"]
    for (group, name), rows in interesting.items():
        ordered = sorted(
            rows, key=lambda row: row.size if isinstance(row.size, int) else 0
        )
        complexity = ordered[0].complexity or "not documented"
        lines.append(f"{group}.{name}  ({complexity})")
        previous: Optional[BenchmarkResult] = None
        for row in ordered:
            if previous is None or previous.best <= 0:
                ratio = ""
            else:
                size_ratio = (
                    row.size / previous.size
                    if isinstance(row.size, int) and isinstance(previous.size, int)
                    and previous.size
                    else float("nan")
                )
                time_ratio = row.best / previous.best
                exponent = (
                    math.log(time_ratio) / math.log(size_ratio)
                    if size_ratio and size_ratio > 1 and time_ratio > 0
                    else float("nan")
                )
                ratio = f"  time x{time_ratio:5.2f}  implied exponent {exponent:5.2f}"
            lines.append(
                "    "
                + _format_size(row.size).rjust(12)
                + _format_seconds(row.best).rjust(12)
                + ratio
            )
            previous = row
    return "\n".join(lines)


def environment() -> Dict[str, Any]:
    """Return the machine and interpreter details that a result depends on.

    A measurement without its machine is not comparable with anything, so
    this is recorded alongside every result set.
    """
    return {
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "processor": platform.processor() or "unknown",
        "machine": platform.machine(),
        "system": platform.system(),
        "gc_enabled_by_default": gc.isenabled(),
        "recursion_limit": sys.getrecursionlimit(),
        "base_seed": BASE_SEED,
    }


def results_to_json(
    results: Sequence[BenchmarkResult],
    indent: int = 2,
) -> str:
    """Return the results and the environment as a JSON document.

    The keys are sorted, so two runs on the same machine produce files that
    differ only where the measurements differ, which is what makes the
    comparison in the pipeline readable.
    """
    payload = {
        "schema": 1,
        "environment": environment(),
        "results": [row.to_dict() for row in results],
    }
    return json.dumps(payload, indent=indent, sort_keys=True, default=str)


def results_from_json(text: str) -> List[BenchmarkResult]:
    """Rebuild a result list from the output of :func:`results_to_json`."""
    document = json.loads(text or "{}")
    rows = document.get("results", document if isinstance(document, list) else [])
    return [BenchmarkResult.from_dict(row) for row in rows if isinstance(row, dict)]


def compare_results(
    baseline: Sequence[BenchmarkResult],
    current: Sequence[BenchmarkResult],
) -> List[Tuple[str, Any, float, float, float]]:
    """Return the benchmarks present in both runs, with their ratios.

    Args:
        baseline: The earlier run.
        current: The later run.

    Returns:
        Tuples of the qualified name, the size, the baseline best, the
        current best, and the ratio of the two.
    """
    index = {
        (row.group, row.name, str(row.size)): row
        for row in baseline
        if row.status == "ok"
    }
    rows: List[Tuple[str, Any, float, float, float]] = []
    for row in current:
        if row.status != "ok":
            continue
        earlier = index.get((row.group, row.name, str(row.size)))
        if earlier is None or earlier.best <= 0:
            continue
        rows.append(
            (
                f"{row.group}.{row.name}",
                row.size,
                earlier.best,
                row.best,
                row.best / earlier.best,
            )
        )
    return rows


def format_comparison(
    baseline: Sequence[BenchmarkResult],
    current: Sequence[BenchmarkResult],
    threshold: float = 2.0,
) -> str:
    """Return a comparison table and a note about what it can establish.

    Only a difference of at least ``threshold`` in either direction is
    highlighted, because a shared machine cannot resolve less than that and
    highlighting noise trains a reader to ignore the report.
    """
    rows = compare_results(baseline, current)
    if not rows:
        return "no benchmark appears in both runs"

    width = max(len(name) for name, _, _, _, _ in rows) + 2
    lines = [
        "",
        "comparison",
        "----------",
        "benchmark".ljust(width)
        + "size".rjust(12)
        + "baseline".rjust(12)
        + "current".rjust(12)
        + "ratio".rjust(9),
    ]
    notable: List[Tuple[str, Any, float]] = []
    for name, size, before, after, ratio in rows:
        lines.append(
            name.ljust(width)
            + _format_size(size).rjust(12)
            + _format_seconds(before).rjust(12)
            + _format_seconds(after).rjust(12)
            + f"{ratio:8.2f}"
        )
        if ratio >= threshold or ratio <= 1 / threshold:
            notable.append((name, size, ratio))

    lines.append("")
    if notable:
        lines.append(f"differences of at least a factor of {threshold:g}:")
        for name, size, ratio in notable:
            direction = "slower" if ratio > 1 else "faster"
            lines.append(
                f"  {name} at {_format_size(size)}: {ratio:.2f} times {direction}"
            )
    else:
        lines.append(f"no difference of a factor of {threshold:g} or more")
    lines.append("")
    lines.append(
        "A shared machine cannot resolve a few percent. Treat anything "
        "smaller as noise,"
    )
    lines.append(
        "and confirm a real change with a local measurement on a quiet machine."
    )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------

#: The benchmark modules, in the order the domains are taught, which is the
#: order the report presents them in.
BENCHMARK_MODULES = (
    "bench_sets",
    "bench_logic",
    "bench_sat",
    "bench_combinatorics",
    "bench_graphs",
    "bench_number_theory",
    "bench_algebra",
)


def discover() -> List[str]:
    """Import every benchmark module, which registers its benchmarks.

    Returns:
        The modules that imported successfully. A module that fails to import
        is reported on standard error and skipped, because one broken
        benchmark file should not prevent the rest of the suite from running.
    """
    imported: List[str] = []
    for name in BENCHMARK_MODULES:
        try:
            import_module(f"{__name__}.{name}")
            imported.append(name)
        except Exception as error:  # noqa: BLE001
            print(
                f"could not import {name}: {type(error).__name__}: {error}",
                file=sys.stderr,
            )
    return imported
