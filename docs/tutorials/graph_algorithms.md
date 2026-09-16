# Graph algorithms

This tutorial works through the graph package in the order the algorithms
build on one another: representation, then traversal, then shortest paths,
then spanning trees, then flow, then colouring. Each section states what the
algorithm does, shows it running, and says what it costs.

One example graph carries most of the tutorial, so that the algorithms can
be compared rather than merely listed.

## Building a graph

A graph is a pair of a vertex set and an edge set. Vertices may be any
hashable value, which here means strings.

```python
from discretus.graphs import Graph

roads = Graph()
roads.add_edges_from([
    ("Joensuu", "Kuopio", 135),
    ("Joensuu", "Savonlinna", 130),
    ("Kuopio", "Jyvaskyla", 145),
    ("Savonlinna", "Mikkeli", 105),
    ("Mikkeli", "Jyvaskyla", 175),
    ("Mikkeli", "Lahti", 120),
    ("Jyvaskyla", "Tampere", 150),
    ("Lahti", "Tampere", 130),
    ("Lahti", "Helsinki", 105),
    ("Tampere", "Helsinki", 180),
])

print(roads.order(), roads.size())
print(roads.degree("Tampere"), roads.neighbors("Tampere"))
print(roads.weight("Lahti", "Helsinki"))
```

The handshake lemma is the first invariant worth checking, because it holds
for every undirected graph and catches a construction mistake immediately.

$$\sum_{v \in V} \deg(v) = 2\,|E|$$

```python
print(sum(roads.degree(v) for v in roads.vertices()) == 2 * roads.size())
```

The same graph can be held four ways, and the choice is a performance
decision. The conversions are explicit.

```python
print(roads.adjacency_list()["Lahti"])
print(roads.edge_list()[:3])
matrix = roads.adjacency_matrix()
print(matrix.shape)
```

The rule of thumb: adjacency lists for traversal and Dijkstra, matrices for
all pairs computations and spectral work, edge lists for Kruskal, which
sorts the edges anyway.

## Traversal

Breadth first search visits vertices in order of their distance in edges
from the source; depth first search follows one path as far as it goes
before backtracking. Both are linear in the size of the graph.

```python
from discretus.graphs.traversal import bfs, dfs

print(list(bfs(roads, "Joensuu")))
print(list(dfs(roads, "Joensuu")))
```

The two orders differ, and the difference is the whole content of the
algorithms. Breadth first search is the one that finds shortest paths in an
unweighted graph, because it reaches each vertex by a fewest edge route.

```python
from discretus.graphs.shortest_path import bfs_shortest

hops, _ = bfs_shortest(roads, "Joensuu")
print(hops["Helsinki"])
```

Three edges from Joensuu to Helsinki, counting edges rather than distance.
The weighted answer is a different question, and the next section answers it.

Connectivity follows from traversal. A graph is connected when one traversal
reaches everything.

```python
from discretus.graphs.traversal import connected_components

print(connected_components(roads))
print(roads.is_connected())

roads_plus = Graph()
roads_plus.add_edges_from(roads.edges())
roads_plus.add_edge("Rovaniemi", "Oulu", 220)
print(len(connected_components(roads_plus)))
```

Articulation points and bridges are the vertices and edges whose removal
disconnects the graph, and they are what a reliability question is really
asking.

```python
from discretus.graphs.traversal import articulation_points, bridges

print(articulation_points(roads))
print(bridges(roads))
```

In a directed graph, connectivity splits into two notions, and strong
connectivity is the interesting one.

```python
from discretus.graphs import DiGraph
from discretus.graphs.traversal import strongly_connected_components, topological_sort

dependencies = DiGraph()
dependencies.add_edges_from([
    ("core", "sets"),
    ("core", "logic"),
    ("sets", "graphs"),
    ("logic", "sat"),
    ("graphs", "viz"),
    ("sat", "viz"),
])

print(topological_sort(dependencies))
print(strongly_connected_components(dependencies))
```

A topological order exists exactly when the graph is acyclic, and the
library says so rather than returning a partial answer when it is not.

```python
from discretus import InfeasibleError

cyclic = DiGraph()
cyclic.add_edges_from([("a", "b"), ("b", "c"), ("c", "a")])
try:
    topological_sort(cyclic)
except InfeasibleError as error:
    print("no order:", error)
```

## Shortest paths

Dijkstra's algorithm finds shortest paths from one source when every weight
is non negative. With a binary heap it costs

$$O\big((|V| + |E|) \log |V|\big).$$

