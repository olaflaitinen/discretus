<!--
Thank you for contributing. This template is long because a pull request
that answers these questions is reviewed in one pass, and one that does not
takes several rounds of questions that are the same every time.

How to use it:

- The sections marked REQUIRED are the ones a review cannot start without.
- Everything else is optional. Delete a question rather than leaving it
  blank when it does not apply, and delete a whole section when none of it
  applies. A one line typographic fix should keep sections 1, 2, 3, and 15
  and delete the rest.
- For a closed question, tick one or more of the listed options. Every
  option the project recognizes is listed, so if none fits, use the Other
  entry and say what it should have been.
- For an open question, replace the placeholder text.
- Please use plain punctuation. The repository does not use the long dash
  character or emoji anywhere, including in pull requests and commit
  messages.
- The title of this pull request must follow the Conventional Commits
  format, because it becomes the squashed commit subject.

CONTRIBUTING.md contains the quality gate, the code style, the docstring
format, the mathematical conventions, and the testing expectations that the
questions below refer to.
-->

## Section 1. Summary

REQUIRED. Five questions.

**1.1 What does this pull request change?**
Two or three sentences. Describe the change rather than the diff, which the
reviewer can read.

> Your answer here.

**1.2 Why is the change needed?**
A reviewer approves a change against a purpose. State the purpose even when
it seems obvious from the issue.

> Your answer here.

**1.3 What is the shortest description of the user visible effect?**
This is the sentence that belongs in the changelog. If the change has no
user visible effect, say so.

> Your answer here.

**1.4 Is this ready for review, or is it a draft for discussion?**
A draft is welcome. Saying so prevents a reviewer from spending time on a
moving target.

- [ ] Ready for review
- [ ] Draft, opened for early feedback on the approach
- [ ] Draft, blocked on something (say what below)
- [ ] Other (explain)

**1.5 What is blocking it, if it is blocked?**

> Your answer here.

## Section 2. Type of change

REQUIRED. Six questions.

**2.1 What kind of change is this?**
Pick every option that applies. The type matches the prefix of the commit
message convention.

- [ ] `feat`, a new public interface
- [ ] `fix`, a correction to behaviour that was wrong
- [ ] `perf`, a speed or memory improvement with no behaviour change
- [ ] `refactor`, an internal change with no behaviour change
- [ ] `docs`, documentation, docstrings, tutorials, or examples
- [ ] `test`, tests only
- [ ] `build`, packaging, dependencies, or the build backend
- [ ] `ci`, continuous integration or repository automation
- [ ] `chore`, maintenance that fits none of the above
- [ ] `revert`, an undo of an earlier commit
- [ ] Other (explain)

**2.2 Which packages does it touch?**
Pick every option that applies.

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
- [ ] Tests only
- [ ] Documentation only
- [ ] Packaging or continuous integration only

**2.3 How large is the change?**
A reviewer reads a small pull request quickly and a large one slowly, and
knowing which it is sets the expectation.

- [ ] Under fifty changed lines
- [ ] Under two hundred
- [ ] Under a thousand
- [ ] Over a thousand
- [ ] Mostly generated or mechanical

**2.4 Is the change self contained, or part of a series?**
A series is fine when each part is independently reviewable.

- [ ] Self contained
- [ ] The first of a planned series
- [ ] A later part of a series (link the earlier parts below)
- [ ] Other (explain)

**2.5 Does it depend on another pull request?**

- [ ] No
- [ ] Yes (link it below)

**2.6 Does it need to be merged in a particular order relative to anything else?**

> Your answer here.

## Section 3. Linked issues

REQUIRED. Four questions.

**3.1 Which issue does this close?**
Use the closing keyword so that the issue is closed on merge.

> Closes #

**3.2 Which issues does it partially address?**
Use a reference rather than a closing keyword when the work is not
finished.

> Refs #

**3.3 Was the design discussed before implementation?**
For anything substantial, the project asks for an issue first, so that the
interface is agreed before the code exists.

- [ ] Yes, in the linked issue
- [ ] Yes, in a discussion (link it below)
- [ ] No, the change is small enough not to need it
- [ ] No, and I should have opened one first
- [ ] Other (explain)

