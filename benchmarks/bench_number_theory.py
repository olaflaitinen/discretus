# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Benchmarks for the number theory package.

This is the package where the size parameter is the number of bits rather
than the number of objects, and where the arithmetic itself is part of the
cost. A routine that performs a linear number of multiplications on integers
whose digit count grows linearly is quadratic in the digits, and the growth
report is where that distinction becomes visible instead of arguable.

What is measured, and why:

    The greatest common divisor, because it is the most called routine in
    the package and because the library ships two implementations whose
    relative cost the reference makes a claim about.

    Modular exponentiation, because it is the operation that makes public key
    cryptography possible and because its cost must be logarithmic in the
    exponent rather than linear. This is the single most important growth
    ratio in the file.

    The sieves, because the reference states three different bounds for
    three sieves and a reader choosing between them deserves numbers.

    Primality against factorization, at the same bit length. This is the
    asymmetry the whole of public key cryptography rests on, and measuring
    the two side by side is the clearest demonstration of it available.

    The factorization methods separately, because each is fast on inputs the
    others are slow on, and the reference states the condition for each. A
    single benchmark over random inputs would rank them misleadingly.

    The arithmetic functions, both from a cached factorization and from
    scratch, because they are defined in terms of the factorization and the
    reference recommends reusing one.

    The teaching cryptographic primitives, because a reader will want to
    know what a key generation costs before running one in a classroom.

