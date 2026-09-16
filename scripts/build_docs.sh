#!/usr/bin/env bash
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Build the documentation the way the pipeline builds it.
#
# Why this script exists
# ======================
#
# The documentation workflow runs eight jobs, and only one of them is the
# plain HTML build. The others check that every expected page was produced,
# that the build is clean with warnings treated as errors, that the examples
# inside the pages still run, that every public object has a reference entry,
# that every external link still resolves, and that the printable form
# builds. A contributor who runs the plain build locally is checking the one
# thing least likely to be wrong.
#
# This script runs the same stages locally, in the same order. The default is
# the strict build and the page inventory, which together catch the two
# failures that actually happen: a warning that has become an error, and a
# page that was written and never added to a table of contents.
#
# What it can run
# ===============
#
#   html        the plain build, which tolerates warnings
#   strict      the build with warnings treated as errors
#   pages       confirm that every expected page was produced
#   doctest     the examples inside the documentation pages
#   coverage    report public objects with no reference entry
#   links       check that every external link resolves
#   pdf         the printable form, through LaTeX
#   serve       build and serve the result on a local port
#   clean       remove the build tree
#
# The link check reaches the network and is therefore not part of the
# default, both because it is slow and because a transient failure in
# somebody else's server is not a defect in this repository.
#
# Usage
# =====
#
#   scripts/build_docs.sh                  the default stages
#   scripts/build_docs.sh --all            every stage except serve
#   scripts/build_docs.sh --only html      one stage
#   scripts/build_docs.sh --serve          build and serve on port 8000
#   scripts/build_docs.sh --serve --port 9000
#   scripts/build_docs.sh --clean          remove the build tree and stop
#   scripts/build_docs.sh --open           open the result in a browser
#   scripts/build_docs.sh --jobs auto      build in parallel
#
# Exit status
# ===========
#
#   0   every stage that ran passed
#   1   at least one stage failed
#   2   the command line was wrong, or Sphinx is not installed
#
# The tool is reported as missing rather than assumed, because the
# documentation stack is an optional extra: a contributor working on the
# library alone has no reason to have installed it.

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

PYTHON="${PYTHON:-python3}"

# The documentation source and the build tree. The tree is inside docs so
# that the Sphinx makefile and this script agree on where output goes, and
# .gitignore keeps it out of the repository.
DOCS_DIR="docs"
BUILD_DIR="docs/_build"

# The port the serve stage listens on. Overridable, because the obvious port
# is often already taken by whatever else is being worked on.
PORT="${PORT:-8000}"

# How many processes Sphinx uses. Empty means one, which is the reproducible
# default: a parallel build can interleave warnings in a way that makes them
# hard to attribute. Pass --jobs auto when waiting matters more than that.
JOBS=""

# The pages the build must produce. This is the same inventory the page
# confirmation job in the documentation workflow uses, and the two must
# agree. A page missing from the output almost always means it is missing
# from a table of contents, which Sphinx reports as a warning among many.
EXPECTED_PAGES=(
    index.html
    installation.html
    quickstart.html
    contributing.html
    changelog.html
    api/core.html
    api/sets.html
    api/logic.html
    api/combinatorics.html
    api/graphs.html
    api/number_theory.html
    api/recurrences.html
    api/algebra.html
    api/viz.html
    api/io.html
    api/utils.html
    tutorials/getting_started.html
    tutorials/set_theory.html
    tutorials/sat_solving.html
    tutorials/graph_algorithms.html
    tutorials/number_theory.html
    tutorials/group_theory.html
)

# The stages, in the order they run. The plain build comes first so that a
# syntax error in a page is reported before the strict build turns the
# resulting warning into an error and stops.
ALL_STAGES=(html strict pages doctest coverage links pdf)

# What runs when no selection is given. The strict build subsumes the plain
# one, so the default is the strict build and the page inventory.
DEFAULT_STAGES=(strict pages)

# The stages --all leaves out, because each reaches outside the repository.
NETWORK_STAGES=(links)

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
SKIPPED=()

SELECTED=""
WITH_ALL=0
WITH_NETWORK=0
DO_SERVE=0
DO_CLEAN=0
DO_OPEN=0
KEEP_GOING=1

# ---------------------------------------------------------------------------
# Preconditions
# ---------------------------------------------------------------------------

python_module_available() {
    local module="$1"
    "${PYTHON}" -c "import importlib.util, sys; sys.exit(0 if importlib.util.find_spec('${module}') else 1)" \
        > /dev/null 2>&1
}

require_sphinx() {
    if ! python_module_available sphinx; then
        printf 'Sphinx is not installed for %s.\n' "${PYTHON}" >&2
        printf 'Install the documentation extra:\n' >&2
        printf '  %s -m pip install -e ".[docs]"\n' "${PYTHON}" >&2
        exit 2
    fi
}

