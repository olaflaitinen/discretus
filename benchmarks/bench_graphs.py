# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Benchmarks for the graph package.

The graph package is the largest in the library and the one whose reference
makes the most complexity claims, so this is the file where most of those
claims are checked. It is organized around the comparisons that matter
rather than around the module layout, because the useful question is almost
never how fast one routine is but which of two routines to call.

The comparisons this file is built to support:

    Dijkstra against Bellman Ford on the same graph. The reference states
    one as logarithmic in the vertex count per edge and the other as the
    product of the vertex and edge counts. Both are correct on a graph with
    non negative weights, so the choice is purely about cost, and the growth
    ratios are where that choice is justified.

    Floyd Warshall against Johnson. All pairs distances, cubic in the vertex
    count against a Dijkstra run from every vertex. The crossover depends on
    the density, so both are measured on a sparse and on a dense family.

    Kruskal against Prim against Boruvka. Three algorithms for one problem,
    with different strategies and different preferred densities.

    The four maximum flow implementations. They must return the same value,
    and they differ by orders of magnitude on the right input, which is why
    the reference recommends one per situation.

    Hopcroft Karp against a general flow computation for bipartite matching.
    The specialized algorithm is asymptotically better, and measuring both
    is the only way to say by how much.

    A colouring heuristic against the exact chromatic number. Polynomial
    against exponential, on the same graph, which is the starkest contrast
    in the whole library.

    The four graph representations. The reference tells a reader to choose
    an adjacency list for traversal and a matrix for all pairs work, and
    this file measures the same algorithm over both where that is possible.

