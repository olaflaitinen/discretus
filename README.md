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
2. [Mathematical Scope](#mathematical-scope)
3. [Design Philosophy](#design-philosophy)
4. [Architecture](#architecture)
5. [Installation](#installation)
6. [Quick Start](#quick-start)
7. [Set Theory](#set-theory)
8. [Mathematical Logic](#mathematical-logic)
9. [Combinatorics](#combinatorics)
10. [Graph Theory](#graph-theory)
11. [Number Theory](#number-theory)
12. [Recurrence Relations](#recurrence-relations)
13. [Abstract Algebra](#abstract-algebra)
14. [Complexity Reference](#complexity-reference)
15. [Testing and Quality](#testing-and-quality)
16. [Contributing](#contributing)
17. [Citation](#citation)
18. [License](#license)

---

## Introduction

discretus is a comprehensive software library that implements the core theory and algorithms of discrete mathematics for the Python programming language. It serves learners who need transparent building blocks, educators who need dependable primitives for coursework and automated assessment, and practitioners who need fast, correct, and composable routines inside real systems. The library spans seven foundational domains, namely set theory, mathematical logic, combinatorics, graph theory, number theory, recurrence relations, and abstract algebra, and exposes all of them through a single coherent application programming interface.

This document uses full LaTeX notation. On GitHub the equations below render through the built in math support, and in any LaTeX aware Markdown viewer they render as typeset mathematics. Inline mathematics is written between single dollar signs, for example $a \in A$, and display mathematics is written between double dollar signs.

## Mathematical Scope

discretus formalizes and computes the following representative results. Each domain section later in this document restates these with runnable code.

The distributive law of set algebra:

$$A \cap (B \cup C) = (A \cap B) \cup (A \cap C).$$

De Morgan laws for sets and for logic:

$$\overline{A \cup B} = \overline{A} \cap \overline{B}, \qquad \overline{A \cap B} = \overline{A} \cup \overline{B},$$

$$\lnot (p \lor q) \equiv \lnot p \land \lnot q, \qquad \lnot (p \land q) \equiv \lnot p \lor \lnot q.$$

The principle of inclusion and exclusion:

$$\left| \bigcup_{i=1}^{n} A_i \right| = \sum_{\emptyset \neq S \subseteq \{1,\dots,n\}} (-1)^{|S|+1} \left| \bigcap_{i \in S} A_i \right|.$$

## Design Philosophy

discretus is built on a small number of principles applied consistently across every module: correctness first, one obvious way to express each concept, explicit rather than implicit behavior, composability across domains, and transparency of intermediate reasoning. Where a naive method and an advanced method both exist, the advanced method is validated against the naive method on randomized inputs so that optimizations never silently change results.

## Architecture

discretus is organized as a layered architecture. A core layer defines shared abstractions such as the element protocol, relation and function bases, algebraic structure interfaces, arbitrary precision numeric helpers, a step recorder, and a LaTeX rendering mixin. Seven domain packages sit above the core, and three cross cutting service packages provide visualization, serialization, and utilities. The dependency direction is strict and acyclic, and interoperability between domains is provided through explicit conversion functions.

| Package | Responsibility |
| --- | --- |
| `discretus.core` | Shared abstractions and numeric helpers |
| `discretus.sets` | Sets, relations, orders, functions |
| `discretus.logic` | Propositional and predicate logic, SAT |
| `discretus.combinatorics` | Counting, sequences, generation |
| `discretus.graphs` | Graph structures and algorithms |
| `discretus.number_theory` | Integers, primes, modular arithmetic |
| `discretus.recurrences` | Recurrences and asymptotics |
| `discretus.algebra` | Groups, rings, fields, polynomials |
| `discretus.viz` | Visualization backends |
| `discretus.io` | Serialization and interchange |
| `discretus.utils` | Cross cutting helpers |

## Installation

```bash
pip install discretus
```

Optional feature sets are grouped into extras:

```bash
pip install "discretus[viz]"
pip install "discretus[docs]"
pip install "discretus[dev]"
```

A conda package is available on conda-forge:

```bash
conda install -c conda-forge discretus
```

From source:

```bash
git clone https://github.com/olaflaitinen/discretus.git
cd discretus
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Requirements: Python 3.9 and later.

## Quick Start

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

A set is an unordered collection of distinct elements. discretus provides finite sets, multisets, ordered sets, and bit sets under a shared operation vocabulary. The fundamental operations are union, intersection, difference, and symmetric difference:

$$A \cup B = \{ x : x \in A \lor x \in B \}, \qquad A \cap B = \{ x : x \in A \land x \in B \},$$

$$A \setminus B = \{ x : x \in A \land x \notin B \}, \qquad A \triangle B = (A \setminus B) \cup (B \setminus A).$$

The power set of a set of cardinality $n$ has cardinality $2^{n}$:

$$|\mathcal{P}(A)| = 2^{|A|}.$$

A binary relation $R \subseteq A \times A$ is an equivalence relation when it is reflexive, symmetric, and transitive, that is when

$$\forall a\, (a\,R\,a), \qquad \forall a, b\, (a\,R\,b \Rightarrow b\,R\,a), \qquad \forall a, b, c\, (a\,R\,b \land b\,R\,c \Rightarrow a\,R\,c).$$

```python
from discretus.sets import FiniteSet
from discretus.sets.operations import union, intersection, symmetric_difference, power_set
from discretus.sets.relations import Relation

a = FiniteSet({1, 2, 3})
b = FiniteSet({2, 3, 4})
print(union(a, b))
print(intersection(a, b))
print(symmetric_difference(a, b))
print(len(list(power_set(a))))

r = Relation(domain={1, 2, 3}, pairs={(1, 2), (2, 3)})
print(r.is_transitive())
print(r.transitive_closure().pairs)
```

## Mathematical Logic

A propositional formula is built from atoms and the connectives negation, conjunction, disjunction, implication, and biconditional. A formula is a tautology when it evaluates to true under every assignment. The implication and biconditional satisfy

$$p \rightarrow q \equiv \lnot p \lor q, \qquad p \leftrightarrow q \equiv (p \rightarrow q) \land (q \rightarrow p).$$

Every formula admits a conjunctive normal form, a conjunction of disjunctions of literals:

$$\varphi \equiv \bigwedge_{i=1}^{m} \left( \bigvee_{j=1}^{k_i} \ell_{ij} \right).$$

The satisfiability problem asks whether an assignment exists that makes $\varphi$ true. discretus provides a DPLL solver and a conflict driven clause learning solver with watched literals.

```python
from discretus.logic.propositional import parse, is_tautology, are_equivalent
from discretus.logic.normal_forms import to_cnf
from discretus.logic.sat import solve

print(is_tautology(parse("p | ~p")))
print(are_equivalent(parse("~(p & q)"), parse("~p | ~q")))
print(to_cnf(parse("p -> (q -> r)")))
print(solve(parse("(p | q) & (~p | r) & (~q | ~r)")))
```

## Combinatorics

The number of $k$ permutations and $k$ combinations of $n$ objects are

$$P(n, k) = \frac{n!}{(n-k)!}, \qquad \binom{n}{k} = \frac{n!}{k!\,(n-k)!}.$$

The binomial theorem and Pascal identity are

$$(x + y)^{n} = \sum_{k=0}^{n} \binom{n}{k} x^{k} y^{n-k}, \qquad \binom{n}{k} = \binom{n-1}{k-1} + \binom{n-1}{k}.$$

The Catalan numbers and Stirling numbers of the second kind are

$$C_n = \frac{1}{n+1}\binom{2n}{n}, \qquad S(n, k) = \frac{1}{k!}\sum_{j=0}^{k} (-1)^{j}\binom{k}{j}(k-j)^{n}.$$

```python
from discretus.combinatorics.counting import permutations_count, combinations_count, binomial
from discretus.combinatorics.sequences import catalan, bell, stirling_second

print(permutations_count(10, 3))
print(binomial(20, 10))
print(catalan(10))
print(bell(6))
print(stirling_second(5, 2))
```

## Graph Theory

A graph is a pair $G = (V, E)$ where $V$ is a set of vertices and $E$ is a set of edges. The handshake lemma relates degrees to edges:

$$\sum_{v \in V} \deg(v) = 2\,|E|.$$

Dijkstra shortest paths on a graph with non negative weights run in

$$O\big((|V| + |E|) \log |V|\big)$$

with a binary heap. The chromatic number $\chi(G)$ is the least number of colors needed for a proper vertex coloring.

```python
from discretus.graphs import Graph
from discretus.graphs.traversal import bfs, connected_components
from discretus.graphs.shortest_path import dijkstra
from discretus.graphs.spanning import kruskal
from discretus.graphs.coloring import chromatic_number, is_bipartite

g = Graph()
g.add_edges_from([("A", "B", 4), ("A", "C", 1), ("C", "B", 2), ("B", "D", 5)])
print(list(bfs(g, "A")))
print(connected_components(g))
print(dijkstra(g, "A")[0])
print(sum(w for _, _, w in kruskal(g)))
print(chromatic_number(g), is_bipartite(g))
```

## Number Theory

The extended Euclidean algorithm computes integers $x, y$ such that

$$a x + b y = \gcd(a, b).$$

Euler theorem states that if $\gcd(a, n) = 1$ then

$$a^{\varphi(n)} \equiv 1 \pmod{n},$$

where $\varphi$ is the Euler totient. The Chinese remainder theorem guarantees a unique solution modulo $\prod_i n_i$ to a system of congruences with pairwise coprime moduli:

$$x \equiv a_i \pmod{n_i}, \quad i = 1, \dots, k.$$

```python
from discretus.number_theory.gcd import gcd, extended_gcd, lcm
from discretus.number_theory.modular import mod_inverse, mod_exp, crt
from discretus.number_theory.primes import is_prime, primes_up_to
from discretus.number_theory.functions import euler_totient

print(extended_gcd(462, 1071))
print(mod_inverse(3, 11))
print(mod_exp(7, 128, 13))
print(crt([2, 3, 2], [3, 5, 7]))
print(euler_totient(36))
print(is_prime(2_147_483_647))
```

## Recurrence Relations

A linear homogeneous recurrence with constant coefficients has the form

$$a_n = c_1 a_{n-1} + c_2 a_{n-2} + \dots + c_k a_{n-k},$$

with characteristic equation

$$x^{k} = c_1 x^{k-1} + c_2 x^{k-2} + \dots + c_k.$$

The Master Theorem classifies divide and conquer recurrences of the form $T(n) = a\,T(n/b) + f(n)$ by comparing $f(n)$ with $n^{\log_b a}$.

```python
from discretus.recurrences.sequences import fibonacci
from discretus.recurrences.linear import solve_linear_recurrence
from discretus.recurrences.master_theorem import master_theorem

print(fibonacci(50))
print(solve_linear_recurrence(coefficients=[1, 1], initial=[0, 1], n=10))
print(master_theorem(a=2, b=2, f_exponent=1))
```

## Abstract Algebra

A group is a set $G$ with an associative binary operation, an identity element, and inverses. Lagrange theorem states that for a finite group $G$ and a subgroup $H \leq G$,

$$|H| \text{ divides } |G|, \qquad [G : H] = \frac{|G|}{|H|}.$$

The orbit stabilizer theorem for a group action of $G$ on a set $X$ states that for any $x \in X$,

$$|G| = |\mathrm{Orb}(x)| \cdot |\mathrm{Stab}(x)|.$$

```python
from discretus.algebra.groups import CyclicGroup, SymmetricGroup

z6 = CyclicGroup(6)
print(z6.order(), z6.is_abelian())
print(z6.cayley_table())

s3 = SymmetricGroup(3)
print(s3.order())
print([len(o) for o in s3.conjugacy_classes()])
```

## Complexity Reference

| Routine | Complexity |
| --- | --- |
| Transitive closure (Warshall) | $O(n^{3})$ |
| Dijkstra (binary heap) | $O((|V|+|E|)\log |V|)$ |
| Bellman Ford | $O(|V|\,|E|)$ |
| Floyd Warshall | $O(|V|^{3})$ |
| Sieve of Eratosthenes | $O(n \log \log n)$ |
| Modular exponentiation | $O(\log e)$ |
| Miller Rabin (per witness) | $O(\log^{3} n)$ |

## Testing and Quality

The test suite combines example based unit tests, property based tests that assert algebraic laws, and cross validation tests that compare independent implementations. Continuous integration runs the suite across every supported interpreter and operating system. The project maintains strict typing with mypy, formatting with black and isort, linting with ruff and pylint, and security analysis with bandit, all enforced through pre-commit and continuous integration.

## Contributing

Contributions are welcome. Please read `CONTRIBUTING.md` and `CODE_OF_CONDUCT.md` before opening a pull request, and open an issue first for substantial changes. Small, focused pull requests with tests are the easiest to review.

## Citation

```bibtex
@software{discretus,
  title   = {discretus: A Discrete Mathematics library for Python},
  author  = {Laitinen-Fredriksson Lundstrom-Imanov, Gustav Olaf Yunus},
  year    = {2026},
  version = {1.0.0},
  url     = {https://github.com/olaflaitinen/discretus}
}
```

## License

discretus is released under the MIT License. See the `LICENSE` file for the full text.

## Author and Contact

**Author:** Gustav Olaf Yunus Laitinen-Fredriksson Lundström-Imanov $^{\mathrm{a},*}$

$^{\mathrm{a}}$ School of ICT, Metropolia University of Applied Sciences, Myllypurontie 1, 00920 Helsinki, Finland

$^{*}$ Corresponding author. Email: yunus.imanov@metropolia.fi. Phone: +46 76 236 80 88. ORCID: 0009-0006-5184-0810.
