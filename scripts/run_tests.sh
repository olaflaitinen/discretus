#!/usr/bin/env bash
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Run the test suite the way the pipeline runs it.
#
# Why this script exists
# ======================
#
# The test job of the continuous integration workflow does not run one
# command. It runs the suite, then the property based tests with a fixed
# seed, then the tests marked slow on one interpreter only, then the
# docstring examples, and then the same suite again under coverage with a
# minimum percentage. Each of those has an option that matters and that is
# easy to get wrong by hand, and a contributor who runs a bare invocation
# gets a weaker check than the pipeline and finds out later.
#
# This script is the single local entry point for all of it. The defaults
# reproduce what the pipeline does on a pull request, and every stage can be
# selected on its own while investigating one failure.
#
# What it can run
# ===============
#
#   suite         the whole test suite, with strict marker checking
#   property      the property based tests, with the seed pinned
#   slow          the tests marked slow, which the fast path excludes
#   optional      the tests that need an optional dependency
#   doctests      the docstring examples of the library
#   coverage      the suite again, measured, against a minimum percentage
#
# The default is the suite, the docstring examples, and the property based
# tests, which is the combination that catches the most for the least time.
# The slow and optional stages and the coverage measurement are opt in.
#
# Usage
# =====
#
#   scripts/run_tests.sh                     the default combination
#   scripts/run_tests.sh --all               every stage, including slow
#   scripts/run_tests.sh --only suite        one stage
#   scripts/run_tests.sh --coverage          add the measured run
#   scripts/run_tests.sh --coverage --html   and write the browsable report
#   scripts/run_tests.sh --fast              the suite alone, no doctests
#   scripts/run_tests.sh -k dijkstra         pass an expression to pytest
#   scripts/run_tests.sh --matrix            repeat on every interpreter
#   scripts/run_tests.sh -- -x --pdb         pass the rest through verbatim
#
# Exit status
# ===========
#
#   0   every stage that ran passed
#   1   at least one stage failed
#   2   the command line was wrong
#   5   nothing was collected and --require-tests was given
#
# The empty collection case has its own status because the library is built
# out package by package: a package whose tests are not written yet collects
# nothing, and that is expected during development and unacceptable in a
# release, so the two are distinguished rather than conflated.

set -euo pipefail

# ---------------------------------------------------------------------------
# Location
# ---------------------------------------------------------------------------

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" > /dev/null 2>&1 && pwd)"
REPOSITORY_ROOT="$(cd -- "${SCRIPT_DIR}/.." > /dev/null 2>&1 && pwd)"
cd -- "${REPOSITORY_ROOT}"

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# The interpreter under test. Overridable, which is how --matrix works and
# how a contributor checks one interpreter without activating anything.
PYTHON="${PYTHON:-python3}"

# Where the tests live. Declared here as well as in pytest.ini, because this
# script passes it explicitly: an invocation without a path picks up whatever
# the working directory happens to contain, and that has surprised people.
TEST_PATH="tests"

# The package under measurement, and the minimum percentage the measured run
# must reach. The percentage matches the one the coverage job enforces and
# the target recorded in codecov.yml, and it is a floor rather than a goal.
COVERAGE_TARGET="discretus"
COVERAGE_MINIMUM="${COVERAGE_MINIMUM:-90}"

# The seed for the property based tests. A fixed seed is what makes a failure
# reproducible; the pipeline pins it for the same reason, and a contributor
# who wants to search for new counterexamples passes --random-seed instead.
HYPOTHESIS_SEED="${HYPOTHESIS_SEED:-0}"

# The interpreters --matrix tries, in the order the support policy lists
# them. One that is not installed is reported and skipped rather than
# treated as a failure, because no laptop has all of them.
MATRIX_INTERPRETERS=(
    python3.9
    python3.10
    python3.11
    python3.12
    python3.13
    pypy3.10
)

# The stages, in the order they run. Ordered so that a plain failure is
# reported before a measured one, because the measured run is slower and a
# contributor who has broken something wants to know immediately.
ALL_STAGES=(suite doctests property slow optional coverage)

# What runs when no selection is given.
DEFAULT_STAGES=(suite doctests property)

# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

USE_COLOR=1
if [[ ! -t 1 ]] || [[ -n "${NO_COLOR:-}" ]]; then
    USE_COLOR=0