Graphs are generated from a seed derived from the benchmark name, and two
density families are used throughout: sparse, with a constant average
degree, and dense, with a quadratic edge count. A benchmark measured on only
one of them would support the wrong recommendation.
"""

from __future__ import annotations

from typing import Any, List, Tuple

from . import benchmark, random_pairs, require, requires_all, seeded

# ---------------------------------------------------------------------------
# The modules under measurement
# ---------------------------------------------------------------------------

graphs_module = require("discretus.graphs", "Graph", "DiGraph", "BipartiteGraph")
traversal_module = require(
    "discretus.graphs.traversal", "bfs", "dfs", "connected_components"
)
shortest_path_module = require(
    "discretus.graphs.shortest_path", "dijkstra", "bellman_ford", "floyd_warshall"
)
spanning_module = require("discretus.graphs.spanning", "kruskal", "prim", "boruvka")
flow_module = require("discretus.graphs.flow", "edmonds_karp", "dinic", "hopcroft_karp")
coloring_module = require(
    "discretus.graphs.coloring", "dsatur", "chromatic_number", "is_bipartite"
)
paths_module = require(
    "discretus.graphs.paths", "has_eulerian_circuit", "has_hamiltonian_path"
)
properties_module = require(
    "discretus.graphs.properties", "degree_sequence", "diameter", "max_clique"
)
algorithms_module = require(
    "discretus.graphs.algorithms", "pagerank", "betweenness_centrality"
)
generators_module = require(
    "discretus.graphs.generators", "complete_graph", "random_gnp"
)

GROUP_STRUCTURES = "graphs.structures"
GROUP_TRAVERSAL = "graphs.traversal"
GROUP_SHORTEST_PATH = "graphs.shortest_path"
GROUP_SPANNING = "graphs.spanning"
GROUP_FLOW = "graphs.flow"
GROUP_COLORING = "graphs.coloring"
GROUP_PATHS = "graphs.paths"
GROUP_PROPERTIES = "graphs.properties"
GROUP_ANALYSIS = "graphs.analysis"

#: Average degree of the sparse family. Four is dense enough to be connected
#: with high probability and sparse enough that the edge count is linear.
SPARSE_DEGREE = 4


# ---------------------------------------------------------------------------
# Graph construction
# ---------------------------------------------------------------------------
# Every graph is built from an explicit pair list rather than through the
# library's own generators, so that a benchmark of a generator is not
# measured against itself. Construction is never timed.


def make_sparse_graph(vertices: int) -> Any:
    """Return a connected undirected graph with a constant average degree.

    A path is laid down first so that the graph is certainly connected, and
    the remaining edges are added at random. Connectivity matters because
    several algorithms terminate early on a disconnected graph and would
    then be measured on a fraction of the input.
    """
    assert graphs_module is not None
    source = seeded(f"graphs.sparse.{vertices}")
    graph = graphs_module.Graph()
    for index in range(1, vertices):
        graph.add_edge(index - 1, index, weight=source.randint(1, 100))
    extra = vertices * SPARSE_DEGREE // 2
    for left, right in random_pairs(extra, vertices, label=f"graphs.sparse.{vertices}"):
        graph.add_edge(left, right, weight=source.randint(1, 100))
    return graph


def make_dense_graph(vertices: int) -> Any:
    """Return an undirected graph with a quadratic edge count."""
    assert graphs_module is not None
    source = seeded(f"graphs.dense.{vertices}")
    graph = graphs_module.Graph()
    for left in range(vertices):
        for right in range(left + 1, vertices):
            graph.add_edge(left, right, weight=source.randint(1, 100))
    return graph


def make_sparse_digraph(vertices: int) -> Any:
    """Return a strongly connected directed graph with a constant degree."""
    assert graphs_module is not None
    source = seeded(f"graphs.sparse_digraph.{vertices}")
    graph = graphs_module.DiGraph()
    for index in range(vertices):
        graph.add_edge(index, (index + 1) % vertices, weight=source.randint(1, 100))
    extra = vertices * SPARSE_DEGREE
    for _ in range(extra):
        left = source.randrange(vertices)
        right = source.randrange(vertices)
        if left != right:
            graph.add_edge(left, right, weight=source.randint(1, 100))
    return graph


def make_dag(vertices: int) -> Any:
    """Return a directed acyclic graph, for the topological routines."""
    assert graphs_module is not None
    source = seeded(f"graphs.dag.{vertices}")
    graph = graphs_module.DiGraph()
    for index in range(1, vertices):
        parent = source.randrange(index)
        graph.add_edge(parent, index, weight=source.randint(1, 100))
    for _ in range(vertices):
        left = source.randrange(vertices)
        right = source.randrange(vertices)
        if left < right:
            graph.add_edge(left, right, weight=source.randint(1, 100))
    return graph


def make_flow_network(vertices: int) -> Any:
    """Return a layered flow network with a source and a sink.

    A layered network is the realistic shape for a flow problem and is also
    the shape on which the four implementations differ most, because the
    number of augmenting rounds depends on the layer count.
    """
    assert graphs_module is not None
    source_random = seeded(f"graphs.flow.{vertices}")
    graph = graphs_module.DiGraph()
    layers = max(3, int(vertices**0.5))
    per_layer = max(2, vertices // layers)
    graph.add_vertex("source")
    graph.add_vertex("sink")
    previous = ["source"]
    for layer in range(layers):
        current = [f"v{layer}_{index}" for index in range(per_layer)]
        for node in current:
            for parent in previous:
                graph.add_edge(parent, node, capacity=source_random.randint(1, 50))
        previous = current
    for node in previous:
        graph.add_edge(node, "sink", capacity=source_random.randint(1, 50))
    return graph


def make_bipartite_graph(vertices: int) -> Any:
    """Return a bipartite graph with a constant average degree per side."""
    assert graphs_module is not None
    source = seeded(f"graphs.bipartite.{vertices}")
    graph = graphs_module.BipartiteGraph()
    half = max(1, vertices // 2)
    for left in range(half):
        for _ in range(SPARSE_DEGREE):
            graph.add_edge(f"l{left}", f"r{source.randrange(half)}")
    return graph


def make_small_graph(vertices: int) -> Any:
    """Return a small sparse graph, for the exponential routines."""
    return make_sparse_graph(vertices)


def make_graph_with_matrix(vertices: int) -> Tuple[Any, Any]:
    """Return a graph together with its adjacency matrix."""
    graph = make_sparse_graph(vertices)
    return graph, graph.adjacency_matrix()


def make_edge_list(vertices: int) -> List[Tuple[int, int, int]]:
    """Return the edge list of a sparse graph, for construction benchmarks."""
    graph = make_sparse_graph(vertices)
    return graph.edge_list()


# ---------------------------------------------------------------------------
# Structures and representations
# ---------------------------------------------------------------------------


@benchmark(
    group=GROUP_STRUCTURES,
    sizes=[1_000, 10_000, 100_000],
    complexity="O(V + E)",
    setup=make_edge_list,
    requires=graphs_module,
    note="bulk construction from an edge list",
)
def construct_from_edges(edges: List[Tuple[int, int, int]]) -> Any:
    """Build a graph from an edge list."""
    graph = graphs_module.Graph()
    graph.add_edges_from(edges)
    return graph


@benchmark(
    group=GROUP_STRUCTURES,
    sizes=[1_000, 10_000, 100_000],
    complexity="O(V + E)",
    setup=make_sparse_graph,
    requires=graphs_module,
    note="the adjacency list view, which the traversals consume",
)
def adjacency_list(graph: Any) -> Any:
    """Build the adjacency list view of a graph."""
    return graph.adjacency_list()


@benchmark(
    group=GROUP_STRUCTURES,
    sizes=[100, 300, 900],
    complexity="O(V squared)",
    setup=make_sparse_graph,
    requires=graphs_module,
    note=(
        "the matrix view, quadratic in the vertex count regardless of the "
        "edge count, which is why it suits dense graphs and all pairs work"
    ),
)
def adjacency_matrix(graph: Any) -> Any:
    """Build the adjacency matrix view of a graph."""
    return graph.adjacency_matrix()


@benchmark(
    group=GROUP_STRUCTURES,
    sizes=[100, 300, 900],
    complexity="O(V squared)",
    setup=make_sparse_graph,
    requires=graphs_module,
    note="the Laplacian, which the spectral and spanning count routines need",
)
def laplacian_matrix(graph: Any) -> Any:
    """Build the Laplacian matrix of a graph."""
    return graph.laplacian_matrix()


@benchmark(
    group=GROUP_STRUCTURES,
    sizes=[1_000, 10_000, 100_000],
    complexity="O(1) per query",
    setup=make_sparse_graph,
    requires=graphs_module,
)
def neighbour_queries(graph: Any) -> int:
    """Query the neighbours of a thousand vertices."""
    total = 0
    for vertex in graph.vertices()[:1_000]:
        total += len(graph.neighbors(vertex))
    return total


@benchmark(
    group=GROUP_STRUCTURES,
    sizes=[1_000, 10_000, 100_000],
    complexity="O(V + E)",
    setup=make_sparse_graph,
    requires=graphs_module,
    note="the handshake lemma, which is the cheapest structural invariant",
)
def degree_sum(graph: Any) -> int:
    """Sum every degree, which must be twice the edge count."""
    return sum(graph.degree(vertex) for vertex in graph.vertices())


# ---------------------------------------------------------------------------
# Traversal and connectivity
# ---------------------------------------------------------------------------


@benchmark(
    group=GROUP_TRAVERSAL,
    sizes=[1_000, 10_000, 100_000],
    complexity="O(V + E)",
    setup=make_sparse_graph,
    requires=requires_all(graphs_module, traversal_module),
)
def breadth_first_search(graph: Any) -> int:
    """Traverse a graph in breadth first order."""
    return sum(1 for _ in traversal_module.bfs(graph, graph.vertices()[0]))


@benchmark(
    group=GROUP_TRAVERSAL,
    sizes=[1_000, 10_000, 100_000],
    complexity="O(V + E)",
    setup=make_sparse_graph,
    requires=requires_all(graphs_module, traversal_module),
)
def depth_first_search(graph: Any) -> int:
    """Traverse a graph in depth first order."""
    return sum(1 for _ in traversal_module.dfs(graph, graph.vertices()[0]))


@benchmark(
    group=GROUP_TRAVERSAL,
    sizes=[1_000, 10_000, 100_000],
    complexity="O(V + E)",
    setup=make_sparse_graph,
    requires=requires_all(graphs_module, traversal_module),
    note=(
        "the iterative variant, which is what a graph deep enough to exceed "
        "the recursion limit needs"
    ),
)
def iterative_depth_first_search(graph: Any) -> int:
    """Traverse a graph in depth first order without recursion."""
    return sum(1 for _ in traversal_module.iterative_dfs(graph, graph.vertices()[0]))


@benchmark(
    group=GROUP_TRAVERSAL,
    sizes=[1_000, 10_000, 100_000],
    complexity="O(V + E)",
    setup=make_sparse_graph,
    requires=requires_all(graphs_module, traversal_module),
)
def connected_components(graph: Any) -> int:
    """Find the connected components of a graph."""
    return len(traversal_module.connected_components(graph))


@benchmark(
    group=GROUP_TRAVERSAL,
    sizes=[1_000, 10_000, 100_000],
    complexity="O(V + E) in one pass",
    setup=make_sparse_digraph,
    requires=requires_all(graphs_module, traversal_module),
    note="Tarjan's algorithm, which uses one traversal and a low link stack",
)
def tarjan_strong_components(graph: Any) -> int:
    """Find the strong components by Tarjan's algorithm."""
    return len(traversal_module.tarjan_scc(graph))