**3.4 Does this pull request change anything that was agreed in that discussion?**
Divergence is allowed and should be visible.

> Your answer here.

## Section 4. Mathematical notes

REQUIRED for any change that touches mathematics. Eleven questions. Delete
the section for a packaging or typographic change.

**4.1 Which definition, theorem, or algorithm does this implement?**
State it precisely. This is the sentence the docstring should also contain.

> Your answer here.

**4.2 Which reference did you follow?**
A citation lets the reviewer check the implementation against the source
rather than reconstructing it.

> Your answer here.

**4.3 What is the time complexity of the new or changed routine?**
State it in the quantities that matter, for instance the vertex and edge
counts rather than a bare letter.

> Your answer here.

**4.4 What is the space complexity?**

> Your answer here.

**4.5 Does the complexity appear in the docstring and in the reference page?**
The project requires it for anything that is not constant time.

- [ ] Yes, in both
- [ ] In the docstring only
- [ ] In neither, and here is why
- [ ] Not applicable

**4.6 Is the result exact?**
The library computes exactly wherever the mathematics is exact.

- [ ] Yes, over the integers
- [ ] Yes, over the rationals
- [ ] Exact where possible, approximate elsewhere with the tolerance documented
- [ ] Necessarily approximate, and documented as such
- [ ] Not applicable

**4.7 Does any floating point value enter the computation?**
An unnecessary float is the usual way exactness is lost, and it is worth
naming where one is deliberate.

- [ ] No
- [ ] Yes, and it is unavoidable (explain below)
- [ ] Yes, and it is at the caller's boundary only
- [ ] Not applicable

**4.8 Is the result unique, or is any valid answer acceptable?**
This decides what the tests may assert. A minimum spanning tree is not
unique while its total weight is.

- [ ] Unique
- [ ] Not unique, any valid answer is acceptable
- [ ] Not unique, and a canonical answer is chosen (say which below)
- [ ] Not applicable

**4.9 Which degenerate cases did you consider?**
Pick every option that applies, and make sure each ticked one has a test.

- [ ] The empty structure
- [ ] A singleton
- [ ] A modulus of one
- [ ] A zero exponent
- [ ] A negative argument
- [ ] A disconnected graph
- [ ] A self loop or a parallel edge
- [ ] A zero or negative weight
- [ ] A repeated element or root
- [ ] The identity element
- [ ] None apply
- [ ] Other (explain)

**4.10 Does the change respect the project's mathematical conventions?**
These are listed in CONTRIBUTING.md and include that the natural numbers
include zero, that the empty product is one, and that the zero polynomial
has degree minus one.

- [ ] Yes
- [ ] It introduces a new convention (explain below)
- [ ] It deviates from one (explain below)
- [ ] Not applicable

**4.11 Is there a known result that the new behaviour can be checked against?**
An identity linking the new routine to an existing one is the strongest
available test.

> Your answer here.

## Section 5. Interface changes

REQUIRED when the public interface changes. Ten questions.

**5.1 List every public name added.**
Include the full import path of each.

> Your answer here.

**5.2 List every public name changed.**

> Your answer here.

**5.3 List every public name removed or deprecated.**

> Your answer here.

**5.4 Is the change backward compatible?**
Within a major version the public interface stays compatible.

- [ ] Yes, it adds interface only
- [ ] Yes, it changes only undocumented internals
- [ ] No, it changes a documented result
- [ ] No, it changes a signature
- [ ] No, it removes interface
- [ ] Other (explain)

**5.5 If it is not compatible, what is the migration path?**
Every breaking change carries a migration note in the changelog.

> Your answer here.

**5.6 Does a deprecation accompany any removal?**
The policy is to keep the old name working with a warning that names its
replacement and the release in which it will be removed.

- [ ] Yes, with a `DeprecationWarning` naming the replacement and the release
- [ ] No deprecation is needed, the name was never public
- [ ] Not applicable

**5.7 Are the new names consistent with the surrounding module?**
Routines are named after the mathematics they encode, and argument order is
consistent within a module.

- [ ] Yes
- [ ] There is a deviation, justified below
- [ ] Not applicable

