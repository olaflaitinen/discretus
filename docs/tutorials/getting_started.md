# Getting started

This tutorial is the slow path into the library. It assumes you have
installed discretus and know some Python, and it assumes nothing about which
parts of discrete mathematics you already know.

We will build one small project, a room scheduling problem, and solve it
four times: with sets, with logic, with graphs, and with algebra. That is a
contrived amount of variety for one problem, and it is the point. By the end
you will have used four of the seven domains, seen how they interoperate,
and met every convention the library relies on.

Work through it in an interpreter session or a notebook, one block at a
time. Every block runs on a fresh installation with no optional extras.

## The problem

A department has five seminars to schedule. Some pairs cannot be at the same
time, because a person or a room is shared.

| Seminar | Conflicts with |
| --- | --- |
| algebra | logic, graphs |
| logic | algebra, graphs |
| graphs | algebra, logic, numbers |
| numbers | graphs, sets |
| sets | numbers |

Three questions follow, and each belongs to a different domain.

1. Which seminars can be scheduled together, that is which sets of seminars
   are pairwise compatible? This is set theory.
2. Is there a valid schedule with a given number of time slots? This is
   logic.
3. What is the smallest number of slots that suffices? This is graph theory.

## Step one: install and check

```bash
pip install discretus
python -c "import discretus; print(discretus.__version__)"
```

If that printed a version, you are ready. If it did not, the
[installation page](../installation.md) has the troubleshooting.

## Step two: sets

We start by writing the conflicts down as data. The seminars form a set, and
the conflicts form a set of unordered pairs.

```python
from discretus.sets import FiniteSet

seminars = FiniteSet({"algebra", "logic", "graphs", "numbers", "sets"})
print(seminars)
print(len(seminars))
```

The printed set has its members in a sorted order, and that is the first
convention to notice. A mathematical set has no order, so the library has to
choose one for display, and it chooses a total order on the members rather
than the iteration order of the underlying container. The consequence is
practical: the output is identical every time you run it, in every process,
which is not true of printing a Python set.

Now the operations. The library provides them as named functions, which read
like the mathematics.

```python
from discretus.sets.operations import difference, intersection, union

morning = FiniteSet({"algebra", "numbers"})
afternoon = FiniteSet({"logic", "sets"})

print(union(morning, afternoon))
print(intersection(morning, afternoon))
print(difference(seminars, union(morning, afternoon)))
```

The third line answers a real question: which seminars are not yet placed.
Notice that nothing was modified. `union` returned a new set and left both
arguments alone, which is the second convention: values in this library do
not mutate.

That immutability is not a stylistic preference. Because a `FiniteSet` never
changes, it can be hashed, and because it can be hashed it can be a member
of another set. We need exactly that for the next step.

```python
from discretus.sets.operations import power_set

pairs = FiniteSet({
    FiniteSet({"algebra", "logic"}),
    FiniteSet({"algebra", "graphs"}),
    FiniteSet({"logic", "graphs"}),
    FiniteSet({"graphs", "numbers"}),
    FiniteSet({"numbers", "sets"}),
})
print(len(pairs))
print(pairs)
```

A set of sets, written directly. Now we can answer the first question: a set
of seminars is compatible when no conflicting pair is contained in it.

```python
def is_compatible(group: FiniteSet) -> bool:
    return not any(conflict.is_subset(group) for conflict in pairs)


compatible = [group for group in power_set(seminars) if is_compatible(group)]
print(len(compatible))
print(max(compatible, key=len))
```

Two things happened there that are worth slowing down for.

`power_set` returned a generator, not a list. The power set of a five member
set has thirty two members, so materializing it is harmless, but the power
set of a fifty member set has more members than there are grains of sand on
Earth. The library therefore enumerates lazily by default, and a caller who
knows the set is small wraps it in `list` as an explicit acknowledgment. This
is the third convention: anything exponential is lazy.

The largest compatible group is the answer to a question people usually
answer with a graph algorithm, and we will do that too in step four. It is
worth remembering that the same quantity is reachable from several
directions, because seeing that is most of the value of a unified library.

## Step three: logic

The second question was whether a schedule with a given number of slots
exists. That is naturally a logical question: assign to each seminar and
each slot a variable meaning that the seminar is in that slot, and write
down the constraints.

Start with the smaller skill of parsing and evaluating a formula.

```python
from discretus.logic.propositional import is_tautology, parse, truth_table

formula = parse("(p -> q) & (q -> r) -> (p -> r)")
print(formula)
print(is_tautology(formula))
print(truth_table(parse("p -> q")))
```

The first formula is the transitivity of implication, and it is a tautology,
which the truth table would show for a small enough formula. The parser
accepts several spellings, so all three of these are the same formula.

```python
print(parse("p -> q") == parse("p => q") == parse("p implies q"))
```