@benchmark(
    group=GROUP_TRAVERSAL,
    sizes=[1_000, 10_000, 100_000],
    complexity="O(V + E) in two passes",
    setup=make_sparse_digraph,
    requires=requires_all(graphs_module, traversal_module),
    note=(
        "Kosaraju's algorithm, which traverses the graph and its reverse; "
        "the same answer as Tarjan at roughly twice the work"
    ),
)
def kosaraju_strong_components(graph: Any) -> int:
    """Find the strong components by Kosaraju's algorithm."""
    return len(traversal_module.kosaraju(graph))


@benchmark(
    group=GROUP_TRAVERSAL,
    sizes=[1_000, 10_000, 100_000],
    complexity="O(V + E)",
    setup=make_sparse_graph,
    requires=requires_all(graphs_module, traversal_module),
    note="cut vertices in one traversal, rather than by trying every removal",
)
def articulation_points(graph: Any) -> int:
    """Find the articulation points of a graph."""
    return len(traversal_module.articulation_points(graph))


@benchmark(
    group=GROUP_TRAVERSAL,
    sizes=[1_000, 10_000, 100_000],
    complexity="O(V + E)",
    setup=make_sparse_graph,
    requires=requires_all(graphs_module, traversal_module),
)
def bridges(graph: Any) -> int:
    """Find the bridges of a graph."""
    return len(traversal_module.bridges(graph))


@benchmark(
    group=GROUP_TRAVERSAL,
    sizes=[1_000, 10_000, 100_000],
    complexity="O(V + E)",
    setup=make_dag,
    requires=requires_all(graphs_module, traversal_module),
)
def topological_sort(graph: Any) -> List[Any]:
    """Compute a topological order of a directed acyclic graph."""
    return traversal_module.topological_sort(graph)


@benchmark(
    group=GROUP_TRAVERSAL,
    sizes=[1_000, 10_000, 100_000],
    complexity="O(V + E)",
    setup=make_dag,
    requires=requires_all(graphs_module, traversal_module),
    note="Kahn's algorithm, which processes vertices by in degree",
)
def kahn_topological_sort(graph: Any) -> List[Any]:
    """Compute a topological order by Kahn's algorithm."""
    return traversal_module.kahn(graph)


