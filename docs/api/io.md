# `discretus.io`

The input and output package reads and writes the interchange formats that
let a discretus object travel to another tool and back. It covers the graph
formats GraphML, GML, DOT, edge lists, adjacency data, and CSV, the
satisfiability format DIMACS, the general formats JSON and pickle, and LaTeX
export for anything that will be typeset.

Two properties hold for every writer in this package, and they are the
reason it exists rather than each domain writing its own files.

**Determinism.** The same object always produces byte identical output.
Vertices, edges, and attributes are emitted in the universal total order
from `discretus.core.comparators` rather than in iteration order, so a
written file can be committed to version control and a change in the diff
means a change in the mathematics.

**Round tripping.** Reading what a writer produced reconstructs an equal
object, for every format that can express the object. Where a format cannot
express something, for instance a parallel edge in a format for simple
graphs, the writer says so rather than silently dropping it.

## Module map

| Module | Format |
| --- | --- |
| `graphml` | GraphML, the XML based graph format |
| `gml` | GML, the Graph Modelling Language |
| `graph_io` | Format dispatch by name or by file extension |
| `edgelist_io` | Plain edge lists, one edge per line |
| `adjacency_io` | Adjacency lists and adjacency matrices |
| `csv_io` | Tabular edge and vertex tables |
| `dimacs_io` | DIMACS conjunctive normal form and graph formats |
| `json_io` | A JSON representation for any serializable object |
| `pickle_io` | Python pickle, for trusted local caching only |
| `serialization` | The dictionary protocol the other modules build on |
| `latex_export` | LaTeX fragments and standalone documents |

## The common interface

Every format module offers the same four functions, so learning one teaches
all of them.

| Function | Meaning |
| --- | --- |
| `dumps(obj, **options) -> str` | Serialize to a string |
| `loads(text, **options) -> object` | Deserialize from a string |
| `dump(obj, path, **options) -> None` | Write to a file |
| `load(path, **options) -> object` | Read from a file |

```python
from discretus.graphs import Graph
from discretus.io import graphml

g = Graph()
g.add_edges_from([("A", "B", 1), ("B", "C", 2)])

text = graphml.dumps(g)
assert graphml.loads(text) == g

graphml.dump(g, "graph.graphml")
assert graphml.load("graph.graphml") == g
```

The binary formats take and return `bytes` instead of `str`, and say so in
their signatures.

### Dispatch by extension

`graph_io` chooses the format from the file name, which is what a command
line tool or a user supplied path needs.

```python
from discretus.io import graph_io

graph_io.write(g, "graph.gml")            # chosen by extension
graph_io.write(g, "out.txt", format="edgelist")   # chosen explicitly
same = graph_io.read("graph.gml")
```

The recognized extensions are `.graphml`, `.gml`, `.dot`, `.json`, `.csv`,
`.txt` for edge lists, and `.cnf` for DIMACS. An unrecognized extension
raises rather than guessing.

## Graph formats

### GraphML

The most complete of the graph formats. It expresses directedness, weights,
vertex and edge attributes, and mixed vertex types, so a labelled weighted
digraph round trips without loss.

```python
>>> from discretus.graphs import Graph
>>> from discretus.io import graphml
>>> g = Graph()
>>> g.add_edges_from([("A", "B", 1)])
>>> print(graphml.dumps(g).splitlines()[0])
<?xml version="1.0" encoding="utf-8"?>
```

The reader accepts the subset of the specification that describes graphs and
their attributes, rejects a document whose structure it does not recognize
rather than guessing, and validates attribute types against their
declarations. It does not resolve external entities, which is deliberate:
that is the standard way an XML reader becomes a security problem.

### GML

A compact, readable, brace delimited format. It expresses the same
information as GraphML with less ceremony, and it is what several older
tools speak. The writer emits integer identifiers with the original labels
as attributes, because the format's identifiers must be integers.

### DOT

The Graphviz source format. The package writes it and does not read it: DOT
is a layout language with a large grammar, most of which has nothing to do
with the graph, and a partial reader would be a source of silent
misreadings. Writing it is exactly what is wanted for handing a graph to
Graphviz for layout.

```python
>>> from discretus.io import latex_export
>>> from discretus.graphs import Graph
>>> g = Graph(); g.add_edges_from([("A", "B", 1)])
>>> print(latex_export.to_tikz(g).splitlines()[0])
\begin{tikzpicture}
```

