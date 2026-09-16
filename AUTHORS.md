# Authors and Acknowledgments

discretus is developed and maintained at the Department of Physics and
Mathematics, Faculty of Science, Forestry and Technology, University of
Eastern Finland.

This file records who wrote the library, how authorship and credit are
handled, and what the project owes to the work of others. It is the
human readable companion to `CITATION.cff`, `codemeta.json`, and
`.zenodo.json`, which carry the same information in machine readable form
for citation tools, software indexes, and archives.

## Table of contents

1. [Author and maintainer](#author-and-maintainer)
2. [Contributors](#contributors)
3. [How to be listed](#how-to-be-listed)
4. [Credit policy](#credit-policy)
5. [Roles](#roles)
6. [Identity and history](#identity-and-history)
7. [Intellectual contributions](#intellectual-contributions)
8. [Software the project relies on](#software-the-project-relies-on)
9. [Institutional acknowledgment](#institutional-acknowledgment)
10. [Funding](#funding)
11. [How to cite](#how-to-cite)

## Author and maintainer

**Olaf Yunus Laitinen Imanov**, Student Researcher

Department of Physics and Mathematics, Faculty of Science, Forestry and
Technology, University of Eastern Finland, Joensuu, Finland.

- Email: yimanov@student.uef.fi
- ORCID: [0009-0006-5184-0810](https://orcid.org/0009-0006-5184-0810)

The author designed the architecture, wrote the initial implementation of
all eleven packages, and maintains the project. Correspondence about the
library, about collaboration, and about its use in teaching goes to the
address above.

## Contributors

Everyone whose pull request is merged is listed here, in chronological order
of their first merged contribution, with a short description of what they
contributed. The list is maintained by hand rather than generated, because a
one line description of a contribution is more informative than a commit
count.

The list is currently empty. The project has not yet merged an external
contribution, and the first entry is genuinely welcome.

<!-- Add new entries at the end of the list, in the following form:

- **Name** ([@handle](https://github.com/handle)), first contribution in
  version X.Y.Z. Short description of what they contributed.

-->

## How to be listed

If your pull request is merged and your name is not here afterwards, that is
an oversight and not a judgement. Open a pull request that adds your entry,
or say so in any issue and it will be added.

You may choose how you appear: a full name, a preferred name, a handle, or a
pseudonym. You may also choose not to appear at all. Nobody is listed here
against their wishes, and an entry is removed on request without discussion.

If your name or address changes, open a pull request that updates this file
and `.mailmap`. The history itself is never rewritten for that purpose,
because a rewrite changes every later commit hash, breaks the references to
those hashes in issues and reviews, and invalidates signatures, all in
exchange for a cosmetic change that `.mailmap` achieves for free.

## Credit policy

The project credits work rather than volume, and the following kinds of
contribution are all listed here on the same footing.

- Code, whether an algorithm, a structure, a fix, or a performance
  improvement.
- Tests, including a property based test that pins a law the documentation
  claims, and a regression test that accompanies a fix.
- Documentation, including a tutorial, a corrected complexity statement, and
  a clearer error message.
- Defect reports that identify a real problem, particularly one with a
  minimal reproduction. A precise report is often more work than the fix it
  leads to.
- Mathematical review, for instance pointing out that a stated theorem has a
  misplaced quantifier, that an algorithm's complexity claim is wrong, or
  that an edge case contradicts a definition.
- Review of a pull request that materially improved the change.
- Packaging, continuous integration, and tooling work.
- Translation and accessibility work on the documentation.

A security report is credited in the advisory and in the changelog under the
process described in `SECURITY.md`, and the reporter chooses whether to be
named.

## Roles

The project is small, and these roles describe responsibilities rather than
formal positions.

| Role | Responsibility | Current holder |
| --- | --- | --- |
| Author | Original design and implementation | Olaf Yunus Laitinen Imanov |
| Maintainer | Review, merge, release, and roadmap | Olaf Yunus Laitinen Imanov |
| Corresponding author | Academic correspondence and citation | Olaf Yunus Laitinen Imanov |
| Security contact | Private vulnerability reports | Olaf Yunus Laitinen Imanov |
| Domain reviewer | Review within one mathematical domain | Open |
| Documentation reviewer | Review of prose and tutorials | Open |

The open roles are open in a literal sense. A contributor who reviews well
within one domain over several pull requests will be invited to hold the
corresponding role, which means being asked for review on changes in that
area rather than gaining any obligation.

## Identity and history

Authorship in the repository is recorded in three places, each with a
different job.

- The commit objects record who wrote each change. They are never rewritten
  to correct a name or an address.
- `.mailmap` folds the several addresses one person may have committed with
  into a single identity, so that `git shortlog` and the release statistics
  report one contributor rather than several. The author's forge account
  address is canonical there, because that is the address a forge links
  commits to, while the institutional address in this file is the
  correspondence address.
- This file records the human description of who contributed what.

To see the contribution statistics with the mapping applied:

```bash
git shortlog --summary --numbered --email
git log --format='%aN <%aE>' | sort --unique
```

## Intellectual contributions

The library implements classical results rather than new ones, and it owes
its content to the mathematicians whose names its modules carry. Naming them
is not decoration: a reader who knows that `warshall.py` implements
Warshall's algorithm, or that `tonelli_shanks.py` implements the Tonelli
Shanks algorithm, can go to the original source and check what the code
claims.

Among the results the library implements and attributes in its docstrings
are the Euclidean algorithm and its extended form, Eratosthenes' sieve, the
Chinese remainder theorem, Fermat's little theorem, Euler's theorem and
totient, the Mobius function and Mobius inversion, the Miller Rabin and
Solovay Strassen primality tests, Pollard's rho and p minus one
factorizations, the Tonelli Shanks square root algorithm, Lagrange's
theorem, Cayley's theorem and tables, Sylow's theorems, the orbit stabilizer
theorem, Burnside's lemma and Polya's enumeration theorem, De Morgan's laws,
the Quine McCluskey minimization procedure, the Tseitin transformation, the
Davis Putnam Logemann Loveland procedure and conflict driven clause
learning, Dilworth's theorem, Sperner's theorem, Ramsey's theorem, Hall's
marriage theorem, Dijkstra's, Bellman and Ford's, Floyd and Warshall's, and
Johnson's shortest path algorithms, Kruskal's, Prim's, and Boruvka's
spanning tree algorithms, Tarjan's and Kosaraju's strong connectivity
algorithms, Hierholzer's Eulerian circuit construction, the Ford Fulkerson,
Edmonds Karp, Dinic, and push relabel maximum flow algorithms with the max
flow min cut theorem, Hopcroft and Karp's matching algorithm, the Hungarian
assignment method, Stoer and Wagner's minimum cut algorithm, the DSATUR and
Welsh Powell colorings, the Master Theorem and the Akra Bazzi method, and
Binet's formula for the Fibonacci numbers.

Each of these is attributed where it is implemented, with a complexity
statement and, where useful, a reference. If you find an implementation that
fails to attribute the result it computes, that is a documentation defect
worth reporting.

## Software the project relies on

The computational core depends only on the Python standard library, which is
a deliberate design choice and also a debt: the exact integer arithmetic,
the rational arithmetic in `fractions`, the ordered dictionaries, and the
hashing primitives that the library builds on are all standard library
work.

The development and documentation environment relies on the following
projects, each of which is optional for a user of the library and essential
for its contributors.

| Project | Role in discretus |
| --- | --- |
| pytest | Test runner for the unit, property, and cross validation suites |
| Hypothesis | Property based testing of the algebraic laws |
| black and isort | Formatting and import ordering |
| ruff and pylint | Static lint analysis |
| mypy | Static type checking |
| bandit | Security oriented static analysis |
| pre-commit | Running the whole gate before a commit |
| nox and tox | Managing the interpreter matrix |
| Sphinx and MyST | Building the documentation from Markdown sources |
| Furo | Documentation theme |
| matplotlib | Optional raster and vector rendering backend |
| Graphviz | Optional graph and Hasse diagram layout backend |
| asv | Benchmark measurement across releases |

The conventions of the wider scientific Python community shaped decisions
throughout the project, from the shape of the docstrings to the decision to
keep the core dependency free, and that influence is gratefully
acknowledged.

## Institutional acknowledgment

The work is carried out at the Department of Physics and Mathematics,
Faculty of Science, Forestry and Technology, University of Eastern Finland,
in Joensuu. The department's teaching in discrete mathematics shaped both
the scope of the library and the decision to make its reference
implementations readable before making them fast.

Naming the institution acknowledges an academic home. It does not imply that
the university endorses the software or warrants it, and the license
disclaims warranty in the usual way.

## Funding

The project is unfunded. It receives no grant, no commercial sponsorship,
and no individual sponsorship, and `.github/FUNDING.yml` records that
position. Institutional collaboration enquiries are welcome at the
correspondence address above.

The absence of funding is stated plainly because it sets expectations. The
project aims to answer a report within five working days and to review a
pull request within a few days, and it achieves that most of the time and
not all of the time.

## How to cite

Cite the software rather than this file. `CITATION.cff` is the authoritative
source, and most reference managers read it directly from the repository.
The bibliographic entry is:

```bibtex
@software{discretus,
  title   = {discretus: A Discrete Mathematics library for Python},
  author  = {Laitinen Imanov, Olaf Yunus},
  year    = {2026},
  version = {1.0.0},
  url     = {https://github.com/olaflaitinen/discretus}
}
```

If your work depends on a specific version, cite that version, because the
public interface is guaranteed only within a major version. If your work
depends on a specific algorithm, please also cite its original source, which
the docstring names.
