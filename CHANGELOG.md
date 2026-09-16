# Changelog

All notable changes to this project are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and the project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## How this file is maintained

Every change that a user could notice appears here, in the section of the
release that carries it. A change that no user can notice, for instance a
refactor with no behavioral effect or an adjustment to a linter
configuration, is recorded in the commit history and not here, because a
changelog that lists everything is as unhelpful as one that lists nothing.

Entries are grouped under the following headings, in this order, and a
heading is omitted when it has no entries.

| Heading | Meaning |
| --- | --- |
| Added | New public interface: a structure, a routine, a format, an option |
| Changed | Behavior of an existing public interface that is now different |
| Deprecated | Public interface that still works and will be removed |
| Removed | Public interface that is gone, with a migration note |
| Fixed | A defect corrected, with the symptom a user would have seen |
| Security | A change with a security consequence, with the advisory link |
| Performance | A measurable speed or memory improvement, with the factor |
| Documentation | A substantial documentation addition or correction |

Each entry is written from the point of view of somebody upgrading. It names
the interface, says what is different, and where the change could break
existing code it gives the replacement. An entry that only a maintainer
could understand has failed at its job.

## Versioning policy

The public interface is everything documented in the API reference and
everything reachable from a documented import path without a leading
underscore. Within a major version:

- A patch release contains fixes, performance work, and documentation. It
  never changes a documented result.
- A minor release adds interface, and may deprecate interface. It never
  removes interface and never changes a documented result, except to correct
  a result that was demonstrably wrong, which is recorded under `Fixed` with
  the old and the new behavior stated side by side.
- A major release may remove deprecated interface and may change documented
  behavior. Each such change carries a migration note.

A deprecation is announced at least one minor release before removal, and the
deprecation entry names the release in which the removal will happen. Code
that imports a name not documented as public is depending on an internal
detail and may break in any release.

## [Unreleased]

Nothing yet. Changes accumulate here between releases, and the release
process moves this section under a version heading with the date.

## [1.0.0] - 2026-01-15

The first stable release. Every documented interface in this release is
covered by the backward compatibility guarantee stated above.

The release establishes the shape of the library: a layered architecture in
which a core layer of shared abstractions supports seven domain packages,
with three cross cutting service packages above them. The computational core
requires nothing beyond the Python standard library, arithmetic is exact
wherever exactness is meaningful, randomized routines take an explicit seed,
and serialization is deterministic.

### Added

**Core layer.** The abstractions every domain builds on. The element
protocol, which normalizes nested lists, sets, and mappings into hashable
members, and a labelled element wrapper for display names. An immutability
mixin, a hashable read only mapping, and a recursive freeze helper. A
universal total order so that structures over mixed element types sort
deterministically. Canonical byte encodings and process independent digests,
which the built-in hash cannot provide because string hashing is randomized
between processes. Lazy iteration helpers, an on demand indexable sequence, a
lazy mapping, and unbounded memoization for recurrences. Logical combinators
and the finite quantifiers. A finite structure base with deterministic
element order, membership, equality by content, and a fingerprint. A closed
binary operation with axiom checks, identity and inverse search, Cayley
tables, and the Latin square test. The magma, semigroup, monoid, group, and
ring hierarchy, each class verifying only the axioms it adds. Integer
primitives including integer square and nth roots by Newton iteration,
perfect power detection, integer logarithms, and exact division. Digit and
base conversions with a transparent Karatsuba multiplication. Exact rational
helpers including continued fractions and best approximations. Immutable
exact vectors, matrices with powers by repeated squaring, and dense
polynomials with long division, composition, and Horner evaluation. Modular
arithmetic primitives including the extended Euclidean algorithm, modular
inverses and powers, linear congruences, the Chinese remainder theorem, and a
residue class type with operators. A binary relation base with the property
tests, the closures including Warshall, and the matrix and adjacency views. A
total function base with images, preimages, fibers, the injectivity and
surjectivity tests, composition, and inversion. A step recorder, a proof
trace, an explanation decorator, a LaTeX rendering mixin, and a deterministic
serialization mixin.

**Set theory.** Finite sets, bit sets for dense universes, multisets with
counting semantics, ordered sets, interval sets, sparse sets, lazy sets, and
a universal set. The set algebra with union, intersection, difference,
symmetric difference, complement, Cartesian product, power set, disjoint
union, partitions, covers, and closure operators, with lazy enumeration for
the products and power sets that are too large to materialize. Binary and
n-ary relations with the reflexivity, symmetry, antisymmetry, asymmetry,
transitivity, and totality tests, the three closures, composition, the
relation matrix, and the relation graph view. Equivalence relations with
classes, quotient sets, kernels, refinement, and a union find structure with
path compression and union by rank. Order theory with preorders, partial
orders, strict orders, total orders, chains and antichains, maximal and
minimal elements, suprema and infima, lattices including bounded and
distributive lattices, Galois connections, Dilworth's theorem, topological
extensions, and Hasse diagrams with a layout.

