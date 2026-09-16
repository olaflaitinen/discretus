# Changelog

All notable changes to this project are documented in this file. The format
follows the Keep a Changelog convention, and the project adheres to Semantic
Versioning 2.0.0.

## [Unreleased]

### Added

- Nothing yet.

## [1.0.0] - 2026-01-15

The first stable release. The public interface of every documented module is
covered by the backward compatibility guarantee described in the versioning
policy of `README.md`.

### Added

- Core layer with the element protocol, relation and function bases,
  algebraic structure interfaces, exact numeric helpers, a step recorder, and
  a LaTeX rendering mixin.
- Set theory package with finite sets, bit sets, multisets, ordered sets,
  interval sets, set algebra, binary and n-ary relations, closures,
  equivalence relations with union find, and order theory including posets,
  lattices, and Hasse diagrams.
- Logic package with a propositional expression tree, lexer and parser,
  evaluator, truth tables, tautology and equivalence checks, normal forms
  including negation, conjunctive, disjunctive, and algebraic normal form,
  the Tseitin transformation, Quine McCluskey minimization, Karnaugh maps, a
  DPLL solver, a conflict driven clause learning solver with watched literals
  and VSIDS, DIMACS interchange, predicate logic with quantifier evaluation
  and unification, and an inference layer with resolution, chaining, and
  natural deduction.
- Combinatorics package with counting utilities, classical integer
  sequences, lazy generators for permutations, combinations, subsets,
  compositions, partitions, necklaces, and Lyndon words, ranking and
  unranking, formal power series, Polya enumeration, combinatorial designs,
  and discrete probability.
- Graph package with graph, digraph, multigraph, weighted, bipartite, tree,
  forest, and hypergraph structures, adjacency and incidence views, traversal
  and connectivity algorithms, shortest path algorithms, minimum spanning
  trees, network flow and matching, coloring, Eulerian and Hamiltonian path
  analysis, structural properties, centrality measures, and generators.
- Number theory package with greatest common divisor routines, modular
  arithmetic, primality testing, factorization, arithmetic functions,
  diophantine equations, integer sequences, and cryptographic primitives.
- Recurrence package with linear recurrence solvers, matrix exponentiation,
  classical sequences, the Master Theorem, recursion trees, the Akra Bazzi
  method, nonlinear iteration, and asymptotic growth comparison.
- Algebra package with groups, group actions, rings, ideals, fields, finite
  fields, polynomials, exact linear algebra over rings and fields, and
  algebraic lattices.
- Visualization package with pluggable ASCII, SVG, Graphviz, and matplotlib
  backends for graphs, Hasse diagrams, lattices, trees, truth tables,
  Karnaugh maps, matrices, and Venn diagrams.
- Input and output package with GraphML, GML, DIMACS, JSON, CSV, edge list,
  adjacency, and LaTeX interchange.
- Utility package with timing, memoization, bit manipulation, formatting,
  validation, iteration helpers, and seeded randomness.
- Command line interface for primality testing, factorization, formula
  conversion, and graph inspection.
- Documentation, tutorials, runnable examples, and a benchmark suite.

[Unreleased]: https://github.com/olaflaitinen/discretus/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/olaflaitinen/discretus/releases/tag/v1.0.0
