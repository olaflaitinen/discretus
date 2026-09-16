# `discretus.core`

The core layer defines the abstractions that every domain package shares. It
is the reason reflexivity means the same thing in the set package as in the
order package, the reason a matrix produced by the graph package can be read
by the algebra package, and the reason an error raised in one domain looks
like an error raised in another.

Nothing in this layer depends on a domain package, and nothing in it depends
on a third party package. It is written against the standard library alone.

## When to use this layer directly

Most programs never import from `discretus.core`. The domain packages expose
the concepts a user of the library wants, and they are built on top of these
abstractions rather than hiding them.

You import from the core layer in three situations. The first is when you
are extending the library, because a new structure should inherit the
behaviour defined here rather than reimplement it. The second is when you
need exact arithmetic on its own, for instance an exact matrix or an exact
polynomial outside any algebraic structure. The third is when you want the
shared utilities, for instance deterministic hashing or the universal total
order, in your own code.

## Module map

| Module | Responsibility |
| --- | --- |
| `element` | What it means to be a member of a structure |
| `frozen` | Immutability mixin, hashable mapping, recursive freeze |
| `comparators` | A universal total order over mixed element types |
| `repr_utils` | Uniform rendering of sets, sequences, mappings, tables |
| `hashing` | Canonical encodings and process independent digests |
| `iterators` | Lazy iteration helpers for the generators |
| `lazy` | Cached property, on demand sequence, unbounded memoization |
| `predicates` | Logical combinators and finite quantifiers |
| `random_base` | Seeded randomness |
| `structure` | The finite structure base class |
| `operation` | A closed binary operation with axiom checks |
| `algebraic_base` | Magma, semigroup, monoid, group, and ring bases |
| `numeric` | Exact integer primitives |
| `bigint` | Digit and base conversions, Karatsuba multiplication |
| `rationals` | Exact rational helpers and continued fractions |
| `vector_base` | Immutable exact vectors |
| `matrix_base` | Immutable exact matrices |
| `polynomial_base` | Dense exact polynomials |
| `modular_base` | Modular arithmetic primitives and residue classes |
| `relation_base` | The binary relation base class |
| `function_base` | The total function base class |
| `order_base` | The order base class |
| `equivalence` | Partition normalization used by the quotient machinery |
| `morphism` | Structure preserving map base |
| `step_recorder` | Recording the intermediate steps of an algorithm |
| `explain` | Turning a routine into a narrated derivation |
| `proof_trace` | Recording a logical derivation line by line |
| `latex_mixin` | Rendering an object as LaTeX |
| `serializable` | Deterministic dictionary and JSON representations |

## Elements

A member of a structure is an ordinary Python value. The only requirement is
that it is hashable, so that it can live in a set and act as a dictionary
key. The helpers here enforce that requirement and make the common
containers usable as members.

### `normalize_element(value, name="element") -> Element`

Return the value when it can be used as a member. A list becomes a tuple, a
set becomes a frozen set, and a mapping becomes a sorted tuple of pairs,
recursively, because a reader who writes a set of sets in mathematical
notation means exactly that. A value that cannot be made hashable raises
`ValidationError`.

```python
>>> from discretus.core.element import normalize_element
>>> normalize_element([1, 2])
(1, 2)
>>> sorted(normalize_element({1, 2}))
[1, 2]
```

### `normalize_elements(values, name="element") -> List[Element]`

Normalize every member of an iterable, preserving order.

### `as_frozenset(values, name="element") -> FrozenSet[Element]`

Normalize and collect into a frozen set, which is the representation the set
package uses internally.

### `Labeled(value, label)`

A hashable value that carries a display label. Equality and hashing use the
value, so relabelling does not change identity, and printing uses the label.
It is what makes a Cayley graph readable, where the vertices are group
elements that should print as `r`, `rs`, and so on rather than as tuples.

