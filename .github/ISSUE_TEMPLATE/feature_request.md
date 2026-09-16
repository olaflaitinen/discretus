---
name: Feature request
about: Propose a new structure, algorithm, interface, or format
title: "feat: "
labels: ["enhancement", "needs triage"]
assignees: []
---

<!--
Thank you for proposing a feature. This template is long because the design
discussion is the expensive part of adding an algorithm, and having it before
any code exists is far cheaper than having it afterwards.

How to use it:

- The sections marked REQUIRED are the ones a design decision cannot be made
  without.
- Everything else is optional. Delete a question rather than leaving it blank
  when it does not apply, and delete a whole section when none of it applies.
- For a closed question, tick one or more of the listed options. Every option
  the project recognizes is listed, so if none fits, use the Other entry and
  say what it should have been.
- For an open question, replace the placeholder text.
- Please use plain punctuation. The repository does not use the long dash
  character or emoji anywhere, including in issues.

A proposal does not have to be complete to be worth filing. An
underspecified proposal for something genuinely useful is more welcome than
a fully specified proposal for something out of scope, and the questions
below exist to find out which it is.
-->

## Section 1. Summary

REQUIRED. Five questions that let a maintainer judge the proposal before
reading any detail.

**1.1 In one sentence, what do you want to be able to do?**
Phrase it as the capability rather than the implementation. A good answer
reads like "compute the Tutte polynomial of a graph" rather than "add a
deletion contraction recursion".

> Your answer here.

**1.2 What would the call look like?**
One line of Python is enough at this stage. A concrete call makes the scope
of the proposal immediately clear.

```python
# Your sketch here.
```

**1.3 Is this a new capability or a change to an existing one?**

- [ ] A new routine
- [ ] A new structure or type
- [ ] A new subpackage
- [ ] A new interchange format
- [ ] A new rendering backend
- [ ] An addition to an existing routine, for instance a new argument
- [ ] A change to the behaviour of an existing routine
- [ ] A change to a signature or a return type
- [ ] A performance improvement with no behaviour change
- [ ] A documentation addition
- [ ] Other (explain)

**1.4 Did you search the existing issues and the reference?**
The library is large, and the capability may already exist under a name you
did not expect.

- [ ] Yes, and I found nothing
- [ ] Yes, and I found something related (give the number below)
- [ ] Yes, and I found something close but not sufficient (explain below)
- [ ] No
- [ ] Other (explain)

**1.5 Related issues, discussions, or reference sections.**

> Your answer here.

## Section 2. Motivation

REQUIRED. Eight questions. The project adds capability in response to a
need, and this section is where the need is established.

**2.1 What are you trying to achieve?**
Describe the task rather than the feature. The maintainer may know a
different route to the same end.

> Your answer here.

**2.2 What do you do today instead?**
Pick every option that applies.

- [ ] I implement it myself outside the library
- [ ] I use another library for this part
- [ ] I compose several existing routines awkwardly
- [ ] I do it by hand
- [ ] I avoid the problem
- [ ] Nothing, I have no workaround
- [ ] Other (explain)

**2.3 If you implement it yourself, how long is your implementation?**
A short workaround argues for documenting the composition; a long one
argues for adding the feature.

> Your answer here.

**2.4 Who else would use this?**
The library serves learners, educators, and practitioners, and a feature
that serves one of them well is worth adding.

- [ ] Learners working through a course
- [ ] Educators preparing material or assessment
- [ ] Researchers
- [ ] Practitioners in production systems
- [ ] Only me, as far as I know
- [ ] Other (explain)

**2.5 How often would it be used?**
A rarely used routine is still worth adding when it is a standard part of
the subject, and knowing the frequency helps decide where it lives.

- [ ] In almost every program that touches this domain
- [ ] Regularly
- [ ] Occasionally
- [ ] Rarely, but it is a standard part of the subject
- [ ] I do not know

**2.6 Is this part of a standard curriculum or a standard reference?**
The library's scope is the classical content of discrete mathematics, so a
standard topic has a strong claim.