**5.8 Is `__all__` updated in every module you touched?**
The library declares its public names explicitly.

- [ ] Yes
- [ ] No names were added or removed
- [ ] Not applicable

**5.9 Does the change add an argument with a default to an existing routine?**
Adding one is compatible; changing an existing default is not.

- [ ] No
- [ ] Yes, with a default that preserves the previous behaviour
- [ ] Yes, and it changes an existing default (explain below)

**5.10 Does the change alter the order of any returned collection?**
Order is documented behaviour, because ranking and unranking depend on it.

- [ ] No
- [ ] Yes (explain below)
- [ ] Not applicable

## Section 6. Implementation

Optional, ten questions.

**6.1 Summarize the approach.**
Two or three sentences on how the change works, which lets a reviewer read
the diff with the intended structure in mind.

> Your answer here.

**6.2 Did you consider an alternative approach?**
Naming what you rejected and why is often the most useful paragraph in a
pull request.

> Your answer here.

**6.3 Does the change respect the acyclic dependency rule?**
A domain package may import from the core and the utility layers and not
from another domain package. Interoperability goes through explicit
conversions.

- [ ] Yes
- [ ] It adds a cross domain import, justified below
- [ ] Not applicable

**6.4 Does it add or change anything in the core layer?**
A change there affects every domain, so it is reviewed more strictly.

- [ ] No
- [ ] Yes (explain below)

**6.5 Does it mutate any argument or any existing object?**
Value types in this library are immutable, and every operation returns a new
object.

- [ ] No
- [ ] Yes, and the object is a documented builder
- [ ] Yes (explain below)

**6.6 Does it introduce global or module level mutable state?**
The library's only process wide state is the configuration and the
inspectable caches.

- [ ] No
- [ ] Yes, a cache registered through the utility package
- [ ] Yes (explain below)

**6.7 Does it add a cache?**
Caches in this library report their statistics and can be cleared, which is
what makes them testable.

- [ ] No
- [ ] Yes, through `discretus.utils.memoize` or `discretus.core.lazy`
- [ ] Yes, implemented directly (explain below)

**6.8 Does it use randomness?**
Randomized routines take a seed, route through
`discretus.core.random_base`, and never touch the global random state.

- [ ] No
- [ ] Yes, with an explicit seed argument
- [ ] Yes (explain below)

**6.9 Does it sort anything that a caller will see?**
Output order goes through the universal total order so that results do not
depend on hash values and are identical between processes.

- [ ] No
- [ ] Yes, through `discretus.core.comparators`
- [ ] Yes, with its own ordering (justify below)

**6.10 Are there parts of the diff you are unsure about?**
Pointing at them directs the review to where it is most useful.

> Your answer here.

## Section 7. Performance

Optional, nine questions. Complete this section for a `perf` change or for
anything that could plausibly slow something down.

**7.1 What did you measure?**
State the routine, the input sizes, and the machine.

> Your answer here.

**7.2 Paste the measurement before and after.**
The minimum of several repetitions is the informative number for a
deterministic computation.

```text
# Your measurement here.
```

**7.3 How did you measure it?**

- [ ] `discretus.utils.timing.measure`
- [ ] The benchmark suite under `benchmarks/`
- [ ] `timeit`
- [ ] A manual timer
- [ ] Other (explain)

**7.4 Did you clear the caches between the two measurements?**
A warm cache makes whichever ran second look faster, which is the most
common way a benchmark misleads.

- [ ] Yes
- [ ] No
- [ ] Not relevant

**7.5 Did you confirm that the results did not change?**
A speedup that alters output order, loses exactness, or makes a routine
nondeterministic is not a speedup.

- [ ] Yes, the outputs are identical
- [ ] The outputs differ, and here is why that is correct
- [ ] Not relevant

**7.6 Does the change alter a documented complexity?**

- [ ] No
- [ ] Yes, it improves one (update the reference)
- [ ] Yes, it worsens one (justify below)

**7.7 Does it change memory use materially?**

> Your answer here.

**7.8 Does it add a benchmark?**
A performance change that is not measured in the suite will regress
unnoticed.