Now the scheduling constraints. With five seminars and three slots we need
fifteen variables, named so that we can read them.

```python
seminar_names = sorted(seminars.members())
slots = [0, 1, 2]


def variable(seminar: str, slot: int) -> str:
    return f"{seminar}_{slot}"


clauses = []

# Every seminar is in at least one slot.
for seminar in seminar_names:
    clauses.append(" | ".join(variable(seminar, s) for s in slots))

# No seminar is in two slots.
for seminar in seminar_names:
    for first in slots:
        for second in slots:
            if first < second:
                clauses.append(
                    f"~({variable(seminar, first)} & {variable(seminar, second)})"
                )

# Conflicting seminars are not in the same slot.
for conflict in pairs:
    left, right = sorted(conflict)
    for slot in slots:
        clauses.append(f"~({variable(left, slot)} & {variable(right, slot)})")

print(len(clauses))
```

We have a list of constraints as text. Conjoin them and solve.

```python
from discretus.logic.sat import solve

problem = parse(" & ".join(f"({clause})" for clause in clauses))
model = solve(problem)
print(model.is_satisfiable)
```

If that reported satisfiable, there is a schedule with three slots, and the
model contains it. Read it back into a form a human can use.

```python
if model.is_satisfiable:
    schedule = {}
    for seminar in seminar_names:
        for slot in slots:
            if model[variable(seminar, slot)]:
                schedule[seminar] = slot
    print(schedule)
```

Before trusting that, verify it. The model can check itself against the
formula, which is a cheap assertion and worth making a habit.

```python
print(model.satisfies(problem))
```

Now try two slots, by rebuilding the constraints with a shorter slot list.
The answer will be that no schedule exists, and the solver will say so
rather than guessing.

```python
def schedule_exists(slot_count: int) -> bool:
    local_slots = list(range(slot_count))
    local = []
    for seminar in seminar_names:
        local.append(" | ".join(variable(seminar, s) for s in local_slots))
        for first in local_slots:
            for second in local_slots:
                if first < second:
                    local.append(
                        f"~({variable(seminar, first)} & {variable(seminar, second)})"
                    )
    for conflict in pairs:
        left, right = sorted(conflict)
        for slot in local_slots:
            local.append(f"~({variable(left, slot)} & {variable(right, slot)})")
    joined = parse(" & ".join(f"({clause})" for clause in local))
    return solve(joined).is_satisfiable


print([slot_count for slot_count in range(1, 5) if schedule_exists(slot_count)])
```

That prints the slot counts that work, and the smallest of them is the
answer to the third question. We have just computed a chromatic number by
reduction to satisfiability, which is a legitimate method and is more work
than necessary. The graph package does it directly.

## Step four: graphs

The conflict structure is a graph: the seminars are vertices and the
conflicts are edges. Building it from the data we already have is two lines.

```python
from discretus.graphs import Graph

conflict_graph = Graph()
conflict_graph.add_vertices_from(seminar_names)
for conflict in pairs:
    left, right = sorted(conflict)
    conflict_graph.add_edge(left, right)

print(conflict_graph.order(), conflict_graph.size())
print(conflict_graph.degree("graphs"))
print(conflict_graph.neighbors("graphs"))
```

A valid schedule is a proper colouring of this graph, and the least number
of slots is its chromatic number. Both are one call.

```python
from discretus.graphs.coloring import chromatic_number, dsatur, is_bipartite

print(chromatic_number(conflict_graph))
print(dsatur(conflict_graph))
print(is_bipartite(conflict_graph))
```

`chromatic_number` is exact and exponential, because the problem is NP hard,
and the reference says so. `dsatur` is a heuristic that runs in near linear
time and returns an actual colouring, which may use more colours than the
minimum but usually does not on a graph this small. The library provides
both and documents the difference rather than hiding one behind the other.

Compare the answer with the logical one from step three. They agree, and
they should: a colouring is exactly an assignment of seminars to slots such
that no conflicting pair shares one.

The largest compatible group of seminars, which we computed by enumerating
the power set, is a maximum independent set of the conflict graph.

```python
from discretus.graphs.properties import max_clique, max_independent_set

print(max_independent_set(conflict_graph))
print(max_clique(conflict_graph))
```

Three quantities, computed three ways, agreeing. That is the shape of a good
sanity check, and it is also how this library's test suite is written: when
two routines must agree, the suite asserts that they do.

The clique tells us something useful about the schedule as well. A clique is
a set of mutually conflicting seminars, and every member of it needs its own
slot, so the clique number is a lower bound on the chromatic number. In this
graph the two are equal, which is why three slots suffice and two do not.

## Step five: crossing between domains

We built the graph by hand from the pairs. The library can do the conversion
directly, because a set of pairs over a ground set is a relation, and a
relation is a graph seen differently.

