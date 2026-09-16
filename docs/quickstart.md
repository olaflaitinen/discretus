# Quick start

This page is a guided tour of the whole library in one sitting. It moves
through the seven domains in the order they are usually taught, shows the
cross domain conversions that make a unified library worth having, and ends
with the configuration, error handling, and output facilities that apply
everywhere.

Every block runs as written on a fresh installation with no extras. Blocks
that need the visualization extra are marked.

If you prefer to learn one domain thoroughly rather than all seven quickly,
start with the [getting started tutorial](tutorials/getting_started.md)
instead.

## Installing and checking

```bash
pip install discretus
python -c "import discretus; print(discretus.__version__)"
```

## Sets

A set is an unordered collection of distinct members. The finite set is a
hashable, immutable value type, so it can itself be a member of another set,
which is what makes the set of subsets of a set expressible directly.

```python
from discretus.sets import FiniteSet
from discretus.sets.operations import (
    cartesian_product,
    difference,
    intersection,
    power_set,
    symmetric_difference,
    union,
)

a = FiniteSet({1, 2, 3})
b = FiniteSet({2, 3, 4})

print(union(a, b))                    # {1, 2, 3, 4}
print(intersection(a, b))             # {2, 3}
print(difference(a, b))               # {1}
print(symmetric_difference(a, b))     # {1, 4}
print(a.is_subset(FiniteSet({1, 2, 3, 4})))
print(len(list(power_set(a))))        # 8
print(len(list(cartesian_product(a, b))))
```

Two properties of the printed output are worth noticing immediately, because
they hold throughout the library. The members appear in a deterministic
order, sorted through a universal total order rather than in hash order, so
the same set prints the same way in every process. And the operations return
new objects: nothing you passed in was modified.

The power set and the Cartesian product are lazy. The call above wraps them
in `list` because the sets are tiny; for a larger ground set, iterate
instead, and nothing is materialized.

```python
for subset in power_set(FiniteSet(range(20))):
    if len(subset) == 19:
        print(subset)
        break
```

A set whose ground universe is dense and integer valued has a compact
representation, and a set whose members repeat has a counting one. Both
speak the same operation vocabulary.

```python
from discretus.sets import BitSet, Multiset

dense = BitSet(range(0, 100, 3))
print(len(dense), 33 in dense)

bag = Multiset("mississippi")
print(bag.multiplicity("s"), bag.distinct_count(), len(bag))
```

## Relations and orders

A binary relation is a set of ordered pairs over a ground set. It is the
object that ties several domains together: an order is a relation with three
properties, an equivalence is a relation with three others, and a directed
graph is a relation drawn differently.

```python
from discretus.sets.relations import Relation

r = Relation(domain={1, 2, 3}, pairs={(1, 2), (2, 3)})

print(r.is_reflexive(), r.is_symmetric(), r.is_transitive())
print(sorted(r.transitive_closure().pairs))
print(r.properties())
print(r.matrix())
```

The transitive closure is computed by Warshall's algorithm in cubic time, and
the reference entry says so. Asking for the closure of a relation that is
already transitive returns an equal relation rather than doing nothing
visible, which is what the mathematics requires.

A partial order can be given by its comparison rule rather than by listing
its pairs, which is how divisibility orders and subset orders are usually
described.

```python
from discretus.sets.orders import PartialOrder

divides = PartialOrder.from_relation(
    ground={1, 2, 3, 4, 6, 12},
    leq=lambda x, y: y % x == 0,
)

print(divides.minimal_elements(), divides.maximal_elements())
print(divides.is_lattice())
print(divides.meet(4, 6), divides.join(4, 6))
print(divides.covers(2))
print(divides.height())
```

An equivalence relation partitions its ground set, and the partition is the
object you usually want.

```python
from discretus.sets.equivalence import EquivalenceRelation

mod3 = EquivalenceRelation.from_kernel(range(10), key=lambda n: n % 3)
print(mod3.classes())
print(mod3.class_of(7))
print(mod3.quotient_set())
```

## Logic