# ---------------------------------------------------------------------------
# Shortest paths
# ---------------------------------------------------------------------------


@benchmark(
    group=GROUP_SHORTEST_PATH,
    sizes=[1_000, 10_000, 100_000],
    complexity="O((V + E) log V) with a binary heap",
    setup=make_sparse_graph,
    requires=requires_all(graphs_module, shortest_path_module),
)
def dijkstra_sparse(graph: Any) -> Any:
    """Single source shortest paths on a sparse graph."""
    return shortest_path_module.dijkstra(graph, graph.vertices()[0])


@benchmark(
    group=GROUP_SHORTEST_PATH,
    sizes=[100, 300, 600],
    complexity="O((V + E) log V)",
    setup=make_dense_graph,
    requires=requires_all(graphs_module, shortest_path_module),
    note="the same routine on a dense graph, where the edge term dominates",
)
def dijkstra_dense(graph: Any) -> Any:
    """Single source shortest paths on a dense graph."""
    return shortest_path_module.dijkstra(graph, graph.vertices()[0])


@benchmark(
    group=GROUP_SHORTEST_PATH,
    sizes=[200, 500, 1_000],
    complexity="O(V times E)",
    setup=make_sparse_graph,
    requires=requires_all(graphs_module, shortest_path_module),
    note=(
        "the same answer as Dijkstra on a graph with non negative weights, "
        "at a cost that grows as the product rather than the sum"
    ),
)
def bellman_ford_sparse(graph: Any) -> Any:
    """Single source shortest paths tolerating negative weights."""
    return shortest_path_module.bellman_ford(graph, graph.vertices()[0])


@benchmark(
    group=GROUP_SHORTEST_PATH,
    sizes=[200, 500, 1_000],
    complexity="O(V times E) worst case, far better in practice",
    setup=make_sparse_graph,
    requires=requires_all(graphs_module, shortest_path_module),
    note="the queue based variant, which visits far fewer relaxations",
)
def spfa(graph: Any) -> Any:
    """Single source shortest paths by the queue based variant."""
    return shortest_path_module.spfa(graph, graph.vertices()[0])


@benchmark(
    group=GROUP_SHORTEST_PATH,
    sizes=[1_000, 10_000, 100_000],
    complexity="O(V + E)",
    setup=make_sparse_graph,
    requires=requires_all(graphs_module, shortest_path_module),
    note=(
        "the unweighted case, which is linear; calling Dijkstra here would "
        "pay a logarithmic factor for nothing"
    ),
)
def bfs_shortest(graph: Any) -> Any:
    """Shortest paths by edge count rather than by weight."""
    return shortest_path_module.bfs_shortest(graph, graph.vertices()[0])


@benchmark(
    group=GROUP_SHORTEST_PATH,
    sizes=[1_000, 10_000, 100_000],
    complexity="O(V + E) with a topological order",
    setup=make_dag,
    requires=requires_all(graphs_module, shortest_path_module),
    note="linear even with negative weights, because the order is known",
)
def dag_shortest(graph: Any) -> Any:
    """Shortest paths on a directed acyclic graph."""
    return shortest_path_module.dag_shortest(graph, graph.vertices()[0])


@benchmark(
    group=GROUP_SHORTEST_PATH,
    sizes=[60, 120, 240],
    complexity="O(V cubed)",
    setup=make_sparse_graph,
    requires=requires_all(graphs_module, shortest_path_module),
    note="all pairs, and indifferent to the edge count",
)
def floyd_warshall_sparse(graph: Any) -> Any:
    """All pairs shortest paths by Floyd Warshall on a sparse graph."""
    return shortest_path_module.floyd_warshall(graph)


@benchmark(
    group=GROUP_SHORTEST_PATH,
    sizes=[60, 120, 240],
    complexity="O(V cubed)",
    setup=make_dense_graph,
    requires=requires_all(graphs_module, shortest_path_module),
    note=(
        "the same routine on a dense graph; the near identical time is the "
        "point, because the cost does not depend on the edge count"
    ),
)
def floyd_warshall_dense(graph: Any) -> Any:
    """All pairs shortest paths by Floyd Warshall on a dense graph."""
    return shortest_path_module.floyd_warshall(graph)


@benchmark(
    group=GROUP_SHORTEST_PATH,
    sizes=[60, 120, 240],
    complexity="O(V E log V)",
    setup=make_sparse_graph,
    requires=requires_all(graphs_module, shortest_path_module),
    note="all pairs on a sparse graph, where it should beat Floyd Warshall",
)
def johnson_sparse(graph: Any) -> Any:
    """All pairs shortest paths by Johnson on a sparse graph."""
    return shortest_path_module.johnson(graph)


@benchmark(
    group=GROUP_SHORTEST_PATH,
    sizes=[1_000, 10_000, 100_000],
    complexity="O(length of the path)",
    setup=make_sparse_graph,
    requires=requires_all(graphs_module, shortest_path_module),
    note="reading a path out of a predecessor map, which should be trivial",
)
def reconstruct_path(graph: Any) -> List[Any]:
    """Reconstruct one shortest path from a predecessor map."""
    vertices = graph.vertices()
    _, predecessors = shortest_path_module.dijkstra(graph, vertices[0])
    return shortest_path_module.reconstruct_path(predecessors, vertices[-1])


