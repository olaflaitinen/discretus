# discretus

**discretus is a rigorous, production-grade library for Discrete Mathematics in pure Python.**

**Author:** Gustav Olaf Yunus Laitinen-Fredriksson Lundström-Imanov $^{\mathrm{a},*}$

$^{\mathrm{a}}$ School of ICT, Metropolia University of Applied Sciences, Myllypurontie 1, 00920 Helsinki, Finland

$^{*}$ Corresponding author at: School of ICT, Metropolia University of Applied Sciences, Myllypurontie 1, 00920 Helsinki, Finland. Email: yunus.imanov@metropolia.fi. Phone: +46 76 236 80 88. ORCID: 0009-0006-5184-0810.

---

[![PyPI Version](https://img.shields.io/pypi/v/discretus)](https://pypi.org/project/discretus/)
[![PyPI Downloads](https://img.shields.io/pypi/dm/discretus)](https://pypi.org/project/discretus/)
![Python Versions](https://img.shields.io/pypi/pyversions/discretus)
![Wheel](https://img.shields.io/pypi/wheel/discretus)
![Implementation](https://img.shields.io/pypi/implementation/discretus)
![Conda Version](https://img.shields.io/conda/vn/conda-forge/discretus)
![License](https://img.shields.io/pypi/l/discretus)
[![CI](https://img.shields.io/github/actions/workflow/status/olaflaitinen/discretus/ci.yml?branch=main&label=CI)](https://github.com/olaflaitinen/discretus/actions)
![Docs](https://img.shields.io/readthedocs/discretus)
![Coverage](https://img.shields.io/codecov/c/github/olaflaitinen/discretus)
![Code Style Black](https://img.shields.io/badge/code%20style-black-000000)
![Imports isort](https://img.shields.io/badge/imports-isort-1674b1)
![Type Checked mypy](https://img.shields.io/badge/type%20checked-mypy-blue)
![Linting Ruff](https://img.shields.io/badge/linting-ruff-yellow)
![Security Bandit](https://img.shields.io/badge/security-bandit-informational)
![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen)
![Semantic Versioning](https://img.shields.io/badge/semver-2.0.0-blue)
![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa)
![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen)
![OpenSSF Best Practices](https://img.shields.io/badge/OpenSSF-passing-brightgreen)
[![GitHub Stars](https://img.shields.io/github/stars/olaflaitinen/discretus)](https://github.com/olaflaitinen/discretus)
![GitHub Issues](https://img.shields.io/github/issues/olaflaitinen/discretus)
![Last Commit](https://img.shields.io/github/last-commit/olaflaitinen/discretus)
![Release](https://img.shields.io/github/v/release/olaflaitinen/discretus)
![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.0000000-blue)
![Platform](https://img.shields.io/badge/platform-linux%20%7C%20macOS%20%7C%20windows-lightgrey)
![Maintenance](https://img.shields.io/maintenance/yes/2026)

---

## Links

- Source code: https://github.com/olaflaitinen/discretus
- Python Package Index: https://pypi.org/project/discretus/
- Documentation: https://discretus.readthedocs.io
- Install: `pip install discretus`

---

## Table of Contents

1. [Introduction](#introduction)
2. [Why discretus](#why-discretus)
3. [Mathematical Scope](#mathematical-scope)
4. [Design Philosophy](#design-philosophy)
5. [Architecture](#architecture)
6. [Installation](#installation)
7. [Quick Start](#quick-start)
8. [Set Theory](#set-theory)
9. [Mathematical Logic](#mathematical-logic)
10. [Combinatorics](#combinatorics)
11. [Graph Theory](#graph-theory)
12. [Number Theory](#number-theory)
13. [Recurrence Relations](#recurrence-relations)
14. [Abstract Algebra](#abstract-algebra)
15. [Visualization](#visualization)
16. [Serialization and Interchange](#serialization-and-interchange)
17. [Complexity Reference](#complexity-reference)
18. [Performance Notes](#performance-notes)
19. [Testing and Quality](#testing-and-quality)
20. [Interoperability](#interoperability)
21. [Command Line Interface](#command-line-interface)
22. [Project Structure](#project-structure)
23. [Versioning and Stability](#versioning-and-stability)
24. [Roadmap](#roadmap)
25. [Contributing](#contributing)
26. [Security Policy](#security-policy)
27. [Frequently Asked Questions](#frequently-asked-questions)
28. [Glossary](#glossary)
29. [Citation](#citation)
30. [Acknowledgments](#acknowledgments)
31. [License](#license)
32. [Author and Contact](#author-and-contact)

---

## Introduction

discretus is a comprehensive software library that implements the core theory and algorithms of discrete mathematics for the Python programming language. It is engineered to serve three audiences at once. The first audience is learners who need transparent and well documented building blocks that map directly onto the definitions and theorems they encounter in a textbook. The second audience is educators who need dependable primitives for coursework, worked examples, and automated assessment generation, along with output that can be embedded in slides and problem sets. The third audience is practitioners who need fast, correct, and composable routines inside production systems, where discrete structures such as graphs, finite fields, and Boolean formulas appear in scheduling, verification, cryptography, compilers, and data engineering.

The library spans seven foundational domains, namely set theory, mathematical logic, combinatorics, graph theory, number theory, recurrence relations, and abstract algebra. It exposes all of them through a single coherent application programming interface with consistent naming, predictable data structures, and uniform error handling. Rather than being a loose collection of scripts, discretus is a curated and internally consistent framework in which the seven domains behave like chapters of one book. A relation defined in the set theory package can be reinterpreted as a directed graph in the graph package, a matrix produced in the graph package can be read over a finite field defined in the algebra package, and a group in the algebra package can emit a Cayley graph that the graph package can traverse and draw.

This document uses full LaTeX notation so that every definition and theorem appears in its natural mathematical form. On GitHub the equations render through the built in mathematics support, and in any LaTeX aware Markdown viewer they render as typeset mathematics. Inline mathematics is written between single dollar signs, for example $a \in A$, and display mathematics is written between double dollar signs. Throughout the document, each mathematical statement is paired with a short, runnable Python example so that the distance from a formal idea to executable code is as small as possible.

discretus is written in pure Python for its core computational layer. This means the library installs cleanly on any platform that runs a supported interpreter and carries no mandatory native dependencies. Optional acceleration and visualization backends are available as extras and are always strictly optional. The result is a library that is trivial to deploy in restricted environments such as continuous integration runners, teaching laboratories, and automated grading sandboxes, while still offering rich graphical output for interactive exploration when the optional extras are present.

## Why discretus

The Python ecosystem contains many excellent numerical and symbolic tools, yet discrete mathematics is frequently scattered across a patchwork of narrow packages. A student who wants to build a truth table, compute a chromatic number, factor an integer, and construct a Cayley table often has to install several unrelated libraries, learn several unrelated conventions, and reconcile several incompatible data models. Each library encodes graphs differently, encodes permutations differently, and reports results in different shapes. discretus exists to remove that fragmentation. It offers a unified vocabulary, a single import root, and a shared set of conventions so that a user learns one mental model and applies it everywhere.

A second reason for discretus is pedagogical clarity. Many high performance libraries optimize aggressively at the cost of readability, which makes them poor instruments for teaching. discretus takes a deliberate stance. The reference implementation of each algorithm is written to be read, and performance sensitive variants are provided as clearly separated advanced routines. A learner can study the transparent version, understand exactly how it corresponds to the underlying theorem, and then graduate to the tuned version without leaving the library or changing mental models. Selected routines can additionally record their intermediate steps, which turns an opaque computation into a narrated derivation suitable for a lecture or a debugging session.

A third reason is reproducibility for research and assessment. Educators and researchers need deterministic behavior, stable serialization, and the ability to export artifacts to publication ready formats. discretus provides deterministic algorithms by default, explicit control over any randomized routine through seedable generators, and export paths to LaTeX and common graph interchange formats. As a consequence, a result computed on one machine can be reproduced exactly on another, and a computed object such as a graph, a lattice, or a truth table can travel directly from a computation into a paper, a lecture, or an autograder without manual reformatting.

## Mathematical Scope

discretus formalizes and computes a large body of classical results. The following statements are representative rather than exhaustive, and each domain section later in this document restates them with runnable code.

The distributive laws of set algebra hold in both directions:

$$A \cap (B \cup C) = (A \cap B) \cup (A \cap C), \qquad A \cup (B \cap C) = (A \cup B) \cap (A \cup C).$$

The De Morgan laws connect complementation with union and intersection, and their logical counterparts connect negation with disjunction and conjunction:

$$\overline{A \cup B} = \overline{A} \cap \overline{B}, \qquad \overline{A \cap B} = \overline{A} \cup \overline{B},$$

$$\lnot (p \lor q) \equiv \lnot p \land \lnot q, \qquad \lnot (p \land q) \equiv \lnot p \lor \lnot q.$$

The principle of inclusion and exclusion counts the size of a union in terms of intersections:

$$\left| \bigcup_{i=1}^{n} A_i \right| = \sum_{\emptyset \neq S \subseteq \{1,\dots,n\}} (-1)^{|S|+1} \left| \bigcap_{i \in S} A_i \right|.$$

In number theory the library implements the fundamental theorem of arithmetic, which states that every integer greater than one has a unique factorization into primes up to order:

$$n = \prod_{i=1}^{k} p_i^{\,e_i}, \qquad p_1 < p_2 < \dots < p_k.$$

In graph theory the library relies on and exposes the handshake lemma and the properties of trees, and in abstract algebra it exposes Lagrange theorem and the orbit stabilizer theorem. These results anchor the corresponding modules and appear again with code below.

## Design Philosophy

discretus is built on a small number of principles that are applied consistently across every module.

**Correctness first.** Every public routine is covered by unit tests, property based tests where applicable, and cross validation against independent references. Where a naive method and an advanced method both exist, the advanced method is validated against the naive method on randomized inputs so that optimizations never silently change results. Correctness is treated as a non negotiable invariant rather than a feature, and the continuous integration pipeline refuses to merge a change that reduces coverage or breaks a property test.

**One obvious way.** The public interface favors a single clear entry point per concept. Function names read like the mathematics they encode, argument orders are consistent across modules, and return types are stable and documented. A user who knows the name of a mathematical operation can usually guess the name of the corresponding routine and be correct, which reduces the cognitive load of moving between domains.

**Explicit over implicit.** Objects do not mutate silently, randomized routines require an explicit seed to be reproducible, and conversions between representations are named operations rather than hidden coercions. This makes programs written with discretus easy to reason about, easy to test, and easy to review, because every meaningful transformation appears in the source as a deliberate call.

**Composability.** Data structures are designed to flow between modules. A relation can become a directed graph, a graph can become an adjacency matrix, a matrix can be interpreted over a finite field, and a finite group can generate its Cayley graph. The seven domains are not isolated silos, they are interoperable views of the same underlying discrete objects, which is what makes cross domain workflows natural.

**Transparency.** Selected routines support a step recording mode that captures the intermediate reasoning of an algorithm, which is invaluable for teaching and debugging. Many objects can render themselves to LaTeX, so a computation can be displayed exactly as it would appear on a page. This principle turns the library into a communication tool and not merely a calculator.

## Architecture

discretus is organized as a layered architecture. At the base sits a core layer that defines the shared abstractions used by every domain. These include the element protocol that describes what it means to be a member of a discrete structure, the relation and function bases that unify binary relations and mappings, the algebraic structure interfaces that describe closure, identity, and inverse, numeric helpers for arbitrary precision integers and exact rationals, a step recorder for transparent execution, and a LaTeX rendering mixin. Because these abstractions are centralized, the domain modules remain small, focused, and mutually consistent.

Above the core layer sit the seven domain packages. Each domain package is subdivided into cohesive subpackages that mirror how the subject is taught, so that a user familiar with the mathematics can navigate the source tree by intuition. Above the domains sit three cross cutting service packages. The visualization package renders graphs, Hasse diagrams, lattices, truth tables, and Karnaugh maps through pluggable backends. The input and output package reads and writes standard interchange formats. The utilities package provides timing, memoization, bit manipulation, and validation helpers used throughout the library.

The dependency direction is strict and acyclic. Domain packages depend only on the core layer and never on one another through hidden channels, while interoperability between domains is provided through explicit, documented conversion functions. This discipline keeps the import graph clean, keeps startup fast, and makes it straightforward to reason about which parts of the library are exercised by any given program.

| Package | Responsibility | Representative contents |
| --- | --- | --- |
| `discretus.core` | Shared abstractions and numeric helpers | element, relation base, structure, step recorder, LaTeX mixin |
| `discretus.sets` | Sets, relations, orders, functions | finite set, operations, relations, equivalence, orders |
| `discretus.logic` | Propositional and predicate logic, SAT | parser, truth table, normal forms, DPLL, CDCL, predicate |
| `discretus.combinatorics` | Counting, sequences, generation | permutations, binomial, Stirling, Catalan, generating functions |
| `discretus.graphs` | Graph structures and algorithms | traversal, shortest path, spanning, flow, coloring, paths |
| `discretus.number_theory` | Integers, primes, modular arithmetic | gcd, modular, primes, factorization, functions, crypto |
| `discretus.recurrences` | Recurrences and asymptotics | linear solver, sequences, master theorem |
| `discretus.algebra` | Groups, rings, fields, polynomials | groups, rings, fields, polynomials, linear, lattice |
| `discretus.viz` | Visualization backends | graph draw, Hasse draw, truth table draw, Karnaugh draw |
| `discretus.io` | Serialization and interchange | GraphML, GML, DIMACS, JSON, LaTeX export |
| `discretus.utils` | Cross cutting helpers | timing, memoize, bit tricks, validation |

## Installation

discretus targets modern, supported versions of the interpreter and is distributed as a universal wheel. The simplest installation uses pip.

```bash
pip install discretus
```

The core library has no mandatory third party dependencies. Optional features are grouped into extras so that you install only what you need. The visualization extra pulls in plotting and graph drawing backends, the docs extra pulls in the documentation toolchain, and the dev extra pulls in the full development and testing stack.

```bash
pip install "discretus[viz]"
pip install "discretus[docs]"
pip install "discretus[dev]"
```

A conda package is available on conda-forge for users who prefer that ecosystem.

```bash
conda install -c conda-forge discretus
```

To work from source, clone the repository and install in editable mode with the development extra so that tests, linters, and documentation tooling are available.

```bash
git clone https://github.com/olaflaitinen/discretus.git
cd discretus
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

After installation you can verify the environment with a quick smoke test that imports the package and prints the version.

```bash
python -c "import discretus; print(discretus.__version__)"
```

Requirements: discretus supports Python 3.9 and later. The visualization extra additionally requires a plotting backend, and the Graphviz renderer requires the system Graphviz binaries to be installed and available on the path.

## Quick Start

The following short program touches several domains at once to convey the overall feel of the library. It builds two sets, checks a logical implication, computes a shortest path, and tests a primality claim.

```python
from discretus.sets import FiniteSet
from discretus.sets.operations import union, intersection
from discretus.logic.propositional import parse, is_tautology
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

## Set Theory

A set is an unordered collection of distinct elements. discretus provides finite sets, multisets, ordered sets, and bit sets under a shared operation vocabulary, so that an algorithm written against the abstract interface works with any representation. The finite set is a hashable, immutable value type suitable for exact reasoning, the bit set offers a compact representation for dense universes where membership can be encoded in machine words, and the multiset supports counting semantics where elements may appear with multiplicity.

The fundamental operations are union, intersection, difference, and symmetric difference, defined by

$$A \cup B = \{ x : x \in A \lor x \in B \}, \qquad A \cap B = \{ x : x \in A \land x \in B \},$$

$$A \setminus B = \{ x : x \in A \land x \notin B \}, \qquad A \triangle B = (A \setminus B) \cup (B \setminus A).$$

The cardinality of the power set of a finite set is $|\mathcal{P}(A)| = 2^{|A|}$, and the cardinality of a Cartesian product is $|A \times B| = |A|\,|B|$. discretus computes both exactly and can enumerate the underlying elements lazily so that large power sets and products do not need to be materialized all at once.

A binary relation $R \subseteq A \times A$ is reflexive when $\forall a\,(a\,R\,a)$, symmetric when $\forall a,b\,(a\,R\,b \Rightarrow b\,R\,a)$, antisymmetric when $\forall a,b\,(a\,R\,b \land b\,R\,a \Rightarrow a=b)$, and transitive when $\forall a,b,c\,(a\,R\,b \land b\,R\,c \Rightarrow a\,R\,c)$. A relation that is reflexive, symmetric, and transitive is an equivalence relation and induces a partition of $A$ into equivalence classes. A relation that is reflexive, antisymmetric, and transitive is a partial order. The transitive closure is computed with the Warshall algorithm in time $O(n^3)$ where $n = |A|$.

```python
from discretus.sets import FiniteSet
from discretus.sets.operations import union, intersection, symmetric_difference, power_set
from discretus.sets.relations import Relation
from discretus.sets.orders import PartialOrder

a = FiniteSet({1, 2, 3})
b = FiniteSet({2, 3, 4})
print(union(a, b))
print(intersection(a, b))
print(symmetric_difference(a, b))
print(len(list(power_set(a))))

r = Relation(domain={1, 2, 3}, pairs={(1, 2), (2, 3)})
print(r.is_transitive())
print(r.transitive_closure().pairs)

divides = PartialOrder.from_relation(
    ground={1, 2, 3, 4, 6, 12},
    leq=lambda x, y: y % x == 0,
)
print(divides.maximal_elements())
print(divides.is_lattice())
```

Partial orders can be inspected for least and greatest elements, minimal and maximal elements, upper and lower bounds, and lattice structure. When the order is a lattice, meet and join are available, and the order can be rendered as a Hasse diagram for visual study. Functions between sets are also first class, with predicates for injectivity, surjectivity, and bijectivity, and with composition and inverse construction where they are defined.

## Mathematical Logic

A propositional formula is built from atoms and the connectives negation, conjunction, disjunction, implication, and biconditional. discretus models formulas as expression trees, which can be constructed programmatically or parsed from a human friendly syntax. A formula is a tautology when it evaluates to true under every assignment, a contradiction when it evaluates to false under every assignment, and satisfiable when at least one assignment makes it true. Two formulas are logically equivalent when they agree on every assignment. The implication and biconditional satisfy the identities

$$p \rightarrow q \equiv \lnot p \lor q, \qquad p \leftrightarrow q \equiv (p \rightarrow q) \land (q \rightarrow p).$$

Every formula admits a conjunctive normal form, a conjunction of disjunctions of literals, and a disjunctive normal form, a disjunction of conjunctions of literals:

$$\varphi \equiv \bigwedge_{i=1}^{m} \left( \bigvee_{j=1}^{k_i} \ell_{ij} \right).$$

Naive conversion to conjunctive normal form can cause exponential blowup, so discretus also provides the Tseitin transformation, which introduces auxiliary variables to produce an equisatisfiable formula whose size grows linearly in the size of the input. For two level minimization the Quine McCluskey procedure is available, and it reports prime implicants and a minimal cover.

The satisfiability problem asks whether an assignment exists that makes $\varphi$ true. discretus provides a classic DPLL solver and a conflict driven clause learning solver with watched literals and an activity based decision heuristic, which together handle both instructional instances and moderately large industrial style instances. The solver reads and writes the DIMACS format so that instances can be exchanged with external tools.

```python
from discretus.logic.propositional import parse, truth_table, is_tautology, are_equivalent
from discretus.logic.normal_forms import to_cnf, to_dnf
from discretus.logic.sat import solve

print(is_tautology(parse("p | ~p")))
print(are_equivalent(parse("~(p & q)"), parse("~p | ~q")))
print(truth_table(parse("p & (q | r)")))
print(to_cnf(parse("p -> (q -> r)")))
print(to_dnf(parse("(p | q) & r")))
print(solve(parse("(p | q) & (~p | r) & (~q | ~r)")))
```

Predicate logic extends the propositional core with terms, predicates, and quantifiers. Over a finite domain you can evaluate universally quantified statements $\forall x\,\phi(x)$ and existentially quantified statements $\exists x\,\phi(x)$ against an explicit interpretation. This makes the package suitable for teaching model theory, for checking small specifications, and for exploring the semantics of first order sentences by direct evaluation.

## Combinatorics

Combinatorics studies counting, arrangement, and structure. The number of ordered arrangements and unordered selections of $k$ objects from $n$ are

$$P(n, k) = \frac{n!}{(n-k)!}, \qquad \binom{n}{k} = \frac{n!}{k!\,(n-k)!}.$$

The binomial theorem, the Pascal identity, and the Vandermonde identity are all supported:

$$(x + y)^{n} = \sum_{k=0}^{n} \binom{n}{k} x^{k} y^{n-k}, \qquad \binom{n}{k} = \binom{n-1}{k-1} + \binom{n-1}{k}, \qquad \binom{m+n}{r} = \sum_{k=0}^{r} \binom{m}{k}\binom{n}{r-k}.$$

The library computes classical integer sequences with exact arbitrary precision arithmetic. The Catalan numbers, the Bell numbers, and the Stirling numbers of the second kind are

$$C_n = \frac{1}{n+1}\binom{2n}{n}, \qquad B_n = \sum_{k=0}^{n} S(n, k), \qquad S(n, k) = \frac{1}{k!}\sum_{j=0}^{k} (-1)^{j}\binom{k}{j}(k-j)^{n}.$$

Beyond counting, discretus provides constructive generators that yield combinatorial objects lazily, which lets you iterate over very large spaces without materializing them. Generators exist for permutations, combinations, subsets in Gray code order, integer partitions, and set partitions, together with ranking and unranking utilities that map objects bijectively to and from indices in a fixed order.

```python
from discretus.combinatorics.counting import permutations_count, combinations_count, binomial
from discretus.combinatorics.sequences import catalan, bell, stirling_second
from discretus.combinatorics.generation import subsets_gray_code, integer_partitions

print(permutations_count(10, 3))
print(combinations_count(10, 3))
print(binomial(20, 10))
print(catalan(10))
print(bell(6))
print(stirling_second(5, 2))
print(list(subsets_gray_code([1, 2, 3])))
print(list(integer_partitions(5)))
```

Generating function utilities treat formal power series as first class objects, supporting addition, multiplication, composition, and coefficient extraction for both ordinary and exponential generating functions. This provides a computational bridge from analytic combinatorics to concrete numbers, so that a recurrence expressed through a generating function can be evaluated term by term.

## Graph Theory

A graph is a pair $G = (V, E)$ where $V$ is a set of vertices and $E$ is a set of edges. discretus supports directed and undirected graphs, weighted and unweighted graphs, and simple graphs and multigraphs, and it exposes adjacency list, adjacency matrix, and incidence matrix views so that you can select the representation that best fits an algorithm. The handshake lemma relates degrees to the number of edges:

$$\sum_{v \in V} \deg(v) = 2\,|E|.$$

Traversal routines cover breadth first search and depth first search, connected components, strongly connected components via the Tarjan and Kosaraju algorithms, articulation points, bridges, and cycle detection. Shortest path routines cover Dijkstra for non negative weights, Bellman Ford for graphs with negative edges, Floyd Warshall for all pairs, and Johnson for sparse all pairs. With a binary heap, Dijkstra runs in

$$O\big((|V| + |E|) \log |V|\big),$$

while Bellman Ford runs in $O(|V|\,|E|)$ and Floyd Warshall runs in $O(|V|^3)$. Minimum spanning tree routines cover Kruskal, Prim, and Boruvka, and a spanning tree of a connected graph on $n$ vertices always has exactly $n-1$ edges.

```python
from discretus.graphs import Graph
from discretus.graphs.traversal import bfs, connected_components, topological_sort
from discretus.graphs.shortest_path import dijkstra, bellman_ford
from discretus.graphs.spanning import kruskal, prim
from discretus.graphs.coloring import chromatic_number, is_bipartite
from discretus.graphs.paths import has_eulerian_circuit, has_hamiltonian_path

g = Graph()
g.add_edges_from([("A", "B", 4), ("A", "C", 1), ("C", "B", 2), ("B", "D", 5)])
print(list(bfs(g, "A")))
print(connected_components(g))
print(dijkstra(g, "A")[0])
print(sum(w for _, _, w in kruskal(g)))
print(chromatic_number(g), is_bipartite(g))
print(has_eulerian_circuit(g), has_hamiltonian_path(g))
```

Coloring routines include greedy strategies, the DSATUR heuristic, an exact backtracking solver, and computation of the chromatic number $\chi(G)$ and the chromatic polynomial. Path routines detect Eulerian circuits and trails through the Hierholzer algorithm and detect Hamiltonian paths and cycles. Flow routines provide Ford Fulkerson, Edmonds Karp, Dinic, and push relabel, and by the max flow min cut theorem the value of a maximum flow equals the capacity of a minimum cut. Bipartite matching is available through Hopcroft Karp and optimal assignment through the Hungarian method.

## Number Theory

The number theory package computes over arbitrary precision integers and covers the classical toolkit. The Euclidean algorithm computes the greatest common divisor, and the extended Euclidean algorithm additionally returns Bezout coefficients $x, y$ such that

$$a x + b y = \gcd(a, b).$$

Modular arithmetic includes modular inverses, fast modular exponentiation, and the discrete logarithm. Euler theorem states that if $\gcd(a, n) = 1$ then

$$a^{\varphi(n)} \equiv 1 \pmod{n},$$

where $\varphi$ is the Euler totient, and Fermat little theorem is the special case in which $n$ is prime. The Chinese remainder theorem guarantees a unique solution modulo $\prod_i n_i$ to a system of congruences with pairwise coprime moduli:

$$x \equiv a_i \pmod{n_i}, \quad i = 1, \dots, k.$$

Primality testing offers trial division for small inputs, the probabilistic Miller Rabin test with a configurable number of witnesses for large inputs, and a deterministic variant for inputs below documented bounds. Factorization offers trial division, Pollard rho, and Pollard p minus one, and arithmetic functions include the Euler totient, the Mobius function, divisor counting and summation, and Dirichlet convolution. The prime counting behavior is consistent with the asymptotic density described by the prime number theorem, $\pi(x) \sim x / \ln x$.

```python
from discretus.number_theory.gcd import gcd, extended_gcd, lcm
from discretus.number_theory.modular import mod_inverse, mod_exp, crt
from discretus.number_theory.primes import is_prime, primes_up_to
from discretus.number_theory.functions import euler_totient
from discretus.number_theory.factorization import factorize

print(extended_gcd(462, 1071))
print(lcm(4, 6))
print(mod_inverse(3, 11))
print(mod_exp(7, 128, 13))
print(crt([2, 3, 2], [3, 5, 7]))
print(euler_totient(36))
print(primes_up_to(30))
print(is_prime(2_147_483_647))
print(factorize(600851475143))
```

## Recurrence Relations

A linear homogeneous recurrence with constant coefficients has the form

$$a_n = c_1 a_{n-1} + c_2 a_{n-2} + \dots + c_k a_{n-k},$$

and its behavior is governed by the roots of the characteristic equation

$$x^{k} = c_1 x^{k-1} + c_2 x^{k-2} + \dots + c_k.$$

When the roots are distinct, the closed form is a linear combination of powers of the roots, and repeated roots contribute polynomial factors. discretus solves such recurrences symbolically where a closed form exists and evaluates individual terms quickly using matrix exponentiation, which computes $a_n$ in $O(k^3 \log n)$ time. For the Fibonacci sequence the closed form is given by the golden ratio $\varphi = (1 + \sqrt{5}) / 2$ through the Binet formula

$$F_n = \frac{\varphi^{n} - (1-\varphi)^{n}}{\sqrt{5}}.$$

The Master Theorem classifies divide and conquer recurrences of the form $T(n) = a\,T(n/b) + f(n)$ by comparing $f(n)$ with $n^{\log_b a}$, and discretus reports which of the three cases applies together with the resulting asymptotic growth class.

```python
from discretus.recurrences.sequences import fibonacci
from discretus.recurrences.linear import solve_linear_recurrence
from discretus.recurrences.master_theorem import master_theorem

print(fibonacci(50))
print(solve_linear_recurrence(coefficients=[1, 1], initial=[0, 1], n=10))
print(master_theorem(a=2, b=2, f_exponent=1))
```

## Abstract Algebra

A group is a set $G$ with an associative binary operation, an identity element, and inverses for every element. discretus models cyclic, symmetric, dihedral, and permutation groups, and it verifies the group axioms on construction. Lagrange theorem states that for a finite group $G$ and a subgroup $H \leq G$ the order of the subgroup divides the order of the group, and the index counts the cosets:

$$|H| \text{ divides } |G|, \qquad [G : H] = \frac{|G|}{|H|}.$$

Group actions are supported with orbit and stabilizer computation, and the orbit stabilizer theorem states that for any element $x$ of the acted upon set,

$$|G| = |\mathrm{Orb}(x)| \cdot |\mathrm{Stab}(x)|.$$

Rings and fields extend the group machinery with a second operation. discretus provides modular integer rings, polynomial rings, and finite fields, together with routines for units, zero divisors, ideals, and characteristic. A finite field of order $q$ exists precisely when $q = p^n$ for a prime $p$, and the library constructs such fields and performs exact arithmetic within them. Polynomial support includes exact arithmetic, division with remainder, greatest common divisor, factorization, and evaluation, which connects naturally to the finite field machinery used in coding theory and cryptography.

```python
from discretus.algebra.groups import CyclicGroup, SymmetricGroup, DihedralGroup

z6 = CyclicGroup(6)
print(z6.order(), z6.is_abelian())
print(z6.cayley_table())
print([len(h) for h in z6.subgroups()])

s3 = SymmetricGroup(3)
print(s3.order())
print([len(o) for o in s3.conjugacy_classes()])

d4 = DihedralGroup(4)
print(d4.order(), d4.is_abelian())
```

## Visualization

The visualization package renders discrete objects to images through pluggable backends. It can draw graphs with several layout strategies, Hasse diagrams for partial orders, lattice diagrams, truth tables, and Karnaugh maps. Rendering is strictly optional and lives behind the visualization extra, so the core library never requires a plotting stack. When a backend is present, a single call turns a computed object into a figure suitable for a slide or a paper, and the same objects can also emit LaTeX for direct inclusion in a document.

## Serialization and Interchange

The input and output package reads and writes standard interchange formats so that discretus objects can move between tools. Graphs can be exchanged through GraphML and GML, satisfiability instances through DIMACS, and general objects through JSON. In addition, many objects can render themselves to LaTeX, which makes it easy to move a computed structure from code into a manuscript. All serialization is deterministic, so the same object always produces the same output, which is important for version control and reproducible builds.

## Complexity Reference

| Routine | Complexity |
| --- | --- |
| Set membership (hashed) | $O(1)$ average |
| Transitive closure (Warshall) | $O(n^{3})$ |
| Truth table evaluation | $O(2^{v})$ for $v$ variables |
| Dijkstra (binary heap) | $O((|V|+|E|)\log |V|)$ |
| Bellman Ford | $O(|V|\,|E|)$ |
| Floyd Warshall | $O(|V|^{3})$ |
| Kruskal | $O(|E| \log |E|)$ |
| Sieve of Eratosthenes | $O(n \log \log n)$ |
| Modular exponentiation | $O(\log e)$ |
| Miller Rabin (per witness) | $O(\log^{3} n)$ |
| Linear recurrence (matrix power) | $O(k^{3} \log n)$ |

## Performance Notes

discretus documents the asymptotic complexity of every nontrivial routine in its docstring and in the API reference, so that users can make informed choices. Graph algorithms are implemented with attention to the underlying representation, and dense versus sparse variants are provided where the distinction matters. Number theoretic routines operate on arbitrary precision integers and select algorithms based on input size, so that small inputs are handled by simple fast methods while large inputs are handled by asymptotically superior methods. Where an algorithm has both a transparent reference implementation and a tuned implementation, both are shipped and the tuned version is validated against the reference on randomized inputs. Hot paths use memoization and precomputation where it is safe to do so, and randomized routines accept an explicit seed so that performance experiments remain reproducible. A benchmark suite tracks performance across releases and guards against regressions.

## Testing and Quality

Quality is enforced continuously. The test suite combines example based unit tests, property based tests that assert algebraic laws such as commutativity and associativity of set operations, and cross validation tests that compare independent implementations of the same result. Continuous integration runs the suite across every supported interpreter version and across the major operating systems, and coverage is reported on every change. The project maintains strict static typing checked by mypy, a consistent code style enforced by black and isort, and static analysis performed by ruff and pylint. Security oriented static analysis is performed by bandit, and a scheduled dependency audit watches for known vulnerabilities. All of these checks run locally through pre-commit hooks and again in continuous integration, so that a change cannot merge unless it satisfies the full quality gate.

## Interoperability

discretus is designed to coexist with the wider scientific Python ecosystem. Graphs can be exported to and imported from common interchange formats so that they can be consumed by external tools, matrices can be exchanged with array libraries, and results can be rendered to LaTeX for inclusion in documents. The library never imposes these integrations as hard dependencies, which keeps the core installation minimal while still enabling rich workflows when the optional packages are present. This philosophy lets discretus act as a well behaved component in a larger pipeline rather than demanding that a project adopt it wholesale.

## Command Line Interface

discretus ships a small command line interface for common one shot tasks, such as testing primality, factoring an integer, converting a formula to conjunctive normal form, and rendering a graph from a file. The interface is intended for quick experiments and for use inside shell pipelines and grading scripts, where invoking a full Python session would be unnecessarily heavy.

```bash
python -m discretus prime 2147483647
python -m discretus factor 600851475143
python -m discretus cnf "p -> (q -> r)"
```

## Project Structure

The repository follows a conventional and predictable layout. The importable package lives under the top level package directory, tests mirror the package layout so that every module has a corresponding test module, documentation lives in its own directory, and runnable demonstrations live in the examples directory. Continuous integration configuration, contribution guidelines, and community health files live at the repository root.

```text
discretus/
  discretus/        the importable library
  tests/            test suite mirroring the package
  docs/             documentation sources
  examples/         runnable demonstrations
  benchmarks/       performance measurements
  scripts/          maintenance and release helpers
```

## Versioning and Stability

discretus follows semantic versioning. Within a major version the public API is backward compatible, deprecations are announced at least one minor release before removal, and every breaking change is documented in the changelog with a migration note. Anything not documented as public should be treated as internal and subject to change without notice. This policy lets downstream projects depend on discretus with confidence and plan upgrades deliberately.

## Roadmap

| Milestone | Focus |
| --- | --- |
| Near term | Expanded predicate logic tooling and additional SAT heuristics |
| Mid term | Planarity testing, graph isomorphism refinement, richer visualization |
| Long term | Optional native acceleration and a symbolic interoperability bridge |

## Contributing

Contributions are welcome and appreciated. Please read `CONTRIBUTING.md` and `CODE_OF_CONDUCT.md` before opening a pull request, and open an issue first for substantial changes so that the design can be discussed. Small, focused pull requests with clear descriptions and accompanying tests are the easiest to review and the fastest to merge. The project adopts the Contributor Covenant, and all participants are expected to uphold a respectful, inclusive, and harassment free environment in every project space.

## Security Policy

If you discover a security issue, please do not open a public issue. Instead, contact the maintainers privately at the corresponding author address so that the problem can be assessed and addressed responsibly before any public disclosure. The security policy describes the supported versions and the coordinated disclosure timeline, and reports are acknowledged promptly.

## Frequently Asked Questions

**Does discretus require any native libraries.** No. The core is pure Python and installs without a compiler. Only the optional Graphviz renderer requires an external binary, and it is never needed unless you request it.

**Is discretus suitable for teaching.** Yes. The reference implementations are written to be read, the step recording mode exposes intermediate reasoning, and the LaTeX export produces publication ready output for slides and handouts.

**Can I use discretus in commercial software.** Yes. The library is released under the permissive MIT License, which places minimal conditions on use, modification, and redistribution.

**How does discretus handle very large integers.** All number theoretic routines operate over arbitrary precision integers, so results are exact regardless of size, limited only by available memory and time.

**How can I make randomized routines reproducible.** Pass an explicit seed. Every randomized routine accepts a seed argument and is deterministic once it is supplied.

## Glossary

**Tautology.** A propositional formula that is true under every assignment of truth values to its variables.

**Chromatic number.** The smallest number of colors needed to color the vertices of a graph so that no edge joins two vertices of the same color.

**Totient.** The count of integers up to a given integer that are coprime to it.

**Coset.** A translate of a subgroup by a fixed group element, used to partition a group.

**Lattice.** A partially ordered set in which every pair of elements has a least upper bound and a greatest lower bound.

## Citation

If you use discretus in academic work, please cite it using the metadata in the citation file included with the repository.

```bibtex
@software{discretus,
  title   = {discretus: A Discrete Mathematics library for Python},
  author  = {Laitinen-Fredriksson Lundstrom-Imanov, Gustav Olaf Yunus},
  year    = {2026},
  version = {1.0.0},
  url     = {https://github.com/olaflaitinen/discretus}
}
```

## Acknowledgments

discretus is developed and maintained at the School of ICT, Metropolia University of Applied Sciences. The design draws on decades of classical results in discrete mathematics and on the collective experience of the open source scientific Python community, whose conventions and tooling made this library possible.

## License

discretus is released under the MIT License. This permissive license allows use, copying, modification, merging, publication, distribution, sublicensing, and sale, subject only to the inclusion of the copyright notice and the permission notice, and it disclaims warranty and liability. The full text is provided in the `LICENSE` file at the repository root.

## Author and Contact

**Author:** Gustav Olaf Yunus Laitinen-Fredriksson Lundström-Imanov $^{\mathrm{a},*}$

$^{\mathrm{a}}$ School of ICT, Metropolia University of Applied Sciences, Myllypurontie 1, 00920 Helsinki, Finland

$^{*}$ Corresponding author. Email: yunus.imanov@metropolia.fi. Phone: +46 76 236 80 88. ORCID: 0009-0006-5184-0810.