Bit lengths rather than magnitudes are used as sizes wherever the cost is
governed by the digit count, so that the growth report reads as a doubling
per step. Every input is generated from a seed derived from the benchmark
name, which matters more here than elsewhere: factorization runtimes vary by
orders of magnitude between inputs of the same size, so an unseeded family
would make two runs incomparable.
"""

from __future__ import annotations

from typing import Any, List, Optional, Tuple

from . import benchmark, require, requires_all, seeded

# ---------------------------------------------------------------------------
# The modules under measurement
# ---------------------------------------------------------------------------

gcd_module = require(
    "discretus.number_theory.gcd", "gcd", "extended_gcd", "binary_gcd"
)
modular_module = require(
    "discretus.number_theory.modular", "mod_exp", "mod_inverse", "crt"
)
primes_module = require(
    "discretus.number_theory.primes", "is_prime", "primes_up_to", "next_prime"
)
factorization_module = require(
    "discretus.number_theory.factorization", "factorize", "pollard_rho"
)
functions_module = require(
    "discretus.number_theory.functions", "euler_totient", "mobius"
)
diophantine_module = require(
    "discretus.number_theory.diophantine", "linear_diophantine", "pell"
)
sequences_module = require(
    "discretus.number_theory.sequences", "perfect_numbers", "farey"
)
crypto_module = require("discretus.number_theory.crypto", "rsa", "primitive_root")

#: The core primitives are available even before the number theory package
#: is filled in, so the benchmarks that measure them can run today and give
#: the suite something to report.
core_modular_module = require(
    "discretus.core.modular_base", "extended_euclidean", "mod_power"
)
core_numeric_module = require("discretus.core.numeric", "integer_sqrt", "integer_nth_root")
core_bigint_module = require("discretus.core.bigint", "karatsuba_multiply")

GROUP_GCD = "number_theory.gcd"
GROUP_MODULAR = "number_theory.modular"
GROUP_PRIMES = "number_theory.primes"
GROUP_FACTORIZATION = "number_theory.factorization"
GROUP_FUNCTIONS = "number_theory.functions"
GROUP_DIOPHANTINE = "number_theory.diophantine"
GROUP_SEQUENCES = "number_theory.sequences"
GROUP_CRYPTO = "number_theory.crypto"
GROUP_CORE = "number_theory.core"


# ---------------------------------------------------------------------------
# Input preparation
# ---------------------------------------------------------------------------


def random_of_bits(bits: int, label: str) -> int:
    """Return a reproducible odd integer of the given bit length.

    Odd, because an even input is factored in one step and would make a
    factorization benchmark measure nothing. The top bit is forced so that
    the bit length is exactly what was asked for.
    """
    source = seeded(f"{label}.{bits}")
    value = source.getrandbits(bits) | 1 | (1 << (bits - 1))
    return value


def make_coprime_pair(bits: int) -> Tuple[int, int]:
    """Return two integers of the given bit length, usually coprime.

    Two random integers are coprime with probability about six over pi
    squared, so most draws give the case the inverse benchmarks need without
    any construction.
    """
    return (
        random_of_bits(bits, "nt.pair.left"),
        random_of_bits(bits, "nt.pair.right"),
    )


def make_worst_case_pair(bits: int) -> Tuple[int, int]:
    """Return two consecutive Fibonacci numbers of roughly the given size.

    Consecutive Fibonacci numbers are the worst case for the Euclidean
    algorithm: every division step has a quotient of one, so the number of
    steps is maximal for the size. A benchmark that only measured random
    inputs would report a better bound than the algorithm guarantees.
    """
    previous, current = 0, 1
    while current.bit_length() < bits:
        previous, current = current, previous + current
    return current, previous


def make_modular_triple(bits: int) -> Tuple[int, int, int]:
    """Return a base, an exponent, and a modulus of the given bit length."""
    return (
        random_of_bits(bits, "nt.base"),
        random_of_bits(bits, "nt.exponent"),
        random_of_bits(bits, "nt.modulus"),
    )


def make_semiprime(bits: int) -> Optional[int]:
    """Return a product of two primes of half the requested bit length.

    This is the shape of an RSA modulus and the input for which
    factorization is hard. The primes are found deterministically from a
    seed, so the same semiprime is factored on every run.
    """
    if primes_module is None:
        return None
    half = max(8, bits // 2)
    left = primes_module.next_prime(random_of_bits(half, "nt.semiprime.left"))
    right = primes_module.next_prime(random_of_bits(half, "nt.semiprime.right"))
    return left * right


def make_close_semiprime(bits: int) -> Optional[int]:
    """Return a product of two nearby primes, which suits Fermat's method.

    Fermat's difference of squares finds a factor quickly when the two
    factors are close to the square root, and slowly otherwise. Measuring it
    on this family rather than on a random one is what makes the reference's
    claim about it checkable.
    """
    if primes_module is None:
        return None
    half = max(8, bits // 2)
    left = primes_module.next_prime(random_of_bits(half, "nt.close"))
    right = primes_module.next_prime(left + 1)
    return left * right


def make_smooth_semiprime(bits: int) -> Optional[int]:
    """Return a semiprime one of whose factors has a smooth predecessor.

    This is the family Pollard's p minus one method is designed for. As with
    the Fermat case, the point is to measure each method where it is meant
    to work.
    """
    if primes_module is None:
        return None
    half = max(8, bits // 2)
    product = 2
    for candidate in primes_module.primes_up_to(64):
        product *= candidate
        if product.bit_length() > half:
            break
    smooth = primes_module.next_prime(product)
    other = primes_module.next_prime(random_of_bits(half, "nt.smooth.other"))
    return smooth * other


def make_factorization_cache(bits: int) -> Optional[Tuple[int, Any]]:
    """Return an integer together with its factorization.

    The arithmetic functions are defined in terms of the factorization, and
    the reference recommends computing one and reusing it. This setup is
    what makes that recommendation measurable.
    """
    if factorization_module is None:
        return None
    value = random_of_bits(min(bits, 48), "nt.cache")
    return value, factorization_module.factorize(value)


def make_congruence_system(count: int) -> Optional[Tuple[List[int], List[int]]]:
    """Return a solvable system of congruences with coprime moduli."""
    if primes_module is None:
        return None
    moduli = primes_module.primes_up_to(count * 20)[:count]
    source = seeded(f"nt.crt.{count}")
    values = [source.randrange(modulus) for modulus in moduli]
    return values, moduli


def make_rsa_keypair(bits: int) -> Optional[Any]:
    """Return an RSA key pair of the given modulus size."""
    if crypto_module is None:
        return None
    return crypto_module.rsa.generate_keypair(bits=bits, seed=20260115)


# ---------------------------------------------------------------------------
# Greatest common divisors
# ---------------------------------------------------------------------------


@benchmark(
    group=GROUP_GCD,
    sizes=[256, 1_024, 4_096],
    complexity="O(log min(a, b)) division steps",
    setup=make_coprime_pair,
    requires=gcd_module,
    note="the size is the bit length, so each step quadruples the digits",
)
def euclidean(payload: Tuple[int, int]) -> int:
    """Compute a greatest common divisor by repeated division."""
    left, right = payload
    return gcd_module.gcd(left, right)


@benchmark(
    group=GROUP_GCD,
    sizes=[256, 1_024, 4_096],
    complexity="O(log min(a, b)) division steps, worst case",
    setup=make_worst_case_pair,
    requires=gcd_module,
    note=(
        "consecutive Fibonacci numbers, where every quotient is one and the "
        "step count is maximal for the size"
    ),
)
def euclidean_worst_case(payload: Tuple[int, int]) -> int:
    """Compute a greatest common divisor on the worst case input."""
    left, right = payload
    return gcd_module.gcd(left, right)


@benchmark(
    group=GROUP_GCD,
    sizes=[256, 1_024, 4_096],
    complexity="O(log min(a, b))",
    setup=make_coprime_pair,
    requires=gcd_module,
    note="the extended form, which also returns the Bezout coefficients",
)
def extended_euclidean(payload: Tuple[int, int]) -> Tuple[int, int, int]:
    """Compute a divisor together with its Bezout coefficients."""
    left, right = payload
    return gcd_module.extended_gcd(left, right)


@benchmark(
    group=GROUP_GCD,
    sizes=[256, 1_024, 4_096],
    complexity="O(log squared) bit operations",
    setup=make_coprime_pair,
    requires=gcd_module,
    note=(
        "Stein's algorithm, which replaces division with shifting; the "
        "reference says this is not an advantage in Python, and this is "
        "where that claim is checked"
    ),
)
def binary_gcd(payload: Tuple[int, int]) -> int:
    """Compute a greatest common divisor by shifting and subtraction."""
    left, right = payload
    return gcd_module.binary_gcd(left, right)


@benchmark(
    group=GROUP_GCD,
    sizes=[10, 100, 1_000],
    complexity="O(k log max)",
    requires=gcd_module,
    note="the divisor of many integers, where the size is the argument count",
)
def gcd_multiple(count: int) -> int:
    """Compute the greatest common divisor of many integers."""
    source = seeded(f"nt.gcd_multiple.{count}")
    values = [source.randint(1, 10**12) for _ in range(count)]
    return gcd_module.gcd_multiple(values)


@benchmark(
    group=GROUP_CORE,
    sizes=[256, 1_024, 4_096],
    complexity="O(log min(a, b))",
    setup=make_coprime_pair,
    requires=core_modular_module,
    note=(
        "the core primitive the number theory package exposes, measured "
        "directly so that the suite reports something before the package is "
        "filled in"
    ),
)
def core_extended_euclidean(payload: Tuple[int, int]) -> Tuple[int, int, int]:
    """Compute the Bezout identity through the core primitive."""
    left, right = payload
    return core_modular_module.extended_euclidean(left, right)


# ---------------------------------------------------------------------------
# Modular arithmetic
# ---------------------------------------------------------------------------


@benchmark(
    group=GROUP_MODULAR,
    sizes=[256, 512, 1_024, 2_048],
    complexity="O(log exponent) modular multiplications",
    setup=make_modular_triple,
    requires=modular_module,
    note=(
        "the most important ratio in the file: doubling the bit length "
        "doubles the multiplication count and quadruples the cost of each, "
        "so the implied exponent should be near three and never near the "
        "exponent itself"
    ),
)
def modular_exponentiation(payload: Tuple[int, int, int]) -> int:
    """Compute a modular power by square and multiply."""
    base, exponent, modulus = payload
    return modular_module.mod_exp(base, exponent, modulus)


@benchmark(
    group=GROUP_MODULAR,
    sizes=[256, 1_024, 4_096],
    complexity="O(log modulus)",
    setup=make_coprime_pair,
    requires=modular_module,
)
def modular_inverse(payload: Tuple[int, int]) -> int:
    """Compute a multiplicative inverse."""
    value, modulus = payload
    return modular_module.mod_inverse(value, modulus)


@benchmark(
    group=GROUP_MODULAR,
    sizes=[10, 100, 1_000],
    complexity="O(k log max modulus)",
    setup=make_congruence_system,
    requires=requires_all(primes_module, modular_module),
    note="the Chinese remainder theorem over many congruences",
)
def chinese_remainder(payload: Tuple[List[int], List[int]]) -> Tuple[int, int]:
    """Combine many congruences into one."""
    values, moduli = payload
    return modular_module.crt(values, moduli)


@benchmark(
    group=GROUP_MODULAR,
    sizes=[64, 128, 256],
    complexity="O(log squared p)",
    requires=requires_all(primes_module, modular_module),
    note="Tonelli Shanks, which needs a prime modulus and a residue",
)
def modular_square_root(bits: int) -> int:
    """Compute a square root modulo a prime."""
    prime = primes_module.next_prime(random_of_bits(bits, "nt.sqrt.prime"))
    value = pow(random_of_bits(bits // 2, "nt.sqrt.value"), 2, prime)
    return modular_module.tonelli_shanks(value, prime)


@benchmark(
    group=GROUP_MODULAR,
    sizes=[32, 40, 48],
    complexity="O(square root of the modulus) time and space",
    requires=requires_all(primes_module, modular_module),
    note=(
        "the discrete logarithm by the meet in the middle method; the cost "
        "grows as the square root of the modulus, which is what makes the "
        "forward direction usable and the inverse infeasible"
    ),
)
def discrete_logarithm(bits: int) -> int:
    """Recover an exponent from a modular power."""
    prime = primes_module.next_prime(random_of_bits(bits, "nt.dlog.prime"))
    base = 5
    exponent = random_of_bits(bits // 2, "nt.dlog.exponent") % prime
    target = pow(base, exponent, prime)
    return modular_module.discrete_log(base, target, prime)


@benchmark(
    group=GROUP_MODULAR,
    sizes=[64, 256, 1_024],
    complexity="O(log modulus)",
    requires=requires_all(primes_module, modular_module),
)
def legendre_symbol(bits: int) -> int:
    """Compute a Legendre symbol."""
    prime = primes_module.next_prime(random_of_bits(bits, "nt.legendre"))
    return modular_module.legendre(random_of_bits(bits // 2, "nt.legendre.a"), prime)


@benchmark(
    group=GROUP_CORE,
    sizes=[256, 512, 1_024, 2_048],
    complexity="O(log exponent) modular multiplications",
    setup=make_modular_triple,
    requires=core_modular_module,
    note="the core primitive, measurable before the package exists",
)
def core_modular_exponentiation(payload: Tuple[int, int, int]) -> int:
    """Compute a modular power through the core primitive."""
    base, exponent, modulus = payload
    return core_modular_module.mod_power(base, exponent, modulus)


@benchmark(
    group=GROUP_CORE,
    sizes=[1_024, 4_096, 16_384],
    complexity="O(log value) Newton iterations",
    requires=core_numeric_module,
    note="the exact integer square root, which a float cannot provide",
)
def core_integer_sqrt(bits: int) -> int:
    """Compute an exact integer square root."""
    return core_numeric_module.integer_sqrt(random_of_bits(bits, "nt.isqrt"))


@benchmark(
    group=GROUP_CORE,
    sizes=[1_024, 4_096, 16_384],
    complexity="O(log value) Newton iterations",
    requires=core_numeric_module,
)
def core_integer_nth_root(bits: int) -> int:
    """Compute an exact integer cube root."""
    return core_numeric_module.integer_nth_root(random_of_bits(bits, "nt.nthroot"), 3)


@benchmark(
    group=GROUP_CORE,
    sizes=[1_024, 4_096, 16_384],
    complexity="O(n to the power log2(3)) bit operations",
    setup=make_coprime_pair,
    requires=core_bigint_module,
    note=(
        "the transparent Karatsuba implementation, whose divide and conquer "
        "recurrence the documentation cites; the built-in multiplication is "
        "faster and this exists to be read"
    ),
)
def core_karatsuba(payload: Tuple[int, int]) -> int:
    """Multiply two integers by the Karatsuba method."""
    left, right = payload
    return core_bigint_module.karatsuba_multiply(left, right)


# ---------------------------------------------------------------------------
# Primality
# ---------------------------------------------------------------------------


@benchmark(
    group=GROUP_PRIMES,
    sizes=[100_000, 1_000_000, 10_000_000],
    complexity="O(n log log n)",
    requires=primes_module,
    note="the sieve of Eratosthenes, and the reference bound to check",
)
def sieve_eratosthenes(limit: int) -> List[int]:
    """Find every prime below a limit by the classical sieve."""
    return primes_module.sieve_eratosthenes(limit)


@benchmark(
    group=GROUP_PRIMES,
    sizes=[100_000, 1_000_000, 10_000_000],
    complexity="O(n / log log n)",
    requires=primes_module,
    note="the sieve of Atkin, asymptotically better and with a worse constant",
)
def sieve_atkin(limit: int) -> List[int]:
    """Find every prime below a limit by the sieve of Atkin."""
    return primes_module.sieve_atkin(limit)


@benchmark(
    group=GROUP_PRIMES,
    sizes=[100_000, 1_000_000, 10_000_000],
    complexity="O(n)",
    requires=primes_module,
    note="the linear sieve, which also yields the smallest prime factors",
)
def linear_sieve(limit: int) -> Any:
    """Find every prime below a limit by the linear sieve."""
    return primes_module.linear_sieve(limit)


@benchmark(
    group=GROUP_PRIMES,
    sizes=[1_000_000, 10_000_000],
    complexity="O((high - low) log log high)",
    requires=primes_module,
    note="the segmented sieve, whose memory is the interval rather than the bound",
)
def segmented_sieve(limit: int) -> List[int]:
    """Find the primes in an interval near a bound."""
    return primes_module.segmented_sieve(limit, limit + 100_000)


@benchmark(
    group=GROUP_PRIMES,
    sizes=[64, 128, 256, 512],
    complexity="O(rounds log cubed n)",
    requires=primes_module,
    note=(
        "Miller Rabin on a prime, which is the worst case because every "
        "witness must be tried"
    ),
)
def miller_rabin_on_prime(bits: int) -> bool:
    """Test a prime for primality by Miller Rabin."""
    candidate = primes_module.next_prime(random_of_bits(bits, "nt.mr.prime"))
    return primes_module.miller_rabin(candidate)


@benchmark(
    group=GROUP_PRIMES,
    sizes=[64, 128, 256, 512],
    complexity="O(log cubed n) for a composite, usually one witness",
    requires=primes_module,
    note="the same test on a composite, which usually stops at the first witness",
)
def miller_rabin_on_composite(bits: int) -> bool:
    """Test a composite for primality by Miller Rabin."""
    value = random_of_bits(bits, "nt.mr.composite") | 3
    return primes_module.miller_rabin(value * 3)


@benchmark(
    group=GROUP_PRIMES,
    sizes=[24, 32, 40],
    complexity="O(square root of n)",
    requires=primes_module,
    note=(
        "trial division, whose cost is the square root of the value rather "
        "than a polynomial in its digits; compare the sizes it can reach "
        "with those Miller Rabin handles"
    ),
)
def trial_division_primality(bits: int) -> bool:
    """Test a number for primality by trial division."""
    return primes_module.trial_division(random_of_bits(bits, "nt.trial"))


@benchmark(
    group=GROUP_PRIMES,
    sizes=[64, 256, 1_024],
    complexity="O(gap times the test cost)",
    requires=primes_module,
    note="finding the next prime, which tests a run of candidates",
)
def next_prime(bits: int) -> int:
    """Find the next prime above a value."""
    return primes_module.next_prime(random_of_bits(bits, "nt.next"))


@benchmark(
    group=GROUP_PRIMES,
    sizes=[100_000, 1_000_000],
    complexity="O(n log log n) through a sieve",
    requires=primes_module,
)
def prime_counting(limit: int) -> int:
    """Count the primes below a bound."""
    return primes_module.prime_counting(limit)


# ---------------------------------------------------------------------------
# Factorization
# ---------------------------------------------------------------------------


@benchmark(
    group=GROUP_FACTORIZATION,
    sizes=[32, 48, 64],
    complexity="dispatches by size and structure",
    requires=factorization_module,
    note="the default entry point, on a random integer rather than a semiprime",
)
def factorize_random(bits: int) -> Any:
    """Factor a random integer."""
    return factorization_module.factorize(random_of_bits(bits, "nt.factor.random"))


@benchmark(
    group=GROUP_FACTORIZATION,
    sizes=[32, 40, 48],
    complexity="O(fourth root of n) expected",
    setup=make_semiprime,
    requires=requires_all(primes_module, factorization_module),
    note=(
        "Pollard's rho on a semiprime, which is the hard shape; the sizes "
        "are bit lengths, and the cost grows as the fourth root of the value"
    ),
)
def pollard_rho(value: int) -> Any:
    """Factor a semiprime by Pollard's rho."""
    return factorization_module.pollard_rho(value, seed=20260115)


