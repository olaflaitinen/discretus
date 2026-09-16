# Satisfiability solving

This tutorial starts with truth tables and ends with a conflict driven
solver, building each step from the one before it. By the end you will know
what the solver does, why it does it that way, how to encode a problem for
it, and how to tell whether an answer is right.

Satisfiability is the first problem shown to be NP complete, and it is also
one of the most practically successful: modern solvers routinely decide
instances with millions of variables. Both halves of that sentence matter,
and this tutorial takes both seriously.

## The problem

A propositional formula is satisfiable when some assignment of truth values
to its variables makes it true. The question is whether such an assignment
exists.

```python
from discretus.logic.propositional import is_satisfiable, parse

print(is_satisfiable(parse("p & q")))
print(is_satisfiable(parse("p & ~p")))
```

The first has a satisfying assignment and the second does not, because a
variable and its negation cannot both hold. Those two are decidable by
inspection. Everything below is about what to do when inspection fails.

## Level zero: truth tables

The definition gives an algorithm immediately: try every assignment.

```python
from discretus.logic.propositional import truth_table

print(truth_table(parse("(p | q) & (~p | r)")))
```

The table has one row per assignment, so a formula with $v$ variables has
$2^v$ rows. That is fine for three variables and hopeless for a hundred.

```python
formula = parse("(p | q) & (~p | r) & (~q | ~r)")
table = truth_table(formula)
print(len(table.rows()))
print(table.models())
print(table.countermodels()[:2])
```

The table object is the complete answer to the question, and everything
else in this tutorial is an attempt to answer the same question without
building it. It remains the right tool for a small formula, because it
reports all the models rather than one, and because it is the ground truth
against which the solvers are checked.

Notice the growth rate before moving on.

```python
for count in (10, 20, 30, 40):
    print(count, 2 ** count)
```

At forty variables the table has over a trillion rows. A solver that decides
such a formula in milliseconds is not doing this faster; it is doing
something else.

## Level one: clause form

Solvers work on conjunctive normal form: a conjunction of clauses, each
clause a disjunction of literals, each literal a variable or its negation.

$$\varphi \equiv \bigwedge_{i=1}^{m} \left( \bigvee_{j=1}^{k_i} \ell_{ij} \right)$$

Any formula can be converted.

```python
from discretus.logic.normal_forms import to_cnf

print(to_cnf(parse("p -> (q -> r)")))
print(to_cnf(parse("~(p & q)")))
```

The conversion preserves equivalence, and its cost can be exponential. A
nested biconditional is the standard example.

```python
nested = parse("(p <-> q) <-> (r <-> s)")
print(len(to_cnf(nested).clauses()))

deeper = parse("((p <-> q) <-> (r <-> s)) <-> ((t <-> u) <-> (v <-> w))")
print(len(to_cnf(deeper).clauses()))
```

The clause count grows sharply, and for a formula with a few dozen
biconditionals the conversion itself becomes the bottleneck. The Tseitin
transformation solves that by giving up equivalence and keeping
equisatisfiability: it names each subformula with a fresh variable and
constrains the name to match the subformula.

```python
from discretus.logic.normal_forms import tseitin

print(tseitin(nested).clause_count())
print(tseitin(deeper).clause_count())
```

Linear rather than exponential. The formula it produces is not equivalent to
the original, because it has extra variables, and it is satisfiable exactly
when the original is, which is all a solver needs. That distinction is worth
holding onto: use `to_cnf` when the formula itself is the object of study,
and `tseitin` when you are about to hand it to a solver.

Why do clauses help at all? Because a clause is a constraint that is easy to
check and easy to propagate. A clause with all but one literal falsified
forces the remaining literal, and that single observation is the engine of
everything that follows.

## Level two: unit propagation

A unit clause is a clause with one literal. It forces that literal. Forcing
it may falsify literals in other clauses, creating new unit clauses, and so
on to a fixed point.

