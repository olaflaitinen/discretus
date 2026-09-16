# `discretus.recurrences`

The recurrence package solves recurrence relations and classifies the growth
of the functions they define. It covers linear recurrences with constant
coefficients, the classical sequences that satisfy them, the divide and
conquer recurrences that arise in algorithm analysis, nonlinear iteration,
and asymptotic comparison.

The package answers three different questions that are easy to conflate. The
first is what the value of a term is, which is a computation. The second is
what the closed form of the sequence is, which is algebra. The third is how
fast the sequence grows, which is analysis. Each has its own subpackage, and
the reference states which question a routine answers.

## Mathematical basis

A linear homogeneous recurrence with constant coefficients has the form

$$a_n = c_1 a_{n-1} + c_2 a_{n-2} + \dots + c_k a_{n-k},$$

and its behaviour is governed by the roots of the characteristic equation

$$x^{k} = c_1 x^{k-1} + c_2 x^{k-2} + \dots + c_k.$$

When the roots are distinct the closed form is a linear combination of their
powers, and a root of multiplicity $m$ contributes that power multiplied by
a polynomial of degree $m - 1$. For the Fibonacci sequence the roots are the
golden ratio $\varphi = (1 + \sqrt{5}) / 2$ and its conjugate, and the
closed form is Binet's formula

$$F_n = \frac{\varphi^{n} - (1-\varphi)^{n}}{\sqrt{5}}.$$

A single distant term is best obtained not from the closed form, which
requires irrational arithmetic, but from the matrix formulation

$$\begin{pmatrix} a_{n} \\ a_{n-1} \end{pmatrix}
= \begin{pmatrix} c_1 & c_2 \\ 1 & 0 \end{pmatrix}
\begin{pmatrix} a_{n-1} \\ a_{n-2} \end{pmatrix},$$

whose power is computed by repeated squaring in $O(k^3 \log n)$ exact
operations.

The Master Theorem classifies divide and conquer recurrences
$T(n) = a\,T(n/b) + f(n)$ by comparing $f(n)$ with $n^{\log_b a}$, and the
package reports which of the three cases applies together with the
resulting growth class.

## Module map

| Subpackage | Responsibility |
| --- | --- |
| `sequences` | Classical sequences and arbitrary memoized recursions |
| `linear` | Characteristic equations, closed forms, matrix methods |
| `master_theorem` | The Master Theorem, Akra Bazzi, recursion trees |
| `divide_conquer` | Cost models and analysis of divide and conquer algorithms |
| `nonlinear` | Fixed points, iteration, the logistic map |
| `asymptotic` | Growth classes and their comparison |

## Classical sequences

| Routine | Sequence | Recurrence |
| --- | --- | --- |
| `fibonacci(n)` | Fibonacci numbers | Sum of the two preceding terms |
| `lucas(n)` | Lucas numbers | The same recurrence, different start |
| `pell(n)` | Pell numbers | Twice the previous plus the one before |
| `jacobsthal(n)` | Jacobsthal numbers | Previous plus twice the one before |
| `tribonacci(n)` | Tribonacci numbers | Sum of the three preceding terms |
| `factorial_sequence(n)` | Factorials | The index times the previous term |
| `custom_recursive(coefficients, initial, n)` | Any linear recurrence | As given |
| `memoized(function)` | Any recursion, memoized | As written |

```python
>>> from discretus.recurrences.sequences import fibonacci, lucas, pell
>>> [fibonacci(n) for n in range(10)]
[0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
>>> fibonacci(200)
280571172992510140037611932413038677189525
>>> lucas(20), pell(10)
(15127, 2378)
```

Each routine chooses its method by the index. A small index is computed by
iteration, which is linear and has a tiny constant. A large index is
computed by matrix exponentiation, which is logarithmic in the index. The
threshold is documented, both methods are public, and the suite asserts that
they agree, which is the standard pattern in this library for a routine that
dispatches.

The identities these sequences satisfy are checkable and are checked. The
Lucas numbers relate to the Fibonacci numbers by $L_n = F_{n-1} + F_{n+1}$,
consecutive Fibonacci numbers are coprime, and the Cassini identity
$F_{n-1} F_{n+1} - F_n^2 = (-1)^n$ holds for every index. The suite asserts
all three, which pins the sequences far more tightly than a table of the
first twenty terms would.

## Linear recurrences

| Routine | Answers |
| --- | --- |
| `characteristic_polynomial(coefficients)` | The characteristic equation |
| `characteristic_roots(coefficients)` | Its roots, exactly where possible |
| `solve_homogeneous(coefficients, initial)` | The closed form of a homogeneous recurrence |
| `solve_nonhomogeneous(coefficients, initial, forcing)` | The closed form with a forcing term |
| `solve_linear_recurrence(coefficients, initial, n)` | The term at an index |
| `matrix_form(coefficients)` | The companion matrix |
| `matrix_exponentiation(coefficients, initial, n)` | A distant term by matrix power |
| `generating_function_solver(coefficients, initial)` | The rational generating function |

