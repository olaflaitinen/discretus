# Security Policy

discretus is a computational library. It has no mandatory third party
dependencies, it opens no sockets, it starts no subprocesses during a
computation, and it needs no credentials. That narrow surface shapes this
policy: the realistic risks are concentrated in the places where the library
reads data it did not produce, and in the way its teaching oriented
cryptographic primitives might be misused.

This document states which versions receive fixes, how to report a problem,
what happens after you report it, and which classes of problem are in scope.

## Table of contents

1. [Supported versions](#supported-versions)
2. [Reporting a vulnerability](#reporting-a-vulnerability)
3. [What to include in a report](#what-to-include-in-a-report)
4. [Our response](#our-response)
5. [Disclosure process](#disclosure-process)
6. [Scope](#scope)
7. [Out of scope](#out-of-scope)
8. [Cryptographic primitives](#cryptographic-primitives)
9. [Deserialization and untrusted input](#deserialization-and-untrusted-input)
10. [Resource exhaustion](#resource-exhaustion)
11. [Hardening guidance for deployments](#hardening-guidance-for-deployments)
12. [Supply chain](#supply-chain)
13. [Recognition](#recognition)

## Supported versions

Security fixes are provided for the most recent minor release of the current
major version. An older minor release receives a fix only when the issue is
severe and a straightforward backport exists.

| Version | Supported | Notes |
| --- | --- | --- |
| 1.0.x | Yes | Current release series |
| Older than 1.0 | No | Pre release versions, upgrade instead |

The project follows semantic versioning, so a security fix that does not
change the public interface arrives as a patch release and is safe to take
without code changes on your side. When a fix has to change documented
behavior, the change and its reason are stated in the changelog and in the
release notes.

## Reporting a vulnerability

Please do not open a public issue for a security problem, and please do not
describe it in a discussion, a pull request, or a social media post before
it has been addressed.

Report it privately by email:

- Address: yimanov@student.uef.fi
- Subject line: `discretus security report`

If you prefer a forge based channel, the repository accepts private
vulnerability reports through the security advisory mechanism of the hosting
platform, which keeps the report invisible until an advisory is published.

You will receive an acknowledgement that a human has read your report. If
you do not hear back within five working days, please send a short follow up
in case the first message was filtered.

## What to include in a report

A report that contains the following can usually be triaged in one pass
rather than several.

- The version of discretus, from
  `python -c "import discretus; print(discretus.__version__)"`.
- The interpreter version and the operating system.
- Which optional extras are installed, if any.
- A minimal program that demonstrates the problem, ideally under twenty
  lines and free of third party imports.
- The input that triggers it. If the input is large or awkward to paste,
  describe how to generate it deterministically, for example with a seed.
- What you expected to happen and what happened instead.
- Your assessment of the impact, if you have one. It is useful even when it
  is uncertain, because it tells us how you expect the library to be used.
- Whether you intend to publish, and on what timeline. We will work to it if
  it is reasonable, and we will tell you if it is not.

Please do not include real secrets, production data, or personal data in a
report. If a reproduction genuinely requires such data, say so and we will
agree on a way to handle it.

## Our response

1. Acknowledgement within five working days.
2. Triage and a severity assessment within ten working days, using the
   Common Vulnerability Scoring System as a shared vocabulary rather than as
   a verdict.
3. A written decision on whether the report is in scope, with the reasoning.
   A report judged out of scope is still answered, and if it describes a
   genuine defect it becomes an ordinary issue with your agreement.
4. A fix prepared privately, together with a regression test that fails
   before it and passes after it.
5. A patched release, an advisory, and a changelog entry.

Throughout, you will be told what is happening. Silence is a failure of this
process, not a stage of it.

## Disclosure process

The project practices coordinated disclosure.

1. The report stays private while the fix is prepared.
2. A fix is developed on a private branch and reviewed there.
3. A release is published, with the advisory and the changelog entry.
4. Details are disclosed publicly after the release, normally within ninety
   days of the original report and sooner when the fix is straightforward.
5. The reporter is credited by the name and link they choose, or remains
   anonymous if they prefer.

If a problem is already public when it reaches us, or is being exploited, we
will shorten this timeline and say so.

## Scope

The following are in scope and will be treated as security issues.

**Untrusted input handling in the parsers and readers.** The library reads
several textual formats, and a malformed or hostile input should raise a
library exception rather than crash the interpreter, corrupt an object, or
consume unbounded resources. The relevant entry points are:

- the propositional formula parser in `discretus.logic.propositional`,
- the predicate formula parser in `discretus.logic.predicate`,
- the DIMACS reader in `discretus.logic.sat`,
- the GraphML, GML, JSON, CSV, edge list, and adjacency readers in
  `discretus.io`.

**Unbounded resource consumption from a modest input.** A small input that
causes a routine to allocate or compute without limit is in scope, because a
service that accepts user supplied formulas or graphs can be taken down by
it. The configured enumeration limit exists precisely to bound this, and a
path that bypasses it is a defect.

**Incorrect results that have a security consequence.** A wrong answer is
normally an ordinary defect. It becomes a security issue when a caller would
reasonably rely on it for a security decision, for instance a primality test
that reports a composite as prime, or a satisfiability solver that reports a
formula unsatisfiable when a model exists.

**Code execution through data.** Any path where reading a file or a string
leads to evaluation of attacker controlled code is in scope and would be
treated as critical. The library does not use `eval`, `exec`, or
`pickle.loads` on data in its ordinary paths, and a report showing otherwise
is welcome.

**Dependency vulnerabilities in the optional extras** that affect a
documented use of the library, for instance a rendering backend that
executes content from a graph label.

## Out of scope

The following are not security issues here, although some of them are
legitimate ordinary issues.

- Deliberate misuse of `discretus.io.pickle_io` on untrusted data. The
  module documents that Python pickle is unsafe for untrusted input and
  exists only for trusted local caching. That documented limitation is not
  a vulnerability.
- The teaching cryptographic primitives being unsuitable for production.
  See the next section; this is a documentation matter by design.
- Slow performance that is inherent to the problem. Exponential behavior in
  satisfiability, in exact graph coloring, or in exhaustive enumeration is
  the mathematics rather than a defect, and each such routine documents its
  complexity. A resource limit bypass in a routine documented as polynomial
  is different and is in scope.
- A report that the library can compute a large object when explicitly asked
  to, for instance the power set of a large ground set after the caller has
  raised the enumeration limit.
- Findings from an automated scanner without a demonstration of impact in a
  documented use of this library.
- Vulnerabilities in a development only dependency that cannot affect a
  user of the published package.
- Issues in a fork, a vendored copy, or a modified version of the library.

## Cryptographic primitives

`discretus.number_theory.crypto` contains textbook implementations of RSA,
ElGamal, and Diffie Hellman, along with primitive roots, multiplicative
orders, and Lucas sequences. They exist so that a learner can see the number
theory working, and so that an educator can demonstrate the algorithms on
small parameters.

They are not hardened. In particular they make no attempt at constant time
execution, they do not blind their exponentiations, they do not defend
against fault injection or against timing and cache side channels, they do
not implement the padding schemes that real protocols require, and they draw
randomness through a seedable generator that is chosen for reproducibility
rather than for cryptographic strength.

Do not use them to protect real secrets. For production cryptography use a
library built and audited for that purpose. A report that these primitives
are unsuitable for production is a documentation issue, and one that finds a
place where the documentation fails to say so is welcome and will be fixed
promptly.

The number theoretic routines these primitives are built on, for instance
modular exponentiation, the extended Euclidean algorithm, Miller Rabin
primality testing, and integer factorization, are correctness critical and
are in scope as described above. A wrong result from any of them is a
serious defect regardless of the cryptographic context.

## Deserialization and untrusted input

If your application feeds user supplied data into discretus, the following
reflects how the library is built and is the basis on which reports are
judged.

- Every reader validates structure before building an object, and raises
  `ParseError` or `SerializationError` with the position or the offending
  element when it cannot.
- No reader evaluates its input as code, and none imports a module named by
  its input.
- JSON is read through the standard library parser, and the resulting
  structure is validated against the expected shape rather than trusted.
- The pickle helper is the single exception and is documented as unsafe for
  untrusted data. Prefer JSON or one of the graph interchange formats when
  the source is not under your control.
- A reader never writes to the filesystem, and it never follows a reference
  in its input to an external location.

## Resource exhaustion

Two mechanisms bound the work a single call can do, and both are relevant
when the library sits behind a network service.

**The enumeration limit.** `discretus.config.Config.max_enumeration` caps
the number of objects a routine will materialize, and the guard raises
`LimitExceededError` rather than allocating. Set it deliberately in a
service. A generous default is right for interactive use and wrong for a
public endpoint.

```python
from discretus.config import set_config

set_config(max_enumeration=10_000, strict_validation=True)
```

**The recursion bound.** `Config.max_recursion_depth` sits below the
interpreter limit so that a deep structure produces a library error rather
than a `RecursionError` from the interpreter, which is harder to handle
safely.

Beyond these, apply the usual controls outside the library: a timeout on the
request, a memory limit on the worker, and a bound on the size of the input
you accept. The library cannot enforce a wall clock limit on your behalf,
because it holds the interpreter for the duration of an exact computation.

## Hardening guidance for deployments

If you expose discretus to untrusted input, the following configuration is a
reasonable starting point.

- Keep `strict_validation` enabled, so that preconditions are checked even
  where the check is comparatively expensive.
- Lower `max_enumeration` to the largest structure your service legitimately
  needs.
- Set an explicit `default_seed` if you need reproducibility, and understand
  that a fixed seed makes randomized routines predictable, which is
  acceptable for benchmarks and grading and not for anything adversarial.
- Prefer the exact routines over any floating point path, so that results do
  not depend on the platform.
- Read untrusted graphs through the interchange formats rather than through
  the pickle helper.
- Run the computation in a worker with a memory limit and a timeout, and
  treat a killed worker as a request level failure rather than a crash.
- Pin the version and watch the changelog, which records every security
  relevant change.

## Supply chain

The following measures protect the path from the repository to an installed
package, and reports about any of them are in scope.

- The published package has no runtime dependencies, so the runtime supply
  chain is the interpreter and the standard library.
- Releases are published from a tagged commit by the release workflow, which
  refuses to publish when the tag and the declared version disagree.
- Publication uses trusted publishing rather than a long lived token, so no
  credential for the package index exists in the repository or in a
  maintainer's shell history.
- Every workflow declares a minimal permission set, and the ones that can
  write are limited to the release path.
- Dependency updates arrive as pull requests from an automated account and
  are reviewed like any other change.
- A scheduled workflow audits the development requirements for known
  vulnerabilities, and the code scanning workflow runs the security and
  quality query suite.
- Tags for releases are signed, and the commit that bumps the version is
  part of the tagged history.

If you find a way to influence a published artifact without going through
review, that is a critical report and we want to hear it immediately.

## Recognition

We are grateful for careful reports and we say so publicly. With your
agreement, a fixed report is credited in the advisory and in the changelog
entry, by the name and link you choose. If you prefer to stay anonymous,
that is respected without question.

There is no bug bounty. This is unfunded academic work, and the only reward
available is credit and our thanks.