```python
from discretus.logic.sat import Cnf, unit_propagate

instance = Cnf([[1], [-1, 2], [-2, 3]])
assignment, conflict = unit_propagate(instance)
print(assignment, conflict)
```

The first clause forces variable one true. That falsifies the first literal
of the second clause, which forces variable two, which forces variable
three. Three assignments from one, with no search at all.

Propagation can also discover a contradiction.

```python
assignment, conflict = unit_propagate(Cnf([[1], [-1]]))
print(conflict is not None)
```

Unit propagation is linear in the total size of the clauses and it does an
astonishing amount of the work on real instances. The rest of a solver is
machinery for deciding what to assume when propagation runs out.

## Level three: DPLL

The Davis Putnam Logemann Loveland procedure is propagation plus a decision
plus backtracking.

1. Propagate. If a clause is falsified, backtrack.
2. If every variable is assigned, report satisfiable.
3. Choose an unassigned variable, assume a value, and recurse.
4. If that fails, assume the other value.

```python
from discretus.logic.sat import solve_dpll

result = solve_dpll(parse("(p | q) & (~p | r) & (~q | ~r)"))
print(result.is_satisfiable)
print(result.assignment)
print(result.statistics)
```

The statistics report the decisions and the propagations, which is the
interesting part: the ratio of propagations to decisions is a measure of how
much structure the instance has.

DPLL also benefits from the pure literal rule: a variable that appears with
only one polarity can be assigned that polarity without loss.

```python
print(solve_dpll(parse("(p | q) & (p | r)"), pure_literals=True).statistics)
```

DPLL is a complete algorithm, meaning it always terminates with a correct
answer, and it is exponential in the worst case, which is unavoidable
because the problem is NP complete. It is in this library to be read: the
implementation is short enough to follow in one sitting, and every later
improvement is an answer to a specific weakness of it.

## Level four: what DPLL wastes

Run DPLL on a pigeonhole instance, which says that $n + 1$ pigeons fit into
$n$ holes with at most one pigeon per hole. It is unsatisfiable, and it is
famously hard for this kind of search.

```python
from discretus.logic.sat import pigeonhole, solve_dpll

for holes in (3, 4, 5):
    instance = pigeonhole(holes + 1, holes)
    result = solve_dpll(instance)
    print(holes, result.is_satisfiable, result.statistics["decisions"])
```

The decision count grows very fast. The reason is that plain DPLL forgets:
when a subtree fails, it backtracks one level and tries again, and it
relearns the same contradiction in a slightly different arrangement many
times over.

Two ideas fix that, and together they are what distinguishes a modern solver
from DPLL.

**Learn from a conflict.** When propagation falsifies a clause, analyse why.
The analysis produces a new clause that is implied by the original formula
and that rules out the whole class of assignments responsible, not just the
one that was tried.

**Jump rather than step.** Having learned a clause, backtrack to the level
where that clause becomes useful rather than to the parent level.

## Level five: conflict driven clause learning

The default solver in this library implements both.

```python
from discretus.logic.sat import solve

for holes in (3, 4, 5, 6):
    result = solve(pigeonhole(holes + 1, holes))
    print(holes, result.is_satisfiable, result.statistics["conflicts"], result.statistics["learned"])
```

Compare the numbers with the DPLL run above. The conflict count grows far
more slowly, because each conflict produces a clause that prevents a family
of future conflicts.

The parts are separate modules so that each can be read on its own, and each
answers one question.

**Which variable to decide next?** The VSIDS heuristic keeps an activity
score per variable, bumps the scores of the variables involved in each
conflict, and decays all scores periodically. The effect is to focus the
search on the part of the formula where the contradictions are.

```python
result = solve(pigeonhole(6, 5), record_statistics=True)
print(result.statistics["decisions"], result.statistics["propagations"])
```

