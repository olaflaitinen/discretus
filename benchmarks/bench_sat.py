# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Benchmarks for the satisfiability solvers.

Satisfiability is measured separately from the rest of the logic package
because it is the one part of the library whose cost is dominated by search
rather than by traversal. A traversal benchmark measures a routine; a solver
benchmark measures a routine against an instance family, and the family
matters more than the size.

Five families are used here, each chosen because it isolates one thing.

    Unit propagation chains. Every clause becomes unit as soon as the
    previous one is satisfied, so the whole instance is decided by
    propagation with no decisions at all. This measures the propagation
    machinery in isolation, which is where the watched literal scheme earns
    its place.

    Random instances below the threshold. At a low clause to variable ratio
    almost every instance is satisfiable and easy, because a satisfying
    assignment is dense in the space.

    Random instances at the threshold. Around four and a quarter clauses per
    variable for three literal clauses, satisfiable and unsatisfiable
    instances are equally likely and both are hardest. This is the family
    that distinguishes a solver from a search.

    Random instances above the threshold. Almost every instance is
    unsatisfiable, and a solver that learns clauses proves it far faster
    than one that does not.

    Pigeonhole instances. These say that n plus one pigeons fit into n holes
    with at most one pigeon per hole, which is false, and they are famously
    hard for resolution based search. They are the clearest demonstration of
    what conflict driven clause learning buys, because plain backtracking
    relearns the same contradiction many times over.

Both solvers are measured on the same families wherever the reference
implementation can finish, because the project ships a transparent
implementation to be read and a tuned one to be used, and a comparison is
the only honest way to describe the difference.