- [ ] Yes, it is standard textbook material (cite it below)
- [ ] Yes, it is standard in research practice
- [ ] It is specialized but well established
- [ ] It is recent or non standard
- [ ] I do not know

**2.7 Cite the reference that establishes it as standard, if you can.**

> Your answer here.

**2.8 What goes wrong if this is not added?**

- [ ] I cannot use the library for my task at all
- [ ] I keep a workaround that duplicates library internals
- [ ] I depend on a second library for one routine
- [ ] It is merely less convenient
- [ ] Other (explain)

## Section 3. Proposed interface

REQUIRED. Eleven questions. The interface is the part that cannot be changed
later without a breaking release, so it gets the most attention in review.

**3.1 Propose the full signature, with annotations.**
Include the parameter names, the defaults, and the return type.

```python
# Your proposed signature here.
```

**3.2 Where should it live?**
Give the intended import path, for instance
`discretus.graphs.properties.tutte_polynomial`. The subpackages mirror how
the subject is taught.

> Your answer here.

**3.3 Should it be a free function, a method, or a class?**
The library uses free functions for algorithms and methods for the intrinsic
properties of a structure, and a class when there is state worth naming.

- [ ] A free function
- [ ] A method on an existing type
- [ ] A new class
- [ ] A classmethod or an alternative constructor
- [ ] A property
- [ ] Other (explain)

**3.4 If it is a method, on which type?**

> Your answer here.

**3.5 What should it return?**
Name the type and its shape. The library prefers concrete containers over
iterators unless the routine is documented as lazy.

> Your answer here.

**3.6 Should it be lazy or eager?**
Anything whose output can grow exponentially is a generator in this library,
and the caller materializes it explicitly when the space is small.

- [ ] Eager, the output is bounded
- [ ] Lazy, the output can be large
- [ ] Both, as two routines with different names
- [ ] I do not know

**3.7 Does the proposal need new arguments on existing routines?**
Adding a keyword argument with a default is backward compatible, and
changing a default is not.

- [ ] No
- [ ] Yes, a new keyword argument with a default
- [ ] Yes, a new required argument
- [ ] Yes, and it changes an existing default
- [ ] Other (explain)

**3.8 What should the routine be called?**
The library names routines after the mathematics they encode, spelled out
rather than abbreviated.

> Your answer here.

**3.9 Are there alternative names worth considering?**
Naming is most of interface design, and listing the alternatives makes the
choice reviewable.

> Your answer here.

**3.10 Is the argument order consistent with the surrounding module?**
Where a routine takes a structure and a parameter, the structure comes
first.

- [ ] Yes
- [ ] No, and here is why the deviation is justified
- [ ] I am not sure

**3.11 Sketch a complete usage example.**
Ten lines that a reader could run. This often exposes an interface problem
that the signature alone hides.

```python
# Your example here.
```

## Section 4. Mathematical definition

REQUIRED. Eleven questions. The library implements mathematics, so the
definition is the specification.

**4.1 State the definition or the theorem precisely.**
In words or in notation. This becomes the first paragraph of the docstring.

> Your answer here.

**4.2 Which domain does it belong to?**

- [ ] Set theory
- [ ] Mathematical logic
- [ ] Combinatorics
- [ ] Graph theory
- [ ] Number theory
- [ ] Recurrence relations
- [ ] Abstract algebra
- [ ] It spans several domains
- [ ] It is a cross cutting utility
- [ ] Other (explain)

**4.3 What are the preconditions on the input?**
Every documented precondition becomes a validation check and a raised
exception, so stating them here writes part of the implementation.

> Your answer here.

**4.4 What should happen on the empty input?**
The library treats the empty case as ordinary: the empty sum is zero, the
empty product is one, and the empty relation is vacuously transitive.

> Your answer here.

**4.5 What should happen on the degenerate cases?**
Pick every case that is meaningful here, and say what each should produce.

- [ ] A singleton structure
- [ ] A modulus of one
- [ ] A zero exponent
- [ ] A negative argument
- [ ] A disconnected graph
- [ ] A zero or negative weight
- [ ] A repeated element or root
- [ ] The identity element
- [ ] None of these apply
- [ ] Other (explain)

