# `discretus.logic`

The logic package covers propositional logic, Boolean normal forms and
minimization, satisfiability solving, predicate logic over finite
interpretations, and an inference layer with proof checking.

It is the largest package after graphs, and the one where the distance
between a definition and a running program is shortest: a formula is an
expression tree, a truth table is an enumeration of its assignments, and a
model is a mapping from variable names to truth values.

## Mathematical basis

A propositional formula is built from atoms and the connectives negation,
conjunction, disjunction, implication, and biconditional. The last two are
definable from the first three,

$$p \rightarrow q \equiv \lnot p \lor q, \qquad
p \leftrightarrow q \equiv (p \rightarrow q) \land (q \rightarrow p),$$

and negation distributes over the binary connectives by the De Morgan laws,

$$\lnot (p \lor q) \equiv \lnot p \land \lnot q, \qquad
\lnot (p \land q) \equiv \lnot p \lor \lnot q.$$

A formula is a tautology when every assignment satisfies it, a contradiction
when none does, and satisfiable when at least one does. Two formulas are
equivalent when they agree on every assignment, and a set of formulas
entails a formula when every assignment satisfying the set satisfies it.
Equivalence and entailment reduce to satisfiability, which is how the
package implements them for formulas large enough that a truth table is not
an option.

Every formula has a conjunctive normal form, a conjunction of disjunctions
of literals,

$$\varphi \equiv \bigwedge_{i=1}^{m} \left( \bigvee_{j=1}^{k_i} \ell_{ij} \right),$$

and a disjunctive normal form, the dual. The naive conversion can grow
exponentially, which is why the Tseitin transformation exists: it introduces
auxiliary variables and produces an equisatisfiable formula whose size is
linear in the input.

## Module map

| Subpackage | Responsibility |
| --- | --- |
| `propositional` | Expression trees, parsing, evaluation, truth tables |
| `normal_forms` | Negation, conjunctive, disjunctive, and algebraic forms, minimization |
| `sat` | DPLL and conflict driven satisfiability solving, DIMACS |
| `predicate` | Terms, quantifiers, interpretations, unification |
| `inference` | Resolution, chaining, natural deduction, proof checking |

## Building and parsing formulas

### The expression tree

`propositional.ast_nodes` defines the node types: `Variable`, `Constant`,
`Not`, `And`, `Or`, `Implies`, `Iff`, `Xor`, `Nand`, and `Nor`. Nodes are
immutable and hashable, so a formula can be a dictionary key and two
structurally equal formulas are equal and hash alike, which the caches rely
on.

```python
>>> from discretus.logic.propositional import And, Implies, Not, Variable
>>> p, q = Variable("p"), Variable("q")
>>> formula = Implies(And(p, Not(q)), p)
>>> str(formula)
'((p & ~q) -> p)'
```

### `parse(text) -> Expression`

Parse a formula from a readable syntax. The lexer accepts several spellings
of each connective, so a formula copied from a textbook, from a programming
language, or from a lecture slide is usually accepted unchanged.

| Connective | Accepted spellings |
| --- | --- |
| Negation | `~`, `!`, `not` |
| Conjunction | `&`, `&&`, `and` |
| Disjunction | `|`, `||`, `or` |
| Implication | `->`, `=>`, `implies` |
| Biconditional | `<->`, `<=>`, `==`, `iff` |
| Exclusive or | `^`, `xor` |
| Constants | `T`, `F` |

Precedence, from tightest to loosest, is negation, conjunction, exclusive
or, disjunction, implication, biconditional. Implication associates to the
right, so `p -> q -> r` parses as `p -> (q -> r)`, which is the standard
convention. A malformed formula raises `ParseError` with the position of the
offending character.

```python
>>> from discretus.logic.propositional import parse
>>> parse("p and not q or r") == parse("(p & ~q) | r")
True
```

## Evaluating and tabulating

| Routine | Meaning | Complexity |
| --- | --- | --- |
| `evaluate(formula, assignment)` | Truth value under one assignment | O(size) |
| `variables(formula)` | The variable names, sorted | O(size) |
| `truth_table(formula)` | The table over every assignment | O(2 to the v) |
| `is_tautology(formula)` | True under every assignment | O(2 to the v) |
| `is_contradiction(formula)` | False under every assignment | O(2 to the v) |
| `is_satisfiable(formula)` | True under some assignment | O(2 to the v) or solver |
| `are_equivalent(left, right)` | Agreement on every assignment | O(2 to the v) |
| `entails(premises, conclusion)` | Every model of the premises is one | O(2 to the v) |
| `simplify(formula)` | Equivalent formula, smaller where possible | O(size) |
| `substitute(formula, mapping)` | Replace variables by formulas | O(size) |

