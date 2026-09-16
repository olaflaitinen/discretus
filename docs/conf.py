# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Sphinx configuration for the discretus documentation.

The documentation is written in Markdown and rendered through MyST, so that
the sources read the same on the forge and on the documentation site. The
configuration is deliberately explicit: every extension is listed with the
reason it is present, and every option that changes rendered output carries
a comment, because a documentation build that behaves differently on a
contributor's laptop than in continuous integration wastes more time than
the configuration saves.

Build locally:

    make docs
    python -m http.server --directory _build/html

Build with warnings treated as errors, which is what the release check does:

    sphinx-build -b html -W --keep-going . _build/html
"""

from __future__ import annotations

import os
import sys
from datetime import date
from typing import Any, Dict, List

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
# The library is normally installed in editable mode before the build, which
# is what the documentation workflow does. Adding the repository root to the
# import path as well means the build also works in a checkout where the
# package was never installed, for instance on a first clone.
sys.path.insert(0, os.path.abspath(".."))

from discretus.__about__ import (  # noqa: E402
    __affiliation__,
    __author__,
    __documentation__,
    __summary__,
    __url__,
    __version__,
)

# ---------------------------------------------------------------------------
# Project information
# ---------------------------------------------------------------------------
project = "discretus"
author = __author__
copyright = f"2026, {__author__}"  # noqa: A001
project_copyright = copyright

# The short version is the one the theme prints next to the title, and the
# full version is the one the reader needs when reporting a defect. Both come
# from the package rather than being repeated here, so that a version bump
# never leaves the documentation stale.
version = ".".join(__version__.split(".")[:2])
release = __version__

# Used by the templates below and by the citation page.
affiliation = __affiliation__
project_summary = __summary__
build_date = date.today().isoformat()

# ---------------------------------------------------------------------------
# Extensions
# ---------------------------------------------------------------------------
extensions = [
    # Markdown support. The documentation sources are Markdown rather than
    # reStructuredText, so that the same files render correctly in the
    # repository browser.
    "myst_parser",
    # Pull docstrings out of the library, so that the API reference never
    # repeats a signature that the code could change.
    "sphinx.ext.autodoc",
    # Generate the per module stub pages that autodoc fills in.
    "sphinx.ext.autosummary",
    # Read the Google style docstring sections the project uses, namely
    # Args, Returns, Raises, Complexity, and Example.
    "sphinx.ext.napoleon",
    # Link to the standard library documentation for the types the library
    # accepts and returns.
    "sphinx.ext.intersphinx",
    # Render the doctest examples in the docstrings as verified examples,
    # and make them runnable through sphinx-build -b doctest.
    "sphinx.ext.doctest",
    # Link a documented object to the exact source line that defines it,
    # which matters for a library whose reference implementations are meant
    # to be read.
    "sphinx.ext.viewcode",
    # Render the mathematics. The documentation states theorems, so this is
    # not optional.
    "sphinx.ext.mathjax",
    # Report coverage of the API reference, so that a public routine cannot
    # be added without a documentation entry.
    "sphinx.ext.coverage",
    # Support the todo notes used while a section is being drafted, which
    # the release build turns off.
    "sphinx.ext.todo",
    # Add a copy button to every code block, so that an example can be run
    # without selecting it by hand.
    "sphinx_copybutton",
]

# ---------------------------------------------------------------------------
# Source files
# ---------------------------------------------------------------------------
source_suffix = {
    ".md": "markdown",
    ".rst": "restructuredtext",
}

master_doc = "index"
root_doc = "index"

exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    "requirements.txt",
]

# Files that are copied verbatim into the output, for instance the
# stylesheet and any image the tutorials reference.
html_static_path = ["_static"]
templates_path = ["_templates"]

language = "en"

# ---------------------------------------------------------------------------
# MyST configuration
# ---------------------------------------------------------------------------
# Only the extensions the documentation actually uses are enabled, so that a
# source file cannot come to depend on a syntax the forge renderer does not
# understand.
myst_enable_extensions = [
    # Dollar delimited mathematics, which the domain pages use to state
    # definitions and theorems.
    "dollarmath",
    # Amsmath environments for the multi line derivations in the tutorials.
    "amsmath",
    # Definition lists, used by the glossary and the option tables.
    "deflist",
    # Field lists, used by the metadata blocks at the top of the API pages.
    "fieldlist",
    # Admonitions written as fenced blocks, which keeps a note readable in
    # the raw Markdown.
    "colon_fence",
    # Smart quotes and dashes are deliberately NOT enabled, because the
    # project writes with plain punctuation and a transformation that
    # introduces a long dash would contradict the repository convention.
    "substitution",
    "tasklist",
    "linkify",
]

# Substitutions available in every page, so that the version and the contact
# address are written once.
myst_substitutions = {
    "version": release,
    "author": author,
    "affiliation": affiliation,
    "repository": __url__,
    "documentation": __documentation__,
    "summary": project_summary,
}

# Generate anchors for headings down to level three, so that the API pages
# can link to a specific routine.
myst_heading_anchors = 3

# Report a broken cross reference as a warning, which the release build
# turns into an error.
myst_all_links_external = False
myst_url_schemes = ("http", "https", "mailto", "ftp")

# ---------------------------------------------------------------------------
# Autodoc and autosummary
# ---------------------------------------------------------------------------
autosummary_generate = True
autosummary_imported_members = False

autodoc_default_options = {
    "members": True,
    "undoc-members": False,
    "show-inheritance": True,
    "member-order": "bysource",
    "exclude-members": "__weakref__,__dict__,__module__",
}

# Keep the signature in the description rather than in the heading, which
# reads better for the routines that take several keyword arguments.
autodoc_typehints = "description"
autodoc_typehints_description_target = "documented"
autodoc_typehints_format = "short"

# Do not evaluate default arguments at build time. The library has value
# types whose repr is long, and a preserved literal is more informative.
autodoc_preserve_defaults = True

# Class documentation comes from the class docstring, and the constructor
# arguments are documented there as well, which is the convention the
# library follows.
autoclass_content = "class"
autodoc_class_signature = "mixed"

autodoc_mock_imports: List[str] = [
    # The optional rendering backends are not installed in the
    # documentation environment, and the viz modules import them lazily, so
    # mocking them keeps the reference complete without pulling in a
    # plotting stack.
    "matplotlib",
    "graphviz",
]

# ---------------------------------------------------------------------------
# Napoleon
# ---------------------------------------------------------------------------
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = False
napoleon_use_ivar = True
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = True
napoleon_attr_annotations = True

# The project adds a Complexity section to its docstrings. Registering it
# here makes it render as a labelled admonition rather than as a stray
# paragraph, which is the single most useful piece of information in the
# reference for many routines.
napoleon_custom_sections = [
    ("Complexity", "params_style"),
    ("Mathematical background", "notes_style"),
    ("See also", "params_style"),
]

# ---------------------------------------------------------------------------
# Intersphinx
# ---------------------------------------------------------------------------
intersphinx_mapping: Dict[str, Any] = {
    "python": ("https://docs.python.org/3", None),
}
intersphinx_timeout = 10

# ---------------------------------------------------------------------------
# Doctest
# ---------------------------------------------------------------------------
# Every example in the documentation is executed, so an example that stops
# working fails the build rather than misleading a reader. The setup block
# is prepended to every doctest group, which keeps the examples free of
# repeated imports.
doctest_global_setup = """
from fractions import Fraction

