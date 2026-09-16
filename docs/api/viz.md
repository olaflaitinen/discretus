# `discretus.viz`

The visualization package renders discrete objects through pluggable
backends. It draws graphs with several layouts, Hasse diagrams, lattices,
trees, truth tables, Karnaugh maps, matrices, and Venn diagrams, and it
emits LaTeX and DOT for objects that will be typeset or laid out elsewhere.

Rendering is strictly optional. Two backends need nothing beyond the
standard library, so a textual or vector rendering is always available, and
the two that need a plotting stack live behind the `viz` extra. The core
library never imports a rendering dependency, and a missing backend produces
an actionable error rather than an import failure at startup.

## What this package is for

A discrete structure is often easier to check by looking at it than by
reading a repr. A Hasse diagram shows immediately whether a poset is a
lattice; a drawn graph shows immediately whether a colouring is proper; a
Karnaugh map shows immediately why a minimization grouped the terms it did.
The package exists so that the picture is one call away from the object, and
so that the same object can produce a terminal sketch while developing and a
publication figure for a paper.

There is a second purpose, which is teaching. A rendering that a student can
produce from their own computation is a much stronger learning aid than one
supplied in a textbook, because it responds to their input.

## Backends

| Backend | Dependency | Output | Use |
| --- | --- | --- | --- |
| `ascii` | None | Text | Terminals, docstrings, log files, tests |
| `svg` | None | SVG markup | Web pages, documents, version control |
| `graphviz` | `graphviz` package and the system binaries | Any Graphviz format | Publication quality layout |
| `matplotlib` | `matplotlib` | Raster and vector images | Figures alongside other plots |

Backends register themselves in the central registry, so the available set
can be inspected at runtime and a caller can choose deliberately.

```python
>>> from discretus.registry import VIZ_BACKENDS
>>> "ascii" in VIZ_BACKENDS, "svg" in VIZ_BACKENDS
(True, True)
```

The configured preference decides what `auto` means. The default resolves in
the order graphviz, matplotlib, svg, ascii, so a machine with the full stack
produces the best available rendering and a machine without it still
produces something useful.

```python
from discretus.config import set_config

set_config(viz_backend="svg")      # or "ascii", "graphviz", "matplotlib", "auto"
```

Requesting a backend whose dependency is absent raises
`OptionalDependencyError`, and the message contains the command to install
it. That is deliberate: a silent fallback to a different backend would
produce a figure that is not the one the caller asked for, which is worse in
a paper than an error.

## Drawing graphs

### `graph_draw.draw(graph, layout=None, backend=None, **options)`

The single entry point for drawing a graph. The layout decides where the
vertices go and the backend decides how they are painted, which keeps the
two concerns separable: the same layout can be rendered by any backend, and
the same backend can render any layout.

| Option | Meaning |
| --- | --- |
| `layout` | A layout name or a mapping from vertex to position |
| `backend` | A backend name, or `None` for the configured preference |
| `labels` | Whether to draw vertex labels, or a mapping of labels |
| `edge_labels` | Whether to draw weights, or a mapping |
| `colors` | A mapping from vertex to colour, for instance a colouring |
| `highlight` | Vertices or edges to emphasize, for instance a path |
| `directed` | Override the arrow drawing |
| `size` | The canvas size, in the backend's units |
| `seed` | The seed for a layout that uses randomness |

```python
from discretus.graphs import Graph
from discretus.graphs.coloring import dsatur
from discretus.graphs.shortest_path import dijkstra, reconstruct_path
from discretus.viz import graph_draw

g = Graph()
g.add_edges_from([("A", "B", 4), ("A", "C", 1), ("C", "B", 2), ("B", "D", 5)])

# A terminal sketch, with the weights shown.
print(graph_draw.draw(g, backend="ascii", edge_labels=True))

# The same graph, coloured by a colouring the graph package computed.
svg = graph_draw.draw(g, backend="svg", colors=dsatur(g))

# The same graph, with a shortest path emphasized.
_, predecessors = dijkstra(g, "A")
path = reconstruct_path(predecessors, "D")
highlighted = graph_draw.draw(g, backend="svg", highlight=path)
```

The third example is the pattern that makes this package worth having: the
result of an algorithm is passed straight into the drawing as data. A
colouring is a mapping from vertex to colour and so is the `colors` option;
a path is a list of vertices and so is the `highlight` option. Nothing has
to be reformatted.

### Layouts