# The reference is generated by importing the library, so a library that does
# not import produces a build full of autodoc warnings that all say the same
# thing. Report the import failure instead.
require_import() {
    if ! "${PYTHON}" -c "import discretus" > /dev/null 2>&1; then
        fatal "the library does not import, so the reference cannot be generated"
    fi
}

report_versions() {
    note "interpreter: $("${PYTHON}" --version 2>&1)"
    note "sphinx:      $("${PYTHON}" -m sphinx --version 2>&1)"
    if python_module_available myst_parser; then
        note "myst:        present"
    else
        warn "myst-parser is absent, so the Markdown pages will not be parsed"
    fi
    if python_module_available furo; then
        note "theme:       furo"
    else
        warn "the configured theme is absent, so the build will fall back"
    fi
}

record() {
    local name="$1"
    local outcome="$2"
    local detail="${3:-}"
    case "${outcome}" in
        pass)
            PASSED+=("${name}")
            printf '%spass%s  %s\n' "${GREEN}" "${RESET}" "${name}"
            ;;
        fail)
            FAILED+=("${name}")
            printf '%sfail%s  %s\n' "${RED}" "${RESET}" "${name}"
            ;;
        skip)
            SKIPPED+=("${name}")
            printf '%sskip%s  %s (%s)\n' "${YELLOW}" "${RESET}" "${name}" "${detail}"
            ;;
        *)
            fatal "internal error: unknown outcome ${outcome}"
            ;;
    esac
}

run_stage() {
    local name="$1"
    shift
    if "$@"; then
        record "${name}" pass
    else
        record "${name}" fail
    fi
}

# Assemble the options every Sphinx invocation shares.
sphinx_options() {
    local options=()
    if [[ -n "${JOBS}" ]]; then
        options+=("-j" "${JOBS}")
    fi
    if [[ "${#options[@]}" -gt 0 ]]; then
        printf '%s\n' "${options[@]}"
    fi
}

read_sphinx_options() {
    local -n target="$1"
    target=()
    local line
    while IFS= read -r line; do
        target+=("${line}")
    done < <(sphinx_options)
}

# ---------------------------------------------------------------------------
# The stages
# ---------------------------------------------------------------------------

stage_html() {
    # The plain build. Warnings are printed and tolerated, which is what
    # makes this stage useful before the strict one: a page with a broken
    # reference still builds, so the rest of the output can be inspected.
    local options=()
    read_sphinx_options options
    "${PYTHON}" -m sphinx -b html "${options[@]}" \
        "${DOCS_DIR}" "${BUILD_DIR}/html"
}

stage_strict() {
    # The build the release check uses. Warnings become errors, and the keep
    # going flag reports every one of them instead of stopping at the first,
    # because fixing warnings one build at a time is the slowest possible
    # way to do it.
    local options=()
    read_sphinx_options options
    if [[ "${KEEP_GOING}" -eq 1 ]]; then
        options+=(--keep-going)
    fi
    "${PYTHON}" -m sphinx -b html -W "${options[@]}" \
        "${DOCS_DIR}" "${BUILD_DIR}/html"
}

stage_pages() {
    # Confirm that every page the inventory names was produced. A missing
    # page is almost always a page left out of a table of contents, which
    # Sphinx reports as one warning among many and which is invisible in a
    # build that tolerates warnings.
    local root="${BUILD_DIR}/html"
    if [[ ! -d "${root}" ]]; then
        note "nothing is built yet, so the inventory has nothing to check"
        return 1
    fi

    local page
    local missing=()
    for page in "${EXPECTED_PAGES[@]}"; do
        if [[ ! -f "${root}/${page}" ]]; then
            missing+=("${page}")
        fi
    done

    if [[ "${#missing[@]}" -gt 0 ]]; then
        printf 'pages missing from the built site:\n'
        printf '  %s\n' "${missing[@]}"
        printf '\nA missing page is usually a page absent from a toctree.\n'
        return 1
    fi

    note "all ${#EXPECTED_PAGES[@]} expected pages were produced"
}

stage_doctest() {
    # The examples inside the documentation pages, as opposed to the ones
    # inside the docstrings. Both are executed, because an example that is
    # not executed is a comment that looks like a guarantee, and the two
    # live in different places and are checked by different builders.
    local options=()
    read_sphinx_options options
    "${PYTHON}" -m sphinx -b doctest "${options[@]}" \
        "${DOCS_DIR}" "${BUILD_DIR}/doctest"
}

