---
name: Bug report
about: Report incorrect behavior, a crash, a wrong mathematical result, or a performance regression
title: "bug: "
labels: ["bug", "needs triage"]
assignees: []
---

<!--
Thank you for reporting a defect. This template is long because a complete
report is triaged in one pass and an incomplete one takes several rounds of
questions. You are not expected to answer every question.

How to use it:

- The sections marked REQUIRED are the ones a maintainer cannot work without.
- Everything else is optional. Delete a question rather than leaving it blank
  when it does not apply, and delete a whole section when none of it applies.
- For a closed question, tick one or more of the listed options. Every option
  the project recognizes is listed, so if none fits, use the Other entry and
  say what it should have been.
- For an open question, replace the placeholder text.
- Please use plain punctuation. The repository does not use the long dash
  character or emoji anywhere, including in issues.

If your report concerns a security vulnerability, do not file it here. See
SECURITY.md and write to yimanov@student.uef.fi instead.
-->

## Section 1. Summary

REQUIRED. Four questions that let a maintainer understand the report before
reading any detail.

**1.1 In one sentence, what goes wrong?**
State the symptom, not the suspected cause. A good answer reads like
"factorize returns an incomplete factorization for a perfect square" rather
than "the factorization cache is broken".

> Your answer here.

**1.2 Which single routine or object is at the centre of the problem?**
Give the full import path if you know it, for example
`discretus.number_theory.factorization.factorize`. If you do not know, name
the operation you were performing.

> Your answer here.

**1.3 Is this the first time you have reported this problem?**
Duplicate reports are welcome when they add information, and knowing helps
the maintainer link them.

- [ ] Yes, this is a new report
- [ ] No, it extends an existing issue (give the number below)
- [ ] I am not sure
- [ ] Other (explain)

**1.4 Did you search the existing issues before filing?**
A link to a related issue is useful even when it is not the same problem.

- [ ] Yes, and I found nothing related
- [ ] Yes, and I found something related (give the number below)
- [ ] Yes, and I found what may be a duplicate (give the number below)
- [ ] No
- [ ] Other (explain)

**1.5 Related issue or discussion numbers, if any.**
List them so that the maintainer can read the earlier context.

> Your answer here.

## Section 2. Classification

REQUIRED. Six closed questions that route the report to the right area.

**2.1 What kind of defect is this?**
Pick every option that applies. The distinction matters because a wrong
result is treated more urgently than a confusing message.

- [ ] A wrong mathematical result
- [ ] An exception raised where a result was expected
- [ ] A result returned where an exception was expected
- [ ] A crash, a hang, or an unbounded allocation
- [ ] Nondeterministic behavior between runs
- [ ] A performance regression against an earlier version
- [ ] Incorrect or misleading documentation
- [ ] An unclear or unhelpful error message
- [ ] A packaging or installation failure
- [ ] A type annotation that disagrees with the runtime behavior
- [ ] Other (explain)

**2.2 Which package does the problem occur in?**
Pick every option that applies. If you cannot tell, pick the last option.

- [ ] `discretus.core`
- [ ] `discretus.sets`
- [ ] `discretus.logic`
- [ ] `discretus.combinatorics`
- [ ] `discretus.graphs`
- [ ] `discretus.number_theory`
- [ ] `discretus.recurrences`
- [ ] `discretus.algebra`
- [ ] `discretus.viz`
- [ ] `discretus.io`
- [ ] `discretus.utils`
- [ ] The command line interface
- [ ] The packaging or the build
- [ ] The documentation
- [ ] I cannot tell which package

**2.3 Which subpackage, if you can narrow it further?**
Naming the subpackage, for example `graphs.shortest_path` or
`logic.normal_forms`, usually identifies the file.

> Your answer here.

**2.4 How severe is the effect on your work?**
This is your assessment of impact, not a demand for a schedule. It is
genuinely useful for ordering the queue.

- [ ] Blocking: I cannot proceed and no workaround exists
- [ ] Serious: I have a workaround, and it is expensive or unsafe
- [ ] Moderate: I have a reasonable workaround
- [ ] Minor: it is an inconvenience
- [ ] Cosmetic: it does not affect results
- [ ] Other (explain)

**2.5 Could a user of this library be misled into believing a wrong result?**
A silently wrong answer is the worst class of defect in a mathematics
library, and it is prioritized accordingly.