@benchmark(
    group=GROUP_SHORTEST_PATH,
    sizes=[200, 500, 1_000],
    complexity="O(k V (E + V log V))",
    setup=make_sparse_graph,
    requires=requires_all(graphs_module, shortest_path_module),
)
def k_shortest_paths(graph: Any) -> Any:
    """Find the five shortest paths between two vertices."""
    vertices = graph.vertices()
    return shortest_path_module.k_shortest(graph, vertices[0], vertices[-1], 5)


# ---------------------------------------------------------------------------
# Spanning trees
# ---------------------------------------------------------------------------


@benchmark(
    group=GROUP_SPANNING,
    sizes=[1_000, 10_000, 100_000],
    complexity="O(E log E), dominated by the sort",
    setup=make_sparse_graph,
    requires=requires_all(graphs_module, spanning_module),
)
def kruskal_sparse(graph: Any) -> Any:
    """Minimum spanning tree by Kruskal on a sparse graph."""
    return spanning_module.kruskal(graph)


@benchmark(
    group=GROUP_SPANNING,
    sizes=[1_000, 10_000, 100_000],
    complexity="O((V + E) log V)",
    setup=make_sparse_graph,
    requires=requires_all(graphs_module, spanning_module),
)
def prim_sparse(graph: Any) -> Any:
    """Minimum spanning tree by Prim on a sparse graph."""
    return spanning_module.prim(graph)


@benchmark(
    group=GROUP_SPANNING,
    sizes=[1_000, 10_000, 100_000],
    complexity="O(E log V)",
    setup=make_sparse_graph,
    requires=requires_all(graphs_module, spanning_module),
    note="contracts every component per round, which parallelizes naturally",
)
def boruvka_sparse(graph: Any) -> Any:
    """Minimum spanning tree by Boruvka on a sparse graph."""
    return spanning_module.boruvka(graph)


@benchmark(
    group=GROUP_SPANNING,
    sizes=[100, 300, 600],
    complexity="O(E log E)",
    setup=make_dense_graph,
    requires=requires_all(graphs_module, spanning_module),
    note="on a dense graph the sort dominates, which favours Prim",
)
def kruskal_dense(graph: Any) -> Any:
    """Minimum spanning tree by Kruskal on a dense graph."""
    return spanning_module.kruskal(graph)


@benchmark(
    group=GROUP_SPANNING,
    sizes=[100, 300, 600],
    complexity="O((V + E) log V)",
    setup=make_dense_graph,
    requires=requires_all(graphs_module, spanning_module),
)
def prim_dense(graph: Any) -> Any:
    """Minimum spanning tree by Prim on a dense graph."""
    return spanning_module.prim(graph)


@benchmark(
    group=GROUP_SPANNING,
    sizes=[20, 40, 80],
    complexity="O(V cubed) through the matrix tree theorem",
    setup=make_sparse_graph,
    requires=requires_all(graphs_module, spanning_module),
    note=(
        "counting the spanning trees without enumerating them, by a cofactor "
        "of the Laplacian, computed exactly"
    ),
)
def spanning_tree_count(graph: Any) -> int:
    """Count the spanning trees of a graph exactly."""
    return spanning_module.spanning_tree_count(graph)


# ---------------------------------------------------------------------------
# Flow and matching
# ---------------------------------------------------------------------------


@benchmark(
    group=GROUP_FLOW,
    sizes=[50, 200, 800],
    complexity="O(V E squared)",
    setup=make_flow_network,
    requires=requires_all(graphs_module, flow_module),
    note="shortest augmenting paths, which bounds the round count",
)
def edmonds_karp(network: Any) -> Any:
    """Maximum flow by Edmonds Karp."""
    return flow_module.edmonds_karp(network, "source", "sink")


@benchmark(
    group=GROUP_FLOW,
    sizes=[50, 200, 800],
    complexity="O(V squared E)",
    setup=make_flow_network,
    requires=requires_all(graphs_module, flow_module),
    note="blocking flows on level graphs, which suits a layered network",
)
def dinic(network: Any) -> Any:
    """Maximum flow by Dinic."""
    return flow_module.dinic(network, "source", "sink")


@benchmark(
    group=GROUP_FLOW,
    sizes=[50, 200],
    complexity="O(E times the flow value)",
    setup=make_flow_network,
    requires=requires_all(graphs_module, flow_module),
    note=(
        "the cost depends on the flow value rather than only on the size, "
        "which is why the reference warns against it for large capacities"
    ),
)
def ford_fulkerson(network: Any) -> Any:
    """Maximum flow by Ford Fulkerson."""
    return flow_module.ford_fulkerson(network, "source", "sink")


@benchmark(
    group=GROUP_FLOW,
    sizes=[50, 200, 800],
    complexity="O(V cubed)",
    setup=make_flow_network,
    requires=requires_all(graphs_module, flow_module),
)
def push_relabel(network: Any) -> Any:
    """Maximum flow by preflow push with relabelling."""
    return flow_module.push_relabel(network, "source", "sink")


