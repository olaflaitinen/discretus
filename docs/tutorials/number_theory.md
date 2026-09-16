# Number theory

This tutorial goes from the Euclidean algorithm to RSA in one line of
development, because that is genuinely how the subject builds: greatest
common divisors give modular inverses, inverses give the Chinese remainder
theorem, primality and factorization give the parameters, and Euler's
theorem gives the scheme.

Everything here is exact. The numbers get large quickly, and that is a
feature of the subject rather than an inconvenience.

## Divisibility and the Euclidean algorithm

The greatest common divisor is computed by repeated division, which is the
oldest non trivial algorithm still in use.

```python
from discretus.number_theory.gcd import gcd, lcm

print(gcd(462, 1071))
print(lcm(4, 6))
print(gcd(2 ** 100, 3 ** 100))
```

The cost is logarithmic in the smaller argument, which is why it works on
numbers of any size.

```python
from discretus.utils.timing import Timer

a, b = 2 ** 4000 + 1, 3 ** 2500 + 7
with Timer() as timer:
    print(gcd(a, b), timer.human)
```

The extended algorithm additionally returns the Bezout coefficients, which
satisfy

$$a x + b y = \gcd(a, b).$$

```python
from discretus.number_theory.gcd import extended_gcd

divisor, x, y = extended_gcd(462, 1071)
print(divisor, x, y)
print(462 * x + 1071 * y == divisor)
```

Always verify the identity the first time you use this routine. The
coefficients are not unique, so a different implementation may return a
different pair, and the identity is the only thing that characterizes them.

This single identity is the source of almost everything that follows.

## Modular arithmetic

Working modulo $n$ means identifying numbers that differ by a multiple of
$n$. Addition, subtraction, and multiplication descend to the residue
classes without difficulty.

```python
from discretus.number_theory.modular import mod_exp, mod_inverse

print((17 + 25) % 12, (17 * 25) % 12)
print(mod_exp(7, 128, 13))
```

Modular exponentiation is not repeated multiplication. It is square and
multiply, which costs a logarithmic number of multiplications, and that
difference is what makes public key cryptography possible.

```python
print(mod_exp(3, 10 ** 6, 1_000_003))

with Timer() as fast:
    mod_exp(3, 2 ** 20, 1_000_003)
print("logarithmic:", fast.human)
```

Division is the interesting operation, because it is not always possible. An
element has a multiplicative inverse modulo $n$ exactly when it is coprime
to $n$, and the extended Euclidean algorithm both decides that and computes
the inverse.

```python
print(mod_inverse(3, 11))
print(3 * mod_inverse(3, 11) % 11)

from discretus import InfeasibleError

try:
    mod_inverse(2, 4)
except InfeasibleError as error:
    print("no inverse:", error)
```

The error message names the greatest common divisor, which is the reason
there is no inverse. Two and four share a factor of two, so no multiple of
two is congruent to one modulo four.

The units, that is the invertible residues, form a group under
multiplication, and its size is the Euler totient.

```python
from discretus.number_theory.functions import euler_totient
from discretus.core.modular_base import units

print(units(12), len(units(12)), euler_totient(12))
```

## The Chinese remainder theorem

A system of congruences with pairwise coprime moduli has a unique solution
modulo the product:

$$x \equiv a_i \pmod{n_i}, \quad i = 1, \dots, k.$$

```python
from discretus.number_theory.modular import crt

value, modulus = crt([2, 3, 2], [3, 5, 7])
print(value, modulus)
print([value % n for n in (3, 5, 7)])
```

The routine returns both the residue and the combined modulus, because the
residue alone is not an answer.

The theorem is more than a puzzle solver. It says that arithmetic modulo a
composite number is the same as arithmetic modulo each of its prime power
factors, performed in parallel. That is why factorization breaks a modular
problem into independent smaller ones, and it is why the security of RSA
depends on factorization being hard.

```python
print(crt([1, 0], [4, 25]))
print(crt([1, 2], [4, 6]))
```