**How to propagate quickly?** The watched literal scheme watches two
literals per clause. A clause needs examining only when one of its watches
is falsified, so most clauses are untouched by most assignments. That turns
propagation from a scan over every clause into a scan over a small
neighbourhood.

**What to learn from a conflict?** Conflict analysis walks the implication
graph back from the falsified clause to the first unique implication point
and produces the clause that records the real reason. That clause is
asserting, meaning it immediately forces a literal after the backjump, which
is what makes the search make progress.

**When to give up on the current search path?** Restart policies discard the
current assignment while keeping the learned clauses, on a schedule that
grows so that the solver remains complete. The Luby sequence is the standard
choice and is what this solver uses.

```python
print(result.statistics["restarts"])
```

## Verifying an answer

A satisfiable answer is easy to check: evaluate the formula under the
returned assignment. Always do it.

```python
formula = parse("(p | q) & (~p | r) & (~q | ~r)")
model = solve(formula)
print(model.satisfies(formula))
```

That assertion is in this library's own test suite for every solved
instance, and it is worth keeping in your own code too. A solver is a
complicated program and a model checker is three lines, so the check costs
nothing and catches everything.

An unsatisfiable answer is harder, because there is no assignment to
exhibit. Three checks are available and worth knowing.

First, compare with the truth table on a formula small enough to have one.

```python
from discretus.logic.propositional import is_satisfiable

small = parse("(p | q) & (~p | q) & (p | ~q) & (~p | ~q)")
print(solve(small).is_satisfiable, is_satisfiable(small))
```

Second, compare the two solvers. They share almost no code, so agreement is
meaningful.

```python
from discretus.logic.sat import solve_dpll

instance = pigeonhole(5, 4)
print(solve(instance).is_satisfiable, solve_dpll(instance).is_satisfiable)
```

Third, for a serious unsatisfiability claim, ask for the proof. The solver
can record the resolution steps that produced each learned clause, and the
checker verifies that the empty clause follows.

```python
result = solve(pigeonhole(4, 3), record_proof=True)
print(result.is_satisfiable)
print(len(result.proof))
print(result.proof.is_valid())
```

## Encoding a problem

Most of the work in using a solver is encoding, and the encodings worth
knowing are few. Here they are, applied to a small graph colouring problem.

```python
from discretus.graphs.generators import petersen_graph

graph = petersen_graph()
colours = 3
vertices = graph.vertices()


def variable(vertex, colour):
    return f"x_{vertex}_{colour}"


clauses = []

# At least one colour per vertex.
for vertex in vertices:
    clauses.append([variable(vertex, c) for c in range(colours)])

# At most one colour per vertex, pairwise.
for vertex in vertices:
    for first in range(colours):
        for second in range(first + 1, colours):
            clauses.append([f"~{variable(vertex, first)}", f"~{variable(vertex, second)}"])

# Adjacent vertices differ.
for left, right in graph.edges():
    for colour in range(colours):
        clauses.append([f"~{variable(left, colour)}", f"~{variable(right, colour)}"])

instance = Cnf.from_clause_lists(clauses)
result = solve(instance)
print(result.is_satisfiable, instance.variable_count(), instance.clause_count())
```

The Petersen graph is three chromatic, so this is satisfiable, and asking
for two colours is not.

Three encoding patterns appear there and cover most needs.

**At least one** of a set of literals is a single clause containing them
all. It is the cheapest constraint there is.

**At most one** of a set of $k$ literals is $k(k-1)/2$ pairwise clauses,
which is quadratic and fine for small $k$. For large $k$ a commander or
sequential encoding uses auxiliary variables and is linear, and the library
provides both.

```python
from discretus.logic.sat import at_most_one, exactly_one

print(len(at_most_one([f"a{i}" for i in range(6)], encoding="pairwise")))
print(len(at_most_one([f"a{i}" for i in range(6)], encoding="sequential")))
print(len(exactly_one([f"a{i}" for i in range(6)])))
```