**Mathematical logic.** A propositional expression tree with the
connectives, a lexer and a recursive descent parser for a human friendly
syntax, an evaluator, truth tables, and the tautology, contradiction,
satisfiability, equivalence, and entailment tests. Simplification,
substitution, and text and LaTeX printers. Normal forms including negation,
conjunctive, disjunctive, and algebraic normal form, the Horn test, the
Tseitin transformation for an equisatisfiable form of linear size, the Quine
McCluskey two level minimization with prime implicants and a minimal cover,
and Karnaugh maps. Satisfiability solving with a classical DPLL procedure and
a conflict driven clause learning solver with watched literals, VSIDS
activity, conflict analysis, and restarts, together with a clause database,
an assignment structure, unit propagation, and DIMACS interchange. Predicate
logic with terms, predicates, quantifiers, interpretations over an explicit
finite domain, free and bound variable analysis, substitution, unification,
Skolemization, and prenex form. An inference layer with resolution, forward
and backward chaining, natural deduction, a sequent calculus, a proof
structure, and a proof checker.

**Combinatorics.** Counting utilities for factorials, falling and rising
factorials, permutations, combinations, multinomials, multiset permutations
and combinations, derangements, Pascal's triangle, inclusion and exclusion,
the pigeonhole principle, and the twelvefold way. Classical sequences,
namely Bell, Bernoulli, Catalan, composition, Eulerian, Fibonacci like, Lah,
Motzkin, Narayana, partition, and both kinds of Stirling numbers, all exact.
Lazy generators for permutations, combinations, subsets, subsets in Gray code
order, tuples, compositions, integer partitions, set partitions, necklaces,
and Lyndon words, with ranking and unranking that map objects bijectively to
indices. Formal power series with addition, multiplication, composition,
convolution, inversion, and coefficient extraction, for both ordinary and
exponential generating functions. Polya enumeration with cycle index
polynomials and Burnside's lemma. Combinatorial designs including block
designs, Latin squares, Steiner systems, Sperner families, and Ramsey
numbers. Discrete probability with counting probabilities, discrete
distributions, expectation, and urn models.

**Graph theory.** Graph, digraph, multigraph, weighted, labeled, bipartite,
directed acyclic, dynamic, tree, forest, and hypergraph structures, with
node and edge types and adjacency list, adjacency matrix, edge list, and
incidence matrix views. Traversal with breadth first and depth first search,
iterative depth first search, best first and bidirectional search, connected
components, strong connectivity by Tarjan and by Kosaraju, biconnected
components, articulation points, bridges, cycle detection, and topological
sorting by depth first search and by Kahn's algorithm. Shortest paths by
Dijkstra with a binary heap, Bellman Ford with negative cycle detection, the
shortest path faster algorithm, Floyd Warshall, Johnson, A star, breadth
first search for unweighted graphs, the directed acyclic graph relaxation,
Yen's algorithm and k shortest paths, and path reconstruction. Minimum
spanning trees by Kruskal, Prim, Boruvka, and reverse delete, with spanning
tree counting by the matrix tree theorem, minimum arborescence, and Steiner
trees. Network flow by Ford Fulkerson, Edmonds Karp, Dinic, and push
relabel, with the max flow min cut theorem, minimum cost flow, bipartite
matching by Hopcroft Karp, optimal assignment by the Hungarian method, and
global minimum cut by Stoer Wagner. Coloring by greedy strategies, Welsh
Powell, DSATUR, and exact backtracking, with the chromatic number, the
chromatic polynomial, edge coloring, and the bipartite test. Path analysis
for Eulerian circuits and trails by Hierholzer and by Fleury, Hamiltonian
paths and cycles, the Chinese postman problem, and exact and heuristic
travelling salesman routines. Structural properties including degrees,
connectivity, diameter, radius and center, girth, cliques, independent sets,
vertex covers, dominating sets, isomorphism, automorphism, planarity, and
Kuratowski subgraphs. Analysis including degree, closeness, and betweenness
centrality, PageRank, HITS, random walks, spectral properties, community
detection, and the Louvain method. Generators for complete, path, cycle,
star, wheel, grid, hypercube, and Petersen graphs, and for the random models
of Erdos and Renyi in both forms, Barabasi and Albert, and Watts and
Strogatz.