@benchmark(
    group=GROUP_FLOW,
    sizes=[50, 200, 800],
    complexity="as the underlying flow routine",
    setup=make_flow_network,
    requires=requires_all(graphs_module, flow_module),
    note="the cut whose capacity equals the flow value, which is the theorem",
)
def max_flow_min_cut(network: Any) -> Any:
    """Maximum flow together with a minimum cut."""
    return flow_module.max_flow_min_cut(network, "source", "sink")


@benchmark(
    group=GROUP_FLOW,
    sizes=[200, 1_000, 5_000],
    complexity="O(E times the square root of V)",
    setup=make_bipartite_graph,
    requires=requires_all(graphs_module, flow_module),
    note="the specialized algorithm, asymptotically better than a flow run",
)
def hopcroft_karp(graph: Any) -> Any:
    """Maximum bipartite matching by Hopcroft Karp."""
    return flow_module.hopcroft_karp(graph)


@benchmark(
    group=GROUP_FLOW,
    sizes=[200, 1_000],
    complexity="O(V E)",
    setup=make_bipartite_graph,
    requires=requires_all(graphs_module, flow_module),
    note="the augmenting path matching, for comparison with Hopcroft Karp",
)
def bipartite_matching(graph: Any) -> Any:
    """Maximum bipartite matching by augmenting paths."""
    return flow_module.bipartite_matching(graph)


@benchmark(
    group=GROUP_FLOW,
    sizes=[20, 40, 80],
    complexity="O(n cubed)",
    requires=flow_module,
    note="optimal assignment by the Hungarian method, on a cost matrix",
)
def hungarian(size: int) -> Any:
    """Solve an optimal assignment problem."""
    source = seeded(f"graphs.hungarian.{size}")
    matrix = [[source.randint(1, 100) for _ in range(size)] for _ in range(size)]
    return flow_module.hungarian(matrix)


@benchmark(
    group=GROUP_FLOW,
    sizes=[40, 80, 160],
    complexity="O(V E + V squared log V)",
    setup=make_sparse_graph,
    requires=requires_all(graphs_module, flow_module),
    note="the global minimum cut, without a designated source and sink",
)
def stoer_wagner(graph: Any) -> Any:
    """Global minimum cut by Stoer Wagner."""
    return flow_module.stoer_wagner(graph)


# ---------------------------------------------------------------------------
# Colouring
# ---------------------------------------------------------------------------


@benchmark(
    group=GROUP_COLORING,
    sizes=[1_000, 10_000, 100_000],
    complexity="O(V + E)",
    setup=make_sparse_graph,
    requires=requires_all(graphs_module, coloring_module),
)
def greedy_coloring(graph: Any) -> Any:
    """Colour a graph greedily in vertex order."""
    return coloring_module.greedy_coloring(graph)


@benchmark(
    group=GROUP_COLORING,
    sizes=[1_000, 10_000, 100_000],
    complexity="O(V log V + E)",
    setup=make_sparse_graph,
    requires=requires_all(graphs_module, coloring_module),
    note="greedy in decreasing degree order, usually with fewer colours",
)
def welsh_powell(graph: Any) -> Any:
    """Colour a graph by the Welsh Powell ordering."""
    return coloring_module.welsh_powell(graph)


@benchmark(
    group=GROUP_COLORING,
    sizes=[1_000, 10_000, 100_000],
    complexity="O((V + E) log V)",
    setup=make_sparse_graph,
    requires=requires_all(graphs_module, coloring_module),
    note="saturation degree ordering, the best of the polynomial heuristics",
)
def dsatur(graph: Any) -> Any:
    """Colour a graph by the saturation degree heuristic."""
    return coloring_module.dsatur(graph)


@benchmark(
    group=GROUP_COLORING,
    sizes=[12, 16, 20],
    complexity="exponential, because the problem is NP hard",
    setup=make_small_graph,
    requires=requires_all(graphs_module, coloring_module),
    note=(
        "the exact chromatic number; compare the sizes here with the "
        "heuristics above, which run on graphs five thousand times larger"
    ),
)
def chromatic_number(graph: Any) -> int:
    """Compute the exact chromatic number of a small graph."""
    return coloring_module.chromatic_number(graph)


@benchmark(
    group=GROUP_COLORING,
    sizes=[8, 10, 12],
    complexity="exponential, by deletion and contraction",
    setup=make_small_graph,
    requires=requires_all(graphs_module, coloring_module),
    note="counting the colourings is harder than finding one",
)
def chromatic_polynomial(graph: Any) -> Any:
    """Compute the chromatic polynomial of a very small graph."""
    return coloring_module.chromatic_polynomial(graph)


@benchmark(
    group=GROUP_COLORING,
    sizes=[1_000, 10_000, 100_000],
    complexity="O(V + E)",
    setup=make_sparse_graph,
    requires=requires_all(graphs_module, coloring_module),
    note="two colourability, which is linear and answers the question exactly",
)
def bipartite_test(graph: Any) -> bool:
    """Decide whether a graph is bipartite."""
    return coloring_module.is_bipartite(graph)


# ---------------------------------------------------------------------------
# Paths and tours
# ---------------------------------------------------------------------------