```python
>>> from discretus.recurrences.linear import (
...     characteristic_polynomial, matrix_exponentiation, solve_linear_recurrence,
... )
>>> solve_linear_recurrence(coefficients=[1, 1], initial=[0, 1], n=10)
55
>>> matrix_exponentiation([1, 1], [0, 1], 90)
2880067194370816120
>>> characteristic_polynomial([1, 1]).to_text()
'x^2 - x - 1'
```

The coefficient convention is the one in the definition above: the first
coefficient multiplies the immediately preceding term. The initial values
are given in increasing index order. Both are stated in every docstring in
the subpackage, because the opposite convention is equally common in the
literature and a silent mismatch produces a plausible wrong answer.

The closed form is returned as a structured object rather than as a string:
it reports the roots, their multiplicities, and the coefficient of each
term, and it can evaluate itself at an index and render itself to LaTeX.
That matters because the coefficients are exact rationals and the roots may
be irrational, so a string would either lose the exactness or be unusable.

The generating function solver returns the rational function whose Taylor
coefficients are the sequence, which connects this package to the formal
power series in [`discretus.combinatorics`](combinatorics.md). For the
Fibonacci sequence it returns $x / (1 - x - x^2)$, and expanding that series
reproduces the terms, which the suite asserts.

## The Master Theorem

| Routine | Answers |
| --- | --- |
| `master_theorem(a, b, f_exponent, log_power=0)` | The case and the growth class |
| `akra_bazzi(coefficients, fractions, f_exponent)` | The Akra Bazzi exponent |
| `recursion_tree(a, b, f_exponent, depth)` | The cost per level |
| `substitution_check(recurrence, guess)` | Whether a guess satisfies the recurrence |
| `complexity_class(expression)` | The growth class of an expression |

```python
>>> from discretus.recurrences.master_theorem import master_theorem
>>> master_theorem(a=2, b=2, f_exponent=1)
MasterTheoremResult(case=2, growth='n log n', critical_exponent=Fraction(1, 1))
>>> master_theorem(a=8, b=2, f_exponent=2)
MasterTheoremResult(case=1, growth='n^3', critical_exponent=Fraction(3, 1))
>>> master_theorem(a=2, b=2, f_exponent=2)
MasterTheoremResult(case=3, growth='n^2', critical_exponent=Fraction(1, 1))
```

The result reports the case as well as the bound, because the case is the
part a reader is trying to learn: the first case is where the recursion
dominates, the second is where the two balance and the logarithmic factor
appears, and the third is where the work at the top dominates. The critical
exponent is $\log_b a$, returned as an exact rational so that the comparison
with the exponent of the forcing function is exact rather than a floating
point near miss.

The three worked examples above are the three canonical ones: binary
search's sibling with linear merging gives $n \log n$, eight subproblems of
half size with quadratic work gives the cube, and two subproblems of half
size with quadratic work is dominated by the top level.

`akra_bazzi` handles the recurrences the Master Theorem cannot, where the
subproblems are of different sizes, by solving for the exponent that makes
the weighted sum of the fractions equal one. `recursion_tree` reports the
cost at each level and the number of nodes, which is the picture that makes
the three cases obvious.

## Divide and conquer analysis

| Routine | Meaning |
| --- | --- |
| `analyze(a, b, f_exponent)` | The full analysis, with the method used |
| `CostModel(split, combine, base)` | A parametrized cost model |
| `known_examples()` | The classical recurrences with their solutions |

`known_examples` returns the recurrences a reader will meet, with their
parameters and their solutions: binary search, merge sort, Karatsuba
multiplication, Strassen multiplication, the closest pair of points, and the
median of medians selection. Having them as data rather than as prose means
they can be used as test fixtures, and the suite does exactly that: every
example is passed through `master_theorem` and the reported class is
compared with the known answer.

## Nonlinear recurrences

| Routine | Meaning |
| --- | --- |
| `iterate(function, start, steps)` | The orbit of a point |
| `fixed_points(function, candidates)` | The points a function fixes |
| `is_attracting(function, point, epsilon)` | Local stability of a fixed point |
| `logistic_map(rate, start, steps)` | The orbit of the logistic map |
| `period_of(orbit)` | The eventual period of an orbit |

Nonlinear recurrences have no general closed form, so this subpackage
computes and classifies rather than solving. The logistic map is included
because it is the standard demonstration that a simple recurrence can be
chaotic: at a rate below three the orbit converges, above it the orbit
doubles its period repeatedly, and beyond the accumulation point it is
aperiodic. The orbit is computed with exact rationals when the rate and the
start are rational, which makes the period detection exact rather than a
consequence of rounding.