```python
>>> from discretus.core.element import Labeled
>>> r = Labeled((0, 1), "r")
>>> str(r), r == Labeled((0, 1), "rotation")
('r', True)
```

### `element_repr(value) -> str`

Render a member in the library's uniform style. A frozen set prints in brace
notation with its members in display order, so two equal sets always render
identically.

## Immutability

### `FrozenMixin`

Reject attribute assignment after construction. A subclass sets its state
through `_initialize` inside its own constructor and is immutable from then
on. Assignment afterwards raises `StructureError`, which is a deliberate
choice: a silent mutation of a value type would invalidate its hash and
corrupt any set it belongs to.

### `FrozenDict(data=None, **extra)`

A hashable read only mapping with deterministic iteration order. Two
mappings built in different orders are equal and hash alike, so a frozen
mapping can itself be a member of a set. `with_entry` and `without` return
modified copies.

### `freeze(value) -> Any`

Recursively convert a nested container into its immutable counterpart.

## Deterministic ordering

Python randomizes string hashing between processes, so iterating a set and
returning the result would produce different output on different runs. The
library never does that: anything it returns in an order is sorted through
this module.

### `universal_key(value) -> Tuple[Any, ...]`

Return a sort key that totally orders arbitrary members. Numbers sort
numerically before strings, strings lexicographically, tuples component by
component, sets by size and then by their sorted members, and anything else
by type name and representation. The order never consults a hash value.

```python
>>> from discretus.core.comparators import sorted_elements
>>> sorted_elements([3, "a", 1, (2,), (1, 0)])
[1, 3, 'a', (1, 0), (2,)]
```

### `sorted_elements(values) -> List[Any]`

Sort by `universal_key`.

### `compare(left, right) -> int`

Return minus one, zero, or one in the universal order.

### `lexicographic(left, right) -> int`

Compare two sequences component by component, with a proper prefix preceding
the longer sequence.

### `by_key(key)`, `reverse_comparator(comparator)`, `is_sorted(values, strict=False)`

Comparator construction and inspection.

## Deterministic hashing

### `canonical_bytes(value) -> bytes`

A canonical byte encoding of a nested immutable value, prefixed by a type
tag so that `1`, `"1"`, and `(1,)` never collide, with unordered containers
encoded by sorting their members' encodings.

### `stable_hash(value) -> int` and `stable_digest(value) -> str`

A sixty four bit hash and a hexadecimal digest that are identical across
processes and machines. These are what a canonical form, an on disk cache,
or a structural fingerprint needs, and what the built-in `hash` cannot
provide.

### `combine_hashes(*values)` and `hash_unordered(values)`

Order sensitive and order insensitive combination of hash values.

## Iteration and laziness

`iterators` provides `take`, `drop`, `first`, `nth`, `chunked`, `windowed`,
`pairwise`, `unique`, `interleave`, `count_items`, `exhaust`,
`repeat_apply`, and `sorted_unique`. None of them materializes its input
unless its documentation says so, which is what allows the combinatorial
generators to iterate over spaces that cannot be held in memory.

`lazy` provides four things.

`cached_property` computes a value once per instance and stores it in the
instance dictionary, so later reads cost a lookup.

`LazySequence(generator, length=None)` is an indexable sequence whose terms
are produced on demand and cached, with `length=None` for a conceptually
infinite sequence such as the primes or the Catalan numbers.

```python
>>> from discretus.core.lazy import LazySequence
>>> squares = LazySequence(lambda n: n * n)
>>> squares[4], squares.prefix(5)
(16, [0, 1, 4, 9, 16])
```

`LazyMapping(function)` is the same idea for a mapping.

`memoized_recursion(function)` memoizes a recursive function on its
positional arguments with an unbounded cache, which suits the recurrences in
this library where the argument space is small and every value is reused.

## Predicates