@benchmark(
    group=GROUP_FACTORIZATION,
    sizes=[32, 48, 64],
    complexity="fast when the factors are near the square root",
    setup=make_close_semiprime,
    requires=requires_all(primes_module, factorization_module),
    note="the family Fermat's method is designed for, where it wins",
)
def fermat_factor_close(value: int) -> Any:
    """Factor a product of two nearby primes by Fermat's method."""
    return factorization_module.fermat_factor(value)


@benchmark(
    group=GROUP_FACTORIZATION,
    sizes=[32, 40],
    complexity="slow when the factors are far apart",
    setup=make_semiprime,
    requires=requires_all(primes_module, factorization_module),
    note=(
        "the same method on a random semiprime, where it is the wrong "
        "choice; the ratio against the benchmark above is the reference's "
        "claim about it"
    ),
)
def fermat_factor_random(value: int) -> Any:
    """Factor a random semiprime by Fermat's method."""
    return factorization_module.fermat_factor(value)


@benchmark(
    group=GROUP_FACTORIZATION,
    sizes=[32, 48, 64],
    complexity="fast when a factor has a smooth predecessor",
    setup=make_smooth_semiprime,
    requires=requires_all(primes_module, factorization_module),
    note="the family Pollard's p minus one is designed for",
)
def pollard_p1(value: int) -> Any:
    """Factor a semiprime with a smooth factor predecessor."""
    return factorization_module.pollard_p1(value, bound=1_000)


