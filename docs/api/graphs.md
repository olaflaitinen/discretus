# `discretus.graphs`

The graph package is the largest in the library. It provides the graph
structures, four representations of each, and the algorithm families that a
course and a production system both need: traversal and connectivity,
shortest paths, minimum spanning trees, network flow and matching,
colouring, Eulerian and Hamiltonian analysis, structural properties,
centrality and spectral analysis, and generators.

## Mathematical basis

A graph is a pair $G = (V, E)$ of a vertex set and an edge set. In an
undirected graph an edge is an unordered pair and the handshake lemma holds,

$$\sum_{v \in V} \deg(v) = 2\,|E|,$$

so the number of vertices of odd degree is even. In a directed graph an edge
is an ordered pair and the analogous identity relates the in degrees and the
out degrees to the edge count,

$$\sum_{v \in V} \deg^{-}(v) = \sum_{v \in V} \deg^{+}(v) = |E|.$$

A tree on $n$ vertices is connected and acyclic, has exactly $n - 1$ edges,
and is characterized by any two of those three properties. A spanning tree
of a connected graph therefore has $n - 1$ edges, which is the invariant the
spanning algorithms preserve.

The max flow min cut theorem states that the value of a maximum flow from a
source to a sink equals the capacity of a minimum cut separating them, which
is why the flow routines can answer a connectivity question and a capacity
question with the same computation.

## Module map

| Subpackage | Responsibility |
| --- | --- |
| `structures` | Graph types, vertices, edges, and the four representations |
| `traversal` | Search, components, strong connectivity, cycles, topological order |
| `shortest_path` | Single source, all pairs, and k shortest path algorithms |
| `spanning` | Minimum spanning trees, arborescences, Steiner trees |
| `flow` | Maximum flow, minimum cut, matching, assignment |
| `coloring` | Vertex and edge colouring, chromatic number and polynomial |
| `paths` | Eulerian and Hamiltonian analysis, postman and salesman routes |
| `properties` | Degrees, connectivity, distances, cliques, covers, planarity |
| `algorithms` | Centrality, ranking, random walks, spectra, communities |
| `generators` | Classical families and random models |

## Structures

### `Graph` and `DiGraph`

The two types most programs use. A graph is built by adding edges, and the
vertices appear as they are mentioned, which is what makes a graph literal
short.

```python
>>> from discretus.graphs import Graph
>>> g = Graph()
>>> g.add_edges_from([("A", "B", 4), ("A", "C", 1), ("C", "B", 2)])
>>> g.order(), g.size(), g.degree("A")
(3, 3, 2)
```

| Group | Members |
| --- | --- |
| Construction | `add_vertex`, `add_vertices_from`, `add_edge`, `add_edges_from`, `from_adjacency`, `from_edge_list`, `from_matrix` |
| Removal | `without_vertex`, `without_edge`, `subgraph`, `induced_subgraph` |
| Query | `vertices`, `edges`, `order`, `size`, `has_vertex`, `has_edge`, `neighbors`, `degree`, `weight` |
| Directed query | `predecessors`, `successors`, `in_degree`, `out_degree` |
| Views | `adjacency_list`, `adjacency_matrix`, `incidence_matrix`, `edge_list`, `laplacian_matrix` |
| Properties | `is_directed`, `is_weighted`, `is_simple`, `is_connected`, `is_acyclic`, `is_tree`, `is_regular`, `is_complete` |
| Conversion | `to_undirected`, `to_directed`, `reverse`, `to_relation`, `complement` |
| Interchange | `to_dict`, `to_graphml`, `to_dot`, `to_latex` |

Vertices may be any hashable value. Nothing assumes they are integers, and
nothing assumes they can be compared with one another, because the library
sorts them through the universal order in `discretus.core.comparators`.
Every method that returns a collection returns it in that order, so output
is identical between processes.

Graphs are immutable in the sense the library uses everywhere: `add_edge`
returns the graph for chaining and mutates the builder, while every derived
object, including a subgraph, a reversal, and a complement, is a new graph.
The distinction is documented per method, and the algorithms never mutate
their argument.

### The other structures