## Asymptotic comparison

| Routine | Meaning |
| --- | --- |
| `big_o(f, g, limit)` | Whether f is O of g, on the sampled range |
| `big_omega(f, g, limit)` | Whether f is Omega of g |
| `big_theta(f, g, limit)` | Whether f is Theta of g |
| `growth_class(expression)` | The class of a symbolic expression |
| `compare_growth(left, right)` | Which of two classes dominates |
| `GROWTH_HIERARCHY` | The standard chain of classes |

These routines are honest about what they do, which is worth emphasizing.
Deciding an asymptotic relation between arbitrary functions is not
computable, so `big_o` and its siblings sample the functions over a range
and report whether the relation held there, with the range in the result.
They are a sanity check and a teaching aid, not a proof. `growth_class` and
`compare_growth` work symbolically on the standard hierarchy, from constant
through logarithmic, linear, linearithmic, polynomial, exponential, and
factorial, and those comparisons are exact because the hierarchy is known.

```python
>>> from discretus.recurrences.asymptotic import compare_growth, growth_class
>>> growth_class("n log n")
GrowthClass.LINEARITHMIC
>>> compare_growth("n^2", "2^n")
-1
```

## Choosing a method for a linear recurrence

Four routines can give you a term of a linear recurrence, and the right
choice depends entirely on what you are going to do with it.

**Iteration**, through `solve_linear_recurrence` with a small index or
through the sequence routines, is the right choice when you want many
consecutive terms. It computes each one from its predecessors, so producing
the first thousand terms costs one pass rather than a thousand separate
solves.

**Matrix exponentiation** is the right choice for a single distant term. The
cost is logarithmic in the index, so the millionth Fibonacci number is a few
dozen matrix multiplications rather than a million additions. The result is
exact, which distinguishes it from the closed form.

**The closed form**, from `solve_homogeneous`, is the right choice when you
want to reason about the sequence rather than evaluate it: to see which root
dominates, to read off the growth rate, or to present the solution. It is
the algebraic answer, and evaluating it at a large index would require
irrational arithmetic, which is why it is not the evaluation path.

**The generating function**, from `generating_function_solver`, is the right
choice when the recurrence is one step in a larger manipulation, because a
rational generating function can be added, multiplied, and composed with
others before any coefficient is extracted.

```python
from discretus.recurrences.linear import (
    generating_function_solver,
    matrix_exponentiation,
    solve_homogeneous,
    solve_linear_recurrence,
)

coefficients, initial = [1, 1], [0, 1]

first_twenty = [solve_linear_recurrence(coefficients, initial, n) for n in range(20)]
distant = matrix_exponentiation(coefficients, initial, 1_000_000)
closed = solve_homogeneous(coefficients, initial)
series = generating_function_solver(coefficients, initial)

print(first_twenty[:10])
print(distant.bit_length(), "bits")
print(closed.to_latex())
print(series.coefficients(10))
```

## Worked example: analysing an algorithm end to end

The package is most useful when the three questions are asked together, and
the following does that for merge sort.

Merge sort splits its input in half, sorts both halves, and merges them in
linear time, so its cost satisfies $T(n) = 2\,T(n/2) + \Theta(n)$. The
Master Theorem classifies it, the recursion tree shows why, and a direct
count confirms the prediction.

```python
from discretus.recurrences.master_theorem import master_theorem, recursion_tree

result = master_theorem(a=2, b=2, f_exponent=1)
print(result.case, result.growth, result.critical_exponent)

for level in recursion_tree(a=2, b=2, f_exponent=1, depth=5):
    print(level.index, level.node_count, level.cost_per_node, level.total_cost)
```

The tree makes the second case visible: every level costs the same, there
are logarithmically many levels, and the product is the reported bound. That
is the entire content of the case, and reading it off a table is more
convincing than being told.

Now confirm it by measurement rather than by trust. Counting comparisons is
exact and machine independent, which makes it a better check than timing.

```python
comparisons = 0


def merge_sort(values):
    global comparisons
    if len(values) <= 1:
        return values
    middle = len(values) // 2
    left, right = merge_sort(values[:middle]), merge_sort(values[middle:])
    merged, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        comparisons += 1
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    return merged + left[i:] + right[j:]


from discretus.core.random_base import SeededRandom

source = SeededRandom(2026)
for size in (256, 512, 1024, 2048):
    comparisons = 0
    merge_sort(source.shuffled(range(size)))
    ratio = comparisons / (size * (size.bit_length() - 1))
    print(size, comparisons, round(ratio, 3))
```