**4.6 Is the result unique, or is any valid answer acceptable?**
A minimum spanning tree is not unique while its total weight is, and the
distinction decides what a test can assert.

- [ ] Unique
- [ ] Not unique, and any valid answer is acceptable
- [ ] Not unique, and a specific canonical answer should be chosen
- [ ] I do not know

**4.7 If a canonical answer is wanted, which one?**
For instance the lexicographically least, or the one with the smallest
representative.

> Your answer here.

**4.8 Should the result be exact?**
The library computes exactly wherever the mathematics is exact, over
unbounded integers and exact rationals.

- [ ] Yes, exactly, over the integers
- [ ] Yes, exactly, over the rationals
- [ ] Exact where possible and approximate otherwise, with the tolerance documented
- [ ] Necessarily approximate, and here is why
- [ ] Other (explain)

**4.9 Does the routine need a ground set, a universe, or a modulus supplied?**
The library requires these explicitly rather than inferring them, because
the answer depends on them.

- [ ] Yes (say which below)
- [ ] No
- [ ] Optionally, with a documented default

**4.10 Which established results does it rely on?**
Naming them lets the implementation cite them in its docstring, which is
what makes a reference implementation readable.

> Your answer here.

**4.11 Is there a worked example with a known answer?**
A textbook example with a published value is the best first test.

> Your answer here.

## Section 5. Algorithm and complexity

REQUIRED. Ten questions. The reference states the complexity of every
nontrivial routine, so it has to be known before the routine is accepted.

**5.1 Which algorithm should be used?**
Name it. If it has an author's name, use it, since that is how the library
names its modules.

> Your answer here.

**5.2 What is its time complexity?**
State it in the quantities that matter, for instance the vertex and edge
counts rather than a bare letter.

> Your answer here.

**5.3 What is its space complexity?**

> Your answer here.

**5.4 Is the problem tractable in general?**
Several routines in this library are exponential because the problems are
hard, and that is documented rather than hidden.

- [ ] Polynomial
- [ ] Polynomial with a large exponent
- [ ] Exponential, and unavoidably so
- [ ] Exponential in the worst case and fast in practice
- [ ] Subexponential
- [ ] Undecidable in general, and decidable for the finite case here
- [ ] I do not know

**5.5 Is there a better algorithm that is harder to read?**
The library ships a transparent reference implementation and a tuned one
where the distinction is instructive, and validates the second against the
first.

- [ ] No, one algorithm is both clear and efficient
- [ ] Yes, and both should be shipped
- [ ] Yes, and only the readable one is needed for now
- [ ] Other (explain)

**5.6 Is there a heuristic worth shipping alongside the exact routine?**
The pattern in the library is an exact routine with its complexity stated
and a polynomial heuristic next to it.

- [ ] Yes (name it below)
- [ ] No
- [ ] I do not know

**5.7 Does the algorithm need randomness?**
Every randomized routine in the library takes a seed and is deterministic
once it is supplied.

- [ ] No
- [ ] Yes, and it should accept a seed
- [ ] Yes, and it is a Monte Carlo method whose error should be documented
- [ ] Other (explain)

**5.8 Which representation does the algorithm want?**
The choice between an adjacency list, an adjacency matrix, an edge list, and
an incidence matrix is a factor of the input size.

- [ ] An adjacency list
- [ ] An adjacency matrix
- [ ] An edge list
- [ ] An incidence matrix
- [ ] A clause list
- [ ] A factorization
- [ ] Not relevant
- [ ] Other (explain)

**5.9 Can it reuse an existing routine in the library?**
Building on what exists keeps the implementation short and keeps the
behaviour consistent.

> Your answer here.

**5.10 Does it belong in the core layer or in a domain package?**
The core layer holds what models mathematics and is shared; a domain package
holds what belongs to one subject. Domain packages never import one another.

- [ ] In a domain package
- [ ] In the core layer, because several domains need it
- [ ] In the utility package, because it is engineering rather than mathematics
- [ ] I do not know

## Section 6. Correctness and testing