| Type | Purpose |
| --- | --- |
| `MultiGraph` | Parallel edges and self loops, each edge with an identity |
| `WeightedGraph` | Weights as a first class part of the type |
| `LabeledGraph` | Vertex and edge attributes |
| `BipartiteGraph` | Two parts, with the part of each vertex recorded |
| `Dag` | A directed acyclic graph, acyclicity verified on construction |
| `Tree` | A rooted tree, with parents, children, depth, and subtree size |
| `Forest` | A disjoint union of trees |
| `HyperGraph` | Edges that join any number of vertices |
| `DynamicGraph` | Incremental connectivity under edge insertion |

`Dag` verifying acyclicity on construction is the pattern the library uses
throughout: a type that promises a property checks it once, so that the
algorithms which depend on the property need not re check it and cannot be
given a graph that violates it.

### Representations

The same graph can be held four ways, and the choice is a performance
decision rather than a cosmetic one.

| Representation | Space | Good for |
| --- | --- | --- |
| Adjacency list | O(V + E) | Traversal, Dijkstra, anything sparse |
| Adjacency matrix | O(V squared) | Floyd Warshall, spectral work, dense graphs |
| Edge list | O(E) | Kruskal, which sorts the edges anyway |
| Incidence matrix | O(V times E) | Cycle and cut space computations |

Conversion is explicit and cheap relative to the algorithm that follows, and
the matrices are exact matrices from
[`discretus.core`](core.md), so a matrix power or a determinant computed
from a graph is exact.

## Traversal and connectivity

| Routine | Result | Complexity |
| --- | --- | --- |
| `bfs(graph, source)` | Vertices in breadth first order | O(V + E) |
| `dfs(graph, source)` | Vertices in depth first order | O(V + E) |
| `iterative_dfs(graph, source)` | The same, without recursion | O(V + E) |
| `best_first(graph, source, key)` | Vertices by a priority | O((V + E) log V) |
| `bidirectional(graph, source, target)` | A path from both ends | O(V + E) |
| `connected_components(graph)` | The components | O(V + E) |
| `strongly_connected_components(graph)` | The strong components | O(V + E) |
| `tarjan_scc(graph)` | Strong components by Tarjan | O(V + E) |
| `kosaraju(graph)` | Strong components by Kosaraju | O(V + E) |
| `biconnected_components(graph)` | The biconnected components | O(V + E) |
| `articulation_points(graph)` | Cut vertices | O(V + E) |
| `bridges(graph)` | Cut edges | O(V + E) |
| `detect_cycle(graph)` | A cycle, or `None` | O(V + E) |
| `topological_sort(graph)` | A linear order | O(V + E) |
| `kahn(graph)` | Topological order by Kahn | O(V + E) |

Two implementations of strong connectivity are provided because they teach
different things: Tarjan's algorithm does it in one pass with a stack of
low link values, and Kosaraju's does it in two passes over the graph and its
reverse. They are cross validated against one another on randomized
digraphs, which is how the library treats any pair of routines that must
agree.

`topological_sort` raises `InfeasibleError` naming a vertex on a cycle when
the graph is cyclic. That is the right behaviour rather than returning a
partial order, because a caller who asked for a topological order of a
cyclic graph has a bug and needs to know where.

```python
>>> from discretus.graphs import DiGraph
>>> from discretus.graphs.traversal import strongly_connected_components
>>> d = DiGraph()
>>> d.add_edges_from([("a", "b"), ("b", "c"), ("c", "a"), ("c", "d")])
>>> strongly_connected_components(d)
[['a', 'b', 'c'], ['d']]
```

## Shortest paths

| Routine | Handles | Complexity |
| --- | --- | --- |
| `dijkstra(graph, source, target=None)` | Non negative weights | O((V + E) log V) |
| `bellman_ford(graph, source)` | Negative weights, detects negative cycles | O(V E) |
| `spfa(graph, source)` | The queue based Bellman Ford variant | O(V E) worst case |
| `bfs_shortest(graph, source)` | Unweighted graphs | O(V + E) |
| `dag_shortest(graph, source)` | Directed acyclic graphs, any weights | O(V + E) |
| `floyd_warshall(graph)` | All pairs, negative weights allowed | O(V cubed) |
| `johnson(graph)` | All pairs, sparse, negative weights allowed | O(V E log V) |
| `a_star(graph, source, target, heuristic)` | Single target with a heuristic | O((V + E) log V) |
| `k_shortest(graph, source, target, k)` | The k shortest paths | O(k V (E + V log V)) |
| `yen(graph, source, target, k)` | The k shortest loopless paths | O(k V (E + V log V)) |
| `reconstruct_path(predecessors, target)` | A path from a predecessor map | O(length) |