For formulas with more variables than a truth table can enumerate,
`is_satisfiable`, `are_equivalent`, and `entails` route through the
satisfiability solver instead, which is the standard reduction: two formulas
are equivalent exactly when their biconditional is a tautology, and a
formula is a tautology exactly when its negation is unsatisfiable.

```python
>>> from discretus.logic.propositional import parse, truth_table
>>> print(truth_table(parse("p -> q")))
p | q | (p -> q)
--+---+---------
F | F | T
F | T | T
T | F | F
T | T | T
```

The table object is more than its printed form: it exposes `rows`,
`models`, `countermodels`, `to_latex`, and `to_csv`, so it can drive a
figure, a handout, or an assertion in a test.

## Normal forms and minimization

| Routine | Result | Notes |
| --- | --- | --- |
| `to_nnf(formula)` | Negation normal form | Negations only on atoms |
| `to_cnf(formula)` | Conjunctive normal form | Equivalent, may grow exponentially |
| `to_dnf(formula)` | Disjunctive normal form | Dual of the above |
| `to_anf(formula)` | Algebraic normal form | Exclusive or of conjunctions |
| `tseitin(formula)` | Equisatisfiable conjunctive form | Linear size, new variables |
| `is_horn(formula)` | Whether every clause is Horn | Horn satisfiability is linear |
| `quine_mccluskey(formula)` | Prime implicants and a minimal cover | Exact two level minimization |
| `minimize(formula)` | Minimal two level form | Wraps the above |
| `karnaugh_map(formula)` | The map, with groupings | Up to four variables |
| `to_prenex(formula)` | Prenex form | Predicate logic |
| `skolemize(formula)` | Skolem normal form | Predicate logic |

The distinction between `to_cnf` and `tseitin` matters in practice and is
worth stating once. `to_cnf` produces an equivalent formula, which is what
you want when the formula itself is the object of study, and its size can
double with each nested biconditional. `tseitin` produces a formula that is
satisfiable exactly when the input is, at the cost of introducing one new
variable per subformula, and it is what you want before handing a formula to
a solver.

```python
>>> from discretus.logic.normal_forms import to_cnf, tseitin
>>> from discretus.logic.propositional import parse
>>> nested = parse("(p <-> q) <-> (r <-> s)")
>>> len(to_cnf(nested).clauses()), tseitin(nested).clause_count()
(8, 16)
```

The Quine McCluskey procedure reports its intermediate structure rather than
only a result: the prime implicants, the essential ones, and the chosen
cover, which is what makes it teachable.

## Satisfiability

### `solve(formula, **options) -> Model`

The default entry point. It converts to clause form, runs the conflict
driven solver, and returns a `Model` that reports the satisfying assignment,
or a result object that reports unsatisfiability. A `Model` can verify
itself against the original formula with `satisfies`, which is a cheap and
worthwhile assertion in a test.

### `solve_dpll(formula, **options) -> Model`

The classical Davis Putnam Logemann Loveland procedure: unit propagation,
pure literal elimination, and a decision with backtracking. It is the
transparent reference implementation, and the conflict driven solver is
validated against it on randomized instances.

### `Cdcl(clauses, **options)`

The conflict driven clause learning solver. Its parts are separate modules
so that each can be read and tested on its own.

| Module | Role |
| --- | --- |
| `clause` | A clause as a frozen set of signed integer literals |
| `clause_db` | The clause database, with learned clause management |
| `assignment` | The trail, with decision levels and antecedents |
| `unit_propagation` | Propagation to a fixed point |
| `watched_literals` | Two watched literals per clause |
| `conflict_analysis` | First unique implication point learning |
| `vsids` | Variable state independent decaying sum activity |
| `heuristics` | Decision and phase selection |
| `restart` | Luby restart schedule |
| `model` | The satisfying assignment, with verification |
| `dimacs` | Reading and writing the interchange format |

Options include a conflict budget, a propagation budget, a restart policy, a
random seed for the tie breaking in the decision heuristic, and a flag that
records the resolution steps of each learned clause for teaching.

```python
>>> from discretus.logic.propositional import parse
>>> from discretus.logic.sat import solve
>>> model = solve(parse("(p | q) & (~p | r) & (~q | ~r)"))
>>> model.satisfies(parse("(p | q) & (~p | r) & (~q | ~r)"))
True
```

### DIMACS interchange

```python
>>> from discretus.logic.sat import Cnf
>>> instance = Cnf([[1, 2], [-1, 3], [-2, -3]])
>>> print(instance.to_dimacs())
p cnf 3 3
1 2 0
-1 3 0
-2 -3 0
```

