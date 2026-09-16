#!/usr/bin/env bash
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Run every quality check the pipeline runs, in the same order, locally.
#
# Why this script exists
# ======================
#
# The lint workflow runs ten jobs in parallel on ten runners. That is the
# right shape for a pipeline and the wrong shape for a laptop: a contributor
# who pushes to find out whether the formatter agrees waits minutes for an
# answer that takes seconds locally. This script is the local equivalent, and
# it is deliberately ordered cheapest first so that the common failure, a
# formatting difference, is reported before the slow type check starts.
#
# It is also the script the pre commit configuration and the contributing
# guide point at, so that there is one answer to the question of what has to
# pass before a change is proposed.
#
# What it checks
# ==============
#
#   format        black and isort, in check mode
#   ruff          the fast rule set configured in pyproject.toml
#   flake8        the complexity and naming rules in .flake8
#   pylint        the slower analysis configured in .pylintrc
#   typing        mypy over the library
#   security      bandit over the library
#   prose         no long dash character and no emoji
#   notice        the license notice on every source file
#   version       every declaration of the version agrees
#   docstrings    every public module, class, and function has one
#   configs       every configuration file parses
#   shell         shellcheck over this directory
#   yaml          yamllint over the workflow and configuration files
#   spelling      codespell over the prose and the source
#   doctests      the docstring examples of the built packages
#
# A missing tool is reported as skipped rather than as a failure, because a
# contributor who has installed only the formatter should still be able to
# run the formatter check. Pass --strict to turn a missing tool into a
# failure, which is what the pipeline wants.
#
# Usage
# =====
#
#   scripts/lint.sh                    run every check
#   scripts/lint.sh --fix              apply what can be applied, then check
#   scripts/lint.sh --fast             skip pylint, mypy, and the doctests
#   scripts/lint.sh --only format,ruff run only these checks
#   scripts/lint.sh --skip pylint      run everything except these
#   scripts/lint.sh --list             print the check names and exit
#   scripts/lint.sh --strict           a missing tool is a failure
#   scripts/lint.sh --no-color         plain output, for a log or a pipe
#
# Exit status
# ===========
#
#   0   every check that ran passed
#   1   at least one check failed
#   2   the command line was wrong
#
# The status is what a hook or a pipeline reads, and the summary at the end is
# what a person reads. Both are produced in every mode.

set -euo pipefail

# ---------------------------------------------------------------------------
# Location
# ---------------------------------------------------------------------------

# Resolve the repository root from this file rather than from the working
# directory, so that the script behaves the same whether it is invoked as
# scripts/lint.sh, as ./lint.sh from inside scripts, or through an absolute
# path from a hook.
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" > /dev/null 2>&1 && pwd)"
REPOSITORY_ROOT="$(cd -- "${SCRIPT_DIR}/.." > /dev/null 2>&1 && pwd)"
cd -- "${REPOSITORY_ROOT}"

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# The interpreter to run the Python tools with. Overridable so that a
# contributor can check a change against another interpreter without
# activating an environment, which is the usual reason to want to.
PYTHON="${PYTHON:-python3}"

# The paths the Python linters are pointed at. This is the same list the
# lint workflow puts in its SOURCES variable, and the two must agree: a path
# checked in one place and not the other is a path where a defect can land.
SOURCES=(discretus tests examples benchmarks scripts)

# The package the type checker and the security scanner examine. They are
# pointed at the library alone, because a test may use a loose annotation on
# purpose and an example may use an assertion that the scanner dislikes.
LIBRARY="discretus"

# The trees whose docstring examples are executed. The whole library is
# named, and the runner skips a file of zero length, which is how the
# placeholders for the packages that are not written yet are passed over
# without maintaining a second list that would fall behind them.
DOCTEST_TARGETS=(discretus)

# The forbidden characters, written as code points so that this file does not
# itself contain what it rejects. The long dash and the shorter range dash
# are both excluded, and every character in the symbol category is treated as
# an emoji. The lint workflow holds its own copy of this set, and the two
# must stay in step.
FORBIDDEN_CODE_POINTS="0x2014,0x2013"

# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

USE_COLOR=1
if [[ ! -t 1 ]] || [[ -n "${NO_COLOR:-}" ]]; then
    USE_COLOR=0
fi

# Named escape sequences, assigned once so that the reporting functions read
# as prose. They are emptied when color is off, which makes every function
# below work unchanged in a log file.
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

report_pass() {
    printf '%spass%s  %s\n' "${GREEN}" "${RESET}" "$1"
}

report_fail() {
    printf '%sfail%s  %s\n' "${RED}" "${RESET}" "$1"
}

report_skip() {
    printf '%sskip%s  %s (%s)\n' "${YELLOW}" "${RESET}" "$1" "$2"
}

# ---------------------------------------------------------------------------
# Bookkeeping
# ---------------------------------------------------------------------------

PASSED=()
FAILED=()
SKIPPED=()

# The status a check returns to say that it could not run. Any value above
# the range the tools themselves use would do; this one is conventionally
# reserved for exactly this meaning and is not produced by any of them.
SKIP_STATUS=77

# Why the most recent check could not run, set by the check itself just
# before it returns the skip status.
SKIP_REASON=""

# Every check in the order it runs. Cheapest first, so that the answer a
# contributor is most likely to need arrives first, and the slow analysis
# only runs once the fast rules are satisfied.
ALL_CHECKS=(
    format
    ruff
    flake8
    prose
    notice
    version
    docstrings
    configs
    shell
    yaml
    spelling
    typing
    security
    pylint
    doctests
)

# The checks --fast leaves out. Each is slow for a different reason: the
# type checker builds a cache from nothing on a first run, the deep analysis
# imports the whole library, and the docstring examples execute it.
SLOW_CHECKS=(typing pylint doctests)

FIX=0
FAST=0
STRICT=0
ONLY=""
SKIP=""

# ---------------------------------------------------------------------------
# Tool availability
# ---------------------------------------------------------------------------

# A Python tool is available when the interpreter can import it as a module,
# which is a stronger test than looking for an executable on the path: a tool
# installed into a different environment has an executable that would run
# against the wrong interpreter.
python_module_available() {
    local module="$1"
    "${PYTHON}" -c "import importlib.util, sys; sys.exit(0 if importlib.util.find_spec('${module}') else 1)" \
        > /dev/null 2>&1
}

# An external tool is available when the shell can find it. The builtin is
# used rather than the external lookup command, because the latter is absent
# from a minimal image and its exit status is not portable.
command_available() {
    command -v -- "$1" > /dev/null 2>&1
}

# Record the outcome of one check. Every check funnels through this, so the
# summary cannot disagree with what was printed.
record() {
    local name="$1"
    local outcome="$2"
    local detail="${3:-}"
    case "${outcome}" in
        pass)
            PASSED+=("${name}")
            report_pass "${name}"
            ;;
        fail)
            FAILED+=("${name}")
            report_fail "${name}"
            ;;
        skip)
            if [[ "${STRICT}" -eq 1 ]]; then
                FAILED+=("${name}")
                report_fail "${name} (${detail}, and --strict was given)"
            else
                SKIPPED+=("${name}")
                report_skip "${name}" "${detail}"
            fi
            ;;
        *)
            printf 'internal error: unknown outcome %s\n' "${outcome}" >&2
            exit 1
            ;;
    esac
}

# Run a command, record the outcome under a check name, and keep going. The
# call sits in a condition, which is what suspends the exit on error setting
# for it, so a failing check does not abort the run: the point of the script
# is to report every problem at once rather than the first one.
run_check() {
    local name="$1"
    shift
    local status=0
    SKIP_REASON=""
    "$@" || status="$?"
    if [[ "${status}" -eq "${SKIP_STATUS}" ]]; then
        record "${name}" skip "${SKIP_REASON}"
    elif [[ "${status}" -eq 0 ]]; then
        record "${name}" pass
    else
        record "${name}" fail
    fi
}