The second call has moduli that are not coprime, and the library still
succeeds because the two congruences agree on the shared factor. When they
disagree there is no solution, and the error says so.

```python
try:
    crt([1, 2], [4, 6, 8])
except Exception as error:
    print(type(error).__name__, error)

try:
    crt([0, 1], [4, 6])
except InfeasibleError as error:
    print("inconsistent:", error)
```

## Primes

A prime has no divisors other than one and itself. Deciding primality and
finding factors are different problems with very different costs, and the
gap between them is where cryptography lives.

Trial division is the definition made into an algorithm, and it costs the
square root of the input.

```python
from discretus.number_theory.primes import is_prime, primes_up_to, trial_division

print(primes_up_to(50))
print(trial_division(1_000_003))
```

A sieve is far better when every prime below a bound is wanted, because it
does the work once for all of them.

```python
with Timer() as sieve:
    primes = primes_up_to(2_000_000)
print(len(primes), sieve.human)
```

The count agrees with the prime number theorem, which says the number of
primes below $x$ is asymptotically $x / \ln x$.

```python
import math

estimate = 2_000_000 / math.log(2_000_000)
print(len(primes), round(estimate), round(len(primes) / estimate, 4))
```

For a single large number a sieve is useless and a probabilistic test is
right. The Fermat test uses Fermat's little theorem, that
$a^{p-1} \equiv 1 \pmod p$ for a prime $p$ and a base coprime to it.

```python
from discretus.number_theory.primes import fermat_test, miller_rabin

print(fermat_test(1_000_003, rounds=5, seed=1))
print(fermat_test(561, rounds=5, seed=1))
print(miller_rabin(561))
```

Five hundred and sixty one is a Carmichael number: composite, and yet it
passes the Fermat test for every base coprime to it. The Miller Rabin test
rejects it, because it checks a stronger condition, and that is why Miller
Rabin is the test the library uses.

```python
carmichael = [561, 1105, 1729, 2465, 2821, 6601, 8911]
print([fermat_test(n, rounds=10, seed=2) for n in carmichael])
print([miller_rabin(n) for n in carmichael])
print([is_prime(n) for n in carmichael])
```

`is_prime` dispatches by size, and below a documented bound of about three
times ten to the twenty fourth power it is deterministic, using a fixed
witness set.

```python
print(is_prime(2 ** 61 - 1))
print(is_prime(2 ** 67 - 1))
```

The first is a Mersenne prime and the second is not, which was a famous
hand computation and is now instant.

## Factorization

Every integer above one factors uniquely into primes.

$$n = \prod_{i=1}^{k} p_i^{\,e_i}, \qquad p_1 < p_2 < \dots < p_k$$

```python
from discretus.number_theory.factorization import divisors, factorize

print(factorize(600_851_475_143))
print(factorize(2 ** 20 - 1))
print(divisors(360))
```

The factorization is returned as a mapping from prime to exponent, which is
the form the arithmetic functions consume. Reconstructing the input is the
check worth making.

```python
from discretus.core.numeric import product

n = 987_654_321
factors = factorize(n)
print(factors)
print(product(p ** e for p, e in factors.items()) == n)
```

The methods are separately available, because each has inputs where it is
the right choice.

```python
from discretus.number_theory.factorization import fermat_factor, pollard_p1, pollard_rho

semiprime = 1_000_003 * 1_000_033
print(pollard_rho(semiprime, seed=1))
print(fermat_factor(semiprime))
print(pollard_p1(299_209, bound=100))
```

Fermat's method is fast when the two factors are close together, which is
exactly the case here, and slow otherwise. Pollard's rho is the general
purpose choice for medium factors. Pollard's p minus one finds a factor
whose predecessor is smooth. The reference states the condition under which
each one is fast, because they are complementary rather than ranked.

The cost gap between primality and factorization is the whole point. Test a
large number for primality and then try to factor a product of two such
numbers.

