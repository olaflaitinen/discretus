# `discretus.number_theory`

The number theory package computes over arbitrary precision integers
throughout. It covers greatest common divisors, modular arithmetic,
primality testing, factorization, the arithmetic functions, diophantine
equations, classical integer sequences, and a set of teaching
implementations of the number theoretic cryptosystems.

Exactness is not a convenience here, it is the subject. Every routine in
this package returns an exact integer or an exact rational, and none of them
uses a floating point intermediate, because a float has fifty three bits of
mantissa and the questions in this package regularly involve numbers with
thousands of bits.

## Mathematical basis

The Euclidean algorithm computes the greatest common divisor, and its
extended form additionally returns Bezout coefficients with

$$a x + b y = \gcd(a, b).$$

Euler's theorem states that if $\gcd(a, n) = 1$ then

$$a^{\varphi(n)} \equiv 1 \pmod{n},$$

where $\varphi$ is the Euler totient, and Fermat's little theorem is the
special case in which $n$ is prime. The Chinese remainder theorem guarantees
a unique solution modulo $\prod_i n_i$ to a system

$$x \equiv a_i \pmod{n_i}, \quad i = 1, \dots, k,$$

when the moduli are pairwise coprime, and the library's implementation
succeeds more generally, whenever the system is consistent.

The fundamental theorem of arithmetic states that every integer greater than
one factors uniquely into primes up to order,

$$n = \prod_{i=1}^{k} p_i^{\,e_i}, \qquad p_1 < p_2 < \dots < p_k,$$

and the prime number theorem describes their density,
$\pi(x) \sim x / \ln x$, which the prime counting routines are consistent
with.

## Module map

| Subpackage | Responsibility |
| --- | --- |
| `gcd` | Greatest common divisors, Bezout coefficients, least common multiples |
| `modular` | Modular arithmetic, congruences, residues, discrete logarithms |
| `primes` | Primality tests, sieves, prime counting, prime gaps |
| `factorization` | Integer factorization, from trial division to a quadratic sieve |
| `functions` | The arithmetic functions and Dirichlet convolution |
| `diophantine` | Linear equations, Pythagorean triples, Pell, continued fractions |
| `sequences` | Perfect, amicable, Mersenne, Fermat numbers, Farey, Stern Brocot |
| `crypto` | Teaching implementations of RSA, ElGamal, Diffie Hellman |

## Greatest common divisors

| Routine | Meaning | Complexity |
| --- | --- | --- |
| `gcd(a, b)` | The greatest common divisor | O(log min(a, b)) divisions |
| `gcd_multiple(values)` | The divisor of several integers | O(k log max) |
| `extended_gcd(a, b)` | The divisor with Bezout coefficients | O(log min(a, b)) |
| `bezout(a, b)` | The coefficients alone | O(log min(a, b)) |
| `binary_gcd(a, b)` | Stein's algorithm, shifts instead of divisions | O(log squared) bit operations |
| `lcm(a, b)`, `lcm_multiple(values)` | Least common multiples | As the divisor |
| `are_coprime(a, b)` | Whether the divisor is one | As the divisor |

```python
>>> from discretus.number_theory.gcd import extended_gcd, gcd, lcm
>>> gcd(462, 1071), lcm(4, 6)
(21, 12)
>>> g, x, y = extended_gcd(462, 1071)
>>> g, 462 * x + 1071 * y
(21, 21)
```

The Bezout coefficients returned are not unique, and the library returns the
pair the algorithm produces rather than a normalized pair, which is
documented so that a caller who needs a specific representative can adjust
by the usual multiple of the quotients. The identity itself always holds
exactly, and the suite asserts it on randomized inputs.

`binary_gcd` exists because it is instructive: it replaces division with
subtraction and shifting, which was a real advantage on hardware without a
divider. It is validated against `gcd` and is not faster in Python, and the
documentation says so.

## Modular arithmetic