# ---------------------------------------------------------------------------
# The checks
# ---------------------------------------------------------------------------

check_format() {
    local failures=0
    if python_module_available black; then
        if [[ "${FIX}" -eq 1 ]]; then
            "${PYTHON}" -m black "${SOURCES[@]}" || failures=1
        else
            "${PYTHON}" -m black --check --diff "${SOURCES[@]}" || failures=1
        fi
    else
        SKIP_REASON="black is not installed"
        return "${SKIP_STATUS}"
    fi

    if python_module_available isort; then
        if [[ "${FIX}" -eq 1 ]]; then
            "${PYTHON}" -m isort "${SOURCES[@]}" || failures=1
        else
            "${PYTHON}" -m isort --check-only --diff "${SOURCES[@]}" || failures=1
        fi
    else
        printf 'note: isort is not installed, import order was not checked\n'
    fi

    return "${failures}"
}

check_ruff() {
    if ! python_module_available ruff; then
        SKIP_REASON="ruff is not installed"
        return "${SKIP_STATUS}"
    fi
    if [[ "${FIX}" -eq 1 ]]; then
        "${PYTHON}" -m ruff check --fix "${SOURCES[@]}"
    else
        "${PYTHON}" -m ruff check "${SOURCES[@]}"
    fi
}

check_flake8() {
    if ! python_module_available flake8; then
        SKIP_REASON="flake8 is not installed"
        return "${SKIP_STATUS}"
    fi
    # The rule selection lives in .flake8. Nothing is passed here, so that
    # the configuration is the single description of what the rules are.
    "${PYTHON}" -m flake8 "${SOURCES[@]}"
}

check_pylint() {
    if ! python_module_available pylint; then
        SKIP_REASON="pylint is not installed"
        return "${SKIP_STATUS}"
    fi
    # Pointed at the library alone. The deeper analysis complains about
    # patterns that are correct in a test, an example, or a benchmark, and
    # silencing it there would mean scattering suppressions through code
    # whose purpose is to be read.
    "${PYTHON}" -m pylint "${LIBRARY}"
}

check_typing() {
    if ! python_module_available mypy; then
        SKIP_REASON="mypy is not installed"
        return "${SKIP_STATUS}"
    fi
    "${PYTHON}" -m mypy "${LIBRARY}"
}

check_security() {
    if ! python_module_available bandit; then
        SKIP_REASON="bandit is not installed"
        return "${SKIP_STATUS}"
    fi
    "${PYTHON}" -m bandit -c .bandit -r "${LIBRARY}"
}