### Edge lists and adjacency data

The simplest formats, and the right choice for interoperating with a script
rather than with a tool. An edge list is one edge per line with an optional
weight; adjacency data is either one vertex and its neighbours per line or a
matrix.

```python
from discretus.io import adjacency_io, edgelist_io

print(edgelist_io.dumps(g))
print(adjacency_io.dumps(g, form="list"))
print(adjacency_io.dumps(g, form="matrix"))
```

The options that matter are the separator, whether weights are present,
whether a comment character is honoured, and for matrices whether the
vertex order is written as a header. All are explicit, because a format this
simple has no way to describe itself and a mismatch produces a plausible
wrong graph.

### CSV

Two tables, one of vertices with their attributes and one of edges with
theirs, which is the shape a spreadsheet or a data pipeline wants. The
writer emits a header row, and the reader requires one, so column order is
never significant.

## DIMACS

The format that satisfiability solvers speak, in both its conjunctive normal
form variant and its graph variant.

```python
>>> from discretus.logic.sat import Cnf
>>> from discretus.io import dimacs_io
>>> instance = Cnf([[1, 2], [-1, 3], [-2, -3]])
>>> print(dimacs_io.dumps(instance))
p cnf 3 3
1 2 0
-1 3 0
-2 -3 0
```

The reader tolerates the deviations that real instances contain: comment
lines, a header whose counts disagree with the body, blank lines, and
clauses split across lines. It reports a disagreement between the header and
the body as a warning rather than an error, because a competition benchmark
with a stale header is still a usable instance, and refusing it would be
unhelpful.

Reading and writing this format is what makes the logic package
interoperable. An instance too hard for the built-in solver can be handed to
a dedicated one, and a benchmark from a competition can be read directly.

## JSON

A representation for any object implementing the serialization protocol,
which covers sets, relations, orders, functions, formulas, graphs, groups,
matrices, and polynomials.

```python
from discretus.io import json_io
from discretus.sets import FiniteSet

payload = json_io.dumps(FiniteSet({3, 1, 2}))
assert json_io.loads(payload) == FiniteSet({1, 2, 3})
assert json_io.dumps(json_io.loads(payload)) == payload
```

The last assertion is the determinism property, and it is what makes JSON
the right format for a cache, a fixture, or a graded submission: the output
is stable, so it can be compared byte for byte.

Each payload carries a type tag and a schema version, so a reader can
reconstruct the right class and a future format change can be detected
rather than misread. The tag is the class name and the version is an
integer, both visible in the document rather than implied.

## Pickle

`pickle_io` exists for one purpose: caching a computed object locally
between runs of the same program. Python pickle is not safe for untrusted
input, because unpickling can execute arbitrary code, and the module
documents that at the top, in every function, and in the security policy.

Use JSON for anything that crosses a trust boundary. If you use pickle,
treat the file as code.

## LaTeX export

| Routine | Produces |
| --- | --- |
| `to_latex(obj)` | A fragment, for embedding in a sentence or an equation |
| `to_tikz(graph, **options)` | A TikZ picture of a graph or a diagram |
| `to_tabular(table)` | A tabular environment for a truth table or a Cayley table |
| `to_standalone(obj)` | A complete compilable document |

```python
from discretus.algebra.linear import Matrix
from discretus.io import latex_export
from discretus.logic.propositional import parse, truth_table

print(latex_export.to_latex(Matrix([[1, 2], [3, 4]])))
print(latex_export.to_tabular(truth_table(parse("p -> q"))))
```

The export path is what turns a computation into a figure or a table in a
document without manual reformatting, which is the third of the project's
stated purposes after learning and production use. A `to_standalone`
document compiles on its own, which is convenient for checking a fragment
before pasting it into a manuscript.

## Options that apply widely

| Option | Meaning |
| --- | --- |
| `encoding` | Text encoding, defaulting to UTF-8 |
| `newline` | Line ending, defaulting to the Unix convention |
| `sort_keys` | Whether to sort, defaulting to true and rarely worth changing |
| `indent` | Indentation for the structured formats |
| `include_attributes` | Whether to write vertex and edge attributes |
| `weight_key` | The attribute name used for weights |
| `strict` | Whether an unexpected element is an error or a warning |

The default of sorting is what produces determinism, and turning it off is
supported only for the case where a caller must match the byte output of
another tool.