```python
from discretus.sets.relations import Relation

conflict_relation = Relation(
    domain=set(seminar_names),
    pairs={(a, b) for conflict in pairs for a, b in [tuple(sorted(conflict))]},
)
print(conflict_relation.is_symmetric())
print(conflict_relation.symmetric_closure().is_symmetric())

as_graph = conflict_relation.symmetric_closure().to_digraph().to_undirected()
print(as_graph.order(), as_graph.size())
```

The relation as we wrote it is not symmetric, because we listed each
conflict once. Taking the symmetric closure fixes that, and the closure is a
new relation rather than a modification of the old one. The conversion to a
graph is then a named call.

This is the fourth convention: a conversion between representations is an
explicit operation, never an implicit coercion. You can always see in the
source where a relation became a graph.

Two more conversions are worth trying, because they lead into the remaining
domains.

```python
from discretus.sets.orders import PartialOrder

divides = PartialOrder.from_relation(
    ground={1, 2, 3, 4, 6, 12},
    leq=lambda x, y: y % x == 0,
)
print(divides.is_lattice())
print(divides.hasse_diagram().edges())
```

A partial order defined by a rule, converted into the graph of its cover
relation. And from algebra:

```python
from discretus.algebra.groups import CyclicGroup

group = CyclicGroup(6)
print(group.order(), group.is_abelian())
print(group.cayley_graph().order())
```

A group, converted into its Cayley graph, which every routine in the graph
package now accepts.

## Step six: the conventions, collected

You have now met all of them. They are listed here so that you can recognize
them in the reference.

**Members may be anything hashable.** Our seminars were strings and the
divisors were integers. Nothing assumed either.

**Output order is deterministic.** Everything the library returns in an
order is sorted through a universal total order, so results are identical
between runs and between machines.

**Values do not mutate.** Every operation returns a new object. Builders
such as `Graph.add_edge` are the documented exception and say so.

**Anything exponential is lazy.** Power sets, products, permutations, and
subsets are generators. A configured limit catches an accidental request to
materialize a huge one.

**Arithmetic is exact.** Integers are unbounded and rationals are exact
fractions. We did not need that here; step seven does.

**Conversions are explicit.** A relation becomes a graph by a named call.

**Errors are a hierarchy.** Everything the library raises deliberately
derives from `DiscretusError`, and the specific class tells you what to do.

```python
from discretus import DiscretusError, DomainError, InfeasibleError
from discretus.graphs import DiGraph
from discretus.graphs.traversal import topological_sort

cyclic = DiGraph()
cyclic.add_edges_from([("a", "b"), ("b", "a")])
try:
    topological_sort(cyclic)
except InfeasibleError as error:
    print("no order exists:", error)

try:
    conflict_graph.degree("nonexistent")
except DomainError as error:
    print("bad input:", error)

print(issubclass(InfeasibleError, DiscretusError), issubclass(DomainError, DiscretusError))
```

The difference between those two is the one to remember. `DomainError` means
your input was not acceptable. `InfeasibleError` means your input was fine
and the thing you asked for does not exist.

## Step seven: exactness, briefly

The scheduling problem never needed a large number. Most of this library
does, so it is worth seeing the exactness once.

```python
from discretus.combinatorics.counting import binomial
from discretus.number_theory.factorization import factorize
from discretus.recurrences.sequences import fibonacci

print(binomial(200, 100))
print(fibonacci(500))
print(factorize(600_851_475_143))
```

Those are exact integers, not approximations, and the second one has over a
hundred digits. A library that used floating point would have lost the
answer entirely by the third digit. This is why the library is built on
Python integers and `fractions.Fraction` rather than on floats, and it is
the property that makes it usable for assessment: a hand computed answer and
a computed answer agree exactly or one of them is wrong.

## Step eight: configuration and reproducibility

Two settings are worth knowing from the start.

```python
from discretus.config import config_scope, get_config, set_config

print(get_config().max_enumeration)

with config_scope(max_enumeration=100):
    try:
        list(power_set(FiniteSet(range(20))))
    except Exception as error:
        print(type(error).__name__, error)
```

The enumeration limit is a guard rail. It caught an accidental request to
materialize a million subsets, which is exactly what it is for. The limit
does not apply to the lazy iteration, only to materializing.

```python
from discretus.graphs.generators import random_gnp

first = random_gnp(20, 0.3, seed=1234)
second = random_gnp(20, 0.3, seed=1234)
print(first.edges() == second.edges())

set_config(default_seed=2026)
print(random_gnp(10, 0.5).edges() == random_gnp(10, 0.5).edges())
```

Every randomized routine takes a seed and is deterministic once it has one.
Setting a process wide default makes a whole run reproducible, which is what
a benchmark, a graded exercise, or a failing test needs.

## Step nine: seeing the result

Finally, look at what we computed. The ASCII backend needs no dependencies.