A propositional formula is an expression tree. Build it programmatically or
parse it from a readable syntax that accepts several spellings of each
connective.

```python
from discretus.logic.propositional import (
    are_equivalent,
    is_contradiction,
    is_satisfiable,
    is_tautology,
    parse,
    truth_table,
)

phi = parse("(p -> q) & (q -> r) -> (p -> r)")
print(is_tautology(phi))
print(is_satisfiable(parse("p & ~p")), is_contradiction(parse("p & ~p")))
print(are_equivalent(parse("~(p & q)"), parse("~p | ~q")))
print(truth_table(parse("p & (q | r)")))
```

The truth table prints as an aligned text table, and the same object renders
to LaTeX for a handout with `to_latex`.

Normal forms are next. The naive conversion to conjunctive form can grow
exponentially, so the Tseitin transformation is available when only
satisfiability has to be preserved, and it grows linearly.

```python
from discretus.logic.normal_forms import minimize, to_cnf, to_dnf, tseitin

print(to_cnf(parse("p -> (q -> r)")))
print(to_dnf(parse("(p | q) & r")))
print(tseitin(parse("(p <-> q) <-> (r <-> s)")).clause_count())
print(minimize(parse("(p & ~q) | (p & q)")))
```

Satisfiability solving is a first class part of the package. The classical
procedure is there to be read, and the conflict driven solver is there to be
used.

```python
from discretus.logic.sat import solve, solve_dpll, Cnf

formula = parse("(p | q) & (~p | r) & (~q | ~r)")
model = solve(formula)
print(model)
print(model.satisfies(formula))

print(solve_dpll(formula).assignment)

# DIMACS interchange, so a hard instance can go to a dedicated tool.
instance = Cnf.from_formula(formula)
print(instance.to_dimacs())
```

Predicate logic evaluates a quantified sentence against an explicit finite
interpretation, which makes model theory something a reader can experiment
with rather than only prove about.

```python
from discretus.logic.predicate import Interpretation, parse_formula

interpretation = Interpretation(
    domain={0, 1, 2, 3},
    predicates={"Even": lambda n: n % 2 == 0, "Lt": lambda x, y: x < y},
)

print(interpretation.evaluate(parse_formula("forall x. exists y. Lt(x, y)")))
print(interpretation.evaluate(parse_formula("exists x. Even(x) & Lt(x, 1)")))
```

## Combinatorics

Counting first. Everything is exact, so a result with two hundred digits is
simply a two hundred digit integer.

```python
from discretus.combinatorics.counting import (
    binomial,
    combinations_count,
    derangements,
    multinomial,
    permutations_count,
)

print(permutations_count(10, 3), combinations_count(10, 3))
print(binomial(100, 50))
print(multinomial([3, 2, 1]))
print(derangements(6))
```

The classical sequences are computed with the recurrences that define them
and memoized, so a later term costs nothing after an earlier one.

```python
from discretus.combinatorics.sequences import (
    bell,
    catalan,
    partition_number,
    stirling_second,
)

print([catalan(n) for n in range(8)])
print(bell(6), stirling_second(5, 2), partition_number(20))
```

Generation is lazy, and ranking maps an object to its index in a fixed order
and back, which is what lets a program address a combinatorial space without
enumerating it.

```python
from discretus.combinatorics.generation import (
    integer_partitions,
    permutation_rank,
    permutation_unrank,
    subsets_gray_code,
)

print(list(subsets_gray_code([1, 2, 3])))
print(list(integer_partitions(5)))

print(permutation_rank((2, 0, 1)))
print(permutation_unrank(3, 1_000_000))
```

## Graphs

A graph is built by adding edges; the vertices appear as they are mentioned.
Vertices may be any hashable value, and here they are strings.

