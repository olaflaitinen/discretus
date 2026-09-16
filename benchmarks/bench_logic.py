# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Benchmarks for the propositional and predicate logic packages.

The satisfiability solvers are measured separately, in ``bench_sat``, because
their cost is dominated by search rather than by traversal and because a
solver benchmark needs its own instance families. What is measured here is
everything around them.

What is measured, and why each measurement earns its runtime:

    Parsing, because every program that reads a formula from text pays for
    it, and because the lexer accepts several spellings per connective,
    which is exactly the kind of convenience that can become a bottleneck.

    Evaluation under one assignment, because it is the inner loop of the
    truth table, of the equivalence test, and of the model verification that
    the solver performs on every answer.

    Truth tables, because they grow as two to the number of variables and
    the growth report is the clearest demonstration in the whole suite of
    what an exponential routine costs.

    The normal forms, because the difference between an equivalent
    conversion and an equisatisfiable one is the difference between
    exponential and linear growth. The two are measured on the same input
    family so that the difference is visible as a ratio rather than claimed
    in prose.

    Quine McCluskey minimization, because it is exponential in the variable
    count and is the routine most likely to be called on an input that is
    one variable too large.

    Predicate evaluation, because the cost is the domain size raised to the
    quantifier nesting depth, which is a bound a reader will want to have
    seen measured before relying on it.

    Unification, because it is linear with the occurs check and quadratic
    without a careful implementation, and because the inference layer calls
    it once per resolution step.

Formula families are generated from a seed derived from the benchmark name.
Three families are used deliberately, because they stress different parts of
the implementation: a wide conjunction of small clauses, a deeply nested
chain of implications, and a nest of biconditionals, which is the input that
makes the naive conjunctive conversion blow up.
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

from . import benchmark, require, requires_all, seeded

# ---------------------------------------------------------------------------
# The modules under measurement
# ---------------------------------------------------------------------------

propositional_module = require(
    "discretus.logic.propositional", "parse", "evaluate", "truth_table"
)
normal_forms_module = require(
    "discretus.logic.normal_forms", "to_cnf", "to_nnf", "tseitin"
)
predicate_module = require(
    "discretus.logic.predicate", "Interpretation", "parse_formula", "unify"
)
inference_module = require(
    "discretus.logic.inference", "forward_chaining", "Proof", "check"
)

GROUP = "logic"
GROUP_NORMAL_FORMS = "logic.normal_forms"
GROUP_PREDICATE = "logic.predicate"
GROUP_INFERENCE = "logic.inference"


# ---------------------------------------------------------------------------
# Formula families
# ---------------------------------------------------------------------------
# Each family is built as text and parsed, so that the benchmark measures the
# routine under test rather than a construction convenience. The text is
# generated deterministically from a seed derived from the family name.