`Cnf.from_dimacs` reads the format, tolerating comments and a header whose
counts disagree with the body, which real instances sometimes have. The
writer is deterministic, so the same instance always produces the same file.

Reading and writing DIMACS is what makes the package interoperable: an
instance too hard for this solver can be handed to a dedicated one without
reformatting, and an instance from a competition benchmark can be read
directly.

## Predicate logic

Predicate logic here is evaluated over an explicit finite interpretation
rather than proved about, which makes it a tool for teaching model theory
and for checking small specifications.

| Module | Role |
| --- | --- |
| `term` | Variables, constants, and function applications |
| `predicate` | Predicate symbols with an arity |
| `formula` | Atoms, connectives, and quantifiers |
| `quantifier` | Universal and existential quantification |
| `domain` | The finite carrier of an interpretation |
| `interpretation` | Assignment of meaning to symbols |
| `evaluator` | Evaluation of a sentence under an interpretation |
| `free_bound` | Free and bound variable analysis |
| `substitution` | Capture avoiding substitution |
| `unification` | Most general unifier of two terms |
| `skolemization` | Removal of existential quantifiers |
| `parser` | A readable syntax for quantified formulas |

```python
>>> from discretus.logic.predicate import Interpretation, parse_formula
>>> model = Interpretation(
...     domain={0, 1, 2, 3},
...     predicates={"Even": lambda n: n % 2 == 0, "Lt": lambda x, y: x < y},
... )
>>> model.evaluate(parse_formula("forall x. exists y. Lt(x, y)"))
False
>>> model.evaluate(parse_formula("forall x. Even(x) | ~Even(x)"))
True
```

The first sentence is false because the domain has a greatest element, which
is exactly the kind of fact a reader is meant to discover by evaluation
rather than by being told. Evaluation of a quantified sentence over a domain
of size $d$ with $k$ nested quantifiers costs $O(d^k)$ evaluations of the
body, which the reference states so that the cost of a deeply nested
sentence is not a surprise.

Unification returns the most general unifier as a substitution, or reports
failure with the clash, and it performs the occurs check, without which the
result would be unsound.

## Inference

The inference layer produces and checks derivations, which is the part of
logic that a solver deliberately skips.

| Module | Role |
| --- | --- |
| `rules` | The inference rules, as data |
| `modus_ponens` | The rule and its application |
| `resolution` | Resolution refutation with a clause set |
| `forward_chaining` | Data driven inference over Horn clauses |
| `backward_chaining` | Goal driven inference over Horn clauses |
| `natural_deduction` | Introduction and elimination rules |
| `sequent_calculus` | Sequents and their rules |
| `proof` | A derivation as a sequence of justified lines |
| `proof_checker` | Verification that every line follows from its premises |

A `Proof` is a list of lines, each with a formula, a rule, and the indices
of its premises. The checker verifies each line independently, so a proof
produced by hand, by a student, or by the library itself is checked the same
way. That makes the module usable for automated assessment: a submitted
derivation is data, and checking it is a function call.

```python
>>> from discretus.logic.inference import Proof, check
>>> from discretus.logic.propositional import parse
>>> proof = Proof()
>>> proof.assume(parse("p -> q"))
0
>>> proof.assume(parse("p"))
1
>>> proof.derive(parse("q"), rule="modus ponens", premises=[0, 1])
2
>>> check(proof).is_valid
True
```

Forward and backward chaining are restricted to Horn clauses, where
satisfiability is decidable in linear time, and the modules say so: the
restriction is the reason the algorithms are efficient, not an omission.

## Complexity summary

| Routine | Complexity |
| --- | --- |
| Parsing | O(size of the text) |
| Evaluation under one assignment | O(size of the formula) |
| Truth table | O(2 to the v) rows, each O(size) |
| Tautology, contradiction, equivalence by table | O(2 to the v) |
| Satisfiability | Exponential in the worst case, NP complete |
| Horn satisfiability | O(total size of the clauses) |
| Conversion to negation normal form | O(size) |
| Conversion to conjunctive normal form | Exponential in the worst case |
| Tseitin transformation | O(size), linear in clauses and variables |
| Quine McCluskey | Exponential in the number of variables |
| Unit propagation | O(total size of the clauses) per fixed point |
| Predicate evaluation | O(d to the k) for k nested quantifiers |
| Unification | O(size) with the occurs check |

The exponential entries are the mathematics rather than a defect.
Satisfiability is NP complete, and the library's job is to state the cost
and to provide the practical solver, not to promise a bound that cannot
exist.

## Errors