- [ ] Yes, the wrong result looks plausible and would not be noticed
- [ ] Yes, but the wrong result is obviously wrong
- [ ] No, the problem announces itself with an exception
- [ ] I am not sure
- [ ] Other (explain)

**2.6 Does the problem affect correctness, performance, or usability?**
Pick every option that applies.

- [ ] Correctness of a returned value
- [ ] Correctness of a raised exception
- [ ] Time taken
- [ ] Memory used
- [ ] Reproducibility between runs or machines
- [ ] Clarity of the interface or the message
- [ ] Other (explain)

## Section 3. Environment

REQUIRED. Twelve questions. Several defects turn out to be version specific,
and the answers here are what make that visible.

**3.1 Which version of discretus?**
Run `python -c "import discretus; print(discretus.__version__)"` and paste
the output.

> Your answer here.

**3.2 Which git revision, if you installed from source?**
Run `python -c "from discretus._version import full_version; print(full_version())"`
or `git rev-parse --short HEAD`.

> Your answer here.

**3.3 Which Python version?**
Run `python --version`. The supported range is 3.9 through 3.13.

> Your answer here.

**3.4 Which interpreter implementation?**
The library is pure Python and runs on several implementations, and a defect
that appears on only one of them is a useful clue.

- [ ] CPython
- [ ] PyPy
- [ ] GraalPy
- [ ] Pyodide or another WebAssembly runtime
- [ ] Other (explain)

**3.5 Which operating system and version?**
For example Ubuntu 24.04, macOS 15.1, Windows 11 24H2.

> Your answer here.

**3.6 Which processor architecture?**
The library has no compiled parts, so this rarely matters, and when it does
the cause is usually the interpreter build rather than the library.

- [ ] x86-64
- [ ] ARM64, including Apple silicon
- [ ] Other (explain)

**3.7 How did you install the package?**
Installation method explains a surprising share of reports, particularly
those where a routine is missing entirely.

- [ ] `pip install discretus` from the package index
- [ ] `pip install` with a pinned version
- [ ] `pip install -e .` from a source checkout
- [ ] `pip install` from a git reference
- [ ] `conda install` from conda-forge
- [ ] From the `environment.yml` in the repository
- [ ] From a container image built from the `Dockerfile`
- [ ] From a distribution package provided by my operating system
- [ ] Other (explain)

**3.8 Which optional extras are installed?**
Pick every option that applies. Run `pip show discretus` and
`pip list` if you are not sure.

- [ ] None, the core only
- [ ] `viz`
- [ ] `docs`
- [ ] `dev`
- [ ] I am not sure

**3.9 Are the Graphviz system binaries installed and on the path?**
Only relevant to a rendering problem. Run `dot -V` to check.

- [ ] Yes
- [ ] No
- [ ] Not relevant to this report
- [ ] I am not sure

**3.10 Are you running inside a virtual environment, a container, or the system interpreter?**
A report of a missing module is usually an environment mismatch, and this
question is how that gets found.

- [ ] A virtual environment created with `venv`
- [ ] A conda environment
- [ ] A container
- [ ] The interpreter provided by the operating system
- [ ] A notebook environment whose kernel I did not create myself
- [ ] Other (explain)

**3.11 Which `DISCRETUS_` environment variables are set?**
Run `env | grep DISCRETUS` on a Unix shell. The library reads nine of them,
and one of them explains several reports on its own.

> Your answer here.

**3.12 Did you change any setting through `discretus.config`?**
Paste the calls if you did. `strict_validation`, `max_enumeration`, and
`default_seed` are the ones that change behaviour most visibly.

> Your answer here.

## Section 4. Reproduction

REQUIRED. Ten questions. A minimal reproduction is the single most valuable
part of a report, and it is usually also the part that identifies the cause
before a maintainer ever reads it.

**4.1 Paste the smallest program that shows the problem.**
Aim for under twenty lines, with no third party imports and no reliance on
a local file. Include the imports so that it can be run as written.

```python
# Your reproduction here.
```

**4.2 Paste the exact output you observed.**
Include the full traceback when there is one, not only its last line. The
frames above the last one are usually where the cause is.

```text
# Your output here.
```

**4.3 Is the reproduction minimal?**
A report with a large reproduction is still welcome. Saying so honestly
saves the maintainer from assuming that every line matters.

- [ ] Yes, I removed everything that was not needed
- [ ] Mostly, a few lines may be unnecessary
- [ ] No, it is extracted from a larger program
- [ ] No, I could not reduce it further and it needs my own data
- [ ] Other (explain)