| Routine | Meaning | Complexity |
| --- | --- | --- |
| `mod_add`, `mod_subtract`, `mod_multiply` | Residue arithmetic | O(1) on machine sized inputs |
| `mod_exp(base, exponent, modulus)` | Modular power by square and multiply | O(log exponent) multiplications |
| `mod_inverse(value, modulus)` | The multiplicative inverse | O(log modulus) |
| `mod_divide(a, b, modulus)` | Quotient of residues | O(log modulus) |
| `solve_congruence(a, b, modulus)` | The solution set of a linear congruence | O(log modulus) |
| `crt(values, moduli)` | The Chinese remainder theorem | O(k log max modulus) |
| `mod_sqrt(value, modulus)` | A modular square root | O(log squared p) |
| `tonelli_shanks(value, prime)` | The square root algorithm | O(log squared p) |
| `quadratic_residues(modulus)` | The residues that are squares | O(modulus) |
| `legendre(value, prime)` | The Legendre symbol | O(log p) |
| `jacobi(value, modulus)` | The Jacobi symbol | O(log modulus) |
| `discrete_log(base, target, modulus)` | The discrete logarithm | O(square root of modulus) |
| `baby_step_giant_step(base, target, modulus)` | The same, by the meet in the middle | O(square root of modulus) |
| `multiplicative_order(value, modulus)` | The order of a unit | O(divisors of the totient) |

```python
>>> from discretus.number_theory.modular import crt, mod_exp, mod_inverse
>>> mod_inverse(3, 11), mod_exp(7, 128, 13)
(4, 3)
>>> crt([2, 3, 2], [3, 5, 7])
(23, 105)
```

`mod_inverse` raises `InfeasibleError` when the argument is not coprime to
the modulus, and the message names the greatest common divisor, because that
is the information a caller needs. `crt` returns both the residue and the
combined modulus, since the residue alone is meaningless.

The Legendre and Jacobi symbols deserve a note about what they decide. The
Legendre symbol is defined for an odd prime and tells you exactly whether
the argument is a quadratic residue. The Jacobi symbol generalizes it to an
odd composite modulus, and a value of one no longer implies that the
argument is a residue. The documentation says so at both call sites, because
confusing the two is the classic error in this area.

## Primality

| Routine | Method | Complexity |
| --- | --- | --- |
| `is_prime(n)` | Dispatches by size | See below |
| `trial_division(n)` | Divide by candidates up to the square root | O(square root of n) |
| `fermat_test(n, rounds, seed=None)` | Fermat's little theorem as a test | O(rounds log cubed n) |
| `miller_rabin(n, rounds=None, seed=None)` | Strong probable prime test | O(rounds log cubed n) |
| `solovay_strassen(n, rounds, seed=None)` | Euler probable prime test | O(rounds log cubed n) |
| `aks(n)` | A reference deterministic polynomial time test | Polynomial but impractical |
| `sieve_eratosthenes(limit)` | Every prime below a limit | O(n log log n) |
| `sieve_atkin(limit)` | The same, by the Atkin sieve | O(n / log log n) |
| `linear_sieve(limit)` | Primes with smallest prime factors | O(n) |
| `segmented_sieve(low, high)` | Primes in an interval | O((high - low) log log high) |
| `primes_up_to(limit)` | Convenience wrapper over a sieve | O(n log log n) |
| `next_prime(n)`, `previous_prime(n)` | The neighbouring primes | O(gap times test cost) |
| `prime_counting(x)` | The number of primes up to x | O(x) sieving |
| `prime_gaps(limit)` | The gaps between consecutive primes | O(n log log n) |

`is_prime` dispatches: small inputs go to trial division, and larger ones go
to Miller Rabin with the witness set that makes the test deterministic below
a documented bound of about three times ten to the twenty fourth power.
Above that bound it is a probabilistic test, and the documentation states
the error bound rather than pretending otherwise.

```python
>>> from discretus.number_theory.primes import is_prime, primes_up_to
>>> is_prime(2_147_483_647)
True
>>> primes_up_to(30)
[2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
```

