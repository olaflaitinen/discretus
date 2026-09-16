# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Command line entry point for the discretus benchmark suite.

This module is what ``python -m benchmarks`` runs. It parses the arguments,
discovers and filters the benchmarks, measures them, and writes the report in
whichever formats were requested.

The interface is designed for three callers, and each one wants something
different from the same run.

    A contributor investigating a routine wants the table and the growth
    ratios on the terminal, filtered to the routine in question, and wants to
    be able to raise the repetition count until the numbers settle.

    The continuous integration pipeline wants a machine readable file that it
    can archive and later compare, and wants an exit status it can act on.

    A reviewer reading a pull request wants the comparison against an earlier
    run, rendered compactly, with a clear statement of what the comparison
    can and cannot establish.

Exit status:

    0   Every selected benchmark ran, or was skipped because the routine it
        measures is not available in this build.
    1   At least one benchmark raised.
    2   The arguments were invalid, or a file could not be read.
    3   A regression threshold was exceeded and the run was asked to enforce
        it with the fail on regression option.

Examples:

    python -m benchmarks
    python -m benchmarks --list
    python -m benchmarks --group graphs --group sets
    python -m benchmarks --filter dijkstra --repeats 15
    python -m benchmarks --quick --json results.json
    python -m benchmarks --compare baseline.json --threshold 1.5
    python -m benchmarks --json new.json --markdown summary.md
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
from typing import List, Optional, Sequence

from . import (
    DEFAULT_REPEATS,
    DEFAULT_WARMUP,
    QUICK_SIZE_LIMIT,
    REGISTRY,
    BenchmarkResult,
    compare_results,
    discover,
    environment,
    format_comparison,
    format_growth,
    format_results,
    group_names,
    results_from_json,
    results_to_json,
    run_all,
)

__all__ = ["build_parser", "main"]

#: The exit codes the module returns, named so that the code reads.
EXIT_OK = 0
EXIT_BENCHMARK_ERROR = 1
EXIT_USAGE_ERROR = 2
EXIT_REGRESSION = 3