```python
from discretus.number_theory.primes import next_prime

p = next_prime(10 ** 12)
q = next_prime(10 ** 12 + 10 ** 6)
with Timer() as test:
    is_prime(p) and is_prime(q)
print("two primality tests:", test.human)

with Timer() as factoring:
    print(pollard_rho(p * q, seed=3))
print("one factorization:", factoring.human)
```

Both numbers are twelve digits, and the asymmetry is already visible. At six
hundred digits the primality test is still milliseconds and the
factorization is beyond any computer.

## The arithmetic functions

These functions are defined in terms of the factorization, so computing the
factorization once and reusing it is the efficient path.

```python
from discretus.number_theory.functions import (
    divisor_count, divisor_sum, euler_totient, mobius, omega,
)

for n in (12, 36, 97, 360):
    print(n, euler_totient(n), divisor_count(n), divisor_sum(n), mobius(n), omega(n))
```

They satisfy identities that make excellent checks, because each one links
several routines.

```python
from discretus.number_theory.factorization import divisors

for n in range(1, 40):
    assert sum(euler_totient(d) for d in divisors(n)) == n
    assert sum(mobius(d) for d in divisors(n)) == (1 if n == 1 else 0)
    assert divisor_count(n) == len(divisors(n))
    assert divisor_sum(n) == sum(divisors(n))
print("four identities hold for every n below forty")
```

The first says the totient sums to its argument over the divisors. The
second is the statement that makes Mobius inversion work. Both are proved in
any textbook and are more convincing when you have watched them hold.

Euler's theorem generalizes Fermat's little theorem to a composite modulus:
if $\gcd(a, n) = 1$ then

$$a^{\varphi(n)} \equiv 1 \pmod{n}.$$

```python
from discretus.number_theory.modular import mod_exp

for n in (12, 35, 91, 1000):
    for a in range(2, 10):
        if gcd(a, n) == 1:
            assert mod_exp(a, euler_totient(n), n) == 1
print("Euler's theorem holds")
```

That theorem is the last ingredient. Everything needed for RSA is now in
place.

## RSA

The scheme is short enough to write out, and writing it out is the best way
to understand it. Choose two primes, multiply them, compute the totient of
the product, choose an exponent coprime to the totient, and invert it.

```python
from discretus.number_theory.gcd import gcd
from discretus.number_theory.modular import mod_exp, mod_inverse
from discretus.number_theory.primes import next_prime

p = next_prime(10 ** 20 + 7)
q = next_prime(10 ** 20 + 391)
n = p * q
totient = (p - 1) * (q - 1)

e = 65537
assert gcd(e, totient) == 1
d = mod_inverse(e, totient)

message = 1234567890123456789
cipher = mod_exp(message, e, n)
recovered = mod_exp(cipher, d, n)

print(n.bit_length())
print(cipher)
print(recovered == message)
```

The correctness is Euler's theorem: raising to $e$ and then to $d$ raises to
$ed$, which is one more than a multiple of the totient, so the result is the
original message. The security rests on the difficulty of recovering $p$
and $q$ from $n$, which is the factorization problem you timed above.

The library's own implementation does the same thing and reports every
intermediate, so the scheme can be inspected rather than trusted.

```python
from discretus.number_theory.crypto import rsa

keys = rsa.generate_keypair(bits=128, seed=7)
print(keys.public)
print(keys.private.exponent * keys.public.exponent % keys.totient == 1)
print(rsa.decrypt(rsa.encrypt(42, keys.public), keys.private))
```

These primitives are for teaching. They are not hardened against side
channel attacks, they implement no padding, and they must not be used to
protect real secrets. The security policy in the repository says so at
length, and so does every module in the subpackage.

## Diophantine equations

A linear diophantine equation is solvable exactly when the greatest common
divisor of the coefficients divides the constant, and the Bezout
coefficients give the solution.

```python
from discretus.number_theory.diophantine import linear_diophantine, pythagorean_triples

solution = linear_diophantine(6, 15, 9)
print(solution)
print(6 * solution.x + 15 * solution.y == 9)

print(linear_diophantine(6, 15, 7))
```

The second call reports no solution, because the divisor three does not
divide seven.