```python
from discretus.graphs import Graph
from discretus.graphs.traversal import bfs, connected_components, dfs
from discretus.graphs.shortest_path import bellman_ford, dijkstra, floyd_warshall
from discretus.graphs.spanning import kruskal, prim
from discretus.graphs.coloring import chromatic_number, is_bipartite
from discretus.graphs.paths import has_eulerian_circuit, has_hamiltonian_path

g = Graph()
g.add_edges_from([("A", "B", 4), ("A", "C", 1), ("C", "B", 2), ("B", "D", 5)])

print(g.order(), g.size())
print(g.degree("B"), g.neighbors("B"))

print(list(bfs(g, "A")), list(dfs(g, "A")))
print(connected_components(g))

distances, predecessors = dijkstra(g, "A")
print(distances["D"])
print(dijkstra(g, "A", target="D")[0])

print(bellman_ford(g, "A")[0] == distances)
print(floyd_warshall(g)["A"]["D"])

print(sum(weight for _, _, weight in kruskal(g)))
print(sum(weight for _, _, weight in prim(g)))

print(chromatic_number(g), is_bipartite(g))
print(has_eulerian_circuit(g), has_hamiltonian_path(g))
```

Notice that Dijkstra and Bellman Ford agree. That is not a coincidence in
the tests either: the two are cross validated against one another on
randomized graphs, because a graph with non negative weights must give both
the same answer.

Directed graphs add the algorithms that need a direction.

```python
from discretus.graphs import DiGraph
from discretus.graphs.traversal import (
    strongly_connected_components,
    topological_sort,
)

d = DiGraph()
d.add_edges_from([("a", "b"), ("b", "c"), ("c", "a"), ("c", "d")])

print(strongly_connected_components(d))
print(d.is_acyclic())

dag = DiGraph()
dag.add_edges_from([("shirt", "tie"), ("tie", "jacket"), ("belt", "jacket")])
print(topological_sort(dag))
```

Flow and matching follow, with the theorem that connects them.

```python
from discretus.graphs import DiGraph
from discretus.graphs.flow import edmonds_karp, max_flow_min_cut

net = DiGraph()
net.add_edges_from([
    ("s", "u", 10), ("s", "v", 5),
    ("u", "v", 15), ("u", "t", 5),
    ("v", "t", 10),
])

value, flow = edmonds_karp(net, "s", "t")
cut_value, partition = max_flow_min_cut(net, "s", "t")
print(value, cut_value, value == cut_value)
```

Generators produce the classical families and the standard random models,
and the random ones take a seed.

```python
from discretus.graphs.generators import complete_graph, petersen_graph, random_gnp

print(complete_graph(5).size())
print(petersen_graph().order())

first = random_gnp(20, 0.3, seed=1234)
second = random_gnp(20, 0.3, seed=1234)
print(first.edges() == second.edges())
```

## Number theory

Everything here is exact over unbounded integers.

```python
from discretus.number_theory.gcd import extended_gcd, gcd, lcm
from discretus.number_theory.modular import crt, discrete_log, mod_exp, mod_inverse
from discretus.number_theory.primes import is_prime, next_prime, primes_up_to
from discretus.number_theory.factorization import factorize
from discretus.number_theory.functions import divisor_count, euler_totient, mobius

print(gcd(462, 1071), lcm(4, 6))
print(extended_gcd(462, 1071))

print(mod_inverse(3, 11), mod_exp(7, 128, 13))
print(crt([2, 3, 2], [3, 5, 7]))
print(discrete_log(2, 3, 101))

print(primes_up_to(30))
print(is_prime(2_147_483_647), next_prime(1_000_000))
print(factorize(600_851_475_143))

print(euler_totient(36), mobius(30), divisor_count(360))
```

The Bezout coefficients returned by the extended algorithm satisfy the
identity they are defined by, which is worth checking once so that the
argument order is never in doubt:

```python
g, x, y = extended_gcd(462, 1071)
assert 462 * x + 1071 * y == g
```

## Recurrences

A linear recurrence can be evaluated term by term, solved in closed form
where one exists, or evaluated at a single distant index by matrix
exponentiation, which costs a logarithmic number of matrix multiplications.

```python
from discretus.recurrences.sequences import fibonacci, lucas
from discretus.recurrences.linear import solve_linear_recurrence
from discretus.recurrences.master_theorem import master_theorem

print(fibonacci(50), lucas(20))
print(fibonacci(1000).bit_length())

print(solve_linear_recurrence(coefficients=[1, 1], initial=[0, 1], n=10))

print(master_theorem(a=2, b=2, f_exponent=1))
print(master_theorem(a=8, b=2, f_exponent=2))
```