```python
from discretus.graphs.shortest_path import dijkstra, reconstruct_path

distances, predecessors = dijkstra(roads, "Joensuu")
print(distances["Helsinki"])
print(reconstruct_path(predecessors, "Helsinki"))
```

Every single source routine in the package returns the same pair, a distance
map and a predecessor map, so retrieving a path is always the same two
calls. That consistency is deliberate and it is worth relying on.

Bellman Ford is slower at $O(|V|\,|E|)$ and handles negative weights, and it
detects a negative cycle rather than returning nonsense.

```python
from discretus.graphs.shortest_path import bellman_ford

bellman_distances, _ = bellman_ford(roads, "Joensuu")
print(bellman_distances == distances)
```

The two agree, and they must: on a graph with non negative weights both
compute the same shortest path distances. This library's test suite asserts
exactly that on randomized graphs, which is the cross validation pattern it
applies wherever two routines must agree.

A negative weight changes the picture.

```python
discounts = DiGraph()
discounts.add_edges_from([("a", "b", 4), ("b", "c", -2), ("a", "c", 3)])
print(bellman_ford(discounts, "a")[0]["c"])

negative_cycle = DiGraph()
negative_cycle.add_edges_from([("a", "b", 1), ("b", "a", -2)])
try:
    bellman_ford(negative_cycle, "a")
except InfeasibleError as error:
    print("negative cycle:", error)
```

All pairs distances have their own algorithms. Floyd Warshall is cubic and
simple; Johnson is better on a sparse graph.

```python
from discretus.graphs.shortest_path import floyd_warshall, johnson

all_pairs = floyd_warshall(roads)
print(all_pairs["Joensuu"]["Helsinki"])
print(johnson(roads)["Joensuu"]["Helsinki"] == all_pairs["Joensuu"]["Helsinki"])
```

The choice between them is about density. Floyd Warshall does not care how
many edges there are; Johnson runs Dijkstra from every vertex, so it wins
when the edge count is far below the square of the vertex count.

A heuristic can help when only one target matters.

```python
from discretus.graphs.shortest_path import a_star

coordinates = {
    "Joensuu": (62.6, 29.8), "Kuopio": (62.9, 27.7), "Savonlinna": (61.9, 28.9),
    "Jyvaskyla": (62.2, 25.7), "Mikkeli": (61.7, 27.3), "Lahti": (61.0, 25.7),
    "Tampere": (61.5, 23.8), "Helsinki": (60.2, 24.9),
}


def straight_line(vertex, target):
    ax, ay = coordinates[vertex]
    bx, by = coordinates[target]
    return 80 * ((ax - bx) ** 2 + (ay - by) ** 2) ** 0.5


cost, path = a_star(roads, "Joensuu", "Helsinki", heuristic=straight_line)
print(cost, path)
```

The heuristic must never overestimate the true remaining distance, and when
it does not, the answer is exactly Dijkstra's answer with less search. The
reference states the condition, because a heuristic that overestimates
produces a confident wrong answer.

## Spanning trees

A spanning tree of a connected graph on $n$ vertices has exactly $n - 1$
edges, and a minimum spanning tree has the least total weight among them.

```python
from discretus.graphs.spanning import boruvka, kruskal, prim

tree = kruskal(roads)
print(len(tree), roads.order() - 1)
print(sum(weight for _, _, weight in tree))
```

Three algorithms compute it, by three different strategies. Kruskal sorts
the edges and adds any that joins two components, using a disjoint set
forest. Prim grows a single tree with a heap. Boruvka contracts every
component's cheapest edge in each round.

```python
total = sum(weight for _, _, weight in tree)
for algorithm in (kruskal, prim, boruvka):
    result = algorithm(roads)
    print(algorithm.__name__, len(result), sum(w for _, _, w in result) == total)
```

The totals agree and the trees themselves may differ, because ties can be
broken differently. That is exactly what the cross validation test asserts,
and asserting equality of the trees would fail for correct implementations.

The number of spanning trees is computable without enumerating them, by
Kirchhoff's matrix tree theorem: it is any cofactor of the Laplacian matrix.

```python
from discretus.graphs.generators import complete_graph
from discretus.graphs.spanning import spanning_tree_count

print(spanning_tree_count(roads))
for n in range(2, 7):
    print(n, spanning_tree_count(complete_graph(n)), n ** (n - 2))
```

The second loop is Cayley's formula, that the complete graph on $n$ vertices
has $n^{n-2}$ spanning trees, computed two ways and agreeing exactly because
the determinant is exact.

## Flow