@benchmark(
    group=GROUP_FACTORIZATION,
    sizes=[24, 32, 40],
    complexity="O(square root of n)",
    requires=factorization_module,
    note="trial division, for comparison with the methods above",
)
def trial_factor(bits: int) -> Any:
    """Factor an integer by trial division."""
    return factorization_module.trial_factor(random_of_bits(bits, "nt.trialfactor"))


@benchmark(
    group=GROUP_FACTORIZATION,
    sizes=[24, 32, 40],
    complexity="O(number of divisors) from the factorization",
    requires=factorization_module,
)
def divisors(bits: int) -> List[int]:
    """Enumerate every divisor of an integer."""
    return factorization_module.divisors(random_of_bits(min(bits, 40), "nt.divisors"))


@benchmark(
    group=GROUP_FACTORIZATION,
    sizes=[128, 256, 512],
    complexity="O(log cubed n) against exponential",
    requires=requires_all(primes_module, factorization_module),
    note=(
        "the asymmetry the whole of public key cryptography rests on: two "
        "primality tests against one factorization attempt at the same bit "
        "length, with the factorization bounded so the benchmark terminates"
    ),
)
def primality_against_factorization(bits: int) -> Tuple[bool, bool]:
    """Test two primes, then attempt to factor their product briefly."""
    half = bits // 2
    left = primes_module.next_prime(random_of_bits(half, "nt.asym.left"))
    right = primes_module.next_prime(random_of_bits(half, "nt.asym.right"))
    tested = primes_module.is_prime(left) and primes_module.is_prime(right)
    attempted = factorization_module.is_smooth(left * right, bound=10_000)
    return tested, attempted


