# discretus

{{ summary }}

discretus implements the core theory and algorithms of discrete mathematics
for Python. It spans seven foundational domains, namely set theory,
mathematical logic, combinatorics, graph theory, number theory, recurrence
relations, and abstract algebra, and it exposes all of them through a single
coherent interface with consistent naming, predictable data structures, and
uniform error handling.

```{toctree}
:maxdepth: 2
:caption: Getting started

installation
quickstart
```

```{toctree}
:maxdepth: 2
:caption: Tutorials

tutorials/getting_started
tutorials/set_theory
tutorials/sat_solving
tutorials/graph_algorithms
tutorials/number_theory
tutorials/group_theory
```

```{toctree}
:maxdepth: 2
:caption: API reference

api/core
api/sets
api/logic
api/combinatorics
api/graphs
api/number_theory
api/recurrences
api/algebra
api/viz
api/io
api/utils
```

```{toctree}
:maxdepth: 1
:caption: Project

contributing
changelog
```

## What discretus is for

The library was written to serve three audiences at once, and the design
reflects all three rather than compromising between them.

A **learner** needs building blocks that map directly onto the definitions
and theorems in a textbook. When the notes say that a relation is transitive
when every two composable pairs compose, the library should have a routine
called `is_transitive` whose implementation a reader can check against the
definition in a minute. When the notes prove that the transitive closure can
be computed in cubic time by Warshall's algorithm, the library should compute
it by Warshall's algorithm and say so. discretus keeps its reference
implementations readable for exactly this reason, and it provides a step
recording mode that turns a computation into a narrated derivation.

An **educator** needs primitives that can be trusted in coursework, in
worked examples, and in automated assessment. That requires exactness, so
that a hand computed answer and a computed answer agree; determinism, so
that the answer does not depend on which machine graded it; and stable
output, so that a generated exercise is the same exercise next term. It also
requires output that can be embedded in materials, which is why many objects
render themselves to LaTeX and why the visualization package can draw a
Hasse diagram, a Karnaugh map, or a Cayley graph.

A **practitioner** needs routines that are correct, composable, and fast
enough, inside systems where discrete structures appear without being the
point: a scheduler that is really a graph colouring, a verifier that is
really a satisfiability instance, a compiler pass that is really a dominator
computation, a protocol that is really modular arithmetic. That requires an
installation with no build step, a small import surface, no global state,
and no surprises. The computational core of discretus depends on nothing
beyond the Python standard library.

## Why one library rather than several

The Python ecosystem has excellent numerical and symbolic tools, and yet
discrete mathematics is scattered across a patchwork of narrow packages. A
student who wants to build a truth table, compute a chromatic number, factor
an integer, and construct a Cayley table typically installs four unrelated
libraries, learns four unrelated conventions, and then writes glue between
four incompatible data models. One library encodes a graph as a dictionary
of lists, another as an adjacency matrix with integer labels, a third as an
object whose vertices must be hashable but whose edges must be tuples of a
particular arity. Permutations are one line notation in one package and
cycle notation in another. Errors arrive as `ValueError`, `KeyError`,
`AssertionError`, and bare `Exception`.

discretus removes that fragmentation. There is one vocabulary, one import
root, and one set of conventions, which means a reader learns a single
mental model and applies it in every domain. The gain is largest exactly
where the mathematics is most interesting, at the boundaries between
domains: a relation becomes a directed graph, a graph becomes a matrix, a
matrix is read over a finite field, and a finite group emits a Cayley graph
that the graph package can traverse and draw.

## Architecture at a glance

The library is layered, and the dependency direction is strict and acyclic.

| Layer | Packages | Depends on |
| --- | --- | --- |
| Core | `discretus.core` | Standard library only |
| Domains | `sets`, `logic`, `combinatorics`, `graphs`, `number_theory`, `recurrences`, `algebra` | Core, utils |
| Services | `viz`, `io`, `utils` | Core, and the domains they serve |