`predicates` provides `always`, `never`, `negate`, `conjoin`, `disjoin`,
`implies`, `equivalent`, `exclusive`, `for_all`, `exists`, `exactly_one`,
`count_satisfying`, and `restrict`. The empty conjunction is true and the
empty disjunction is false, matching the mathematical convention, and
`for_all` and `exists` are the finite quantifiers with the same convention.

A partial order defined by a rule, a set defined by a membership test, and a
relation filtered by a property all compose through these combinators rather
than through ad hoc lambdas.

## Seeded randomness

Every randomized routine in the library routes its randomness through this
module, and the library never touches the global random state, so it can
neither perturb nor be perturbed by the randomness your own program uses.

### `rng(seed=None) -> random.Random`

An independent generator seeded by the argument, or by
`Config.default_seed` when the argument is `None`.

### `SeededRandom(seed=None)`

A small explicit interface over a seeded generator, exposing `integer`,
`unit`, `bernoulli`, `choice`, `sample`, `shuffled`, and `permutation`. The
surface is deliberately narrow so that the randomized routines are easy to
audit for reproducibility.

### `deterministic_sample(population, size, seed=None)` and `deterministic_shuffle(population, seed=None)`

Convenience wrappers for the two operations the library needs most.

## Structures

### `Structure`

The abstract base of every finite discrete structure. A subclass provides
`elements`, which returns the carrier set in deterministic order, and
inherits everything else: `order`, `cardinality`, `is_empty`, `contains`,
`require_member`, `index_of`, `to_dict`, `signature`, membership through
`in`, iteration, length, equality by content, and hashing.

Because the base defines them once, every structure in the library agrees on
what its size is called, how it decides membership, and when two structures
are equal.

### `FiniteStructure(elements, sort=True)`

A structure whose carrier is given explicitly. Duplicates are removed and
the order is normalized, so two structures built from the same members
compare equal. Pass `sort=False` to preserve the given order, which matters
for a structure such as a permutation group where a natural indexing already
exists.

## Binary operations

### `BinaryOperation(carrier, function, symbol="*", check_closure=True)`

A closed binary operation on a finite carrier set, and the computational
heart of the algebra package. Every axiom that a group, a ring, or a lattice
has to satisfy is checked here once.

| Method | Meaning | Complexity |
| --- | --- | --- |
| `apply(left, right)` | Apply the operation, memoized | O(1) after first call |
| `verify_closure()` | Raise when a product leaves the carrier | O(n squared) |
| `is_associative()` | Whether the operation is associative | O(n cubed) |
| `associativity_counterexample()` | A violating triple, or `None` | O(n cubed) |
| `is_commutative()` | Whether the operation commutes | O(n squared) |
| `commutativity_counterexample()` | A violating pair, or `None` | O(n squared) |
| `is_idempotent()` | Whether every member is its own product | O(n) |
| `identity()` | The two sided identity, or `None` | O(n squared) |
| `require_identity()` | The identity, raising when absent | O(n squared) |
| `inverse(element)` | The two sided inverse, or `None` | O(n) |
| `inverses()` | Every inverse | O(n squared) |
| `has_inverses()` | Whether every member is invertible | O(n squared) |
| `is_group()` | Closure, associativity, and inverses | O(n cubed) |
| `table()` | The operation as a mapping from pairs | O(n squared) |
| `rows()` | The Cayley table as a list of rows | O(n squared) |
| `cayley_table()` | The Cayley table rendered as text | O(n squared) |
| `is_latin_square()` | Whether rows and columns are permutations | O(n squared) |
| `restricted(subset)` | The operation on a closed subset | O(m squared) |

```python
>>> from discretus.core.operation import BinaryOperation
>>> plus = BinaryOperation([0, 1, 2], lambda a, b: (a + b) % 3, symbol="+")
>>> plus.identity(), plus.inverse(1), plus.is_group()
(0, 2, True)
>>> print(plus.cayley_table())
+ | 0 | 1 | 2
--+---+---+--
0 | 0 | 1 | 2
1 | 1 | 2 | 0
2 | 2 | 0 | 1
```

