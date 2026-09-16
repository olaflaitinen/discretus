"""Rendering helpers that keep the textual output of the library uniform.

Every structure in the library prints through these helpers, so that the
same set prints identically whether it appears on its own, inside a
relation, or inside a Cayley table.
"""

from __future__ import annotations

from typing import Any, Iterable, List, Mapping, Optional, Sequence

from .element import element_repr

__all__ = [
    "format_set",
    "format_sequence",
    "format_mapping",
    "format_pairs",
    "truncate",
    "class_repr",
    "format_table",
    "sort_for_display",
]

#: Number of members shown before the rendering is abbreviated.
DEFAULT_LIMIT = 12


def sort_for_display(values: Iterable[Any]) -> List[Any]:
    """Return the values in a deterministic, human friendly order.

    Values that compare with one another keep their natural order. Mixed
    collections fall back to ordering by type name and then representation,
    which is stable across runs because it never depends on hash values.

    Example:
        >>> sort_for_display([3, 1, 2])
        [1, 2, 3]
        >>> sort_for_display(["b", 1, "a"])
        [1, 'a', 'b']
    """
    items = list(values)
    try:
        return sorted(items)
    except TypeError:
        return sorted(items, key=lambda item: (type(item).__name__, element_repr(item)))


def truncate(items: Sequence[str], limit: int = DEFAULT_LIMIT) -> List[str]:
    """Return at most ``limit`` renderings, with an ellipsis marker if cut.

    Example:
        >>> truncate(["1", "2", "3"], limit=2)
        ['1', '2', '...']
    """
    if limit <= 0 or len(items) <= limit:
        return list(items)
    return [*items[:limit], "..."]


def format_set(
    values: Iterable[Any],
    limit: int = DEFAULT_LIMIT,
    empty: str = "{}",
) -> str:
    """Render a collection in brace notation with sorted members.

    Example:
        >>> format_set([3, 1, 2])
        '{1, 2, 3}'
        >>> format_set([])
        '{}'
    """
    rendered = [element_repr(value) for value in sort_for_display(values)]
    if not rendered:
        return empty
    return "{" + ", ".join(truncate(rendered, limit)) + "}"


def format_sequence(
    values: Iterable[Any],
    limit: int = DEFAULT_LIMIT,
    brackets: str = "[]",
) -> str:
    """Render a sequence in its given order.

    Example:
        >>> format_sequence([3, 1, 2])
        '[3, 1, 2]'
        >>> format_sequence((1, 2), brackets="()")
        '(1, 2)'
    """
    opening, closing = brackets[0], brackets[1]
    rendered = [element_repr(value) for value in values]
    return opening + ", ".join(truncate(rendered, limit)) + closing


def format_pairs(pairs: Iterable[Any], limit: int = DEFAULT_LIMIT) -> str:
    """Render a set of ordered pairs.

    Example:
        >>> format_pairs([(1, 2), (1, 1)])
        '{(1, 1), (1, 2)}'
    """
    rendered = [
        "(" + ", ".join(element_repr(part) for part in pair) + ")"
        for pair in sort_for_display(pairs)
    ]
    if not rendered:
        return "{}"
    return "{" + ", ".join(truncate(rendered, limit)) + "}"


def format_mapping(mapping: Mapping[Any, Any], limit: int = DEFAULT_LIMIT) -> str:
    """Render a mapping with its keys in display order.

    Example:
        >>> format_mapping({"b": 2, "a": 1})
        '{a: 1, b: 2}'
    """
    keys = sort_for_display(mapping.keys())
    rendered = [f"{element_repr(key)}: {element_repr(mapping[key])}" for key in keys]
    if not rendered:
        return "{}"
    return "{" + ", ".join(truncate(rendered, limit)) + "}"


def class_repr(instance: Any, **fields: Any) -> str:
    """Return a constructor style representation of an object.

    Example:
        >>> class Thing: pass
        >>> class_repr(Thing(), size=3, name="x")
        "Thing(size=3, name='x')"
    """
    inner = ", ".join(f"{name}={value!r}" for name, value in fields.items())
    return f"{type(instance).__name__}({inner})"


def format_table(
    rows: Sequence[Sequence[Any]],
    header: Optional[Sequence[Any]] = None,
    separator: str = " | ",
) -> str:
    """Render a table with columns padded to a common width.

    Args:
        rows: The body of the table.
        header: Optional header row, underlined with dashes.
        separator: Text placed between two columns.

    Returns:
        The table as a newline separated string without a trailing newline.

    Example:
        >>> print(format_table([[1, 2], [30, 4]], header=["a", "b"]))
        a  | b
        ---+--
        1  | 2
        30 | 4
    """
    body = [[element_repr(cell) for cell in row] for row in rows]
    head = [element_repr(cell) for cell in header] if header is not None else None
    width_source = body + ([head] if head else [])
    if not width_source:
        return ""
    columns = max(len(row) for row in width_source)
    widths = [0] * columns
    for row in width_source:
        for index, cell in enumerate(row):
            widths[index] = max(widths[index], len(cell))

    def render(row: Sequence[str]) -> str:
        padded = [
            row[index].ljust(widths[index]) if index < len(row) else " " * widths[index]
            for index in range(columns)
        ]
        return separator.join(padded).rstrip()

    lines: List[str] = []
    if head is not None:
        lines.append(render(head))
        rule_separator = "".join(
            "+" if character.strip() else "-" for character in separator
        )
        lines.append(rule_separator.join("-" * width for width in widths))
    lines.extend(render(row) for row in body)
    return "\n".join(lines)