REQUIRED. Nine questions. A new algorithm is accepted with its validation,
not before it.

**6.1 How can the result be validated independently?**
Pick every option that applies. Cross validation on randomized inputs is
required for a new algorithm that duplicates an existing result.

- [ ] Against a naive implementation on randomized inputs
- [ ] Against another routine in this library that must agree
- [ ] Against a published table of values
- [ ] Against an independent library
- [ ] By a property or an identity that must hold
- [ ] By exhaustive enumeration for small cases
- [ ] By hand computation for small cases
- [ ] Other (explain)

**6.2 Which properties or laws must the result satisfy?**
These become property based tests, which are stronger than examples.

> Your answer here.

**6.3 Which small cases have known answers?**
List the inputs and the expected outputs. These become the first unit tests.

> Your answer here.

**6.4 Is there an identity that links it to an existing routine?**
An identity across two independently implemented routines is the strongest
test available.

> Your answer here.

**6.5 Which degenerate cases should be tested explicitly?**
The empty structure, the singleton, and the boundary values are where
defects concentrate.

> Your answer here.

**6.6 Can the answer be verified more cheaply than it can be computed?**
When it can, the verification belongs in the test suite and sometimes in the
routine itself.

- [ ] Yes (explain below)
- [ ] No
- [ ] I do not know

**6.7 Should the routine be able to verify its own output?**
The satisfiability model does this, and it is why a solver defect surfaces
as a failed verification rather than as a wrong answer.

- [ ] Yes
- [ ] No
- [ ] Other (explain)

**6.8 Should it support step recording?**
Selected routines can record their derivation, which is what makes them
usable for teaching.

- [ ] Yes, the intermediate steps are instructive
- [ ] No
- [ ] Other (explain)

**6.9 Is a benchmark worth adding?**
The benchmark suite tracks performance across releases and guards against
regressions.

- [ ] Yes
- [ ] No
- [ ] Other (explain)

## Section 7. Errors and edge behaviour

Optional, seven questions. The exception a routine raises is part of its
interface.

**7.1 Which exception should an invalid input raise?**
Pick every option that applies. The hierarchy is documented in
`discretus.exceptions`.

- [ ] `ValidationError`, for a wrong type or shape
- [ ] `DomainError`, for a value outside the mathematical domain
- [ ] `DimensionError`, for incompatible shapes
- [ ] `AxiomViolationError`, for a structure that fails an axiom
- [ ] `NotAFunctionError`, for a relation that is not single valued
- [ ] `ParseError`, for malformed text
- [ ] `InfeasibleError`, when the requested object does not exist
- [ ] `LimitExceededError`, when an enumeration bound is reached
- [ ] `ConvergenceError`, when an iteration does not converge
- [ ] A new exception type is needed (explain below)
- [ ] Other (explain)

**7.2 When the object does not exist, should the routine raise or return nothing?**
The library raises `InfeasibleError` when absence is exceptional and returns
`None` when absence is an ordinary outcome a caller will branch on.

- [ ] Raise, absence is exceptional
- [ ] Return `None`, absence is ordinary
- [ ] Return an empty container
- [ ] Other (explain)

**7.3 Should the enumeration limit apply?**
The limit protects a caller from materializing a structure large enough to
kill the process, and it does not apply to lazy iteration.

- [ ] Yes
- [ ] No, the routine is lazy
- [ ] No, the output is bounded by the input
- [ ] I do not know

**7.4 What should the error message contain?**
The library's messages name the offending value and the condition it
violated, in the terms of the mathematics.

> Your answer here.

**7.5 Are there inputs where the correct behaviour is genuinely ambiguous?**
Saying so early prevents a disagreement in review.

> Your answer here.

**7.6 Should validation be skippable under `strict_validation`?**
Checks that cost as much as the computation they guard consult the
configuration and become no operations when a caller opts out.

- [ ] Yes, the check is expensive
- [ ] No, the check is cheap and should always run
- [ ] Other (explain)

**7.7 Does the routine need to guard against an adversarial input?**
Relevant if it will be reachable from user supplied data, which the security
policy discusses.