### `operation_from_table(carrier, rows, symbol="*")`

Build an operation from an explicit Cayley table, which is how a structure
defined by exhibiting its table is entered.

## The algebraic hierarchy

The classes form the standard chain of successively stronger axioms, and
each one verifies exactly the axioms it adds, so a subclass never repeats a
check its parent performed. Verification happens on construction by default,
which means an instance satisfies its axioms for its whole lifetime.

| Class | Axioms |
| --- | --- |
| `Magma` | Closure |
| `Semigroup` | Closure, associativity |
| `Monoid` | Closure, associativity, identity |
| `GroupBase` | Closure, associativity, identity, inverses |
| `RingBase` | Additive abelian group, multiplicative monoid, distributivity |

`Semigroup` adds `power`, computed by repeated squaring in a logarithmic
number of applications. `Monoid` adds `identity`, a `power` that accepts
zero, and `units`. `GroupBase` adds `inverse`, a `power` that accepts
negative exponents, `element_order`, `element_orders`, and `commutator`.
`RingBase` adds `add`, `multiply`, `zero`, `one`, `negate`, `subtract`, and
`is_commutative`, and its verification includes distributivity in both
directions, which costs cubic time in the carrier size.

An axiom failure raises `AxiomViolationError`, naming the axiom and, where
one exists, the counterexample.

```python
>>> from discretus.core.algebraic_base import GroupBase
>>> g = GroupBase([0, 1, 2, 3], lambda a, b: (a + b) % 4, symbol="+")
>>> g.inverse(1), g.element_order(1), g.is_abelian()
(3, 4, True)
```

## Exact integers

`numeric` provides the integer primitives, all free of floating point so
that results hold for inputs of any size: `sign`, `product`, `ceil_div`,
`floor_div`, `integer_sqrt`, `is_perfect_square`, `integer_nth_root`,
`is_perfect_power`, `integer_log`, `exact_divide`, `clamp`,
`next_power_of_two`, `is_power_of_two`, `bit_count`, `triangular`, and
`divisor_pairs`.

`integer_nth_root` uses integer Newton iteration and then corrects the
result by at most one step in each direction, so it is exact rather than
nearly exact, which a floating point root is not for large inputs.

```python
>>> from discretus.core.numeric import integer_nth_root, is_perfect_power
>>> integer_nth_root(10 ** 30, 3)
1000000000
>>> is_perfect_power(64)
(2, 6)
```

`bigint` provides the digit level utilities: `digits`, `from_digits`,
`to_base`, `from_base`, `digit_sum`, `digital_root`, `digit_count`,
`reverse_digits`, `is_palindrome`, and `karatsuba_multiply`. The last is a
transparent reference implementation of the divide and conquer recurrence
whose solution is about O(n to the power 1.585); it exists to be read, and it
falls back to the built-in multiplication below its threshold.

## Exact rationals

`rationals` converts into and out of exact fractions and renders them:
`as_fraction`, `as_fractions`, `common_denominator`, `clear_denominators`,
`mediant`, `harmonic_number`, `fraction_to_latex`, `fraction_to_text`,
`continued_fraction_of`, `from_continued_fraction`, and
`best_approximation`.

```python
>>> from discretus.core.rationals import continued_fraction_of, harmonic_number
>>> continued_fraction_of("415/93")
[4, 2, 6, 7]
>>> harmonic_number(4)
Fraction(25, 12)
```

## Exact linear algebra

### `VectorBase(entries)`

An immutable vector of exact rational entries, with `zero`, `unit`, `add`,
`subtract`, `scale`, `negate`, `dot`, `norm_squared`, `is_zero`,
`is_orthogonal_to`, and `normalized_by_first`, plus the arithmetic
operators. The squared norm is returned rather than the norm, because the
square root is irrational in general and the library does not silently
introduce an approximation. Normalizing by the first nonzero entry is the
exact substitute, and it is what the library uses to compare eigenvectors
and kernel bases.