check_prose() {
    # The repository writes prose with plain punctuation. The long dash and
    # the range dash are rejected, and so is every character the Unicode
    # tables classify as a symbol, which is how an emoji is recognised
    # without maintaining a list of them.
    #
    # The check is implemented here rather than delegated, so that it runs
    # without a network and without any tool installed. The lint workflow
    # holds an equivalent copy; the suffix set and the code points below are
    # the parts that must agree between them.
    FORBIDDEN_CODE_POINTS="${FORBIDDEN_CODE_POINTS}" "${PYTHON}" - <<'PY'
import os
import pathlib
import subprocess
import sys
import unicodedata

SUFFIXES = {
    ".py", ".md", ".txt", ".cfg", ".ini", ".toml", ".yml", ".yaml",
    ".json", ".jsonc", ".example", ".css", ".bat", ".sh",
}
EXTRA_NAMES = {
    ".mailmap", ".gitmessage", ".codespellrc", ".shellcheckrc",
    ".python-version", ".tool-versions", "Dockerfile", "Makefile",
    "CODEOWNERS", "NOTICE",
}
SKIP_FILES = {"LICENSE"}

forbidden = {
    chr(int(point, 16))
    for point in os.environ["FORBIDDEN_CODE_POINTS"].split(",")
}

def tracked_files():
    """Yield the files git tracks, or every file when git is unavailable.

    Only committed files are checked. A generated tree such as a coverage
    report or a built environment is ignored by git and is not the
    repository's prose, so checking it would report a failure that no edit
    of the repository could fix.
    """
    try:
        output = subprocess.run(
            ["git", "ls-files", "-z"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        return [
            path
            for path in sorted(pathlib.Path(".").rglob("*"))
            if path.is_file()
        ]
    return [
        pathlib.Path(name)
        for name in output.split("\0")
        if name and pathlib.Path(name).is_file()
    ]


failures = []
for path in tracked_files():
    if path.name in SKIP_FILES:
        continue
    if path.suffix not in SUFFIXES and path.name not in EXTRA_NAMES:
        continue
    text = path.read_text(encoding="utf-8", errors="replace")
    for number, line in enumerate(text.splitlines(), start=1):
        for character in line:
            if character in forbidden:
                failures.append(f"{path}:{number}: long dash character")
                break
            if unicodedata.category(character) == "So":
                failures.append(f"{path}:{number}: emoji or symbol character")
                break

if failures:
    print("\n".join(failures))
    print()
    print("Replace a long dash with a comma, a colon, or a period.")
    sys.exit(1)
PY
}

check_notice() {
    # The Mozilla Public License 2.0 applies per file, so a source file
    # without the three line notice is a licensing defect rather than a
    # style one. An empty file is exempt, because the repository carries
    # placeholders for packages that are not written yet.
    "${PYTHON}" - <<'PY'
import pathlib
import subprocess
import sys

NOTICE = "mozilla.org/MPL/2.0"

def tracked_files():
    """Yield the files git tracks, or every file when git is unavailable.

    Only committed files are checked. A generated tree such as a coverage
    report or a built environment is ignored by git and is not the
    repository's prose, so checking it would report a failure that no edit
    of the repository could fix.
    """
    try:
        output = subprocess.run(
            ["git", "ls-files", "-z"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        return [
            path
            for path in sorted(pathlib.Path(".").rglob("*"))
            if path.is_file()
        ]
    return [
        pathlib.Path(name)
        for name in output.split("\0")
        if name and pathlib.Path(name).is_file()
    ]


failures = []
for path in tracked_files():
    if path.suffix not in {".py", ".sh"}:
        continue
    if path.stat().st_size == 0:
        continue
    if NOTICE not in path.read_text(encoding="utf-8")[:500]:
        failures.append(str(path))

if failures:
    print("missing the license notice:")
    for name in sorted(failures):
        print("  ", name)
    sys.exit(1)
PY
}

check_version() {
    # The version appears in several files that must never disagree, because
    # the release workflow refuses to publish when the tag and the declared
    # version differ. .bumpversion.cfg is the list of those files, so the
    # check reads it rather than carrying a second list that could drift.
    "${PYTHON}" - <<'PY'
import configparser
import pathlib
import re
import sys

text = pathlib.Path("discretus/__about__.py").read_text(encoding="utf-8")
match = re.search(r'__version__ = "([^"]+)"', text)
if match is None:
    print("discretus/__about__.py does not declare __version__")
    sys.exit(1)
version = match.group(1)

failures = []

tuple_match = re.search(r"__version_info__ = \(([^)]*)\)", text)
if tuple_match is None:
    failures.append("discretus/__about__.py does not declare __version_info__")
else:
    parts = [part.strip() for part in tuple_match.group(1).split(",")]
    parts = [part for part in parts if part]
    if ".".join(parts) != version:
        failures.append(
            f"__version_info__ is {tuple_match.group(1)} but __version__ is {version}"
        )

config = configparser.RawConfigParser()
config.read(".bumpversion.cfg")
if config["bumpversion"]["current_version"] != version:
    failures.append(
        f".bumpversion.cfg declares {config['bumpversion']['current_version']}"
    )

for section in config.sections():
    if not section.startswith("bumpversion:file"):
        continue
    # A section is either bumpversion:file:PATH or, when one file needs
    # more than one replacement, bumpversion:file(label):PATH. The path is
    # the last colon separated part in both forms.
    path = pathlib.Path(section.split(":", 2)[-1])
    if not path.exists():
        failures.append(f"{path} is listed in .bumpversion.cfg and missing")
        continue
    # The search string is a format template, so a literal brace in it is
    # doubled. Formatting it rather than substituting the placeholder by
    # hand is what makes the README citation example, whose value is inside
    # braces, resolve to the text that is actually in the file.
    needle = config[section]["search"].format(current_version=version)
    if needle not in path.read_text(encoding="utf-8"):
        failures.append(f"{path} does not contain {needle!r}")

if failures:
    print("\n".join(failures))
    sys.exit(1)
print(f"every declaration agrees on {version}")
PY
}

check_docstrings() {
    # Every public module, class, and function carries a docstring, because
    # the reference is generated from them and an undocumented name produces
    # an empty entry rather than an obvious gap.
    #
    # The rule matches the convention the contributing guide states, which is
    # narrower than requiring a docstring on everything:
    #
    #   a module needs one, unless the file is an empty placeholder for a
    #   package that has not been written yet
    #
    #   a class or function defined at module level needs one, unless its
    #   name begins with an underscore, which marks it private
    #
    #   a method in the body of a public class needs one under the same
    #   rule, so a leading underscore exempts it
    #
    #   a special method does not need one, because what it does is fixed by
    #   the language and the documentation tool renders the inherited text
    #
    #   a function nested inside another function does not need one, because
    #   it is not reachable from outside and cannot appear in the reference
    #
    # The docstring completeness job in the lint workflow checks the names in
    # every __all__ declaration instead, which is a different and narrower
    # cut of the same rule. Both are worth running: this one catches a public
    # routine that was never exported, and that one catches an exported name
    # that does not exist.
    "${PYTHON}" - <<'PYCHECK'
import ast
import pathlib
import sys


def is_special(name):
    return name.startswith("__") and name.endswith("__")


def needs_docstring(name):
    return not name.startswith("_")


failures = []
for path in sorted(pathlib.Path("discretus").rglob("*.py")):
    if "__pycache__" in path.parts or path.stat().st_size == 0:
        continue
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    if ast.get_docstring(tree) is None:
        failures.append(f"{path}:1: the module has no docstring")

    definition = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
    for node in tree.body:
        if not isinstance(node, definition):
            continue
        if not needs_docstring(node.name):
            continue
        if ast.get_docstring(node) is None:
            failures.append(f"{path}:{node.lineno}: {node.name} has no docstring")
        if not isinstance(node, ast.ClassDef):
            continue
        for member in node.body:
            if not isinstance(member, definition):
                continue
            if is_special(member.name) or not needs_docstring(member.name):
                continue
            if ast.get_docstring(member) is None:
                failures.append(
                    f"{path}:{member.lineno}: "
                    f"{node.name}.{member.name} has no docstring"
                )

if failures:
    print("\n".join(failures))
    sys.exit(1)
PYCHECK
}

check_configs() {
    # Every configuration file parses. A malformed one usually fails much
    # later, in a job that looks unrelated, so parsing them all up front is
    # the cheapest check in the suite and one of the most useful.
    "${PYTHON}" - <<'PY'
import configparser
import json
import pathlib
import re
import subprocess
import sys

try:
    import yaml
except ImportError:
    yaml = None

def tracked_files():
    """Yield the files git tracks, or every file when git is unavailable.

    Only committed files are checked. A generated tree such as a coverage
    report or a built environment is ignored by git and is not the
    repository's prose, so checking it would report a failure that no edit
    of the repository could fix.
    """
    try:
        output = subprocess.run(
            ["git", "ls-files", "-z"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        return [
            path
            for path in sorted(pathlib.Path(".").rglob("*"))
            if path.is_file()
        ]
    return [
        pathlib.Path(name)
        for name in output.split("\0")
        if name and pathlib.Path(name).is_file()
    ]

failures = []
skipped = 0


def parse_commented_json(text):
    return json.loads(re.sub(r"^\s*//.*$", "", text, flags=re.M))


def check(path, loader):
    try:
        loader(path.read_text(encoding="utf-8"))
    except Exception as error:
        failures.append(f"{path}: {type(error).__name__}: {error}")


for path in tracked_files():
    if path.suffix in {".yml", ".yaml"}:
        if yaml is None:
            skipped += 1
            continue
        check(path, yaml.safe_load)
    elif path.suffix == ".jsonc" or path.name == "asv.conf.json":
        check(path, parse_commented_json)
    elif path.suffix == ".json":
        check(path, json.loads)
    elif path.suffix in {".cfg", ".ini"} or path.name in {
        ".codespellrc",
        ".bumpversion.cfg",
    }:
        check(path, lambda text: configparser.RawConfigParser().read_string(text))

if failures:
    print("\n".join(failures))
    sys.exit(1)
if skipped:
    print(f"{skipped} YAML files were not parsed because PyYAML is absent")
PY
}

check_shell() {
    if ! command_available shellcheck; then
        SKIP_REASON="shellcheck is not installed"
        return "${SKIP_STATUS}"
    fi
    # The severity floor is a command line concern, and .shellcheckrc says
    # so. The lowest level is requested here so that a finding is visible
    # locally before it is visible in review.
    shellcheck --severity=style scripts/*.sh
}

check_yaml() {
    if ! python_module_available yamllint; then
        SKIP_REASON="yamllint is not installed"
        return "${SKIP_STATUS}"
    fi
    "${PYTHON}" -m yamllint --strict .
}

check_spelling() {
    if ! python_module_available codespell_lib; then
        SKIP_REASON="codespell is not installed"
        return "${SKIP_STATUS}"
    fi
    # The word list and the ignored paths live in .codespellrc.
    "${PYTHON}" -m codespell_lib
}

check_doctests() {
    # The docstring examples are executed, because an example that is not
    # executed is a comment that looks like a guarantee. Only the packages
    # that are implemented are listed, and the list grows with the library.
    local target
    local failures=0
    for target in "${DOCTEST_TARGETS[@]}"; do
        if [[ ! -d "${target}" ]]; then
            continue
        fi
        if ! "${PYTHON}" - "${target}" <<'PY'
import doctest
import importlib
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
package = str(root).replace("/", ".")
attempted = 0
failed = 0
for path in sorted(root.rglob("*.py")):
    if "__pycache__" in path.parts or path.stat().st_size == 0:
        continue
    name = str(path.with_suffix("")).replace("/", ".")
    if name.endswith(".__init__"):
        name = name[: -len(".__init__")]
    module = importlib.import_module(name)
    result = doctest.testmod(module, verbose=False)
    attempted += result.attempted
    failed += result.failed

print(f"{package}: {attempted} docstring examples, {failed} failed")
sys.exit(1 if failed else 0)
PY
        then
            failures=1
        fi
    done
    return "${failures}"
}

# ---------------------------------------------------------------------------
# Command line
# ---------------------------------------------------------------------------

usage() {
    cat <<'USAGE'
Run the repository quality checks.

Usage:
  scripts/lint.sh [options]

Options:
  --fix              apply what can be applied, then check the rest
  --fast             skip the slow checks, namely typing, pylint, doctests
  --only NAMES       run only these checks, comma separated
  --skip NAMES       run everything except these checks, comma separated
  --strict           treat a missing tool as a failure
  --list             print the check names in the order they run
  --no-color         plain output, for a log file or a pipe
  -h, --help         print this text

Checks:
  format ruff flake8 prose notice version docstrings configs shell yaml
  spelling typing security pylint doctests

Examples:
  scripts/lint.sh --fix
  scripts/lint.sh --fast
  scripts/lint.sh --only prose,notice,version
  scripts/lint.sh --skip pylint,typing
USAGE
}

parse_arguments() {
    while [[ "$#" -gt 0 ]]; do
        case "$1" in
            --fix)
                FIX=1
                shift
                ;;
            --fast)
                FAST=1
                shift
                ;;
            --strict)
                STRICT=1
                shift
                ;;
            --only)
                if [[ "$#" -lt 2 ]]; then
                    printf 'the --only option needs a value\n' >&2
                    exit 2
                fi
                ONLY="$2"
                shift 2
                ;;
            --only=*)
                ONLY="${1#--only=}"
                shift
                ;;
            --skip)
                if [[ "$#" -lt 2 ]]; then
                    printf 'the --skip option needs a value\n' >&2
                    exit 2
                fi
                SKIP="$2"
                shift 2
                ;;
            --skip=*)
                SKIP="${1#--skip=}"
                shift
                ;;
            --no-color)
                USE_COLOR=0
                shift
                ;;
            --list)
                printf '%s\n' "${ALL_CHECKS[@]}"
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

# Return success when a name appears in a comma separated list.
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

# Decide whether one check runs, applying the selection options in the order
# their names suggest: an explicit selection wins over an exclusion, and both
# win over the fast preset.
wanted() {
    local name="$1"
    if [[ -n "${ONLY}" ]]; then
        in_list "${name}" "${ONLY}"
        return "$?"
    fi
    if [[ -n "${SKIP}" ]] && in_list "${name}" "${SKIP}"; then
        return 1
    fi
    if [[ "${FAST}" -eq 1 ]]; then
        local slow
        for slow in "${SLOW_CHECKS[@]}"; do
            if [[ "${slow}" == "${name}" ]]; then
                return 1
            fi
        done
    fi
    return 0
}

# Reject a selection that names a check that does not exist, rather than
# quietly running nothing, which is the failure mode of a typed option.
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
        for known in "${ALL_CHECKS[@]}"; do
            if [[ "${known}" == "${item}" ]]; then
                found=1
                break
            fi
        done
        if [[ "${found}" -eq 0 ]]; then
            IFS="${saved_ifs}"
            printf 'the %s option names an unknown check: %s\n' "${label}" "${item}" >&2
            printf 'known checks: %s\n' "${ALL_CHECKS[*]}" >&2
            exit 2
        fi
    done
    IFS="${saved_ifs}"
}

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

summarise() {
    heading "Summary"
    printf 'passed:  %s\n' "${#PASSED[@]}"
    printf 'failed:  %s\n' "${#FAILED[@]}"
    printf 'skipped: %s\n' "${#SKIPPED[@]}"

    if [[ "${#SKIPPED[@]}" -gt 0 ]]; then
        printf '\nnot run: %s\n' "${SKIPPED[*]}"
        printf 'install the development extra to run them:\n'
        printf '  %s -m pip install -e ".[dev]"\n' "${PYTHON}"
    fi

    if [[ "${#FAILED[@]}" -gt 0 ]]; then
        printf '\n%sfailing: %s%s\n' "${RED}" "${FAILED[*]}" "${RESET}"
        printf 'Most formatting failures are fixed by:\n'
        printf '  scripts/lint.sh --fix\n'
        return 1
    fi

    printf '\n%severy check that ran passed%s\n' "${GREEN}" "${RESET}"
    return 0
}

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

main() {
    parse_arguments "$@"
    configure_color

    if [[ -n "${ONLY}" ]]; then
        validate_selection "${ONLY}" "--only"
    fi
    if [[ -n "${SKIP}" ]]; then
        validate_selection "${SKIP}" "--skip"
    fi

    heading "Checking ${REPOSITORY_ROOT}"
    printf 'interpreter: %s (%s)\n' "${PYTHON}" "$("${PYTHON}" --version 2>&1)"
    if [[ "${FIX}" -eq 1 ]]; then
        printf 'mode: applying what can be applied\n'
    fi

    local name
    for name in "${ALL_CHECKS[@]}"; do
        if ! wanted "${name}"; then
            continue
        fi
        heading "${name}"
        run_check "${name}" "check_${name}"
    done

    summarise
}

main "$@"