A flow network is a directed graph with capacities, a source, and a sink.
The maximum flow min cut theorem says the largest flow equals the smallest
cut capacity.

```python
from discretus.graphs.flow import dinic, edmonds_karp, ford_fulkerson, max_flow_min_cut

network = DiGraph()
network.add_edges_from([
    ("source", "a", 10), ("source", "b", 5),
    ("a", "b", 15), ("a", "sink", 5),
    ("b", "sink", 10),
])

value, flow = edmonds_karp(network, "source", "sink")
print(value)
print({edge: amount for edge, amount in flow.items() if amount})

cut_value, (left, right) = max_flow_min_cut(network, "source", "sink")
print(cut_value, left, right)
print(value == cut_value)
```

Four implementations are provided and all return the same value, which is
the theorem and also the cross validation.

```python
for algorithm in (ford_fulkerson, edmonds_karp, dinic):
    print(algorithm.__name__, algorithm(network, "source", "sink")[0])
```

They differ in complexity rather than in answer. Ford Fulkerson depends on
the flow value, which can be bad with large capacities. Edmonds Karp
augments along shortest paths and is polynomial. Dinic uses level graphs and
is better on dense networks.

Matching is a flow problem in disguise, and the specialized algorithms are
faster than the reduction.

```python
from discretus.graphs import BipartiteGraph
from discretus.graphs.flow import hopcroft_karp

assignments = BipartiteGraph()
assignments.add_edges_from([
    ("ana", "monday"), ("ana", "tuesday"),
    ("ben", "tuesday"),
    ("cai", "monday"), ("cai", "wednesday"),
])
matching = hopcroft_karp(assignments)
print(len(matching), matching)
```

Hall's marriage theorem says a perfect matching on one side exists exactly
when every subset of that side has at least as many neighbours as members,
and the library can report the violating subset when there is none, which is
far more useful than a bare failure.

## Colouring

A proper colouring assigns colours so that adjacent vertices differ, and the
chromatic number is the least number of colours needed.

```python
from discretus.graphs.coloring import (
    chromatic_number, chromatic_polynomial, dsatur, greedy_coloring, is_bipartite, welsh_powell,
)

print(is_bipartite(roads))
print(chromatic_number(roads))
print(dsatur(roads))
```

The heuristics are polynomial and the exact routine is exponential, because
the problem is NP hard. Compare them.

```python
for method in (greedy_coloring, welsh_powell, dsatur):
    colouring = method(roads)
    used = len(set(colouring.values()))
    proper = all(colouring[u] != colouring[v] for u, v in roads.edges())
    print(method.__name__, used, proper)
```

Every heuristic returns a proper colouring, and each may use more colours
than necessary. The check on the last line is worth keeping: a colouring is
easy to verify even when it is hard to find, which is the defining feature
of this class of problems.

The chromatic polynomial counts proper colourings as a function of the
number of colours available.

```python
polynomial = chromatic_polynomial(complete_graph(4))
print(polynomial.to_text())
print(polynomial.evaluate(4), polynomial.evaluate(3))
```

For the complete graph on four vertices the polynomial is the falling
factorial, its value at four is twenty four, and its value at three is zero,
which is the statement that three colours do not suffice.

## Structure

The remaining families answer questions about shape rather than about
routes.

```python
from discretus.graphs.properties import (
    center, clique_number, degree_sequence, diameter, girth,
    max_independent_set, min_vertex_cover, radius,
)

print(degree_sequence(roads))
print(diameter(roads), radius(roads), center(roads))
print(girth(roads))
print(clique_number(roads), len(max_independent_set(roads)), len(min_vertex_cover(roads)))
```

The last line contains a theorem: the independence number plus the vertex
cover number equals the vertex count, for every graph. Check it.

```python
print(len(max_independent_set(roads)) + len(min_vertex_cover(roads)) == roads.order())
```

Centrality ranks vertices by importance, with several notions of important.

```python
from discretus.graphs.algorithms import (
    betweenness_centrality, closeness_centrality, degree_centrality, pagerank,
)

for name, measure in [
    ("degree", degree_centrality),
    ("closeness", closeness_centrality),
    ("betweenness", betweenness_centrality),
]:
    ranking = measure(roads)
    top = max(ranking, key=ranking.get)
    print(name, top, round(float(ranking[top]), 3))
```

The three measures often disagree, and the disagreement is informative:
degree finds the busiest junction, closeness finds the most central one, and
betweenness finds the one whose removal would hurt most.

## Generators and experiments