The core layer defines what every domain shares: what it means to be a
member of a structure, what a relation and a function are, what closure,
identity, and inverse mean, how exact integers, rationals, vectors,
matrices, and polynomials behave, how modular arithmetic works, how a
derivation is recorded, and how an object renders itself to LaTeX. Because
these abstractions are centralized, the domain packages stay small and
mutually consistent, and the property that reflexivity means the same thing
in the set package as in the order package is a fact about the code rather
than a coincidence.

The domain packages never import one another. Interoperability is provided
through explicit, documented conversions, which keeps the import graph
acyclic, keeps startup fast, and makes it possible to reason about what a
program actually exercises. A domain package is further divided into
subpackages that mirror how the subject is taught, so a reader who knows the
mathematics can navigate the source tree by intuition: shortest path
algorithms live under `graphs/shortest_path/`, one file per algorithm, named
after it.

Domain packages are imported on first use rather than at import time, so a
program that needs only number theory does not pay for the graph and logic
packages.

```python
import discretus

# The number theory package is imported here, and nothing else is.
discretus.number_theory.primes.is_prime(97)
```

## Design principles

**Correctness first.** Every public routine is covered by unit tests,
property based tests where a law can be stated, and cross validation against
an independent implementation. Where a naive method and an advanced method
both exist, the advanced one is validated against the naive one on
randomized inputs, so that an optimization can never silently change a
result. Correctness is treated as an invariant rather than a feature.

**One obvious way.** There is a single clear entry point per concept.
Function names read like the mathematics they encode, argument orders are
consistent across modules, and return types are stable and documented. A
reader who knows the name of an operation can usually guess the name of the
routine and be right.

**Explicit over implicit.** Objects do not mutate. Randomized routines
require a seed to be reproducible. Conversions between representations are
named operations rather than hidden coercions. Every meaningful
transformation appears in the source as a deliberate call, which is what
makes a program written with this library reviewable.

**Composability.** Data structures are designed to flow between packages.
The seven domains are interoperable views of the same discrete objects
rather than isolated silos.

**Transparency.** Selected routines record their intermediate steps, and
many objects render themselves to LaTeX. A computation can therefore explain
itself, which turns the library into a communication tool and not merely a
calculator.

## Conventions you can rely on

These choices are consistent throughout the library, and knowing them
removes most of the surprises a new reader might otherwise meet.

- Members of a structure may be any hashable value. Nothing assumes that
  vertices are integers or that set members are comparable with one another.
  Output that has an order is sorted through a universal total order, so it
  never depends on hash values and therefore never differs between
  processes.
- Arithmetic is exact. Integers are unbounded and rationals are
  `fractions.Fraction`. A float appears only where the mathematics is
  genuinely approximate, and the tolerance is then documented.
- The natural numbers include zero, the empty sum is zero, and the empty
  product is one, so a routine over an empty collection returns the unit of
  its operation instead of raising.
- The zero polynomial has degree minus one.
- A graph is simple unless its type says otherwise. Self loops and parallel
  edges belong to the multigraph type.
- Indices in ranking and unranking are zero based, and the enumeration order
  is documented per routine.
- Every error raised deliberately derives from `DiscretusError`, so library
  failures can be caught as a group.
- Randomized routines take a `seed` argument and are deterministic once it is
  supplied.
- Serialization is deterministic: the same object always produces byte
  identical output, which makes results diffable and reproducible.

## A first taste

The following program touches four domains in a dozen lines, which is the
clearest short demonstration of what a unified interface buys.