- [ ] Yes
- [ ] No, one already covers it
- [ ] No (explain below)

**7.9 Could the change slow anything else down?**
A shared helper on a hot path affects callers that the diff does not
mention.

> Your answer here.

## Section 8. Testing

REQUIRED. Twelve questions. This is the section reviewers ask about most
often, so answering it fully saves a round trip.

**8.1 Which tests did you add?**
List the files and the test names.

> Your answer here.

**8.2 Which kinds of test does the change have?**
Pick every option that applies. A new algorithm normally has at least two
kinds.

- [ ] Example based unit tests with values a reader can verify
- [ ] Property based tests asserting a law or an identity
- [ ] Cross validation against a naive or independent implementation
- [ ] A regression test for the reported defect
- [ ] Doctests in the docstring
- [ ] Tests of the degenerate cases
- [ ] Tests of the raised exceptions
- [ ] Benchmarks
- [ ] None yet (explain below)

**8.3 For a fix, is the regression test in the same commit as the fix?**
The project asks for this so that the defect cannot silently return.

- [ ] Yes
- [ ] No (explain below)
- [ ] Not a fix

**8.4 Does the new test fail before the change and pass after it?**
Confirming this is what distinguishes a regression test from a test that
happens to pass.

- [ ] Yes, I checked both directions
- [ ] I did not check the failing direction
- [ ] Not applicable

**8.5 Which properties or identities do the property based tests assert?**
Naming them lets the reviewer judge whether they pin the behaviour.

> Your answer here.

**8.6 What did you cross validate against?**

- [ ] A naive implementation written for the test
- [ ] Another routine in this library that must agree
- [ ] Exhaustive enumeration for small cases
- [ ] A published table of values
- [ ] An independent library
- [ ] Nothing (explain below)

**8.7 Are the tests deterministic?**
Every test in the suite must be, either through a routine's seed argument or
through a fixture.

- [ ] Yes
- [ ] No (explain below)

**8.8 Do the tests mirror the package layout?**
A module at `discretus/graphs/spanning/kruskal.py` is tested by
`tests/graphs/test_spanning.py`.

- [ ] Yes
- [ ] No (explain below)

**8.9 Did you mark slow or optional tests?**
The `slow` marker keeps the default run comfortable and the `optional`
marker covers tests that need an extra.

- [ ] Yes
- [ ] No markers are needed
- [ ] Not applicable

**8.10 Does coverage stay level or improve?**
The project sits above ninety percent overall and holds new lines to ninety
five.

- [ ] It improves
- [ ] It stays level
- [ ] It decreases (explain below)
- [ ] I did not measure

**8.11 Paste the relevant test output.**
The summary line is enough for a routine change; a fuller paste helps for
anything unusual.

```text
# Your output here.
```

**8.12 Did you run the full suite locally, or only part of it?**
Continuous integration runs the whole matrix, and a local full run catches
the obvious failures sooner.

- [ ] The full suite on one interpreter
- [ ] The full suite on several interpreters through nox or tox
- [ ] Only the tests for the package I changed
- [ ] None locally

## Section 9. Errors and validation

Optional, six questions.

**9.1 Which exceptions can the new or changed code raise?**
List them with the condition that triggers each.

> Your answer here.

**9.2 Are they all from `discretus.exceptions`?**
The library raises its own hierarchy rather than bare built-in exceptions,
so that a caller can catch library failures as a group.

- [ ] Yes
- [ ] No (explain below)
- [ ] Not applicable

**9.3 Does the change add a new exception type?**
A new type needs a place in the documented hierarchy and an entry in the
reference.

- [ ] No
- [ ] Yes (explain below)

**9.4 Do the error messages name the offending value and the violated condition?**
The project aims to explain a failure in terms of the mathematics rather
than the implementation.

- [ ] Yes
- [ ] Not applicable

**9.5 Does the change use the validation helpers?**
Using `discretus.validation` keeps the messages uniform across the library.

- [ ] Yes
- [ ] No, the checks are specific to this routine
- [ ] Not applicable

**9.6 Does the change respect `strict_validation` for expensive checks?**
A check that costs as much as the computation it guards consults the
configuration.