fi

BOLD=""
RED=""
GREEN=""
YELLOW=""
RESET=""

configure_color() {
    if [[ "${USE_COLOR}" -eq 1 ]]; then
        BOLD=$'\033[1m'
        RED=$'\033[31m'
        GREEN=$'\033[32m'
        YELLOW=$'\033[33m'
        RESET=$'\033[0m'
    else
        BOLD=""
        RED=""
        GREEN=""
        YELLOW=""
        RESET=""
    fi
}

heading() {
    printf '\n%s%s%s\n' "${BOLD}" "$1" "${RESET}"
}

note() {
    printf '%s\n' "$1"
}

warn() {
    printf '%swarning:%s %s\n' "${YELLOW}" "${RESET}" "$1" >&2
}

fatal() {
    printf '%serror:%s %s\n' "${RED}" "${RESET}" "$1" >&2
    exit 2
}

# ---------------------------------------------------------------------------
# Bookkeeping
# ---------------------------------------------------------------------------

PASSED=()
FAILED=()
EMPTY=()

# Interpreters the matrix mode found but could not use, kept apart from the
# empty collections because the remedy is different: one needs a test stack
# installed, the other needs tests written.
UNAVAILABLE=()

# The status pytest returns when it collected nothing. Treated as its own
# outcome rather than as a failure, for the reason given in the header.
NO_TESTS_STATUS=5

SELECTED=""
EXTRA_STAGES=""
FAST=0
WITH_HTML=0
WITH_XML=0
REQUIRE_TESTS=0
MATRIX=0
VERBOSE=0
DURATIONS=10
KEYWORD=""
MARKER=""
PASSTHROUGH=()

# ---------------------------------------------------------------------------
# Preconditions
# ---------------------------------------------------------------------------

python_module_available() {
    local module="$1"
    "${PYTHON}" -c "import importlib.util, sys; sys.exit(0 if importlib.util.find_spec('${module}') else 1)" \
        > /dev/null 2>&1
}

require_python() {
    if ! command -v -- "${PYTHON}" > /dev/null 2>&1; then
        fatal "the interpreter ${PYTHON} was not found"
    fi
}

require_pytest() {
    if ! python_module_available pytest; then
        printf 'pytest is not installed for %s.\n' "${PYTHON}" >&2
        printf 'Install the development extra:\n' >&2
        printf '  %s -m pip install -e ".[dev]"\n' "${PYTHON}" >&2
        exit 2
    fi
}

# Report whether the library imports at all before running anything. A
# failure here would otherwise appear as a collection error in every test
# file at once, which buries the one message that matters.
check_import() {
    if ! "${PYTHON}" -c "import discretus; print('discretus', discretus.__version__)"; then
        fatal "the library does not import, so no stage can be meaningful"
    fi
}

# ---------------------------------------------------------------------------
# Stage machinery
# ---------------------------------------------------------------------------

# Record the outcome of one stage from the status its command returned.
record_status() {
    local name="$1"
    local status="$2"
    if [[ "${status}" -eq 0 ]]; then
        PASSED+=("${name}")
        printf '%spass%s  %s\n' "${GREEN}" "${RESET}" "${name}"
    elif [[ "${status}" -eq "${NO_TESTS_STATUS}" ]]; then
        EMPTY+=("${name}")
        printf '%sempty%s %s (nothing was collected)\n' "${YELLOW}" "${RESET}" "${name}"
    else
        FAILED+=("${name}")
        printf '%sfail%s  %s (status %s)\n' "${RED}" "${RESET}" "${name}" "${status}"
    fi
}

# Render a command line so that it can be copied and pasted. An argument
# containing whitespace is quoted, which matters for the marker expressions:
# an unquoted one reads as several arguments and selects something else.
quote_command() {
    local argument
    local rendered=""
    for argument in "$@"; do
        if [[ "${argument}" == *[[:space:]]* ]]; then
            rendered+=" '${argument}'"
        else
            rendered+=" ${argument}"
        fi
    done
    printf '%s\n' "${rendered# }"
}

# Print a command before running it, so that a contributor can copy it and
# investigate one stage by hand without reading this script.
run_stage() {
    local name="$1"
    shift
    quote_command "$@"
    local status=0
    "$@" || status="$?"
    record_status "${name}" "${status}"
}