The Master Theorem result reports which of the three cases applies and the
resulting growth class, rather than only the bound, because the case is the
part a reader is usually trying to learn.

## Algebra

Structures verify their axioms when they are constructed, so an object of a
given type is guaranteed to satisfy that type's axioms for its whole
lifetime.

```python
from discretus.algebra.groups import CyclicGroup, DihedralGroup, SymmetricGroup

z6 = CyclicGroup(6)
print(z6.order(), z6.is_abelian())
print(z6.element_orders())
print([subgroup.order() for subgroup in z6.subgroups()])
print(z6.cayley_table())

s3 = SymmetricGroup(3)
print(s3.order(), s3.is_abelian())
print([len(cls) for cls in s3.conjugacy_classes()])

d4 = DihedralGroup(4)
print(d4.order(), [n.order() for n in d4.normal_subgroups()])
```

Lagrange's theorem is visible in the third line: every subgroup order
divides six. The library does not merely allow you to check that, it relies
on it internally when it searches for subgroups.

Rings, fields, and polynomials follow the same pattern.

```python
from discretus.algebra.rings import Zmod
from discretus.algebra.fields import GaloisField, PrimeField
from discretus.algebra.polynomials import Polynomial

r = Zmod(12)
print(r.units(), r.zero_divisors(), r.characteristic())

f = PrimeField(7)
print(f.inverse(3), f.order())

gf = GaloisField(2, 3)
print(gf.order(), gf.is_field())

p = Polynomial([1, 0, -1])       # 1 - x squared
q = Polynomial([1, 1])           # 1 + x
print(p, q, p * q)
print(divmod(p, q))
print(p.roots())
```

## Crossing between domains

This is where a single library earns its place. Each conversion below is an
explicit, documented call rather than a coincidence of representation.

```python
from discretus.sets.relations import Relation
from discretus.sets.orders import PartialOrder
from discretus.algebra.groups import CyclicGroup

# A relation becomes a directed graph.
r = Relation(domain={1, 2, 3, 4}, pairs={(1, 2), (2, 3), (3, 4)})
graph = r.to_digraph()
print(graph.order(), graph.size())

# A graph becomes an exact matrix.
matrix = graph.adjacency_matrix()
print(matrix.power(2).rows)

# An order becomes a Hasse diagram, which is a graph.
divides = PartialOrder.from_relation({1, 2, 3, 6}, lambda x, y: y % x == 0)
print(divides.hasse_diagram().edges())

# A group becomes its Cayley graph, which the graph package can traverse.
cayley = CyclicGroup(6).cayley_graph()
print(cayley.order(), cayley.is_connected())
```

## Configuration

The library works with no configuration. Where behaviour is adjustable, it
is adjustable in one place, either process wide or for a block.

```python
from discretus.config import config_scope, get_config, set_config

print(get_config().max_enumeration)

set_config(notation="unicode")
print(get_config().notation)

with config_scope(explain=True, max_enumeration=1000):
    ...            # step recording on, enumeration bounded, inside the block
print(get_config().explain)
```

The same settings can be supplied through the environment, which is how a
container or a grading sandbox configures the library without touching code.

```bash
export DISCRETUS_MAX_ENUMERATION=10000
export DISCRETUS_NOTATION=unicode
```

## Errors

Every error the library raises deliberately derives from `DiscretusError`,
so you can catch library failures as a group and let genuine programming
mistakes propagate.

```python
from discretus import DiscretusError, DomainError, InfeasibleError
from discretus.number_theory.modular import mod_inverse
from discretus.graphs import DiGraph
from discretus.graphs.traversal import topological_sort

try:
    mod_inverse(2, 4)
except InfeasibleError as error:
    print("no inverse:", error)

cyclic = DiGraph()
cyclic.add_edges_from([("a", "b"), ("b", "a")])
try:
    topological_sort(cyclic)
except InfeasibleError as error:
    print("no topological order:", error)

try:
    mod_inverse(3, 0)
except DomainError as error:
    print("bad modulus:", error)

assert issubclass(InfeasibleError, DiscretusError)
assert issubclass(DomainError, DiscretusError)
```