@benchmark(
    group=GROUP_PATHS,
    sizes=[1_000, 10_000, 100_000],
    complexity="O(V + E), decided by the degrees",
    setup=make_sparse_graph,
    requires=requires_all(graphs_module, paths_module),
    note=(
        "the Eulerian question is linear; compare with the Hamiltonian one "
        "below, which looks similar and is NP complete"
    ),
)
def eulerian_test(graph: Any) -> bool:
    """Decide whether a graph has an Eulerian circuit."""
    return paths_module.has_eulerian_circuit(graph)


@benchmark(
    group=GROUP_PATHS,
    sizes=[12, 16, 20],
    complexity="exponential, because the problem is NP complete",
    setup=make_small_graph,
    requires=requires_all(graphs_module, paths_module),
)
def hamiltonian_test(graph: Any) -> bool:
    """Decide whether a small graph has a Hamiltonian path."""
    return paths_module.has_hamiltonian_path(graph)


@benchmark(
    group=GROUP_PATHS,
    sizes=[10, 12, 14],
    complexity="O(V squared times 2 to the V), by Held and Karp",
    setup=make_small_graph,
    requires=requires_all(graphs_module, paths_module),
)
def tsp_exact(graph: Any) -> Any:
    """Find an optimal tour of a very small graph."""
    return paths_module.tsp_exact(graph)


@benchmark(
    group=GROUP_PATHS,
    sizes=[100, 400, 1_600],
    complexity="O(V squared)",
    setup=make_sparse_graph,
    requires=requires_all(graphs_module, paths_module),
    note="the heuristic tour, polynomial and without an optimality guarantee",
)
def tsp_heuristic(graph: Any) -> Any:
    """Find a heuristic tour of a graph."""
    return paths_module.tsp_heuristic(graph, method="nearest_neighbour")


# ---------------------------------------------------------------------------
# Structural properties
# ---------------------------------------------------------------------------


@benchmark(
    group=GROUP_PROPERTIES,
    sizes=[1_000, 10_000, 100_000],
    complexity="O(V log V)",
    setup=make_sparse_graph,
    requires=requires_all(graphs_module, properties_module),
)
def degree_sequence(graph: Any) -> List[int]:
    """Compute the degree sequence of a graph."""
    return properties_module.degree_sequence(graph)


@benchmark(
    group=GROUP_PROPERTIES,
    sizes=[200, 500, 1_000],
    complexity="O(V (V + E)) by repeated traversal",
    setup=make_sparse_graph,
    requires=requires_all(graphs_module, properties_module),
)
def diameter(graph: Any) -> int:
    """Compute the diameter of a graph."""
    return properties_module.diameter(graph)


@benchmark(
    group=GROUP_PROPERTIES,
    sizes=[200, 500, 1_000],
    complexity="O(V (V + E))",
    setup=make_sparse_graph,
    requires=requires_all(graphs_module, properties_module),
)
def girth(graph: Any) -> int:
    """Compute the length of a shortest cycle."""
    return properties_module.girth(graph)


@benchmark(
    group=GROUP_PROPERTIES,
    sizes=[14, 18, 22],
    complexity="exponential, NP hard",
    setup=make_small_graph,
    requires=requires_all(graphs_module, properties_module),
)
def max_clique(graph: Any) -> Any:
    """Find a maximum clique of a small graph."""
    return properties_module.max_clique(graph)


@benchmark(
    group=GROUP_PROPERTIES,
    sizes=[14, 18, 22],
    complexity="exponential, NP hard",
    setup=make_small_graph,
    requires=requires_all(graphs_module, properties_module),
    note="the complement problem of the clique, and equally hard",
)
def max_independent_set(graph: Any) -> Any:
    """Find a maximum independent set of a small graph."""
    return properties_module.max_independent_set(graph)


@benchmark(
    group=GROUP_PROPERTIES,
    sizes=[200, 500, 1_000],
    complexity="O(V + E)",
    setup=make_sparse_graph,
    requires=requires_all(graphs_module, properties_module),
)
def planarity_test(graph: Any) -> bool:
    """Decide whether a graph is planar."""
    return properties_module.is_planar(graph)


@benchmark(
    group=GROUP_PROPERTIES,
    sizes=[20, 40, 80],
    complexity="exponential in the worst case",
    setup=make_small_graph,
    requires=requires_all(graphs_module, properties_module),
    note="isomorphism against a copy of the same graph, the worst case",
)
def isomorphism(graph: Any) -> bool:
    """Decide whether a graph is isomorphic to a copy of itself."""
    return properties_module.is_isomorphic(graph, graph)


# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------


@benchmark(
    group=GROUP_ANALYSIS,
    sizes=[1_000, 10_000, 100_000],
    complexity="O(V + E)",
    setup=make_sparse_graph,
    requires=requires_all(graphs_module, algorithms_module),
)
def degree_centrality(graph: Any) -> Any:
    """Compute the degree centrality of every vertex."""
    return algorithms_module.degree_centrality(graph)


@benchmark(
    group=GROUP_ANALYSIS,
    sizes=[200, 500, 1_000],
    complexity="O(V (V + E))",
    setup=make_sparse_graph,
    requires=requires_all(graphs_module, algorithms_module),
)
def closeness_centrality(graph: Any) -> Any:
    """Compute the closeness centrality of every vertex."""
    return algorithms_module.closeness_centrality(graph)