- [ ] Yes
- [ ] The checks are cheap and always run
- [ ] Not applicable

## Section 10. Documentation

REQUIRED when the public interface or documented behaviour changes. Nine
questions.

**10.1 Does every new public routine have a docstring in the project format?**
The format is the Google style sections plus a `Complexity` section, and it
is shown in CONTRIBUTING.md.

- [ ] Yes
- [ ] No (explain below)
- [ ] Not applicable

**10.2 Does each docstring document its parameters, return value, and exceptions?**

- [ ] Yes
- [ ] Not applicable

**10.3 Does each docstring carry a runnable doctest?**
The documentation job executes every example, so a broken one fails the
build rather than misleading a reader.

- [ ] Yes
- [ ] No (explain below)
- [ ] Not applicable

**10.4 Which reference pages did you update?**

> Your answer here.

**10.5 Did you update a tutorial?**

- [ ] Yes (name it below)
- [ ] No, the change does not affect any tutorial
- [ ] No, and it probably should (explain below)

**10.6 Did you add or update an example script?**
The `examples/` directory holds runnable programs, and the documentation job
runs all of them.

- [ ] Yes
- [ ] No, not needed
- [ ] Not applicable

**10.7 Did you add a changelog entry under `Unreleased`?**
The project requires one for every user visible change, written from the
point of view of somebody upgrading.

- [ ] Yes
- [ ] No, the change is not user visible
- [ ] No (explain below)

**10.8 Under which changelog heading?**

- [ ] Added
- [ ] Changed
- [ ] Deprecated
- [ ] Removed
- [ ] Fixed
- [ ] Security
- [ ] Performance
- [ ] Documentation
- [ ] Not applicable

**10.9 Did you build the documentation locally?**
`make docs` catches a broken cross reference or a failing doctest before the
pipeline does.

- [ ] Yes, it builds cleanly
- [ ] Yes, with warnings (say which below)
- [ ] No

## Section 11. Quality gate

REQUIRED. Ten questions. Continuous integration checks all of these, and
running them locally is faster than waiting for it.

**11.1 Does `make test` pass?**

- [ ] Yes
- [ ] No (explain below)

**11.2 Does `make lint` pass?**
This runs black, isort, and ruff in check mode.

- [ ] Yes
- [ ] No (explain below)

**11.3 Does `pylint` pass over the library?**

- [ ] Yes
- [ ] No (explain below)
- [ ] I did not run it

**11.4 Does `make type` pass?**
mypy is configured to require annotations on every function.

- [ ] Yes
- [ ] No (explain below)

**11.5 Does `make security` pass?**
bandit is advisory for style and blocking for a genuine finding.

- [ ] Yes
- [ ] No (explain below)
- [ ] I did not run it

**11.6 Do the pre-commit hooks pass over the whole tree?**
`make precommit` runs all of them, including the prose and configuration
linters.

- [ ] Yes
- [ ] No (explain below)
- [ ] I did not run them

**11.7 Did you introduce any long dash character or emoji?**
The prose job in the pipeline rejects both anywhere in the repository.

- [ ] No
- [ ] Yes, and it is unavoidable (explain below)

**11.8 Does every new source file carry the license notice?**
The Mozilla Public License 2.0 applies per file, so every source file opens
with the three line notice.

- [ ] Yes
- [ ] No files were added
- [ ] No (explain below)

**11.9 Did you silence any lint rule?**
Silencing on one line with a reason is acceptable; changing the
configuration belongs in its own pull request.

- [ ] No
- [ ] Yes, on specific lines with a stated reason
- [ ] Yes, in the configuration (explain below)

**11.10 Is the continuous integration pipeline green?**
A red pipeline is the contributor's to resolve, and a reviewer will usually
wait for it.

- [ ] Yes
- [ ] No, and I am working on it
- [ ] No, and the failure looks unrelated (explain below)
- [ ] It has not finished yet

## Section 12. Compatibility and dependencies

Optional, seven questions.

**12.1 Does the change work on every supported interpreter?**
The supported range is 3.9 through 3.13.

- [ ] Yes, and the matrix confirms it
- [ ] I only tested one version
- [ ] No (explain below)