The distinction the library maintains is worth internalizing:
`ValidationError` and `DomainError` mean your input was not acceptable, and
`InfeasibleError` means your input was fine and the object you asked for does
not exist.

## Explaining a computation

Selected routines record their intermediate steps, which turns a result into
a derivation.

```python
from discretus.number_theory.gcd import extended_gcd
from discretus.core.explain import explained

result, steps = explained(extended_gcd)(462, 1071)
print(result)
for label, data in steps:
    print(label, data)
```

## Output

Objects render themselves in plain text, in LaTeX for a document, and
through the visualization backends for a figure.

```python
from discretus.logic.propositional import parse, truth_table
from discretus.algebra.linear import Matrix

table = truth_table(parse("p -> q"))
print(table)
print(table.to_latex())

m = Matrix([[1, 2], [3, 4]])
print(m.to_latex())
```

Interchange formats are deterministic, so a written file is stable under
version control.

```python
from discretus.graphs import Graph
from discretus.io import graphml, json_io

g = Graph()
g.add_edges_from([("A", "B", 1), ("B", "C", 2)])

text = graphml.dumps(g)
print(text[:60])
assert graphml.loads(text) == g

payload = json_io.dumps(g)
assert json_io.dumps(json_io.loads(payload)) == payload
```

Rendering to an image needs the visualization extra, and the ASCII and SVG
backends need nothing.

```python
from discretus.viz import ascii_render, svg_backend

print(ascii_render.draw(g))
svg = svg_backend.draw(g)
print(svg[:40])
```

## The command line

For one shot work, a shell command is lighter than an interpreter session,
and the interface is designed for pipelines and grading scripts.

```bash
discretus prime 2147483647
discretus factor 600851475143
discretus cnf "p -> (q -> r)"
discretus graph --format graphml --info path/to/graph.graphml
```

## Patterns worth learning early

Five habits make the difference between using the library and fighting it.
Each one follows from a design decision described on the
[index page](index.md), and each saves time repeatedly.

### Iterate rather than materialize

Anything whose size grows exponentially is available lazily, and the lazy
form is the one to reach for by default. The power set of a thirty member
set has over a billion members, which no machine should hold, and yet
searching it for the first subset with a property is instant if the search
stops early.

```python
from discretus.sets import FiniteSet
from discretus.sets.operations import power_set

ground = FiniteSet(range(30))
for subset in power_set(ground):
    if sum(subset) == 42:
        print(subset)
        break
```

The enumeration limit exists to catch the opposite mistake, where a program
asks for the whole thing by accident. When you see
`LimitExceededError`, the right response is usually to switch to the lazy
form rather than to raise the limit.

### Choose the representation the algorithm wants

The same graph can be held as an adjacency list, an adjacency matrix, an
edge list, or an incidence matrix, and the difference is not cosmetic. A
traversal over a sparse graph wants the adjacency list, since it visits only
the edges that exist. An all pairs computation wants the matrix, since it
reads and writes every entry anyway. Converting is explicit and cheap
relative to the algorithm that follows.

```python
from discretus.graphs import Graph

g = Graph()
g.add_edges_from([("A", "B", 1), ("B", "C", 2), ("C", "A", 3)])

adjacency = g.adjacency_list()      # for traversal and Dijkstra
matrix = g.adjacency_matrix()       # for Floyd Warshall and spectral work
edges = g.edge_list()               # for Kruskal, which sorts the edges
```

The same applies to sets: the bit set is the right representation for a
dense integer universe and the wrong one for arbitrary hashable members, and
both implement the same operations so the choice is local.

### Keep arithmetic exact

The library computes exactly wherever the mathematics is exact, and the way
to lose that is to introduce a float at the boundary. Pass integers and
`Fraction` values rather than floats, and the results stay exact all the way
through.