## Choosing a format

Eleven modules is more choice than most tasks need, so here is the decision
in one place.

**Interoperating with another graph tool:** GraphML. It is the most
expressive of the graph formats, it is widely supported, and it round trips
attributes and weights without loss. GML is the second choice when the other
tool prefers it or when a human will read the file.

**Handing a graph to Graphviz for layout:** DOT, through `dot_export`. The
file is source for a layout engine rather than a description of a graph, so
it is written and not read.

**Interoperating with a script or a shell pipeline:** an edge list. One edge
per line is the format every language can read in three lines, and the
options that matter, namely the separator and whether weights are present,
are explicit.

**Interoperating with a spreadsheet or a data pipeline:** CSV, as two
tables. The header row means column order is never significant.

**Caching a computed object between runs of your own program:** JSON.
Deterministic output means the cache key can be the file's hash, and unlike
pickle it is safe to read a file you did not write.

**Handing a satisfiability instance to a dedicated solver, or reading a
benchmark:** DIMACS. It is the only format those tools speak, and the reader
tolerates the deviations real instances contain.

**Putting a result into a document:** LaTeX export. A fragment for a
sentence, a tabular for a table, a TikZ picture for a figure, or a
standalone document for checking one before pasting it.

**Anything crossing a trust boundary:** JSON or one of the graph formats,
never pickle.

## Worked example: a pipeline across tools

The following program is the kind of workflow the package is built for. It
reads a graph produced elsewhere, analyses it, writes an instance for an
external solver, and emits a figure and a table for a document, without any
manual reformatting at the boundaries.

```python
from discretus.graphs.coloring import chromatic_number, dsatur
from discretus.graphs.properties import diameter, degree_sequence
from discretus.io import dimacs_io, graph_io, json_io, latex_export
from discretus.logic.sat import Cnf
from discretus.viz import dot_export

# 1. Read a graph written by another tool. The format is chosen by the
#    extension, and the reader refuses an extension it does not recognize
#    rather than guessing.
graph = graph_io.read("input/conflicts.graphml")
print(graph.order(), graph.size())

# 2. Analyse it with the graph package.
summary = {
    "order": graph.order(),
    "size": graph.size(),
    "degrees": degree_sequence(graph),
    "diameter": diameter(graph),
    "chromatic_number": chromatic_number(graph),
}

# 3. Write the summary as deterministic JSON, so that it can be committed
#    and compared between runs of the pipeline.
json_io.dump(summary, "output/summary.json")

# 4. Encode the k colourability question as a satisfiability instance and
#    write it for an external solver, in case the exact chromatic number
#    computation is too slow at the real input size.
instance = Cnf.from_graph_coloring(graph, colours=summary["chromatic_number"])
dimacs_io.dump(instance, "output/coloring.cnf")

# 5. Emit the figure as DOT, so that the document pipeline can lay it out
#    with Graphviz and never needs to import Python.
open("output/conflicts.dot", "w", encoding="utf-8").write(dot_export.to_dot(graph))

# 6. Emit the summary as a LaTeX table for the manuscript.
open("output/summary.tex", "w", encoding="utf-8").write(
    latex_export.to_tabular(summary)
)

# 7. Write the graph back out in a second format, for the next stage.
graph_io.write(graph, "output/conflicts.gml")
```

Every step at a boundary is one call, and every artifact it writes is
deterministic, which has a practical consequence worth stating: the whole
pipeline can be run twice and the outputs compared byte for byte. If they
differ, something in the pipeline is nondeterministic, and that is a defect
to find rather than a fact of life. This library's own test suite uses
exactly that check.

The round trip is worth asserting explicitly when a pipeline is being
written, because it catches a format mismatch immediately rather than three
stages later.

```python
from discretus.io import gml, graphml

for module in (graphml, gml):
    assert module.loads(module.dumps(graph)) == graph
    assert module.dumps(module.loads(module.dumps(graph))) == module.dumps(graph)
print("both formats round trip and are byte stable")
```

## Errors

| Exception | Raised when |
| --- | --- |
| `SerializationError` | An object cannot be expressed in the requested format |
| `ParseError` | Input text is malformed, with the line and column |
| `ValidationError` | An unknown format name or an unrecognized extension |
| `DomainError` | A format cannot express a feature, for instance a parallel edge in GraphML without a key |
| `OptionalDependencyError` | A format needing an optional package is requested |
| `LimitExceededError` | An input describes a structure larger than the configured limit |

