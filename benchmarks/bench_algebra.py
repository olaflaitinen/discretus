# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Benchmarks for the abstract algebra package.

The distinguishing cost in this package is axiom verification. A structure
here checks its axioms when it is constructed, which means that building a
group of order n performs a cubic number of operation evaluations before it
returns, and every routine afterwards is free to assume associativity, an
identity, and inverses. That trade is the central design decision of the
package, and the first group of benchmarks is what makes its price visible.

What is measured, and why:

    Construction with and without verification, so that the cost of the
    guarantee is a number rather than an assertion. The reference documents
    a flag that skips the check, and a reader deciding whether to use it
    deserves to know what it saves.

    The individual axioms, because they differ: closure is quadratic in the
    carrier, associativity is cubic, and the identity search is quadratic.
    Knowing which dominates tells a contributor where to optimize.

    Subgroup enumeration, because it is exponential in general and is pruned
    by Lagrange's theorem, and because the pruning is the difference between
    a usable routine and an unusable one.

    Group actions, because the orbit stabilizer computation is the group
    order times the point count, which is a bound the Polya machinery in
    the combinatorics package inherits.

    Exact linear algebra, because a determinant over the rationals grows its
    intermediate numerators and a fraction free elimination is the reason
    the cost stays cubic in the dimension rather than worse.

    Polynomial arithmetic, because multiplication is quadratic in the
    degree, division is the quotient degree times the divisor degree, and
    the greatest common divisor repeats the division, so the three should
    separate cleanly in the growth report.

    Finite field arithmetic, because every multiplication is a polynomial
    multiplication followed by a reduction, and the cost therefore depends
    on the extension degree rather than on the field order.

Structures are built at orders rather than at bit lengths, because the cost
here is governed by the carrier size. The orders are kept small on purpose:
a group of order one hundred already costs a million operation evaluations
to verify.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Any, List, Optional, Tuple

from . import benchmark, require, seeded

# ---------------------------------------------------------------------------
# The modules under measurement
# ---------------------------------------------------------------------------

groups_module = require(
    "discretus.algebra.groups", "CyclicGroup", "SymmetricGroup", "GroupAction"
)
rings_module = require("discretus.algebra.rings", "Zmod")
fields_module = require("discretus.algebra.fields", "PrimeField", "GaloisField")
polynomials_module = require(
    "discretus.algebra.polynomials", "Polynomial", "interpolate", "gcd"
)
linear_module = require("discretus.algebra.linear", "Matrix", "determinant", "rank")
lattice_module = require("discretus.algebra.lattice", "BooleanAlgebra")

#: The core layer is available before the algebra package is filled in, so
#: the benchmarks that measure the shared machinery run today.
core_operation_module = require("discretus.core.operation", "BinaryOperation")
core_algebraic_module = require(
    "discretus.core.algebraic_base", "GroupBase", "RingBase"
)
core_matrix_module = require("discretus.core.matrix_base", "MatrixBase")
core_polynomial_module = require("discretus.core.polynomial_base", "PolynomialBase")

GROUP_GROUPS = "algebra.groups"
GROUP_ACTIONS = "algebra.actions"
GROUP_RINGS = "algebra.rings"
GROUP_FIELDS = "algebra.fields"
GROUP_POLYNOMIALS = "algebra.polynomials"
GROUP_LINEAR = "algebra.linear"
GROUP_LATTICE = "algebra.lattice"
GROUP_CORE = "algebra.core"


# ---------------------------------------------------------------------------
# Input preparation
# ---------------------------------------------------------------------------


def make_cyclic_group(order: int) -> Any:
    """Return a cyclic group of the given order."""
    assert groups_module is not None
    return groups_module.CyclicGroup(order)


def make_symmetric_group(letters: int) -> Any:
    """Return a symmetric group on the given number of letters.

    The letter count is small because the order is its factorial, and the
    verification cost is cubic in the order.
    """
    assert groups_module is not None
    return groups_module.SymmetricGroup(letters)


def make_dihedral_group(sides: int) -> Any:
    """Return the symmetry group of a regular polygon."""
    assert groups_module is not None
    return groups_module.DihedralGroup(sides)


def make_modular_ring(modulus: int) -> Any:
    """Return the ring of integers modulo a value."""
    assert rings_module is not None
    return rings_module.Zmod(modulus)