### `MatrixBase(rows)`

An immutable matrix of exact rational entries.

| Group | Members |
| --- | --- |
| Construction | `zero`, `identity`, `diagonal`, `from_columns` |
| Shape | `shape`, `row_count`, `column_count`, `is_square` |
| Access | `entry`, `row`, `column`, `with_entry`, indexing |
| Arithmetic | `add`, `subtract`, `scale`, `multiply`, `apply`, `power` |
| Structure | `transpose`, `trace`, `submatrix`, `is_symmetric`, `is_diagonal`, `is_identity` |
| Row operations | `swap_rows`, `scale_row`, `add_row_multiple` |
| Rendering | `to_latex`, `to_text` |

`power` uses repeated squaring, which is what makes matrix exponentiation a
practical way to evaluate a linear recurrence at a distant index.

```python
>>> from discretus.core.matrix_base import MatrixBase
>>> MatrixBase([[1, 1], [1, 0]]).power(10)
MatrixBase([[89, 55], [55, 34]])
```

The entry in the corner is the Fibonacci number at index ten, which is the
identity that the recurrence package relies on.

### `PolynomialBase(coefficients, variable="x")`

A dense polynomial with exact coefficients, stored from the constant term
upward so that the index matches the exponent, and normalized so that the
leading coefficient is nonzero. The zero polynomial has an empty
coefficient tuple and degree minus one.

Construction: `zero`, `one`, `monomial`, `from_roots`. Access: `degree`,
`coefficient`, `leading_coefficient`, `is_zero`, `is_constant`, `is_monic`.
Arithmetic: `add`, `subtract`, `scale`, `multiply`, `power`, `divmod`,
`evaluate`, `compose`, `derivative`, `monic`. Rendering: `to_text`,
`to_latex`.

Long division satisfies the identity that defines it exactly, with a
remainder of smaller degree than the divisor.

```python
>>> from discretus.core.polynomial_base import PolynomialBase
>>> p = PolynomialBase([-1, 0, 0, 1])
>>> divmod(p, PolynomialBase([-1, 1]))
(PolynomialBase(x^2 + x + 1), PolynomialBase(0))
```

## Modular arithmetic

The number theory package exposes the documented public interface for
modular arithmetic. The primitives live here because the algebra package
needs them too, for modular integer rings, prime fields, and modular
matrices, and two copies would drift apart.

Functions: `normalize`, `mod_add`, `mod_subtract`, `mod_multiply`,
`mod_power`, `extended_euclidean`, `mod_inverse`, `mod_divide`,
`solve_congruence`, `residues`, `units`, `crt_pair`, and `crt`.

`extended_euclidean` returns a triple whose Bezout identity holds exactly,
with a non negative divisor. `mod_inverse` raises `InfeasibleError` when the
argument is not coprime to the modulus, naming the greatest common divisor,
because that is the information a caller needs in order to understand why.
`crt` combines any number of congruences and does not require the moduli to
be coprime, succeeding whenever the system is consistent.

### `ModularInteger(value, modulus)`

A residue class with arithmetic operators, so that modular computation reads
like ordinary arithmetic while the modulus stays attached to the value. Two
residues with different moduli cannot be combined by accident: the attempt
raises `DomainError`.

```python
>>> from discretus.core.modular_base import ModularInteger
>>> a = ModularInteger(7, 5)
>>> a + 4, a * 3, a ** 3, a.inverse()
(ModularInteger(value=1, modulus=5), ModularInteger(value=1, modulus=5), ModularInteger(value=3, modulus=5), ModularInteger(value=3, modulus=5))
>>> ModularInteger(2, 7).order()
3
```

## Relations

### `RelationBase(domain, pairs=(), infer_domain=False)`

A binary relation over a finite ground set, and the base of the relation,
order, and equivalence types in the set package.