# ---------------------------------------------------------------------------
# Arithmetic functions
# ---------------------------------------------------------------------------


@benchmark(
    group=GROUP_FUNCTIONS,
    sizes=[24, 32, 40],
    complexity="O(the factorization) plus O(distinct primes)",
    requires=functions_module,
    note="from scratch, which pays for a factorization each time",
)
def euler_totient_cold(bits: int) -> int:
    """Compute the Euler totient of an integer."""
    return functions_module.euler_totient(random_of_bits(bits, "nt.totient"))


@benchmark(
    group=GROUP_FUNCTIONS,
    sizes=[24, 32, 40],
    complexity="O(distinct primes) with the factorization in hand",
    setup=make_factorization_cache,
    requires=requires_all(factorization_module, functions_module),
    note=(
        "from a cached factorization, which is what the reference recommends "
        "when several functions are wanted for one argument"
    ),
)
def euler_totient_from_factorization(payload: Tuple[int, Any]) -> int:
    """Compute the totient from a factorization that is already available."""
    value, factors = payload
    return functions_module.euler_totient(value, factorization=factors)


@benchmark(
    group=GROUP_FUNCTIONS,
    sizes=[24, 32, 40],
    complexity="O(the factorization)",
    requires=functions_module,
)
def mobius(bits: int) -> int:
    """Compute the Mobius function of an integer."""
    return functions_module.mobius(random_of_bits(bits, "nt.mobius"))