**4.4 Does the problem reproduce every time?**
Intermittence points at randomness, at iteration order, or at a cache, and
each of those has a different investigation.

- [ ] Every time
- [ ] Most of the time
- [ ] Occasionally
- [ ] Only once so far
- [ ] Only in a specific environment
- [ ] Other (explain)

**4.5 Does it reproduce in a fresh interpreter session?**
A problem that needs prior state in the session is a different defect from
one that does not.

- [ ] Yes
- [ ] No, it needs earlier calls in the same session
- [ ] I have not tried
- [ ] Other (explain)

**4.6 Does it reproduce with the default configuration?**
Try again after `discretus.config.reset_config()` with no environment
variables set.

- [ ] Yes, with defaults
- [ ] No, it needs a changed setting
- [ ] I have not tried
- [ ] Other (explain)

**4.7 What is the smallest input that triggers it?**
Shrinking the input is the fastest route to the cause. A graph with four
vertices is far more informative than one with four thousand.

> Your answer here.

**4.8 Does it depend on the size of the input?**
A defect that appears above a threshold usually points at a dispatch
boundary, a cache, or an overflow in a converted value.

- [ ] It happens at every size
- [ ] Only above some size (state it below)
- [ ] Only below some size (state it below)
- [ ] Only at one specific size (state it below)
- [ ] It does not depend on size
- [ ] I have not tried other sizes

**4.9 Does it depend on the values in the input rather than the size?**
For instance only on a negative weight, only on a composite modulus, only on
an empty structure, or only on a value of a particular type.

> Your answer here.

**4.10 How long does the reproduction take to run?**
This tells the maintainer whether they can iterate on it quickly.

- [ ] Under a second
- [ ] Under a minute
- [ ] Minutes
- [ ] Hours
- [ ] It does not terminate

## Section 5. Expected and actual behaviour

REQUIRED. Eight questions. The difference between what you expected and what
happened is the definition of the defect, and stating both explicitly
prevents a long exchange about which is which.

**5.1 What result did you expect?**
State the value, not only that it should be different.

> Your answer here.

**5.2 What result did you get?**
Paste it exactly, including the type when that matters.

> Your answer here.

**5.3 How do you know the expected result is correct?**
Pick every option that applies. This is the question that most often
resolves a report immediately, in either direction.

- [ ] A definition or a theorem
- [ ] A textbook or a paper (cite it below)
- [ ] A hand computation
- [ ] An independent implementation in another library
- [ ] A published table of values
- [ ] The documentation of this library
- [ ] An earlier version of this library
- [ ] Another routine in this library that disagrees
- [ ] Other (explain)

**5.4 Cite the source, if there is one.**
A reference lets the maintainer check the claim without reconstructing it.

> Your answer here.

**5.5 Do two routines in this library disagree with each other?**
An internal disagreement is a strong report, because one of the two is
certainly wrong.

- [ ] Yes (name both below)
- [ ] No
- [ ] I have not compared
- [ ] Other (explain)

**5.6 Which two routines, and what do they each return?**
Name them and paste both results.

> Your answer here.

**5.7 Does the documentation say what you expected?**
If the documentation and the behaviour disagree, one of them is a defect,
and it is worth saying which you believe should change.

- [ ] Yes, the behaviour contradicts the documentation
- [ ] No, the documentation agrees with the behaviour and I believe both are wrong
- [ ] The documentation does not address this case
- [ ] I did not find the relevant documentation
- [ ] Other (explain)

**5.8 Where is the relevant documentation?**
A link or a path, for instance `docs/api/graphs.md` or the docstring of the
routine.

> Your answer here.

## Section 6. Mathematical correctness

Optional, ten questions. Complete this section when the report is about a
wrong value rather than about a crash or an interface problem.

**6.1 Which definition or theorem does the behaviour contradict?**
State it, in words or in notation. The maintainer will check the
implementation against it.

> Your answer here.

**6.2 Is the disagreement in the value, in the type, or in the shape?**
A returned list where a set was documented is a different defect from a
wrong number.

- [ ] The value is wrong
- [ ] The type is wrong
- [ ] The shape or the length is wrong
- [ ] The order is wrong
- [ ] The sign is wrong
- [ ] The result is off by one
- [ ] Other (explain)

**6.3 Is the result exact or approximate?**
The library computes exactly wherever the mathematics is exact, so an
approximate result where an exact one was documented is itself a defect.