# The options every invocation shares. Strict marker checking turns a typed
# marker into an error rather than a silent selection of nothing, which is
# the single most common way a marked test stops running unnoticed.
common_pytest_options() {
    local options=(--strict-markers)
    if [[ "${VERBOSE}" -eq 1 ]]; then
        options+=(-v)
    fi
    if [[ "${DURATIONS}" -gt 0 ]]; then
        options+=("--durations=${DURATIONS}")
    fi
    if [[ -n "${KEYWORD}" ]]; then
        options+=(-k "${KEYWORD}")
    fi
    if [[ "${#PASSTHROUGH[@]}" -gt 0 ]]; then
        options+=("${PASSTHROUGH[@]}")
    fi
    printf '%s\n' "${options[@]}"
}

# Read the shared options into an array. A function cannot return an array,
# so the lines it prints are read back, which also keeps a value containing
# whitespace intact.
read_common_options() {
    local -n target="$1"
    target=()
    local line
    while IFS= read -r line; do
        target+=("${line}")
    done < <(common_pytest_options)
}

# ---------------------------------------------------------------------------
# The stages
# ---------------------------------------------------------------------------

stage_suite() {
    # The whole suite, excluding the two opt in marks. Deselecting rather
    # than relying on a default keeps the marks meaningful: a test marked
    # slow is still collected, still counted, and still runnable by name.
    local options=()
    read_common_options options
    local selection="not slow and not optional"
    if [[ -n "${MARKER}" ]]; then
        selection="${MARKER}"
    fi
    run_stage suite \
        "${PYTHON}" -m pytest "${TEST_PATH}" "${options[@]}" -m "${selection}"
}

stage_slow() {
    # The tests the suite stage leaves out. The pipeline runs these on one
    # interpreter and one operating system only, because their cost is in
    # the algorithm rather than in the platform.
    local options=()
    read_common_options options
    run_stage slow \
        "${PYTHON}" -m pytest "${TEST_PATH}" "${options[@]}" -m slow
}

stage_optional() {
    # The tests that need an optional dependency. They are skipped rather
    # than failed when the dependency is absent, so the stage is reported as
    # passing on a minimal install, which is correct: nothing is broken.
    local options=()
    read_common_options options
    if ! python_module_available matplotlib; then
        note "matplotlib is absent, so the rendering tests will skip themselves"
    fi
    run_stage optional \
        "${PYTHON}" -m pytest "${TEST_PATH}" "${options[@]}" -m optional
}

stage_property() {
    # The property based tests, which assert the algebraic laws rather than
    # individual results. The seed is pinned so that a failure is
    # reproducible; without that, a counterexample found here is a story
    # rather than a bug report.
    if ! python_module_available hypothesis; then
        note "hypothesis is not installed, so the property stage is skipped"
        return 0
    fi
    local options=()
    read_common_options options
    run_stage property \
        "${PYTHON}" -m pytest "${TEST_PATH}" "${options[@]}" \
        -m property "--hypothesis-seed=${HYPOTHESIS_SEED}"
}

stage_doctests() {
    # The docstring examples of the library. They are executed because an
    # example that is never executed is a comment that looks like a
    # guarantee, and because the reference is generated from the same text.
    #
    # A file of zero length is skipped, which is how the placeholders for
    # the packages that are not written yet are passed over.
    local status=0
    printf '%s\n' "${PYTHON} - (doctest over discretus)"
    "${PYTHON}" - <<'PYDOCTEST' || status="$?"
import doctest
import importlib
import pathlib
import sys

attempted = 0
failed = 0
modules = 0
for path in sorted(pathlib.Path("discretus").rglob("*.py")):
    if "__pycache__" in path.parts or path.stat().st_size == 0:
        continue
    name = str(path.with_suffix("")).replace("/", ".")
    if name.endswith(".__init__"):
        name = name[: -len(".__init__")]
    try:
        module = importlib.import_module(name)
    except Exception as error:
        print(f"could not import {name}: {type(error).__name__}: {error}")
        failed += 1
        continue
    result = doctest.testmod(module, verbose=False)
    modules += 1
    attempted += result.attempted
    failed += result.failed

print(f"{modules} modules, {attempted} docstring examples, {failed} failed")
sys.exit(1 if failed else 0)
PYDOCTEST
    record_status doctests "${status}"
}