- [ ] Yes
- [ ] No
- [ ] I do not know

## Section 8. Dependencies and packaging

Optional, six questions. The computational core will not gain a mandatory
third party dependency within a major version.

**8.1 Does the proposal need a third party package?**

- [ ] No, the standard library suffices
- [ ] Yes, and it belongs behind the `viz` extra
- [ ] Yes, and it belongs behind a new extra
- [ ] Yes, and it would have to be mandatory
- [ ] I do not know

**8.2 Which package, and why is it necessary?**
A dependency that saves a hundred lines is usually not worth it here, and
one that provides a rendering backend or a native accelerator may be.

> Your answer here.

**8.3 Can the feature degrade gracefully without it?**
The pattern is an import inside the function that needs it, raising
`OptionalDependencyError` with the extra to install.

- [ ] Yes, it can raise a clear error when absent
- [ ] Yes, a reduced version works without it
- [ ] No, the feature is the dependency
- [ ] Other (explain)

**8.4 Does it need a system binary rather than a Python package?**
The Graphviz renderer is the existing precedent, and its binaries cannot be
installed by pip.

- [ ] Yes (name it below)
- [ ] No

**8.5 Does it need a new interchange format to be read or written?**

- [ ] No
- [ ] Yes, reading only
- [ ] Yes, writing only
- [ ] Yes, both

**8.6 Does it need to be exposed in the command line interface?**
The interface exists for one shot tasks in shell pipelines and grading
scripts.

- [ ] Yes
- [ ] No
- [ ] Other (explain)

## Section 9. Compatibility and stability

Optional, eight questions. The public interface is backward compatible
within a major version.

**9.1 Is the proposal backward compatible?**

- [ ] Yes, it adds interface only
- [ ] It changes behaviour that was documented
- [ ] It changes behaviour that was undocumented
- [ ] It changes a signature
- [ ] It changes a return type
- [ ] It removes interface
- [ ] I do not know

**9.2 If it is not compatible, what is the migration path?**
A breaking change needs a deprecation with a warning that names its
replacement and the release in which it will be removed.

> Your answer here.

**9.3 Does it change the result of any existing routine?**
A changed documented result is a breaking change unless the old result was
demonstrably wrong.

- [ ] No
- [ ] Yes, and the old result was wrong
- [ ] Yes, and both results are defensible
- [ ] I do not know

**9.4 Does it change a documented complexity?**
An improvement is welcome and still needs the reference updated.

- [ ] No
- [ ] Yes, it improves one
- [ ] Yes, it worsens one
- [ ] I do not know

**9.5 Does it change the order of any returned collection?**
Order is part of the documented behaviour, because ranking and unranking
depend on it.

- [ ] No
- [ ] Yes (explain below)
- [ ] I do not know

**9.6 Does it affect determinism or exactness anywhere?**

- [ ] No
- [ ] Yes (explain below)
- [ ] I do not know

**9.7 Which release would be appropriate?**

- [ ] A patch release
- [ ] The next minor release
- [ ] The next major release
- [ ] I do not know

**9.8 Should it be marked experimental at first?**
An interface marked experimental is not yet covered by the compatibility
guarantee, which is a reasonable way to ship something whose shape is not
settled.

- [ ] Yes
- [ ] No
- [ ] Other (explain)

## Section 10. Documentation

Optional, seven questions. A routine that is not documented does not exist
as far as a user is concerned.

**10.1 Which reference page would gain an entry?**

> Your answer here.

**10.2 Does it deserve a section in a tutorial?**

- [ ] Yes, in an existing tutorial (name it below)
- [ ] Yes, and it justifies a new tutorial
- [ ] No, a reference entry is enough
- [ ] Other (explain)

**10.3 Would an example script be useful?**
The `examples/` directory holds runnable programs, each focused on one
topic, and the documentation build executes every one of them.

- [ ] Yes
- [ ] No

**10.4 Should the docstring include a doctest?**
Every public routine carries one, and the documentation job runs them all.

- [ ] Yes, and here is a candidate
- [ ] Yes, and I cannot think of a small enough one
- [ ] Other (explain)