Every single source routine returns a pair of a distance map and a
predecessor map, in that order, which is the convention throughout the
subpackage. The predecessor map is what `reconstruct_path` consumes, so
retrieving an actual path is always the same two calls regardless of which
algorithm produced the map.

```python
>>> from discretus.graphs import Graph
>>> from discretus.graphs.shortest_path import dijkstra, reconstruct_path
>>> g = Graph()
>>> g.add_edges_from([("A", "B", 4), ("A", "C", 1), ("C", "B", 2), ("B", "D", 5)])
>>> distances, predecessors = dijkstra(g, "A")
>>> distances["D"], reconstruct_path(predecessors, "D")
(8, ['A', 'C', 'B', 'D'])
```

Choosing between them: use `bfs_shortest` when the graph is unweighted,
because it is linear; use `dijkstra` for non negative weights; use
`bellman_ford` when a weight can be negative, and read its negative cycle
report rather than its distances when it finds one; use `dag_shortest` on a
directed acyclic graph even with negative weights, because the topological
order makes it linear; use `floyd_warshall` for all pairs on a dense graph
and `johnson` for all pairs on a sparse one.

Dijkstra and Bellman Ford must agree on a graph with non negative weights,
and the suite asserts exactly that on randomized graphs.

## Spanning trees

| Routine | Method | Complexity |
| --- | --- | --- |
| `kruskal(graph)` | Sort the edges, union find | O(E log E) |
| `prim(graph, start=None)` | Grow one tree with a heap | O((V + E) log V) |
| `boruvka(graph)` | Contract every component per round | O(E log V) |
| `reverse_delete(graph)` | Remove the heaviest non bridge repeatedly | O(E log E times connectivity) |
| `spanning_tree_count(graph)` | Kirchhoff's matrix tree theorem | O(V cubed) |
| `minimum_arborescence(graph, root)` | Directed, by Chu Liu and Edmonds | O(V E) |
| `steiner_tree(graph, terminals)` | Approximate Steiner tree | O(terminals times (V + E) log V) |

All four minimum spanning tree algorithms return an edge list, and the total
weight is what a caller almost always wants:

```python
>>> from discretus.graphs.spanning import kruskal, prim
>>> sum(w for _, _, w in kruskal(g)) == sum(w for _, _, w in prim(g))
True
```

The trees themselves can differ when weights are repeated, and the total
weight cannot. That distinction is exactly what the cross validation test
asserts, because asserting equality of the trees would fail for a correct
implementation.

`spanning_tree_count` uses the matrix tree theorem, which says that the
number of spanning trees equals any cofactor of the Laplacian matrix. The
computation is exact, so the count of spanning trees of a complete graph on
twelve vertices is the exact integer that Cayley's formula predicts, which
the suite asserts.

## Flow and matching

| Routine | Method | Complexity |
| --- | --- | --- |
| `ford_fulkerson(graph, source, sink)` | Augmenting paths | O(E times max flow) |
| `edmonds_karp(graph, source, sink)` | Shortest augmenting paths | O(V E squared) |
| `dinic(graph, source, sink)` | Blocking flows on level graphs | O(V squared E) |
| `push_relabel(graph, source, sink)` | Preflow push with relabelling | O(V cubed) |
| `min_cost_flow(graph, source, sink, flow)` | Successive shortest paths | O(flow times V E) |
| `max_flow_min_cut(graph, source, sink)` | The value and the cut | As the flow routine |
| `stoer_wagner(graph)` | Global minimum cut | O(V E + V squared log V) |
| `bipartite_matching(graph)` | Augmenting path matching | O(V E) |
| `hopcroft_karp(graph)` | Matching in phases | O(E times square root of V) |
| `hungarian(cost_matrix)` | Optimal assignment | O(n cubed) |

The flow value returned by every maximum flow routine is the same, and it
equals the capacity of the cut that `max_flow_min_cut` returns. That is the
theorem, and it is also the cross validation the suite performs across all
four implementations.

