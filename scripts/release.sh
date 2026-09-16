#!/usr/bin/env bash
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Drive a release up to the point where a person has to decide.
#
# What a release is here
# ======================
#
# A release is a pushed tag. The release workflow triggers on a tag of the
# form vX.Y.Z, verifies that the tag agrees with the declared version,
# builds the distribution once, installs it on every supported platform,
# publishes it to the test index, then to the real one through trusted
# publishing, and finally creates the forge release. No credential for a
# package index is stored anywhere, and none is needed: the workflow proves
# its identity to the index instead.
#
# That means this script cannot and must not publish anything. What it can
# do is everything that happens before the tag is pushed, so that a failure
# is found on a laptop in minutes rather than in a pipeline that has already
# made a version number public.
#
# The order below is the same order the workflow uses, and each stage gates
# the next:
#
#   preflight   the repository is in a releasable state at all
#   version     every declaration of the version agrees, and the tag is free
#   changelog   the version has an entry, and Unreleased was emptied
#   lint        the quality gate passes
#   tests       the suite, the docstring examples, and the coverage floor
#   docs        the strict documentation build
#   build       the source distribution and the wheel, with the metadata
#               checked and the digests recorded
#   install     both artifacts installed into throwaway environments and
#               exercised, which is the only check that catches a packaging
#               mistake such as a missing subpackage
#   summary     what to do next, and the exact commands to do it with
#
# Usage
# =====
#
#   scripts/release.sh                     every stage, then stop
#   scripts/release.sh --only build,install
#   scripts/release.sh --skip docs
#   scripts/release.sh --list
#   scripts/release.sh --tag               create the annotated tag as well
#   scripts/release.sh --push              create it and push it, which
#                                          starts the publishing workflow
#   scripts/release.sh --dry-run           print the plan and change nothing
#
# Exit status
# ===========
#
#   0   every stage that ran passed
#   1   at least one stage failed, so the release is not ready
#   2   the command line was wrong, or a required tool is absent
#
# Publishing
# ==========
#
# Never from here. When every stage passes:
#
#   scripts/bump_version.py minor          raise the version and tag it
#   git show                               read what it did
#   git push --follow-tags                 the workflow does the rest
#
# A mistaken push cannot be recalled, and a version that reached an index
# cannot be replaced, only superseded. The separation is deliberate.

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

# The branch a release is cut from. A tag on any other branch would publish
# code that never passed the pipeline on the default branch.
RELEASE_BRANCH="${RELEASE_BRANCH:-main}"

# The distribution directory. Cleared before a build, because a stale
# artifact from an earlier version is the classic way to publish the wrong
# file: the upload step takes everything it finds here.
DIST_DIR="dist"

# Where the throwaway environments for the install stage go.
VERIFY_DIR="build/release-verify"

# The minimum coverage percentage the test stage enforces, which is the same
# floor the coverage job uses.
COVERAGE_MINIMUM="${COVERAGE_MINIMUM:-90}"

# The stages, in the order they run.
ALL_STAGES=(
    preflight
    version
    changelog
    lint
    tests
    docs
    build
    install
)

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
SKIP=""
DRY_RUN=0
DO_TAG=0
DO_PUSH=0
ALLOW_DIRTY=0
ALLOW_BRANCH=0

# The version being released, read once in the version stage and reported in
# the summary. Empty until then.
VERSION=""

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

python_module_available() {
    local module="$1"
    "${PYTHON}" -c "import importlib.util, sys; sys.exit(0 if importlib.util.find_spec('${module}') else 1)" \
        > /dev/null 2>&1
}