Pythagorean triples and Pell's equation are the classical non linear cases.

```python
from discretus.number_theory.diophantine import continued_fraction, pell

print(pythagorean_triples(40, primitive_only=True))
print(pell(2, limit=3))
print(continued_fraction("415/93"))
```

Pell's equation is where continued fractions earn their keep: the
fundamental solution is read off the expansion of the square root of the
coefficient. The library exposes both steps, so the connection is visible.

## Quadratic residues

One more layer is worth meeting, because it appears in primality testing, in
factorization, and in cryptography. A residue is a quadratic residue modulo
a prime when it is a square there.

```python
from discretus.number_theory.modular import (
    legendre, mod_sqrt, quadratic_residues, tonelli_shanks,
)

prime = 13
print(quadratic_residues(prime))
print([legendre(a, prime) for a in range(1, prime)])
```

The Legendre symbol is one for a residue, minus one for a non residue, and
zero for a multiple of the prime. Exactly half of the nonzero residues are
squares, which the two lines above show.

When a residue is a square, its roots can be computed, and Tonelli Shanks is
the algorithm that does it.

```python
print(mod_sqrt(10, 13))
root = tonelli_shanks(10, 13)
print(root, root * root % 13)
```

Asking for the square root of a non residue raises, with the reason.

```python
from discretus import InfeasibleError

try:
    tonelli_shanks(5, 13)
except InfeasibleError as error:
    print("not a residue:", error)
```

The Jacobi symbol extends the Legendre symbol to an odd composite modulus,
and the extension loses a property that is easy to assume. A Jacobi symbol
of one does not imply that the argument is a square.

```python
from discretus.number_theory.modular import jacobi

modulus = 15
print(jacobi(2, modulus), 2 in quadratic_residues(modulus))
```

The symbol is one and two is not a square modulo fifteen. Confusing the two
symbols is the classic error in this area, which is why the reference states
the distinction at both call sites.

The reason to care: the Solovay Strassen primality test is built on exactly
this discrepancy, and so is the quadratic sieve factorization method.

## Discrete logarithms

Exponentiation modulo a prime is easy and its inverse is believed to be
hard, which is the second asymmetry cryptography is built on, alongside
factorization.

```python
from discretus.number_theory.modular import baby_step_giant_step, discrete_log

prime = 1_000_003
base, exponent = 5, 123_456
target = mod_exp(base, exponent, prime)

print(target)
with Timer() as forward:
    mod_exp(base, exponent, prime)
with Timer() as backward:
    recovered = discrete_log(base, target, prime)
print(recovered, forward.human, backward.human)
```

The forward direction is logarithmic and the backward direction, by the meet
in the middle method, costs the square root of the modulus in both time and
memory. At a six digit modulus the difference is already obvious, and at the
sizes used in practice the backward direction is infeasible.

Diffie Hellman key exchange is that asymmetry turned into a protocol, and it
is four lines.

```python
from discretus.number_theory.crypto import diffie_hellman, primitive_root

prime = 1_000_003
generator = primitive_root(prime)
print(generator)

alice_secret, bob_secret = 123_457, 987_653
alice_public = mod_exp(generator, alice_secret, prime)
bob_public = mod_exp(generator, bob_secret, prime)

shared_one = mod_exp(bob_public, alice_secret, prime)
shared_two = mod_exp(alice_public, bob_secret, prime)
print(shared_one == shared_two)
```

Both parties reach the same value because exponentiation commutes, and an
observer who sees only the public values faces a discrete logarithm. The
primitive root is a generator of the multiplicative group, which the library
finds by checking candidates against the factorization of the group order.

```python
from discretus.core.modular_base import ModularInteger

print(ModularInteger(generator, prime).order() == prime - 1)
```

## Integer sequences worth knowing

The package computes several classical families, and each one is a
definition made computable rather than a curiosity.