def make_prime_field(order: int) -> Optional[Any]:
    """Return a prime field of an order at least the requested value."""
    if fields_module is None:
        return None
    candidate = order | 1
    while True:
        if all(candidate % divisor for divisor in range(3, int(candidate**0.5) + 1, 2)):
            break
        candidate += 2
    return fields_module.PrimeField(candidate)


def make_galois_field(degree: int) -> Optional[Any]:
    """Return the binary field extension of the given degree."""
    if fields_module is None:
        return None
    return fields_module.GaloisField(2, degree)


def make_polynomial(degree: int) -> Any:
    """Return a dense polynomial with exact coefficients."""
    assert polynomials_module is not None
    source = seeded(f"algebra.polynomial.{degree}")
    return polynomials_module.Polynomial(
        [source.randint(-50, 50) or 1 for _ in range(degree + 1)]
    )


def make_two_polynomials(degree: int) -> Tuple[Any, Any]:
    """Return two polynomials, the second of roughly half the degree."""
    assert polynomials_module is not None
    source = seeded(f"algebra.polynomial_pair.{degree}")
    left = polynomials_module.Polynomial(
        [source.randint(-50, 50) or 1 for _ in range(degree + 1)]
    )
    right = polynomials_module.Polynomial(
        [source.randint(-50, 50) or 1 for _ in range(degree // 2 + 1)]
    )
    return left, right


def make_core_polynomial(degree: int) -> Any:
    """Return a core layer polynomial, measurable before the package exists."""
    assert core_polynomial_module is not None
    source = seeded(f"algebra.core_polynomial.{degree}")
    return core_polynomial_module.PolynomialBase(
        [source.randint(-50, 50) or 1 for _ in range(degree + 1)]
    )


def make_two_core_polynomials(degree: int) -> Tuple[Any, Any]:
    """Return two core layer polynomials for the division benchmarks."""
    assert core_polynomial_module is not None
    source = seeded(f"algebra.core_pair.{degree}")
    left = core_polynomial_module.PolynomialBase(
        [source.randint(-50, 50) or 1 for _ in range(degree + 1)]
    )
    right = core_polynomial_module.PolynomialBase(
        [source.randint(-50, 50) or 1 for _ in range(degree // 2 + 1)]
    )
    return left, right


def make_matrix(size: int) -> Any:
    """Return a square matrix with small integer entries.

    Small entries matter for an exact computation: elimination multiplies
    the entries together, so a matrix of large integers would measure the
    integer arithmetic rather than the elimination.
    """
    assert linear_module is not None
    source = seeded(f"algebra.matrix.{size}")
    rows = [[source.randint(-9, 9) for _ in range(size)] for _ in range(size)]
    return linear_module.Matrix(rows)


def make_rational_matrix(size: int) -> Any:
    """Return a square matrix with exact rational entries."""
    assert linear_module is not None
    source = seeded(f"algebra.rational_matrix.{size}")
    rows = [
        [Fraction(source.randint(-9, 9), source.randint(1, 9)) for _ in range(size)]
        for _ in range(size)
    ]
    return linear_module.Matrix(rows)


def make_core_matrix(size: int) -> Any:
    """Return a core layer matrix, measurable before the package exists."""
    assert core_matrix_module is not None
    source = seeded(f"algebra.core_matrix.{size}")
    rows = [[source.randint(-9, 9) for _ in range(size)] for _ in range(size)]
    return core_matrix_module.MatrixBase(rows)


def make_fibonacci_matrix(exponent: int) -> Tuple[Any, int]:
    """Return the Fibonacci matrix together with the exponent to raise it to.

    Both are returned because the benchmark has to use the size. A benchmark
    that ignored it would report a flat curve for a trivial reason rather
    than because the routine is logarithmic in the exponent, which is the
    claim being checked.
    """
    assert core_matrix_module is not None
    return core_matrix_module.MatrixBase([[1, 1], [1, 0]]), exponent


def make_boolean_lattice(size: int) -> Optional[Any]:
    """Return the Boolean algebra on the given number of atoms."""
    if lattice_module is None:
        return None
    return lattice_module.BooleanAlgebra.on_atoms(range(size))


def make_action(letters: int) -> Optional[Tuple[Any, Any]]:
    """Return a symmetric group acting on the subsets of its letters."""
    if groups_module is None:
        return None
    from itertools import combinations

    group = groups_module.SymmetricGroup(letters)
    points = [
        frozenset(chosen)
        for size in range(letters + 1)
        for chosen in combinations(range(letters), size)
    ]
    action = groups_module.GroupAction(
        group=group,
        points=points,
        action=lambda permutation, subset: frozenset(
            permutation[index] for index in subset
        ),
    )
    return group, action


# ---------------------------------------------------------------------------
# Axiom verification
# ---------------------------------------------------------------------------


@benchmark(
    group=GROUP_GROUPS,
    sizes=[20, 40, 80],
    complexity="O(n cubed) operation evaluations",
    requires=groups_module,
    note=(
        "construction with verification, which is the default; the cubic "
        "term is associativity"
    ),
)
def cyclic_group_verified(order: int) -> Any:
    """Build a cyclic group with its axioms verified."""
    return groups_module.CyclicGroup(order)


@benchmark(
    group=GROUP_GROUPS,
    sizes=[20, 40, 80],
    complexity="O(n) with no verification",
    requires=groups_module,
    note=(
        "the same construction with the check skipped; the ratio against the "
        "benchmark above is what the guarantee costs, and the reference says "
        "to skip it only when the axioms are already established"
    ),
)
def cyclic_group_unverified(order: int) -> Any:
    """Build a cyclic group without verifying its axioms."""
    return groups_module.CyclicGroup(order, verify=False)


@benchmark(
    group=GROUP_CORE,
    sizes=[20, 40, 80],
    complexity="O(n squared) operation evaluations",
    requires=core_operation_module,
    note="closure alone, which is quadratic in the carrier",
)
def core_verify_closure(order: int) -> None:
    """Verify closure of addition modulo a value."""
    operation = core_operation_module.BinaryOperation(
        range(order), lambda a, b: (a + b) % order, symbol="+", check_closure=False
    )
    return operation.verify_closure()


@benchmark(
    group=GROUP_CORE,
    sizes=[10, 20, 40],
    complexity="O(n cubed) operation evaluations",
    requires=core_operation_module,
    note=(
        "associativity alone, which is the cubic term and therefore the "
        "dominant cost of every structure in the package"
    ),
)
def core_verify_associativity(order: int) -> bool:
    """Verify associativity of addition modulo a value."""
    operation = core_operation_module.BinaryOperation(
        range(order), lambda a, b: (a + b) % order, symbol="+", check_closure=False
    )
    return operation.is_associative()


@benchmark(
    group=GROUP_CORE,
    sizes=[20, 40, 80],
    complexity="O(n squared) operation evaluations",
    requires=core_operation_module,
)
def core_identity_search(order: int) -> Any:
    """Find the two sided identity of an operation."""
    operation = core_operation_module.BinaryOperation(
        range(order), lambda a, b: (a + b) % order, symbol="+", check_closure=False
    )
    return operation.identity()


@benchmark(
    group=GROUP_CORE,
    sizes=[20, 40, 80],
    complexity="O(n squared) operation evaluations",
    requires=core_operation_module,
)
def core_inverse_table(order: int) -> Any:
    """Compute the inverse of every member of a carrier."""
    operation = core_operation_module.BinaryOperation(
        range(order), lambda a, b: (a + b) % order, symbol="+"
    )
    return operation.inverses()


@benchmark(
    group=GROUP_CORE,
    sizes=[20, 40, 80],
    complexity="O(n squared)",
    requires=core_operation_module,
    note="the Latin square test, a cheap necessary condition for a group",
)
def core_latin_square(order: int) -> bool:
    """Test whether a Cayley table is a Latin square."""
    operation = core_operation_module.BinaryOperation(
        range(order), lambda a, b: (a + b) % order, symbol="+"
    )
    return operation.is_latin_square()


@benchmark(
    group=GROUP_CORE,
    sizes=[10, 20, 40],
    complexity="O(n cubed)",
    requires=core_algebraic_module,
    note="the full group verification through the core hierarchy",
)
def core_group_base(order: int) -> Any:
    """Build a group through the core hierarchy, verifying every axiom."""
    return core_algebraic_module.GroupBase(
        list(range(order)), lambda a, b: (a + b) % order, symbol="+"
    )


@benchmark(
    group=GROUP_CORE,
    sizes=[6, 10, 14],
    complexity="O(n cubed) including distributivity",
    requires=core_algebraic_module,
    note="ring verification, which adds distributivity in both directions",
)
def core_ring_base(order: int) -> Any:
    """Build a ring through the core hierarchy, verifying every axiom."""
    return core_algebraic_module.RingBase(
        list(range(order)),
        lambda a, b: (a + b) % order,
        lambda a, b: (a * b) % order,
    )


# ---------------------------------------------------------------------------
# Group structure
# ---------------------------------------------------------------------------


@benchmark(
    group=GROUP_GROUPS,
    sizes=[60, 120, 240],
    complexity="O(n) operation applications per element",
    setup=make_cyclic_group,
    requires=groups_module,
)
def element_orders(group: Any) -> Any:
    """Compute the order of every element of a group."""
    return group.element_orders()


@benchmark(
    group=GROUP_GROUPS,
    sizes=[24, 48, 96],
    complexity="exponential in general, pruned by Lagrange",
    setup=make_cyclic_group,
    requires=groups_module,
    note=(
        "only divisors of the group order need be considered, which is the "
        "pruning that makes the search tractable at all"
    ),
)
def subgroup_enumeration(group: Any) -> List[Any]:
    """Enumerate every subgroup of a group."""
    return group.subgroups()


@benchmark(
    group=GROUP_GROUPS,
    sizes=[24, 48, 96],
    complexity="O(n) per coset",
    setup=make_cyclic_group,
    requires=groups_module,
    note="the coset decomposition, which is the proof of Lagrange's theorem",
)
def coset_decomposition(group: Any) -> Any:
    """Decompose a group into the cosets of a subgroup."""
    subgroup = group.subgroups()[1]
    return group.cosets(subgroup, side="left")


@benchmark(
    group=GROUP_GROUPS,
    sizes=[4, 5, 6],
    complexity="O(n squared) conjugations",
    setup=make_symmetric_group,
    requires=groups_module,
    note=(
        "in a symmetric group the classes are the cycle types, and the group "
        "order is the factorial of the letter count"
    ),
)
def conjugacy_classes(group: Any) -> Any:
    """Compute the conjugacy classes of a group."""
    return group.conjugacy_classes()


@benchmark(
    group=GROUP_GROUPS,
    sizes=[4, 5, 6],
    complexity="O(n squared)",
    setup=make_symmetric_group,
    requires=groups_module,
)
def centre(group: Any) -> Any:
    """Compute the centre of a group."""
    return group.center()


@benchmark(
    group=GROUP_GROUPS,
    sizes=[8, 12, 16],
    complexity="exponential in general",
    setup=make_dihedral_group,
    requires=groups_module,
)
def normal_subgroups(group: Any) -> Any:
    """Find the normal subgroups of a group."""
    return group.normal_subgroups()


@benchmark(
    group=GROUP_GROUPS,
    sizes=[8, 12, 16],
    complexity="exponential in general",
    setup=make_dihedral_group,
    requires=groups_module,
    note="Sylow theory, which says which subgroup orders must occur",
)
def sylow_subgroups(group: Any) -> Any:
    """Find the Sylow two subgroups of a group."""
    return group.sylow_subgroups(2)


@benchmark(
    group=GROUP_GROUPS,
    sizes=[40, 80, 160],
    complexity="O(n squared)",
    setup=make_cyclic_group,
    requires=groups_module,
    note="the Cayley table, which is the whole structure of a small group",
)
def cayley_table(group: Any) -> Any:
    """Build the Cayley table of a group."""
    return group.operation.rows()


@benchmark(
    group=GROUP_GROUPS,
    sizes=[40, 80, 160],
    complexity="O(n times the generator count)",
    setup=make_cyclic_group,
    requires=groups_module,
    note="the bridge into the graph package, which consumes it as a graph",
)
def cayley_graph(group: Any) -> Any:
    """Build the Cayley graph of a group."""
    return group.cayley_graph()


@benchmark(
    group=GROUP_GROUPS,
    sizes=[24, 48, 96],
    complexity="O(n) per candidate morphism",
    setup=make_cyclic_group,
    requires=groups_module,
)
def homomorphism_verification(group: Any) -> Any:
    """Verify that a reduction map is a homomorphism."""
    target = groups_module.CyclicGroup(max(2, group.order() // 2))
    return groups_module.Homomorphism(
        group, target, lambda value: value % target.order()
    )


@benchmark(
    group=GROUP_GROUPS,
    sizes=[12, 24, 48],
    complexity="exponential in the worst case",
    setup=make_cyclic_group,
    requires=groups_module,
    note="isomorphism against a direct product, which must be decided",
)
def isomorphism_test(group: Any) -> bool:
    """Decide whether a group is isomorphic to a copy of itself."""
    return groups_module.are_isomorphic(group, group)


# ---------------------------------------------------------------------------
# Group actions
# ---------------------------------------------------------------------------


@benchmark(
    group=GROUP_ACTIONS,
    sizes=[4, 5, 6],
    complexity="O(group order times point count)",
    setup=make_action,
    requires=groups_module,
    note="the orbit computation, whose cost the Polya machinery inherits",
)
def orbits(payload: Tuple[Any, Any]) -> Any:
    """Compute every orbit of a group action."""
    _, action = payload
    return action.orbits()


@benchmark(
    group=GROUP_ACTIONS,
    sizes=[4, 5, 6],
    complexity="O(group order) per point",
    setup=make_action,
    requires=groups_module,
    note=(
        "the stabilizer, whose size times the orbit size must equal the "
        "group order, which is the theorem the suite asserts"
    ),
)
def stabilizers(payload: Tuple[Any, Any]) -> int:
    """Compute the stabilizer of every point of an action."""
    group, action = payload
    checked = 0
    for point in action.points:
        orbit = action.orbit(point)
        stabilizer = action.stabilizer(point)
        if len(orbit) * stabilizer.order() != group.order():
            raise AssertionError("the orbit stabilizer theorem failed")
        checked += 1
    return checked


@benchmark(
    group=GROUP_ACTIONS,
    sizes=[4, 5, 6],
    complexity="O(group order) fixed point counts",
    setup=make_action,
    requires=groups_module,
    note="Burnside's lemma, which counts the orbits without listing them",
)
def burnside_count(payload: Tuple[Any, Any]) -> int:
    """Count the orbits of an action by Burnside's lemma."""
    _, action = payload
    return action.burnside_count()


# ---------------------------------------------------------------------------
# Rings and fields
# ---------------------------------------------------------------------------


@benchmark(
    group=GROUP_RINGS,
    sizes=[12, 24, 48],
    complexity="O(n cubed) including distributivity",
    requires=rings_module,
)
def modular_ring_construction(modulus: int) -> Any:
    """Build the ring of integers modulo a value."""
    return rings_module.Zmod(modulus)


@benchmark(
    group=GROUP_RINGS,
    sizes=[60, 120, 240],
    complexity="O(n log n) through the divisor test",
    setup=make_modular_ring,
    requires=rings_module,
    note="the units, whose count is the Euler totient of the modulus",
)
def ring_units(ring: Any) -> Any:
    """Find the invertible elements of a ring."""
    return ring.units()


@benchmark(
    group=GROUP_RINGS,
    sizes=[60, 120, 240],
    complexity="O(n log n)",
    setup=make_modular_ring,
    requires=rings_module,
    note="every nonzero element is a unit or a zero divisor, and this is the other half",
)
def ring_zero_divisors(ring: Any) -> Any:
    """Find the zero divisors of a ring."""
    return ring.zero_divisors()


@benchmark(
    group=GROUP_FIELDS,
    sizes=[101, 1_009, 10_007],
    complexity="O(1) per construction",
    requires=fields_module,
    note="a prime field, whose arithmetic is modular arithmetic",
)
def prime_field_construction(order: int) -> Any:
    """Build a prime field of roughly the given order."""
    return make_prime_field(order)


@benchmark(
    group=GROUP_FIELDS,
    sizes=[101, 1_009, 10_007],
    complexity="O(log order) per inverse",
    setup=make_prime_field,
    requires=fields_module,
)
def prime_field_inverses(field: Any) -> int:
    """Invert a thousand elements of a prime field."""
    order = field.order()
    total = 0
    for value in range(1, min(order, 1_001)):
        total += int(field.inverse(value))
    return total


@benchmark(
    group=GROUP_FIELDS,
    sizes=[4, 8, 12],
    complexity="O(degree squared) per multiplication",
    setup=make_galois_field,
    requires=fields_module,
    note=(
        "the size is the extension degree, so the field order doubles at "
        "each step while the multiplication cost grows as its square"
    ),
)
def galois_field_multiplication(field: Any) -> Any:
    """Multiply a thousand pairs of elements of a binary field extension."""
    elements = field.elements()[: min(len(field.elements()), 40)]
    result = None
    for left in elements:
        for right in elements:
            result = field.multiply(left, right)
    return result


@benchmark(
    group=GROUP_FIELDS,
    sizes=[4, 8, 12],
    complexity="O(degree cubed) through the extended algorithm",
    setup=make_galois_field,
    requires=fields_module,
)
def galois_field_inverses(field: Any) -> Any:
    """Invert every nonzero element of a binary field extension."""
    result = None
    for element in field.elements():
        if element != field.zero():
            result = field.inverse(element)
    return result


@benchmark(
    group=GROUP_FIELDS,
    sizes=[4, 8, 12],
    complexity="O(order times the divisor count)",
    setup=make_galois_field,
    requires=fields_module,
    note="a generator of the multiplicative group, which is cyclic",
)
def primitive_element(field: Any) -> Any:
    """Find a primitive element of a finite field."""
    return field.primitive_element()


# ---------------------------------------------------------------------------
# Polynomials
# ---------------------------------------------------------------------------


@benchmark(
    group=GROUP_POLYNOMIALS,
    sizes=[100, 400, 1_600],
    complexity="O(n)",
    setup=make_two_polynomials,
    requires=polynomials_module,
)
def polynomial_add(payload: Tuple[Any, Any]) -> Any:
    """Add two polynomials."""
    left, right = payload
    return left + right


@benchmark(
    group=GROUP_POLYNOMIALS,
    sizes=[100, 200, 400],
    complexity="O(n times m)",
    setup=make_two_polynomials,
    requires=polynomials_module,
    note="the quadratic operation, and the one to watch",
)
def polynomial_multiply(payload: Tuple[Any, Any]) -> Any:
    """Multiply two polynomials."""
    left, right = payload
    return left * right


@benchmark(
    group=GROUP_POLYNOMIALS,
    sizes=[100, 200, 400],
    complexity="O((n - m + 1) times m)",
    setup=make_two_polynomials,
    requires=polynomials_module,
)
def polynomial_divmod(payload: Tuple[Any, Any]) -> Any:
    """Divide one polynomial by another with remainder."""
    left, right = payload
    return divmod(left, right)


@benchmark(
    group=GROUP_POLYNOMIALS,
    sizes=[50, 100, 200],
    complexity="O(n times m) through repeated division",
    setup=make_two_polynomials,
    requires=polynomials_module,
)
def polynomial_gcd(payload: Tuple[Any, Any]) -> Any:
    """Compute the greatest common divisor of two polynomials."""
    left, right = payload
    return polynomials_module.gcd(left, right)


@benchmark(
    group=GROUP_POLYNOMIALS,
    sizes=[1_000, 10_000, 100_000],
    complexity="O(n) by Horner evaluation",
    setup=make_polynomial,
    requires=polynomials_module,
)
def polynomial_evaluate(polynomial: Any) -> Any:
    """Evaluate a polynomial at a point."""
    return polynomial.evaluate(3)


@benchmark(
    group=GROUP_POLYNOMIALS,
    sizes=[20, 40, 80],
    complexity="O(n squared) or worse",
    setup=make_two_polynomials,
    requires=polynomials_module,
)
def polynomial_compose(payload: Tuple[Any, Any]) -> Any:
    """Substitute one polynomial into another."""
    left, right = payload
    return left.compose(right)


@benchmark(
    group=GROUP_POLYNOMIALS,
    sizes=[10, 20, 40],
    complexity="depends on the factorization method",
    setup=make_polynomial,
    requires=polynomials_module,
    note="factorization over the rationals, by root extraction and combination",
)
def polynomial_factor(polynomial: Any) -> Any:
    """Factor a polynomial over the rationals."""
    return polynomial.factor()


@benchmark(
    group=GROUP_POLYNOMIALS,
    sizes=[20, 50, 100],
    complexity="O(n squared)",
    requires=polynomials_module,
    note="Lagrange interpolation, which is exact over the rationals",
)
def polynomial_interpolate(points: int) -> Any:
    """Interpolate a polynomial through exact points."""
    source = seeded(f"algebra.interpolate.{points}")
    samples = [(index, source.randint(-50, 50)) for index in range(points)]
    return polynomials_module.interpolate(samples)


@benchmark(
    group=GROUP_CORE,
    sizes=[100, 200, 400],
    complexity="O(n times m)",
    setup=make_two_core_polynomials,
    requires=core_polynomial_module,
    note="the core layer polynomial, measurable before the package exists",
)
def core_polynomial_multiply(payload: Tuple[Any, Any]) -> Any:
    """Multiply two core layer polynomials."""
    left, right = payload
    return left.multiply(right)


@benchmark(
    group=GROUP_CORE,
    sizes=[100, 200, 400],
    complexity="O((n - m + 1) times m)",
    setup=make_two_core_polynomials,
    requires=core_polynomial_module,
)
def core_polynomial_divmod(payload: Tuple[Any, Any]) -> Any:
    """Divide two core layer polynomials with remainder."""
    left, right = payload
    return left.divmod(right)


@benchmark(
    group=GROUP_CORE,
    sizes=[1_000, 10_000, 100_000],
    complexity="O(n) multiplications on a growing accumulator",
    setup=make_core_polynomial,
    requires=core_polynomial_module,
    note=(
        "linear in the coefficient count and superlinear in the digits, "
        "because Horner's accumulator grows with the degree; the implied "
        "exponent therefore sits above one, which is the cost of exactness "
        "rather than a defect"
    ),
)
def core_polynomial_evaluate(polynomial: Any) -> Any:
    """Evaluate a core layer polynomial at a point."""
    return polynomial.evaluate(3)


# ---------------------------------------------------------------------------
# Exact linear algebra
# ---------------------------------------------------------------------------


@benchmark(
    group=GROUP_LINEAR,
    sizes=[10, 20, 40],
    complexity="O(n cubed) exact operations",
    setup=make_matrix,
    requires=linear_module,
    note=(
        "the determinant over the integers, computed fraction free so that "
        "the intermediate numerators stay bounded"
    ),
)
def determinant_integer(matrix: Any) -> Any:
    """Compute the determinant of an integer matrix exactly."""
    return linear_module.determinant(matrix)


@benchmark(
    group=GROUP_LINEAR,
    sizes=[10, 20, 40],
    complexity="O(n cubed) exact operations",
    setup=make_rational_matrix,
    requires=linear_module,
    note=(
        "the same computation over the rationals; the ratio against the "
        "integer case is the cost of exact fraction arithmetic"
    ),
)
def determinant_rational(matrix: Any) -> Any:
    """Compute the determinant of a rational matrix exactly."""
    return linear_module.determinant(matrix)


@benchmark(
    group=GROUP_LINEAR,
    sizes=[10, 20, 40],
    complexity="O(n cubed)",
    setup=make_matrix,
    requires=linear_module,
)
def gaussian_elimination(matrix: Any) -> Any:
    """Reduce a matrix to row echelon form."""
    return linear_module.gaussian_elimination(matrix)


@benchmark(
    group=GROUP_LINEAR,
    sizes=[10, 20, 40],
    complexity="O(n cubed)",
    setup=make_matrix,
    requires=linear_module,
    note="the rank, which over the rationals is a fact rather than a guess",
)
def matrix_rank(matrix: Any) -> int:
    """Compute the rank of a matrix exactly."""
    return linear_module.rank(matrix)


@benchmark(
    group=GROUP_LINEAR,
    sizes=[10, 20, 40],
    complexity="O(n cubed)",
    setup=make_matrix,
    requires=linear_module,
)
def matrix_inverse(matrix: Any) -> Any:
    """Invert a matrix exactly."""
    return linear_module.inverse(matrix)


@benchmark(
    group=GROUP_LINEAR,
    sizes=[10, 20, 40],
    complexity="O(n cubed) plus the factoring",
    setup=make_matrix,
    requires=linear_module,
    note="the characteristic polynomial, from which the eigenvalues follow",
)
def characteristic_polynomial(matrix: Any) -> Any:
    """Compute the characteristic polynomial of a matrix."""
    return linear_module.characteristic_polynomial(matrix)


@benchmark(
    group=GROUP_CORE,
    sizes=[10, 20, 40],
    complexity="O(n cubed) exact multiplications",
    setup=make_core_matrix,
    requires=core_matrix_module,
    note="the core layer matrix product, measurable before the package exists",
)
def core_matrix_multiply(matrix: Any) -> Any:
    """Multiply a core layer matrix by itself."""
    return matrix.multiply(matrix)


@benchmark(
    group=GROUP_CORE,
    sizes=[1_000, 10_000, 100_000],
    complexity="O(k cubed log n) exact operations",
    setup=make_fibonacci_matrix,
    requires=core_matrix_module,
    note=(
        "the identity behind the recurrence package: the matrix power needs "
        "only a logarithmic number of multiplications. The implied exponent "
        "starts well below one and rises toward one as the exponent grows, "
        "because the entries are Fibonacci numbers whose digit count grows "
        "linearly and whose multiplication is superlinear in the digits. "
        "What the measurement establishes is that the multiplication count "
        "is logarithmic; the remaining growth is the arithmetic on the "
        "answer itself, which no method can avoid"
    ),
)
def core_matrix_power(payload: Tuple[Any, int]) -> Any:
    """Raise the Fibonacci matrix to the power given by the size."""
    matrix, exponent = payload
    return matrix.power(exponent)


# ---------------------------------------------------------------------------
# Lattices
# ---------------------------------------------------------------------------


@benchmark(
    group=GROUP_LATTICE,
    sizes=[4, 6, 8],
    complexity="O(n squared) to verify the absorption laws",
    requires=lattice_module,
    note="the size is the atom count, so the carrier doubles at each step",
)
def boolean_algebra_construction(atoms: int) -> Any:
    """Build a Boolean algebra on the given number of atoms."""
    return make_boolean_lattice(atoms)


@benchmark(
    group=GROUP_LATTICE,
    sizes=[4, 6, 8],
    complexity="O(n cubed)",
    setup=make_boolean_lattice,
    requires=lattice_module,
)
def lattice_distributivity(lattice: Any) -> bool:
    """Verify the distributive laws of a lattice."""
    return lattice.is_distributive()


@benchmark(
    group=GROUP_LATTICE,
    sizes=[4, 6, 8],
    complexity="O(n squared)",
    setup=make_boolean_lattice,
    requires=lattice_module,
    note="complementation, which distinguishes a Boolean algebra",
)
def lattice_complements(lattice: Any) -> Any:
    """Compute the complement of every element of a lattice."""
    return {element: lattice.complement(element) for element in lattice.elements()}


# ---------------------------------------------------------------------------
# Notes on reading these results
# ---------------------------------------------------------------------------
#
# The comparisons this file exists for:
#
#   cyclic_group_verified against cyclic_group_unverified. The central
#   measurement of the file. The ratio is the price of the guarantee that
#   every structure in the package satisfies its axioms, and the growth
#   report should show the verified construction growing cubically while the
#   unverified one grows linearly. The reference offers a flag to skip the
#   check and tells a reader to use it only when the axioms are already
#   established, and this pair is where that advice is priced.
#
#   core_verify_closure against core_verify_associativity. Quadratic against
#   cubic on the same carrier, which identifies associativity as the term
#   that dominates every construction in the package. A contributor
#   optimizing verification should start there and nowhere else.
#
#   determinant_integer against determinant_rational. The same elimination
#   over two coefficient domains. The ratio is the cost of exact fraction
#   arithmetic, and it is the reason the implementation is fraction free
#   where it can be.
#
#   polynomial_add against polynomial_multiply against polynomial_divmod.
#   Linear, quadratic, and the quotient degree times the divisor degree. The
#   three should separate cleanly, and polynomial_gcd should track the
#   division rather than the multiplication because it repeats the former.
#
#   galois_field_multiplication across the extension degrees. The field
#   order doubles at each step while the multiplication cost grows as the
#   square of the degree, so the time should grow far more slowly than the
#   order. A cost that tracked the order would mean the implementation is
#   enumerating the field somewhere.
#
#   core_matrix_power. The implied exponent should be far below one, because
#   raising a matrix to the power n costs a logarithmic number of
#   multiplications. This is the identity the recurrence package relies on
#   to evaluate a distant term, and a measurement that grew linearly would
#   mean the repeated squaring had regressed to repeated multiplication.
#
#   subgroup_enumeration across the orders. The growth is not smooth,
#   because the cost depends on the divisor structure of the order rather
#   than on the order itself. An order with many divisors is much more
#   expensive than a nearby prime order, which is Lagrange's theorem
#   appearing in a benchmark.