Properties: `is_reflexive`, `is_irreflexive`, `is_symmetric`,
`is_antisymmetric`, `is_asymmetric`, `is_transitive`, `is_total`,
`is_equivalence`, `is_partial_order`, `is_preorder`, `is_function`, and
`properties`, which returns them all at once.

Derived relations: `converse`, `complement`, `union`, `intersection`,
`difference`, `compose`, `reflexive_closure`, `symmetric_closure`,
`transitive_closure`, and `equivalence_closure`.

Views: `matrix`, `adjacency`, `image_of`, `preimage_of`.

The transitive closure is Warshall's algorithm over the adjacency matrix,
which costs cubic time in the size of the ground set. The transitivity test
is cheaper, since it only has to find one violating composition.

```python
>>> from discretus.core.relation_base import RelationBase
>>> r = RelationBase(domain={1, 2, 3}, pairs={(1, 2), (2, 3)})
>>> r.is_transitive(), sorted(r.transitive_closure().pairs)
(False, [(1, 2), (1, 3), (2, 3)])
```

## Functions

### `FunctionBase(domain, codomain=None, mapping=None, rule=None)`

A total function between finite sets, given either by a mapping or by a
rule. Totality is checked on construction, so an instance is a genuine
function; a mapping that omits a member of the domain raises
`NotAFunctionError`, and a value outside the codomain raises `DomainError`.

Access: `domain`, `codomain`, `mapping`, `apply`, call syntax, `pairs`.

Properties: `image`, `image_of`, `preimage_of`, `fiber`, `is_injective`,
`is_surjective`, `is_bijective`, `is_identity`, `is_constant`,
`fixed_points`, and `properties`.

Derived functions: `compose`, which applies this function first and raises
when the image leaves the second domain, `inverse`, which raises
`InfeasibleError` with the reason when the function is not bijective, and
`restricted_to`.

```python
>>> from discretus.core.function_base import FunctionBase
>>> f = FunctionBase(domain={1, 2, 3}, rule=lambda n: n % 2)
>>> f(3), f.image(), f.is_surjective(), f.fiber(1)
(1, [0, 1], True, [1, 3])
```

## Transparency

`step_recorder` records the intermediate steps of an algorithm as labelled
entries, `explain` wraps a routine so that it returns its result together
with the recorded derivation, and `proof_trace` records a logical derivation
line by line with its rule and premises so that it can be checked and
printed. Recording is off by default and is controlled globally by
`Config.explain` or locally by the wrapper, because a derivation that nobody
reads is wasted work.

`latex_mixin` gives an object a `to_latex` method and the rich display hook
that notebooks use, so a matrix, a truth table, or a Hasse diagram displays
as typeset mathematics rather than as a repr.

`serializable` gives an object a deterministic dictionary and JSON
representation, which is what makes the interchange formats byte stable.

## Errors raised by this layer

| Exception | Raised when |
| --- | --- |
| `ValidationError` | An argument has the wrong type or shape |
| `DomainError` | A value is outside the mathematical domain |
| `DimensionError` | Two structures have incompatible shapes |
| `StructureError` | An immutable object is assigned to |
| `AxiomViolationError` | A candidate structure fails an axiom it claims |
| `NotAFunctionError` | A mapping used as a function is not total |
| `InfeasibleError` | The requested object does not exist |
| `LimitExceededError` | A configured enumeration limit was reached |

Every one of them derives from `DiscretusError`.

## See also

- [`discretus.sets`](sets.md), which builds its relations, orders, and
  functions on the bases here.
- [`discretus.algebra`](algebra.md), which builds its groups, rings, and
  fields on the operation and hierarchy classes here.
- [`discretus.number_theory`](number_theory.md), which exposes the public
  interface for the modular primitives.
- [`discretus.utils`](utils.md), for the cross cutting helpers that are not
  mathematical abstractions.