```python
>>> from discretus.graphs import DiGraph
>>> from discretus.graphs.flow import dinic, edmonds_karp, max_flow_min_cut
>>> net = DiGraph()
>>> net.add_edges_from([("s", "u", 10), ("s", "v", 5), ("u", "v", 15), ("u", "t", 5), ("v", "t", 10)])
>>> value, _ = edmonds_karp(net, "s", "t")
>>> cut_value, _ = max_flow_min_cut(net, "s", "t")
>>> value == cut_value == dinic(net, "s", "t")[0]
True
```

## Colouring

| Routine | Meaning | Complexity |
| --- | --- | --- |
| `greedy_coloring(graph, order=None)` | A colouring in the given vertex order | O(V + E) |
| `welsh_powell(graph)` | Greedy in decreasing degree order | O(V log V + E) |
| `dsatur(graph)` | Greedy by saturation degree | O((V + E) log V) |
| `backtracking_coloring(graph, colours)` | An exact k colouring, or `None` | Exponential |
| `chromatic_number(graph)` | The least number of colours | Exponential |
| `chromatic_polynomial(graph)` | The polynomial, by deletion and contraction | Exponential |
| `edge_coloring(graph)` | A proper edge colouring | O(V E) |
| `is_bipartite(graph)` | Two colourability, with the parts | O(V + E) |

The heuristics are polynomial and give an upper bound on the chromatic
number; the exact routines are exponential because the problem is NP hard.
Both are provided, the difference is documented, and `chromatic_number`
validates its answer against the heuristics on small graphs in the test
suite, since a heuristic that uses fewer colours than the claimed chromatic
number would be a contradiction.

The chromatic polynomial evaluated at an integer counts the proper
colourings with that many colours, which gives another cross check: its
value at the chromatic number must be positive and at one less must be zero.

## Paths and tours

| Routine | Meaning | Complexity |
| --- | --- | --- |
| `has_eulerian_circuit(graph)` | Connected with all degrees even | O(V + E) |
| `has_eulerian_path(graph)` | At most two odd degree vertices | O(V + E) |
| `hierholzer(graph)` | An Eulerian circuit or trail | O(E) |
| `fleury(graph)` | The same, by the bridge avoiding rule | O(E squared) |
| `has_hamiltonian_path(graph)` | Existence of a Hamiltonian path | Exponential |
| `hamiltonian_cycle(graph)` | A Hamiltonian cycle, or `None` | Exponential |
| `chinese_postman(graph)` | A shortest closed walk covering every edge | O(V cubed) |
| `tsp_exact(graph)` | An optimal tour, by Held and Karp | O(V squared 2 to the V) |
| `tsp_heuristic(graph, method)` | A tour by nearest neighbour or two opt | O(V squared) |

The Eulerian conditions are decidable in linear time and the Hamiltonian
ones are not, which is one of the most instructive contrasts in the subject.
The package makes it visible by putting the two next to each other with
their complexities stated.

## Structural properties

| Routine | Meaning |
| --- | --- |
| `degree_sequence(graph)` | Degrees in non increasing order |
| `is_graphical(sequence)` | Whether a sequence is realizable, by Erdos and Gallai |
| `connectivity(graph)`, `edge_connectivity(graph)` | Vertex and edge connectivity |
| `diameter(graph)`, `radius(graph)`, `eccentricity(graph, v)` | Distance measures |
| `center(graph)`, `periphery(graph)` | Extremal vertex sets |
| `girth(graph)` | The length of a shortest cycle |
| `max_clique(graph)`, `clique_number(graph)` | Largest complete subgraph |
| `max_independent_set(graph)` | Largest pairwise non adjacent set |
| `min_vertex_cover(graph)` | Smallest set meeting every edge |
| `min_dominating_set(graph)` | Smallest set dominating every vertex |
| `is_isomorphic(left, right)` | Isomorphism, by refinement and search |
| `automorphism_group(graph)` | The automorphisms, as permutations |
| `is_planar(graph)` | Planarity |
| `kuratowski_subgraph(graph)` | A forbidden subdivision when not planar |

The complement relations among clique, independent set, and vertex cover are
exposed rather than hidden: the independence number of a graph is the clique
number of its complement, and the vertex cover number is the vertex count
minus the independence number. Those identities are asserted in the suite,
which is a strong check because the three routines are implemented
separately.

## Analysis