```python
from discretus.sets import FiniteSet
from discretus.sets.operations import intersection, union
from discretus.logic.propositional import is_tautology, parse
from discretus.graphs import Graph
from discretus.graphs.shortest_path import dijkstra
from discretus.number_theory.primes import is_prime

a = FiniteSet({1, 2, 3})
b = FiniteSet({3, 4, 5})
print(union(a, b))
print(intersection(a, b))

print(is_tautology(parse("(p -> q) & (q -> r) -> (p -> r)")))

g = Graph()
g.add_edge("A", "B", weight=4)
g.add_edge("A", "C", weight=1)
g.add_edge("C", "B", weight=2)
print(dijkstra(g, source="A")[0]["B"])

print(is_prime(2_147_483_647))
```

The [quick start](quickstart.md) walks through this program line by line and
then goes further, and the [tutorials](tutorials/getting_started.md) treat
each domain in turn.

## The seven domains in brief

Each domain has its own tutorial and its own reference page. This section is
a one paragraph orientation to each, so that you can tell at a glance where
the routine you need is likely to live.

### Set theory

`discretus.sets` provides finite sets, bit sets for dense universes,
multisets with counting semantics, ordered sets, and interval sets, all under
a shared operation vocabulary, so an algorithm written against the abstract
interface works with any representation. On top of them sit the set algebra,
with lazy enumeration for the products and power sets that are too large to
materialize, binary and n-ary relations with the full battery of property
tests and the three closures, equivalence relations with classes, quotients,
and a union find structure, and order theory with posets, chains and
antichains, bounds, lattices, Galois connections, and Hasse diagrams. The
package is where most cross domain work begins, because a relation is the
common ancestor of an order, a graph, and an equivalence.

$$A \cap (B \cup C) = (A \cap B) \cup (A \cap C), \qquad |\mathcal{P}(A)| = 2^{|A|}.$$

### Mathematical logic

`discretus.logic` models propositional formulas as expression trees that can
be built programmatically or parsed from a readable syntax, and it evaluates
them, tabulates them, and decides tautology, contradiction, satisfiability,
equivalence, and entailment. Above that sit the normal forms, including the
Tseitin transformation, which produces an equisatisfiable conjunctive form
whose size grows linearly rather than exponentially, and the Quine McCluskey
procedure, which reports prime implicants and a minimal cover. The
satisfiability layer offers a classical DPLL procedure for instruction and a
conflict driven clause learning solver with watched literals and activity
based decisions for real instances, and it reads and writes DIMACS. Predicate
logic adds terms, quantifiers, interpretations over an explicit finite
domain, unification, and Skolemization, and the inference layer adds
resolution, chaining, natural deduction, and a proof checker.

$$\lnot (p \lor q) \equiv \lnot p \land \lnot q, \qquad p \rightarrow q \equiv \lnot p \lor q.$$

### Combinatorics

`discretus.combinatorics` counts, generates, and enumerates. The counting
layer covers factorials, arrangements, selections, multinomials, multiset
variants, derangements, inclusion and exclusion, and the twelvefold way. The
sequence layer computes the classical integer sequences exactly, including
Catalan, Bell, both kinds of Stirling numbers, Bernoulli, Eulerian, Lah,
Motzkin, Narayana, and partition numbers. The generation layer yields
combinatorial objects lazily, so that a space far too large to hold in
memory can still be iterated, and it provides ranking and unranking that map
objects bijectively to indices. Above these sit formal power series, Polya
enumeration with cycle index polynomials and Burnside's lemma, combinatorial
designs, and discrete probability.

$$\binom{n}{k} = \binom{n-1}{k-1} + \binom{n-1}{k}, \qquad C_n = \frac{1}{n+1}\binom{2n}{n}.$$

### Graph theory

`discretus.graphs` is the largest package. It provides directed and
undirected graphs, weighted and unweighted, simple graphs and multigraphs,
along with trees, forests, bipartite graphs, directed acyclic graphs, and
hypergraphs, and it exposes adjacency list, adjacency matrix, edge list, and
incidence matrix views so that an algorithm can choose the representation it
needs. The algorithm layers cover traversal and connectivity, shortest
paths, minimum spanning trees, network flow and matching, colouring,
Eulerian and Hamiltonian analysis, structural properties, centrality, and
generators for the classical families and the standard random models.