| Layout | Placement | Suitable for |
| --- | --- | --- |
| `circular_layout` | Vertices evenly on a circle | Small graphs, Cayley graphs, cycles |
| `spring_layout` | Force directed with a spring model | General graphs up to a few hundred vertices |
| `force_directed` | The same family, with configurable forces | Tuning a difficult layout |
| `graph_layout.layered` | By rank, for a directed acyclic graph | Dependency graphs, Hasse diagrams |
| `graph_layout.bipartite` | Two columns | Bipartite graphs and matchings |
| `graph_layout.grid` | On a lattice | Grid graphs, meshes |
| `graph_layout.tree` | Rooted, children below parents | Trees and forests |

Every layout returns a mapping from vertex to coordinates, which is plain
data. It can be inspected, adjusted, stored, and reused, so a figure that
appears twice in a document can use identical positions rather than two
independent layouts that a reader would have to re learn.

The randomized layouts take a seed and are deterministic once given one,
which matters for a figure in a paper: the same input must produce the same
picture when the document is rebuilt.

```python
from discretus.viz import circular_layout, spring_layout

positions = spring_layout.compute(g, seed=7, iterations=200)
same = spring_layout.compute(g, seed=7, iterations=200)
assert positions == same
```

## Drawing order theoretic objects

### `hasse_draw.draw(order, backend=None, **options)`

Draw the Hasse diagram of a partial order, with the layout computed from the
rank function so that every cover edge points upward and no edge is drawn
that transitivity implies.

```python
from discretus.sets.orders import PartialOrder
from discretus.viz import hasse_draw

divides = PartialOrder.from_relation(
    ground={1, 2, 3, 4, 6, 12},
    leq=lambda x, y: y % x == 0,
)
print(hasse_draw.draw(divides, backend="ascii"))
```

The diagram is the fastest way to see the structure of a small poset. Whether
it is a lattice, where its atoms are, how tall it is, and which elements are
incomparable are all visible at a glance and each takes a separate call to
establish otherwise.

### `lattice_draw.draw(lattice, backend=None, **options)`

The same for a lattice, with the meet and join of a selected pair
highlightable, which is the drawing that explains what the two operations
do.

## Drawing logic

### `truth_table_draw.draw(table, backend=None, **options)`

Render a truth table. The text backend produces an aligned table, the SVG
backend produces a grid, and the LaTeX renderer produces a tabular
environment for a handout. Rows can be filtered to the models or the
countermodels, which is how a counterexample is presented.

### `karnaugh_draw.draw(formula, backend=None, **options)`

Render a Karnaugh map for up to four variables, with the groupings that the
minimization chose drawn over it. This is the one rendering in the package
that explains an algorithm rather than an object: the groups are the prime
implicants, and seeing them is the point of the map.

```python
from discretus.logic.propositional import parse, truth_table
from discretus.viz import karnaugh_draw, truth_table_draw

formula = parse("(p & ~q) | (p & q) | (~p & q & r)")
print(truth_table_draw.draw(truth_table(formula), backend="ascii"))
print(karnaugh_draw.draw(formula, backend="ascii", show_groups=True))
```

## Drawing other structures

| Routine | Draws |
| --- | --- |
| `tree_draw.draw(tree)` | A rooted tree, with depth downward |
| `matrix_heatmap.draw(matrix)` | A matrix, with magnitude as intensity |
| `venn.draw(sets)` | A Venn diagram for two or three sets |
| `dot_export.to_dot(graph)` | DOT source, for external layout |
| `latex_render.to_latex(obj)` | A LaTeX fragment for any renderable object |

The matrix heat map is useful for the objects that are matrices without
looking like them: an adjacency matrix shows the block structure of a graph's
components, a reachability matrix shows the partial order of the strong
components, and a Laplacian shows the degree distribution on its diagonal.

The Venn diagram is limited to three sets on purpose. A Venn diagram of four
or more sets cannot be drawn with circles, and the shapes that do work are
harder to read than the set expressions they illustrate, so the package
declines rather than producing something misleading.

## Colours

### `color_palette`

| Routine | Meaning |
| --- | --- |
| `palette(name)` | A named palette, as a list of colour values |
| `for_coloring(coloring)` | A colour per colour class of a graph colouring |
| `sequential(count)` | A sequential ramp for ordered data |
| `qualitative(count)` | A qualitative set for unordered categories |
| `colorblind_safe(count)` | A set chosen for deuteranopia and protanopia |

The defaults are the colourblind safe ones, because a figure in a paper is
read by people who did not choose the palette. The palettes are plain data,
so a caller with a house style passes their own list.

## Rendering without a backend

Two capabilities need no dependency at all and are worth knowing about
because they cover most uses.