The last one matters when reading untrusted input. A file that declares a
billion vertices should be refused before the allocation rather than after,
and the security policy discusses this class of problem directly.

## Complexity summary

| Operation | Complexity |
| --- | --- |
| Edge list write and read | O(E) |
| Adjacency list write and read | O(V + E) |
| Adjacency matrix write and read | O(V squared) |
| GraphML or GML write | O((V + E) log(V + E)) with the sort |
| GraphML or GML read | O(V + E) |
| DIMACS write and read | O(total literals) |
| JSON write | O(size log size) with the sort |
| LaTeX export | O(size of the object) |

The logarithmic factors are the deterministic ordering, and they are worth
paying: an unordered writer is faster and produces a file that changes for
no reason between runs.

## Design notes

**Determinism over speed.** Sorting before writing costs a logarithmic
factor and buys a file that can be committed, compared, and cached. For the
sizes these formats are used at, the trade is not close.

**Round trips are tested, not assumed.** The suite asserts, for every format
and a family of generated objects, that reading what was written returns an
equal object and that writing it again produces identical bytes. That pair
of assertions catches most serialization defects, including the ones that
only appear for an empty structure or a single vertex.

**Formats are honest about their limits.** A format that cannot express a
feature raises rather than dropping it. The alternative, a file that looks
fine and describes a different object, is the worst possible outcome for an
interchange format.

**No external entity resolution, ever.** The XML reader does not fetch
anything, which closes the standard class of attack against XML parsers and
costs nothing, because no legitimate graph document needs it.

**One unsafe format, clearly labelled.** Pickle is useful for local caching
and dangerous for anything else, so it is present, isolated in its own
module, and documented as unsafe in three places.

## Reading untrusted input

The readers in this package are the library's main exposure to data it did
not produce, and the security policy names them for that reason. If your
program reads files or strings that a user supplied, the following is the
short version of how to do it safely.

**Bound the size before you read.** The configured enumeration limit stops a
document that declares an enormous structure, and lowering it for a service
is the single most effective control.

```python
from discretus.config import config_scope
from discretus.io import graph_io

with config_scope(max_enumeration=50_000, strict_validation=True):
    graph = graph_io.read(uploaded_path)
```

**Catch the library's errors, not everything.** A malformed document raises
`ParseError` or `SerializationError`, both of which derive from
`DiscretusError`. Catching that group turns a bad upload into a clean
rejection, while a genuine defect in your own code still propagates.

```python
from discretus import DiscretusError

try:
    graph = graph_io.read(uploaded_path)
except DiscretusError as error:
    return reject(f"could not read the graph: {error}")
```

**Prefer the structured formats.** JSON, GraphML, and GML validate what they
read against an expected shape. An edge list has no way to describe itself,
so a malformed file is more likely to produce a wrong graph than an error,
which makes it the wrong choice for untrusted input even though it is the
most convenient for a script.

**Never read pickle from an untrusted source.** Unpickling can execute
arbitrary code. This is a property of the format rather than of this
library, and no amount of validation inside the reader can change it.

**Use strict mode.** Passing `strict=True` turns a tolerated deviation into
an error, which is what you want when the input should have been produced by
a machine and a deviation means something went wrong upstream.

## Version compatibility of written files

A file written by one version of the library should be readable by the next,
and the package makes that a guarantee rather than a hope.

The structured formats carry a schema version. A reader accepts its own
version and every earlier one within the same major version, and it raises
`SerializationError` naming both versions when it meets a document from a
future version, rather than misreading it.

The graph formats are standards rather than the library's own, so they carry
no schema version of ours. What they do carry is a producer comment naming
the library and the version that wrote the file, which is information a
maintainer wants when a file from two years ago does not read as expected.

Within a major version, no writer will start omitting information that an
earlier version wrote, and no reader will stop accepting a document an
earlier version produced. A change that would break either is a breaking
change and waits for a major release with a migration note, exactly like a
change to the public interface.

## See also

- [`discretus.graphs`](graphs.md), whose structures these formats carry.
- [`discretus.logic`](logic.md), for the satisfiability instances DIMACS
  carries.
- [`discretus.core`](core.md), for the serialization protocol and the
  deterministic ordering the writers use.
- [`discretus.viz`](viz.md), for drawing, which is rendering rather than
  interchange.