The ratio of the comparison count to $n \log_2 n$ settles near a constant,
which is what the second case predicts. If it drifted upward with the size,
the prediction would be wrong, and that is the point of running it: an
asymptotic claim is a claim about a trend, and a trend is something you can
observe.

The same three steps apply to any divide and conquer algorithm. Karatsuba
multiplication has three subproblems of half size with linear combination,
so `master_theorem(a=3, b=2, f_exponent=1)` reports the first case and the
exponent $\log_2 3$, which is the bound cited for the implementation in
`discretus.core.bigint`. Strassen multiplication has seven subproblems of
half size with quadratic combination, giving $\log_2 7$, and the closest pair
of points has two subproblems of half size with linearithmic combination,
which is the case the plain theorem cannot express and `akra_bazzi` can.

## Complexity summary

| Routine | Complexity |
| --- | --- |
| Iterative evaluation of a k term recurrence to index n | O(n k) additions |
| Matrix exponentiation to index n | O(k cubed log n) exact operations |
| Characteristic polynomial | O(k) |
| Characteristic roots | Exact for degree at most four, numeric above |
| Closed form evaluation | O(k) per index |
| Generating function solution | O(k squared) |
| Master Theorem | O(1) |
| Akra Bazzi | O(iterations of the exponent search) |
| Recursion tree to depth d | O(d) |
| Orbit of length m | O(m) applications |

The two entries worth comparing are the first two. Evaluating a recurrence
iteratively costs a number of additions proportional to the index, and those
additions are on integers that grow linearly in the index, so the real cost
is quadratic in the number of digits. Matrix exponentiation costs a
logarithmic number of matrix multiplications, which is dramatically better
for a distant index and worse for a near one because of the constant factor.
The dispatch in `fibonacci` exists for exactly this reason.

## Errors

| Exception | Raised when |
| --- | --- |
| `DomainError` | A negative index, a base of one or less in a divide and conquer recurrence |
| `ValidationError` | The initial value count does not match the coefficient count |
| `InfeasibleError` | No closed form exists in the form requested |
| `ConvergenceError` | An iterative fixed point search did not converge |
| `LimitExceededError` | An orbit or an enumeration exceeded the configured limit |

The mismatch between initial values and coefficients is the most common
error in this package, and the message states both counts, because a
recurrence of order three needs exactly three initial values and the
off by one is easy to make.

## Design notes

**Three questions, three subpackages.** Computing a term, finding a closed
form, and classifying growth are different problems with different costs and
different failure modes. Keeping them apart means a routine's name says
which one it answers, and a caller who only wants a term does not pay for an
algebraic solution.

**Exactness through the rationals.** Coefficients, initial values, and the
critical exponent of the Master Theorem are exact rationals. A closed form
whose roots are irrational keeps the roots symbolically rather than
evaluating them, so the reported form is correct rather than approximately
correct.

**Dispatch is documented and both methods stay public.** `fibonacci` chooses
between iteration and matrix exponentiation, and both remain available
because a reader studying the matrix method wants to call it directly and a
benchmark wants to compare them.

**Asymptotic sampling is labelled as sampling.** A routine that cannot
decide a relation in general says so in its docstring and returns the range
it sampled. The alternative, a confident answer that is sometimes wrong,
would be worse than no routine at all.

## Conventions in this package

Three conventions are fixed throughout the package, and each is the opposite
of a convention used elsewhere in the literature, so they are worth stating
once rather than looking up at every call.

**Coefficient order.** The coefficient list starts with the one multiplying
the immediately preceding term. For the Fibonacci recurrence, where each
term is the sum of the two before it, the list is one and one; for a
recurrence in which the term two back is doubled, the list is zero and two.
The opposite order, starting from the oldest term, appears often enough that
a silent mismatch would produce a plausible wrong sequence, which is why
every docstring in the subpackage repeats the convention.

**Initial value order.** Initial values are given in increasing index order,
so the first entry is the term at index zero. A recurrence of order three
needs exactly three of them, and a mismatch between the two lengths raises
`ValidationError` with both counts, because the off by one is the most
common mistake here.

**Index base.** Sequences are indexed from zero, and the Fibonacci sequence
therefore starts at zero rather than at one. That is the convention that
makes the identities in the documentation hold as written, including
Cassini's identity and the divisibility properties, and it is the one the
combinatorics package uses as well.

## See also

- [`discretus.combinatorics`](combinatorics.md), for the generating
  functions and the sequences that satisfy these recurrences.
- [`discretus.core`](core.md), for the exact matrices the matrix method uses
  and the exact rationals the closed forms carry.
- [`discretus.algebra`](algebra.md), for the polynomial arithmetic behind
  the characteristic equation.
- [`discretus.number_theory`](number_theory.md), for the divisibility
  properties of the Fibonacci and Lucas sequences.