The classical families have known invariants, which makes them the right
fixtures for an experiment.

```python
from discretus.graphs.generators import (
    complete_graph, cycle_graph, hypercube_graph, petersen_graph, random_gnp,
)

petersen = petersen_graph()
print(petersen.order(), petersen.size(), girth(petersen), chromatic_number(petersen))

cube = hypercube_graph(4)
print(cube.order(), cube.is_regular(), is_bipartite(cube))
```

The Petersen graph has ten vertices, fifteen edges, girth five, and
chromatic number three. The hypercube of dimension four is four regular and
bipartite. Those are facts, so they make good assertions.

Random models are for experiments, and they take seeds.

```python
from discretus.utils.timing import Timer

for probability in (0.05, 0.1, 0.2):
    graph = random_gnp(200, probability, seed=2026)
    with Timer() as timer:
        components = connected_components(graph)
    print(probability, graph.size(), len(components), timer.human)
```

Watching the component count collapse as the edge probability rises past the
threshold near the reciprocal of the vertex count is the classic experiment
in random graph theory, and it is four lines here.

## Choosing an algorithm

The package offers several routines for most questions, and the reference
states the complexity of each. This section collects the decisions in one
place, because the choice is usually more important than anything else you
can do about performance.

**Shortest paths.** Unweighted graph: breadth first search, which is linear.
Non negative weights: Dijkstra. Any weights: Bellman Ford, and read its
negative cycle report. Directed acyclic graph with any weights:
the topological relaxation, which is linear. All pairs on a dense graph:
Floyd Warshall. All pairs on a sparse graph: Johnson. One target with a
geometric structure: A star with an admissible heuristic.

**Spanning trees.** Sparse graph: Kruskal, whose cost is dominated by
sorting the edges. Dense graph: Prim, which does not touch every edge.
Parallel or distributed setting: Boruvka, whose rounds are independent. The
count rather than a tree: the matrix tree theorem, which needs no
enumeration at all.

**Maximum flow.** Small integer capacities: any of them. Large capacities:
not Ford Fulkerson, whose cost depends on the flow value. Dense network:
Dinic. Unit capacities and a bipartite structure: Hopcroft Karp, which is
asymptotically better than any general flow routine on that input.

**Colouring.** A proper colouring quickly: DSATUR. The exact chromatic
number on a small graph: the exact routine. Two colourability: the bipartite
test, which is linear and answers the question completely. The count of
colourings: the chromatic polynomial.

**Connectivity.** Undirected components: one traversal. Strong components:
Tarjan, in one pass. Vertices and edges whose removal disconnects: the
articulation point and bridge routines, which are one traversal each and far
cheaper than testing every removal.

A worked comparison, on a graph large enough for the difference to show:

```python
from discretus.graphs.generators import random_gnp
from discretus.graphs.shortest_path import (
    bellman_ford, dijkstra, floyd_warshall, johnson,
)
from discretus.utils.timing import Timer

graph = random_gnp(120, 0.06, seed=2026, weighted=True, max_weight=50)
print(graph.order(), graph.size())

with Timer() as one:
    dijkstra(graph, graph.vertices()[0])
with Timer() as two:
    bellman_ford(graph, graph.vertices()[0])
print("single source:", one.human, two.human)

with Timer() as three:
    floyd_warshall(graph)
with Timer() as four:
    johnson(graph)
print("all pairs:", three.human, four.human)
```

On a sparse graph the ordering is the one the complexities predict, and
seeing it once is worth more than reading it several times.

## Where the cost is exponential

Four families in this package are exponential, and they are exponential
because the problems are hard rather than because the implementations are
poor. Knowing which they are prevents the most common surprise.

| Routine | Why |
| --- | --- |
| `chromatic_number` | Graph colouring is NP hard |
| `max_clique`, `max_independent_set`, `min_vertex_cover` | All NP hard, and interreducible |
| `has_hamiltonian_path`, `hamiltonian_cycle`, `tsp_exact` | Hamiltonicity and the salesman problem are NP hard |
| `chromatic_polynomial` | Counting colourings is harder still |

Each of them has a polynomial alternative that answers a weaker question,
and the pairing is worth memorizing.

```python
from discretus.graphs.coloring import chromatic_number, dsatur
from discretus.graphs.paths import has_eulerian_circuit, has_hamiltonian_path
from discretus.graphs.properties import clique_number, max_independent_set

small = random_gnp(14, 0.3, seed=11)

# Exponential: the exact chromatic number. Polynomial: a proper colouring.
print(chromatic_number(small), len(set(dsatur(small).values())))

# Exponential: Hamiltonian. Polynomial: Eulerian, decided by degrees.
print(has_hamiltonian_path(small), has_eulerian_circuit(small))

# Exponential: the clique number. Polynomial: the degree sequence bound.
print(clique_number(small), max(small.degree(v) for v in small.vertices()) + 1)
```