def wide_conjunction_text(clauses: int) -> str:
    """Return a conjunction of many small disjunctions.

    This is the shape a real instance has: many clauses, each over a few
    variables. It is the right input for the traversal routines, because it
    is broad rather than deep and therefore does not test the recursion
    limit instead of the algorithm.
    """
    source = seeded("logic.wide_conjunction")
    variables = max(4, clauses // 3)
    parts = []
    for _ in range(clauses):
        chosen = source.sample(range(variables), 3)
        literals = [
            f"{'~' if source.random() < 0.5 else ''}p{index}" for index in chosen
        ]
        parts.append("(" + " | ".join(literals) + ")")
    return " & ".join(parts)


def implication_chain_text(length: int) -> str:
    """Return a right associated chain of implications.

    Implication associates to the right, so this is a deeply nested formula
    with a shallow branching factor. It is the input that finds a recursive
    traversal without an iterative fallback.
    """
    return " -> ".join(f"p{index}" for index in range(length))


def biconditional_nest_text(depth: int) -> str:
    """Return a balanced nest of biconditionals.

    This is the standard input on which the naive conversion to conjunctive
    normal form grows exponentially, because each biconditional expands into
    two implications and the expansion compounds. It is the reason the
    Tseitin transformation exists, and measuring both on this family is what
    makes that reason visible.
    """
    if depth <= 0:
        return "p0"
    left = biconditional_nest_text(depth - 1)
    right = left.replace("p", "q")
    return f"({left}) <-> ({right})"


def make_wide_formula(clauses: int) -> Any:
    """Parse a wide conjunction of the given clause count."""
    assert propositional_module is not None
    return propositional_module.parse(wide_conjunction_text(clauses))


def make_chain_formula(length: int) -> Any:
    """Parse an implication chain of the given length."""
    assert propositional_module is not None
    return propositional_module.parse(implication_chain_text(length))


def make_nested_formula(depth: int) -> Any:
    """Parse a biconditional nest of the given depth."""
    assert propositional_module is not None
    return propositional_module.parse(biconditional_nest_text(depth))


def make_small_formula(variables: int) -> Any:
    """Parse a formula over exactly the requested number of variables.

    Used by the exponential routines, where the variable count is the size
    parameter and the growth report should read as a doubling per step.
    """
    assert propositional_module is not None
    terms = []
    source = seeded("logic.small_formula")
    for index in range(variables):
        sign = "~" if source.random() < 0.4 else ""
        terms.append(f"{sign}p{index}")
    first = " & ".join(terms[: max(1, variables // 2)])
    second = " | ".join(terms[max(1, variables // 2) :] or terms)
    return propositional_module.parse(f"({first}) | ({second})")


def make_formula_and_assignment(clauses: int) -> Tuple[Any, Dict[str, bool]]:
    """Return a wide formula together with a total assignment for it."""
    assert propositional_module is not None
    formula = make_wide_formula(clauses)
    source = seeded("logic.assignment")
    names = propositional_module.variables(formula)
    return formula, {name: source.random() < 0.5 for name in names}


def make_text_only(clauses: int) -> str:
    """Return formula text, for the parsing benchmarks."""
    return wide_conjunction_text(clauses)


def make_two_formulas(clauses: int) -> Tuple[Any, Any]:
    """Return two formulas over the same variables, for the equivalence test."""
    assert propositional_module is not None
    left = make_wide_formula(clauses)
    right = propositional_module.parse(f"~(~({wide_conjunction_text(clauses)}))")
    return left, right


def make_interpretation(domain_size: int) -> Any:
    """Return a finite interpretation over a range, with two predicates."""
    assert predicate_module is not None
    return predicate_module.Interpretation(
        domain=set(range(domain_size)),
        predicates={
            "Even": lambda value: value % 2 == 0,
            "Lt": lambda left, right: left < right,
            "Sum": lambda left, right, total: left + right == total,
        },
    )


def make_terms(depth: int) -> Tuple[Any, Any]:
    """Return two terms that unify, nested to the given depth.

    Deeply nested terms are where the occurs check costs something, and
    where an implementation without one loops forever.
    """
    assert predicate_module is not None
    left = "x"
    right = "a"
    for index in range(depth):
        left = f"f({left}, y{index})"
        right = f"f({right}, b{index})"
    return (
        predicate_module.parse_term(left),
        predicate_module.parse_term(right),
    )


def make_horn_clauses(count: int) -> List[Any]:
    """Return a chain of Horn clauses, which chaining resolves in one pass."""
    assert propositional_module is not None
    return [
        propositional_module.parse(f"p{index} -> p{index + 1}")
        for index in range(count)
    ]


# ---------------------------------------------------------------------------
# Parsing and printing
# ---------------------------------------------------------------------------


@benchmark(
    group=GROUP,
    sizes=[100, 1_000, 10_000],
    complexity="O(size of the text)",
    setup=make_text_only,
    requires=propositional_module,
    note="every program that reads a formula from text pays this",
)
def parse_wide(text: str) -> Any:
    """Parse a wide conjunction."""
    return propositional_module.parse(text)


@benchmark(
    group=GROUP,
    sizes=[100, 1_000, 10_000],
    complexity="O(size of the text)",
    requires=propositional_module,
    note="the deeply nested input, which finds a recursive parser's limit",
)
def parse_chain(length: int) -> Any:
    """Parse a right associated implication chain."""
    return propositional_module.parse(implication_chain_text(length))


@benchmark(
    group=GROUP,
    sizes=[1_000, 10_000],
    complexity="O(size of the text)",
    setup=make_text_only,
    requires=propositional_module,
    note="the alternative spellings the lexer accepts should cost nothing",
)
def parse_word_operators(text: str) -> Any:
    """Parse the same formula written with word operators."""
    spelled = text.replace("&", " and ").replace("|", " or ").replace("~", " not ")
    return propositional_module.parse(spelled)


@benchmark(
    group=GROUP,
    sizes=[100, 1_000, 10_000],
    complexity="O(size of the formula)",
    setup=make_wide_formula,
    requires=propositional_module,
)
def print_formula(formula: Any) -> str:
    """Render a formula back to text."""
    return str(formula)


@benchmark(
    group=GROUP,
    sizes=[100, 1_000, 10_000],
    complexity="O(size of the formula)",
    setup=make_wide_formula,
    requires=propositional_module,
)
def collect_variables(formula: Any) -> List[str]:
    """Collect the variable names of a formula, sorted."""
    return propositional_module.variables(formula)


@benchmark(
    group=GROUP,
    sizes=[1_000, 10_000],
    complexity="O(size of the formula)",
    setup=make_wide_formula,
    requires=propositional_module,
    note="the round trip; the printed form must parse back to an equal tree",
)
def round_trip(formula: Any) -> bool:
    """Print a formula and parse the result back."""
    return propositional_module.parse(str(formula)) == formula


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------


@benchmark(
    group=GROUP,
    sizes=[100, 1_000, 10_000],
    complexity="O(size of the formula)",
    setup=make_formula_and_assignment,
    requires=propositional_module,
    note="the inner loop of the truth table and of model verification",
)
def evaluate_once(payload: Tuple[Any, Dict[str, bool]]) -> bool:
    """Evaluate a formula under one total assignment."""
    formula, assignment = payload
    return propositional_module.evaluate(formula, assignment)


@benchmark(
    group=GROUP,
    sizes=[100, 1_000],
    complexity="O(size of the formula) per assignment",
    setup=make_formula_and_assignment,
    requires=propositional_module,
    note="a thousand evaluations, which is the shape a search performs",
)
def evaluate_many(payload: Tuple[Any, Dict[str, bool]]) -> int:
    """Evaluate a formula a thousand times under varying assignments."""
    formula, assignment = payload
    names = sorted(assignment)
    satisfied = 0
    for index in range(1_000):
        for position, name in enumerate(names):
            assignment[name] = bool((index >> (position % 16)) & 1)
        if propositional_module.evaluate(formula, assignment):
            satisfied += 1
    return satisfied


@benchmark(
    group=GROUP,
    sizes=[8, 12, 16, 20],
    complexity="O(2 to the v) rows, each O(size)",
    setup=make_small_formula,
    requires=propositional_module,
    note=(
        "the size is the variable count, so each step doubles the rows; this "
        "is the clearest exponential growth in the suite"
    ),
)
def truth_table(formula: Any) -> Any:
    """Build the full truth table of a formula."""
    return propositional_module.truth_table(formula)


@benchmark(
    group=GROUP,
    sizes=[8, 12, 16],
    complexity="O(2 to the v)",
    setup=make_small_formula,
    requires=propositional_module,
)
def tautology_test(formula: Any) -> bool:
    """Decide whether a formula is a tautology."""
    return propositional_module.is_tautology(formula)


@benchmark(
    group=GROUP,
    sizes=[8, 12, 16],
    complexity="O(2 to the v) by table, or a solver call",
    setup=make_small_formula,
    requires=propositional_module,
)
def satisfiability_test(formula: Any) -> bool:
    """Decide whether a formula is satisfiable."""
    return propositional_module.is_satisfiable(formula)


@benchmark(
    group=GROUP,
    sizes=[20, 100, 500],
    complexity="O(2 to the v) by table, or a solver call",
    setup=make_two_formulas,
    requires=propositional_module,
    note=(
        "the two formulas are equivalent by construction, so the routine "
        "cannot stop early; a formula this wide must route through the "
        "solver rather than through a table"
    ),
)
def equivalence_test(payload: Tuple[Any, Any]) -> bool:
    """Decide whether two formulas are equivalent."""
    left, right = payload
    return propositional_module.are_equivalent(left, right)


@benchmark(
    group=GROUP,
    sizes=[100, 1_000, 10_000],
    complexity="O(size of the formula)",
    setup=make_wide_formula,
    requires=propositional_module,
)
def simplify(formula: Any) -> Any:
    """Simplify a formula structurally."""
    return propositional_module.simplify(formula)


@benchmark(
    group=GROUP,
    sizes=[100, 1_000, 10_000],
    complexity="O(size of the formula)",
    setup=make_wide_formula,
    requires=propositional_module,
)
def substitute(formula: Any) -> Any:
    """Substitute a formula for a variable."""
    mapping = {"p0": propositional_module.parse("q0 & q1")}
    return propositional_module.substitute(formula, mapping)


# ---------------------------------------------------------------------------
# Normal forms
# ---------------------------------------------------------------------------


@benchmark(
    group=GROUP_NORMAL_FORMS,
    sizes=[100, 1_000, 10_000],
    complexity="O(size)",
    setup=make_wide_formula,
    requires=requires_all(propositional_module, normal_forms_module),
    note="negation normal form is the cheap one: it only pushes negations in",
)
def to_nnf(formula: Any) -> Any:
    """Convert to negation normal form."""
    return normal_forms_module.to_nnf(formula)


@benchmark(
    group=GROUP_NORMAL_FORMS,
    sizes=[100, 1_000, 5_000],
    complexity="exponential in the worst case",
    setup=make_wide_formula,
    requires=requires_all(propositional_module, normal_forms_module),
    note="on a wide conjunction of clauses the conversion is nearly free",
)
def to_cnf_wide(formula: Any) -> Any:
    """Convert a wide conjunction to conjunctive normal form."""
    return normal_forms_module.to_cnf(formula)


@benchmark(
    group=GROUP_NORMAL_FORMS,
    sizes=[2, 3, 4, 5],
    complexity="exponential in the nesting depth",
    setup=make_nested_formula,
    requires=requires_all(propositional_module, normal_forms_module),
    note=(
        "the same routine on the input that defeats it; compare the growth "
        "here with tseitin_nested below, which is the whole argument for the "
        "Tseitin transformation"
    ),
)
def to_cnf_nested(formula: Any) -> Any:
    """Convert a biconditional nest to conjunctive normal form."""
    return normal_forms_module.to_cnf(formula)


@benchmark(
    group=GROUP_NORMAL_FORMS,
    sizes=[2, 3, 4, 5, 6, 7],
    complexity="O(size), linear in clauses and variables",
    setup=make_nested_formula,
    requires=requires_all(propositional_module, normal_forms_module),
    note=(
        "equisatisfiable rather than equivalent, which is what buys the "
        "linear growth; it reaches depths the equivalent conversion cannot"
    ),
)
def tseitin_nested(formula: Any) -> Any:
    """Apply the Tseitin transformation to a biconditional nest."""
    return normal_forms_module.tseitin(formula)


@benchmark(
    group=GROUP_NORMAL_FORMS,
    sizes=[100, 1_000, 5_000],
    complexity="exponential in the worst case",
    setup=make_wide_formula,
    requires=requires_all(propositional_module, normal_forms_module),
    note="the dual conversion, expensive on the input that suits the other",
)
def to_dnf_wide(formula: Any) -> Any:
    """Convert a wide conjunction to disjunctive normal form."""
    return normal_forms_module.to_dnf(formula)


@benchmark(
    group=GROUP_NORMAL_FORMS,
    sizes=[6, 8, 10],
    complexity="exponential in the variable count",
    setup=make_small_formula,
    requires=requires_all(propositional_module, normal_forms_module),
)
def to_anf(formula: Any) -> Any:
    """Convert to algebraic normal form, an exclusive or of conjunctions."""
    return normal_forms_module.to_anf(formula)


@benchmark(
    group=GROUP_NORMAL_FORMS,
    sizes=[4, 6, 8, 10],
    complexity="exponential in the variable count",
    setup=make_small_formula,
    requires=requires_all(propositional_module, normal_forms_module),
    note=(
        "exact two level minimization; the routine most likely to be called "
        "on an input one variable larger than it can afford"
    ),
)
def quine_mccluskey(formula: Any) -> Any:
    """Minimize a formula by the Quine McCluskey procedure."""
    return normal_forms_module.quine_mccluskey(formula)


@benchmark(
    group=GROUP_NORMAL_FORMS,
    sizes=[2, 3, 4],
    complexity="O(2 to the v)",
    setup=make_small_formula,
    requires=requires_all(propositional_module, normal_forms_module),
    note="limited to four variables by the geometry of the map",
)
def karnaugh_map(formula: Any) -> Any:
    """Build a Karnaugh map with its groupings."""
    return normal_forms_module.karnaugh_map(formula)


@benchmark(
    group=GROUP_NORMAL_FORMS,
    sizes=[100, 1_000, 10_000],
    complexity="O(total size of the clauses)",
    setup=make_wide_formula,
    requires=requires_all(propositional_module, normal_forms_module),
    note="the Horn test, which decides whether linear satisfiability applies",
)
def horn_test(formula: Any) -> bool:
    """Decide whether every clause of a formula is Horn."""
    return normal_forms_module.is_horn(formula)


# ---------------------------------------------------------------------------
# Predicate logic
# ---------------------------------------------------------------------------


@benchmark(
    group=GROUP_PREDICATE,
    sizes=[10, 100, 1_000],
    complexity="O(d) for one quantifier over a domain of size d",
    setup=make_interpretation,
    requires=predicate_module,
)
def evaluate_one_quantifier(interpretation: Any) -> bool:
    """Evaluate a singly quantified sentence."""
    formula = predicate_module.parse_formula("forall x. Even(x) | ~Even(x)")
    return interpretation.evaluate(formula)


@benchmark(
    group=GROUP_PREDICATE,
    sizes=[10, 30, 100],
    complexity="O(d squared) for two nested quantifiers",
    setup=make_interpretation,
    requires=predicate_module,
    note="the growth should be the square of the domain size",
)
def evaluate_two_quantifiers(interpretation: Any) -> bool:
    """Evaluate a doubly quantified sentence."""
    formula = predicate_module.parse_formula("forall x. exists y. Lt(x, y)")
    return interpretation.evaluate(formula)


@benchmark(
    group=GROUP_PREDICATE,
    sizes=[6, 10, 16],
    complexity="O(d cubed) for three nested quantifiers",
    setup=make_interpretation,
    requires=predicate_module,
    note=(
        "the domain is small because the cost is its cube; this is the "
        "measurement that justifies the bound the reference states"
    ),
)
def evaluate_three_quantifiers(interpretation: Any) -> bool:
    """Evaluate a triply quantified sentence."""
    formula = predicate_module.parse_formula(
        "forall x. forall y. exists z. Sum(x, y, z)"
    )
    return interpretation.evaluate(formula)


@benchmark(
    group=GROUP_PREDICATE,
    sizes=[100, 1_000, 10_000],
    complexity="O(size of the text)",
    requires=predicate_module,
)
def parse_predicate_formula(length: int) -> Any:
    """Parse a quantified formula of increasing length."""
    body = " & ".join(f"Even(x{index})" for index in range(max(1, length // 20)))
    prefix = " ".join(f"forall x{index}." for index in range(max(1, length // 20)))
    return predicate_module.parse_formula(f"{prefix} {body}")


@benchmark(
    group=GROUP_PREDICATE,
    sizes=[10, 100, 1_000],
    complexity="O(size) with the occurs check",
    setup=make_terms,
    requires=predicate_module,
    note=(
        "linear with a careful implementation and quadratic without one; the "
        "occurs check is what keeps the result sound"
    ),
)
def unify(payload: Tuple[Any, Any]) -> Any:
    """Compute the most general unifier of two nested terms."""
    left, right = payload
    return predicate_module.unify(left, right)


@benchmark(
    group=GROUP_PREDICATE,
    sizes=[10, 100, 1_000],
    complexity="O(size)",
    setup=make_terms,
    requires=predicate_module,
)
def substitution(payload: Tuple[Any, Any]) -> Any:
    """Apply a capture avoiding substitution to a term."""
    left, _ = payload
    return predicate_module.substitute(left, {"x": predicate_module.parse_term("g(z)")})


@benchmark(
    group=GROUP_PREDICATE,
    sizes=[10, 50, 100],
    complexity="O(size)",
    requires=predicate_module,
)
def skolemize(depth: int) -> Any:
    """Remove the existential quantifiers of a formula."""
    prefix = " ".join(
        f"{'forall' if index % 2 else 'exists'} x{index}." for index in range(depth)
    )
    body = " & ".join(f"Even(x{index})" for index in range(depth))
    formula = predicate_module.parse_formula(f"{prefix} {body}")
    return predicate_module.skolemize(formula)


# ---------------------------------------------------------------------------
# Inference
# ---------------------------------------------------------------------------


@benchmark(
    group=GROUP_INFERENCE,
    sizes=[10, 100, 1_000],
    complexity="O(total size of the clauses)",
    setup=make_horn_clauses,
    requires=requires_all(propositional_module, inference_module),
    note="Horn inference is linear, which is why the restriction exists",
)
def forward_chaining(clauses: List[Any]) -> Any:
    """Derive every consequence of a Horn chain, data driven."""
    return inference_module.forward_chaining(clauses, facts={"p0"})


@benchmark(
    group=GROUP_INFERENCE,
    sizes=[10, 100, 1_000],
    complexity="O(total size of the clauses)",
    setup=make_horn_clauses,
    requires=requires_all(propositional_module, inference_module),
    note="the same derivation, goal driven, which visits fewer clauses",
)
def backward_chaining(clauses: List[Any]) -> Any:
    """Prove the last consequence of a Horn chain, goal driven."""
    target = f"p{len(clauses)}"
    return inference_module.backward_chaining(clauses, facts={"p0"}, goal=target)


@benchmark(
    group=GROUP_INFERENCE,
    sizes=[10, 20, 40],
    complexity="exponential in the worst case",
    setup=make_horn_clauses,
    requires=requires_all(propositional_module, inference_module),
    note="resolution refutation, which is complete and not polynomial",
)
def resolution(clauses: List[Any]) -> Any:
    """Refute a clause set by resolution."""
    return inference_module.resolution(clauses)


@benchmark(
    group=GROUP_INFERENCE,
    sizes=[10, 100, 1_000],
    complexity="O(lines times premises)",
    setup=make_horn_clauses,
    requires=requires_all(propositional_module, inference_module),
    note=(
        "checking a derivation is cheap, which is what makes the module "
        "usable for automated assessment"
    ),
)
def proof_checking(clauses: List[Any]) -> Any:
    """Build a derivation by modus ponens and check every line."""
    proof = inference_module.Proof()
    proof.assume(propositional_module.parse("p0"))
    for index, clause in enumerate(clauses):
        proof.assume(clause)
        proof.derive(
            propositional_module.parse(f"p{index + 1}"),
            rule="modus ponens",
            premises=[index * 2, index * 2 + 1],
        )
    return inference_module.check(proof)


# ---------------------------------------------------------------------------
# Notes on reading these results
# ---------------------------------------------------------------------------
#
# The comparisons worth looking at:
#
#   to_cnf_nested against tseitin_nested. This is the central measurement of
#   the file. The first grows exponentially in the nesting depth and stops
#   being runnable around depth five; the second is linear and reaches depth
#   seven comfortably. The two routines answer different questions, and the
#   documentation says which to use when, and this is where that advice is
#   earned rather than asserted.
#
#   to_cnf_wide against to_cnf_nested. The same routine on two input
#   families, one of which it handles almost for free. A complexity claim of
#   "exponential in the worst case" is only honest when the ordinary case is
#   also measured.
#
#   truth_table against satisfiability_test. Both are exponential in the
#   variable count, and the second should pull away as the formula grows,
#   because it routes through the solver rather than enumerating rows.
#
#   evaluate_one_quantifier, evaluate_two_quantifiers, and
#   evaluate_three_quantifiers. The implied exponents in the growth report
#   should be roughly one, two, and three, which is the bound the reference
#   states for k nested quantifiers over a domain of size d.
#
#   forward_chaining against backward_chaining. Both are linear, and the
#   goal driven direction should visit fewer clauses on this input family,
#   which is the reason both are provided.
#
#   parse_wide against parse_word_operators. The alternative spellings the
#   lexer accepts should cost nothing measurable. A gap means the lexer is
#   doing string replacement rather than recognizing tokens.