git_output() {
    git "$@" 2> /dev/null || true
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

# Run a command and show its output only when it fails. Used where a stage
# delegates to another script whose own summary would be noise inside this
# one: the delegate's report matters when it fails and not otherwise.
run_quietly() {
    local output=""
    local status=0
    output="$("$@" 2>&1)" || status="$?"
    if [[ "${status}" -ne 0 ]]; then
        printf '%s\n' "${output}"
    fi
    return "${status}"
}

# Read the declared version from the canonical location. The library is
# imported rather than parsed, because that is what the release workflow
# does, and a version that the parser and the interpreter disagree about is
# a defect worth finding here.
declared_version() {
    "${PYTHON}" -c "import discretus; print(discretus.__version__)"
}

# ---------------------------------------------------------------------------
# The stages
# ---------------------------------------------------------------------------

stage_preflight() {
    # The repository has to be in a state where a tag would mean something:
    # on the release branch, with nothing uncommitted, and not behind the
    # remote. Each check is overridable by name, because a maintainer
    # rehearsing the sequence has a reason to skip one.
    local failures=0

    local branch
    branch="$(git_output rev-parse --abbrev-ref HEAD)"
    if [[ -z "${branch}" ]]; then
        note "this does not look like a git repository"
        return 1
    fi
    note "branch: ${branch}"
    if [[ "${branch}" != "${RELEASE_BRANCH}" ]]; then
        if [[ "${ALLOW_BRANCH}" -eq 1 ]]; then
            warn "releasing from ${branch} rather than ${RELEASE_BRANCH}"
        else
            note "a release is cut from ${RELEASE_BRANCH}, not from ${branch}"
            note "pass --allow-branch if that is deliberate"
            failures=1
        fi
    fi

    local dirty
    dirty="$(git_output status --porcelain)"
    if [[ -n "${dirty}" ]]; then
        if [[ "${ALLOW_DIRTY}" -eq 1 ]]; then
            warn "the working tree is not clean"
        else
            note "the working tree has uncommitted changes:"
            printf '%s\n' "${dirty}"
            note "pass --allow-dirty if that is deliberate"
            failures=1
        fi
    fi

    # Being behind the remote means the tag would miss commits that the
    # pipeline has already accepted. Being ahead is fine: those commits are
    # what is being released.
    local upstream
    upstream="$(git_output rev-parse --abbrev-ref --symbolic-full-name '@{upstream}')"
    if [[ -n "${upstream}" ]]; then
        local behind
        behind="$(git_output rev-list --count "HEAD..${upstream}")"
        if [[ -n "${behind}" ]] && [[ "${behind}" -gt 0 ]]; then
            note "the branch is ${behind} commits behind ${upstream}"
            note "run: git pull --ff-only"
            failures=1
        fi
    else
        warn "the branch has no upstream, so it cannot be compared to a remote"
    fi

    return "${failures}"
}

stage_version() {
    # Every declaration of the version agrees, and no tag claims it yet.
    # The quality gate already has this check, so it is delegated rather
    # than copied: one implementation cannot disagree with itself.
    if ! run_quietly "${SCRIPT_DIR}/lint.sh" --only version --no-color; then
        return 1
    fi

    VERSION="$(declared_version)"
    note "releasing version ${VERSION}"

    if [[ -n "$(git_output tag --list "v${VERSION}")" ]]; then
        note "the tag v${VERSION} already exists, so this version was released"
        note "raise the version first: scripts/bump_version.py patch"
        return 1
    fi
}

stage_changelog() {
    # The changelog has a section for this version, that section is not
    # empty, the comparison link exists, and the Unreleased section was
    # emptied. The release workflow checks all four, and a failure there
    # wastes a tag, so they are checked here first.
    local version="${VERSION}"
    if [[ -z "${version}" ]]; then
        version="$(declared_version)"
    fi

    VERSION="${version}" "${PYTHON}" - <<'PYCHANGELOG'
import os
import pathlib
import re
import sys

version = os.environ["VERSION"]
text = pathlib.Path("CHANGELOG.md").read_text(encoding="utf-8")

failures = []

heading = f"## [{version}]"
if heading not in text:
    failures.append(f"there is no {heading} section")
else:
    start = text.index(heading)
    end = text.find("\n## ", start + len(heading))
    if end < 0:
        end = text.find("\n[Unreleased]:", start)
    if end < 0:
        end = len(text)
    body = text[start + len(heading) : end]
    # The heading carries the date, so the first line is not content.
    body = body.split("\n", 1)[1] if "\n" in body else ""
    if not body.strip():
        failures.append(f"the {version} section is empty")

if f"[{version}]:" not in text:
    failures.append(f"there is no comparison link for {version}")

unreleased = re.search(
    r"## \[Unreleased\]\n(.*?)(?=\n## |\n\[Unreleased\]:)", text, re.S
)
if unreleased is None:
    failures.append("there is no Unreleased section")
else:
    remaining = unreleased.group(1).strip()
    placeholder = remaining.startswith("Nothing yet.")
    if remaining and not placeholder:
        failures.append(
            "the Unreleased section still has entries; they belong under "
            f"the {version} heading"
        )

if failures:
    for line in failures:
        print(f"  {line}")
    sys.exit(1)
print(f"the changelog documents {version} and Unreleased is empty")
PYCHANGELOG
}

stage_lint() {
    # The quality gate, in strict mode: a tool that is missing is a failure
    # here, unlike in everyday use, because a release must not skip a check
    # merely because the machine cutting it is incompletely set up.
    "${SCRIPT_DIR}/lint.sh" --strict --no-color
}

stage_tests() {
    # The suite, the docstring examples, the property based tests, the slow
    # tests, and the coverage floor. A release runs everything, including
    # the stages that everyday use leaves out.
    "${SCRIPT_DIR}/run_tests.sh" --all --no-color --min "${COVERAGE_MINIMUM}"
}

stage_docs() {
    # The strict documentation build, because the documentation is part of
    # the release: a reference that fails to build is a reference that will
    # not be published for this version.
    run_quietly "${SCRIPT_DIR}/build_docs.sh" --only strict,pages --no-color
}

stage_build() {
    # The source distribution and the wheel, built once. The directory is
    # cleared first, because the upload step of the workflow takes
    # everything it finds and a stale artifact from an earlier version is
    # the classic way to publish the wrong file.
    if ! python_module_available build; then
        note "the build frontend is not installed"
        note "  ${PYTHON} -m pip install build twine"
        return 1
    fi

    if [[ -d "${DIST_DIR}" ]]; then
        note "clearing ${DIST_DIR}"
        rm -rf -- "${DIST_DIR}"
    fi

    "${PYTHON}" -m build || return 1

    if python_module_available twine; then
        "${PYTHON}" -m twine check --strict "${DIST_DIR}"/* || return 1
    else
        warn "twine is absent, so the metadata was not checked strictly"
    fi

    # Record the digests. The workflow records them too, and a difference
    # between the two means the artifact was rebuilt rather than reused,
    # which defeats the point of building once.
    note "artifact digests:"
    "${PYTHON}" - <<'PYDIGEST'
import hashlib
import pathlib

for path in sorted(pathlib.Path("dist").iterdir()):
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    size = path.stat().st_size
    print(f"  {digest}  {size:>10}  {path.name}")
PYDIGEST

    # A wheel that is not universal would mean the build picked up a
    # platform or an interpreter constraint, which for a pure Python
    # library is always a mistake in the configuration.
    local wheel
    wheel="$(printf '%s\n' "${DIST_DIR}"/*.whl | head -n 1)"
    if [[ "${wheel}" != *"-py3-none-any.whl" ]]; then
        note "the wheel is not universal: ${wheel}"
        note "a pure Python library builds a py3-none-any wheel"
        return 1
    fi
    note "the wheel is universal"
}

stage_install() {
    # Install each artifact into a throwaway environment and exercise it.
    # This is the only stage that catches a packaging mistake, because
    # everything before it runs against the working tree, where a
    # subpackage missing from the distribution is still importable.
    if [[ ! -d "${DIST_DIR}" ]]; then
        note "nothing is built, so there is nothing to install"
        return 1
    fi

    mkdir -p -- "${VERIFY_DIR}"

    # The exercise is written to a file rather than piped in, so that the
    # installed package is imported from a working directory outside the
    # source tree. Piping it in would leave the current directory on the
    # import path, and the working copy would satisfy every import whether
    # or not the distribution carries it.
    local exercise="${VERIFY_DIR}/exercise.py"
    cat > "${exercise}" <<'PYEXERCISE'
"""Exercise an installed copy of the library from outside the source tree."""

import discretus
from discretus import __about__
from discretus.core import element, numeric, structure

print("  version: ", discretus.__version__)
print("  license: ", discretus.__license__)
print("  author:  ", discretus.__author__)
print("  position:", __about__.__position__)

# One routine from each layer, so that a subpackage missing from the
# distribution fails here rather than at some later import.
assert element.normalize_element(3) == 3
assert numeric.is_perfect_square(49) is True
assert structure.FiniteStructure is not None
print("  the installed package imports and runs")
PYEXERCISE

    local failures=0
    local artifact
    local environment
    for artifact in "${DIST_DIR}"/*.whl "${DIST_DIR}"/*.tar.gz; do
        if [[ ! -f "${artifact}" ]]; then
            continue
        fi
        heading "installing $(basename -- "${artifact}")"
        environment="${VERIFY_DIR}/env"
        rm -rf -- "${environment}"

        if ! "${PYTHON}" -m venv "${environment}"; then
            note "could not create a virtual environment"
            failures=1
            continue
        fi

        # A wheel is installed without touching an index at all, because
        # the library declares no runtime dependency and a wheel needs no
        # build step. A source distribution does need one: building it
        # fetches the build backend, so that install is allowed an index
        # and is the one step here that needs the network.
        local hermetic=0
        if [[ "${artifact}" == *.whl ]]; then
            hermetic=1
        fi

        if ! install_and_exercise \
            "${environment}" "${artifact}" "${exercise}" "${hermetic}"; then
            failures=1
        fi
        rm -rf -- "${environment}"
    done

    rm -rf -- "${VERIFY_DIR}"
    return "${failures}"
}

# Install one artifact into one environment and run the exercise in it. Kept
# separate so that the loop above reads as the sequence it is, and so that a
# failure at any step leaves the loop able to continue with the next
# artifact rather than aborting the stage.
install_and_exercise() {
    local environment="$1"
    local artifact="$2"
    local exercise="$3"
    local hermetic="${4:-0}"

    # Absolute, because the exercise runs with the working directory changed
    # and a relative path would stop resolving the moment it does.
    local interpreter="${REPOSITORY_ROOT}/${environment}/bin/python"
    local absolute_artifact="${REPOSITORY_ROOT}/${artifact}"
    local absolute_exercise="${REPOSITORY_ROOT}/${exercise}"

    if [[ ! -x "${interpreter}" ]]; then
        note "the environment has no interpreter at ${interpreter}"
        return 1
    fi

    # The installer that comes with the environment is good enough to
    # install a local file. Updating it needs the network, so a failure
    # here is reported and not fatal: an offline machine can still check
    # that the artifact installs and runs.
    if ! "${interpreter}" -m pip install --quiet --upgrade pip; then
        warn "could not update the installer, continuing with the bundled one"
    fi

    local options=(--quiet)
    if [[ "${hermetic}" -eq 1 ]]; then
        # The library declares no runtime dependency, which is the whole
        # point of the design, so installing a wheel needs no index.
        # Asking for none makes the check hermetic and would fail loudly if
        # a dependency were ever added without being noticed here.
        options+=(--no-index)
    fi

    if ! "${interpreter}" -m pip install "${options[@]}" \
        -- "${absolute_artifact}"; then
        if [[ "${hermetic}" -eq 1 ]]; then
            note "the wheel would not install without an index"
            note "either it is malformed, or it has gained a dependency"
        else
            note "the source distribution would not install"
            note "building one fetches the build backend, so this step"
            note "needs network access"
        fi
        return 1
    fi

    # Run from a directory that contains neither the source tree nor the
    # exercise, with both given as absolute paths, which is what keeps the
    # working copy off the import path.
    if ! (cd -- "${REPOSITORY_ROOT}/${environment}" \
        && "${interpreter}" "${absolute_exercise}"); then
        note "the installed package did not run"
        return 1
    fi

    if ! "${interpreter}" -m pip uninstall --quiet --yes discretus; then
        warn "the artifact would not uninstall cleanly"
    fi
}

# ---------------------------------------------------------------------------
# Tagging
# ---------------------------------------------------------------------------

create_tag() {
    # The tag is annotated, because the release workflow reads its name from
    # a ref that only an annotated tag guarantees to be stable in a shallow
    # clone, and because an annotated tag carries an author and a date.
    #
    # The usual route is scripts/bump_version.py, which raises the version
    # and creates this tag in one commit. This exists for the case where the
    # version was already raised and only the tag is missing.
    local version="${VERSION}"
    if [[ -z "${version}" ]]; then
        version="$(declared_version)"
    fi

    if [[ -n "$(git_output tag --list "v${version}")" ]]; then
        note "the tag v${version} already exists"
        return 0
    fi

    git tag --annotate "v${version}" --message "discretus ${version}"
    note "created the annotated tag v${version}"
}

push_tag() {
    # Pushing the tag starts the publishing workflow, and a version that
    # reached an index cannot be replaced, only superseded. The confirmation
    # is therefore explicit rather than a flag alone.
    local version="${VERSION}"
    if [[ -z "${version}" ]]; then
        version="$(declared_version)"
    fi

    local remote
    remote="$(git_output remote)"
    remote="${remote%%$'\n'*}"
    if [[ -z "${remote}" ]]; then
        fatal "there is no remote to push to"
    fi

    printf '\n'
    printf 'This pushes v%s to %s and starts the publishing workflow.\n' \
        "${version}" "${remote}"
    printf 'A published version cannot be replaced, only superseded.\n'
    printf 'Type the version to confirm: '
    local answer=""
    read -r answer
    if [[ "${answer}" != "${version}" ]]; then
        fatal "the confirmation did not match, nothing was pushed"
    fi

    git push "${remote}" "v${version}"
    note "pushed v${version}, the workflow takes it from here"
}

# ---------------------------------------------------------------------------
# Command line
# ---------------------------------------------------------------------------

usage() {
    cat <<'USAGE'
Drive a release up to the point where a person has to decide.

Usage:
  scripts/release.sh [options]

Stage selection:
  --only NAMES       run only these stages, comma separated
  --skip NAMES       run everything except these stages
  --list             print the stage names in the order they run

Actions after the stages pass:
  --tag              create the annotated tag for the declared version
  --push             create it and push it, which starts the publishing
                     workflow, after an explicit confirmation

Overrides, each of which reports that it was used:
  --allow-dirty      proceed with uncommitted changes
  --allow-branch     proceed from a branch other than the release branch
  --min N            the coverage floor the test stage enforces

Other:
  --dry-run          print the plan and change nothing
  --no-color         plain output, for a log file or a pipe
  -h, --help         print this text

Stages:
  preflight version changelog lint tests docs build install

Publishing never happens here. When every stage passes:
  scripts/bump_version.py minor
  git show
  git push --follow-tags
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
            --skip)
                [[ "$#" -ge 2 ]] || fatal "the --skip option needs a value"
                SKIP="$2"
                shift 2
                ;;
            --skip=*)
                SKIP="${1#--skip=}"
                shift
                ;;
            --tag)
                DO_TAG=1
                shift
                ;;
            --push)
                DO_TAG=1
                DO_PUSH=1
                shift
                ;;
            --allow-dirty)
                ALLOW_DIRTY=1
                shift
                ;;
            --allow-branch)
                ALLOW_BRANCH=1
                shift
                ;;
            --min)
                [[ "$#" -ge 2 ]] || fatal "the --min option needs a value"
                COVERAGE_MINIMUM="$2"
                shift 2
                ;;
            --dry-run)
                DRY_RUN=1
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

resolve_stages() {
    local name
    for name in "${ALL_STAGES[@]}"; do
        if [[ -n "${SELECTED}" ]] && ! in_list "${name}" "${SELECTED}"; then
            continue
        fi
        if [[ -n "${SKIP}" ]] && in_list "${name}" "${SKIP}"; then
            continue
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
        printf '\n%sthe release is not ready: %s%s\n' \
            "${RED}" "${FAILED[*]}" "${RESET}"
        printf '%s\n' \
            'Fix the failing stage and run it again on its own:' \
            "  scripts/release.sh --only ${FAILED[0]}"
        return 1
    fi

    local version="${VERSION}"
    if [[ -z "${version}" ]]; then
        version="$(declared_version)"
    fi

    printf '\n%severy stage passed, version %s is ready%s\n' \
        "${GREEN}" "${version}" "${RESET}"
    printf '\n%s\n' "What happens next, and where:"
    printf '%s\n' \
        "  1. Raise the version and tag it, here:" \
        "       scripts/bump_version.py patch" \
        "  2. Read what that did, here:" \
        "       git show" \
        "  3. Push, which is the only outward step:" \
        "       git push --follow-tags" \
        "  4. Everything after that happens in the release workflow:" \
        "       it rebuilds, installs on every platform, publishes to the" \
        "       test index, then to the real one through trusted publishing," \
        "       and creates the forge release. No index credential is" \
        "       stored anywhere, so there is nothing to configure here."
    return 0
}

print_plan() {
    local stages=()
    local line
    while IFS= read -r line; do
        stages+=("${line}")
    done < <(resolve_stages)

    heading "Plan"
    printf 'repository: %s\n' "${REPOSITORY_ROOT}"
    printf 'branch:     %s\n' "$(git_output rev-parse --abbrev-ref HEAD)"
    printf 'version:    %s\n' "$(declared_version)"
    printf 'stages:     %s\n' "${stages[*]}"
    printf 'tag:        %s\n' "$([[ "${DO_TAG}" -eq 1 ]] && echo yes || echo no)"
    printf 'push:       %s\n' "$([[ "${DO_PUSH}" -eq 1 ]] && echo yes || echo no)"
    printf '\nnothing was run, because --dry-run was given\n'
}

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

main() {
    parse_arguments "$@"
    configure_color

    if [[ -n "${SELECTED}" ]]; then
        validate_selection "${SELECTED}" "--only"
    fi
    if [[ -n "${SKIP}" ]]; then
        validate_selection "${SKIP}" "--skip"
    fi

    if [[ "${DRY_RUN}" -eq 1 ]]; then
        print_plan
        return 0
    fi

    local stages=()
    local line
    while IFS= read -r line; do
        stages+=("${line}")
    done < <(resolve_stages)

    if [[ "${#stages[@]}" -eq 0 ]]; then
        fatal "the selection leaves no stage to run"
    fi

    heading "Preparing a release of ${REPOSITORY_ROOT}"
    printf 'interpreter: %s (%s)\n' "${PYTHON}" "$("${PYTHON}" --version 2>&1)"
    printf 'stages:      %s\n' "${stages[*]}"

    local stage
    for stage in "${stages[@]}"; do
        heading "${stage}"
        run_stage "${stage}" "stage_${stage}"
    done

    local status=0
    summarise || status="$?"
    if [[ "${status}" -ne 0 ]]; then
        return "${status}"
    fi

    if [[ "${DO_TAG}" -eq 1 ]]; then
        create_tag
    fi
    if [[ "${DO_PUSH}" -eq 1 ]]; then
        push_tag
    fi

    return 0
}

main "$@"