@benchmark(
    group=GROUP_FUNCTIONS,
    sizes=[24, 32, 40],
    complexity="O(the factorization)",
    requires=functions_module,
)
def divisor_count(bits: int) -> int:
    """Count the divisors of an integer."""
    return functions_module.divisor_count(random_of_bits(bits, "nt.divcount"))


@benchmark(
    group=GROUP_FUNCTIONS,
    sizes=[24, 32, 40],
    complexity="O(the factorization)",
    requires=functions_module,
)
def divisor_sum(bits: int) -> int:
    """Sum the divisors of an integer."""
    return functions_module.divisor_sum(random_of_bits(bits, "nt.divsum"))


@benchmark(
    group=GROUP_FUNCTIONS,
    sizes=[1_000, 10_000, 100_000],
    complexity="O(n log n)",
    requires=functions_module,
    note=(
        "the totient of every integer up to a bound, which a sieve computes "
        "far faster than repeated factorization"
    ),
)
def totient_sieve(limit: int) -> Any:
    """Compute the totient of every integer below a bound."""
    return [functions_module.euler_totient(value) for value in range(1, limit + 1)]


@benchmark(
    group=GROUP_FUNCTIONS,
    sizes=[100, 1_000, 10_000],
    complexity="O(n log n)",
    requires=functions_module,
    note="Dirichlet convolution of two arithmetic functions",
)
def dirichlet_convolution(limit: int) -> Any:
    """Convolve two arithmetic functions up to a bound."""
    return functions_module.dirichlet_convolution(
        functions_module.mobius, lambda value: 1, limit=limit
    )