The Fermat test is included because the Carmichael numbers defeat it, and
that is worth seeing: the smallest of them is five hundred and sixty one,
and the test declares it prime for every base coprime to it. The suite
asserts that Miller Rabin rejects the Carmichael numbers that Fermat
accepts, which is the cleanest demonstration of why the strong test is the
one to use.

The AKS implementation is a reference rather than a tool. It is polynomial
time, which is its significance, and it is far slower than Miller Rabin on
every input anyone will try, which the docstring says plainly.

## Factorization

| Routine | Method | Suitable for |
| --- | --- | --- |
| `factorize(n)` | Dispatches by size and structure | Anything |
| `trial_factor(n)` | Trial division | Small factors |
| `fermat_factor(n)` | Fermat's difference of squares | Factors near the square root |
| `pollard_rho(n, seed=None)` | Cycle detection on a pseudorandom map | Medium factors |
| `pollard_p1(n, bound)` | The p minus one method | Factors with smooth predecessors |
| `ecm(n, curves, seed=None)` | Elliptic curve factorization | Medium to large factors |
| `dixon(n)` | Dixon's random squares | Instructional |
| `quadratic_sieve(n)` | The quadratic sieve | Larger semiprimes |
| `is_smooth(n, bound)` | Whether every factor is below a bound | Smoothness testing |
| `divisors(n)` | Every divisor, sorted | From the factorization |

```python
>>> from discretus.number_theory.factorization import divisors, factorize
>>> factorize(600_851_475_143)
{71: 1, 839: 1, 1471: 1, 6857: 1}
>>> divisors(36)
[1, 2, 3, 4, 6, 9, 12, 18, 36]
```

The factorization is returned as a mapping from prime to exponent, which is
the form the arithmetic functions consume and the form that makes the
fundamental theorem of arithmetic visible. Reconstructing the input from it
is a one line assertion that the suite makes on every randomized case.

`factorize` dispatches rather than committing to one method: it removes small
factors by trial division, checks for a perfect power, and then applies
Pollard's rho with a fallback, which is the standard practical ordering. The
individual methods remain available because each one is instructive and
because each has inputs on which it is the right choice.

## Arithmetic functions

| Routine | Definition |
| --- | --- |
| `euler_totient(n)` | The count of integers up to n coprime to n |
| `mobius(n)` | Zero on non squarefree n, otherwise minus one to the number of prime factors |
| `divisor_count(n)` | The number of divisors |
| `divisor_sum(n, power=1)` | The sum of the divisors, or of their powers |
| `carmichael(n)` | The exponent of the unit group |
| `liouville(n)` | Minus one to the number of prime factors with multiplicity |
| `mangoldt(n)` | The logarithm of p when n is a prime power, else zero |
| `omega(n)`, `big_omega(n)` | Distinct and total prime factor counts |
| `is_multiplicative(function, limit)` | Whether a function is multiplicative on a range |
| `dirichlet_convolution(f, g)` | The convolution of two arithmetic functions |
| `mobius_inversion(f)` | Recovery of a function from its divisor sums |

```python
>>> from discretus.number_theory.functions import divisor_count, euler_totient, mobius
>>> euler_totient(36), mobius(30), divisor_count(360)
(12, -1, 24)
```

The functions are computed from the factorization through their
multiplicative formulas rather than by counting, which is what makes them
fast for large arguments. Mobius inversion and Dirichlet convolution are
provided as operations on functions, so an identity such as the sum of the
totient over the divisors of $n$ being $n$ itself can be checked rather than
recited, and the suite checks exactly that.

## Diophantine equations

| Routine | Solves |
| --- | --- |
| `linear_diophantine(a, b, c)` | The equation with the full solution family |
| `pythagorean_triples(limit)` | Primitive and all triples below a bound |
| `pell(d, limit=None)` | The fundamental and further solutions of Pell's equation |
| `continued_fraction(value)` | The expansion of a rational or a quadratic irrational |
| `convergents(expansion)` | The convergents of an expansion |
| `frobenius(coins)` | The largest amount not representable |

