# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Deterministic hashing for discrete structures.

Python randomizes the hash of strings between processes, which makes the
built-in hash unusable as a stable structural fingerprint. The helpers here
produce values that are identical across runs and across machines, which is
what canonical forms, caches on disk, and reproducible serialization need.
"""

from __future__ import annotations

import hashlib
from typing import Any, Iterable, Mapping

from .frozen import FrozenDict

__all__ = [
    "canonical_bytes",
    "stable_hash",
    "stable_digest",
    "combine_hashes",
    "hash_unordered",
]

#: Width of the integer returned by :func:`stable_hash`.
_MASK = (1 << 64) - 1


def canonical_bytes(value: Any) -> bytes:
    """Return a canonical byte encoding of a nested immutable value.

    The encoding is prefixed by a type tag, so that ``1``, ``"1"``, and
    ``(1,)`` never collide. Unordered containers are encoded by sorting the
    encodings of their members, which makes the result independent of
    iteration order.

    Example:
        >>> canonical_bytes(1)
        b'i:1'
        >>> canonical_bytes(frozenset({2, 1})) == canonical_bytes(frozenset({1, 2}))
        True
    """
    if value is None:
        return b"n:"
    if isinstance(value, bool):
        return b"b:1" if value else b"b:0"
    if isinstance(value, int):
        return b"i:" + str(value).encode("utf-8")
    if isinstance(value, float):
        return b"f:" + repr(value).encode("utf-8")
    if isinstance(value, str):
        return b"s:" + value.encode("utf-8")
    if isinstance(value, bytes):
        return b"y:" + value
    if isinstance(value, (frozenset, set)):
        parts = sorted(canonical_bytes(item) for item in value)
        return b"S:[" + b",".join(parts) + b"]"
    if isinstance(value, (tuple, list)):
        parts = [canonical_bytes(item) for item in value]
        return b"T:[" + b",".join(parts) + b"]"
    if isinstance(value, (Mapping, FrozenDict)):
        parts = sorted(
            canonical_bytes(key) + b"=" + canonical_bytes(item)
            for key, item in value.items()
        )
        return b"M:[" + b",".join(parts) + b"]"
    return b"o:" + repr(value).encode("utf-8")


def stable_digest(value: Any) -> str:
    """Return the hexadecimal SHA256 digest of the canonical encoding.

    Example:
        >>> stable_digest(()) == stable_digest([])
        True
        >>> len(stable_digest(1))
        64
    """
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def stable_hash(value: Any) -> int:
    """Return a 64 bit hash that is identical across processes.

    Example:
        >>> stable_hash("abc") == stable_hash("abc")
        True
        >>> stable_hash("abc") != stable_hash("abd")
        True
    """
    digest = hashlib.sha256(canonical_bytes(value)).digest()
    return int.from_bytes(digest[:8], "big") & _MASK


def combine_hashes(*values: int) -> int:
    """Combine hash values in an order sensitive way.

    Example:
        >>> combine_hashes(1, 2) != combine_hashes(2, 1)
        True
    """
    result = 0xCBF29CE484222325
    for value in values:
        result ^= value & _MASK
        result = (result * 0x100000001B3) & _MASK
    return result


def hash_unordered(values: Iterable[int]) -> int:
    """Combine hash values in an order insensitive way.

    Example:
        >>> hash_unordered([1, 2]) == hash_unordered([2, 1])
        True
    """
    total = 0
    product = 1
    count = 0
    for value in values:
        masked = value & _MASK
        total = (total + masked) & _MASK
        product = (product * (masked | 1)) & _MASK
        count += 1
    return combine_hashes(total, product, count)
