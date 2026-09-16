"""Mathematical and notational constants used across the library.

The module holds exact integer data where exactness matters, high precision
decimal expansions of the irrational constants that appear in closed forms,
and the notation tables shared by the parsers and the printers.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Dict, Final, Tuple

__all__ = [
    "GOLDEN_RATIO",
    "GOLDEN_RATIO_CONJUGATE",
    "SILVER_RATIO",
    "SQRT_TWO",
    "SQRT_FIVE",
    "EULER_MASCHERONI",
    "APERY",
    "CATALAN_CONSTANT",
    "DEFAULT_TOLERANCE",
    "SMALL_PRIMES",
    "MILLER_RABIN_DETERMINISTIC_BASES",
    "DETERMINISTIC_MILLER_RABIN_BOUND",
    "FIRST_FIBONACCI",
    "FIRST_CATALAN",
    "FIRST_BELL",
    "NOT",
    "AND",
    "OR",
    "IMPLIES",
    "IFF",
    "XOR",
    "NAND",
    "NOR",
    "TRUE_LITERAL",
    "FALSE_LITERAL",
    "ASCII_CONNECTIVES",
    "UNICODE_CONNECTIVES",
    "LATEX_CONNECTIVES",
    "LATEX_SET_SYMBOLS",
    "EMPTY_SET",
    "FORALL",
    "EXISTS",
]

# Irrational constants that appear in the closed forms this library reports.
GOLDEN_RATIO: Final[float] = 1.618033988749894848204586834365638117720309179805762862135
GOLDEN_RATIO_CONJUGATE: Final[float] = GOLDEN_RATIO - 1.0
SILVER_RATIO: Final[float] = 2.414213562373095048801688724209698078569671875376948073176
SQRT_TWO: Final[float] = 1.414213562373095048801688724209698078569671875376948073176
SQRT_FIVE: Final[float] = 2.236067977499789696409173668731276235440618359611525724270
EULER_MASCHERONI: Final[float] = 0.577215664901532860606512090082402431042159335939923598805
APERY: Final[float] = 1.202056903159594285399738161511449990764986292340498881792
CATALAN_CONSTANT: Final[float] = 0.915965594177219015054603514932384110774
#: Tolerance used when a routine has to compare inexact floating point values.
DEFAULT_TOLERANCE: Final[float] = 1e-12

#: Every prime below one hundred, used for fast trial division.
SMALL_PRIMES: Final[Tuple[int, ...]] = (
    2, 3, 5, 7, 11, 13, 17, 19, 23, 29,
    31, 37, 41, 43, 47, 53, 59, 61, 67, 71,
    73, 79, 83, 89, 97,
)

#: Witness bases that make the Miller Rabin test deterministic for every
#: input below :data:`DETERMINISTIC_MILLER_RABIN_BOUND`.
MILLER_RABIN_DETERMINISTIC_BASES: Final[Tuple[int, ...]] = (
    2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37,
)
DETERMINISTIC_MILLER_RABIN_BOUND: Final[int] = 3_317_044_064_679_887_385_961_981

FIRST_FIBONACCI: Final[Tuple[int, ...]] = (
    0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987,
)
FIRST_CATALAN: Final[Tuple[int, ...]] = (
    1, 1, 2, 5, 14, 42, 132, 429, 1430, 4862, 16796, 58786,
)
FIRST_BELL: Final[Tuple[int, ...]] = (
    1, 1, 2, 5, 15, 52, 203, 877, 4140, 21147, 115975,
)

# Canonical ASCII notation for the propositional connectives. The parser
# accepts the aliases listed in ``ASCII_CONNECTIVES`` as well.
NOT: Final[str] = "~"
AND: Final[str] = "&"
OR: Final[str] = "|"
IMPLIES: Final[str] = "->"
IFF: Final[str] = "<->"
XOR: Final[str] = "^"
NAND: Final[str] = "~&"
NOR: Final[str] = "~|"
TRUE_LITERAL: Final[str] = "T"
FALSE_LITERAL: Final[str] = "F"

#: Alternative spellings the lexer maps onto the canonical operators.
ASCII_CONNECTIVES: Final[Dict[str, str]] = {
    "~": NOT,
    "!": NOT,
    "not": NOT,
    "&": AND,
    "&&": AND,
    "and": AND,
    "|": OR,
    "||": OR,
    "or": OR,
    "->": IMPLIES,
    "=>": IMPLIES,
    "implies": IMPLIES,
    "<->": IFF,
    "<=>": IFF,
    "==": IFF,
    "iff": IFF,
    "^": XOR,
    "xor": XOR,
}

UNICODE_CONNECTIVES: Final[Dict[str, str]] = {
    NOT: "¬",
    AND: "∧",
    OR: "∨",
    IMPLIES: "→",
    IFF: "↔",
    XOR: "⊕",
    NAND: "⊼",
    NOR: "⊽",
}

LATEX_CONNECTIVES: Final[Dict[str, str]] = {
    NOT: r"\lnot ",
    AND: r"\land",
    OR: r"\lor",
    IMPLIES: r"\rightarrow",
    IFF: r"\leftrightarrow",
    XOR: r"\oplus",
    NAND: r"\uparrow",
    NOR: r"\downarrow",
}

LATEX_SET_SYMBOLS: Final[Dict[str, str]] = {
    "union": r"\cup",
    "intersection": r"\cap",
    "difference": r"\setminus",
    "symmetric_difference": r"\triangle",
    "subset": r"\subseteq",
    "proper_subset": r"\subset",
    "member": r"\in",
    "not_member": r"\notin",
    "empty": r"\emptyset",
    "power_set": r"\mathcal{P}",
    "cartesian": r"\times",
}

EMPTY_SET: Final[str] = "∅"
FORALL: Final[str] = "∀"
EXISTS: Final[str] = "∃"

#: One half as an exact rational, used by the probability helpers.
ONE_HALF: Final[Fraction] = Fraction(1, 2)
