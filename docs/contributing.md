# Contributing

The contributing guide lives at the repository root, in `CONTRIBUTING.md`,
and is included below in full. It is kept in one place rather than in two
because a duplicated process document drifts, and a contributor who follows
the stale copy is then told in review that they followed the wrong one.

What the guide covers, so that you can jump to the part you need:

- Setting up a development environment, with pip, with conda, in a
  container, or in a browser based workspace.
- The everyday commands, and how to run one package's tests rather than the
  whole suite.
- The repository layout and the acyclic dependency rule between packages,
  which is the single most important architectural constraint to understand
  before adding code.
- The ten point quality gate a change has to pass.
- The code style decisions that tools cannot enforce, including immutability,
  exact arithmetic, deterministic ordering, and the prose conventions.
- The docstring format, with the rule for each section and the requirement
  that every nontrivial routine states its complexity.
- The mathematical conventions the library is consistent about, from whether
  zero is a natural number to the degree of the zero polynomial.
- Error handling, with a table mapping every situation to the exception it
  should raise.
- The four kinds of test the suite uses, with an example of each, and why a
  new algorithm needs cross validation rather than only unit tests.
- Performance work, and what disqualifies a speedup.
- A ten step procedure for adding a new algorithm.
- How to add an optional dependency behind an extra.
- Commit message conventions, pull request expectations, and what a
  contributor and a reviewer may expect of each other.
- The deprecation procedure and the release sequence.

For the code of conduct, see `CODE_OF_CONDUCT.md`, and for reporting a
vulnerability, see `SECURITY.md`. Neither is reproduced here.

```{include} ../CONTRIBUTING.md
:start-after: "# Contributing to discretus"
```