**ASCII rendering** produces text, which goes into a terminal, a docstring,
a log file, or an assertion in a test. Because it is text, it is
deterministic and diffable, and the library uses it in its own doctests: the
Cayley table and the Hasse diagram examples in the reference are produced by
this backend, which is why they can be checked by the documentation build.

**SVG rendering** produces markup, which goes into a web page, an HTML
report, or a document. SVG is text as well, so a figure under version
control produces a readable diff when the underlying object changes, which
is not true of a raster image.

```python
from discretus.viz import ascii_render, svg_backend

print(ascii_render.draw(g))
svg = svg_backend.draw(g)
open("graph.svg", "w", encoding="utf-8").write(svg)
```

## Rich display in notebooks

Every renderable object implements the display hooks that notebooks use, so
the value of the last expression in a cell appears as a figure or as typeset
mathematics rather than as a repr. The mechanism is the LaTeX mixin and the
SVG backend from `discretus.core`, so it works without the plotting extras.

There is nothing to configure: displaying a truth table, a matrix, a
polynomial, a Hasse diagram, or a graph in a notebook cell just works, and
`to_latex` or the backend call is there for the case where the output needs
to be captured rather than displayed.

## Worked example: a figure for a paper

The following produces a publication figure from a computation, and it
illustrates every decision the package asks a caller to make: which layout,
which backend, which colours, and what to emphasize.

The subject is a small scheduling problem. Five tasks conflict pairwise when
they need the same resource, so a valid schedule is a proper colouring of
the conflict graph, and the number of time slots needed is its chromatic
number.

```python
from discretus.graphs import Graph
from discretus.graphs.coloring import chromatic_number, dsatur
from discretus.viz import color_palette, graph_draw, spring_layout

conflicts = Graph()
conflicts.add_edges_from([
    ("setup", "measure"),
    ("setup", "calibrate"),
    ("measure", "calibrate"),
    ("measure", "analyse"),
    ("calibrate", "report"),
    ("analyse", "report"),
])

slots = chromatic_number(conflicts)
schedule = dsatur(conflicts)
print(slots, schedule)

# One layout, computed once and reused, so that every figure in the
# document places the tasks identically.
positions = spring_layout.compute(conflicts, seed=20260115, iterations=400)

figure = graph_draw.draw(
    conflicts,
    layout=positions,
    backend="svg",
    labels=True,
    colors=color_palette.for_coloring(schedule),
    size=(600, 400),
)
open("conflicts.svg", "w", encoding="utf-8").write(figure)
```

Four things in that program are the point.

The colouring came from the graph package and went into the drawing without
being reformatted, because a colouring is a mapping from vertex to colour
class and `for_coloring` turns colour classes into colours.

The layout was computed once and passed in, rather than being recomputed by
the drawing call. That is what makes a second figure of the same graph, for
instance one with a different emphasis, place the vertices in the same
places, which a reader needs in order to compare the two.

The seed is explicit, so rebuilding the document a year later produces the
identical figure. A layout without a seed would move the vertices on every
build, which produces a meaningless diff in version control and a figure
that no longer matches the caption.

The output is SVG, which is text. It goes into version control as a readable
diff, it scales without loss in print, and it needed no dependency beyond
the library.

For a figure that will sit next to other plots, the matplotlib backend takes
the same arguments and returns a figure object, which can then be given axes
labels, a title, and a size that matches the rest of the document.

```python
figure = graph_draw.draw(
    conflicts,
    layout=positions,
    backend="matplotlib",
    colors=color_palette.for_coloring(schedule),
)
figure.savefig("conflicts.pdf", bbox_inches="tight", dpi=300)
```

And for a figure that needs professional layout of a directed acyclic
structure, the Graphviz backend delegates the placement to the layout engine
that was built for it, which handles a hierarchy far better than a force
directed layout can.

```python
from discretus.viz import dot_export

print(dot_export.to_dot(conflicts))          # the source, for inspection
```

Emitting DOT rather than rendering it is worth remembering: it lets the
figure be laid out by an external toolchain, checked into version control as
source, and rebuilt by a document pipeline that never imports Python at all.

The same three level choice applies to every drawing in the package. Use
ASCII while developing, because it is instant and needs nothing. Use SVG or
DOT for a document, because they are text. Use matplotlib when the figure
belongs in a family of plots.

## Errors

| Exception | Raised when |
| --- | --- |
| `OptionalDependencyError` | A backend's dependency is missing, with the install command |
| `BackendError` | A backend failed, for instance the Graphviz binary is absent or returned an error |
| `ValidationError` | An unknown layout or backend name, or a malformed position mapping |
| `DomainError` | A Venn diagram of more than three sets, or a Karnaugh map of more than four variables |
| `LimitExceededError` | A drawing whose vertex or cell count exceeds the configured limit |