# ---------------------------------------------------------------------------
# Diophantine equations and sequences
# ---------------------------------------------------------------------------


@benchmark(
    group=GROUP_DIOPHANTINE,
    sizes=[256, 1_024, 4_096],
    complexity="O(log min(a, b))",
    setup=make_coprime_pair,
    requires=diophantine_module,
)
def linear_diophantine(payload: Tuple[int, int]) -> Any:
    """Solve a linear diophantine equation."""
    left, right = payload
    return diophantine_module.linear_diophantine(left, right, 1)


@benchmark(
    group=GROUP_DIOPHANTINE,
    sizes=[100, 1_000, 10_000],
    complexity="O(limit squared) candidate pairs",
    requires=diophantine_module,
)
def pythagorean_triples(limit: int) -> Any:
    """Enumerate the primitive Pythagorean triples below a bound."""
    return diophantine_module.pythagorean_triples(limit, primitive_only=True)


@benchmark(
    group=GROUP_DIOPHANTINE,
    sizes=[64, 256, 1_024],
    complexity="O(log value) division steps",
    requires=diophantine_module,
    note="the continued fraction expansion, which Pell's equation needs",
)
def continued_fraction(bits: int) -> Any:
    """Expand a rational number as a continued fraction."""
    left, right = make_coprime_pair(bits)
    return diophantine_module.continued_fraction(f"{left}/{right}")


@benchmark(
    group=GROUP_DIOPHANTINE,
    sizes=[13, 61, 109],
    complexity="depends on the expansion period",
    requires=diophantine_module,
    note=(
        "Pell's equation, whose fundamental solution can be enormous even "
        "for a small coefficient; sixty one is the classical example"
    ),
)
def pell_equation(coefficient: int) -> Any:
    """Find the fundamental solution of Pell's equation."""
    return diophantine_module.pell(coefficient, limit=1)


@benchmark(
    group=GROUP_SEQUENCES,
    sizes=[10_000, 100_000, 1_000_000],
    complexity="O(n log log n) through a divisor sieve",
    requires=sequences_module,
)
def perfect_numbers(limit: int) -> List[int]:
    """Find the perfect numbers below a bound."""
    return sequences_module.perfect_numbers(limit)


@benchmark(
    group=GROUP_SEQUENCES,
    sizes=[10_000, 100_000],
    complexity="O(n log log n)",
    requires=sequences_module,
)
def amicable_pairs(limit: int) -> Any:
    """Find the amicable pairs below a bound."""
    return sequences_module.amicable_pairs(limit)


@benchmark(
    group=GROUP_SEQUENCES,
    sizes=[100, 500, 2_000],
    complexity="O(n squared) exact rational arithmetic",
    requires=sequences_module,
    note="the Farey sequence, built from mediants",
)
def farey_sequence(order: int) -> Any:
    """Build the Farey sequence of an order."""
    return sequences_module.farey(order)


# ---------------------------------------------------------------------------
# Cryptographic primitives
# ---------------------------------------------------------------------------


@benchmark(
    group=GROUP_CRYPTO,
    sizes=[128, 256, 512],
    complexity="dominated by the primality search",
    requires=crypto_module,
    note=(
        "key generation, which a reader will want to have measured before "
        "running one in a classroom; these are teaching implementations and "
        "must not protect real secrets"
    ),
)
def rsa_keygen(bits: int) -> Any:
    """Generate an RSA key pair."""
    return crypto_module.rsa.generate_keypair(bits=bits, seed=20260115)