```python
from discretus.number_theory.sequences import (
    amicable_pairs, is_perfect, mersenne, perfect_numbers,
)

print(perfect_numbers(10_000))
print([is_perfect(n) for n in (6, 28, 12)])
print(amicable_pairs(1500))
print([mersenne(p) for p in (2, 3, 5, 7)])
```

A perfect number equals the sum of its proper divisors, and the four below
ten thousand have been known since antiquity. An amicable pair consists of
two numbers each equal to the sum of the other's proper divisors, and the
smallest is two hundred and twenty with two hundred and eighty four.

The connection between perfect numbers and Mersenne primes is one of the
oldest theorems in the subject: an even number is perfect exactly when it
has the form $2^{p-1}(2^p - 1)$ with $2^p - 1$ prime. Check it.

```python
from discretus.number_theory.primes import is_prime

for p in (2, 3, 5, 7, 13, 17):
    candidate = 2 ** p - 1
    if is_prime(candidate):
        perfect = 2 ** (p - 1) * candidate
        assert is_perfect(perfect)
        print(p, candidate, perfect)
```

Every line of that output is a perfect number, produced from a prime
exponent, and the assertion confirms it by the definition rather than by the
formula. That pairing, a construction checked against a definition, is the
strongest kind of test available in this subject.

## Exercises

1. Verify Bezout's identity on two hundred random pairs.
2. Find the smallest Carmichael number above ten thousand by testing
   candidates with the Fermat and Miller Rabin tests and looking for a
   disagreement.
3. Confirm the prime number theorem estimate at several bounds and watch the
   ratio approach one.
4. Implement RSA signing rather than encryption, which is the same
   arithmetic with the exponents exchanged, and verify a signature.
5. Compute the multiplicative order of two modulo each prime below a hundred
   and check that it always divides the prime minus one.
6. Use the Chinese remainder theorem to solve a system of three congruences
   with non coprime moduli, and construct one that has no solution.

## Why exactness matters here

This tutorial is the clearest place to see why the library refuses floating
point. Two examples make the point.

A float has fifty three bits of mantissa, so it cannot represent an integer
above about nine quadrillion exactly. The numbers in this tutorial passed
that bound in the second section.

```python
n = 10 ** 20 + 39
print(n)
print(int(float(n)))
print(int(float(n)) == n)
```

The float round trip lost the last few digits, which in this subject is the
difference between a prime and a composite. Every routine in the package
works on Python integers, which are unbounded, so nothing is ever rounded.

The second example is subtler and more dangerous. A computation can look
correct while being wrong, because the error is small relative to the
magnitude and fatal relative to the question.

```python
candidate = 2 ** 61 - 1
print(is_prime(candidate))

# A float based square root bound, as a naive trial division might use.
import math

print(math.isqrt(candidate))
print(int(math.sqrt(candidate)))
print(math.isqrt(candidate) == int(math.sqrt(candidate)))
```

The exact integer square root and the float one disagree, and a trial
division loop that used the float bound would test the wrong range. The
library uses `integer_sqrt` from the core layer, which is exact by Newton
iteration, throughout.

The same discipline applies to the rationals. The convergents of a continued
fraction, the coefficients of an interpolating polynomial, and the
probabilities in a counting problem are all exact fractions here, so a chain
of such computations does not drift.

```python
from fractions import Fraction

from discretus.core.rationals import best_approximation, continued_fraction_of

print(continued_fraction_of(Fraction(415, 93)))
print(best_approximation(Fraction(415, 93), 10))
print(sum(Fraction(1, k) for k in range(1, 11)))
```

The last line is the tenth harmonic number, exactly. Computed in floating
point it would be a number close to that fraction and not equal to it, and
the difference compounds in any computation that continues from it.

## Where to go next

- The [number theory reference](../api/number_theory.md) for the complete
  interface, including the sieves, the quadratic residue machinery, and the
  factorization methods this tutorial did not use.
- [Group theory](group_theory.md), where the unit group of this tutorial
  becomes a group object with subgroups and generators.
- The [algebra reference](../api/algebra.md) for prime fields and finite
  fields, which are the modular arithmetic of this tutorial with a second
  operation.