**10.5 Propose the doctest.**
Small enough that a reader can verify it by hand.

```python
# Your doctest here.
```

**10.6 Does the feature need a figure?**
The visualization package can draw graphs, Hasse diagrams, lattices, truth
tables, and Karnaugh maps.

- [ ] Yes
- [ ] No

**10.7 Does it change anything in the README?**
The README states the mathematical scope, and a genuinely new capability may
belong in it.

- [ ] Yes
- [ ] No

## Section 11. Alternatives and prior art

Optional, eight questions. Knowing what was considered and rejected is part
of the design record.

**11.1 What alternatives did you consider?**

> Your answer here.

**11.2 Why are they less suitable?**

> Your answer here.

**11.3 Could the capability be achieved by composing existing routines?**
If it can, the outcome may be a documentation change rather than new code,
which is a good outcome.

- [ ] No
- [ ] Yes, but the composition is awkward (show it below)
- [ ] Yes, and it is reasonable
- [ ] I do not know

**11.4 Show the composition, if one exists.**

```python
# Your composition here.
```

**11.5 Which other libraries provide this?**
Naming them is useful for comparing interfaces, and this library does not
aim to copy any of them.

> Your answer here.

**11.6 How do they name it, and what do they return?**
An established name is worth adopting when it does not conflict with the
conventions here.

> Your answer here.

**11.7 Is there a reference implementation you can point at?**
A link to code in a paper or another project speeds up the implementation.

> Your answer here.

**11.8 Is the feature better served by a separate package?**
Some proposals are good ideas and out of scope for a library whose core has
no dependencies, and saying so early is not a rejection of the idea.

- [ ] It belongs in this library
- [ ] It could be a separate package that builds on this one
- [ ] I do not know

## Section 12. Implementation and contribution

Optional, seven questions.

**12.1 Would you like to implement it?**

- [ ] Yes, I would like to open a pull request
- [ ] Yes, with guidance on where to start
- [ ] Yes, if the interface is agreed first
- [ ] No, I am proposing it only
- [ ] I cannot, for policy or time reasons
- [ ] Other (explain)

**12.2 Have you read CONTRIBUTING.md?**
It contains the ten step procedure for adding an algorithm, which answers
most questions an implementer has.

- [ ] Yes
- [ ] No
- [ ] Not applicable

**12.3 How large do you expect the change to be?**

- [ ] One file
- [ ] A few files in one subpackage
- [ ] A new subpackage
- [ ] Changes across several packages
- [ ] I do not know

**12.4 Which parts would you want help with?**
Pick every option that applies.

- [ ] The interface design
- [ ] The algorithm
- [ ] The tests
- [ ] The documentation
- [ ] The benchmarks
- [ ] None, I can do all of it
- [ ] Other (explain)

**12.5 Do you have a timeline?**
The project makes no schedule commitment, and knowing yours helps with
ordering.

> Your answer here.

**12.6 Would a partial implementation be useful?**
Shipping the common case first, with the general case documented as not yet
supported, is often the right first step.

- [ ] Yes
- [ ] No, it is all or nothing
- [ ] Other (explain)

**12.7 Are you able to sign off that your contribution is yours to give?**
Contributions are accepted under the Mozilla Public License 2.0, and a
contribution copied from an incompatibly licensed source cannot be
accepted.

- [ ] Yes, the work would be my own
- [ ] It would be derived from a source I will name
- [ ] I do not know

## Section 13. Final checklist

REQUIRED. Seven boxes.

- [ ] I have stated the capability in one sentence and sketched the call
- [ ] I have stated the mathematical definition
- [ ] I have named the algorithm and its complexity, or said that I do not know
- [ ] I have said how the result can be validated independently
- [ ] I have checked that the capability does not already exist under another name
- [ ] I have confirmed that the feature fits one of the seven documented domains,
      or explained why it belongs anyway
- [ ] I have used plain punctuation, with no long dash characters and no emoji

## Section 14. Anything else

**14.1 Is there anything else a maintainer should know?**
Context about the work the feature would serve often suggests a better
design than the one proposed.

> Your answer here.