```python
from discretus.viz import graph_draw, hasse_draw

print(graph_draw.draw(conflict_graph, backend="ascii"))
print(hasse_draw.draw(divides, backend="ascii"))
```

For a figure in a document, the SVG backend also needs nothing, and the
colouring we computed goes straight into the drawing as data.

```python
from discretus.viz import color_palette

svg = graph_draw.draw(
    conflict_graph,
    backend="svg",
    colors=color_palette.for_coloring(dsatur(conflict_graph)),
    labels=True,
)
print(svg[:80])
```

## Common mistakes in the first hour

Five mistakes account for most of the confusion a new reader meets. All of
them come from a convention above, and each has a one line fix.

**Expecting an operation to modify its argument.** `union(a, b)` returns a
new set and leaves both alone. If you wrote `union(a, b)` on a line by
itself and then printed `a`, nothing changed, and nothing was supposed to.
Assign the result.

**Wrapping a lazy generator in `len`.** A generator has no length.
`len(power_set(s))` raises, and `sum(1 for _ in power_set(s))` counts, while
`2 ** len(s)` computes the same number without enumerating anything.

**Reaching for the exact routine when a heuristic is wanted.**
`chromatic_number` is exponential, and on a graph with a hundred vertices it
will not finish. `dsatur` returns a colouring in near linear time. The
reference states the complexity of each, which is the information the choice
needs.

**Comparing a `FiniteSet` with a built-in set and being surprised.** They
compare equal when their members are equal, and `FiniteSet` is not a
subclass of `set`, so a function annotated for a built-in set will not
accept one without conversion. `to_frozenset()` converts, and
`FiniteSet(...)` converts back.

**Forgetting a seed and then trying to reproduce a result.** A randomized
routine without a seed is not reproducible. If you found an interesting
random graph and lost it, the graph is gone; if you had passed a seed, the
graph is one call away. Pass a seed whenever the result matters.

## How to read the reference

The reference pages are organized the same way, and knowing the shape makes
them faster to use.

Each page opens with what the package is for and the mathematics it
implements, stated as definitions and theorems. That section is worth
reading once per package, because the conventions it states, for instance
that the zero polynomial has degree minus one, explain behaviour that looks
arbitrary otherwise.

The module map comes next, and it is the fastest way to locate a routine.
The subpackages mirror how the subject is taught, so a shortest path
algorithm is under `shortest_path` and a colouring is under `coloring`.

The routines are then grouped by subject, with a table giving the meaning
and the complexity of each. The complexity column is the one to read before
calling something on a large input, and it is expressed in the quantities
that matter rather than in a bare letter.

Every page has a worked example, which is usually the fastest way to learn
the package: it is a complete program rather than a fragment, and it is the
same kind of program the test suite runs.

The errors table says which exception a routine raises and when, which
matters because the class carries information. `DomainError` means fix the
input, `InfeasibleError` means the object does not exist,
`LimitExceededError` means raise the limit or iterate lazily, and
`OptionalDependencyError` means install an extra.

The design notes at the end of each page explain the decisions that could
have gone the other way. They are not required reading, and they are where
to look when something seems arbitrary, because in most cases the reason is
recorded there.

## Exercises

These are ordered by effort, and each one is answerable with what you have
seen.

1. Add a sixth seminar, `probability`, conflicting with `numbers` and
   `sets`. Does the chromatic number change? Verify your answer twice, with
   `chromatic_number` and with the satisfiability reduction.
2. Compute the complement of the conflict graph and explain why its cliques
   are the compatible groups.
3. Find all maximum independent sets rather than one, by filtering the power
   set, and check that the largest has the size that
   `max_independent_set` reported.
4. Write the conflict graph to GraphML with `discretus.io.graphml`, read it
   back, and assert that the result equals the original.
5. Turn the divisibility order into a lattice and print its meet and join
   tables. Which pairs have no common upper bound if you remove twelve from
   the ground set?
6. Use `discretus.combinatorics.counting.binomial` to count the number of
   ways to choose three of the five seminars, then verify it by enumerating
   with `discretus.combinatorics.generation.combinations`.

## Where to go next

You have used sets, logic, graphs, and a little algebra and number theory.
The remaining tutorials go deeper into one domain each, and each assumes
only what is above.

- [Set theory](set_theory.md), for relations, orders, and lattices in
  earnest.
- [Satisfiability](sat_solving.md), for how the solver you just used
  actually works.
- [Graph algorithms](graph_algorithms.md), for traversal, shortest paths,
  spanning trees, and flow.
- [Number theory](number_theory.md), from the Euclidean algorithm to RSA.
- [Group theory](group_theory.md), from the axioms to Sylow theory.

The [quick start](../quickstart.md) is the fast version of all of them, and
the API reference in the sidebar is the place to look up a routine, its
errors, and its complexity.