@benchmark(
    group=GROUP_CRYPTO,
    sizes=[128, 256, 512],
    complexity="O(log exponent) modular multiplications",
    setup=make_rsa_keypair,
    requires=crypto_module,
    note="encryption with the small public exponent, which is cheap",
)
def rsa_encrypt(keys: Any) -> int:
    """Encrypt an integer with an RSA public key."""
    return crypto_module.rsa.encrypt(42, keys.public)


@benchmark(
    group=GROUP_CRYPTO,
    sizes=[128, 256, 512],
    complexity="O(log exponent) modular multiplications",
    setup=make_rsa_keypair,
    requires=crypto_module,
    note=(
        "decryption with the full private exponent, which is far more "
        "expensive than encryption; the ratio is the reason the public "
        "exponent is chosen small"
    ),
)
def rsa_decrypt(keys: Any) -> int:
    """Decrypt an integer with an RSA private key."""
    cipher = crypto_module.rsa.encrypt(42, keys.public)
    return crypto_module.rsa.decrypt(cipher, keys.private)


@benchmark(
    group=GROUP_CRYPTO,
    sizes=[64, 128, 256],
    complexity="O(divisors of the group order)",
    requires=requires_all(primes_module, crypto_module),
    note="finding a generator of the multiplicative group",
)
def primitive_root(bits: int) -> int:
    """Find a primitive root modulo a prime."""
    prime = primes_module.next_prime(random_of_bits(bits, "nt.primroot"))
    return crypto_module.primitive_root(prime)


@benchmark(
    group=GROUP_CRYPTO,
    sizes=[128, 256, 512],
    complexity="two modular exponentiations per party",
    requires=requires_all(primes_module, crypto_module),
)
def diffie_hellman(bits: int) -> int:
    """Perform a Diffie Hellman key exchange."""
    prime = primes_module.next_prime(random_of_bits(bits, "nt.dh.prime"))
    generator = crypto_module.primitive_root(prime)
    return crypto_module.diffie_hellman.exchange(
        prime, generator, secrets=(12345, 67890)
    )


# ---------------------------------------------------------------------------
# Notes on reading these results
# ---------------------------------------------------------------------------
#
# The comparisons this file exists for:
#
#   modular_exponentiation across the bit lengths. Doubling the bit length
#   doubles the number of multiplications and roughly quadruples the cost of
#   each, so the implied exponent should be near three. What it must never
#   be is linear in the exponent itself, because every public key scheme in
#   the package depends on this operation being logarithmic.
#
#   primality_against_factorization. Two primality tests and one bounded
#   factorization attempt at the same bit length. The tests stay in
#   milliseconds as the size grows and the factorization does not, which is
#   the asymmetry public key cryptography rests on.
#
#   miller_rabin_on_prime against trial_division_primality. Note the sizes
#   rather than the times: the probabilistic test runs at five hundred and
#   twelve bits and trial division at forty, because one is polynomial in
#   the digits and the other is exponential in them.
#
#   fermat_factor_close against fermat_factor_random. The same method on the
#   family it suits and on a family it does not. The reference states that
#   Fermat's method is fast when the factors are near the square root, and
#   this pair is where that statement is earned.
#
#   pollard_rho against trial_factor at the same bit length. The expected
#   fourth root against the square root, which is why rho is the general
#   purpose choice.
#
#   euler_totient_cold against euler_totient_from_factorization. The
#   difference is the factorization, and it is the measurement behind the
#   advice to compute one and reuse it.
#
#   sieve_eratosthenes against sieve_atkin against linear_sieve. Three
#   bounds for one problem. The asymptotically better sieves have worse
#   constants, so the crossover matters more than the exponent, and this is
#   where a reader can see where it falls.
#
#   euclidean against euclidean_worst_case. Consecutive Fibonacci numbers
#   maximize the step count for a given size, so the second is the bound the
#   reference should quote.
#
#   euclidean against binary_gcd. The reference says the binary algorithm is
#   not an advantage in Python, because the division is implemented in C and
#   the shifting is not. If that ever stops being true, this pair is where it
#   will show.
#
#   rsa_encrypt against rsa_decrypt. The public exponent is small and the
#   private one is not, and the ratio explains why every deployment chooses
#   the exponent that way.