Every instance is generated from a seed derived from its benchmark name, so
a measurement can be repeated exactly. That matters more here than anywhere
else in the suite: solver runtimes vary by orders of magnitude between
instances of the same size, so an unseeded family would make two runs
incomparable.
"""

from __future__ import annotations

from typing import Any, List, Optional, Tuple

from . import benchmark, require, requires_all, seeded

# ---------------------------------------------------------------------------
# The modules under measurement
# ---------------------------------------------------------------------------

sat_module = require(
    "discretus.logic.sat", "Cnf", "solve", "solve_dpll", "unit_propagate"
)
propositional_module = require("discretus.logic.propositional", "parse")
dimacs_module = require("discretus.io.dimacs_io", "loads", "dumps")

GROUP = "sat"
GROUP_PROPAGATION = "sat.propagation"
GROUP_ENCODING = "sat.encoding"
GROUP_INTERCHANGE = "sat.interchange"

#: The clause to variable ratio at which three literal random instances are
#: hardest. Below it almost every instance is satisfiable, above it almost
#: every instance is unsatisfiable, and at it the two are equally likely.
THRESHOLD_RATIO = 4.26


# ---------------------------------------------------------------------------
# Instance families
# ---------------------------------------------------------------------------
# A family is built as a list of clauses of signed integer literals, which is
# the representation the solver uses internally and the one DIMACS carries.
# Building the instance is never timed.


def random_clauses(
    variables: int,
    clauses: int,
    width: int = 3,
    label: str = "sat.random",
) -> List[List[int]]:
    """Return a reproducible random instance with the given shape.

    Each clause is a sample of distinct variables with independent random
    polarities, which is the standard uniform random model. Duplicate
    variables within a clause are excluded, because a clause containing a
    variable and its negation is trivially satisfied and would make the
    instance easier than its shape suggests.
    """
    source = seeded(f"{label}.{variables}.{clauses}.{width}")
    instance: List[List[int]] = []
    for _ in range(clauses):
        chosen = source.sample(range(1, variables + 1), min(width, variables))
        instance.append(
            [value if source.random() < 0.5 else -value for value in chosen]
        )
    return instance


def make_easy_instance(variables: int) -> Optional[Any]:
    """Return a random instance well below the satisfiability threshold."""
    if sat_module is None:
        return None
    clauses = int(variables * 2.0)
    return sat_module.Cnf(random_clauses(variables, clauses, label="sat.easy"))


def make_threshold_instance(variables: int) -> Optional[Any]:
    """Return a random instance at the satisfiability threshold."""
    if sat_module is None:
        return None
    clauses = int(variables * THRESHOLD_RATIO)
    return sat_module.Cnf(random_clauses(variables, clauses, label="sat.threshold"))


def make_hard_unsat_instance(variables: int) -> Optional[Any]:
    """Return a random instance above the threshold, almost surely unsatisfiable."""
    if sat_module is None:
        return None
    clauses = int(variables * 6.0)
    return sat_module.Cnf(random_clauses(variables, clauses, label="sat.unsat"))


def make_propagation_chain(length: int) -> Optional[Any]:
    """Return an instance decided entirely by unit propagation.

    The first clause is a unit clause, and every later clause becomes unit as
    soon as the previous variable is assigned. No decision is ever needed, so
    the whole runtime is propagation.
    """
    if sat_module is None:
        return None
    clauses: List[List[int]] = [[1]]
    for index in range(1, length):
        clauses.append([-index, index + 1])
    return sat_module.Cnf(clauses)


def make_pigeonhole(holes: int) -> Optional[Any]:
    """Return the pigeonhole instance for one more pigeon than holes.

    The encoding is the standard one: a variable per pigeon and hole, a
    clause saying every pigeon is in some hole, and a clause per pair of
    pigeons per hole saying they do not share it. The instance is
    unsatisfiable, and its size grows as the cube of the hole count.
    """
    if sat_module is None:
        return None
    pigeons = holes + 1

    def variable(pigeon: int, hole: int) -> int:
        return pigeon * holes + hole + 1

    clauses: List[List[int]] = []
    for pigeon in range(pigeons):
        clauses.append([variable(pigeon, hole) for hole in range(holes)])
    for hole in range(holes):
        for first in range(pigeons):
            for second in range(first + 1, pigeons):
                clauses.append([-variable(first, hole), -variable(second, hole)])
    return sat_module.Cnf(clauses)


def make_graph_coloring(vertices: int) -> Optional[Any]:
    """Return a three colouring instance for a reproducible random graph.

    This is the encoding the satisfiability tutorial builds, and it is worth
    measuring because it is the shape a real application produces: an at
    least one constraint per object, an at most one constraint per object,
    and a difference constraint per relation.
    """
    if sat_module is None:
        return None
    colours = 3
    source = seeded(f"sat.coloring.{vertices}")
    edges = set()
    for _ in range(vertices * 3):
        left = source.randrange(vertices)
        right = source.randrange(vertices)
        if left != right:
            edges.add((min(left, right), max(left, right)))

    def variable(vertex: int, colour: int) -> int:
        return vertex * colours + colour + 1

    clauses: List[List[int]] = []
    for vertex in range(vertices):
        clauses.append([variable(vertex, colour) for colour in range(colours)])
        for first in range(colours):
            for second in range(first + 1, colours):
                clauses.append([-variable(vertex, first), -variable(vertex, second)])
    for left, right in sorted(edges):
        for colour in range(colours):
            clauses.append([-variable(left, colour), -variable(right, colour)])
    return sat_module.Cnf(clauses)


def make_instance_and_model(variables: int) -> Optional[Tuple[Any, Any]]:
    """Return a satisfiable instance together with a model of it.

    Used by the verification benchmark. Solving is not timed; only the check
    that the returned assignment satisfies the instance is.
    """
    if sat_module is None:
        return None
    instance = make_easy_instance(variables)
    model = sat_module.solve(instance)
    return instance, model


def make_dimacs_text(variables: int) -> Optional[str]:
    """Return an instance rendered as DIMACS text."""
    if sat_module is None:
        return None
    return make_threshold_instance(variables).to_dimacs()


def make_literal_pool(count: int) -> List[str]:
    """Return variable names for the cardinality encoding benchmarks."""
    return [f"x{index}" for index in range(count)]


# ---------------------------------------------------------------------------
# Propagation
# ---------------------------------------------------------------------------


@benchmark(
    group=GROUP_PROPAGATION,
    sizes=[1_000, 10_000, 100_000],
    complexity="O(total size of the clauses)",
    setup=make_propagation_chain,
    requires=sat_module,
    note="the whole instance is decided without a single decision",
)
def unit_propagation(instance: Any) -> Any:
    """Propagate a chain to its fixed point."""
    return sat_module.unit_propagate(instance)


@benchmark(
    group=GROUP_PROPAGATION,
    sizes=[1_000, 10_000, 100_000],
    complexity="O(total size of the clauses)",
    setup=make_propagation_chain,
    requires=sat_module,
    note=(
        "the full solver on an instance that needs no search, which isolates "
        "the propagation machinery from the decision heuristic"
    ),
)
def solve_propagation_only(instance: Any) -> Any:
    """Solve an instance that propagation alone decides."""
    return sat_module.solve(instance)


@benchmark(
    group=GROUP_PROPAGATION,
    sizes=[1_000, 10_000],
    complexity="O(total size of the clauses)",
    setup=make_propagation_chain,
    requires=sat_module,
    note="the reference implementation on the same instance, for comparison",
)
def solve_propagation_only_dpll(instance: Any) -> Any:
    """Solve a propagation chain with the classical procedure."""
    return sat_module.solve_dpll(instance)


# ---------------------------------------------------------------------------
# Random instances
# ---------------------------------------------------------------------------


@benchmark(
    group=GROUP,
    sizes=[50, 100, 200, 400],
    complexity="exponential in the worst case",
    setup=make_easy_instance,
    requires=sat_module,
    note="two clauses per variable, far below the threshold, almost always easy",
)
def solve_easy(instance: Any) -> Any:
    """Solve a random instance below the satisfiability threshold."""
    return sat_module.solve(instance)


@benchmark(
    group=GROUP,
    sizes=[30, 60, 90, 120],
    complexity="exponential in the worst case",
    setup=make_threshold_instance,
    requires=sat_module,
    note=(
        "at the threshold, where satisfiable and unsatisfiable instances are "
        "equally likely and both are hardest"
    ),
)
def solve_threshold(instance: Any) -> Any:
    """Solve a random instance at the satisfiability threshold."""
    return sat_module.solve(instance)


@benchmark(
    group=GROUP,
    sizes=[30, 60, 90],
    complexity="exponential in the worst case",
    setup=make_hard_unsat_instance,
    requires=sat_module,
    note=(
        "above the threshold, almost surely unsatisfiable, which requires a "
        "proof rather than a witness"
    ),
)
def solve_unsatisfiable(instance: Any) -> Any:
    """Refute a random instance above the satisfiability threshold."""
    return sat_module.solve(instance)


@benchmark(
    group=GROUP,
    sizes=[15, 20, 25],
    complexity="exponential in the worst case",
    setup=make_threshold_instance,
    requires=sat_module,
    note=(
        "the reference implementation at the threshold; the sizes are small "
        "because plain backtracking cannot reach the ones above"
    ),
)
def solve_threshold_dpll(instance: Any) -> Any:
    """Solve a threshold instance with the classical procedure."""
    return sat_module.solve_dpll(instance)


@benchmark(
    group=GROUP,
    sizes=[15, 20, 25],
    complexity="exponential in the worst case",
    setup=make_threshold_instance,
    requires=sat_module,
    note="the tuned solver at the same sizes, so the ratio is meaningful",
)
def solve_threshold_cdcl_small(instance: Any) -> Any:
    """Solve a small threshold instance with the conflict driven solver."""
    return sat_module.solve(instance)


# ---------------------------------------------------------------------------
# Pigeonhole instances
# ---------------------------------------------------------------------------


@benchmark(
    group=GROUP,
    sizes=[5, 6, 7, 8],
    complexity="exponential, and famously hard for resolution",
    setup=make_pigeonhole,
    requires=sat_module,
    note=(
        "the family that demonstrates clause learning; each learned clause "
        "rules out a whole class of assignments rather than one"
    ),
)
def pigeonhole_cdcl(instance: Any) -> Any:
    """Refute a pigeonhole instance with the conflict driven solver."""
    return sat_module.solve(instance)


@benchmark(
    group=GROUP,
    sizes=[4, 5, 6],
    complexity="exponential, and worse here than for the tuned solver",
    setup=make_pigeonhole,
    requires=sat_module,
    note=(
        "the same family without learning, which relearns the same "
        "contradiction many times; compare the growth with pigeonhole_cdcl"
    ),
)
def pigeonhole_dpll(instance: Any) -> Any:
    """Refute a pigeonhole instance with the classical procedure."""
    return sat_module.solve_dpll(instance)


@benchmark(
    group=GROUP,
    sizes=[5, 6, 7],
    complexity="exponential",
    setup=make_pigeonhole,
    requires=sat_module,
    note=(
        "recording the resolution steps of each learned clause, so that the "
        "refutation can be checked; the overhead of doing so is the point"
    ),
)
def pigeonhole_with_proof(instance: Any) -> Any:
    """Refute a pigeonhole instance and record the proof."""
    return sat_module.solve(instance, record_proof=True)


# ---------------------------------------------------------------------------
# Application shaped instances
# ---------------------------------------------------------------------------


@benchmark(
    group=GROUP,
    sizes=[20, 50, 100, 200],
    complexity="exponential in the worst case",
    setup=make_graph_coloring,
    requires=sat_module,
    note=(
        "the shape a real application produces: at least one, at most one, "
        "and a difference constraint per relation"
    ),
)
def solve_graph_coloring(instance: Any) -> Any:
    """Decide three colourability of a random graph through the solver."""
    return sat_module.solve(instance)


@benchmark(
    group=GROUP,
    sizes=[50, 100, 200],
    complexity="exponential in the worst case",
    setup=make_easy_instance,
    requires=sat_module,
    note="solving with the statistics recorded, to measure the bookkeeping",
)
def solve_with_statistics(instance: Any) -> Any:
    """Solve an instance while recording the search statistics."""
    return sat_module.solve(instance, record_statistics=True)


@benchmark(
    group=GROUP,
    sizes=[100, 400, 1_600],
    complexity="O(total size of the clauses)",
    setup=make_instance_and_model,
    requires=sat_module,
    note=(
        "verifying a model is cheap, which is why the suite asserts it on "
        "every solved instance rather than trusting the solver"
    ),
)
def verify_model(payload: Tuple[Any, Any]) -> bool:
    """Check that a returned assignment satisfies the instance."""
    instance, model = payload
    return model.satisfies(instance)


# ---------------------------------------------------------------------------
# Cardinality encodings
# ---------------------------------------------------------------------------


@benchmark(
    group=GROUP_ENCODING,
    sizes=[10, 50, 100, 200],
    complexity="O(k squared) clauses",
    setup=make_literal_pool,
    requires=sat_module,
    note="the pairwise encoding, quadratic and fine for a small k",
)
def at_most_one_pairwise(literals: List[str]) -> Any:
    """Encode an at most one constraint pairwise."""
    return sat_module.at_most_one(literals, encoding="pairwise")


@benchmark(
    group=GROUP_ENCODING,
    sizes=[10, 50, 100, 200, 1_000],
    complexity="O(k) clauses with auxiliary variables",
    setup=make_literal_pool,
    requires=sat_module,
    note=(
        "the sequential encoding, linear in the literal count; the growth "
        "ratio against the pairwise encoding is the reason both exist"
    ),
)
def at_most_one_sequential(literals: List[str]) -> Any:
    """Encode an at most one constraint sequentially."""
    return sat_module.at_most_one(literals, encoding="sequential")


@benchmark(
    group=GROUP_ENCODING,
    sizes=[10, 50, 100, 200],
    complexity="O(k squared) clauses with the pairwise encoding",
    setup=make_literal_pool,
    requires=sat_module,
)
def exactly_one(literals: List[str]) -> Any:
    """Encode an exactly one constraint."""
    return sat_module.exactly_one(literals)


@benchmark(
    group=GROUP_ENCODING,
    sizes=[100, 1_000, 10_000],
    complexity="O(size of the formula)",
    requires=requires_all(propositional_module, sat_module),
    note="converting a parsed formula into the clause representation",
)
def formula_to_clauses(clauses: int) -> Any:
    """Convert a parsed formula into a clause instance."""
    source = seeded(f"sat.formula_to_clauses.{clauses}")
    variables = max(4, clauses // 3)
    parts = []
    for _ in range(clauses):
        chosen = source.sample(range(variables), 3)
        literals = [
            f"{'~' if source.random() < 0.5 else ''}p{index}" for index in chosen
        ]
        parts.append("(" + " | ".join(literals) + ")")
    formula = propositional_module.parse(" & ".join(parts))
    return sat_module.Cnf.from_formula(formula)


# ---------------------------------------------------------------------------
# Interchange
# ---------------------------------------------------------------------------


@benchmark(
    group=GROUP_INTERCHANGE,
    sizes=[100, 1_000, 10_000],
    complexity="O(total literals)",
    setup=make_threshold_instance,
    requires=sat_module,
    note="writing the format a dedicated solver reads",
)
def write_dimacs(instance: Any) -> str:
    """Render an instance as DIMACS text."""
    return instance.to_dimacs()


@benchmark(
    group=GROUP_INTERCHANGE,
    sizes=[100, 1_000, 10_000],
    complexity="O(total literals)",
    setup=make_dimacs_text,
    requires=sat_module,
    note="reading it back, tolerating comments and a stale header",
)
def read_dimacs(text: str) -> Any:
    """Parse an instance from DIMACS text."""
    return sat_module.Cnf.from_dimacs(text)


@benchmark(
    group=GROUP_INTERCHANGE,
    sizes=[100, 1_000, 10_000],
    complexity="O(total literals)",
    setup=make_threshold_instance,
    requires=sat_module,
    note=(
        "the round trip, which must reconstruct an equal instance and then "
        "produce identical bytes"
    ),
)
def dimacs_round_trip(instance: Any) -> bool:
    """Write an instance, read it back, and write it again."""
    first = instance.to_dimacs()
    recovered = sat_module.Cnf.from_dimacs(first)
    return recovered.to_dimacs() == first


@benchmark(
    group=GROUP_INTERCHANGE,
    sizes=[1_000, 10_000],
    complexity="O(total literals)",
    setup=make_dimacs_text,
    requires=requires_all(sat_module, dimacs_module),
    note="the same read through the interchange package rather than the type",
)
def read_dimacs_via_io(text: str) -> Any:
    """Parse an instance through the interchange module."""
    return dimacs_module.loads(text)


# ---------------------------------------------------------------------------
# Notes on reading these results
# ---------------------------------------------------------------------------
#
# Read the growth ratios rather than the absolute times, and read the
# comparisons rather than either.
#
#   pigeonhole_cdcl against pigeonhole_dpll. The central measurement of the
#   file. Both are exponential, and the conflict driven solver should reach
#   two or three more holes in comparable time. That difference is what
#   clause learning buys, and it is the reason the tuned solver exists
#   alongside the readable one.
#
#   solve_threshold_dpll against solve_threshold_cdcl_small. The same
#   instances, both solvers, at sizes the reference implementation can
#   finish. This is the ratio to quote when somebody asks what the tuned
#   solver is worth.
#
#   solve_easy, solve_threshold, and solve_unsatisfiable. Three ratios of
#   clauses to variables, on the same solver. The threshold family should be
#   dramatically slower than either side of it, which is the phase
#   transition the tutorial describes. A run where the three are comparable
#   means the instance generator has stopped producing the intended family.
#
#   unit_propagation against solve_propagation_only. Both decide the same
#   instance, one by propagating and one through the full solver. The gap is
#   the solver's fixed overhead, and it should be a small constant factor
#   rather than growing with the instance.
#
#   at_most_one_pairwise against at_most_one_sequential. The first is
#   quadratic in the literal count and the second linear, which the growth
#   report should show clearly. The sequential encoding introduces auxiliary
#   variables, so it is not free; it is asymptotically better.
#
#   write_dimacs against dimacs_round_trip. The round trip does three times
#   the work of a single write, so a ratio far above three means the reader
#   is more expensive than the writer, which is worth knowing when an
#   instance is read once and solved many times.
#
# A caution specific to this file. Solver runtimes vary by orders of
# magnitude between instances of the same shape, so a single instance per
# size is a weak sample. The seeds make the sample reproducible rather than
# representative. When a change looks like a regression here, rerun with a
# different seed offset before believing it.