A linear diophantine equation has a solution exactly when the greatest
common divisor of the coefficients divides the constant, and then the
solutions form an arithmetic family. The routine returns the family rather
than one member, because the family is the answer.

Pell's equation is where continued fractions earn their place: the
fundamental solution is read off the expansion of the square root of the
coefficient, and the later solutions follow by a recurrence. Both are
exposed, so the connection is visible rather than hidden inside one routine.

## Integer sequences

| Routine | Sequence |
| --- | --- |
| `perfect_numbers(limit)` | Numbers equal to the sum of their proper divisors |
| `is_perfect(n)`, `is_abundant(n)`, `is_deficient(n)` | The classification |
| `amicable_pairs(limit)` | Pairs whose divisor sums swap |
| `mersenne(n)`, `is_mersenne_prime(exponent)` | Mersenne numbers and primes |
| `fermat_number(n)` | Fermat numbers |
| `farey(order)` | The Farey sequence of an order |
| `stern_brocot(depth)` | The Stern Brocot tree |

The Farey sequence and the Stern Brocot tree are both generated by the
mediant operation from `discretus.core.rationals`, which is the kind of
sharing the core layer exists for: the operation is defined once and two
different constructions use it.

## Cryptographic primitives

These are teaching implementations. They are not hardened, they make no
attempt at constant time execution, they implement no padding scheme, and
they must not be used to protect real secrets. The security policy in the
repository states this in full, and the modules repeat it.

| Routine | Meaning |
| --- | --- |
| `rsa.generate_keypair(bits, seed=None)` | A key pair, with the primes recorded |
| `rsa.encrypt`, `rsa.decrypt` | Textbook RSA on integers |
| `rsa.sign`, `rsa.verify` | Textbook signing |
| `elgamal.generate_keypair(bits, seed=None)` | An ElGamal key pair |
| `elgamal.encrypt`, `elgamal.decrypt` | ElGamal on integers |
| `diffie_hellman.exchange(prime, generator, secrets)` | A shared secret |
| `primitive_root(modulus)` | A generator of the unit group, when one exists |
| `order(value, modulus)` | The multiplicative order |
| `lucas_sequence(p, q, n, modulus)` | Lucas sequences modulo a modulus |

The value of these modules is that every intermediate is inspectable. An RSA
key pair reports its primes, its totient, and its exponents, so a reader can
verify that the decryption exponent is the inverse of the encryption
exponent modulo the totient, which is the entire content of the scheme.

```python
>>> from discretus.number_theory.crypto import rsa
>>> keys = rsa.generate_keypair(bits=64, seed=7)
>>> message = 42
>>> rsa.decrypt(rsa.encrypt(message, keys.public), keys.private) == message
True
```

## Worked example: checking the theorems

The theorems this package implements are checkable on small inputs, and
checking them is the fastest way to be sure that the argument order and the
conventions are what you think they are. The following is close to what the
suite asserts, with a fixed seed.