$$\sum_{v \in V} \deg(v) = 2\,|E|, \qquad \text{Dijkstra: } O\big((|V| + |E|) \log |V|\big).$$

### Number theory

`discretus.number_theory` computes over unbounded integers throughout. It
covers greatest common divisors and Bezout coefficients, modular arithmetic
including inverses, exponentiation, square roots, quadratic residues, and
the Chinese remainder theorem, primality testing from trial division through
Miller Rabin with a deterministic variant below a documented bound,
factorization from trial division through Pollard's methods and a quadratic
sieve, the arithmetic functions with Dirichlet convolution, diophantine
equations, classical integer sequences, and teaching implementations of RSA,
ElGamal, and Diffie Hellman.

$$a x + b y = \gcd(a, b), \qquad a^{\varphi(n)} \equiv 1 \pmod{n} \text{ when } \gcd(a, n) = 1.$$

### Recurrence relations

`discretus.recurrences` solves linear recurrences with constant
coefficients, symbolically where a closed form exists and by matrix
exponentiation when a single distant term is wanted, which costs a
logarithmic number of matrix multiplications rather than a linear number of
additions. It provides the classical sequences, the Master Theorem with its
three cases and the Akra Bazzi method for unbalanced divisions, recursion
trees, nonlinear iteration with fixed point analysis, and asymptotic
comparison.

$$a_n = c_1 a_{n-1} + \dots + c_k a_{n-k}, \qquad T(n) = a\,T(n/b) + f(n).$$

### Abstract algebra

`discretus.algebra` builds structures from the axioms up. Groups include the
cyclic, symmetric, alternating, dihedral, Klein, quaternion, permutation,
and direct product families, with subgroups, cosets, quotients, morphisms,
Lagrange's theorem, Sylow's theorems, actions, and the orbit stabilizer
theorem. Rings add ideals, units, zero divisors, and characteristic. Fields
include prime fields, Galois fields, and extensions with minimal
polynomials. Polynomials support exact arithmetic, division, greatest common
divisors, factorization, and interpolation, and the linear algebra layer is
exact over the rationals and over modular rings.

$$|H| \text{ divides } |G|, \qquad |G| = |\mathrm{Orb}(x)| \cdot |\mathrm{Stab}(x)|.$$

## Reproducibility and determinism

Reproducibility is a design requirement rather than a side effect, because
the library is used for assessment and for research, and both demand that a
result obtained today can be obtained again tomorrow on another machine.
Four decisions carry that requirement.

**Exact arithmetic.** Where the mathematics is exact, the computation is
exact. There is no accumulation of rounding error, no dependence on the
width of a machine word, and no difference between platforms.

**Deterministic ordering.** Anything the library returns in an order is
sorted through a universal total order defined in the core layer. Python
randomizes string hashing between processes, so an implementation that
iterated a set and returned the result would produce different output on
different runs. discretus never does that.

**Explicit seeds.** A randomized routine takes a seed and is deterministic
once it is supplied. The library never touches the global random state, so
it cannot perturb, or be perturbed by, the randomness your own program uses.

```python
from discretus.graphs.generators import random_gnp

first = random_gnp(20, 0.3, seed=1234)
second = random_gnp(20, 0.3, seed=1234)
assert first.edges() == second.edges()
```

**Stable serialization.** Every writer in `discretus.io` produces byte
identical output for an equal object, so a computed structure can be
committed to version control and a change in a diff means a change in the
mathematics rather than a change in iteration order.

## Performance expectations

The library is pure Python, which sets the constant factor, and the
asymptotic behaviour is the one the documentation states for each routine.
Three practices keep that honest.