stage_coverage() {
    # Report the public objects that have no entry in the reference. The
    # builder writes its findings to a file rather than to the terminal and
    # exits successfully either way, so the file is read back and an
    # undocumented object is turned into a failure here.
    local options=()
    read_sphinx_options options
    if ! "${PYTHON}" -m sphinx -b coverage "${options[@]}" \
        "${DOCS_DIR}" "${BUILD_DIR}/coverage"; then
        return 1
    fi

    local report="${BUILD_DIR}/coverage/python.txt"
    if [[ ! -f "${report}" ]]; then
        warn "the coverage builder produced no report"
        return 1
    fi

    note "the report is at ${report}"
    # The report lists a module heading for every module it examined, and
    # an indented line for every object with no entry. A report with no
    # indented lines is a complete reference.
    local undocumented
    undocumented="$(grep -c '^[[:space:]]\+' "${report}" || true)"
    if [[ "${undocumented}" -gt 0 ]]; then
        printf '%s objects have no reference entry:\n' "${undocumented}"
        grep '^[[:space:]]\+' "${report}" | head -n 40
        if [[ "${undocumented}" -gt 40 ]]; then
            printf '  ... and %s more, see the report\n' "$((undocumented - 40))"
        fi
        return 1
    fi

    note "every public object has a reference entry"
}

stage_links() {
    # Check that every external link resolves. This reaches the network, so
    # it is opt in: a transient failure in somebody else's server is not a
    # defect in this repository, and the pipeline runs it on a schedule for
    # exactly that reason.
    local options=()
    read_sphinx_options options
    if ! "${PYTHON}" -m sphinx -b linkcheck "${options[@]}" \
        "${DOCS_DIR}" "${BUILD_DIR}/linkcheck"; then
        local report="${BUILD_DIR}/linkcheck/output.txt"
        if [[ -f "${report}" ]]; then
            printf 'the broken links are:\n'
            grep -v -e '\[ *ok *\]' "${report}" | head -n 40 || true
        fi
        return 1
    fi
    note "every link resolved"
}

stage_pdf() {
    # The printable form. Sphinx produces the LaTeX sources and a makefile,
    # and the conversion to a document needs a TeX installation, which most
    # laptops do not have. The sources are built either way, and the
    # conversion is attempted only when the tool is present.
    local options=()
    read_sphinx_options options
    if ! "${PYTHON}" -m sphinx -b latex "${options[@]}" \
        "${DOCS_DIR}" "${BUILD_DIR}/latex"; then
        return 1
    fi

    if ! command -v -- latexmk > /dev/null 2>&1; then
        note "latexmk is absent, so only the LaTeX sources were produced"
        note "they are in ${BUILD_DIR}/latex"
        return 0
    fi

    "${PYTHON}" -m sphinx -M latexpdf "${DOCS_DIR}" "${BUILD_DIR}" \
        > /dev/null
    note "the document is in ${BUILD_DIR}/latex"
}

# ---------------------------------------------------------------------------
# The actions that are not stages
# ---------------------------------------------------------------------------

do_clean() {
    heading "Cleaning"
    if [[ -d "${BUILD_DIR}" ]]; then
        rm -rf -- "${BUILD_DIR}"
        note "removed ${BUILD_DIR}"
    else
        note "nothing to remove"
    fi
}

do_serve() {
    local root="${BUILD_DIR}/html"
    if [[ ! -f "${root}/index.html" ]]; then
        fatal "nothing is built, so there is nothing to serve"
    fi
    heading "Serving"
    note "the documentation is on http://localhost:${PORT}"
    note "stop it with Control C"
    "${PYTHON}" -m http.server "${PORT}" --directory "${root}"
}

do_open() {
    local page="${BUILD_DIR}/html/index.html"
    if [[ ! -f "${page}" ]]; then
        warn "nothing is built, so there is nothing to open"
        return 0
    fi
    # Try the platform openers in turn. Failing to find one is not an error:
    # the path is printed, which is all a terminal user needs.
    local opener
    for opener in xdg-open open; do
        if command -v -- "${opener}" > /dev/null 2>&1; then
            "${opener}" "${page}" > /dev/null 2>&1 || true
            return 0
        fi
    done
    note "open this file in a browser: ${REPOSITORY_ROOT}/${page}"
}

# ---------------------------------------------------------------------------
# Command line
# ---------------------------------------------------------------------------