**12.2 Does it use any syntax or standard library feature newer than 3.9?**
A feature from a later version has to be guarded or avoided.

- [ ] No
- [ ] Yes, and it is guarded (explain below)

**12.3 Does it work on Linux, macOS, and Windows?**
Path handling, line endings, and console encoding are the usual sources of a
platform specific failure.

- [ ] Yes, and the matrix confirms it
- [ ] I only tested one platform
- [ ] No (explain below)

**12.4 Does it add a third party dependency?**
The computational core will not gain a mandatory dependency within a major
version.

- [ ] No
- [ ] Yes, behind an existing extra
- [ ] Yes, behind a new extra
- [ ] Yes, as a mandatory dependency (this needs discussion)

**12.5 If it adds an optional dependency, is the import inside the function that needs it?**
The pattern is a local import raising `OptionalDependencyError` with the
extra to install.

- [ ] Yes
- [ ] Not applicable

**12.6 Did you update every dependency file?**
A new extra belongs in `pyproject.toml`, the matching requirements file, and
`environment.yml`.

- [ ] Yes
- [ ] Not applicable

**12.7 Does the package still import with no extras installed?**
The pipeline has a job for exactly this, because the promise that the core
needs nothing has to be kept true rather than merely stated.

- [ ] Yes
- [ ] Not applicable

## Section 13. Security

Optional, five questions. Complete this section for anything that reads
input it did not produce.

**13.1 Does the change parse or deserialize anything?**

- [ ] No
- [ ] Yes (say which format below)

**13.2 Does it validate structure before building an object?**
A reader should raise a parse error rather than misreading a malformed
document.

- [ ] Yes
- [ ] Not applicable

**13.3 Can a small input cause unbounded time or memory?**
The enumeration limit is the mechanism that bounds this, and a path that
bypasses it is a defect.

- [ ] No
- [ ] Yes, and the enumeration limit bounds it
- [ ] Yes (explain below)

**13.4 Does it use `eval`, `exec`, `pickle`, or a subprocess?**
None of these appear in the ordinary paths of the library, and the pickle
helper is documented as unsafe for untrusted input.

- [ ] No
- [ ] Yes (explain below)

**13.5 Does it touch the cryptographic primitives?**
Those are teaching implementations, and a change must not present them as
production ready.

- [ ] No
- [ ] Yes, and the documented limitations are preserved
- [ ] Yes (explain below)

## Section 14. Review guidance

Optional, six questions. These make the review faster and more useful.

**14.1 Where should a reviewer start?**
Naming the one file that carries the idea saves a reviewer from reading the
diff in alphabetical order.

> Your answer here.

**14.2 Which parts are mechanical and can be skimmed?**
For instance a rename applied across many files, or a generated table.

> Your answer here.

**14.3 Which decisions would you most like feedback on?**

> Your answer here.

**14.4 Is there anything you deliberately left out of scope?**
A stated omission is a decision; an unstated one looks like an oversight.

> Your answer here.

**14.5 Is there follow up work you intend to do separately?**
Linking a follow up issue keeps this pull request small without losing the
plan.

> Your answer here.

**14.6 How would you like the history handled on merge?**
The default is squash and merge with the pull request title as the subject.

- [ ] Squash, the default
- [ ] Keep the commits, they are individually meaningful
- [ ] I have rebased and tidied the history already
- [ ] Other (explain)

## Section 15. Final checklist

REQUIRED. Ten boxes. Tick them honestly rather than completely; an untick
with an explanation is more useful than a tick that is not true.

- [ ] The title follows the Conventional Commits format
- [ ] The description explains what changed and why
- [ ] The linked issue is referenced with a closing keyword where appropriate
- [ ] Tests accompany the change, and a fix has a regression test
- [ ] Every new public routine is annotated and documented, including its
      complexity
- [ ] The changelog has an entry under `Unreleased`, or the change is not
      user visible
- [ ] `make lint type test` passes locally
- [ ] Every new source file carries the license notice
- [ ] No long dash characters and no emoji were introduced
- [ ] The branch is rebased onto the current default branch

## Section 16. Anything else

**16.1 Is there anything else a reviewer should know?**

> Your answer here.