First, every nontrivial routine documents its complexity in its docstring
and in the reference, in terms of the quantities that matter, so the cost of
a call is visible before it is made. Second, where a transparent reference
implementation and a tuned implementation both exist, both are shipped, the
tuned one is validated against the reference on randomized inputs, and the
documentation says which is which. Third, a benchmark suite tracks
performance across releases so that a regression is caught by measurement
rather than by a user.

Practical guidance: prefer the exact routines, because they are the
documented ones; choose the representation an algorithm wants, since a dense
adjacency matrix and a sparse adjacency list differ by orders of magnitude on
the right input; and lower the enumeration limit in a service, because the
default is chosen for interactive use.

## Where to go next

| If you want to | Read |
| --- | --- |
| Install the library and the optional extras | [Installation](installation.md) |
| See the whole interface in fifteen minutes | [Quick start](quickstart.md) |
| Learn the library domain by domain | [Getting started tutorial](tutorials/getting_started.md) |
| Look up a routine, its complexity, and its errors | The API reference in the sidebar |
| Understand how a solver or an algorithm works | The tutorial for that domain |
| Contribute a change | [Contributing](contributing.md) |
| See what changed between versions | [Changelog](changelog.md) |

## Scope and limits

It is worth being clear about what the library does not attempt.

- It is not a computer algebra system. There is no symbolic manipulation of
  expressions with free variables, no integration, and no equation solving
  outside the specific discrete settings the domains cover.
- It is not a numerical library. Floating point linear algebra, optimization,
  and statistics belong elsewhere, and the exact linear algebra here is
  sized for the discrete problems that need it rather than for large dense
  systems.
- It is not a production cryptography library. The primitives in
  `number_theory.crypto` are teaching implementations, they are not hardened
  against side channels, and they must not be used to protect real secrets.
  The number theory beneath them is correctness critical and is treated as
  such.
- It does not attempt to beat a specialized solver at its own game. The
  satisfiability solver is a competent conflict driven implementation
  suitable for instructional and moderate industrial instances, and it reads
  and writes DIMACS so that a hard instance can be handed to a dedicated
  tool.

Exponential problems remain exponential. Exact graph colouring, Hamiltonian
path detection, and exhaustive enumeration are provided because they are
part of the subject, and each one documents its complexity so that the cost
is visible before it is paid. The configurable enumeration limit prevents an
accidental request for an astronomically large structure from consuming a
machine.

## Stability

The project follows semantic versioning. Within a major version the public
interface is backward compatible, a deprecation is announced at least one
minor release before removal, and every breaking change carries a migration
note in the changelog. Anything not documented as public is internal and may
change without notice.

## Citing discretus

If the library contributes to academic work, please cite it. The
authoritative metadata is in `CITATION.cff` in the repository, which most
reference managers read directly, and the same information is available in
`codemeta.json` and `.zenodo.json`.

```bibtex
@software{discretus,
  title   = {discretus: A Discrete Mathematics library for Python},
  author  = {Laitinen Imanov, Olaf Yunus},
  year    = {2026},
  version = {1.0.0},
  url     = {https://github.com/olaflaitinen/discretus}
}
```

Please cite the version you used, since the interface is guaranteed only
within a major version, and please also cite the original source of any
specific algorithm, which the docstring names.

## Author

{{ author }}, Student Researcher.

{{ affiliation }}.

Correspondence: <yimanov@student.uef.fi>. ORCID:
[0009-0006-5184-0810](https://orcid.org/0009-0006-5184-0810).

## License

discretus is released under the Mozilla Public License 2.0, a file level
weak copyleft license. It allows use, modification, distribution, and sale,
and it allows the library to be combined with code under any other license,
including a proprietary one. In exchange, a file of this library that you
modify and distribute must be made available under the same license, and the
license notice and the disclaimers must be preserved. The full text is in
`LICENSE` and the copyright notice is in `NOTICE`.

- Repository: {{ repository }}
- Documentation: {{ documentation }}
- Version documented here: {{ version }}