usage() {
    cat <<'USAGE'
Build the documentation the way the pipeline builds it.

Usage:
  scripts/build_docs.sh [options]

Stage selection:
  --only NAMES       run only these stages, comma separated
  --all              run every stage except the ones that need the network
  --network          include the stages that reach the network
  --list             print the stage names in the order they run

Actions:
  --clean            remove the build tree and stop
  --serve            build, then serve the result locally
  --open             open the result in a browser when the build finishes
  --port N           the port the serve action listens on, default 8000

Build options:
  --jobs N           build with N processes, or auto for one per core
  --no-keep-going    let the strict build stop at the first warning
  --no-color         plain output, for a log file or a pipe
  -h, --help         print this text

Stages:
  html strict pages doctest coverage links pdf

Examples:
  scripts/build_docs.sh
  scripts/build_docs.sh --all
  scripts/build_docs.sh --only html --serve
  scripts/build_docs.sh --only links --network
  scripts/build_docs.sh --clean
USAGE
}

parse_arguments() {
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
            --all)
                WITH_ALL=1
                shift
                ;;
            --network)
                WITH_NETWORK=1
                shift
                ;;
            --clean)
                DO_CLEAN=1
                shift
                ;;
            --serve)
                DO_SERVE=1
                shift
                ;;
            --open)
                DO_OPEN=1
                shift
                ;;
            --port)
                [[ "$#" -ge 2 ]] || fatal "the --port option needs a value"
                PORT="$2"
                shift 2
                ;;
            --jobs)
                [[ "$#" -ge 2 ]] || fatal "the --jobs option needs a value"
                JOBS="$2"
                shift 2
                ;;
            --no-keep-going)
                KEEP_GOING=0
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
            printf 'unknown stage: %s\n' "${item}" >&2
            printf 'known stages: %s\n' "${ALL_STAGES[*]}" >&2
            exit 2
        fi
    done
    IFS="${saved_ifs}"
}

needs_network() {
    local name="$1"
    local stage
    for stage in "${NETWORK_STAGES[@]}"; do
        if [[ "${stage}" == "${name}" ]]; then
            return 0
        fi
    done
    return 1
}

resolve_stages() {
    local requested=()
    local name

    if [[ -n "${SELECTED}" ]]; then
        validate_selection "${SELECTED}"
        for name in "${ALL_STAGES[@]}"; do
            if in_list "${name}" "${SELECTED}"; then
                requested+=("${name}")
            fi
        done
    elif [[ "${WITH_ALL}" -eq 1 ]]; then
        requested=("${ALL_STAGES[@]}")
    else
        requested=("${DEFAULT_STAGES[@]}")
    fi

    # A network stage runs only when it was asked for by name or when the
    # network option was given, so that --all stays offline. Dropping one is
    # announced on the error stream, because a stage that silently does not
    # run is worse than one that visibly did not.
    for name in "${requested[@]}"; do
        if needs_network "${name}" && [[ "${WITH_NETWORK}" -eq 0 ]]; then
            if [[ -z "${SELECTED}" ]]; then
                printf 'the %s stage needs the network, pass --network\n' \
                    "${name}" >&2
                continue
            fi
        fi
        printf '%s\n' "${name}"
    done
}

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

summarise() {
    heading "Summary"
    printf 'passed:  %s\n' "${#PASSED[@]}"
    printf 'failed:  %s\n' "${#FAILED[@]}"
    printf 'skipped: %s\n' "${#SKIPPED[@]}"

    if [[ "${#FAILED[@]}" -gt 0 ]]; then
        printf '\n%sfailing: %s%s\n' "${RED}" "${FAILED[*]}" "${RESET}"
        printf '%s\n' \
            'Re run one stage on its own to investigate:' \
            "  scripts/build_docs.sh --only ${FAILED[0]}"
        return 1
    fi

    if [[ -f "${BUILD_DIR}/html/index.html" ]]; then
        printf '\nthe site is at %s/%s/html/index.html\n' \
            "${REPOSITORY_ROOT}" "${BUILD_DIR}"
    fi
    printf '%severy stage that ran passed%s\n' "${GREEN}" "${RESET}"
    return 0
}

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

main() {
    parse_arguments "$@"
    configure_color

    if [[ "${DO_CLEAN}" -eq 1 ]]; then
        do_clean
        return 0
    fi

    require_sphinx
    require_import

    local stages=()
    local line
    while IFS= read -r line; do
        stages+=("${line}")
    done < <(resolve_stages)

    heading "Building the documentation of ${REPOSITORY_ROOT}"
    report_versions
    printf 'stages:      %s\n' "${stages[*]}"

    local stage
    for stage in "${stages[@]}"; do
        heading "${stage}"
        run_stage "${stage}" "stage_${stage}"
    done

    local status=0
    summarise || status="$?"

    if [[ "${DO_OPEN}" -eq 1 ]]; then
        do_open
    fi

    if [[ "${DO_SERVE}" -eq 1 ]]; then
        if [[ "${status}" -ne 0 ]]; then
            warn "a stage failed, serving the result anyway"
        fi
        do_serve
    fi

    return "${status}"
}

main "$@"