```python
from discretus.core.random_base import SeededRandom
from discretus.number_theory.factorization import divisors, factorize
from discretus.number_theory.functions import euler_totient, mobius
from discretus.number_theory.gcd import extended_gcd, gcd
from discretus.number_theory.modular import crt, mod_exp, mod_inverse
from discretus.number_theory.primes import is_prime, primes_up_to

source = SeededRandom(2026)

for _ in range(200):
    a = source.integer(2, 10 ** 6)
    n = source.integer(2, 10 ** 6)

    # Bezout: the identity holds exactly.
    g, x, y = extended_gcd(a, n)
    assert g == gcd(a, n) and a * x + n * y == g

    # The inverse exists exactly when the arguments are coprime.
    if g == 1:
        assert (mod_inverse(a, n) * a) % n == 1 % n
        # Euler's theorem.
        assert mod_exp(a, euler_totient(n), n) == 1 % n

    # The fundamental theorem of arithmetic, in both directions.
    product = 1
    for prime, exponent in factorize(n).items():
        assert is_prime(prime)
        product *= prime ** exponent
    assert product == n

    # The totient counts the units, which can be verified directly.
    assert euler_totient(n) == sum(1 for k in range(1, n + 1) if gcd(k, n) == 1) if n <= 2000 else True

    # The divisor sum of the Mobius function is one at one and zero above.
    assert sum(mobius(d) for d in divisors(n)) == (1 if n == 1 else 0)

    # The totient sums to the argument over the divisors.
    assert sum(euler_totient(d) for d in divisors(n)) == n

# Fermat's little theorem, on the primes themselves.
for prime in primes_up_to(500):
    base = source.integer(1, prime - 1)
    assert mod_exp(base, prime - 1, prime) == 1

# The Chinese remainder theorem reproduces its inputs.
values, moduli = [2, 3, 2], [3, 5, 7]
combined, modulus = crt(values, moduli)
assert modulus == 105
assert all(combined % m == v % m for v, m in zip(values, moduli))

print("every theorem checks out on 200 randomized cases")
```

Two of these assertions are worth singling out. The identity that the Euler
totient sums to its argument over the divisors is a strong check, because it
links the totient, the divisor enumeration, and the factorization, and an
error in any one of the three breaks it. The identity that the Mobius
function sums to zero over the divisors of anything above one is the
statement that Mobius inversion works at all, so it validates the function
and the divisor routine together.

## Complexity summary

| Routine | Complexity |
| --- | --- |
| Euclidean algorithm | O(log min(a, b)) divisions |
| Modular exponentiation | O(log exponent) multiplications |
| Modular inverse | O(log modulus) |
| Chinese remainder theorem | O(k log max modulus) |
| Sieve of Eratosthenes | O(n log log n) |
| Linear sieve | O(n) |
| Miller Rabin, per witness | O(log cubed n) |
| Trial division | O(square root of n) |
| Pollard's rho | O(fourth root of n) expected |
| Quadratic sieve | Subexponential |
| Euler totient from the factorization | O(number of distinct primes) |
| Discrete logarithm, meet in the middle | O(square root of modulus) time and space |

## Errors

| Exception | Raised when |
| --- | --- |
| `DomainError` | A modulus below one, a negative argument where positivity is required |
| `ValidationError` | A non integer argument, or mismatched congruence lists |
| `InfeasibleError` | No modular inverse, no square root, no primitive root, an inconsistent congruence system, or an unsolvable diophantine equation |
| `LimitExceededError` | A sieve limit beyond the configured enumeration bound |
| `ConvergenceError` | A probabilistic factorization exhausted its iteration budget |

## Design notes

**Dispatching is explicit and documented.** `is_prime` and `factorize`
choose a method by input size, which is what a user wants, and the specific
methods remain public so that a reader can call the one they are studying
and a benchmark can compare them. The dispatch policy is documented, so the
behaviour is predictable rather than magical.

**Probabilistic means probabilistic.** A probable prime test reports a
probable prime, and the documentation gives the error bound and the witness
count. Where a deterministic answer is available below a bound, the bound is
stated. The library never presents a probabilistic result as certain.

**Randomized routines take a seed.** Pollard's rho, the elliptic curve
method, and the probabilistic tests all accept a seed and are deterministic
once given one, which is what makes a failing case reproducible.

**The factorization is the hub.** The arithmetic functions, the divisor
routines, and the sequence classifications all consume a factorization
rather than recomputing one, so factoring once and reusing the result is the
efficient path and is what the convenience wrappers do internally.

## See also

- The [number theory tutorial](../tutorials/number_theory.md), which builds
  from the Euclidean algorithm to RSA.
- [`discretus.core`](core.md), for the modular primitives this package
  exposes and for exact rational arithmetic.
- [`discretus.algebra`](algebra.md), for the unit groups, prime fields, and
  finite fields that this material underlies.
- [`discretus.combinatorics`](combinatorics.md), for the counting functions
  that share identities with the arithmetic functions.