@benchmark(
    group=GROUP_ANALYSIS,
    sizes=[200, 500, 1_000],
    complexity="O(V E) by Brandes",
    setup=make_sparse_graph,
    requires=requires_all(graphs_module, algorithms_module),
    note=(
        "Brandes' algorithm rather than the cubic cost of the definition, "
        "which is the improvement the reference claims"
    ),
)
def betweenness_centrality(graph: Any) -> Any:
    """Compute the betweenness centrality of every vertex."""
    return algorithms_module.betweenness_centrality(graph)


@benchmark(
    group=GROUP_ANALYSIS,
    sizes=[1_000, 10_000, 100_000],
    complexity="O(iterations times (V + E))",
    setup=make_sparse_digraph,
    requires=requires_all(graphs_module, algorithms_module),
)
def pagerank(graph: Any) -> Any:
    """Compute the stationary distribution of the random surfer."""
    return algorithms_module.pagerank(graph, damping=0.85)


@benchmark(
    group=GROUP_ANALYSIS,
    sizes=[40, 80, 160],
    complexity="O(V cubed) exact spectral computation",
    setup=make_sparse_graph,
    requires=requires_all(graphs_module, algorithms_module),
    note="exact where the characteristic polynomial factors over the rationals",
)
def spectral_properties(graph: Any) -> Any:
    """Compute the spectrum of the adjacency and Laplacian matrices."""
    return algorithms_module.spectral_properties(graph)


@benchmark(
    group=GROUP_ANALYSIS,
    sizes=[1_000, 10_000],
    complexity="O(V + E) per pass",
    setup=make_sparse_graph,
    requires=requires_all(graphs_module, algorithms_module),
)
def louvain(graph: Any) -> Any:
    """Detect communities by modularity optimization."""
    return algorithms_module.louvain(graph, seed=20260115)


# ---------------------------------------------------------------------------
# Generators
# ---------------------------------------------------------------------------


@benchmark(
    group=GROUP_STRUCTURES,
    sizes=[100, 300, 900],
    complexity="O(V squared)",
    requires=requires_all(graphs_module, generators_module),
)
def complete_graph(vertices: int) -> Any:
    """Generate a complete graph."""
    return generators_module.complete_graph(vertices)


@benchmark(
    group=GROUP_STRUCTURES,
    sizes=[1_000, 10_000, 100_000],
    complexity="O(V squared) for the edge trials",
    requires=requires_all(graphs_module, generators_module),
    note="seeded, so two runs produce the identical graph",
)
def random_gnp(vertices: int) -> Any:
    """Generate a random graph with independent edge probabilities."""
    return generators_module.random_gnp(vertices, 4.0 / vertices, seed=20260115)


@benchmark(
    group=GROUP_STRUCTURES,
    sizes=[1_000, 10_000, 100_000],
    complexity="O(V + E)",
    requires=requires_all(graphs_module, generators_module),
)
def barabasi_albert(vertices: int) -> Any:
    """Generate a preferential attachment graph."""
    return generators_module.barabasi_albert(vertices, 3, seed=20260115)


# ---------------------------------------------------------------------------
# Notes on reading these results
# ---------------------------------------------------------------------------
#
# The comparisons this file exists for:
#
#   dijkstra_sparse against bellman_ford_sparse. Both return the same
#   distances on these graphs, so the ratio is the whole of the reason to
#   prefer one. Bellman Ford should pull away sharply as the size grows,
#   because its cost is the product of the vertex and edge counts.
#
#   bellman_ford_sparse against spfa. The same algorithm with a queue, which
#   should be far faster in practice while sharing the worst case bound.
#
#   dijkstra_sparse against bfs_shortest. On an unweighted question the
#   linear routine should beat the logarithmic one, which is why the
#   reference tells a reader to use it.
#
#   floyd_warshall_sparse against floyd_warshall_dense. These should be
#   nearly identical, because the cost is cubic in the vertex count and does
#   not depend on the edge count. A gap means the implementation iterates
#   edges somewhere it should iterate cells.
#
#   floyd_warshall_sparse against johnson_sparse. Johnson should win on a
#   sparse graph, which is the recommendation the reference makes.
#
#   kruskal_sparse against prim_sparse against boruvka_sparse, and then
#   kruskal_dense against prim_dense. All three return the same total
#   weight, and their relative cost depends on the density, which is the
#   only reason to ship three.
#
#   edmonds_karp against dinic against push_relabel on the same network.
#   Same value, different bounds. Dinic should do well on this layered
#   family, which is what it was designed for.
#
#   hopcroft_karp against bipartite_matching. The square root factor is the
#   difference, and it should be visible by the largest size.
#
#   dsatur against chromatic_number. The starkest contrast in the library: a
#   heuristic on a graph of a hundred thousand vertices against an exact
#   routine on a graph of twenty. Both are correct answers to different
#   questions, and the reference says which question each answers.
#
#   eulerian_test against hamiltonian_test. Two questions that look alike,
#   one linear and one NP complete, measured side by side. This is the pair
#   worth showing anybody who asks why complexity classes matter.