**An implication** between conjunctions becomes a clause by the equivalence
$p \rightarrow q \equiv \lnot p \lor q$, which is why a constraint of the
form "if these then that" is always expressible.

Two pieces of advice about encoding, both learned the hard way by everyone
who does it. Prefer fewer, wider clauses to many narrow ones when the choice
exists, because propagation visits clauses. And check your encoding on a
case whose answer you know before trusting it on a case whose answer you
want, because an encoding bug produces a confident wrong answer.

## Interoperating

An instance too hard for this solver should go to a dedicated one, and
DIMACS is how.

```python
instance = Cnf([[1, 2], [-1, 3], [-2, -3]])
print(instance.to_dimacs())

recovered = Cnf.from_dimacs(instance.to_dimacs())
print(recovered == instance)
```

The same format reads a competition benchmark, which is the fastest way to
get a realistic instance for experimentation.

```python
from discretus.io import dimacs_io

# dimacs_io.load("benchmark.cnf")
```

## Beyond satisfiability

Two related questions reduce to satisfiability and are worth knowing about.

A formula is a tautology exactly when its negation is unsatisfiable, and two
formulas are equivalent exactly when their biconditional is a tautology. The
library uses these reductions when a formula is too large for a truth table.

```python
from discretus.logic.propositional import are_equivalent, is_tautology

big = parse(" & ".join(f"(p{i} -> p{i + 1})" for i in range(30)))
print(is_tautology(parse(f"({big}) -> (p0 -> p30)")))
print(are_equivalent(parse("~(p & q)"), parse("~p | ~q")))
```

The first formula has thirty one variables, so its truth table would have
over two billion rows, and the question is answered immediately by the
solver.

Model counting and enumeration are the other direction: rather than one
model, count or list them all.

```python
print(truth_table(parse("p | q")).models())
```

For a small formula the table is the right tool. Counting models of a large
formula is a harder problem than satisfiability, and this library does not
attempt it beyond the table, which the reference states.

## Reading the statistics

The solver reports statistics, and knowing what they mean turns a slow run
from a mystery into a diagnosis. The following table is what each number
tells you and what to do about it.

| Statistic | Meaning | What a large value suggests |
| --- | --- | --- |
| `decisions` | Variables assumed rather than forced | The instance has little propagatable structure |
| `propagations` | Literals forced by unit clauses | Healthy; a high ratio to decisions is good |
| `conflicts` | Falsified clauses encountered | The search is hard, or the instance is unsatisfiable |
| `learned` | Clauses added by conflict analysis | Normal; watch the average length |
| `learned_length` | Mean length of a learned clause | Short is strong; long clauses prune little |
| `restarts` | Searches abandoned and retried | Normal on hard instances |
| `deletions` | Learned clauses discarded | The database is being kept in bounds |

The ratio of propagations to decisions is the single most informative
number. On a structured instance, such as a circuit equivalence or a
scheduling problem, it is large, because one assumption forces many
consequences. On a random instance near the satisfiability threshold it is
close to one, which is why random instances are hard for a solver that
relies on structure.

```python
from discretus.logic.sat import random_ksat, solve

for ratio in (2.0, 3.0, 4.26, 5.0):
    instance = random_ksat(variables=80, clauses=int(80 * ratio), width=3, seed=7)
    result = solve(instance)
    stats = result.statistics
    print(
        ratio,
        result.is_satisfiable,
        stats["decisions"],
        round(stats["propagations"] / max(stats["decisions"], 1), 1),
    )
```

The ratio around four and a quarter is the threshold for three literal
clauses, where satisfiable and unsatisfiable instances are equally likely
and both are hardest. Below it almost every instance is satisfiable and
easy; above it almost every instance is unsatisfiable and, for large widths,
also easy. Watching the decision count peak at the threshold is one of the
more striking experiments in the subject and takes four lines here.