def build_parser() -> argparse.ArgumentParser:
    """Return the argument parser, with every option documented.

    The help text is the primary documentation of this interface, so it is
    written to be read rather than skimmed.
    """
    parser = argparse.ArgumentParser(
        prog="python -m benchmarks",
        description=(
            "Measure the discretus benchmark suite. The reported figure is "
            "the fastest of several repetitions, because for a deterministic "
            "computation the variation between repetitions is noise from the "
            "machine."
        ),
        epilog=(
            "A shared machine cannot resolve a few percent. Use the growth "
            "ratios rather than the absolute times when deciding whether "
            "something changed, and confirm a real change on a quiet machine."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    selection = parser.add_argument_group("selecting what to run")
    selection.add_argument(
        "--group",
        action="append",
        dest="groups",
        metavar="NAME",
        help=(
            "Only run this group. May be repeated. Use --list-groups to see "
            "the declared groups."
        ),
    )
    selection.add_argument(
        "--filter",
        dest="pattern",
        metavar="TEXT",
        help=(
            "Only run benchmarks whose qualified name contains this text, "
            "compared case insensitively."
        ),
    )
    selection.add_argument(
        "--quick",
        action="store_true",
        help=(
            f"Skip sizes above {QUICK_SIZE_LIMIT:,}. Suitable for a pull "
            "request, where the question is whether anything changed by a "
            "large factor rather than what the growth rate is."
        ),
    )

    measurement = parser.add_argument_group("measurement")
    measurement.add_argument(
        "--repeats",
        type=int,
        default=None,
        metavar="N",
        help=(
            f"Timed repetitions per measurement, overriding each benchmark's "
            f"own setting. The default is {DEFAULT_REPEATS}. Raise it until "
            "the reported spread stops moving."
        ),
    )
    measurement.add_argument(
        "--warmup",
        type=int,
        default=None,
        metavar="N",
        help=(
            f"Untimed repetitions before the timed ones. The default is "
            f"{DEFAULT_WARMUP}. Raise it when a routine memoizes and the "
            "first call is not representative."
        ),
    )

    output = parser.add_argument_group("output")
    output.add_argument(
        "--json",
        dest="json_path",
        metavar="PATH",
        help=(
            "Write the results and the environment as JSON. The keys are "
            "sorted, so two runs on the same machine produce files that "
            "differ only where the measurements differ."
        ),
    )
    output.add_argument(
        "--markdown",
        dest="markdown_path",
        metavar="PATH",
        help="Write a compact summary as Markdown, for a pull request comment.",
    )
    output.add_argument(
        "--no-table",
        action="store_true",
        help="Suppress the per benchmark table.",
    )
    output.add_argument(
        "--no-growth",
        action="store_true",
        help="Suppress the growth ratio report.",
    )
    output.add_argument(
        "--quiet",
        action="store_true",
        help="Do not report progress while running.",
    )

    comparison = parser.add_argument_group("comparison")
    comparison.add_argument(
        "--compare",
        dest="baseline_path",
        metavar="PATH",
        help="Compare this run against an earlier JSON result file.",
    )
    comparison.add_argument(
        "--threshold",
        type=float,
        default=2.0,
        metavar="FACTOR",
        help=(
            "Highlight a difference of at least this factor in either "
            "direction. The default is 2.0, which is roughly the resolution "
            "of a shared machine."
        ),
    )
    comparison.add_argument(
        "--fail-on-regression",
        action="store_true",
        help=(
            "Exit with status 3 when a benchmark is slower than the baseline "
            "by at least the threshold. Off by default, because a shared "
            "machine produces false positives."
        ),
    )

    inspection = parser.add_argument_group("inspection")
    inspection.add_argument(
        "--list",
        action="store_true",
        help="List the benchmarks that would run, and exit.",
    )
    inspection.add_argument(
        "--list-groups",
        action="store_true",
        help="List the declared groups, and exit.",
    )
    inspection.add_argument(
        "--environment",
        action="store_true",
        help="Print the machine and interpreter details, and exit.",
    )

    return parser


def _apply_overrides(repeats: Optional[int], warmup: Optional[int]) -> None:
    """Replace the registry entries with copies carrying the overrides.

    A benchmark declares its own repetition count, because a slow benchmark
    should not be repeated as often as a fast one. The command line can
    override both, which is what a contributor investigating a routine wants,
    and the override is applied by rebuilding the registry rather than by
    mutating the frozen entries.
    """
    if repeats is None and warmup is None:
        return
    from dataclasses import replace

    updated = []
    for item in REGISTRY:
        changes = {}
        if repeats is not None:
            changes["repeats"] = max(1, repeats)
        if warmup is not None:
            changes["warmup"] = max(0, warmup)
        updated.append(replace(item, **changes))
    REGISTRY[:] = updated


def _selected(groups: Optional[Sequence[str]], pattern: Optional[str]) -> List:
    """Return the registry entries matching the filters."""
    wanted = set(groups) if groups else None
    chosen = []
    for item in REGISTRY:
        if wanted is not None and item.group not in wanted:
            continue
        if pattern and pattern.lower() not in item.qualified_name.lower():
            continue
        chosen.append(item)
    return chosen


def _print_listing(groups: Optional[Sequence[str]], pattern: Optional[str]) -> int:
    """Print the benchmarks that would run, with their sizes and status."""
    chosen = _selected(groups, pattern)
    if not chosen:
        print("no benchmarks matched the filters")
        return EXIT_OK

    width = max(len(item.qualified_name) for item in chosen) + 2
    print("benchmark".ljust(width) + "status".ljust(12) + "sizes")
    print("-" * (width + 12 + 40))
    for item in chosen:
        status = "available" if item.requires is not None else "unavailable"
        sizes = ", ".join(
            "default" if size is None else f"{size:,}" if isinstance(size, int) else str(size)
            for size in item.sizes
        )
        print(item.qualified_name.ljust(width) + status.ljust(12) + sizes)
        if item.complexity:
            print(" " * width + f"            documented as {item.complexity}")

    available = sum(1 for item in chosen if item.requires is not None)
    measurements = sum(
        len(item.sizes) for item in chosen if item.requires is not None
    )
    print()
    print(
        f"{len(chosen)} benchmarks, {available} available, "
        f"{measurements} measurements"
    )
    return EXIT_OK


def _write_markdown(
    path: str,
    results: Sequence[BenchmarkResult],
    baseline: Optional[Sequence[BenchmarkResult]],
    threshold: float,
) -> None:
    """Write a compact Markdown summary, suitable for a review comment.

    The summary leads with what the numbers can establish, because a table of
    times without that caveat invites a reader to act on noise.
    """
    lines: List[str] = ["# Benchmark summary", ""]

    details = environment()
    lines.append(
        f"Measured on {details['python_implementation']} "
        f"{details['python_version']}, {details['platform']}."
    )
    lines.append("")
    lines.append(
        "The reported figure is the fastest of several repetitions. A shared "
        "machine cannot resolve a few percent, so only a difference of at "
        f"least a factor of {threshold:g} is highlighted below."
    )
    lines.append("")

    measured = [row for row in results if row.status == "ok"]
    skipped = [row for row in results if row.status == "skipped"]
    failed = [row for row in results if row.status == "error"]

    lines.append(
        f"Ran {len(measured)} measurements, skipped {len(skipped)}, "
        f"failed {len(failed)}."
    )
    lines.append("")

    if failed:
        lines.append("## Failures")
        lines.append("")
        for row in failed:
            lines.append(f"- `{row.group}.{row.name}` at {row.size}: {row.message}")
        lines.append("")

    if baseline:
        rows = compare_results(baseline, results)
        notable = [
            (name, size, ratio)
            for name, size, _, _, ratio in rows
            if ratio >= threshold or ratio <= 1 / threshold
        ]
        lines.append("## Against the baseline")
        lines.append("")
        if notable:
            lines.append("| benchmark | size | ratio | direction |")
            lines.append("| --- | --- | --- | --- |")
            for name, size, ratio in notable:
                direction = "slower" if ratio > 1 else "faster"
                lines.append(f"| `{name}` | {size} | {ratio:.2f} | {direction} |")
        else:
            lines.append(
                f"No benchmark differs by a factor of {threshold:g} or more."
            )
        lines.append("")

    if measured:
        lines.append("## Measurements")
        lines.append("")
        lines.append("| benchmark | size | best | complexity |")
        lines.append("| --- | --- | --- | --- |")
        for row in measured:
            lines.append(
                f"| `{row.group}.{row.name}` | {row.size} | "
                f"{row.best * 1e3:.3f} ms | {row.complexity or 'not documented'} |"
            )
        lines.append("")

    pathlib.Path(path).write_text("\n".join(lines), encoding="utf-8")


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Run the suite and return the process exit status.

    Args:
        argv: The arguments, excluding the program name. Defaults to the
            process arguments.

    Returns:
        One of the exit codes documented in the module docstring.
    """
    parser = build_parser()
    arguments = parser.parse_args(argv)

    if arguments.environment:
        print(json.dumps(environment(), indent=2, sort_keys=True))
        return EXIT_OK

    imported = discover()
    if not imported:
        print("no benchmark module could be imported", file=sys.stderr)
        return EXIT_USAGE_ERROR

    if arguments.list_groups:
        for name in group_names():
            count = sum(1 for item in REGISTRY if item.group == name)
            available = sum(
                1
                for item in REGISTRY
                if item.group == name and item.requires is not None
            )
            print(f"{name}  ({available} of {count} available)")
        return EXIT_OK

    if arguments.groups:
        declared = set(group_names())
        unknown = sorted(set(arguments.groups) - declared)
        if unknown:
            print(
                f"unknown group: {', '.join(unknown)}. "
                f"Declared groups are: {', '.join(sorted(declared))}",
                file=sys.stderr,
            )
            return EXIT_USAGE_ERROR

    _apply_overrides(arguments.repeats, arguments.warmup)

    if arguments.list:
        return _print_listing(arguments.groups, arguments.pattern)

    baseline: Optional[List[BenchmarkResult]] = None
    if arguments.baseline_path:
        try:
            text = pathlib.Path(arguments.baseline_path).read_text(encoding="utf-8")
        except OSError as error:
            print(f"could not read the baseline: {error}", file=sys.stderr)
            return EXIT_USAGE_ERROR
        try:
            baseline = results_from_json(text)
        except json.JSONDecodeError as error:
            print(f"the baseline is not valid JSON: {error}", file=sys.stderr)
            return EXIT_USAGE_ERROR
        print(
            f"loaded {len(baseline)} baseline measurements from "
            f"{arguments.baseline_path}",
            file=sys.stderr,
        )

    results = run_all(
        groups=arguments.groups,
        pattern=arguments.pattern,
        quick=arguments.quick,
        progress=not arguments.quiet,
    )

    if not results:
        print("no benchmarks matched the filters", file=sys.stderr)
        return EXIT_USAGE_ERROR

    if not arguments.no_table:
        print(format_results(results))
    if not arguments.no_growth:
        print(format_growth(results))

    measured = [row for row in results if row.status == "ok"]
    skipped = [row for row in results if row.status == "skipped"]
    failed = [row for row in results if row.status == "error"]
    unreliable = [row for row in measured if not row.reliable]

    print("")
    print("summary")
    print("-------")
    print(f"measured:   {len(measured)}")
    print(f"skipped:    {len(skipped)}")
    print(f"failed:     {len(failed)}")
    if unreliable:
        print(
            f"unreliable: {len(unreliable)} measurement(s) were too short to "
            "be meaningful; raise the size or the repetition count"
        )
    if skipped:
        groups_skipped = sorted({row.group for row in skipped})
        print(
            "skipped groups: "
            + ", ".join(groups_skipped)
            + " (the routines are not available in this build)"
        )
    for row in failed:
        print(f"  error in {row.group}.{row.name} at {row.size}: {row.message}")

    regression = False
    if baseline is not None:
        print(format_comparison(baseline, results, threshold=arguments.threshold))
        for _, _, _, _, ratio in compare_results(baseline, results):
            if ratio >= arguments.threshold:
                regression = True

    if arguments.json_path:
        try:
            pathlib.Path(arguments.json_path).write_text(
                results_to_json(results), encoding="utf-8"
            )
        except OSError as error:
            print(f"could not write the results: {error}", file=sys.stderr)
            return EXIT_USAGE_ERROR
        print(f"wrote {arguments.json_path}")

    if arguments.markdown_path:
        try:
            _write_markdown(
                arguments.markdown_path, results, baseline, arguments.threshold
            )
        except OSError as error:
            print(f"could not write the summary: {error}", file=sys.stderr)
            return EXIT_USAGE_ERROR
        print(f"wrote {arguments.markdown_path}")

    if failed:
        return EXIT_BENCHMARK_ERROR
    if regression and arguments.fail_on_regression:
        return EXIT_REGRESSION
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