| Exception | Raised when |
| --- | --- |
| `ParseError` | Formula text is malformed, with the position |
| `ValidationError` | An assignment omits a variable the formula uses |
| `DomainError` | A quantifier ranges over an empty domain where the semantics require members |
| `InfeasibleError` | A model is requested from an unsatisfiable formula |
| `LimitExceededError` | A truth table or a normal form exceeded the configured limit |
| `ConvergenceError` | A solver exhausted its conflict budget without deciding |

The last two deserve a note. A truth table over thirty variables has over a
billion rows, and the enumeration limit catches the request before the
allocation, which is why an accidental `truth_table` on a large formula
produces an error rather than an unresponsive machine. A solver that
exhausts its budget reports that it did not decide, rather than reporting
unsatisfiable, because those are different answers and conflating them would
be unsound.

## Worked example: a small verification problem

The following is a complete use of the package on a problem that is not a
textbook exercise: deciding whether a configuration is consistent, and if it
is not, finding out why.

Suppose a build system has four optional features and the following rules.
Feature `a` requires `b`. Features `b` and `c` conflict. Feature `d`
requires either `b` or `c`. At least one of `a` and `d` must be enabled.

```python
from discretus.logic.propositional import parse
from discretus.logic.sat import solve

rules = [
    parse("a -> b"),
    parse("~(b & c)"),
    parse("d -> (b | c)"),
    parse("a | d"),
]

conjunction = rules[0]
for rule in rules[1:]:
    conjunction = parse(f"({conjunction}) & ({rule})")

model = solve(conjunction)
print(model)
print(model.satisfies(conjunction))
```

The instance is satisfiable, and the model names one configuration that
works. Two follow up questions are the ones that matter in practice.

First, is a particular choice forced? A variable is forced to be true
exactly when the instance together with its negation is unsatisfiable, which
is one extra solver call per variable.

```python
for feature in "abcd":
    forced_true = not solve(parse(f"({conjunction}) & ~{feature}")).is_satisfiable
    forced_false = not solve(parse(f"({conjunction}) & {feature}")).is_satisfiable
    if forced_true:
        print(feature, "must be enabled")
    elif forced_false:
        print(feature, "cannot be enabled")
```

Second, if a rule set is inconsistent, which rules are to blame? Add the
rules one at a time and stop at the first addition that makes the set
unsatisfiable. The result is not a minimal explanation in general, but it is
the one line answer that resolves most real inconsistencies.

```python
accumulated = None
for index, rule in enumerate(rules):
    accumulated = rule if accumulated is None else parse(f"({accumulated}) & ({rule})")
    if not solve(accumulated).is_satisfiable:
        print("inconsistent after adding rule", index, ":", rule)
        break
else:
    print("the rule set is consistent")
```

This pattern generalizes to scheduling, to configuration, and to the kind of
small verification question that is usually answered by hand and should not
be. The entire program is four imports and twenty lines, and every
intermediate object is inspectable: the formula prints, the model verifies
itself, and the instance exports to DIMACS if the problem grows beyond what
this solver should be asked to do.

## Design notes

**Formulas are immutable trees.** Every transformation returns a new tree,
so a formula can be shared, cached, and used as a dictionary key. The cost is
allocation, and the benefit is that a transformation cannot corrupt a
formula another part of the program is still reading.

**Two solvers, deliberately.** The DPLL procedure exists to be read, and the
conflict driven solver exists to be used. Keeping both is the pattern the
library applies wherever a transparent and a tuned implementation differ,
and the tuned one is cross validated against the transparent one on
randomized instances, so an optimization cannot silently change an answer.

**Clause form uses signed integers.** Internally a literal is a signed
integer in the DIMACS convention, where the sign is the polarity and the
magnitude is the variable index. That is what the interchange format uses,
what the watched literal scheme wants, and what keeps the inner loops free
of object allocation. The variable names are preserved in a mapping, so the
model that comes back out speaks the caller's vocabulary rather than the
solver's.

**A model verifies itself.** `Model.satisfies` re evaluates the original
formula under the returned assignment. It is redundant when the solver is
correct, which is exactly why it is there: the test suite asserts it on
every solved instance, so a defect in the solver shows up as a failed
verification rather than as a wrong answer that nobody notices.

## See also

- The [satisfiability tutorial](../tutorials/sat_solving.md), which builds up
  from truth tables to conflict driven search.
- [`discretus.combinatorics`](combinatorics.md), for counting the
  assignments this package enumerates.
- [`discretus.io`](io.md), for the DIMACS reader and writer.
- [`discretus.viz`](viz.md), for drawing truth tables and Karnaugh maps.
- [`discretus.algebra`](algebra.md), for the Boolean algebra and the
  algebraic normal form over the binary field.