The enumeration limit applies here too, and for a good reason: a request to
draw a graph with a hundred thousand vertices will produce a figure that
cannot be read and will take a long time doing it. The limit turns that into
an immediate error with a suggestion to draw a subgraph instead.

## Complexity summary

| Operation | Complexity |
| --- | --- |
| Circular layout | O(V) |
| Spring layout | O(iterations times V squared) |
| Layered layout | O(V + E) |
| Tree layout | O(V) |
| Hasse layout | O(V cubed), dominated by the cover relation |
| ASCII graph rendering | O(V + E) |
| SVG rendering | O(V + E) |
| Truth table rendering | O(rows times variables) |
| Karnaugh map rendering | O(2 to the v) |

The spring layout is the expensive one, and it is quadratic per iteration
because every pair of vertices repels every other. For a graph beyond a few
hundred vertices, prefer a layout with structure, namely layered for a
directed acyclic graph, bipartite for a bipartite graph, or grid for a
lattice, or draw a subgraph.

## Design notes

**Layout and rendering are separate.** A layout is a mapping from vertex to
position and a renderer turns positions into output. Keeping them apart is
what lets the same picture be produced in four formats, lets a caller adjust
a position by hand, and lets a figure be reproduced exactly in a rebuild.

**Backends are registered, not imported.** The package registers backends in
`discretus.registry`, and a backend imports its dependency inside the
function that needs it. That is what keeps the core free of a plotting stack
and what makes the available set inspectable at runtime.

**A missing backend is an error, not a downgrade.** Falling back silently
would produce a different figure than the one requested. The error names the
extra to install.

**Algorithm output is drawing input.** A colouring, a path, a matching, a
spanning tree, and a flow are all plain data in the shape the drawing
options accept. No adapter is needed between computing something and showing
it, which is the whole reason for having the visualization inside the same
library rather than beside it.

**Text output is a first class format.** ASCII and SVG are not fallbacks.
They are deterministic and diffable, they work in a terminal and in a
document, and they are what the library's own documentation and tests use.

## Testing a rendering

A figure is output, and output can be tested. The package is designed so
that a test of a rendering is neither a screenshot comparison nor a leap of
faith.

For the text backend, assert the string. It is deterministic, so the
assertion is exact, and a failure prints a readable diff.

```python
from discretus.sets.orders import PartialOrder
from discretus.viz import hasse_draw

order = PartialOrder.from_relation({1, 2, 4}, lambda x, y: y % x == 0)
drawing = hasse_draw.draw(order, backend="ascii")
assert "4" in drawing.splitlines()[0]        # the maximum is on top
```

For the SVG backend, assert the structure rather than the bytes. The markup
contains one element per vertex and one per edge, so the counts are
checkable without depending on the exact coordinates.

```python
from discretus.graphs.generators import cycle_graph
from discretus.viz import svg_backend

markup = svg_backend.draw(cycle_graph(5))
assert markup.count("<circle") == 5
assert markup.count("<line") == 5
```

For a layout, assert the invariant rather than the positions. A layered
layout must place every edge's target below its source; a bipartite layout
must place the two parts in two columns; a tree layout must place a child
below its parent. Those are the properties the layout promises, and they are
what a test should pin.

```python
from discretus.graphs import DiGraph
from discretus.viz import graph_layout

dag = DiGraph()
dag.add_edges_from([("a", "b"), ("b", "c"), ("a", "c")])
positions = graph_layout.layered(dag)
for source, target in dag.edges():
    assert positions[source][1] < positions[target][1]
```

For the optional backends, skip rather than fail when the dependency is
absent, which the `optional` marker in the test configuration exists for.
The library's own suite is arranged that way, so a contributor who installed
without the extras still gets a green run.

```python
import pytest

matplotlib = pytest.importorskip("matplotlib")


@pytest.mark.optional
def test_matplotlib_backend_returns_a_figure():
    from discretus.graphs.generators import path_graph
    from discretus.viz import graph_draw

    figure = graph_draw.draw(path_graph(4), backend="matplotlib")
    assert figure is not None
```

## See also

- [`discretus.graphs`](graphs.md), whose layouts and colourings this package
  renders.
- [`discretus.sets`](sets.md), for the Hasse layout, which is computed there
  because it is order theory rather than rendering.
- [`discretus.logic`](logic.md), for the truth tables and Karnaugh maps.
- [`discretus.io`](io.md), for DOT, GraphML, and LaTeX export, which are
  interchange rather than drawing.
- [`discretus.core`](core.md), for the LaTeX mixin and the rich display
  hooks.