- [ ] It should be exact and it is approximate
- [ ] It is exact and the exact value is wrong
- [ ] It is documented as approximate and the error exceeds the stated tolerance
- [ ] Not relevant
- [ ] Other (explain)

**6.4 Does a floating point value enter the computation anywhere?**
A float passed in at the boundary is the most common cause of an
unexpectedly inexact result, and it is not a defect in the library.

- [ ] No, every input is an integer or a `Fraction`
- [ ] Yes, I passed a float
- [ ] Yes, a float appears inside the library as far as I can tell
- [ ] I am not sure

**6.5 Does the problem involve an empty structure?**
The empty set, the empty relation, the zero polynomial, and the graph with
no vertices are the cases most often mishandled, and the library documents
what each should produce.

- [ ] Yes
- [ ] No
- [ ] Other (explain)

**6.6 Does it involve a degenerate or boundary case?**
Pick every option that applies.

- [ ] A singleton structure
- [ ] A modulus of one
- [ ] A zero exponent
- [ ] A negative argument
- [ ] A disconnected graph
- [ ] A self loop or a parallel edge
- [ ] A zero weight or a negative weight
- [ ] A repeated element or a repeated root
- [ ] The identity element
- [ ] None of these
- [ ] Other (explain)

**6.7 Does the result depend on the element type you used?**
Members of a structure may be any hashable value, and a defect that appears
only for one type is usually in a comparison or a normalization.

- [ ] It happens for every element type I tried
- [ ] Only for integers
- [ ] Only for strings
- [ ] Only for tuples
- [ ] Only for frozen sets or nested structures
- [ ] Only for mixed types in one structure
- [ ] I only tried one type

**6.8 Can you compute the correct answer by hand for a small case?**
A hand computation of a small case is the strongest possible evidence, and
it also gives the maintainer a regression test.

> Your answer here.

**6.9 Does an earlier or later version of the library agree with you?**
If you can, install another version and run the same reproduction.

- [ ] Yes, an earlier version returned the expected result
- [ ] Yes, a later version returns the expected result
- [ ] No, every version I tried behaves the same way
- [ ] I only tried one version

**6.10 Does an independent tool agree with you?**
Naming the tool and its version is useful. A disagreement between two
libraries is not proof that either is wrong, and it is a good starting
point.

> Your answer here.

## Section 7. Determinism and reproducibility

Optional, seven questions. Complete this section when the behaviour changes
between runs, between processes, or between machines. The library guarantees
determinism, so a report here is always taken seriously.

**7.1 Does the result change between runs of the same program?**

- [ ] Yes, in the same process
- [ ] Yes, between processes
- [ ] Yes, between machines
- [ ] No, it is stable and wrong
- [ ] Other (explain)

**7.2 Is a randomized routine involved?**
A routine that takes a `seed` argument is randomized. Without a seed it is
not reproducible by design, which is not a defect.

- [ ] Yes, and I passed a seed
- [ ] Yes, and I did not pass a seed
- [ ] No randomized routine is involved
- [ ] I am not sure

**7.3 Did you set `default_seed` in the configuration?**
A process wide seed makes an unseeded call reproducible, which is the
recommended way to make a whole run deterministic.

- [ ] Yes
- [ ] No
- [ ] Other (explain)

**7.4 Does the order of a returned collection vary?**
Everything the library returns in an order is sorted through a total order
on the members, so a varying order is a defect rather than an expectation.

- [ ] Yes, the order varies
- [ ] No, the order is stable
- [ ] I did not check

**7.5 Does setting `PYTHONHASHSEED` change the behaviour?**
Run the reproduction twice with different values. A difference points at an
iteration order that escaped the sorting.

- [ ] Yes, the result changes with the hash seed
- [ ] No, the result is the same
- [ ] I have not tried

**7.6 Does the behaviour differ between two machines with the same versions?**
If so, describe both machines. This is rare and the report is valuable.

> Your answer here.

**7.7 Does a written file differ between runs for an equal object?**
Every writer in `discretus.io` is documented as byte stable, so a differing
file is a defect.

- [ ] Yes, the bytes differ
- [ ] No, the bytes are identical
- [ ] Not relevant
- [ ] I have not checked

## Section 8. Performance

Optional, eight questions. Complete this section for a slowdown, a hang, or
unexpected memory use. Note first that several routines in this library are
exponential by nature, and the reference states the complexity of each.