| Routine | Meaning |
| --- | --- |
| `degree_centrality(graph)` | Degree, normalized |
| `closeness_centrality(graph)` | Reciprocal of average distance |
| `betweenness_centrality(graph)` | Share of shortest paths through a vertex, by Brandes |
| `pagerank(graph, damping=0.85)` | The stationary distribution of the random surfer |
| `hits(graph)` | Hub and authority scores |
| `random_walk(graph, source, steps, seed=None)` | A seeded walk |
| `spectral_properties(graph)` | Eigenvalues of the adjacency and Laplacian matrices |
| `algebraic_connectivity(graph)` | The second smallest Laplacian eigenvalue |
| `min_cut_partition(graph)` | A partition realizing a minimum cut |
| `communities(graph)` | A community partition |
| `louvain(graph, seed=None)` | Modularity optimization by the Louvain method |

Brandes' algorithm computes betweenness for every vertex in
O(V E) time rather than the cubic cost of the definition, and the
implementation says so and is validated against the definition on small
graphs. The spectral routines return exact values where the characteristic
polynomial factors over the rationals and high precision approximations
otherwise, and they say which they returned.

## Generators

| Routine | Graph |
| --- | --- |
| `complete_graph(n)` | Every pair adjacent |
| `path_graph(n)`, `cycle_graph(n)` | A path, a cycle |
| `star_graph(n)`, `wheel_graph(n)` | A star, a wheel |
| `grid_graph(rows, columns)` | A rectangular lattice |
| `hypercube_graph(dimension)` | Binary strings adjacent under one flip |
| `petersen_graph()` | The Petersen graph |
| `random_gnp(n, probability, seed=None)` | Each edge independently |
| `random_gnm(n, edges, seed=None)` | A uniformly random graph with m edges |
| `barabasi_albert(n, attachments, seed=None)` | Preferential attachment |
| `watts_strogatz(n, degree, probability, seed=None)` | Small world rewiring |

Every random generator takes a seed and is deterministic once it is
supplied, and the classical families are useful precisely because their
invariants are known: the Petersen graph has girth five and chromatic number
three, the hypercube of dimension $d$ is $d$ regular and bipartite, and the
complete graph on $n$ vertices has $n^{n-2}$ spanning trees. The suite uses
these as fixed points.

## Errors

| Exception | Raised when |
| --- | --- |
| `DomainError` | A vertex or an edge is not present |
| `ValidationError` | A weight is not numeric, or a matrix is not square |
| `DimensionError` | A matrix does not match the vertex count |
| `InfeasibleError` | No topological order, no perfect matching, no Hamiltonian cycle, or a negative cycle is reachable |
| `LimitExceededError` | An exponential enumeration exceeded the configured limit |
| `AxiomViolationError` | A type's promise fails, for instance a cyclic graph given to `Dag` |

## Design notes

**A graph carries its directedness.** `Graph` and `DiGraph` are separate
types rather than one type with a flag, because almost every algorithm needs
to know which it has, and a flag would push that question into every routine.
Conversion is explicit with `to_directed` and `to_undirected`.

**Weights are optional and exact.** An unweighted graph is a weighted graph
with every weight one, which is why the unweighted algorithms and the
weighted ones give the same answers on it. Integer and fractional weights
keep distances exact; float weights make them approximate, and the
documentation says so rather than silently rounding.

**Algorithms are free functions, not methods.** A graph has hundreds of
things that can be computed about it, and putting them all on the type would
produce an object nobody could read. The free functions group by subject
instead, so the import path says what family an algorithm belongs to.

**Every routine returns data, not a mutated graph.** A colouring is a
mapping, a flow is a mapping on edges, a spanning tree is an edge list, and
a matching is a set of pairs. Nothing is attached to the graph as a side
effect, which keeps a graph reusable across several analyses.

## See also

- The [graph algorithms tutorial](../tutorials/graph_algorithms.md), which
  develops the traversal, shortest path, spanning, and flow families in
  order.
- [`discretus.sets`](sets.md), for the relation and Hasse diagram
  conversions that produce graphs.
- [`discretus.algebra`](algebra.md), for Cayley graphs and for the exact
  matrices the spectral routines use.
- [`discretus.io`](io.md), for GraphML, GML, DOT, CSV, and edge list
  interchange.
- [`discretus.viz`](viz.md), for drawing graphs and trees.