stage_coverage() {
    # The suite again, measured. The minimum is enforced here rather than
    # only in the pipeline, so that a change that drops coverage is visible
    # before it is pushed.
    if ! python_module_available pytest_cov; then
        note "pytest-cov is not installed, so the coverage stage is skipped"
        return 0
    fi
    # Find out whether anything would be collected before measuring. The
    # minimum percentage would otherwise fail on an empty collection, and
    # report a coverage shortfall for a suite that does not exist yet, which
    # is a misleading way to say that no test was written.
    local collected=0
    "${PYTHON}" -m pytest "${TEST_PATH}" --collect-only -q > /dev/null 2>&1 \
        || collected="$?"
    if [[ "${collected}" -eq "${NO_TESTS_STATUS}" ]]; then
        record_status coverage "${NO_TESTS_STATUS}"
        return 0
    fi

    local options=()
    read_common_options options
    local reports=(--cov-report=term-missing)
    if [[ "${WITH_HTML}" -eq 1 ]]; then
        reports+=(--cov-report=html)
    fi
    if [[ "${WITH_XML}" -eq 1 ]]; then
        reports+=(--cov-report=xml)
    fi
    run_stage coverage \
        "${PYTHON}" -m pytest "${TEST_PATH}" "${options[@]}" \
        "--cov=${COVERAGE_TARGET}" "${reports[@]}" \
        "--cov-fail-under=${COVERAGE_MINIMUM}"

    if [[ "${WITH_HTML}" -eq 1 ]] && [[ -f htmlcov/index.html ]]; then
        note "the browsable report is at htmlcov/index.html"
    fi
}

# ---------------------------------------------------------------------------
# The interpreter matrix
# ---------------------------------------------------------------------------

# Repeat the selected stages on every interpreter that is installed. This is
# the local approximation of the test job's matrix, and it is approximate on
# purpose: it runs them one after another rather than in parallel, because
# the point is to find a version dependent failure, not to be fast.
run_matrix() {
    local interpreter
    local available=()
    for interpreter in "${MATRIX_INTERPRETERS[@]}"; do
        if command -v -- "${interpreter}" > /dev/null 2>&1; then
            available+=("${interpreter}")
        else
            note "${interpreter} is not installed"
        fi
    done

    if [[ "${#available[@]}" -eq 0 ]]; then
        fatal "no interpreter from the matrix is installed"
    fi

    heading "Running on ${#available[@]} interpreters"
    local status=0
    local child=0
    for interpreter in "${available[@]}"; do
        heading "${interpreter}"
        child=0
        PYTHON="${interpreter}" MATRIX_DEPTH=1 "${BASH_SOURCE[0]}" \
            "${FORWARDED_ARGUMENTS[@]}" || child="$?"
        case "${child}" in
            0)
                PASSED+=("${interpreter}")
                ;;
            2)
                # The interpreter exists but cannot run the suite, almost
                # always because the test stack is not installed for it.
                # That is a missing environment rather than a failing test,
                # so it is reported and does not fail the run.
                UNAVAILABLE+=("${interpreter}")
                ;;
            *)
                status=1
                FAILED+=("${interpreter}")
                ;;
        esac
    done
    return "${status}"
}

# ---------------------------------------------------------------------------
# Command line
# ---------------------------------------------------------------------------

usage() {
    cat <<'USAGE'
Run the test suite the way the pipeline runs it.

Usage:
  scripts/run_tests.sh [options] [-- pytest arguments]

Stage selection:
  --only NAMES       run only these stages, comma separated
  --with NAMES       add these stages to the default combination
  --all              run every stage, including the slow and optional ones
  --fast             the suite alone, without the docstring examples
  --coverage         add the measured run with the minimum enforced
  --list             print the stage names in the order they run

Stage options:
  --html             also write the browsable coverage report
  --xml              also write the machine readable coverage report
  --min N            the minimum coverage percentage, default 90
  --seed N           the property test seed, default 0
  --random-seed      draw a new property test seed, to search for new cases
  --require-tests    an empty collection is a failure rather than a note

pytest options:
  -k EXPR            select by expression
  -m MARK            override the marker expression of the suite stage
  -v                 verbose output
  --durations N      report the N slowest tests, default 10, 0 to disable
  --                 pass every remaining argument to pytest verbatim

Other:
  --matrix           repeat the selection on every installed interpreter
  --no-color         plain output, for a log file or a pipe
  -h, --help         print this text

Stages:
  suite doctests property slow optional coverage

Examples:
  scripts/run_tests.sh
  scripts/run_tests.sh --all --coverage --html
  scripts/run_tests.sh --only suite -k "graph and not slow"
  scripts/run_tests.sh --only property --random-seed
  scripts/run_tests.sh -- -x --pdb
USAGE
}