The contrast between the Hamiltonian and the Eulerian questions is the most
instructive of these. Whether a graph has a closed walk using every edge
exactly once is decidable by looking at the degrees, in linear time. Whether
it has a walk using every vertex exactly once is NP complete. The two
questions look similar and are not, and the package places them next to each
other with their complexities stated for exactly that reason.

The enumeration limit protects against accidentally invoking one of the
exponential routines on a large input, and raising it deliberately is the
right response when you know what you are asking for.

```python
from discretus.config import config_scope

with config_scope(max_enumeration=10 ** 7):
    print(chromatic_number(small))
```

## Exercises

1. Add a new city to the road graph and recompute the shortest path from
   Joensuu to Helsinki. Did it change? Explain why or why not from the
   predecessor map.
2. Verify on twenty random weighted graphs that Dijkstra and Bellman Ford
   agree, and that all three spanning tree algorithms produce the same total
   weight.
3. Compute the diameter of the road graph twice, once from
   `floyd_warshall` and once as the maximum eccentricity from repeated
   Dijkstra, and check that they agree.
4. Build the complement of the road graph and confirm that its cliques are
   the independent sets of the original.
5. Turn the bipartite assignment graph into a flow network by hand, with a
   source joined to one side and a sink joined to the other, and confirm
   that the maximum flow equals the matching size.
6. Find a graph where the greedy colouring uses more colours than DSATUR,
   and one where they agree.

## Seeing the results

Every result in this tutorial is data, and the visualization package takes
data. That combination is what makes a graph computation checkable by eye.

```python
from discretus.graphs.coloring import dsatur
from discretus.graphs.shortest_path import dijkstra, reconstruct_path
from discretus.graphs.spanning import kruskal
from discretus.viz import color_palette, graph_draw, spring_layout

# One layout, reused, so that the three figures are comparable.
positions = spring_layout.compute(roads, seed=2026, iterations=300)

# The colouring as colours.
colouring = graph_draw.draw(
    roads, layout=positions, backend="svg",
    colors=color_palette.for_coloring(dsatur(roads)), labels=True,
)

# The shortest path as an emphasis.
_, predecessors = dijkstra(roads, "Joensuu")
route = graph_draw.draw(
    roads, layout=positions, backend="svg",
    highlight=reconstruct_path(predecessors, "Helsinki"), labels=True,
)

# The spanning tree as an emphasis on edges.
tree = graph_draw.draw(
    roads, layout=positions, backend="svg",
    highlight=[(u, v) for u, v, _ in kruskal(roads)], labels=True,
)

for name, markup in [("colouring", colouring), ("route", route), ("tree", tree)]:
    open(f"{name}.svg", "w", encoding="utf-8").write(markup)
```

Reusing one layout across the three figures is the detail that makes them
useful: the cities are in the same places, so the differences between the
pictures are differences in the results rather than differences in the
drawing.

For a quick look while working, the text backend needs nothing at all.

```python
print(graph_draw.draw(roads, backend="ascii"))
```

## Persisting a graph

A graph that took work to build should not have to be rebuilt, and a graph
from elsewhere should be readable. Both are one call, and the writers are
deterministic, so a graph under version control produces a meaningful diff.

```python
from discretus.io import graph_io, graphml

text = graphml.dumps(roads)
assert graphml.loads(text) == roads

graph_io.write(roads, "roads.graphml")
graph_io.write(roads, "roads.gml")
graph_io.write(roads, "roads.txt", format="edgelist")

same = graph_io.read("roads.graphml")
print(same == roads, same.weight("Lahti", "Helsinki"))
```

The round trip assertion on the second line is worth writing whenever a
pipeline is being built, because it catches a format mismatch immediately
rather than three stages later.

## Where to go next

- The [graph reference](../api/graphs.md) for the complete interface,
  including the algorithms this tutorial did not reach: Eulerian and
  Hamiltonian analysis, the travelling salesman routines, planarity, and the
  spectral measures.
- [Satisfiability](sat_solving.md), for the colouring problem encoded as a
  logical one.
- [Set theory](set_theory.md), for the relations and orders that convert
  into graphs.
- [Group theory](group_theory.md), for Cayley graphs.