import discretus
from discretus.config import set_config

# Keep the examples deterministic regardless of the environment.
set_config(default_seed=0, notation="ascii", strict_validation=True)
"""

doctest_test_doctest_blocks = "default"

# ---------------------------------------------------------------------------
# HTML output
# ---------------------------------------------------------------------------
html_theme = "furo"
html_title = f"discretus {release}"
html_short_title = "discretus"
html_last_updated_fmt = "%Y-%m-%d"
html_show_sourcelink = True
html_copy_source = True
html_show_sphinx = False
html_permalinks = True
html_permalinks_icon = "#"
html_css_files = ["custom.css"]

# The theme is configured for both colour schemes, because the library is
# read at a desk and in a lecture hall, and the second is usually dark.
html_theme_options: Dict[str, Any] = {
    "sidebar_hide_name": False,
    "navigation_with_keys": True,
    "top_of_page_buttons": ["view", "edit"],
    "source_repository": f"{__url__}/",
    "source_branch": "main",
    "source_directory": "docs/",
    "light_css_variables": {
        "color-brand-primary": "#1a4f8a",
        "color-brand-content": "#1a4f8a",
        "font-stack": "Inter, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif",
        "font-stack--monospace": "JetBrains Mono, SFMono-Regular, Menlo, monospace",
    },
    "dark_css_variables": {
        "color-brand-primary": "#8ab4f8",
        "color-brand-content": "#8ab4f8",
    },
    "footer_icons": [
        {
            "name": "Repository",
            "url": __url__,
            "class": "",
            "html": "",
        }
    ],
}

# ---------------------------------------------------------------------------
# LaTeX and manual page output
# ---------------------------------------------------------------------------
# The documentation site offers a PDF, which is built from these settings.
latex_engine = "pdflatex"
latex_elements: Dict[str, str] = {
    "papersize": "a4paper",
    "pointsize": "11pt",
    "figure_align": "htbp",
    "preamble": r"""
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{mathtools}
\setcounter{tocdepth}{2}
""",
}

latex_documents = [
    (
        root_doc,
        "discretus.tex",
        "discretus Documentation",
        author,
        "manual",
    )
]

man_pages = [(root_doc, "discretus", "discretus Documentation", [author], 1)]

# ---------------------------------------------------------------------------
# Warnings and quality
# ---------------------------------------------------------------------------
# Treat a missing reference as a warning so that the local build reports it,
# and let the workflow decide whether a warning fails the build. Anchors are
# not checked, because several external sites generate them dynamically.
nitpicky = False
nitpick_ignore: List[Any] = []

linkcheck_ignore = [
    # The badge endpoints redirect and rate limit, and they are not
    # documentation targets.
    r"https://img\.shields\.io/.*",
    # The archival identifier is a placeholder until the first deposition.
    r"https://doi\.org/10\.5281/zenodo\.0+",
]
linkcheck_retries = 2
linkcheck_timeout = 15
linkcheck_anchors = False

# Draft notes are visible locally and hidden in a release build, which the
# workflow signals with an environment variable.
todo_include_todos = os.environ.get("DISCRETUS_DOCS_DRAFT", "") == "1"

# Report the public objects that have no documentation entry.
coverage_show_missing_items = True
coverage_ignore_modules = [
    r"discretus\._version",
    r"discretus\.__main__",
]


def setup(app: Any) -> Dict[str, Any]:
    """Register the build metadata the templates and the citation page use.

    Args:
        app: The Sphinx application being configured.

    Returns:
        The extension metadata, declaring that the configuration is safe for
        both the parallel read and the parallel write phases.
    """
    app.add_config_value("affiliation", affiliation, "env")
    app.add_config_value("build_date", build_date, "env")
    return {
        "version": release,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