## When the solver is the wrong tool

Three situations call for something else, and recognizing them saves time.

**The problem is naturally about numbers rather than truth values.** A
constraint such as a sum being at most a bound can be encoded, and the
encoding is large and the solver's structure heuristics do poorly on it.
Integer programming or a constraint solver is the right tool.

**The problem has a polynomial algorithm.** Two colourability is bipartite
testing, which is linear. Two satisfiability, where every clause has at most
two literals, is decidable in linear time through the implication graph.
Horn satisfiability is linear. Encoding any of these as general
satisfiability works and is slower than the direct algorithm by an unbounded
factor.

```python
from discretus.graphs.generators import cycle_graph
from discretus.graphs.coloring import is_bipartite
from discretus.logic.normal_forms import is_horn
from discretus.logic.propositional import parse

print(is_bipartite(cycle_graph(6)))              # linear, not a solver call
print(is_horn(parse("(~p | ~q | r) & (~r | s)")))  # linear satisfiability
```

**All the models are wanted, not one.** Counting or enumerating models is a
harder problem than deciding satisfiability. For a small formula the truth
table gives all the models directly; for a large one, this is a research
area and the library does not pretend otherwise.

The general lesson is the one the complexity tables in the reference are
there to support: know what problem you have before choosing the tool, and
prefer the algorithm designed for it.

## Exercises

1. Encode the statement that exactly two of five variables are true, and
   verify the model count against `binomial(5, 2)`.
2. Run the pigeonhole instances with both solvers up to the size where one of
   them becomes too slow, and plot the conflict counts.
3. Encode a Sudoku puzzle and solve it. The constraints are exactly the
   three patterns above, applied to rows, columns, and boxes.
4. Take a formula with nested biconditionals, convert it with both `to_cnf`
   and `tseitin`, and confirm that the solver gives the same answer for both
   while the clause counts differ sharply.
5. Write a program that finds a minimal unsatisfiable subset of a clause
   list by removing clauses one at a time and re solving.
6. Use `at_most_one` with both encodings inside a graph colouring instance
   and compare the solver statistics.

## A note on the two solvers

This library ships two solvers, and the reason is worth stating because the
same pattern appears elsewhere in it.

`solve_dpll` is a transparent reference implementation. It is short, it
follows the procedure as the textbook states it, and a reader can hold all
of it in their head. It is there to be understood.

`solve` is the conflict driven solver. It is longer, it is built from seven
modules, and understanding it takes a session per module. It is there to be
used.

Keeping both has a cost, namely that two implementations must be maintained,
and it buys two things. A reader has something to learn from, and the tuned
implementation has something to be checked against. The test suite runs both
solvers on the same randomized instances and asserts that they agree on
satisfiability, which is a strong check precisely because the two share
almost no code: a defect in the clever one shows up as a disagreement rather
than as a wrong answer that nobody notices.

```python
from discretus.logic.sat import random_ksat, solve, solve_dpll

for seed in range(20):
    instance = random_ksat(variables=18, clauses=70, width=3, seed=seed)
    fast = solve(instance)
    reference = solve_dpll(instance)
    assert fast.is_satisfiable == reference.is_satisfiable
    if fast.is_satisfiable:
        assert fast.satisfies(instance) and reference.satisfies(instance)

print("the two solvers agree on twenty random instances")
```

The instances are small on purpose: eighteen variables is within reach of
the reference implementation, and that is the size at which a comparison is
affordable. Scaling the comparison up is not the point, because the
reference solver is not meant to be fast; the point is that within the range
where both can run, they must agree.

## Where to go next

- The [logic reference](../api/logic.md) for the complete interface,
  including predicate logic and the inference layer.
- [Graph algorithms](graph_algorithms.md), for the colouring problem this
  tutorial encoded, solved directly.
- [Set theory](set_theory.md), for the Boolean algebra underneath
  propositional logic.