**8.1 What is the symptom?**

- [ ] It is slower than an earlier version
- [ ] It is slower than the documented complexity suggests
- [ ] It does not terminate
- [ ] It allocates until the process is killed
- [ ] It is slower than another library doing the same thing
- [ ] Other (explain)

**8.2 Which routine, and what input size?**
State the sizes in the terms the complexity is expressed in, for instance
the vertex and edge counts of a graph rather than the size of the file it
came from.

> Your answer here.

**8.3 What does the reference state as the complexity of that routine?**
Quoting it makes clear whether the behaviour is a defect or the documented
cost.

> Your answer here.

**8.4 Have you compared against an earlier version?**
A measured regression between two versions is far stronger than an
impression.

- [ ] Yes, and it is measurably slower (give both numbers below)
- [ ] Yes, and the two are comparable
- [ ] No
- [ ] Other (explain)

**8.5 Paste your measurement.**
Include how you measured it. `discretus.utils.timing.measure` reports every
repetition, and the minimum is the informative number.

```text
# Your measurement here.
```

**8.6 Is the routine one the reference documents as exponential?**
Exact graph colouring, Hamiltonicity, exhaustive enumeration, and
satisfiability are exponential because the problems are hard.

- [ ] Yes, and I believe the constant factor is still wrong
- [ ] No, the reference documents it as polynomial
- [ ] I do not know
- [ ] Other (explain)

**8.7 Did you choose the representation the algorithm wants?**
A dense adjacency matrix and a sparse adjacency list differ by orders of
magnitude on the right input, and the reference says which each algorithm
prefers.

- [ ] Yes
- [ ] No
- [ ] I did not know this mattered

**8.8 Is a cache involved?**
Several routines memoize. A first call and a second call can differ by
orders of magnitude, and comparing the wrong pair is a common measurement
mistake.

- [ ] I cleared the caches between measurements
- [ ] I did not clear the caches
- [ ] Not relevant

## Section 9. Input and data

Optional, seven questions. Complete this section when the problem involves
data read from a file or supplied by a user.

**9.1 Where did the input come from?**

- [ ] I constructed it in the program
- [ ] I read it with `discretus.io`
- [ ] I read it with my own code
- [ ] It was produced by another tool
- [ ] It was supplied by a user of my application
- [ ] Other (explain)

**9.2 Which interchange format?**

- [ ] GraphML
- [ ] GML
- [ ] DOT
- [ ] DIMACS
- [ ] JSON
- [ ] CSV
- [ ] An edge list
- [ ] Adjacency data
- [ ] Pickle
- [ ] Not relevant
- [ ] Other (explain)

**9.3 Can you attach the input, or a reduced version of it?**
A small input file, or a deterministic generator for it, makes the report
self contained. Please do not attach anything confidential.

> Your answer here.

**9.4 Does the input round trip?**
Reading what a writer produced should reconstruct an equal object, and
writing it again should produce identical bytes.

- [ ] Yes, it round trips
- [ ] No, reading what was written gives a different object
- [ ] No, writing twice gives different bytes
- [ ] I have not checked
- [ ] Not relevant

**9.5 Was the input produced by this library or by something else?**
A file from another tool may use a part of a format that this library does
not accept, which is a different defect from a failure on its own output.

- [ ] By this library
- [ ] By another tool (name it below)
- [ ] By hand
- [ ] I do not know

**9.6 Is the input well formed according to the format specification?**
If it is not, the library should report a parse error rather than
misreading, and a misreading is the defect.

- [ ] Yes
- [ ] No
- [ ] I am not sure

**9.7 Is any of the input untrusted, that is supplied by someone else?**
If so, read the resource exhaustion section of SECURITY.md before
continuing, and consider whether the report should be private.

- [ ] Yes
- [ ] No

## Section 10. Regression history

Optional, six questions. Knowing when the behaviour changed narrows the
cause to a small range of commits.

**10.1 Did this work in an earlier version?**

- [ ] Yes (state the last working version below)
- [ ] No, it has never worked for me
- [ ] I do not know
- [ ] Other (explain)

**10.2 Which is the last version that behaved correctly?**
Even an approximate answer is useful.

> Your answer here.

**10.3 Which is the first version that behaves incorrectly?**

> Your answer here.

**10.4 Have you bisected the history?**
If you have, the commit is the single most useful piece of information in
the whole report.