# Kept so that --matrix can hand the same arguments to each interpreter.
FORWARDED_ARGUMENTS=()

parse_arguments() {
    FORWARDED_ARGUMENTS=("$@")
    while [[ "$#" -gt 0 ]]; do
        case "$1" in
            --only)
                [[ "$#" -ge 2 ]] || fatal "the --only option needs a value"
                SELECTED="$2"
                shift 2
                ;;
            --only=*)
                SELECTED="${1#--only=}"
                shift
                ;;
            --with)
                [[ "$#" -ge 2 ]] || fatal "the --with option needs a value"
                EXTRA_STAGES="$2"
                shift 2
                ;;
            --with=*)
                EXTRA_STAGES="${1#--with=}"
                shift
                ;;
            --all)
                SELECTED="$(
                    IFS=','
                    printf '%s' "${ALL_STAGES[*]}"
                )"
                shift
                ;;
            --fast)
                FAST=1
                shift
                ;;
            --coverage)
                EXTRA_STAGES="${EXTRA_STAGES:+${EXTRA_STAGES},}coverage"
                shift
                ;;
            --html)
                WITH_HTML=1
                shift
                ;;
            --xml)
                WITH_XML=1
                shift
                ;;
            --min)
                [[ "$#" -ge 2 ]] || fatal "the --min option needs a value"
                COVERAGE_MINIMUM="$2"
                shift 2
                ;;
            --seed)
                [[ "$#" -ge 2 ]] || fatal "the --seed option needs a value"
                HYPOTHESIS_SEED="$2"
                shift 2
                ;;
            --random-seed)
                HYPOTHESIS_SEED="random"
                shift
                ;;
            --require-tests)
                REQUIRE_TESTS=1
                shift
                ;;
            --matrix)
                MATRIX=1
                shift
                ;;
            --durations)
                [[ "$#" -ge 2 ]] || fatal "the --durations option needs a value"
                DURATIONS="$2"
                shift 2
                ;;
            -k)
                [[ "$#" -ge 2 ]] || fatal "the -k option needs a value"
                KEYWORD="$2"
                shift 2
                ;;
            -m)
                [[ "$#" -ge 2 ]] || fatal "the -m option needs a value"
                MARKER="$2"
                shift 2
                ;;
            -v | --verbose)
                VERBOSE=1
                shift
                ;;
            --no-color)
                USE_COLOR=0
                shift
                ;;
            --list)
                printf '%s\n' "${ALL_STAGES[@]}"
                exit 0
                ;;
            -h | --help)
                usage
                exit 0
                ;;
            --)
                shift
                while [[ "$#" -gt 0 ]]; do
                    PASSTHROUGH+=("$1")
                    shift
                done
                ;;
            *)
                printf 'unknown option: %s\n\n' "$1" >&2
                usage >&2
                exit 2
                ;;
        esac
    done
}

in_list() {
    local needle="$1"
    local list="$2"
    local item
    local saved_ifs="${IFS}"
    IFS=','
    for item in ${list}; do
        if [[ "${item}" == "${needle}" ]]; then
            IFS="${saved_ifs}"
            return 0
        fi
    done
    IFS="${saved_ifs}"
    return 1
}

validate_selection() {
    local list="$1"
    local label="$2"
    local item
    local known
    local found
    local saved_ifs="${IFS}"
    IFS=','
    for item in ${list}; do
        found=0
        for known in "${ALL_STAGES[@]}"; do
            if [[ "${known}" == "${item}" ]]; then
                found=1
                break
            fi
        done
        if [[ "${found}" -eq 0 ]]; then
            IFS="${saved_ifs}"
            printf 'the %s option names an unknown stage: %s\n' "${label}" "${item}" >&2
            printf 'known stages: %s\n' "${ALL_STAGES[*]}" >&2
            exit 2
        fi
    done
    IFS="${saved_ifs}"
}

