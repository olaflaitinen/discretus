#!/usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Raise the project version everywhere it is declared, in one step.

Why this script exists
======================

The version string appears in nine places. Eight of them are ordinary text
substitutions that a version bump tool can express, and .bumpversion.cfg
lists all eight so that a single command reaches them. The remaining two
edits cannot be written as a substitution at all:

The ``__version_info__`` tuple in ``discretus/__about__.py`` holds the same
version as three integers rather than as a string. A search and replace
pattern cannot turn ``(1, 0, 0)`` into ``(1, 1, 0)`` without knowing how to
take a version apart.

The ``Unreleased`` section of ``CHANGELOG.md`` has to move under a new
heading that carries the new version and today's date, the placeholder
paragraph has to be restored above it, and the comparison links at the foot
of the file have to be rewritten so that the new version compares against
the previous one and ``Unreleased`` compares against the new one.

A release where those two edits are forgotten is a release where the tag and
the declared version disagree, or where the changelog documents nothing. The
release workflow refuses to publish in either case, which is the right
behaviour and a slow way to find out. This script does all of it at once,
checks the result, and stops before anything is pushed.

How it relates to the version bump tool
=======================================

When bump2version or its successor is installed, the eight substitutions are
delegated to it, so that .bumpversion.cfg stays the single description of
where the version lives and one tool makes those edits. When it is not
installed, this script performs the same substitutions itself, reading the
same configuration file. Either way the two edits above happen here, and the
result is identical. The tool is therefore a convenience rather than a
requirement, which matters because the version is bumped rarely and few
contributors keep it installed.

Usage
=====

    scripts/bump_version.py patch              1.0.0 becomes 1.0.1
    scripts/bump_version.py minor              1.0.0 becomes 1.1.0
    scripts/bump_version.py major              1.0.0 becomes 2.0.0
    scripts/bump_version.py --set 1.2.3        an explicit version
    scripts/bump_version.py minor --dry-run    show the plan and change nothing
    scripts/bump_version.py minor --no-commit  edit the files, commit nothing
    scripts/bump_version.py minor --date 2026-10-01

What it does not do
===================

It never pushes. The release workflow triggers on a pushed tag, and a
mistaken push cannot be recalled, so pushing is a separate deliberate step
that a person performs after reading the diff:

    git show
    git push --follow-tags

Exit status
===========

    0   the version was raised, or the plan was printed
    1   a precondition failed and nothing was changed
    2   the command line was wrong