```python
from fractions import Fraction

from discretus.algebra.linear import Matrix

exact = Matrix([[Fraction(1, 3), 1], [2, 1]])
print(exact.determinant())          # an exact Fraction

inexact = Matrix([[1 / 3, 1], [2, 1]])
print(inexact.determinant())        # a float, and no longer exact
```

Weights on a graph follow the same rule. Integer or fractional weights give
an exact shortest path distance, and float weights give an approximate one.

### Seed anything randomized

A randomized routine without a seed is not reproducible, and a result you
cannot reproduce is one you cannot debug or grade. Pass a seed at the call
site when the result matters, or set a process wide default when the whole
run should be reproducible.

```python
from discretus.config import set_config
from discretus.graphs.generators import random_gnm

set_config(default_seed=20260115)
print(random_gnm(10, 15).edges() == random_gnm(10, 15).edges())
```

### Catch the library, not the language

Catch `DiscretusError` and its subclasses. Catching `ValueError` also
catches your own conversion mistakes, and catching `Exception` hides
genuine defects in your program. The hierarchy is designed so that the
specific class tells you what to do: a `DomainError` means fix the input,
and an `InfeasibleError` means the object does not exist and the program
should branch.

## Reading the mathematics alongside the code

The library states the definitions and theorems it implements, in the
docstrings and in the reference, because the point of a readable reference
implementation is lost if a reader cannot connect it to the mathematics.

For example, the relation properties in the section above correspond to the
following definitions, and the implementation of each one is a direct
transcription.

$$
\text{reflexive: } \forall a\,(a\,R\,a), \qquad
\text{symmetric: } \forall a, b\,(a\,R\,b \Rightarrow b\,R\,a),
$$

$$
\text{antisymmetric: } \forall a, b\,(a\,R\,b \land b\,R\,a \Rightarrow a = b),
\qquad
\text{transitive: } \forall a, b, c\,(a\,R\,b \land b\,R\,c \Rightarrow a\,R\,c).
$$

A relation that is reflexive, symmetric, and transitive is an equivalence
and induces a partition. A relation that is reflexive, antisymmetric, and
transitive is a partial order. Those two sentences are the reason
`is_equivalence` and `is_partial_order` are compositions of three other
predicates rather than separate implementations, and reading the source
confirms it.

The same applies to the identities that the logic section exercises,

$$p \rightarrow q \equiv \lnot p \lor q, \qquad
p \leftrightarrow q \equiv (p \rightarrow q) \land (q \rightarrow p),$$

to the handshake lemma behind the degree computation,

$$\sum_{v \in V} \deg(v) = 2\,|E|,$$

and to Lagrange's theorem behind the subgroup search,

$$|H| \text{ divides } |G|, \qquad [G : H] = \frac{|G|}{|H|}.$$

When a docstring states a theorem, it also states the algorithm it uses and
the complexity that algorithm achieves, so the reference answers all three
of the questions a reader has: what does this compute, how does it compute
it, and what will it cost.

## A fifteen minute path through the library

If you have limited time and want the most representative tour, run these
five blocks in order. Together they touch every layer: a value type, a
parser, an exact algorithm, a solver, and a structure that verifies its own
axioms.

1. The set algebra block, which introduces immutability, deterministic
   order, and lazy enumeration.
2. The relation and order block, which introduces the property tests and the
   closures, and which is the hinge between the domains.
3. The satisfiability block, which shows a nontrivial solver behind a two
   line interface, and the DIMACS export that makes it interoperable.
4. The number theory block, which shows exactness at a scale where floating
   point would fail outright.
5. The algebra block, which shows axiom verification at construction and the
   Cayley table that makes a group concrete.

Then read the tutorial for whichever of the five interested you most.

## Where to go next

- The [tutorials](tutorials/getting_started.md) treat each domain slowly,
  with the mathematics stated alongside the code.
- The API reference in the sidebar documents every routine, its parameters,
  its errors, and its asymptotic complexity.
- The examples directory in the repository contains fifteen runnable
  programs, each one focused on a single topic.