# Decide the stage list from the options, in the order ALL_STAGES declares,
# so that the order does not depend on how the options were typed.
resolve_stages() {
    local requested=()
    local name

    if [[ -n "${SELECTED}" ]]; then
        validate_selection "${SELECTED}" "--only"
        for name in "${ALL_STAGES[@]}"; do
            if in_list "${name}" "${SELECTED}"; then
                requested+=("${name}")
            fi
        done
    elif [[ "${FAST}" -eq 1 ]]; then
        requested=(suite)
    else
        requested=("${DEFAULT_STAGES[@]}")
    fi

    if [[ -n "${EXTRA_STAGES}" ]]; then
        validate_selection "${EXTRA_STAGES}" "--with"
        for name in "${ALL_STAGES[@]}"; do
            if in_list "${name}" "${EXTRA_STAGES}"; then
                if ! printf '%s\n' "${requested[@]}" | grep -qx -- "${name}"; then
                    requested+=("${name}")
                fi
            fi
        done
    fi

    printf '%s\n' "${requested[@]}"
}

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

summarise() {
    heading "Summary"
    printf 'passed: %s\n' "${#PASSED[@]}"
    printf 'failed: %s\n' "${#FAILED[@]}"
    printf 'empty:  %s\n' "${#EMPTY[@]}"

    if [[ "${#UNAVAILABLE[@]}" -gt 0 ]]; then
        printf '\nnot usable: %s\n' "${UNAVAILABLE[*]}"
        printf '%s\n' \
            'These interpreters are installed but have no test stack.' \
            'Install it for each one you want in the matrix:' \
            '  <interpreter> -m pip install -e ".[dev]"'
    fi

    if [[ "${#EMPTY[@]}" -gt 0 ]]; then
        printf '\nnothing was collected for: %s\n' "${EMPTY[*]}"
        printf '%s\n' \
            'The library is built out package by package, so a package' \
            'whose tests are not written yet collects nothing. Pass' \
            '--require-tests to treat that as a failure.'
        if [[ "${REQUIRE_TESTS}" -eq 1 ]]; then
            printf '\n%san empty collection was required to be a failure%s\n' \
                "${RED}" "${RESET}"
            return "${NO_TESTS_STATUS}"
        fi
    fi

    if [[ "${#FAILED[@]}" -gt 0 ]]; then
        printf '\n%sfailing: %s%s\n' "${RED}" "${FAILED[*]}" "${RESET}"
        printf 'Re run one stage on its own to investigate:\n'
        printf '  scripts/run_tests.sh --only %s -v\n' "${FAILED[0]}"
        return 1
    fi

    printf '\n%severy stage that ran passed%s\n' "${GREEN}" "${RESET}"
    return 0
}

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

main() {
    parse_arguments "$@"
    configure_color

    if [[ "${MATRIX}" -eq 1 ]]; then
        if [[ -n "${MATRIX_DEPTH:-}" ]]; then
            fatal "the --matrix option cannot nest"
        fi
        # The option is consumed here, so the recursive invocations must not
        # see it again. Everything else is forwarded unchanged.
        local forwarded=()
        local argument
        for argument in "${FORWARDED_ARGUMENTS[@]}"; do
            if [[ "${argument}" != "--matrix" ]]; then
                forwarded+=("${argument}")
            fi
        done
        FORWARDED_ARGUMENTS=("${forwarded[@]}")
        run_matrix
        summarise
        return "$?"
    fi

    require_python
    require_pytest

    local stages=()
    local line
    while IFS= read -r line; do
        stages+=("${line}")
    done < <(resolve_stages)

    heading "Testing ${REPOSITORY_ROOT}"
    printf 'interpreter: %s (%s)\n' "${PYTHON}" "$("${PYTHON}" --version 2>&1)"
    printf 'stages:      %s\n' "${stages[*]}"
    check_import

    local stage
    for stage in "${stages[@]}"; do
        heading "${stage}"
        "stage_${stage}"
    done

    summarise
}

main "$@"