"""

from __future__ import annotations

import argparse
import configparser
import datetime as dt
import pathlib
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple

# ---------------------------------------------------------------------------
# Locations
# ---------------------------------------------------------------------------

#: The repository root, derived from this file so that the script behaves the
#: same however it is invoked.
REPOSITORY_ROOT = pathlib.Path(__file__).resolve().parents[1]

#: The canonical declaration of the version. Every other occurrence is
#: derived from this one, and the release workflow reads this one too.
ABOUT_PATH = REPOSITORY_ROOT / "discretus" / "__about__.py"

#: The declaration of where else the version lives.
CONFIG_PATH = REPOSITORY_ROOT / ".bumpversion.cfg"

#: The changelog, whose Unreleased section this script moves.
CHANGELOG_PATH = REPOSITORY_ROOT / "CHANGELOG.md"

#: The forge address the comparison links are built from.
REPOSITORY_URL = "https://github.com/olaflaitinen/discretus"

#: The paragraph that stands in for an empty Unreleased section. It is
#: restored after the section is moved, so that the file never has an empty
#: heading and a contributor always sees where to add an entry.
UNRELEASED_PLACEHOLDER = (
    "Nothing yet. Changes accumulate here between releases, and the release\n"
    "process moves this section under a version heading with the date.\n"
)

#: The parts of a version, in the order a bump considers them.
PARTS = ("major", "minor", "patch")


# ---------------------------------------------------------------------------
# Versions
# ---------------------------------------------------------------------------


@dataclass(frozen=True, order=True)
class Version:
    """A semantic version, restricted to the three numeric components.

    The project publishes only release versions, so there is no pre release
    or build metadata to carry. Adding them later would mean extending this
    class and the pattern in .bumpversion.cfg together, which is the reason
    the restriction is stated here rather than assumed.

    Examples:
        >>> Version.parse("1.2.3")
        Version(major=1, minor=2, patch=3)
        >>> str(Version.parse("1.2.3").bump("minor"))
        '1.3.0'
        >>> str(Version.parse("1.2.3").bump("major"))
        '2.0.0'
        >>> Version.parse("1.0.0") < Version.parse("1.0.1")
        True
    """

    major: int
    minor: int
    patch: int

    @classmethod
    def parse(cls, text: str) -> "Version":
        """Return the version a string denotes.

        Args:
            text: The version, as three numbers separated by dots.

        Returns:
            The parsed version.

        Raises:
            ValueError: If the string is not three dot separated numbers.
        """
        match = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", text.strip())
        if match is None:
            raise ValueError(f"not a version: {text!r}")
        return cls(*(int(group) for group in match.groups()))

    def bump(self, part: str) -> "Version":
        """Return the version that raising one part produces.

        Raising a part resets the parts below it, which is what makes a
        minor release start at patch zero.

        Args:
            part: One of ``major``, ``minor``, or ``patch``.

        Returns:
            The raised version.

        Raises:
            ValueError: If the part is not one of the three.
        """
        if part == "major":
            return Version(self.major + 1, 0, 0)
        if part == "minor":
            return Version(self.major, self.minor + 1, 0)
        if part == "patch":
            return Version(self.major, self.minor, self.patch + 1)
        raise ValueError(f"not a version part: {part!r}")

    def __str__(self) -> str:
        """Return the dotted form, which is what every file carries."""
        return f"{self.major}.{self.minor}.{self.patch}"

    @property
    def tag(self) -> str:
        """Return the git tag for this version, which carries a v prefix."""
        return f"v{self}"

    @property
    def info_tuple(self) -> str:
        """Return the source text of the matching ``__version_info__``."""
        return f"({self.major}, {self.minor}, {self.patch})"


# ---------------------------------------------------------------------------
# Reading the current state
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Replacement:
    """One text substitution that a version bump has to make.

    Attributes:
        path: The file to edit, relative to the repository root.
        search: The text to find, with the current version already
            substituted in.
        replace: The text to put in its place.
        label: The configuration section this came from, used in reporting.
    """

    path: pathlib.Path
    search: str
    replace: str
    label: str


def read_current_version() -> Version:
    """Return the version declared in the canonical location.

    Returns:
        The current version.

    Raises:
        SystemExit: If the declaration is missing, since nothing else in
            this script can be meaningful without it.
    """
    text = ABOUT_PATH.read_text(encoding="utf-8")
    match = re.search(r'__version__ = "([^"]+)"', text)
    if match is None:
        fail(f"{ABOUT_PATH} does not declare __version__")
    return Version.parse(match.group(1))


def read_replacements(current: Version, new: Version) -> List[Replacement]:
    """Return the substitutions .bumpversion.cfg declares.

    The search and replace values in the configuration are format templates,
    so a literal brace in one of them is doubled. They are formatted rather
    than substituted by hand, which is what makes the citation example in
    the README, whose version sits inside braces, resolve to the text that
    is actually in the file.

    Args:
        current: The version now declared.
        new: The version to raise to.

    Returns:
        One replacement per configuration section, in file order.
    """
    config = configparser.RawConfigParser()
    config.read(CONFIG_PATH, encoding="utf-8")

    declared = config["bumpversion"]["current_version"]
    if declared != str(current):
        fail(
            f"{CONFIG_PATH.name} declares {declared} but "
            f"{ABOUT_PATH.name} declares {current}"
        )

    replacements: List[Replacement] = []
    for section in config.sections():
        if not section.startswith("bumpversion:file"):
            continue
        # A section is either bumpversion:file:PATH or, when one file needs
        # more than one replacement, bumpversion:file(label):PATH.
        name = section.split(":", 2)[-1]
        replacements.append(
            Replacement(
                path=REPOSITORY_ROOT / name,
                search=config[section]["search"].format(current_version=str(current)),
                replace=config[section]["replace"].format(new_version=str(new)),
                label=section,
            )
        )
    return replacements


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------


def note(message: str) -> None:
    """Print a progress line."""
    print(message)


def warn(message: str) -> None:
    """Print a warning to the error stream."""
    print(f"warning: {message}", file=sys.stderr)


def fail(message: str) -> "None":
    """Report a failed precondition and stop without changing anything.

    Args:
        message: What went wrong, phrased so that the remedy is obvious.

    Raises:
        SystemExit: Always, with status one.
    """
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(1)


# ---------------------------------------------------------------------------
# Git
# ---------------------------------------------------------------------------


def git(*arguments: str, check: bool = True) -> subprocess.CompletedProcess:
    """Run one git command in the repository and return the result.

    Args:
        *arguments: The command and its arguments, without the program name.
        check: Whether a non zero status raises.

    Returns:
        The completed process, with its output captured as text.
    """
    return subprocess.run(
        ["git", *arguments],
        cwd=REPOSITORY_ROOT,
        check=check,
        capture_output=True,
        text=True,
    )


def require_clean_worktree(allow_dirty: bool) -> None:
    """Refuse to bump a version on top of uncommitted work.

    A bump produces a commit and a tag that name a version, and a tag that
    points at a commit containing unrelated uncommitted work is not the
    release it claims to be. The check is skippable, because a maintainer
    who is rehearsing the sequence has a reason to.

    Args:
        allow_dirty: Whether to proceed anyway.
    """
    result = git("status", "--porcelain", check=False)
    if result.returncode != 0:
        warn("this does not look like a git repository")
        return
    if not result.stdout.strip():
        return
    if allow_dirty:
        warn("the working tree is not clean, continuing because of --allow-dirty")
        return
    print("the working tree has uncommitted changes:", file=sys.stderr)
    print(result.stdout.rstrip(), file=sys.stderr)
    fail("commit or stash them first, or pass --allow-dirty")


def require_tag_absent(version: Version) -> None:
    """Refuse to create a tag that already exists.

    A version that has been tagged has been released, and releasing it again
    under the same number is the one thing semantic versioning forbids
    outright.

    Args:
        version: The version about to be tagged.
    """
    result = git("tag", "--list", version.tag, check=False)
    if result.returncode == 0 and result.stdout.strip():
        fail(
            f"the tag {version.tag} already exists, so {version} has been "
            "released; choose the next version instead"
        )


# ---------------------------------------------------------------------------
# The substitutions
# ---------------------------------------------------------------------------


def verify_replacements(replacements: Sequence[Replacement]) -> None:
    """Check that every declared substitution will find its target.

    A search string that matches nothing is the failure mode of this whole
    mechanism: the bump appears to succeed, one file keeps the old version,
    and the release workflow rejects the tag much later. Checking first
    turns that into an error before anything is written.

    Args:
        replacements: The substitutions to check.
    """
    failures: List[str] = []
    for item in replacements:
        if not item.path.exists():
            failures.append(f"{item.path} is listed in the configuration and missing")
            continue
        if item.search not in item.path.read_text(encoding="utf-8"):
            failures.append(f"{item.path} does not contain {item.search!r}")

    if failures:
        for line in failures:
            print(f"  {line}", file=sys.stderr)
        fail("the version bump configuration does not match the files")


def apply_replacements(replacements: Sequence[Replacement]) -> List[pathlib.Path]:
    """Perform every declared substitution.

    Args:
        replacements: The substitutions to perform.

    Returns:
        The files that were changed, without duplicates and in the order
        they were first touched.
    """
    touched: List[pathlib.Path] = []
    for item in replacements:
        text = item.path.read_text(encoding="utf-8")
        updated = text.replace(item.search, item.replace)
        if updated != text:
            item.path.write_text(updated, encoding="utf-8")
            if item.path not in touched:
                touched.append(item.path)
            note(f"  {item.path.relative_to(REPOSITORY_ROOT)}: {item.label}")
    return touched


def bump_with_tool(part_or_version: str, explicit: bool) -> bool:
    """Delegate the substitutions to the version bump tool, if it is there.

    Args:
        part_or_version: The part to raise, or the explicit new version.
        explicit: Whether the argument is a version rather than a part.

    Returns:
        Whether the tool ran. False means it is not installed and the
        caller should perform the substitutions itself.
    """
    program = shutil.which("bump2version") or shutil.which("bumpversion")
    if program is None:
        return False

    arguments = [program, "--no-commit", "--no-tag", "--allow-dirty"]
    if explicit:
        arguments += ["--new-version", part_or_version, "patch"]
    else:
        arguments.append(part_or_version)

    note(f"delegating the substitutions to {pathlib.Path(program).name}")
    result = subprocess.run(
        arguments, cwd=REPOSITORY_ROOT, capture_output=True, text=True
    )
    if result.returncode != 0:
        print(result.stdout, file=sys.stderr)
        print(result.stderr, file=sys.stderr)
        fail("the version bump tool failed")
    return True


# ---------------------------------------------------------------------------
# The two edits no substitution can express
# ---------------------------------------------------------------------------


def rewrite_version_info(current: Version, new: Version) -> None:
    """Rewrite the ``__version_info__`` tuple to match the new version.

    Args:
        current: The version now declared, used to check the tuple agreed
            before the edit.
        new: The version to raise to.
    """
    text = ABOUT_PATH.read_text(encoding="utf-8")
    match = re.search(r"__version_info__ = \(([^)]*)\)", text)
    if match is None:
        fail(f"{ABOUT_PATH} does not declare __version_info__")

    existing = tuple(part.strip() for part in match.group(1).split(",") if part.strip())
    if ".".join(existing) != str(current):
        fail(
            f"__version_info__ is {match.group(0)} which does not agree "
            f"with the declared version {current}"
        )

    updated = text.replace(match.group(0), f"__version_info__ = {new.info_tuple}")
    ABOUT_PATH.write_text(updated, encoding="utf-8")
    note(f"  {ABOUT_PATH.relative_to(REPOSITORY_ROOT)}: __version_info__")


def rewrite_bumpversion_config(current: Version, new: Version) -> bool:
    """Raise the current version recorded in .bumpversion.cfg.

    The configuration records the version it is currently at, and that line
    is not one of the declared substitutions: the version bump tool updates
    its own configuration as part of a successful run. When the
    substitutions are performed here instead, nothing else would touch it,
    and a stale value makes every later version agreement check fail. This
    is therefore called on both paths and does nothing when the value is
    already current.

    Args:
        current: The version before the bump.
        new: The version after it.

    Returns:
        Whether the file was changed.
    """
    text = CONFIG_PATH.read_text(encoding="utf-8")
    needle = f"current_version = {current}"
    if needle not in text:
        return False
    CONFIG_PATH.write_text(
        text.replace(needle, f"current_version = {new}", 1), encoding="utf-8"
    )
    note(f"  {CONFIG_PATH.name}: current_version")
    return True


def split_changelog(text: str) -> Tuple[str, str, str]:
    """Split the changelog around the Unreleased section.

    Returns:
        The text before the Unreleased heading, the body of the Unreleased
        section, and the text from the next heading onwards.

    Raises:
        SystemExit: If the Unreleased heading is missing, since the release
            process depends on it.
    """
    heading = "## [Unreleased]"
    start = text.find(heading)
    if start < 0:
        fail(f"{CHANGELOG_PATH.name} has no {heading} heading")

    body_start = start + len(heading)
    next_heading = text.find("\n## ", body_start)
    if next_heading < 0:
        # The first release: there is no earlier version heading, so the
        # section runs to the link definitions at the foot of the file.
        next_heading = text.find("\n[Unreleased]:", body_start)
    if next_heading < 0:
        next_heading = len(text)

    return text[:body_start], text[body_start:next_heading], text[next_heading:]


def changelog_is_empty(body: str) -> bool:
    """Return whether the Unreleased section records nothing.

    The section is never literally empty: it carries a placeholder
    paragraph so that a contributor always sees where to add an entry. That
    paragraph, and nothing else, counts as empty.

    Args:
        body: The body of the Unreleased section.

    Examples:
        >>> changelog_is_empty("\\n\\n" + UNRELEASED_PLACEHOLDER)
        True
        >>> changelog_is_empty("\\n\\n### Added\\n\\n- A new routine.\\n")
        False
    """
    stripped = body.strip()
    return not stripped or stripped == UNRELEASED_PLACEHOLDER.strip()


def rewrite_changelog(current: Version, new: Version, release_date: dt.date) -> None:
    """Move the Unreleased section under a heading for the new version.

    Three edits happen together, because each one on its own would leave the
    file inconsistent: the section body moves under a new heading carrying
    the version and the date, the placeholder paragraph is restored under
    the Unreleased heading, and the comparison links at the foot of the file
    are rewritten so that Unreleased compares against the new version and
    the new version compares against the previous one.

    Args:
        current: The version being released from.
        new: The version being released.
        release_date: The date to record in the heading.
    """
    text = CHANGELOG_PATH.read_text(encoding="utf-8")
    before, body, after = split_changelog(text)

    moved = body if not changelog_is_empty(body) else "\n\nNo user visible changes.\n"
    moved = moved.strip("\n")

    rebuilt = (
        f"{before}\n\n{UNRELEASED_PLACEHOLDER}\n"
        f"## [{new}] - {release_date.isoformat()}\n\n"
        f"{moved}\n"
        f"{after}"
    )

    # The link definitions. The Unreleased comparison always ends at the
    # head of the default branch, and the new version compares against the
    # previous one, which is the form Keep a Changelog prescribes.
    unreleased_link = f"[Unreleased]: {REPOSITORY_URL}/compare/{new.tag}...HEAD"
    rebuilt = re.sub(
        r"^\[Unreleased\]: .*$",
        unreleased_link,
        rebuilt,
        count=1,
        flags=re.M,
    )

    new_link = f"[{new}]: {REPOSITORY_URL}/compare/{current.tag}...{new.tag}"
    if f"\n[{new}]:" not in rebuilt:
        rebuilt = rebuilt.replace(unreleased_link, f"{unreleased_link}\n{new_link}", 1)

    CHANGELOG_PATH.write_text(rebuilt, encoding="utf-8")
    note(f"  {CHANGELOG_PATH.name}: moved the Unreleased section under {new}")


# ---------------------------------------------------------------------------
# Committing
# ---------------------------------------------------------------------------


def commit_and_tag(
    current: Version,
    new: Version,
    files: Sequence[pathlib.Path],
    do_commit: bool,
    do_tag: bool,
) -> None:
    """Record the bump as a commit and an annotated tag.

    The message and the tag name come from .bumpversion.cfg, so that a bump
    performed through the tool and a bump performed through this script are
    indistinguishable in the history.

    Nothing is pushed. The release workflow triggers on a pushed tag, and a
    mistaken push cannot be recalled, so the push is left to a person who
    has read the diff.

    Args:
        current: The version before the bump.
        new: The version after it.
        files: The files to stage.
        do_commit: Whether to commit at all.
        do_tag: Whether to create the tag.
    """
    if not do_commit:
        note("nothing was committed, because --no-commit was given")
        note("review the changes with: git diff")
        return

    config = configparser.RawConfigParser()
    config.read(CONFIG_PATH, encoding="utf-8")
    section = config["bumpversion"]
    message = section.get(
        "message", "chore(release): bump version to {new_version}"
    ).format(current_version=str(current), new_version=str(new))
    tag_message = section.get("tag_message", "discretus {new_version}").format(
        current_version=str(current), new_version=str(new)
    )

    relative = [str(path.relative_to(REPOSITORY_ROOT)) for path in files]
    git("add", "--", *relative)
    git("commit", "--message", message)
    note(f"committed: {message}")

    if not do_tag:
        note("no tag was created, because --no-tag was given")
        return

    # An annotated tag rather than a lightweight one, because it carries the
    # author, the date, and a message, and because the release workflow
    # reads the tag name from a ref that only an annotated tag guarantees to
    # be stable in a shallow clone.
    git("tag", "--annotate", new.tag, "--message", tag_message)
    note(f"tagged: {new.tag}")


# ---------------------------------------------------------------------------
# The plan
# ---------------------------------------------------------------------------


def print_plan(
    current: Version,
    new: Version,
    replacements: Sequence[Replacement],
    release_date: dt.date,
) -> None:
    """Print what the bump would change, without changing anything.

    Args:
        current: The version now declared.
        new: The version to raise to.
        replacements: The declared substitutions.
        release_date: The date that would be recorded.
    """
    print(f"current version: {current}")
    print(f"new version:     {new}")
    print(f"tag:             {new.tag}")
    print(f"release date:    {release_date.isoformat()}")
    print()
    print(f"{len(replacements)} text substitutions:")
    for item in replacements:
        print(f"  {item.path.relative_to(REPOSITORY_ROOT)}")
        print(f"    {item.search}")
        print(f"    {item.replace}")
    print()
    print("two edits no substitution can express:")
    print(f"  {ABOUT_PATH.relative_to(REPOSITORY_ROOT)}")
    print(f"    __version_info__ = {current.info_tuple}")
    print(f"    __version_info__ = {new.info_tuple}")
    print(f"  {CHANGELOG_PATH.name}")
    print(f"    the Unreleased section moves under [{new}]")
    print(f"    [Unreleased] compares against {new.tag}")
    print(f"    [{new}] compares {current.tag} against {new.tag}")

    text = CHANGELOG_PATH.read_text(encoding="utf-8")
    _, body, _ = split_changelog(text)
    if changelog_is_empty(body):
        print()
        print("the Unreleased section records nothing yet")


# ---------------------------------------------------------------------------
# Command line
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    """Return the command line parser.

    Returns:
        The parser, with the part argument and the explicit version option
        declared as alternatives, because giving both is contradictory.
    """
    parser = argparse.ArgumentParser(
        prog="scripts/bump_version.py",
        description=(
            "Raise the project version in every file that declares it, "
            "rewrite the version tuple, and move the changelog section."
        ),
        epilog=(
            "Nothing is pushed. After reading the diff, publish with: "
            "git push --follow-tags"
        ),
    )
    parser.add_argument(
        "part",
        nargs="?",
        choices=PARTS,
        help="the part of the version to raise",
    )
    parser.add_argument(
        "--set",
        dest="explicit",
        metavar="VERSION",
        help="set an explicit version instead of raising a part",
    )
    parser.add_argument(
        "--date",
        metavar="YYYY-MM-DD",
        help="the release date to record, defaulting to today",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="print the plan and change nothing",
    )
    parser.add_argument(
        "--no-commit",
        action="store_true",
        help="edit the files but do not commit or tag",
    )
    parser.add_argument(
        "--no-tag",
        action="store_true",
        help="commit but do not create the tag",
    )
    parser.add_argument(
        "--allow-dirty",
        action="store_true",
        help="proceed even though the working tree has uncommitted changes",
    )
    parser.add_argument(
        "--allow-empty-changelog",
        action="store_true",
        help="release even though the Unreleased section records nothing",
    )
    parser.add_argument(
        "--no-tool",
        action="store_true",
        help="perform the substitutions here rather than delegating them",
    )
    return parser


def resolve_target(
    current: Version, part: Optional[str], explicit: Optional[str]
) -> Version:
    """Return the version to raise to, from the command line arguments.

    Args:
        current: The version now declared.
        part: The part to raise, if one was named.
        explicit: The explicit version, if one was given.

    Returns:
        The new version.

    Raises:
        SystemExit: If neither or both were given, or if the explicit
            version is not greater than the current one.
    """
    if part is not None and explicit is not None:
        fail("give either a part or --set, not both")
    if part is None and explicit is None:
        fail("give a part to raise, one of: " + ", ".join(PARTS))

    if explicit is not None:
        try:
            new = Version.parse(explicit)
        except ValueError as error:
            fail(str(error))
        if new <= current:
            fail(
                f"{new} is not greater than the current version {current}; "
                "a version is never reused or lowered"
            )
        return new

    assert part is not None
    return current.bump(part)


def resolve_date(text: Optional[str]) -> dt.date:
    """Return the release date to record.

    Args:
        text: The date in ISO form, or None for today.

    Returns:
        The date.

    Raises:
        SystemExit: If the text is not an ISO date.
    """
    if text is None:
        return dt.date.today()
    try:
        return dt.date.fromisoformat(text)
    except ValueError:
        fail(f"not a date in the form YYYY-MM-DD: {text!r}")
    raise AssertionError("unreachable")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Raise the version, or print the plan.

    Args:
        argv: The command line arguments, defaulting to the real ones.

    Returns:
        A process exit status.
    """
    arguments = build_parser().parse_args(argv)

    current = read_current_version()
    new = resolve_target(current, arguments.part, arguments.explicit)
    release_date = resolve_date(arguments.date)
    replacements = read_replacements(current, new)

    if arguments.dry_run:
        print_plan(current, new, replacements, release_date)
        return 0

    require_clean_worktree(arguments.allow_dirty)
    require_tag_absent(new)
    verify_replacements(replacements)

    _, body, _ = split_changelog(CHANGELOG_PATH.read_text(encoding="utf-8"))
    if changelog_is_empty(body) and not arguments.allow_empty_changelog:
        fail(
            "the Unreleased section of the changelog records nothing, so "
            "this release would document no change; add the entries, or "
            "pass --allow-empty-changelog"
        )

    note(f"raising {current} to {new}")

    touched: List[pathlib.Path] = []
    if arguments.no_tool or not bump_with_tool(
        str(new) if arguments.explicit else str(arguments.part),
        explicit=arguments.explicit is not None,
    ):
        touched = apply_replacements(replacements)
    else:
        touched = [item.path for item in replacements]

    rewrite_version_info(current, new)
    if ABOUT_PATH not in touched:
        touched.append(ABOUT_PATH)

    if rewrite_bumpversion_config(current, new):
        touched.append(CONFIG_PATH)

    rewrite_changelog(current, new, release_date)
    touched.append(CHANGELOG_PATH)

    # Read the result back rather than trusting the edits. Every file that
    # was supposed to change now has to contain the new version, and the
    # canonical declaration has to agree with the tuple beside it.
    declared = read_current_version()
    if declared != new:
        fail(f"after the edits the declared version is {declared}, not {new}")

    recorded = configparser.RawConfigParser()
    recorded.read(CONFIG_PATH, encoding="utf-8")
    if recorded["bumpversion"]["current_version"] != str(new):
        fail(
            f"{CONFIG_PATH.name} still records "
            f"{recorded['bumpversion']['current_version']} after the edits"
        )

    commit_and_tag(
        current,
        new,
        touched,
        do_commit=not arguments.no_commit,
        do_tag=not arguments.no_tag,
    )

    note("")
    note("Read the result before publishing it:")
    note("  git show")
    note("  git push --follow-tags")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