- [ ] Yes (give the commit below)
- [ ] No
- [ ] I tried and could not complete it

**10.5 Which commit introduces the behaviour?**

> Your answer here.

**10.6 Did anything else change in your environment at the same time?**
An interpreter upgrade, a dependency change, or a platform change often
coincides with a library upgrade and is sometimes the real cause.

> Your answer here.

## Section 11. Workarounds and diagnostics

Optional, eleven questions. These help other users who find this issue
before it is fixed, and they narrow the cause.

**11.1 Have you found a workaround?**

- [ ] Yes (describe it below)
- [ ] No
- [ ] Yes, but it is unacceptable for my use

**11.2 Describe the workaround.**
Other readers of this issue will thank you.

> Your answer here.

**11.3 Does calling a different routine avoid the problem?**
For instance using `dsatur` instead of `chromatic_number`, or
`bellman_ford` instead of `dijkstra`.

> Your answer here.

**11.4 Does disabling strict validation change anything?**
Try `discretus.config.set_config(strict_validation=False)` and then again
with it enabled.

- [ ] The behaviour changes
- [ ] The behaviour is the same
- [ ] I have not tried

**11.5 Does raising or lowering `max_enumeration` change anything?**
Relevant when the symptom is a `LimitExceededError` or an allocation.

- [ ] The behaviour changes
- [ ] The behaviour is the same
- [ ] I have not tried

**11.6 Have you enabled the library logger?**
`discretus.logging_utils.configure_logging(level="DEBUG")` makes the
routines that record steps report them.

- [ ] Yes (attach the output below)
- [ ] No
- [ ] The routine does not log anything

**11.7 Paste any logging or step recording output.**
Routines that support it can report their derivation through
`discretus.core.explain`.

```text
# Your output here.
```

**11.8 Have you inspected the intermediate values?**
Saying what you already ruled out prevents the maintainer from repeating it.

> Your answer here.

**11.9 Do you have a suspicion about the cause?**
A guess costs nothing and is often right. It will not be held against the
report if it is wrong.

> Your answer here.

**11.10 Can you point at the line you believe is responsible?**
A file and a line number, or a permalink to the line on the default branch.

> Your answer here.

**11.11 Did any static check flag it?**
Running `mypy`, `ruff`, or `pylint` over your own program sometimes reveals
that the call rather than the library is at fault.

- [ ] Yes (paste the finding below)
- [ ] No
- [ ] I have not run them

## Section 12. Contribution

Optional, five questions. There is no expectation that a reporter fixes the
defect, and an offer is welcome.

**12.1 Would you like to work on a fix?**

- [ ] Yes, I would like to open a pull request
- [ ] Yes, with guidance on where to start
- [ ] No, I am only reporting it
- [ ] I cannot, for policy or time reasons
- [ ] Other (explain)

**12.2 Would you like to contribute a regression test even if not a fix?**
A failing test is a complete contribution on its own, and it is the part
that keeps the defect from returning.

- [ ] Yes
- [ ] No
- [ ] Other (explain)

**12.3 Have you read CONTRIBUTING.md?**
Not a requirement for reporting. It matters only if you intend to open a
pull request.

- [ ] Yes
- [ ] No
- [ ] Not applicable

**12.4 Do you need this fixed by a particular date?**
The project is unfunded academic work and makes no schedule commitment.
Knowing a deadline still helps with ordering, and saying so is not a
demand.

> Your answer here.

**12.5 Would a documented workaround be sufficient for now?**
Sometimes the fastest resolution is a documentation change while the fix is
prepared properly.

- [ ] Yes
- [ ] No, I need the behaviour fixed
- [ ] Other (explain)

## Section 13. Final checklist

REQUIRED. Eight boxes. These are the things that make a report actionable,
and ticking them honestly is more useful than ticking them all.

- [ ] I have given the version of discretus and the Python version
- [ ] I have included a reproduction that runs as written
- [ ] I have included the full output or traceback
- [ ] I have stated the expected result and how I know it is correct
- [ ] I have confirmed the problem with the default configuration, or said
      which setting it needs
- [ ] I have searched the existing issues
- [ ] I have used plain punctuation, with no long dash characters and no
      emoji
- [ ] I have not included any confidential data, credential, or personal
      information

## Section 14. Anything else

**14.1 Is there anything else a maintainer should know?**
Context about what you were trying to achieve often suggests a better
answer than the one the question asked for.

> Your answer here.