**Number theory.** Greatest common divisors by the Euclidean algorithm, the
extended Euclidean algorithm with Bezout coefficients, the binary algorithm,
multiple argument forms, and least common multiples. Modular arithmetic with
inverses, exponentiation, square roots by Tonelli Shanks, quadratic
residues, the Legendre and Jacobi symbols, the Chinese remainder theorem, and
discrete logarithms by baby step giant step. Primality by trial division,
the Fermat test, Miller Rabin with configurable witnesses and a deterministic
variant below a documented bound, Solovay Strassen, and a reference AKS
implementation, with the sieve of Eratosthenes, the sieve of Atkin, a linear
sieve, a segmented sieve, prime counting, prime gaps, and next prime.
Factorization by trial division, Fermat's method, Pollard's rho, Pollard's p
minus one, elliptic curve factorization, Dixon's method, a quadratic sieve,
and smoothness testing. Arithmetic functions including the Euler totient, the
Mobius function, divisor counting and summation, the Carmichael function, the
Liouville function, the von Mangoldt function, the prime omega functions,
multiplicative function machinery, and Dirichlet convolution. Diophantine
equations including linear equations, Pythagorean triples, Pell's equation,
continued fractions, and the Frobenius problem. Integer sequences including
amicable numbers, perfect numbers, Mersenne and Fermat numbers, Farey
sequences, and the Stern Brocot tree. Teaching implementations of RSA,
ElGamal, and Diffie Hellman with primitive roots, multiplicative orders, and
Lucas sequences.

**Recurrence relations.** Linear recurrence solving with characteristic
equations, homogeneous and nonhomogeneous forms, matrix formulation, matrix
exponentiation for a single term in logarithmic time, and a generating
function solver. Classical sequences including Fibonacci, Lucas, Pell,
Jacobsthal, tribonacci, factorial, and arbitrary memoized recursions. The
Master Theorem with its three cases, the Akra Bazzi method for unbalanced
divisions, recursion trees, the substitution method, and complexity class
reporting. Divide and conquer analysis with a cost model and worked
examples. Nonlinear recurrences with fixed point analysis, iteration, and
the logistic map. Asymptotic comparison with big O, big Omega, and big Theta
relations and a growth comparator.

**Abstract algebra.** Groups including cyclic, symmetric, alternating,
dihedral, Klein, quaternion, permutation, and direct product groups, with
subgroups, normal subgroups, cosets, quotient groups, homomorphisms,
isomorphisms, automorphisms, generators, element and group order, Lagrange's
theorem, Sylow's theorems, Cayley tables, Cayley graphs, group actions, and
the orbit stabilizer theorem. Rings including commutative rings, integral
domains, modular integer rings, polynomial rings, quotient rings, ideals,
units, zero divisors, characteristic, and ring homomorphisms. Fields
including prime fields, finite and Galois fields, the binary field, field
extensions, minimal polynomials, and the rational field. Polynomials with
exact arithmetic, division with remainder, greatest common divisors,
factorization, evaluation, interpolation, derivatives, resultants, roots, and
cyclotomic polynomials. Exact linear algebra with vectors, matrices,
determinants, Gaussian elimination, rank, inverses, LU decomposition,
eigenvalues, boolean matrices, and modular matrices. Algebraic lattices
including modular, complemented, and boolean structures.

**Visualization.** Pluggable backends registered through a central registry,
namely ASCII, SVG, Graphviz, and matplotlib, with graph drawing, several
layouts including circular, spring, and force directed, Hasse diagram and
lattice drawing, tree drawing, truth table and Karnaugh map rendering,
matrix heatmaps, Venn diagrams, colour palettes, DOT export, and LaTeX
rendering. Every backend is optional and the core never imports one.

**Interchange.** Deterministic readers and writers for GraphML, GML,
DIMACS, JSON, CSV, edge lists, and adjacency data, a LaTeX exporter, and a
pickle helper documented as unsafe for untrusted input. The same object
always produces byte identical output, which makes results suitable for
version control.

**Utilities.** Timing, memoization, bit manipulation, formatting, validation,
iteration helpers, comparison helpers, a prime cache, progress reporting,
seeded randomness, and optional parallel mapping.

**Command line interface.** One shot commands for primality testing,
factorization, formula conversion to conjunctive normal form, and graph
inspection, intended for shell pipelines and grading scripts.

**Project infrastructure.** Documentation with an API reference and six
tutorials, fifteen runnable examples, a benchmark suite, a test suite
combining example based, property based, and cross validation tests, a
quality gate of formatting, lint, typing, security, and prose checks across
five interpreter versions and three operating systems, archival and citation
metadata, and a container image.

### Security

- The library is released under the Mozilla Public License 2.0, and every
  source file carries the license notice, because the license applies per
  file.
- The cryptographic primitives are documented as teaching implementations
  that are not hardened against side channel attacks and must not be used to
  protect real secrets. `SECURITY.md` states the scope of security reports
  in detail.
- Releases are published from a tagged commit through trusted publishing, so
  no long lived credential for the package index exists anywhere in the
  project.

### Documentation

- A complete README covering the mathematical scope, the design philosophy,
  the architecture, installation, a quick start, one section per domain with
  runnable examples, a complexity reference, and a glossary.
- Every public routine documents its parameters, return value, exceptions,
  and asymptotic complexity, and carries a doctest that the documentation
  job executes.

[Unreleased]: https://github.com/olaflaitinen/discretus/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/olaflaitinen/discretus/releases/tag/v1.0.0
